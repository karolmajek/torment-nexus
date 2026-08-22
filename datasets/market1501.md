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
related: [dataset-market1501-500k, dataset-market1501-attribute, dataset-msmt17, dataset-cuhk03-np,
  reid-benchmarks-datasets]
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
licence = "research use only; no redistribution, no commercial use"
licence_verified = true   # readme.txt in the release states it; quoted in §6
commercial_ok = false
access = "request"
homepage = "https://zheng-lab-anu.github.io/Project/project_reid.html"
dir = "Market-1501-v15.09.15"
adapter = "market1501"
protocols = ["market1501/official@1"]
checked_on = "2026-08-22"
link_verified = true

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
identities = 750
images = 19732            # everything in bounding_box_test/
junk = 3819               # pid -1, dropped before ranking
distractors = 2798        # pid 0, ranked, matching nothing
ranked = 15913            # images - junk; the gallery a query is actually searched against

[expect]
"bounding_box_train" = 12936
"query" = 3368
"bounding_box_test" = 19732

[fetch]
manual = """
Liang Zheng's project page has moved hosts more than once and the canonical archive
(Market-1501-v15.09.15.zip, ~1.7 GB) circulates widely. Prefer the project page; if you take a
mirror, record where it came from in this block and say so in any paper.

The +500k distractor release is a separate download and a different gallery:
datasets/market1501-500k.md.
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
Market-1501-v15.09.15/
  bounding_box_train/
  query/
  bounding_box_test/
  gt_bbox/ gt_query/ readme.txt   # the authors' MATLAB evaluation inputs; unused here
```

Filenames are `{pid:04d}_c{camid}s{seq}_{frame}_{n}.jpg`. Per-directory counts are in §1.

## 4. Splits and protocol

```yaml
name:    market1501/official@1
query:   {split: query}
gallery: {split: gallery}
exclude: [same_uid, same_pid_same_camid, {pid_in: [-1]}]
```

**The two unlabelled classes are the interesting part, and they are not the same class.**

| filename | pid | in the ranking? | what it is |
|---|---|---|---|
| `-1_c…` | `-1` | no — `pid_in: [-1]` drops it | junk: a detector misfire, mostly background |
| `0000_c…` | `0` | **yes**, and it matches nothing | a distractor: a real person nobody labelled |

Junk leaves the ranking, which promotes everything below it. Distractors stay in and cost
precision — that is their entire job, and it is why the gallery a query is really searched
against is 15,913 boxes, not 19,732 and not 13,115.

`reidbench` collapsed the two onto `-1` until 2026-08-22, which scored against 13,115 boxes
under this protocol's name. **Measured** on the same embeddings, that inflated the table's
CLIP row by +0.06 mAP and +0.15 R1 — small, because an encoder this weak rarely had a true
match near the distractors anyway. The size of the error is a property of the model, not of
the rule, and it has not been measured for a strong one. The reason to get it right is not
the magnitude: it is that a number from a 13,115-box gallery is not a Market-1501 number and
cannot be put beside one.

Deleting the distractors on purpose is a different, easier gallery — which is why
`market1501(root, distractors=False)` exists as a *different manifest*, and why a number
produced that way belongs under a different protocol name if it is reported at all. Adding
500,000 more of them is [market1501-500k](market1501-500k.md).

## 5. How to get it

`access = request`. Liang Zheng's project page is the canonical source and has moved hosts more
than once; the archive circulates widely. Prefer the project page. If you take a mirror, record
where it came from — same reasoning as [msmt17.md](msmt17.md) §4, with much lower stakes,
because Market's terms are less contested and its provenance is not in dispute.

## 6. Licence and citation

The terms ship inside the archive, in `readme.txt`, and that is where they were read:

> This dataset should be used for research only. Please DO NOT distribute or use it for
> commercial purpose.

That is the whole licence. It is short enough to quote, which is why `licence_verified = true`
here and `false` on [market1501-500k](market1501-500k.md), whose archive carries no such file.

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
- **Treating `pid 0` as junk.** §4. It needs no bad intent, nothing in the output looks wrong,
  and the gallery you report against is 2,798 boxes smaller than everyone else's.
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
| On disk | ✅ |
| `reidbench` adapter | ✅ `adapters/market1501.py` |
| `reidbench` protocol | ✅ `market1501/official@1` |
| Provenance record | ✅ `market1501` |
| Measured | ✅ [results/table.md](../results/table.md) |
