#!/usr/bin/env python3
"""Every (encoder, dataset) combination this project can evaluate, and the table they make.

    python results/run.py plan            # what would run, and why the rest would not
    python results/run.py all             # run everything missing, then rewrite the table
    python results/run.py all market1501  # only the combinations whose names contain that
    python results/run.py all --force     # ignore existing runs and re-measure
    python results/run.py table           # rewrite results/table.md from what is on disk

The combinations are not listed here. An **encoder** is a JSON spec in ``results/encoders/``,
which is the same file ``reidbench encode --encoder`` consumes, so the spec is never written
down twice. A **dataset** is a page in ``datasets/`` whose ```toml block names a non-empty
``adapter`` and at least one ``protocol`` — the same block ``datasets/get.py`` reads. This
script therefore holds no dataset knowledge and no model knowledge of its own; adding either
is a new file, not an edit here.

Every step shells out to the ``reidbench`` CLI, so what this script does is exactly what a
reader can do by hand, and the run records it leaves behind are the package's own.

Python 3.11+ (tomllib), stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

sys.path.insert(0, str(PROJECT / "datasets"))
import get  # noqa: E402  — the dataset pages are its business, not this script's

ENCODERS = HERE / "encoders"
RUNS = HERE / "runs"
CACHE = HERE / "cache"
TABLE = HERE / "table.md"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ------------------------------------------------------------------------------ the matrix


def data_root() -> Path:
    return Path(os.environ.get("REID_DATA_ROOT") or PROJECT / "data").resolve()


def encoders() -> dict[str, dict[str, Any]]:
    """``results/encoders/*.json``, keyed by file stem. The stem names the run directory."""
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(ENCODERS.glob("*.json"))}


def datasets() -> dict[str, dict[str, Any]]:
    """Dataset pages that have an adapter, a protocol and a directory on disk.

    A page missing any of the three is not an error — most of them are request-gated and
    have never been downloaded. ``plan`` prints the reason so the gap stays visible.
    """
    out = {}
    for name, page in get.load().items():
        if name.startswith("_"):
            continue
        block = page.get("dataset", {})
        out[name] = {
            "adapter": block.get("adapter", ""),
            "protocols": block.get("protocols", []),
            "root": data_root() / block.get("dir", name),
            "why": _why_not(page),
        }
    return out


def _why_not(page: dict[str, Any]) -> str:
    """Why this dataset cannot run, or "". Whether it is on disk is `get`'s question."""
    block = page.get("dataset", {})
    if not block.get("adapter"):
        return "no reidbench adapter"
    if not block.get("protocols"):
        return "no protocol named on the page"
    absent = get.missing(page, data_root())
    return f"not on disk: {absent[0]}" if absent else ""


def combinations(pattern: str = "") -> list[dict[str, Any]]:
    """One entry per (encoder, dataset, protocol). Sorted, so the plan is stable.

    ``pattern`` is a plain substring over ``encoder dataset protocol``. Choosing what to run
    is not a property of the matrix, so it is stored nowhere: it filters the list on the way
    out. One combination expensive enough to not want by accident is enough to need it.
    """
    out = []
    for encoder_name, spec in encoders().items():
        for dataset_name, dataset in sorted(datasets().items()):
            if dataset["why"]:
                continue
            for protocol in dataset["protocols"]:
                out.append(
                    {
                        "encoder": encoder_name,
                        "spec": spec,
                        "dataset": dataset_name,
                        "adapter": dataset["adapter"],
                        "root": dataset["root"],
                        "protocol": protocol,
                        "run": RUNS / encoder_name / dataset_name / protocol.replace("/", "_"),
                    }
                )
    return [c for c in out if pattern in f"{c['encoder']} {c['dataset']} {c['protocol']}"]


# --------------------------------------------------------------------------------- running


def child_env() -> dict[str, str]:
    """The environment the verbs run in.

    ``pip install "reidbench[encoders]"`` is the supported path and needs nothing here. The
    sibling checkout is a fallback so this script also works in a clone that has not been
    installed, which is the state anyone reproducing the table for the first time is in.
    """
    env = dict(os.environ)
    src = PROJECT / "reidbench" / "src"
    if src.is_dir():
        env["PYTHONPATH"] = os.pathsep.join([str(src), env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
    return env


def sh(*args: str | Path) -> None:
    """Run one reidbench verb. Exit code 2 is 'findings', not failure — the run still wrote."""
    printable = [str(a) for a in args]
    print("  $ " + " ".join(printable))
    result = subprocess.run(printable, env=child_env())
    if result.returncode not in (0, 2):
        raise SystemExit(f"failed ({result.returncode}): {' '.join(printable)}")


def reidbench(*args: str | Path) -> None:
    sh(sys.executable, "-m", "reidbench.cli", *args)


def store_of(cache_base: Path, dataset: str) -> Path:
    """The one feature store under a per-(encoder, dataset) cache base.

    Stores are content-addressed, so ``encode`` chooses the path and the caller reads it
    back. Giving each (encoder, dataset) its own base keeps that read unambiguous while
    still letting every protocol over the same pair hit the cache instead of re-extracting.
    """
    found = sorted((cache_base / "features" / dataset).glob("*/description.json"))
    if len(found) != 1:
        raise SystemExit(f"expected one feature store under {cache_base}, found {len(found)}")
    return found[0].parent


