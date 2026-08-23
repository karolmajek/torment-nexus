---
title: "Market-1501 — the near-ceiling secondary, and the format everything else imitates"
kb_id: dataset-market1501
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, market1501, person-reid, distractors, junk-boxes]
retrieved: 2026-08-22
confidence: |
  high — counts, filename convention and the distractor/junk rule are pinned by the adapter and
<<<<<<< HEAD
  protocol that already ship in `reidbench` and are covered by its tests.
  medium — current download availability; the project page has changed hosts more than once.
related: [dataset-market1501-500k, dataset-market1501-attribute, dataset-msmt17, dataset-cuhk03-np,
  reid-benchmarks-datasets]
=======
  protocol that already ship in `reidbench`, and as of 2026-08-22 by the archive itself: it was
  downloaded, checksummed, unpacked and verified against this page.
  high — download availability. The Google Drive link on the current project page serves the
  archive without a form, an agreement or a quota wall; sha256 recorded below.
related: [dataset-market1501-attribute, dataset-msmt17, dataset-cuhk03-np, reid-benchmarks-datasets]
>>>>>>> 9c9f3e0 (market access)
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
<<<<<<< HEAD
licence = "research use only; no redistribution, no commercial use"
licence_verified = true   # readme.txt in the release states it; quoted in §6
commercial_ok = false
access = "request"
homepage = "https://zheng-lab-anu.github.io/Project/project_reid.html"
dir = "Market-1501-v15.09.15"
=======
licence = "research use only; no redistribution, no commercial use (readme.txt, in the archive)"
licence_verified = true
commercial_ok = false
access = "gdrive"
homepage = "https://zheng-lab-anu.github.io/Project/project_reid.html"
dir = "market1501/Market-1501-v15.09.15"
>>>>>>> 9c9f3e0 (market access)
adapter = "market1501"
protocols = ["market1501/official@1"]
checked_on = "2026-08-22"
link_verified = true

[counts]
identities = 1501
images = 32668
cameras = 6
archive_mb = 145.7          # 152_733_771 bytes, not the ~1.7 GB this page used to claim
unpacked_mb = 270

[counts.train]
identities = 751
images = 12936

[counts.query]
identities = 750
images = 3368

[counts.gallery]
<<<<<<< HEAD
identities = 750
images = 19732            # everything in bounding_box_test/
junk = 3819               # pid -1, dropped before ranking
distractors = 2798        # pid 0, ranked, matching nothing
ranked = 15913            # images - junk; the gallery a query is actually searched against
=======
identities = 750          # plus distractor and junk boxes, which carry pid -1
images = 19732
distractors = 2798        # filenames beginning 0000_ ; measured, the project page says 2793
junk = 3819               # filenames beginning -1_
labelled = 13115

[counts.extra]
gt_bbox = 25259           # hand-drawn boxes, used to assign good/distractor/junk. Not for train or test
gt_query = 6736           # .mat index files, 2 per query. The shipped evaluator does not need them
>>>>>>> 9c9f3e0 (market access)

[expect]
"bounding_box_train" = 12936
"query" = 3368
"bounding_box_test" = 19732
"gt_bbox" = 25259
"gt_query" = 6736

