"""Every run record under ``results/runs`` as a flat table of plain dicts.

One row per ``results.json``. A row carries the four axes the paper varies — encoder,
resolution, resize, head — plus the dataset, the protocol, the metrics, and the two
provenance digests that say whether two rows are comparable at all.

The head axis is two things wearing one name. ``head`` is the id, which is unique per fitted
head; ``head_recipe`` and ``head_fit`` separate *what the head is* from *where it was fitted*,
because the same recipe fitted on two splits is two systems and a table that files them under
one name is comparing a head to itself.

The axes are read with :mod:`reidbench.report`'s own labeller rather than by re-deriving
them here. There is exactly one definition of "which resize did this row use", it lives in
the library that wrote the record, and a paper that re-implemented it would eventually
disagree with the table it is citing.

Python 3.11+; numpy and pyarrow come in with reidbench.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
PROJECT = PAPER.parent
RUNS = PROJECT / "results" / "runs"

_src = PROJECT / "reidbench" / "src"
if _src.is_dir():  # the sibling checkout, so a fresh clone renders without an install step
    import sys

    sys.path.insert(0, str(_src))

from reidbench import report  # noqa: E402

AXES = ("encoder", "resolution", "resize", "head", "dataset", "protocol")
METRICS = ("mAP", "R1", "R5", "R10", "mINP")

_LABEL = getattr(report, "_label", None)
if _LABEL is None:  # pragma: no cover — a loud failure beats a silently different table
    raise SystemExit(
        "reidbench.report._label is gone; this script read a record's axes through it so that "
        "the paper and results/table.md cannot disagree. Re-point it at whatever replaced it."
    )

ENCODERS: dict[str, dict[str, Any]] = {
    k: v for k, v in json.loads((HERE / "encoders.json").read_text("utf-8")).items()
    if not k.startswith("_")
}
DATASETS: dict[str, dict[str, Any]] = {
    k: v for k, v in json.loads((HERE / "datasets.json").read_text("utf-8")).items()
    if not k.startswith("_")
}


def spec_stem(path: Path) -> str:
    """The encoder spec's file stem, which is how ``results/runs`` names its directories.

    ``torchhub-c-radio-v4-h-224.arcface/market1501/market1501_official@1`` -> the stem is
    everything before the head suffix. The head itself comes off the record, not off the path.
    """
    return path.relative_to(RUNS).parts[0].split(".")[0]


def _metrics(record: dict[str, Any]) -> dict[str, float | None]:
    values = record.get("metrics") or {}
    return {name: values.get(name) for name in METRICS}


def _scale(record: dict[str, Any]) -> dict[str, Any]:
    """How big the search was. Two rows with different gallery sizes are not one comparison."""
    scores = (record.get("inputs") or {}).get("scores") or {}
    return {"n_query": scores.get("n_query"), "n_gallery": scores.get("n_gallery")}


def _provenance(record: dict[str, Any]) -> dict[str, Any]:
    inputs = record.get("inputs") or {}
    features = inputs.get("features") or {}
    encoder = features.get("encoder") or {}
    head = encoder.get("head") or {}
    source = head.get("source") or {}
    return {
        "protocol_digest": (inputs.get("protocol") or {}).get("digest"),
        "manifest_digest": (inputs.get("manifest") or {}).get("digest"),
        "encoder_id": encoder.get("id"),
        "train_top1": (features.get("probe_training") or {}).get("train_top1"),
        "head_seed": head.get("seed"),
        "head_dim": head.get("dim"),
        # The recipe and the split it was fitted on are two axes, not one. `head` is the id
        # a run directory is named by (`arcface-msmt17`); `head_recipe` is what the head *is*
        # (`arcface`) and `head_fit` is where it learned it. Both are read off the record —
        # splitting the id on a hyphen here would invent a naming convention the library
        # never promised, and would break the first time a split has a hyphen in its name.
        "head_recipe": head.get("head") or "none",
        "head_fit": source.get("dataset"),
        "head_split": source.get("split"),
        "head_images": source.get("n_images"),
        "head_identities": source.get("n_identities"),
        "items_per_second": (features.get("timing") or {}).get("items_per_second"),
        "git_dirty": ((record.get("env") or {}).get("git") or {}).get("dirty"),
    }


def load() -> list[dict[str, Any]]:
    """Every run on disk, one flat dict each, sorted so the output is diffable."""
    out: list[dict[str, Any]] = []
    for path in sorted(RUNS.rglob("results.json")):
        record = report.load(path)
        stem = spec_stem(path)
        row: dict[str, Any] = {axis: _LABEL(record, axis) for axis in AXES}
        row["spec"] = stem
        row.update(ENCODERS.get(stem, {"label": stem, "family": "?", "role": "?", "order": 99}))
        row.update(_metrics(record))
        row.update(_scale(record))
        row.update(_provenance(record))
        out.append(row)
    return out


def pick(rows: list[dict[str, Any]], **where: Any) -> list[dict[str, Any]]:
    """The subset matching every ``key=value``; a list value matches any of its members."""

    def matches(row: dict[str, Any]) -> bool:
        return all(
            row.get(k) in v if isinstance(v, (list, tuple, set)) else row.get(k) == v
            for k, v in where.items()
        )

    return [row for row in rows if matches(row)]


def one(rows: list[dict[str, Any]], **where: Any) -> dict[str, Any] | None:
    """The single row matching, or None. Two matches is a bug in the query, so it raises."""
    found = pick(rows, **where)
    if len(found) > 1:
        raise SystemExit(f"{where} matched {len(found)} rows; the query is under-specified")
    return found[0] if found else None


def value(rows: list[dict[str, Any]], metric: str = "mAP", **where: Any) -> float | None:
    row = one(rows, **where)
    return None if row is None else row.get(metric)
