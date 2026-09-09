#!/usr/bin/env python3
"""Write every table and every inline number in the paper, from ``results/runs``.

    python tools/gen_tables.py

Nothing under ``generated/`` is edited by hand. A number that appears in the prose appears
there as a macro defined in ``generated/macros.tex``, so re-running the sweep and re-running
this script is the whole update path — there is no second copy of a metric to forget.

Each writer is a function of the loaded rows and returns a LaTeX string; ``main`` maps them
over their filenames. Adding a table is one function and one line.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import rows as R  # noqa: E402

OUT = HERE.parent / "generated"

LEAD = "torchhub-c-radio-v4-h-224"
"""The encoder the head study is read on. Named once; every table that says "the lead
encoder" resolves it here rather than repeating a spec stem."""

ABLATION = [
    "torchhub-c-radio-v4-h-224",
    "torchhub-c-radio-v4-so400m-224",
    "timm-vit-giantopt-patch16-siglip2-256",
    "timm-vit-so400m-patch14-siglip2-224",
    "timm-vit-huge-plus-patch16-dinov3-224",
    "timm-vit-large-patch16-dinov3-224",
    "timm-vit-base-patch16-clip-224-squash",
]
"""The teacher ablation's encoders, at one resolution each, in reading order."""

HEADS = ["none", "pca", "linear", "arcface"]
"""The heads fitted on ``market1501/train``. These are *ids*, not recipes: the same three
recipes fitted on ``msmt17/train`` carry different ids, and only ``t_fitsplit`` reports them."""

HEAD_NAME = {"none": "frozen", "pca": "PCA", "linear": "linear", "arcface": "ArcFace"}

FIT_SPLITS = ["market1501", "msmt17"]
"""The training splits a head is fitted on, in the order the fit-split table reads them."""

FITTED = ["pca", "linear", "arcface"]
"""The recipes that are fitted at all. ``none`` has no split and is the baseline row."""


def check_heads(data: list[dict[str, Any]]) -> None:
    """Fail if the matrix holds a head that no table would render.

    Every table but ``t_fitsplit`` selects rows by head *id* against ``HEADS``, so a head this
    file has never heard of does not raise -- it silently vanishes from the tables while still
    counting toward ``nRuns`` and ``nHeads``. That failure has already happened once: the
    msmt17-fitted heads landed, the abstract's counts moved with them, and every table went on
    reporting four heads. A run no table renders is either a table this file owes or a run the
    sweep should not have made, and both are worth stopping for.
    """
    known = set(HEADS) | {f"{r}-{s}" for r in FITTED for s in FIT_SPLITS if s != "market1501"}
    unknown = sorted({row["head"] for row in data} - known)
    if unknown:
        raise SystemExit(
            f"heads with no table: {', '.join(unknown)}. Add them to HEADS (a market1501-fitted "
            "variant every table should report) or to FIT_SPLITS (the same recipe on another "
            "split), or drop the runs."
        )

TIMES = "$\\times$"


# --------------------------------------------------------------------------- formatting


def num(value: Any, places: int = 3) -> str:
    return "--" if value is None else f"{value:.{places}f}"


def best(values: list[float | None]) -> float | None:
    present = [v for v in values if v is not None]
    return max(present) if present else None


def bold(value: Any, top: Any, places: int = 3) -> str:
    text = num(value, places)
    return f"\\textbf{{{text}}}" if value is not None and value == top else text