[fetch]
gdrive_id = "0B8-rUzbwVRk0c054eEozWG9COHM"
resourcekey = "0-8nyl7K9_x37HlQm34MmrYQ"
sha256 = "416bb77b5a2449b32e936f623cbee58becf1a9e7e936f36380cb8f9ab928fe96"
fetched_on = "2026-08-22"
manual = """
<<<<<<< HEAD
Liang Zheng's project page has moved hosts more than once and the canonical archive
(Market-1501-v15.09.15.zip, ~1.7 GB) circulates widely. Prefer the project page; if you take a
mirror, record where it came from in this block and say so in any paper.

The +500k distractor release is a separate download and a different gallery:
datasets/market1501-500k.md.
=======
DOWNLOADED AND VERIFIED on 2026-08-22. `access` was "request" on this page until then and that
was simply wrong: there is no form and no agreement, the project page links a public Drive file.
`gdown 0B8-rUzbwVRk0c054eEozWG9COHM` is enough — the bare id resolves despite the old-style
resourcekey, so `get.py fetch market1501` works unmodified. 146 MB, about ten seconds.

DELETE THE Thumbs.db FILES AFTER UNPACKING. The archive ships one in each of
bounding_box_train/, query/, bounding_box_test/ and gt_bbox/, `get.py verify` counts directory
entries, and so a fresh unpack fails all four checks by exactly one until they are gone:
`find <root> -name Thumbs.db -delete`. The adapter globs *.jpg and never noticed.

The host has now moved twice. zheng-lab.cecs.anu.edu.au, which this page carried as the
homepage, no longer resolves at all (NXDOMAIN) — the live page is on GitHub Pages. The
third mirror the page offers, 188.138.127.15:81 (Julian Tanke), is dead: connection timeout.
Baidu links are listed but untested here.
>>>>>>> 9c9f3e0 (market access)
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
<<<<<<< HEAD
Market-1501-v15.09.15/
  bounding_box_train/
  query/
  bounding_box_test/
  gt_bbox/ gt_query/ readme.txt   # the authors' MATLAB evaluation inputs; unused here
=======
market1501/Market-1501-v15.09.15/
  bounding_box_train/     12,936 jpg
  query/                   3,368 jpg
  bounding_box_test/      19,732 jpg
  gt_bbox/                25,259 jpg   hand-drawn, not part of any split
  gt_query/                6,736 mat   good/junk index per query, unused by our evaluator
  readme.txt                           carries the licence text — see §6
>>>>>>> 9c9f3e0 (market access)
```

Filenames are `{pid:04d}_c{camid}s{seq}_{frame}_{n}.jpg`. Per-directory counts are in §1.

`gt_bbox/` and `gt_query/` are the two directories every tutorial forgets exist. Neither feeds
training or scoring here; they are the raw material the authors used to *derive* the good /
distractor / junk labels that are already baked into the filenames.

## 4. Splits and protocol

```yaml
name:    market1501/official@1
query:   {split: query}
gallery: {split: gallery}
exclude: [same_uid, same_pid_same_camid, {pid_in: [-1]}]
```

<<<<<<< HEAD
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
=======
**The distractor rule is the interesting part, and this project currently gets it wrong.**

The naming, from the project page's own FAQ and confirmed against the archive:

| filename prefix | count in gallery | what it is | official treatment |
|---|---|---|---|
| `0000_` | 2,798 | **distractor** — DPM false positive | **ranked**, and it costs you accuracy |
| `-1_` | 3,819 | **junk** — neither good nor bad box | dropped; zero impact |

The shipped adapter collapses **both** to `pid = -1`, and `market1501/official@1` then excludes
everything with `pid == -1` from scoring. That removes 6,617 of 19,732 gallery images from the
ranking instead of the 3,819 the official protocol removes. The 2,798 distractors are supposed
to compete with the true matches and push them down; here they never get ranked, so they never
distract, and every number this protocol produces is **higher than the published Market numbers
it will be compared against.** §7 warns against exactly this and then the code does it.

This is a live discrepancy, not a settled decision. Fixing it means splitting the collapse in
the adapter (`0` and `-1` are different labels and must survive as such) and narrowing the
protocol's `pid_in` to junk only. Until that happens the protocol should not be called
`official`, and no number from it belongs in a paper.

`market1501(root, distractors=False)` drops `pid <= 0` gallery rows at load time and is a
*different manifest* again — a third gallery, easier still, and one that belongs under its own
protocol name if it is reported at all.
>>>>>>> 9c9f3e0 (market access)

## 5. How to get it

`access = gdrive`, and it takes ten seconds:

```bash
python datasets/get.py fetch market1501
find data/market1501 -name Thumbs.db -delete      # see §1 [fetch]
python datasets/get.py verify market1501
```

Liang Zheng's project page is the canonical source and has now moved hosts twice — the ANU
address this page used to carry is gone entirely. The live page is
<https://zheng-lab-anu.github.io/Project/project_reid.html>. If you ever take a mirror instead,
record where it came from and check it against the sha256 in §1; the archive circulates widely
and the checksum is now the cheap way to know you have the real one.

Market-1501+500k, the distractor expansion, is on the same page as `distractors_500k.zip`
(Drive id `0B8-rUzbwVRk0cGtxWmFFVDZkNUE`, 1,064,961,065 bytes ≈ 1.0 GB). It serves the same way
and is not fetched here — nothing in `reidbench` reads it yet.

## 6. Licence and citation

<<<<<<< HEAD
The terms ship inside the archive, in `readme.txt`, and that is where they were read:
=======
`licence_verified = true` as of 2026-08-22. The terms are not on the web page at all, which is
why this sat unverified for so long — they are inside the archive, in `readme.txt`:
>>>>>>> 9c9f3e0 (market access)

> This dataset should be used for research only. Please DO NOT distribute or use it for
> commercial purpose.

<<<<<<< HEAD
That is the whole licence. It is short enough to quote, which is why `licence_verified = true`
here and `false` on [market1501-500k](market1501-500k.md), whose archive carries no such file.
=======
Research use, no redistribution, no commercial use. That is a real licence statement and it is
now read and recorded; it also means the archive must not be re-hosted from this project.
>>>>>>> 9c9f3e0 (market access)

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
<<<<<<< HEAD
- **Treating `pid 0` as junk.** §4. It needs no bad intent, nothing in the output looks wrong,
  and the gallery you report against is 2,798 boxes smaller than everyone else's.
- **Dropping the distractors.** §4 — quietly raises every number.
=======
- **Dropping the distractors.** §4 — quietly raises every number, and is currently what our own
  protocol does by a different route.
- **Swapping distractor and junk.** `0000_` is the distractor, `-1_` is the junk. This page, the
  adapter docstring and the protocol yaml all had it backwards until 2026-08-22; the page is
  fixed, the two code comments are not.
- **Thumbs.db.** Four of them, straight from the zip. `verify` fails by one per directory until
  they are deleted. §1 [fetch].
>>>>>>> 9c9f3e0 (market access)
- **Single-query vs multi-query.** The official protocol is single-query. Multi-query numbers are
  higher and are a different table.
- **The self-retrieval shape.** Every query identity also appears in the gallery under the same
  camera. An evaluator that forgets same-camera exclusion retrieves the query's own twin at
  similarity 1.0 and reports near-perfect Rank-1. `reidbench` keeps that bug reachable on
  purpose, under a name that says so, as a test that the exclusion rule is doing something.

## 8. Status in this project

| | |
|---|---|
<<<<<<< HEAD
| On disk | ✅ |
| `reidbench` adapter | ✅ `adapters/market1501.py` |
| `reidbench` protocol | ✅ `market1501/official@1` |
| Provenance record | ✅ `market1501` |
| Measured | ✅ [results/table.md](../results/table.md) |
=======
| On disk | ✅ `data/market1501/Market-1501-v15.09.15`, verified 2026-08-22 |
| `reidbench` adapter | ✅ `adapters/market1501.py` — builds a 36,036-row manifest |
| `reidbench` protocol | ⚠️ `market1501/official@1` — ships, but see §4 before reporting it |
| Provenance record | ✅ `market1501` |
| Access | ✅ public Drive link; sha256 recorded |
>>>>>>> 9c9f3e0 (market access)
