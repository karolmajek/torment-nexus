---
title: "The sweep backlog — what to add to the matrix, and what to keep out"
kb_id: reid-sweep-backlog
type: live gap table / build order
domain: computer-vision, re-identification, evaluation-tooling
tags: [backlog, sweep, matrix, probe, head, encoder, results, c1, live]
retrieved: 2026-09-08
confidence: |
  high — every "state" cell is read from the working tree of `results/` and `reidbench/` on 2026-09-08:
  encoder specs, probe specs, run counts and the coverage matrix are enumerated from the generated table,
  not inferred.
  medium — the sizing estimates are estimation.
supersedes: null
related: [reid-head-fit-domain-decisions, reid-reidbench-owed, reid-agglomerative-probe-protocol, probing-protocols, reid-contribution-ledger-2026]
---

# The sweep backlog

> **Live table. Keep it current or delete it.** It answers one question — *what should go into the
> results matrix next, and what should stay out of it?* — and it is only useful while its "state"
> column matches the tree.

## TL;DR

Three pages divide this work and none of them should absorb another's rows:

| Page | Owns |
|---|---|
| [38-reidbench-owed.md](38-reidbench-owed.md) | what the **library** owes — adapters, protocol values, `check` axes, provenance records |
| [92 §14.9](92-protocol-agglomerative-probe.md) | what **C1 has not run** — missing datasets, EUPE, the SAM3 ablation |
| **this page** | what the **matrix** should gain or refuse — heads, encoder-axis values, swept axes |

The axis vocabulary — encoder, head, measure — and the reasoning behind each head is
[probing-protocols-kb.md](../field/probing-protocols-kb.md). Nothing here restates it.

**The one-line answer, and it is now a result rather than a flaw:** the matrix's biggest problem was a
uniform confound — every head was fitted on `market1501/train`, so every non-Market number was a
cross-domain-head number. **Fixed on 2026-09-02** by refitting all three heads on `msmt17/train`
(item 1 below). It cost one JSON file per head and no GPU, and the swap turned out to move mAP by
±0.27 for ArcFace against ±0.006 for PCA — so the confound was real and is now measured in both
directions. The numbers, and the calibration mirror that came with them, are
[94-head-fit-domain-and-decision-metrics.md](94-head-fit-domain-and-decision-metrics.md).

---

## 1. State, 2026-09-08

Read from [`results/table.md`](../../results/table.md), which is generated.

| | count | note |
|---|---|---|
| Encoders | **14** | includes the teachers — DINOv3-L/H+, SigLIP2-SO400M/g-256/g-384, TIPSv2 — so the §7 teacher ablation is runnable |
| Heads | **7** | `none`, and `pca` / `linear` / `arcface` fitted on **each of** `market1501/train` and `msmt17/train` |
| Datasets in the matrix | **9** | 7 further pages cannot run: `veri776` (adapter ✅, no data), `soma` (adapter ✅, not on disk), `last` (data ✅, adapter written but **deliberately unregistered** — [last.md](../../datasets/last.md) §8), `vehicleid` / `veri-wild` (no adapter), `crowdtrack` (a tracking set, no retrieval protocol to write), `market1501-attribute` (labels, not a retrieval set) |
| Cells measured | **840 / 980** | 271.9 h of encoding over 108 feature stores, 939 run records. Read from the generated table on 2026-09-08. The 140-cell gap is exactly the two encoders below: every other (encoder, head, dataset, protocol) cell in the matrix is measured, and `run.py plan --exclude tipsv2-448 --exclude siglip2-384` reports 0 todo |
| Encoders at 0/70 | 2 | `tipsv2-448`, `siglip2-384` — specs exist, never run. Now measured rather than guessed: **1.4** and **2.7 img/s** on 120 images, against 5.4-80 for the twelve that ran. They are 61% of a 14-encoder sweep's GPU cost, which is why they were held back — roughly 11 days to add them across all nine datasets |

Two axes landed since the matrix was three datasets wide, both placed correctly — `preprocess.resize:
crop\|squash` as an encoder-axis value, and tracklet `sample`/`pool` via
[`results/aggregate.py`](../../results/aggregate.py), whose pooling mode goes *inside* the encoder
description so mean- and max-pooled tracklets cannot share a cache key.

---

## 2. The backlog

Ranked by value per unit work. "Forces it" names the claim that is currently unsupportable without it.