def tabular(spec: str, header: list[str], body: list[list[str]], rules: tuple = ()) -> str:
    """A booktabs tabular. ``rules`` names body rows to draw a midrule *before*."""
    lines = [f"\\begin{{tabular}}{{{spec}}}", "\\toprule", " & ".join(header) + " \\\\",
             "\\midrule"]
    for i, row in enumerate(body):
        if i in rules:
            lines.append("\\midrule")
        lines.append(" & ".join(row) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def res(text: str) -> str:
    """``256x128`` as LaTeX. ``native`` is a resolution too, and it is not a product."""
    return text.replace("x", TIMES) if "x" in text else f"\\textit{{{text}}}"


def names(data: list[dict[str, Any]], specs: list[str]) -> dict[str, str]:
    """A display name per spec, disambiguated only where it has to be.

    Two CLIP rows share a checkpoint and an input size and differ only in how the image was
    fitted to it. Printed as bare labels they read as a contradiction, so the fit joins the
    name exactly when the pair would otherwise collide, and nowhere else -- a column that is
    constant down eleven of twelve rows is noise.
    """
    seen: dict[tuple[str, str], int] = {}
    for spec in specs:
        row = R.pick(data, spec=spec)[0]
        seen[(row["label"], row["resolution"])] = seen.get((row["label"], row["resolution"]), 0) + 1
    out: dict[str, str] = {}
    for spec in specs:
        row = R.pick(data, spec=spec)[0]
        collides = seen[(row["label"], row["resolution"])] > 1
        out[spec] = f"{row['label']} ({row['resize']})" if collides else row["label"]
    return out


def ordered(data: list[dict[str, Any]]) -> list[str]:
    return sorted({r["spec"] for r in data}, key=lambda s: R.ENCODERS[s]["order"])


def datasets_in(data: list[dict[str, Any]]) -> list[str]:
    present = {row["dataset"] for row in data}
    return [d for d in sorted(R.DATASETS, key=lambda k: R.DATASETS[k]["order"]) if d in present]


def dname(dataset: str) -> str:
    """The column-header form. Seven full dataset names do not fit in an IEEE column, and a
    table that overflows the column is a worse failure than an abbreviated header."""
    return R.DATASETS.get(dataset, {}).get("short", dataset)


def dfull(dataset: str) -> str:
    return R.DATASETS.get(dataset, {}).get("name", dataset)


def protocol_of(dataset: str) -> str | None:
    """The one protocol the paper's cross-dataset tables report per dataset.

    CCVID ships two that differ by one exclusion, and the same identity is easier to find
    when nobody changed clothes; a table holding both would bold the easier protocol's row
    and call it the better system. The cloth-changing split is reported on its own.
    """
    return "ccvid/tracklet@1" if dataset == "ccvid" else None


def main_rows(data: list[dict[str, Any]], dataset: str, **where: Any) -> list[dict[str, Any]]:
    picked = R.pick(data, dataset=dataset, **where)
    protocol = protocol_of(dataset)
    return [row for row in picked if protocol is None or row["protocol"] == protocol]


def cell(data: list[dict[str, Any]], spec: str, dataset: str, head: str,
         metric: str = "mAP") -> float | None:
    found = main_rows(data, dataset, spec=spec, head=head)
    return found[0][metric] if found else None


# --------------------------------------------------------------------------- tables


def t_datasets(data: list[dict[str, Any]]) -> str:
    body = []
    for dataset in datasets_in(data):
        meta = R.DATASETS[dataset]
        for protocol in sorted({r["protocol"] for r in R.pick(data, dataset=dataset)}):
            sample = R.pick(data, dataset=dataset, protocol=protocol)[0]
            body.append([
                dfull(dataset), meta["object"], meta["regime"],
                f"\\texttt{{{protocol}}}",
                f"{sample['n_query']:,}", f"{sample['n_gallery']:,}",
            ])
    return tabular("llllrr",
                   ["dataset", "object", "regime", "protocol", "queries", "gallery"], body)


def t_encoders(data: list[dict[str, Any]]) -> str:
    body = []
    for spec in ordered(data):
        sample = R.pick(data, spec=spec)[0]
        body.append([
            sample["label"], sample["family"], f"{sample['params_m']}",
            res(sample["resolution"]), sample["resize"],
            f"\\texttt{{\\small {_breakable(str(sample['encoder_id']))}}}",
        ])
    return tabular("lllllp{0.26\\linewidth}",
                   ["encoder", "pre-training", "params (M)", "input", "fit", "checkpoint"], body)


def _breakable(identifier: str) -> str:
    """A checkpoint id that TeX may wrap. Without break opportunities a single 45-character
    \\texttt{} run overflows its column and no amount of shrinking the font fixes it."""
    escaped = identifier.replace("_", "\\_\\allowbreak ")
    return escaped.replace(":", ":\\allowbreak ").replace("/", "/\\allowbreak ")


def t_readout(data: list[dict[str, Any]]) -> str:
    """The headline: Market-1501 mAP under each head, with the rank frozen and the rank probed."""
    specs = ordered(data)
    shown = names(data, specs)
    table = {s: {h: cell(data, s, "market1501", h) for h in HEADS} for s in specs}
    ranks = {h: _rank({s: table[s][h] for s in specs}) for h in HEADS}
    tops = {h: best([table[s][h] for s in specs]) for h in HEADS}

    body = []
    for spec in specs:
        frozen, probed = table[spec]["none"], table[spec]["arcface"]
        gain = "--" if not frozen or not probed else f"{probed / frozen:.1f}{TIMES}"
        body.append([
            shown[spec], res(R.pick(data, spec=spec)[0]["resolution"]),
            *[bold(table[spec][h], tops[h]) for h in HEADS],
            _move(ranks["none"].get(spec), ranks["arcface"].get(spec)), gain,
        ])
    header = ["encoder", "input"] + [HEAD_NAME[h] for h in HEADS] + ["rank", "gain"]
    return tabular("ll" + "r" * len(HEADS) + "cr", header, body)


def _rank(values: dict[str, float | None]) -> dict[str, int]:
    present = {k: v for k, v in values.items() if v is not None}
    return {k: i + 1 for i, k in enumerate(sorted(present, key=lambda k: -present[k]))}


def _move(before: int | None, after: int | None) -> str:
    if before is None or after is None:
        return "--"
    arrow = "$\\to$" if before != after else "$=$"
    return f"{before}\\,{arrow}\\,{after}"


def t_main(data: list[dict[str, Any]]) -> str:
    return _matrix(data, "arcface", "mAP")


def t_main_r1(data: list[dict[str, Any]]) -> str:
    return _matrix(data, "arcface", "R1")


def t_frozen(data: list[dict[str, Any]]) -> str:
    return _matrix(data, "none", "mAP")


def _matrix(data: list[dict[str, Any]], head: str, metric: str) -> str:
    specs, sets = ordered(data), datasets_in(data)
    shown = names(data, specs)
    tops = {d: best([cell(data, s, d, head, metric) for s in specs]) for d in sets}
    body = [[shown[spec], res(R.pick(data, spec=spec)[0]["resolution"]),
             *[bold(cell(data, spec, d, head, metric), tops[d]) for d in sets]]
            for spec in specs]
    return tabular("ll" + "r" * len(sets), ["encoder", "input"] + [dname(d) for d in sets], body)


def t_heads(data: list[dict[str, Any]]) -> str:
    """Every head on the lead encoder, across every dataset. The PCA row is the control."""
    sets = datasets_in(data)
    tops = {d: best([cell(data, LEAD, d, h) for h in HEADS]) for d in sets}
    body = [[HEAD_NAME[h], *[bold(cell(data, LEAD, d, h), tops[d]) for d in sets]] for h in HEADS]
    return tabular("l" + "r" * len(sets), ["head"] + [dname(d) for d in sets], body)


def fit_cell(data: list[dict[str, Any]], dataset: str, recipe: str,
             fit: str | None, metric: str = "mAP") -> float | None:
    """The lead encoder's value for one (recipe, fit split) on one test set."""
    found = main_rows(data, dataset, spec=LEAD, head_recipe=recipe, head_fit=fit)
    return found[0][metric] if found else None


def t_fitsplit(data: list[dict[str, Any]]) -> str:
    """One recipe fitted on each of two splits, read on both of them. The diagonal is bolded.

    The off-diagonal cell is the same recipe, the same encoder, the same fitting budget and the
    same test set; it differs only in where the head was fitted. That is what makes the table a
    control rather than a comparison.
    """
    body = [[HEAD_NAME["none"], "---",
             *[num(fit_cell(data, d, "none", None)) for d in FIT_SPLITS]]]
    for recipe in FITTED:
        for fit in FIT_SPLITS:
            cells = []
            for dataset in FIT_SPLITS:
                text = num(fit_cell(data, dataset, recipe, fit))
                cells.append(f"\\textbf{{{text}}}" if dataset == fit else text)
            body.append([HEAD_NAME[recipe], dfull(fit), *cells])
    header = ["readout", "fitted on"] + [dname(d) for d in FIT_SPLITS]
    return tabular("ll" + "r" * len(FIT_SPLITS), header, body,
                   rules=tuple(range(1, len(body), len(FIT_SPLITS))))


def t_ablation(data: list[dict[str, Any]]) -> str:
    specs = [s for s in ABLATION if R.pick(data, spec=s)]
    shown, sets = names(data, specs), datasets_in(data)
    tops = {d: best([cell(data, s, d, "arcface") for s in specs]) for d in sets}
    body = []
    for spec in specs:
        meta = R.ENCODERS[spec]
        body.append([
            shown[spec], f"{meta['params_m']}", meta["role"].replace("-", " "),
            *[bold(cell(data, spec, d, "arcface"), tops[d]) for d in sets],
        ])
    header = ["encoder", "M", "role"] + [dname(d) for d in sets]
    return tabular("lll" + "r" * len(sets), header, body, rules=(2, 4, 6))


def t_retention(data: list[dict[str, Any]]) -> str:
    """target mAP / source mAP for the one head fitted on ``market1501/train``.

    The absolute source column stays beside the ratios: a retention ratio flatters a weak
    source model, and a table without its denominators cannot be checked for that.
    """
    specs = [s for s in ABLATION if R.pick(data, spec=s)]
    shown = names(data, specs)
    targets = [d for d in datasets_in(data) if d != "market1501"]
    body = []
    for spec in specs:
        source = cell(data, spec, "market1501", "arcface")
        cells = []
        for d in targets:
            target = cell(data, spec, d, "arcface")
            cells.append("--" if not source or target is None else f"{target / source:.2f}")
        body.append([shown[spec], num(source), *cells])
    header = ["encoder", "Market (source)"] + [dname(d) for d in targets]
    return tabular("lr" + "r" * len(targets), header, body)


def t_geometry(data: list[dict[str, Any]]) -> str:
    """Resolution and fit, holding the encoder family and the head fixed."""
    specs = [s for s in ordered(data)
             if R.ENCODERS[s]["family"] == "agglomerative"
             or s.startswith("timm-vit-base-patch16-clip")]
    shown, sets = names(data, specs), datasets_in(data)
    tops = {d: best([cell(data, s, d, "arcface") for s in specs]) for d in sets}
    body = []
    for spec in specs:
        sample = R.pick(data, spec=spec)[0]
        body.append([
            shown[spec], res(sample["resolution"]), sample["resize"],
            *[bold(cell(data, spec, d, "arcface"), tops[d]) for d in sets],
        ])
    header = ["encoder", "input", "fit"] + [dname(d) for d in sets]
    return tabular("lll" + "r" * len(sets), header, body, rules=(3, 6))


def t_margin(data: list[dict[str, Any]]) -> str:
    """Where an angular margin beats a plain linear head, and where it does not."""
    specs = [s for s in ABLATION if R.pick(data, spec=s)]
    shown, sets = names(data, specs), datasets_in(data)
    body = []
    for spec in specs:
        cells = []
        for d in sets:
            linear, arc = cell(data, spec, d, "linear"), cell(data, spec, d, "arcface")
            cells.append("--" if not linear or arc is None else _delta(arc / linear - 1))
        body.append([shown[spec], *cells])
    return tabular("l" + "r" * len(sets), ["encoder"] + [dname(d) for d in sets], body)


def _delta(fraction: float, places: int = 0) -> str:
    text = f"{fraction * 100:+.{places}f}\\%"
    return text if fraction >= 0 else f"\\loss{{{text}}}"


def t_cost(data: list[dict[str, Any]]) -> str:
    """What the frozen features cost, per encoder, on the one card this study ran on."""
    specs = ordered(data)
    shown = names(data, specs)
    body = []
    for spec in specs:
        frozen = main_rows(data, "market1501", spec=spec, head="none")
        rate = frozen[0]["items_per_second"] if frozen else None
        sample = R.pick(data, spec=spec)[0]
        body.append([
            shown[spec], res(sample["resolution"]), f"{sample['params_m']}",
            "--" if rate is None else f"{rate:,.1f}",
        ])
    return tabular("lllr", ["encoder", "input", "params (M)", "img/s"], body)


def t_coverage(data: list[dict[str, Any]]) -> str:
    """Which (encoder, dataset) pairs are measured, so an absence is visible as an absence."""
    specs, sets = ordered(data), datasets_in(data)
    shown = names(data, specs)
    body = []
    for spec in specs:
        cells = [str(len(main_rows(data, d, spec=spec))) if main_rows(data, d, spec=spec)
                 else "\\loss{--}" for d in sets]
        body.append([shown[spec], res(R.pick(data, spec=spec)[0]["resolution"]), *cells])
    return tabular("ll" + "r" * len(sets), ["encoder", "input"] + [dname(d) for d in sets], body)



FAMILY = {
    "student": ["torchhub-c-radio-v4-h-224", "torchhub-c-radio-v4-so400m-224"],
    "siglip": ["timm-vit-giantopt-patch16-siglip2-256", "timm-vit-so400m-patch14-siglip2-224"],
    "dino": ["timm-vit-huge-plus-patch16-dinov3-224", "timm-vit-large-patch16-dinov3-224"],
}
"""The ablation's three families, at one resolution each. Best-of-family is the fair
comparison: the question is whether agglomeration beats the teachers you could have used,
not whether it beats a particular checkpoint of one."""


def family_best(data, family, dataset):
    values = [cell(data, s, dataset, "arcface") for s in FAMILY[family]]
    return best(values)


def t_bracket(data):
    """Where the student sits relative to its teacher families, and how far apart they are.

    The prediction agglomeration makes is that a student inherits a blend. A blend is worse
    than the better teacher exactly where the teachers disagree, so the two columns that
    matter are the teachers' spread and the student's position inside it.
    """
    body = []
    for dataset in datasets_in(data):
        sig, din = family_best(data, "siglip", dataset), family_best(data, "dino", dataset)
        stu = family_best(data, "student", dataset)
        if None in (sig, din, stu):
            body.append([dname(dataset), num(sig), num(din), num(stu), "--", "--", "--"])
            continue
        lo, hi = min(sig, din), max(sig, din)
        spread = f"{hi / lo:.2f}{TIMES}"
        above, below = "\\loss{above}", "\\loss{below}"
        inside = "yes" if lo <= stu <= hi else (above if stu > hi else below)
        body.append([dname(dataset), num(sig), num(din), f"\\textbf{{{num(stu)}}}",
                     spread, inside, _delta(stu / hi - 1, places=1)])
    header = ["dataset", "SigLIP2", "DINOv3", "C-RADIOv4", "spread", "bracketed",
              "vs.\\ best"]
    return tabular("lrrrrcr", header, body)


# --------------------------------------------------------------------------- macros


def macros(data: list[dict[str, Any]]) -> str:
    """Every number the prose quotes, as a macro. The prose never types a metric."""
    out = ["% generated by tools/gen_tables.py from results/runs — do not edit"]

    def put(name: str, text: str) -> None:
        out.append(f"\\newcommand{{\\{name}}}{{{text}}}")

    put("nRuns", f"{len(data):,}")
    put("nEncoderConfigs", str(len({r["spec"] for r in data})))
    put("nEncoders", str(len({r["label"] for r in data})))
    put("nDatasets", str(len({r["dataset"] for r in data})))
    put("nProtocols", str(len({r["protocol"] for r in data})))
    put("nHeads", str(len({r["head"] for r in data})))
    put("nHeadRecipes", str(len({r["head_recipe"] for r in data})))
    put("nFitSplits", str(len({r["head_fit"] for r in data if r["head_fit"]})))
    put("nHeadIdentities", f"{_head_source(data, 'n_identities'):,}")
    put("nHeadImages", f"{_head_source(data, 'n_images'):,}")

    blocks = (_headline(data) + _readout(data) + _ablation(data) + _bracket_macros(data)
              + _fitsplit_macros(data))
    return "\n".join(out + blocks) + "\n"


def _fitsplit_macros(data: list[dict[str, Any]]) -> list[str]:
    """What the fit split is worth, averaged over every encoder rather than read on one.

    The table is the lead encoder because every other table in the paper is; these are means,
    because a claim about what supervision buys should not rest on the encoder that happens to
    win. Same rows, two altitudes.
    """
    def mean(dataset: str, recipe: str, fit: str | None) -> float | None:
        values = [row["mAP"] for row in main_rows(data, dataset, head_recipe=recipe,
                                                  head_fit=fit) if row["mAP"] is not None]
        return sum(values) / len(values) if values else None

    lines: list[str] = []
    for dataset, tag in (("market1501", "Market"), ("msmt17", "Msmt")):
        frozen = mean(dataset, "none", None)
        lines.append(f"\\newcommand{{\\fitFrozen{tag}}}{{{num(frozen)}}}")
        for recipe in FITTED:
            name = HEAD_NAME[recipe].capitalize()
            here = mean(dataset, recipe, dataset)
            there = mean(dataset, recipe, next(f for f in FIT_SPLITS if f != dataset))
            lines.append(f"\\newcommand{{\\fit{name}{tag}Here}}{{{num(here)}}}")
            lines.append(f"\\newcommand{{\\fit{name}{tag}Else}}{{{num(there)}}}")
            if None not in (here, there, frozen) and here > frozen:
                # How much of what the head buys survives being fitted somewhere else. The
                # denominator is the in-domain gain over frozen, so this is a share of an
                # effect the paper already reports rather than a new quantity.
                share = (there - frozen) / (here - frozen) * 100
                lines.append(f"\\newcommand{{\\fitShare{name}{tag}}}{{{share:.0f}\\%}}")
                lines.append(f"\\newcommand{{\\fitSwing{name}{tag}}}{{{here - there:.3f}}}")
    for field, name in (("head_images", "nHeadImagesMsmt"),
                        ("head_identities", "nHeadIdentitiesMsmt")):
        seen = [r[field] for r in data if r["head_fit"] == "msmt17" and r[field]]
        lines.append(f"\\newcommand{{\\{name}}}{{{max(seen, default=0):,}}}")
    return lines


def _bracket_macros(data: list[dict[str, Any]]) -> list[str]:
    """Per dataset: how far apart the teacher families are, and how far the student is from
    the better of them. These two quantities are the whole of the transfer argument."""
    lines = []
    for dataset, tag in DATASET_TAG.items():
        sig, din = family_best(data, "siglip", dataset), family_best(data, "dino", dataset)
        stu = family_best(data, "student", dataset)
        if None in (sig, din):
            continue
        lo, hi = min(sig, din), max(sig, din)
        lines.append(f"\\newcommand{{\\spread{tag}}}{{{hi / lo:.2f}}}")
        if stu is not None:
            lines.append(f"\\newcommand{{\\deficit{tag}}}{{{(stu / hi - 1) * 100:+.0f}}}")
            lines.append(f"\\newcommand{{\\familyStudent{tag}}}{{{num(stu, 4)}}}")
        lines.append(f"\\newcommand{{\\familySiglip{tag}}}{{{num(sig, 4)}}}")
        lines.append(f"\\newcommand{{\\familyDino{tag}}}{{{num(din, 4)}}}")
    return lines


def _head_source(data: list[dict[str, Any]], field: str) -> int:
    """The head's training split, read off a record rather than restated here."""
    row = R.one(data, spec=LEAD, head="arcface", dataset="market1501")
    if row is None:  # pragma: no cover
        return 0
    record = R.report.load(_path_of(row))
    source = (((record["inputs"]["features"]["encoder"] or {}).get("head") or {})
              .get("source") or {})
    return int(source.get(field, 0))


def _path_of(row: dict[str, Any]) -> Path:
    protocol = row["protocol"].replace("/", "_")
    return R.RUNS / f"{row['spec']}.{row['head']}" / row["dataset"] / protocol / "results.json"


def _headline(data: list[dict[str, Any]]) -> list[str]:
    lead256 = "torchhub-c-radio-v4-h-256x128"
    pairs = {
        "bestMarketMAP": cell(data, lead256, "market1501", "arcface"),
        "bestMarketRone": cell(data, lead256, "market1501", "arcface", "R1"),
        "leadMarketFrozen": cell(data, LEAD, "market1501", "none"),
        "leadMarketPCA": cell(data, LEAD, "market1501", "pca"),
        "leadMarketLinear": cell(data, LEAD, "market1501", "linear"),
        "leadMarketArc": cell(data, LEAD, "market1501", "arcface"),
        "leadMarketMINP": cell(data, LEAD, "market1501", "arcface", "mINP"),
        "leadVraiFrozen": cell(data, LEAD, "vrai", "none"),
        "leadVraiPCA": cell(data, LEAD, "vrai", "pca"),
        "leadVraiArc": cell(data, LEAD, "vrai", "arcface"),
        "leadOccludedFrozen": cell(data, LEAD, "occluded-reid", "none"),
        "leadOccludedPCA": cell(data, LEAD, "occluded-reid", "pca"),
        "leadOccludedArc": cell(data, LEAD, "occluded-reid", "arcface"),
        "teacherMarketMINP": cell(data, "timm-vit-giantopt-patch16-siglip2-256",
                                  "market1501", "arcface", "mINP"),
    }
    lines = [f"\\newcommand{{\\{k}}}{{{num(v, 4)}}}" for k, v in pairs.items()]
    ratios = {
        "leadMarketGain": _ratio(pairs["leadMarketArc"], pairs["leadMarketFrozen"], 1),
        "minpGap": _ratio(pairs["leadMarketMINP"], pairs["teacherMarketMINP"]),
    }
    return lines + [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in ratios.items()]


def _ratio(top: float | None, bottom: float | None, places: int = 2) -> str:
    return "--" if not top or not bottom else f"{top / bottom:.{places}f}"


def _readout(data: list[dict[str, Any]]) -> list[str]:
    specs = ordered(data)
    frozen = {s: cell(data, s, "market1501", "none") for s in specs}
    probed = {s: cell(data, s, "market1501", "arcface") for s in specs}
    rf, rp = _rank(frozen), _rank(probed)
    lines = []
    for name, spec in (("Siglipg", "timm-vit-giantopt-patch16-siglip2-256"),
                       ("Siglipso", "timm-vit-so400m-patch14-siglip2-224"),
                       ("Dinohp", "timm-vit-huge-plus-patch16-dinov3-224"),
                       ("Radioh", LEAD)):
        lines += [
            f"\\newcommand{{\\rank{name}Frozen}}{{{rf.get(spec, '--')}}}",
            f"\\newcommand{{\\rank{name}Probed}}{{{rp.get(spec, '--')}}}",
            f"\\newcommand{{\\map{name}Frozen}}{{{num(frozen.get(spec), 4)}}}",
            f"\\newcommand{{\\map{name}Probed}}{{{num(probed.get(spec), 4)}}}",
            # one decimal, to match the gain column of the readout table
            f"\\newcommand{{\\gain{name}}}{{{_ratio(probed.get(spec), frozen.get(spec), 1)}}}",
        ]
    return lines


DATASET_TAG = {"market1501": "Market", "cuhk03-np": "Cuhk", "occluded-reid": "Occluded",
               "vrai": "Vrai", "vric": "Vric", "ccvid": "Ccvid", "msmt17": "Msmt"}


def _ablation(data: list[dict[str, Any]]) -> list[str]:
    roles = {"student": LEAD, "teacher": "timm-vit-giantopt-patch16-siglip2-256",
             "dino": "timm-vit-huge-plus-patch16-dinov3-224",
             "siglipsm": "timm-vit-so400m-patch14-siglip2-224",
             "clip": "timm-vit-base-patch16-clip-224-squash",
             "clipcrop": "timm-vit-base-patch16-clip-224"}
    lines = []
    for dataset, tag in DATASET_TAG.items():
        for role, spec in roles.items():
            value = cell(data, spec, dataset, "arcface")
            lines.append(f"\\newcommand{{\\{role}{tag}}}{{{num(value, 4)}}}")
    return lines


# --------------------------------------------------------------------------- main

WRITERS: dict[str, Callable[[list[dict[str, Any]]], str]] = {
    "tbl-datasets.tex": t_datasets,
    "tbl-encoders.tex": t_encoders,
    "tbl-readout.tex": t_readout,
    "tbl-frozen.tex": t_frozen,
    "tbl-main.tex": t_main,
    "tbl-main-r1.tex": t_main_r1,
    "tbl-heads.tex": t_heads,
    "tbl-fitsplit.tex": t_fitsplit,
    "tbl-ablation.tex": t_ablation,
    "tbl-bracket.tex": t_bracket,
    "tbl-retention.tex": t_retention,
    "tbl-geometry.tex": t_geometry,
    "tbl-margin.tex": t_margin,
    "tbl-cost.tex": t_cost,
    "tbl-coverage.tex": t_coverage,
    "macros.tex": macros,
}

BANNER = "% generated by tools/gen_tables.py from results/runs — edit the runs, not this\n"


def main() -> int:
    loaded = R.load()
    if not loaded:
        raise SystemExit(f"no run records under {R.RUNS}; run `python results/run.py all` first")
    # A dataset with no entry in datasets.json has no name, no short header and no declared
    # regime, so no table can render it -- and counting its runs toward `nRuns` would put a
    # number in the abstract that no table supports. Set those aside, loudly.
    data = [row for row in loaded if row["dataset"] in R.DATASETS]
    for dataset in sorted({r["dataset"] for r in loaded} - set(R.DATASETS)):
        n = len([r for r in loaded if r["dataset"] == dataset])
        print(f"  set aside: {n} runs on {dataset!r} -- not in tools/datasets.json")
    check_heads(data)
    OUT.mkdir(exist_ok=True)
    for name, writer in WRITERS.items():
        text = writer(data)
        body = text if name == "macros.tex" else BANNER + text + "\n"
        (OUT / name).write_text(body, encoding="utf-8")
    print(f"{len(data)} run records -> {len(WRITERS)} files in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
