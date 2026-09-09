#!/usr/bin/env python3
"""Every (encoder, head, dataset) combination this project can evaluate, and the table they make.

    python results/run.py plan            # what would run, and why the rest would not
    python results/run.py all             # run everything missing, then rewrite the table
    python results/run.py all --keep-scores   # ... and keep each run's score matrix
    python results/run.py all market1501  # only the combinations whose names contain that
    python results/run.py all --force     # ignore existing runs and re-measure
    python results/run.py table           # rewrite results/table.md and results/tables/

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
import shutil
import subprocess
import sys
import time
from collections.abc import Sequence
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
TABLES = HERE / "tables"
FIGURES = HERE / "figures.json"
NONE = "none"
"""The name of the head that is not a head. Every encoder is measured with it."""

DEFAULT_METRIC = "cosine"
"""`score.euclidean` does not L2-normalise and `score.cosine` does, so on raw frozen features
the two are genuinely different values rather than a rank-preserving relabelling. That makes
one euclidean control row worth having and a crossed `metric` axis not worth having — see
docs/project/39-sweep-backlog.md §2 item 6 and §3."""

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
            # A tracklet dataset says so on its own page, in the same block that names its
            # adapter. This script therefore still holds no dataset knowledge: "CCVID is
            # tracklet-shaped" is a fact about CCVID and lives on CCVID's page.
            "tracklet_by": block.get("tracklet_by", ""),
            "frames_per_tracklet": block.get("frames_per_tracklet", 0),
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


def combinations(
    pattern: str = "", exclude: Sequence[str] = (), metric: str = "cosine"
) -> list[dict[str, Any]]:
    """One entry per (encoder, head, dataset, protocol). Sorted, so the plan is stable.

    ``pattern`` is a plain substring over ``encoder head dataset protocol``, and ``exclude`` is
    a list of substrings over the same string that removes rows instead. Choosing what to run is
    not a property of the matrix, so neither is stored anywhere: they filter the list on the way
    out. One combination expensive enough to not want by accident is enough to need the first;
    the second is for when the cheap way to say what you want is to name what you do not — two
    encoders out of fourteen are 62% of this matrix's GPU cost, and holding them back for a
    session with more machine time is not the same decision as never running them.

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
                            "metric": metric,
                            # A non-default metric is a different score, so it is a different
                            # run — never the same cell recomputed. `cosine` keeps the bare
                            # path so every number already measured stays where it is.
                            "run": RUNS / variant / dataset_name / (
                                protocol.replace("/", "_")
                                + ("" if metric == DEFAULT_METRIC else f".{metric}")
                            ),
                        }
                    )
    def label(c: dict[str, Any]) -> str:
        return f"{c['encoder']} {c['head']} {c['dataset']} {c['protocol']}"

    return [
        c
        for c in out
        if pattern in label(c) and not any(e in label(c) for e in exclude)
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


TRANSIENT = ("CUDA error", "cuDNN error", "CUDA_ERROR", "out of memory", "no kernel image")
"""Driver-level faults that say nothing about the work being wrong.

A laptop that suspends can come back with an invalidated CUDA context, and the next
allocation fails with a bare ``RuntimeError: CUDA error: out of memory`` — note *not*
``torch.cuda.OutOfMemoryError``, which is the allocator hitting its budget and is a real
"this does not fit" that retrying cannot fix. On 2026-09-04 the first kind killed a 14-hour
encode at 96%, and with it the whole matrix, because one failed verb raises.

Retrying is only correct because every verb here is idempotent: ``encode`` is a cache miss
that writes once, and a second attempt either hits the cache or redoes the same work."""

RETRY_PAUSE_S = 60
"""Long enough for a driver that has just lost a context to settle, short enough not to matter
against a 14-hour encode."""


def sh(*args: str | Path, retries: int = 0) -> None:
    """Run one reidbench verb. Exit code 2 is 'findings', not failure — the run still wrote.

    ``stderr`` is captured so a failure can be *classified* and then re-emitted unchanged;
    ``stdout`` still streams, so progress is live. Nothing is swallowed either way.
    """
    printable = [str(a) for a in args]
    for attempt in range(retries + 1):
        # Flushed, because the child writes straight to the console while this print sits in
        # Python's buffer — without it a redirected log shows the two out of order.
        print("  $ " + " ".join(printable), flush=True)
        result = subprocess.run(printable, env=child_env(), stderr=subprocess.PIPE, text=True)
        if result.stderr:
            sys.stderr.write(result.stderr)
            sys.stderr.flush()
        if result.returncode in (0, 2):
            return
        transient = any(mark in (result.stderr or "") for mark in TRANSIENT)
        if transient and attempt < retries:
            print(
                f"  ! transient GPU fault (attempt {attempt + 1} of {retries + 1}); "
                f"waiting {RETRY_PAUSE_S}s and retrying"
            )
            time.sleep(RETRY_PAUSE_S)
            continue
        raise SystemExit(f"failed ({result.returncode}): {' '.join(printable)}")


def reidbench(*args: str | Path, retries: int = 0) -> None:
    sh(sys.executable, "-m", "reidbench.cli", *args, retries=retries)


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
    known = datasets()[dataset]
    if not path.exists():
        reidbench("manifest", known["adapter"], "--root", known["root"], "--out", path)

    # A video dataset is evaluated over a few frames per tracklet, not all of them, and the
    # thinning happens here — before `encode` — because the point is to not extract features
    # for frames nobody will pool. How many is a fact about the dataset and lives on its page;
    # the sampled manifest stamps the recipe, so every result downstream carries the number.
    by, size = known["tracklet_by"], known["frames_per_tracklet"]
    if not (by and size):
        return path
    sampled = MANIFESTS / f"{dataset}.{size}f.parquet"
    if not sampled.exists():
        sh(
            sys.executable, str(HERE / "aggregate.py"), "sample",
            "--manifest", path, "--by", by, "--size", str(size), "--out", sampled,
        )
    return sampled


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
        # The only verb that touches the GPU, so the only one a driver fault can reach — and
        # the most expensive to lose, at up to 14 hours. One retry, classified by stderr.
        retries=1,
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


def collapse_to_tracklets(
    combo: dict[str, Any], features: Path, manifest: Path, by: str
) -> tuple[Path, Path]:
    """Pool a frame store and its manifest to tracklets, and return the pair to score over.

    Both halves or neither: `manifest.collapse` and `transform.aggregate` agree on the uid, so
    a tracklet protocol scored over them is the same shape as every other protocol. Scoring it
    over the frame-level pair instead materialises a `(frames, frames)` boolean pair — 26 GB on
    CCVID — to answer a question about 834 tracklets.
    """
    dataset = combo["dataset"]
    base = combo["cache"].parent / f"{dataset}.tracklet"
    collapsed = MANIFESTS / f"{dataset}.tracklet.parquet"
    sh(
        sys.executable, str(HERE / "aggregate.py"), "pool",
        "--features", features,
        "--manifest", manifest,
        "--by", by,
        "--cache", base,
        "--out-manifest", collapsed,
    )
    return store_of(base, dataset), collapsed


def run_one(combo: dict[str, Any], force: bool, keep_scores: bool = False) -> None:
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

    features = features_of(combo, combo["dataset"], force)
    manifest = manifest_of(combo, combo["dataset"])
    by = datasets()[combo["dataset"]]["tracklet_by"]
    if by:
        features, manifest = collapse_to_tracklets(combo, features, manifest, by)

    reidbench(
        "score",
        "--features", features,
        "--manifest", manifest,
        "--protocol", combo["protocol"],
        "--metric", combo["metric"],
        "--out", scores,
    )
    # No `--open-set`: it is meaningful only for a protocol with non-mated probes, and
    # which protocols those are is the protocol's business, not this script's. Without
    # them every open-set metric is NaN and `check` says so.
    reidbench("measure", scores, "--out", run)

    # The score matrix is an intermediate, and on the large protocols it is *the* cost: a
    # market1501 run is 212 MB of scores.npz beside 112 KB of results, and the same table over
    # msmt17 and market1501+500k would want 776 GB of them. What the table reads —
    # results.json, per_query.parquet, curves.npz — is kept; this is regenerable by re-running
    # the same three commands, which is why it is safe to discard and why `--keep-scores`
    # exists for anyone who wants to re-measure without re-scoring.
    if not keep_scores:
        shutil.rmtree(work, ignore_errors=True)


# --------------------------------------------------------------------------------- summary


ALL = "all"
"""The row and column a coverage table totals over. No encoder, head or dataset is named it."""

SHOWN = 12
"""How many missing combinations the gaps table names before it counts the rest.

Long enough that adding one encoder lists in full — twelve rows here, one per head and
dataset — and short enough that a matrix nobody has run yet does not push the table it is
summarising off the screen.
"""


def summary(records: Sequence[Path]) -> str:
    """The status block above the table: how much of the matrix is on disk, and what is not.

    The table below it is one row per run, which answers *what was measured* and cannot
    answer *what is missing* — a combination nobody ran is not a row there, it is the
    absence of one, and an absence is invisible in a thousand-line file. So the counts here
    come from the matrix, where a missing combination still exists, and only the provenance
    sentence is read off the records themselves.

    It is written here rather than by ``reidbench render`` because every number in it is a
    fact about *this* directory's cross product — which specs exist, which datasets are on
    this disk — while the renderer is handed the results.json files that exist, which is
    precisely the list a combination nobody ran is absent from.
    """
    combos = combinations()
    runnable = [combo for combo in combos if not combo["why"]]
    live = sorted({combo["dataset"] for combo in runnable})
    parts = [
        "# Summary",
        "",
        _headline(runnable, records),
        "",
        "One cell is *measured / in the matrix*, counting every head and protocol for that"
        " pair. The encoder is named by its spec's file stem, which is also what"
        " `run.py all <pattern>` matches.",
        "",
        _coverage(runnable, "encoder", live),
        "",
        _coverage(runnable, "head", live, _fitted_on()),
    ]
    gaps = _gaps(combos)
    if gaps:
        parts += ["", "## Not measured", "", gaps]
    return "\n".join(parts) + "\n\n"


def _headline(runnable: list[dict[str, Any]], records: Sequence[Path]) -> str:
    """One italic paragraph: the size of the matrix, what it cost, and what wrote it."""
    done = sum(1 for combo in runnable if (combo["run"] / "results.json").exists())
    facts = _facts(records)
    said = [
        f"{len(encoders())} encoders x {len(heads())} heads (`none` is one of them) x "
        f"{len({combo['dataset'] for combo in runnable})} datasets: "
        f"**{done} of {len(runnable)}** combinations measured"
    ]
    if facts["stores"]:
        said.append(f"{facts['hours']:.1f} h of encoding over {facts['stores']} feature stores")
    if facts["created"]:
        first, last = facts["created"][0][:10], facts["created"][-1][:10]
        span = first if first == last else f"{first} to {last}"
        said.append(f"Records written {span} by reidbench {', '.join(facts['versions'])}")
    if facts["dirty"]:
        # Its own clause: a run recorded from a dirty tree cannot be reproduced from the sha
        # it names, and that is a property of the table rather than of any one row in it.
        said.append(f"**{facts['dirty']} of {facts['read']} from a dirty working tree**")
    stray = _stray(runnable, records)
    if stray:
        said.append(
            f"**{len(stray)} records below are no longer in the matrix** — a spec was "
            "renamed or deleted and its runs were not"
        )
    absent = sum(1 for dataset in datasets().values() if dataset["why"])
    if absent:
        said.append(f"{absent} more dataset pages cannot run here")
    return "*" + ". ".join(said) + ".*"


def _facts(records: Sequence[Path]) -> dict[str, Any]:
    """What the run records say about themselves. An unreadable one is skipped, not fatal.

    A half-written results.json is a gap in a status block and not a reason to refuse to
    write the table, which is what the reader came for.
    """
    created: list[str] = []
    versions: set[str] = set()
    read = 0
    dirty = 0
    seconds: dict[str, float] = {}
    for path in records:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        read += 1
        env = record.get("env", {})
        if record.get("created"):
            created.append(str(record["created"]))
        versions.add(str(env.get("reidbench", "?")))
        dirty += bool(env.get("git", {}).get("dirty"))
        features = record.get("inputs", {}).get("features", {})
        timing = features.get("timing") or {}
        # Keyed by feature store rather than summed per run: twelve rows read one store, and
        # charging its extraction time to each of them would report twelve times what the
        # machine actually spent. Only frozen stores count — applying a head is a matrix
        # multiply whose milliseconds are noise beside a forward pass over 36,036 images.
        if timing.get("seconds") and not (features.get("encoder") or {}).get("head"):
            seconds[str(features.get("key"))] = float(timing["seconds"])
    return {
        "read": read,
        "created": sorted(created),
        "versions": sorted(versions),
        "dirty": dirty,
        "stores": len(seconds),
        "hours": sum(seconds.values()) / 3600,
    }


def _stray(runnable: list[dict[str, Any]], records: Sequence[Path]) -> list[Path]:
    """Records on disk that no combination in the matrix would write.

    ``render`` is handed every results.json under ``runs/``, so these are rows in the table
    below — and nothing else in this script would ever mention them again.
    """
    matrix = {(combo["run"] / "results.json").resolve() for combo in runnable}
    return [path for path in records if path.resolve() not in matrix]


def _fitted_on() -> dict[str, str]:
    """``{head: what it is}``, for the column that makes the head table readable alone.

    Every head here is fitted on one split of one dataset, and which one decides whether a
    given column of the table below is in-domain or transfer — so it belongs beside the
    counts rather than only in the prose.
    """
    return {
        name: (
            "the frozen encoder"
            if head is None
            else f"{head['head']} {head.get('dim', '?')}d on "
            f"`{head['train']['dataset']}/{head['train']['split']}`"
        )
        for name, head in heads().items()
    }


def _coverage(
    combos: list[dict[str, Any]],
    axis: str,
    live: list[str],
    describe: dict[str, str] | None = None,
) -> str:
    """One table: ``axis`` down the side, datasets across, *measured / in the matrix* inside."""
    cells: dict[tuple[str, str], list[int]] = {}
    for combo in combos:
        done = (combo["run"] / "results.json").exists()
        for key in (
            (combo[axis], combo["dataset"]),
            (combo[axis], ALL),
            (ALL, combo["dataset"]),
            (ALL, ALL),
        ):
            tally = cells.setdefault(key, [0, 0])
            tally[0] += done
            tally[1] += 1

    def cell(value: str, dataset: str) -> str:
        tally = cells.get((value, dataset))
        return f"{tally[0]}/{tally[1]}" if tally else "—"

    header = [axis] + (["is"] if describe else []) + [*live, "runs"]
    rows = []
    for value in sorted({combo[axis] for combo in combos}) + [ALL]:
        total = value == ALL
        row = [f"**{ALL}**" if total else f"`{value}`"]
        if describe:
            row.append("" if total else describe.get(value, ""))
        rows.append(row + [cell(value, dataset) for dataset in live] + [cell(value, ALL)])
    return _markdown(header, rows, "l" + ("l" if describe else "") + "r" * (len(live) + 1))


def _gaps(combos: list[dict[str, Any]]) -> str:
    """Everything the matrix holds that the table does not: not run yet, or cannot run.

    A dataset that is not on disk is one row here rather than forty-eight blank cells
    above, because one missing download is one fact.
    """
    known = datasets()
    missing = [
        combo
        for combo in combos
        if not combo["why"] and not (combo["run"] / "results.json").exists()
    ]
    rows = [
        [
            f"`{combo['encoder']}` x `{combo['head']}` x `{combo['dataset']}` "
            f"x `{combo['protocol']}`",
            "not run — `run.py all` would run it",
        ]
        for combo in missing[:SHOWN]
    ]
    if len(missing) > SHOWN:
        rows.append([f"… and {len(missing) - SHOWN} more combinations", "not run"])
    rows += [
        [f"dataset `{name}`", _portable(dataset["why"])]
        for name, dataset in sorted(known.items())
        if dataset["why"]
    ]
    rows += [
        [f"head `{name}`", _portable(_why_not_head(head, known))]
        for name, head in heads().items()
        if _why_not_head(head, known)
    ]
    return _markdown(["what", "why"], rows, "ll") if rows else ""


def _portable(why: str) -> str:
    """A reason with this machine out of it: paths relative to the data root, forward slashes.

    ``plan`` prints the absolute path, because someone at a terminal is about to go and look
    for the directory. This table is committed, and a reason that names one laptop's drive
    letter is a diff every other clone would have to make.
    """
    return (
        why.replace(str(data_root()) + os.sep, "")
        .replace(str(data_root()), "")
        .replace("\\", "/")
    )


def _markdown(header: Sequence[str], rows: Sequence[Sequence[str]], align: str) -> str:
    """A padded markdown table. ``report.py`` writes the ones below; this writes these.

    Padded rather than minimal because the copy of this table most of its edits are read
    against is the source, not the render.
    """
    widths = [
        max([len(str(head))] + [len(str(row[i])) for row in rows])
        for i, head in enumerate(header)
    ]

    def line(cells: Sequence[str]) -> str:
        return (
            "| "
            + " | ".join(
                str(cell).rjust(width) if side == "r" else str(cell).ljust(width)
                for cell, width, side in zip(cells, widths, align, strict=True)
            )
            + " |"
        )

    rule = (
        "|"
        + "|".join(
            ("-" * (width + 1) + ":") if side == "r" else "-" * (width + 2)
            for width, side in zip(widths, align, strict=True)
        )
        + "|"
    )
    return "\n".join([line(header), rule, *(line(row) for row in rows)])


def write_table() -> int:
    records = sorted(RUNS.rglob("results.json"))
    if not records:
        print("no runs on disk; nothing to render")
        return 1
    # `render` is handed the tree, not the 355 paths inside it: naming them individually is a
    # 34,832-character command line, and Windows will not start a process past 32,767. That
    # limit was crossed silently — the failure is in CreateProcess, so it surfaced as a
    # traceback after every run had already been written, and two chained jobs swallowed it.
    # The figures are named here rather than left to the renderer's defaults, because which
    # two metrics are worth plotting against each other is a claim about these datasets and
    # belongs where a reader can change it. mAP against mINP, not against R1: R1 tracks mAP
    # almost exactly here, so that scatter would be a diagonal line, while mINP is the
    # hardest true match's rank and separates rows the ranking alone calls equal.
    reidbench(
        "render", RUNS,
        "--labels", "encoder,resolution,resize,head,protocol",
        # A section per dataset *and per protocol*, because the protocol is the one label
        # whose values do not compete. CCVID ships two — `ccvid/tracklet@1` and
        # `ccvid/tracklet-cloth-changing@1` — differing by one exclusion, and the second
        # asks a strictly harder question of the same tracklets. One table over both
        # numbers the rows against each other, emphasises the higher value and draws one
        # scatter through the pair, all three of which say the cloth-changing row lost a
        # comparison nobody made. Named here rather than left to the default because which
        # rows are each other's competition is a claim about these runs.
        "--group-by", "dataset,protocol",
        "--scatter", "mAP,mINP",
        "--bar", "mAP",
        # The head is the axis this table exists to argue about — four of them over seven
        # encoder-resolution pairs — so it is what the marks are coloured by, and the same
        # swatch sits in the head column so a colour in a figure is read off a row rather
        # than remembered from a legend.
        "--series", "head",
        # Which figures, in a file, because which comparison is worth drawing is a claim
        # about these runs and not about the renderer — and because turning one off should
        # be deleting four lines rather than editing this call.
        "--figures", FIGURES,
        # One file per dataset, and `table.md` becomes the index over them. The whole report
        # was 3,000 lines, of which 96% was the numbers: CCVID alone is 756 and five other
        # datasets are ~380 each, so every question about one dataset was asked by scrolling
        # past four others, and re-running one showed up as a diff to the report. What stays
        # in `table.md` is what is about the matrix rather than about a dataset — the
        # coverage summary above, the licences below, and now a table of where to look.
        "--pages", TABLES,
        "--out", TABLE,
    )
    # Prepended rather than passed in: the renderer is given the runs that exist, and the
    # first question anyone opening this file has — is anything missing? — is answerable
    # only from the matrix, which is this script's half of the work.
    TABLE.write_text(summary(records) + TABLE.read_text(encoding="utf-8"), encoding="utf-8")
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
    chosen = combinations(args.pattern, args.exclude, args.metric)
    print("\n" + selection([c for c in chosen if not c["why"]], args.pattern))
    print("\ncombinations")
    for combo in chosen:
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


def selection(combos: list[dict[str, Any]], pattern: str) -> str:
    """One line naming what a pattern actually selected, before anything runs.

    `pattern` is a substring and stays one, because `--exclude arcface` catching
    `arcface-msmt17` is deliberate and useful. The cost of that is a pattern which quietly
    selects more than it reads like: `market1501` also matches `market1501-500k`, which on
    2026-09-04 put a second `run.py` onto the 500k set for two days — scoring 1.7-Gpair
    matrices and CPU-encoding 500,000 images beside the job that was already doing it.
    Nothing detected it because nothing ever said what had been chosen. Now it does.
    """
    def distinct(key: str) -> list[str]:
        return sorted({str(c[key]) for c in combos})

    parts = [f"{len(combos)} runs"]
    for key in ("dataset", "encoder", "head"):
        values = distinct(key)
        parts.append(f"{len(values)} {key}s" if len(values) > 3 else "/".join(values))
    line = f"selected: {', '.join(parts)}"
    datasets_hit = distinct("dataset")
    if pattern and len(datasets_hit) > 1:
        line += (
            f"\n  ! {pattern!r} is a substring and matched {len(datasets_hit)} datasets: "
            f"{', '.join(datasets_hit)} — add --exclude if that is not what you meant"
        )
    return line


def cmd_all(args: argparse.Namespace) -> int:
    todo = [c for c in combinations(args.pattern, args.exclude, args.metric) if not c["why"]]
    if not todo:
        print("nothing to run; `plan` says why")
        return 1
    print(selection(todo, args.pattern))
    for combo in todo:
        run_one(combo, args.force, args.keep_scores)
    return write_table()


def cmd_table(args: argparse.Namespace) -> int:
    return write_table()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    plan_parser = sub.add_parser("plan", help="what would run, and why the rest would not")
    run_parser = sub.add_parser("all", help="run every missing combination, then rewrite the table")
    run_parser.add_argument("--force", action="store_true", help="re-run combinations already on disk")
    run_parser.add_argument(
        "--keep-scores",
        action="store_true",
        help="keep each run's work/scores.npz. Off by default: it is a regenerable intermediate "
             "and 99.9%% of the disk a run costs",
    )
    for one in (plan_parser, run_parser):
        one.add_argument(
            "pattern",
            nargs="?",
            default="",
            help="substring of 'encoder head dataset protocol'. A SUBSTRING, not a name: "
                 "'market1501' also selects 'market1501-500k'. The selection is printed "
                 "before anything runs, and warns when one pattern spans several datasets",
        )
        one.add_argument(
            "--metric",
            default=DEFAULT_METRIC,
            help="score metric. A non-default one writes to its own run directory, because it "
                 "is a different score and not a recomputation of the same cell",
        )
        one.add_argument(
            "--exclude",
            action="append",
            default=[],
            metavar="SUBSTRING",
            help="drop combinations matching this substring; repeatable. For holding an "
                 "expensive encoder back from a short session without editing the matrix",
        )
    sub.add_parser("table", help="rewrite results/table.md and results/tables/ from the runs")
    args = parser.parse_args(argv)
    return {"plan": cmd_plan, "all": cmd_all, "table": cmd_table}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
