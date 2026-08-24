#!/usr/bin/env python3
"""Every (encoder, head, dataset) combination this project can evaluate, and the table they make.

    python results/run.py plan            # what would run, and why the rest would not
    python results/run.py all             # run everything missing, then rewrite the table
    python results/run.py all market1501  # only the combinations whose names contain that
    python results/run.py all --force     # ignore existing runs and re-measure
    python results/run.py table           # rewrite results/table.md from what is on disk

The combinations are not listed here. An **encoder** is a JSON spec in ``results/encoders/``,
which is the same file ``reidbench encode --encoder`` consumes, so the spec is never written
down twice. A **head** is a JSON spec in ``results/probes/``, which is the same file
``results/probe.py fit`` consumes, and it names the split it is fitted on. A **dataset** is a
page in ``datasets/`` whose ```toml block names a non-empty ``adapter`` and at least one
``protocol`` — the same block ``datasets/get.py`` reads. This script therefore holds no
dataset knowledge, no model knowledge and no probe knowledge of its own; adding any of the
three is a new file, not an edit here.

Every encoder is run **with no head** as well as with each of them, and that row is the
baseline the others are read against, so it is a combination like any other rather than a
mode: the axis has a value called ``none``.

Every step shells out to the ``reidbench`` CLI or to ``probe.py``, so what this script does
is exactly what a reader can do by hand, and the run records it leaves behind are the
package's own.

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
PROBES = HERE / "probes"
RUNS = HERE / "runs"
CACHE = HERE / "cache"
MANIFESTS = HERE / "manifests"
TABLE = HERE / "table.md"
NONE = "none"
"""The name of the head that is not a head. Every encoder is measured with it."""

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ------------------------------------------------------------------------------ the matrix


def data_root() -> Path:
    return Path(os.environ.get("REID_DATA_ROOT") or PROJECT / "data").resolve()


def encoders() -> dict[str, dict[str, Any]]:
    """``results/encoders/*.json``, keyed by file stem. The stem names the run directory."""
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(ENCODERS.glob("*.json"))}


def heads() -> dict[str, dict[str, Any]]:
    """``results/probes/*.json``, keyed by file stem, plus the no-head baseline.

    The baseline's spec is ``None`` rather than an empty dict: a head that trains nothing is
    not a configuration of a trainer, it is the absence of one, and the code downstream
    should branch on that rather than on a spec whose every field happens to be missing.
    """
    found = {
        p.stem: json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(PROBES.glob("*.json"))
    }
    return {NONE: None, **found}  # type: ignore[dict-item]


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
    """One entry per (encoder, head, dataset, protocol). Sorted, so the plan is stable.

    ``pattern`` is a plain substring over ``encoder head dataset protocol``. Choosing what to
    run is not a property of the matrix, so it is stored nowhere: it filters the list on the
    way out. One combination expensive enough to not want by accident is enough to need it.

    A head names the dataset it is fitted on, and a head whose train set is not on this disk
    cannot run anywhere — so that reason is attached per combination, beside the reason a
    *target* dataset cannot run, and ``plan`` prints whichever applies.
    """
    known = datasets()
    out = []
    for encoder_name in encoders():
        for head_name, head in heads().items():
            source = (head or {}).get("train", {}).get("dataset")
            variant = encoder_name if head is None else f"{encoder_name}.{head_name}"
            for dataset_name, dataset in sorted(known.items()):
                if dataset["why"]:
                    continue
                for protocol in dataset["protocols"]:
                    out.append(
                        {
                            "encoder": encoder_name,
                            "head": head_name,
                            "source": source,
                            "why": _why_not_head(head, known),
                            "dataset": dataset_name,
                            "adapter": dataset["adapter"],
                            "root": dataset["root"],
                            "protocol": protocol,
                            "cache": CACHE / variant / dataset_name,
                            "probe": CACHE / variant / "probe.npz",
                            "run": RUNS / variant / dataset_name / protocol.replace("/", "_"),
                        }
                    )
    return [
        c
        for c in out
        if pattern in f"{c['encoder']} {c['head']} {c['dataset']} {c['protocol']}"
    ]


def _why_not_head(head: dict[str, Any] | None, known: dict[str, dict[str, Any]]) -> str:
    """Why this head cannot be fitted, or "". The no-head baseline always runs."""
    if head is None:
        return ""
    source = head.get("train", {}).get("dataset")
    if source not in known:
        return f"no dataset page named {source!r} to fit on"
    return f"fits on {source}, which is {known[source]['why']}" if known[source]["why"] else ""


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


def probe(*args: str | Path) -> None:
    sh(sys.executable, str(HERE / "probe.py"), *args)


def store_of(cache_base: Path, dataset: str) -> Path:
    """The one feature store under a per-(variant, dataset) cache base.

    Stores are content-addressed, so whoever wrote one chose the path and the caller reads
    it back. Giving each (variant, dataset) its own base keeps that read unambiguous while
    still letting every protocol over the same pair hit the cache instead of re-extracting.

    Two stores under one base means a spec was edited under a name that already had one, so
    the message names the directory rather than guessing which of them was meant.
    """
    found = sorted((cache_base / "features" / dataset).glob("*/description.json"))
    if len(found) != 1:
        raise SystemExit(
            f"expected one feature store under {cache_base}, found {len(found)}"
            + (" — a spec changed under a name that already had one; delete the stale key"
               if len(found) > 1 else "")
        )
    return found[0].parent


