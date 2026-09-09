#!/usr/bin/env python3
"""The decision half of a run: two numbers per query, without ever keeping the matrix.

    python results/decide.py scan             # every measured run missing its decision.parquet
    python results/decide.py scan msmt17      # ... whose 'encoder head dataset protocol' matches
    python results/decide.py scan --force     # re-reduce runs already done

``run.py`` discards ``scores.npz`` because it is 99.9%% of what a run costs on disk and every
ranking metric it feeds is already in ``results.json``. The *decision* metrics are not, and
they need the one thing the ranking metrics drop: the score itself. They need only two numbers
per query, so this reduces each block of the matrix as it is produced and never holds the whole
of it --- ``score.blocks`` yields a query block, ``openset.acceptance`` reduces it, the block is
dropped. A market1501 run costs 33 KB here instead of 212 MB, and the same pass over
market1501+500k would cost the same 33 KB.

The reduction is deliberately *not* the metrics. A threshold, a bin count and a confidence
mapping are decisions to be argued about in the paper, and persisting a metric freezes them
into a file that has to be regenerated to change one's mind; persisting ``(smax, correct)``
freezes nothing, and every calibration, risk-coverage and threshold-transfer number is
microseconds away from it. Data, not conclusions.

**What this cannot answer.** Every protocol in the matrix today is closed-set: ``mated`` is
true for every query, so FNIR@FPIR, DIR@FAR, AUROC and EER are undefined here and this script
writes the column that says so rather than a number that looks like one. Those need a protocol
with non-mated probes --- a manifest change, and not this script's business. What *is* defined
closed-set is the accept-or-reject decision on the rank-1 candidate, which is what calibration,
risk-coverage and threshold transfer measure.

Python 3.11+; the reidbench environment, because it reads that package's stores.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run  # noqa: E402  — the matrix, the stores and the tracklet collapse are its business
from reidbench import cache  # noqa: E402
from reidbench import manifest as manifest_mod  # noqa: E402
from reidbench import protocol as protocol_mod  # noqa: E402
from reidbench import score as score_mod  # noqa: E402
from reidbench.measure import openset  # noqa: E402
from reidbench.transform import align  # noqa: E402

DECISION = "decision.parquet"

BLOCK_BYTES = 512 << 20
"""Roughly how much a single score block may cost, which is what sets the block size.

Not a fixed number of queries, because the cost of one is a function of the gallery: the
same 4096-query block is 1.3 GB against market1501 and 16 GB against market1501+500k. The
multiplier is 20 bytes per cell rather than the 4 a float32 score would suggest, because
``acceptance`` promotes the block to float64 and ``np.where`` then makes a second copy of
it -- correct for a metric that has to be exact, and the reason this script sizes its
blocks instead of taking the default one.
"""


def reduce_one(combo: dict[str, Any], force: bool = False) -> Path | None:
    """Write ``(q, smax, mated, correct)`` for one run. Returns the path, or None if skipped."""
    out = combo["run"] / DECISION
    if not (combo["run"] / "results.json").exists():
        return None
    if out.exists() and not force:
        return None

    features = run.features_of(combo, combo["dataset"])
    manifest = run.manifest_of(combo, combo["dataset"])
    by = run.datasets()[combo["dataset"]]["tracklet_by"]
    if by:
        features, manifest = run.collapse_to_tracklets(combo, features, manifest, by)

    table = manifest_mod.read(manifest)
    q_uids, g_uids, rel, valid = protocol_mod.select(table, protocol_mod.get(combo["protocol"]))
    uids, X, _ = cache.read_path(features)
    Xq, Xg = align(uids, X, q_uids), align(uids, X, g_uids)

    chunk = max(1, BLOCK_BYTES // (max(len(g_uids), 1) * 20))
    smax, mated, correct = [], [], []
    for rows, block in score_mod.blocks(Xq, Xg, chunk=chunk):
        s, _, m, c = openset.acceptance(block, rel[rows], valid[rows])
        smax.append(s)
        mated.append(m)
        correct.append(c)

    pq.write_table(
        pa.table({
            "q": pa.array(np.arange(len(q_uids)), pa.int32()),
            "smax": pa.array(np.concatenate(smax), pa.float32()),
            "mated": pa.array(np.concatenate(mated), pa.bool_()),
            "correct": pa.array(np.concatenate(correct), pa.bool_()),
        }),
        out,
    )
    return out


def cmd_scan(args: argparse.Namespace) -> int:
    done = skipped = 0
    for combo in run.combinations(args.pattern, args.exclude):
        if combo["why"]:
            continue
        label = f"{combo['encoder']} x {combo['head']} x {combo['dataset']} x {combo['protocol']}"
        written = reduce_one(combo, args.force)
        if written is None:
            skipped += 1
            continue
        done += 1
        print(f"[ done ] {label}")
    print(f"\n{done} reduced, {skipped} already done or not measured")
    return 0 if done or skipped else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="reduce every measured run to its decision vectors")
    scan.add_argument("pattern", nargs="?", default="", help="substring of 'encoder head dataset protocol'")
    scan.add_argument("--exclude", action="append", default=[], metavar="SUBSTRING")
    scan.add_argument("--force", action="store_true", help="re-reduce runs already done")
    args = parser.parse_args(argv)
    return {"scan": cmd_scan}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
