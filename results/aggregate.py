#!/usr/bin/env python3
"""The tracklet plumbing: thin out the frames, then pool what is left into tracklets.

    python results/aggregate.py sample --manifest m.parquet --by trackid --size 8 \
                                       --out m.8f.parquet
    python results/aggregate.py pool   --features STORE --manifest m.8f.parquet --by trackid \
                                       --cache CACHE_BASE --out-manifest t.parquet

Two steps, in that order, either side of ``encode``:

1. **sample** — keep 8 evenly spaced frames per tracklet, *before* extracting features, because
   the point is to not encode frames nobody will pool. 347,833 CCVID frames become 22,848 and
   1,191,003 MARS frames become 163,404.
2. **pool** — after extracting, collapse the rows and pool the vectors into one value per
   tracklet. Both halves or neither: ``manifest.collapse`` and ``transform.aggregate`` agree on
   the uid, so afterwards there are no tracklets, only rows and vectors, and a tracklet protocol
   is the same shape as every other one.

**Why pooling is not optional.** ``reidbench score`` materialises a ``(query, gallery)`` boolean
pair per protocol. Selecting ``ccvid/tracklet@1`` over a frame-level manifest asks for
116,799 x 112,421 — about 26 GB across ``rel`` and ``valid`` — to answer a question about 834
tracklets. Collapsed, it is 834 x 1,074.

**Both steps change the number, and both say so.** Sampling stamps its recipe into the
manifest's Arrow metadata and pooling goes *inside* the encoder description, so the cache key
falls out of it and mean-pooled and max-pooled tracklets address different directories. That is
the same argument ``probe.py`` makes for a trained head: a transform that moves a metric belongs
in the description of the value it produced, never in a constant in a runner script.

``reidbench`` scores systems and does not transform them on the caller's behalf; the plumbing
that reads a store, calls one library function and writes a store back is experiment business,
which is why this lives here beside ``probe.py`` and not in the package.

Python 3.11+; numpy and pyarrow.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

_src = PROJECT / "reidbench" / "src"
if _src.is_dir():  # the sibling checkout, so a fresh clone works without an install step
    sys.path.insert(0, str(_src))

from reidbench import cache, manifest as manifest_mod, splits  # noqa: E402
from reidbench.describe import timing  # noqa: E402
from reidbench.transform import aggregate  # noqa: E402


def cmd_sample(args: argparse.Namespace) -> int:
    """Thin each tracklet down to `size` evenly spaced frames, before anything is encoded."""
    table = manifest_mod.read(args.manifest)
    thinned = splits.frames_per_group(table, args.size, by=args.by)
    manifest_mod.write(thinned, args.out)
    print(
        f"wrote {args.out} — {table.num_rows:,} -> {thinned.num_rows:,} rows, "
        f"<= {args.size} per {args.by}"
    )
    return 0


def cmd_pool(args: argparse.Namespace) -> int:
    """Pool a frame-level store and its manifest into the tracklet-level pair to score over."""
    table = manifest_mod.read(args.manifest)
    collapsed = manifest_mod.collapse(table, by=args.by)
    if not args.out_manifest.exists():
        manifest_mod.write(collapsed, args.out_manifest)

    uids, X, description = cache.read_path(args.features)
    dataset = description.get("dataset", "unknown")
    composite = {**description["encoder"], "aggregate": {"by": args.by, "how": args.how}}
    manifest_description = manifest_mod.describe(collapsed, dataset=dataset)
    key = cache.key(composite, manifest_description["digest"], args.storage_dtype)
    if cache.exists(key, dataset, args.cache):
        print(f"cache hit {key}; nothing to do")
        return 0

    # The store's row order is the manifest's, but that is a fact about how it was written
    # rather than a guarantee, and a positional join that is wrong looks exactly like one that
    # is right. Join on the uid, which is what the uid is for.
    groups = _groups(table, uids, args.by)
    started = time.perf_counter()
    keys, E = aggregate(uids, X, groups, how=args.how)
    elapsed = time.perf_counter() - started

    if list(keys) != collapsed.column("uid").to_pylist():
        raise SystemExit(
            "the pooled uids and the collapsed manifest disagree; they are the same join key "
            "and one of the two was built from a different table"
        )

    directory = cache.write(
        key,
        keys,
        E,
        {"encoder": composite, "manifest": manifest_description},
        dataset=dataset,
        base=args.cache,
        storage_dtype=args.storage_dtype,
        timing=timing(E.shape[0], elapsed, source_key=description.get("key")),
    )
    print(f"wrote {directory} — {X.shape} -> {E.shape}, {args.how} over {args.by}")
    return 0


def _groups(table, uids, by: str):
    """``by`` for each row of the store, in the store's order, joined on uid."""
    cols = manifest_mod.columns(table, ["uid", by])
    position = {u: i for i, u in enumerate(cols["uid"].tolist())}
    missing = [u for u in uids.tolist() if u not in position]
    if missing:
        raise SystemExit(
            f"{len(missing)} store uids are not in the manifest, e.g. {missing[0]!r}; "
            "the store and the manifest are not of the same dataset"
        )
    return np.asarray([cols[by][position[u]] for u in uids.tolist()])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    sample = sub.add_parser("sample", help="keep N evenly spaced frames per tracklet")
    sample.add_argument("--manifest", type=Path, required=True, help="the frame-level manifest")
    sample.add_argument("--by", default="trackid", help="the column that names the tracklet")
    sample.add_argument("--size", type=int, required=True, help="frames to keep per tracklet")
    sample.add_argument("--out", type=Path, required=True, help="destination parquet")
    sample.set_defaults(func=cmd_sample)

    pool = sub.add_parser("pool", help="collapse a store and its manifest to tracklets")
    pool.add_argument("--features", type=Path, required=True, help="the frame-level store")
    pool.add_argument("--manifest", type=Path, required=True, help="that store's manifest")
    pool.add_argument("--by", default="trackid", help="the manifest column to pool over")
    pool.add_argument("--how", default="mean", choices=["mean", "max"], help="pooling")
    pool.add_argument("--cache", type=Path, required=True, help="cache base to write into")
    pool.add_argument(
        "--out-manifest", type=Path, required=True, help="destination for the collapsed manifest"
    )
    pool.add_argument("--storage-dtype", default="float16")
    pool.set_defaults(func=cmd_pool)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
