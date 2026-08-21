---
title: "Market-1501 — the near-ceiling secondary, and the format everything else imitates"
kb_id: dataset-market1501
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, market1501, person-reid, distractors, junk-boxes]
retrieved: 2026-08-21
confidence: |
  high — counts, filename convention and the distractor/junk rule are pinned by the adapter and
  protocol that already ship in `reidbench` and are covered by its tests.
  medium — current download availability; the project page has changed hosts more than once.
related: [dataset-market1501-attribute, dataset-msmt17, dataset-cuhk03-np, reid-benchmarks-datasets]
---

# Market-1501

> The in-domain secondary: report it, do not lead with it. It is close enough to ceiling that a
> two-point difference here means less than a two-point difference almost anywhere else.

## 1. Facts

Single source of truth for this dataset's numbers.

```toml
[dataset]
name = "Market-1501"
kind = "person"
role = "in-domain secondary; near ceiling, report but do not lead with it"
licence = "research/academic use only; no redistribution"
licence_verified = false
commercial_ok = false
access = "request"
homepage = "https://zheng-lab.cecs.anu.edu.au/Project/project_reid.html"
dir = "market1501/Market-1501-v15.09.15"
adapter = "market1501"
protocols = ["market1501/official@1"]
checked_on = "2026-08-21"
link_verified = false

[counts]
identities = 1501
images = 32668
cameras = 6

[counts.train]
identities = 751
images = 12936

[counts.query]
identities = 750
images = 3368

[counts.gallery]
identities = 750          # plus distractor and junk boxes, which carry pid -1
images = 19732

[expect]
"bounding_box_train" = 12936
"query" = 3368
"bounding_box_test" = 19732

[fetch]
manual = """
Liang Zheng's project page has moved hosts more than once and the canonical archive
(Market-1501-v15.09.15.zip, ~1.7 GB) circulates widely. Prefer the project page; if you take a
mirror, record where it came from in this block and say so in any paper.
"""
```

## 2. What it is

Tsinghua campus, six cameras (five HD, one low-res), boxes from DPM. Clean, well-lit, mostly
frontal — the easiest of the classic four, and the most reported. Its lasting contribution is
arguably the *format*: `bounding_box_train/`, `query/`, `bounding_box_test/` with identity and
camera encoded in the filename is now the default layout that CUHK03-NP and half the field
re-publish into.

## 3. What is inside

```
market1501/Market-1501-v15.09.15/
  bounding_box_train/
  query/
  bounding_box_test/
```

Filenames are `{pid:04d}_c{camid}s{seq}_{frame}_{n}.jpg`. Per-directory counts are in §1.

## 4. Splits and protocol

```yaml
name:    market1501/official@1
query:   {split: query}
gallery: {split: gallery}
exclude: [same_uid, same_pid_same_camid, {pid_in: [-1]}]
```

**The distractor rule is the interesting part.** `pid == -1` marks distractor boxes and
`pid == 0` marks junk boxes; the shipped adapter collapses both to `-1` and **keeps them in the
gallery**, where the protocol's `pid_in: [-1]` predicate excludes them from *scoring*. Those are
different things: a distractor that is never ranked is a distractor that never distracted.

Deleting them would produce a different, easier gallery — which is why
`market1501(root, distractors=False)` exists as a *different manifest*, and why a number
produced that way belongs under a different protocol name if it is reported at all.

## 5. How to get it

`access = request`. Liang Zheng's project page is the canonical source and has moved hosts more
than once; the archive circulates widely. Prefer the project page. If you take a mirror, record
where it came from — same reasoning as [msmt17.md](msmt17.md) §4, with much lower stakes,
because Market's terms are less contested and its provenance is not in dispute.

## 6. Licence and citation

Research/academic use, no redistribution. `licence_verified = false`: nobody in this project has
read the current terms on the current host.

```bibtex
@inproceedings{zheng2015scalable,
  title={Scalable Person Re-identification: A Benchmark},
  author={Zheng, Liang and Shen, Liyue and Tian, Lu and Wang, Shengjin and Wang, Jingdong and Tian, Qi},
  booktitle={ICCV}, year={2015}
}
```

## 7. Traps

- **Reporting Market alone.** Near ceiling, no domain shift, no occlusion, no clothing change.
  The standing rule is Market *plus* MSMT17 *plus* a cross-domain pair.
- **Dropping the distractors.** §4 — quietly raises every number.
- **Single-query vs multi-query.** The official protocol is single-query. Multi-query numbers are
  higher and are a different table.
- **The self-retrieval shape.** Every query identity also appears in the gallery under the same
  camera. An evaluator that forgets same-camera exclusion retrieves the query's own twin at
  similarity 1.0 and reports near-perfect Rank-1. `reidbench` keeps that bug reachable on
  purpose, under a name that says so, as a test that the exclusion rule is doing something.

## 8. Status in this project

| | |
|---|---|
| On disk | no |
| `reidbench` adapter | ✅ `adapters/market1501.py` |
| `reidbench` protocol | ✅ `market1501/official@1` |
| Provenance record | ✅ `market1501` |
| Access | request; not yet started |