| # | Item | Work | Forces it | State |
|---|---|---|---|---|
| 1 | ~~**A second train split for the heads**~~ | one JSON per head, no code | ~~Every non-Market row is a cross-domain-head number~~ | ✅ **done 2026-09-02** — 288 runs, ~8.5 h on CPU, no encoding (the train-split features were already cached). Results in [94](94-head-fit-domain-and-decision-metrics.md) |
| 2 | **A crop/squash pair for a strong encoder** | one JSON, ~40 min | [92 §14.9](92-protocol-agglomerative-probe.md) — CLIP is the only encoder with both specs and is too weak on CUHK03 to resolve the geometry question | not started |
| 3 | **Finish the two 0/70 encoders** | none — specs exist | `siglip2-384` is the resolution control for `siglip2-256`, the encoder that wins frozen; `tipsv2` is an unrelated family and a free breadth row | specs written, never run |
| 4 | **BNNeck head** | ~15 lines for BNNeck+CE; the real BoT recipe is more | The ReID community's own baseline head is absent, and a reviewer will ask. See [probing-protocols §3.3](../field/probing-protocols-kb.md) | not started |
| 5 | **Oracle/random guard as a routine step** | two lines per new adapter | [92 §14.9](92-protocol-agglomerative-probe.md) — it is what separated "this dataset is hard" from "the new adapter is silently wrong" on CUHK03 | done once, ad hoc |
| 6 | ~~**One `euclidean` control row at `head = none`**~~ | one flag, already in the CLI | ~~`score.euclidean` does not L2-normalise while `score.cosine` does~~ | ✅ **done 2026-09-06** — `run.py` gained `--metric`, writing to its own `…@1.euclidean` run directory so no cosine cell is touched. 100 runs on CPU from cached features (12 encoders on each of seven datasets — CCVID twice for its two protocols — plus 4 of 12 on `market1501-500k`). **Result: it changes nothing on six of seven datasets** (|mean diff| < 0.4 mAP; MARS is 0.000) and +6.8 mAP on CCVID. That vindicates §3's call — a crossed `metric` axis would have doubled 840 cells to expose one dataset. msmt17 is still owed: skipped to avoid RAM contention with the GPU leg |
| 7 | **CosFace / Circle** | one branch in `fit_torch`'s classifier | Nothing yet. ArcFace already represents the family | not started |

### 2.1 Why item 4 is two items, not one

`probe.py`'s contract is one affine map, `e = W(x/‖x‖) + b`. BatchNorm at eval **is** diagonal-affine,
so the BNNeck half folds into that contract with no change to `apply`. The **triplet** half does not:
[`probe.py`](../../results/probe.py) states plainly that it runs no P×K sampler because neither of its
losses mines pairs, and a triplet term is exactly the loss that would need one. BNNeck+CE is cheap;
BNNeck+CE+triplet buys the sampler too.

---

## 3. What should not enter the matrix

Refusals, with the reason each one is a refusal rather than a backlog item.

| Item | Why not |
|---|---|
| **`metric` as a swept axis** | Doubles every row for a difference mAP cannot see — mAP is rank-only, and on L2-normalised features euclidean and cosine are rank-equivalent. One control row (§2 item 6), never a crossed axis |
| **`truncate` / `asnorm` / `rerank` as axes** | `rerank` is *contradictory* with the open-set metrics — query-adaptive transforms destroy the global threshold ([open-world §3](../field/open-world-rejection-calibration-kb.md)); `truncate` belongs to C16/MRL, not C1; `asnorm` needs a cohort set nothing here has. Design decision 5: grow when an experiment forces it |
| **`--open-set` in the sweep** | Blocked on a **protocol**, not on data — corrected 2026-09-04. `market1501-500k` is measured in full since 2026-09-08, but it would not have unblocked this anyway: it is a **closed-set** protocol. Every query still has a true match; the 500,000 distractors add gallery clutter, not non-mated queries. Non-mated probes come from `splits.identity_disjoint` rewriting the `split` column into `probe_nonmated`, scored under `openset/probe-vs-enrolled@1` — a manifest transform that already ships and works on any dataset. So the item is one seeded transform plus `--open-set`, and `market1501-500k`'s contribution is a deployment-scale gallery to run it against, not the non-mates themselves. [`run.py`](../../results/run.py) still emits nothing rather than a column of NaN, which is right |
| **Attentive probe, PCB** | Both break the affine contract: they read *patch tokens*, so they are a different extraction path, not a new head spec. See [probing-protocols §7](../field/probing-protocols-kb.md) |
| **GeM as a head** | It is an encoder-axis *pooling* value, not a head, and needs patch-token support in `encode.py`. Filed against the library in [38 §1.2](38-reidbench-owed.md) |
| **Probe trainers inside `reidbench`** | Design decision C, plus the deliberate absence of a `probe` extra in the package's `pyproject.toml`. The split is visibly working: `probe.py` and `aggregate.py` both hand results back as content-addressed stores the library already reads |

---

## 4. Retrieval hints

Answers questions of the form: *what should we run next · what is missing from the results matrix ·
which probe heads are still unimplemented · should we sweep the metric axis · why is open-set not in
the table · can we add an attentive probe · what is the head training-split confound · what should
never go into reidbench.*

**Single most quotable fact:** the second head training split has landed, and it showed the confound was
worth ±0.27 mAP for ArcFace and ±0.006 for PCA — the swing scales with how supervised the head is. The
matrix is now 840 / 980. See [94](94-head-fit-domain-and-decision-metrics.md).