def run_one(combo: dict[str, Any], force: bool) -> None:
    run = combo["run"]
    if (run / "results.json").exists() and not force:
        print(f"[ have ] {run.relative_to(PROJECT)}")
        return
    print(f"[  run ] {combo['encoder']} x {combo['dataset']} x {combo['protocol']}")
    work = run / "work"
    work.mkdir(parents=True, exist_ok=True)
    manifest, scores = work / "manifest.parquet", work / "scores.npz"
    spec = ENCODERS / f"{combo['encoder']}.json"
    cache_base = CACHE / combo["encoder"] / combo["dataset"]

    reidbench("manifest", combo["adapter"], "--root", combo["root"], "--out", manifest)
    reidbench(
        "encode",
        "--manifest", manifest,
        "--encoder", spec,
        "--root", combo["root"],
        "--dataset", combo["dataset"],
        "--device", os.environ.get("REIDBENCH_DEVICE", "cuda"),
        "--cache", cache_base,
    )
    reidbench(
        "score",
        "--features", store_of(cache_base, combo["dataset"]),
        "--manifest", manifest,
        "--protocol", combo["protocol"],
        "--out", scores,
    )
    # No `--open-set`: it is meaningful only for a protocol with non-mated probes, and
    # which protocols those are is the protocol's business, not this script's. Without
    # them every open-set metric is NaN and `check` says so.
    reidbench("measure", scores, "--out", run)


def write_table() -> int:
    records = sorted(RUNS.rglob("results.json"))
    if not records:
        print("no runs on disk; nothing to render")
        return 1
    reidbench("render", *records, "--out", TABLE)
    return 0


# -------------------------------------------------------------------------------- commands


def cmd_plan(args: argparse.Namespace) -> int:
    print(f"data root: {data_root()}\n")
    print("datasets")
    for name, dataset in sorted(datasets().items()):
        mark = "  ok  " if not dataset["why"] else " skip "
        print(f"[{mark}] {name:22} {dataset['why']}")
    print("\nencoders")
    for name, spec in encoders().items():
        print(f"[  ok  ] {name:22} {spec['id']}")
    print("\ncombinations")
    for combo in combinations(args.pattern):
        state = "have" if (combo["run"] / "results.json").exists() else "todo"
        print(f"[ {state} ] {combo['encoder']} x {combo['dataset']} x {combo['protocol']}")
    return 0


def cmd_all(args: argparse.Namespace) -> int:
    todo = combinations(args.pattern)
    if not todo:
        print("nothing to run; `plan` says why")
        return 1
    for combo in todo:
        run_one(combo, args.force)
    return write_table()


def cmd_table(args: argparse.Namespace) -> int:
    return write_table()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    plan_parser = sub.add_parser("plan", help="what would run, and why the rest would not")
    run_parser = sub.add_parser("all", help="run every missing combination, then rewrite the table")
    run_parser.add_argument("--force", action="store_true", help="re-run combinations already on disk")
    for one in (plan_parser, run_parser):
        one.add_argument(
            "pattern", nargs="?", default="", help="substring of 'encoder dataset protocol'"
        )
    sub.add_parser("table", help="rewrite results/table.md from the runs on disk")
    args = parser.parse_args(argv)
    return {"plan": cmd_plan, "all": cmd_all, "table": cmd_table}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