def manifest_of(combo: dict[str, Any], dataset: str) -> Path:
    """``results/manifests/{dataset}.parquet``, built once and read by everything after.

    A manifest is a function of a dataset root, so building one per (encoder, head,
    protocol) run produced the same bytes twenty-one times and gave the probe trainer no
    obvious file to read. The content digest is what every result records, so where the
    file sits changes nothing that was already measured.
    """
    path = MANIFESTS / f"{dataset}.parquet"
    if not path.exists():
        known = datasets()[dataset]
        reidbench("manifest", known["adapter"], "--root", known["root"], "--out", path)
    return path


def features_of(combo: dict[str, Any], dataset: str, force: bool = False) -> Path:
    """The store to score over: the frozen encoder's, or that store projected through a head.

    Both are content-addressed feature stores in the same layout, which is the point — a
    trained head produces a value the evaluator already knows how to read, so nothing
    downstream of here has a probe branch in it.
    """
    frozen = CACHE / combo["encoder"] / dataset
    reidbench(
        "encode",
        "--manifest", manifest_of(combo, dataset),
        "--encoder", ENCODERS / f"{combo['encoder']}.json",
        "--root", datasets()[dataset]["root"],
        "--dataset", dataset,
        "--device", os.environ.get("REIDBENCH_DEVICE", "cuda"),
        "--cache", frozen,
    )
    if combo["head"] == NONE:
        return store_of(frozen, dataset)

    fit_probe(combo, force)
    probe(
        "apply",
        "--probe", combo["probe"],
        "--features", store_of(frozen, dataset),
        "--cache", combo["cache"],
    )
    return store_of(combo["cache"], dataset)


def fit_probe(combo: dict[str, Any], force: bool = False) -> None:
    """Fit this (encoder, head) once, whatever it is later applied to.

    Refits when the spec on disk is no longer the spec the weights were fitted from. A head
    is named by a file, and a file's contents change; without this, editing ``arcface.json``
    would leave every future run reading weights fitted from a spec nobody can see any more.
    """
    spec = PROBES / f"{combo['head']}.json"
    if combo["probe"].exists() and not force and _fitted_from(combo["probe"]) == json.loads(
        spec.read_text(encoding="utf-8")
    ):
        return
    source = combo["source"]
    probe(
        "fit",
        "--spec", spec,
        # The frozen features of the split it trains on — extracted here if this encoder has
        # never seen that dataset, which is a cache hit whenever it has.
        "--features", features_of({**combo, "head": NONE}, source),
        "--manifest", manifest_of(combo, source),
        "--out", combo["probe"],
    )


def _fitted_from(path: Path) -> dict[str, Any] | None:
    """The spec a fitted probe records, reduced to the keys a spec file has."""
    import numpy as np

    blob = np.load(path, allow_pickle=False)
    node = json.loads(str(blob["description"]))["head"]
    spec = {k: v for k, v in node.items() if k not in _NOT_SPEC}
    train = {"dataset": node["source"]["dataset"], "split": node["source"]["split"]}
    return {**spec, "train": train}


_NOT_SPEC = frozenset({"kind", "id", "input_norm", "source", "encoder_digest", "weights"})


def run_one(combo: dict[str, Any], force: bool) -> None:
    run = combo["run"]
    if (run / "results.json").exists() and not force:
        print(f"[ have ] {run.relative_to(PROJECT)}")
        return
    print(
        f"[  run ] {combo['encoder']} x {combo['head']} x {combo['dataset']} x {combo['protocol']}"
    )
    work = run / "work"
    work.mkdir(parents=True, exist_ok=True)
    scores = work / "scores.npz"

    reidbench(
        "score",
        "--features", features_of(combo, combo["dataset"], force),
        "--manifest", manifest_of(combo, combo["dataset"]),
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
    # The figures are named here rather than left to the renderer's defaults, because which
    # two metrics are worth plotting against each other is a claim about these datasets and
    # belongs where a reader can change it. mAP against mINP, not against R1: R1 tracks mAP
    # almost exactly here, so that scatter would be a diagonal line, while mINP is the
    # hardest true match's rank and separates rows the ranking alone calls equal.
    reidbench(
        "render", *records,
        "--labels", "encoder,resolution,head,protocol",
        "--scatter", "mAP,mINP",
        "--bar", "mAP",
        "--out", TABLE,
    )
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
    print("\nheads")
    known = datasets()
    for name, head in heads().items():
        why = _why_not_head(head, known)
        mark = "  ok  " if not why else " skip "
        what = (
            "the frozen encoder itself"
            if head is None
            else f"{head['head']} {head.get('dim', '?')}d on "
            f"{head['train']['dataset']}/{head['train']['split']}"
        )
        print(f"[{mark}] {name:22} {what}{'  — ' + why if why else ''}")
    print("\ncombinations")
    for combo in combinations(args.pattern):
        state = (
            "skip"
            if combo["why"]
            else ("have" if (combo["run"] / "results.json").exists() else "todo")
        )
        print(
            f"[ {state} ] {combo['encoder']} x {combo['head']} x {combo['dataset']} "
            f"x {combo['protocol']}{'  — ' + combo['why'] if combo['why'] else ''}"
        )
    return 0


def cmd_all(args: argparse.Namespace) -> int:
    todo = [c for c in combinations(args.pattern) if not c["why"]]
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
            "pattern", nargs="?", default="", help="substring of 'encoder head dataset protocol'"
        )
    sub.add_parser("table", help="rewrite results/table.md from the runs on disk")
    args = parser.parse_args(argv)
    return {"plan": cmd_plan, "all": cmd_all, "table": cmd_table}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
