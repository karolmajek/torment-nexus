---
title: "LaST — long-term, cloth-changing, movie-sourced, and the largest gallery we would search"
kb_id: dataset-last
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, last, person-reid, cloth-changing, long-term, gdrive, access, licensing, provenance]
retrieved: 2026-08-31
confidence: |
  high — every count in §1 is counted from the downloaded release, not quoted from a paper or
  a README. §7 records where the three sources disagree and which one the data settles on.
  high — the layout and file-name schema in §3 are the release's own `readme.txt` plus its
  loader, confirmed against the extracted tree.
  high — the manifest builds, both protocols select, and every one of the 10,176 test queries
  has at least one reachable answer.
related: [dataset-ccvid, dataset-msmt17, dataset-market1501, reid-benchmarks-datasets, reid-reidbench-owed]
---

# LaST

> Long-term person re-identification: 10,862 identities over 228k images cut from ~2,000
> movies, 76% of whom change clothes, across day and night and spring to winter.
>
> 🔌 **On disk, verified, and unarmed on purpose.** The data is downloaded, the counts are
> counted rather than quoted, the adapter is written and passes an oracle/floor guard, and the
> protocols ship — but this page's `adapter` field is empty, so LaST cannot enter the run
> matrix. §8 is the two-edit arming procedure; do not run it while a sweep is in flight.

## 1. Facts

This block is the single source of truth for LaST's numbers in this project. Nothing else —
no wiki page, no protocol comment, no paper draft — restates them; they link here.

```toml
[dataset]
name = "LaST"
kind = "person"
role = "long-term / cloth-changing transfer target; the largest gallery in this collection"
licence = "academic research use only"
licence_verified = true
commercial_ok = false
access = "gdrive"
homepage = "https://github.com/shuxjweb/last"
dir = "last"
# EMPTY ON PURPOSE. `reidbench.adapters.last` exists and is not registered; naming it here
# would put LaST into `run.py plan` the moment the download lands. Arming is §8.
adapter = ""
protocols = []
checked_on = "2026-08-31"
link_verified = true
counts_verified = true
on_disk_since = "2026-08-31"
on_disk_provenance = "downloaded 2026-08-31 from the authors' own Google Drive link, id 1w_TfMx4NBVJfjVGxzKqVHPTxhKj6gQqK, via get.py fetch. First-party, no mirror, no gap."

[counts]
# Counted from the release. Where the README and the paper disagree, §7 says which the data
# supports and why. `identities` counts real people: the 000000 interference class is not one.
identities = 10861
images = 228156
videos = 1581             # the nearest thing LaST has to a scene grouping. NOT cameras — §5
cameras = 0               # not "unknown". LaST labels no cameras at all
clothes_labelled_images = 71248   # exactly the training split, and all of it — §3

[counts.train]
identities = 5000
images = 71248

[counts.val]
identities = 56
images = 21379
queries = 100
gallery = 21279
gallery_interference = 20000   # 94% of the validation gallery is the 000000 class — §5

[counts.test]
identities = 5806         # in the gallery; 5,805 of them are queried, one is gallery-only
images = 135529
queries = 10176
query_identities = 5805
gallery = 125353
gallery_interference = 20275   # 16% of the test gallery
true_pairs = 202079            # query-gallery pairs sharing an identity, under last/test@1

[expect]
# Direct entry counts, which is what `get.py verify` reads. Confirmed against the extracted
# tree on 2026-08-31. Note `test/gallery` is 5,808 directories and not 5,806 identities: the
# 000000 interference directory is one of them, and one identity is spelled two ways — §10.
"train" = 5000
"test/query" = 10176
"test/gallery" = 5808
"val/query" = 100
"val/gallery" = 57

[fetch]
gdrive_id = "1w_TfMx4NBVJfjVGxzKqVHPTxhKj6gQqK"
archive_bytes = 3070378056
archive_entries = 239030
manual = """
One Google Drive file, `last.zip`, 3.07 GB, 239,030 entries, linked from
https://github.com/shuxjweb/last . `get.py fetch last` hands the id to gdown; the file is
large enough that Drive demands the confirm token, which gdown handles. The Baidu Pan mirror
(password `vvfe`) is the authors' own alternative and carries the same licence grant.

UNPACK INTO `data/`, NOT INTO `data/last/`. The archive carries its own top-level `last/`
directory — verified, not assumed — so extracting into the target named by `dir` would give
you `data/last/last/`. This is the opposite of VRIC, whose archive is bare, and it is the
reason `get.py fetch last` places the tree one level too deep; unpack by hand, or strip the
leading component. Note also that gdown preserves the Drive file's own modification time
(2023-04-13 for this one), so a freshly downloaded `last.zip` looks older than everything
else in `data/_downloads/`.
"""
```

`python datasets/get.py counts last` prints the same numbers if you need them at a terminal.

## 2. What it is

Persons detected in roughly two thousand movies, then filtered and labelled by hand — eight
annotators over two and a half months — to keep frames that look like surveillance rather than
like cinema. The point of the construction is the **time span**: the same identity recurs
across changes of clothing (76% of identities change), across day and night (55%/45%), and
across seasons. Every other person set in this collection holds appearance roughly constant
and varies viewpoint; LaST does the opposite, which is why it is the interesting transfer
target and not merely another large one.

It was published in **IEEE TCSVT** (2022), which is this project's target venue
([80-publication-venue-2024.md](../docs/project/80-publication-venue-2024.md)). A reviewer
from that pool is more likely than average to know this dataset.

## 3. What is inside

Two of the five directories are flat and three are one level deep — the release's loader
branches on `'query' in dir_path` to pick its glob:

```
last/
  readme.txt                                 the schema below, and the interference note
  train/          <pid>/<name>.jpg           5,000 identity directories, 71,248 images
  val/
    query/        <name>.jpg                 flat, 100 files
    gallery/      <pid>/<name>.jpg           57 directories, 21,279 images
  test/
    query/        <name>.jpg                 flat, 10,176 files
    gallery/      <pid>/<name>.jpg           5,808 directories, 125,353 images
```

**The file name carries six fields, and the release documents all of them** in `readme.txt`:

```
000051_003_00013_0270_04_001.jpg
^      ^   ^     ^    ^  ^
|      |   |     |    |  clothes id; 000 means unlabelled
|      |   |     |    bounding box id within the frame
|      |   |     frame id within the video
|      |   video id
|      image id for this person
identity
```

That is the real interface, not the directory nesting — the identity is in the name even in
the two flat directories, which is why `adapters/last.py` walks to any depth and parses the
name rather than encoding two glob patterns. The adapter keeps `videoid`, `frameid`, `boxid`
and `clothid` as columns, because they are free and the release documents them.

**Clothing labels are a training annotation, exactly.** All 71,248 training images carry a
clothes id, and no image outside the training split carries one — 1,581 videos and 37 distinct
clothes ids across the release. So a cloth-changing analysis over the *test* split cannot read
this column; it has to infer what the column would have said.

The manifest builds in ~18 s over 228,156 rows and `validate()` returns one warning: the
`val_query` and `val_gallery` split names are not in the package's `KNOWN_SPLITS`. That is
by design — the package's own note says an unknown split name is a warning because "a library
edit is the wrong price for a new one" — so it is left alone rather than silenced.

## 4. How to get it

`access = "gdrive"`, one file, no agreement to sign and no form to fill in:

```bash
python datasets/get.py fetch last
```

which delegates to `gdown`. Drive rate-limits large files, so the browser fallback is likely;
`get.py` prints the URL when gdown fails rather than retrying around it. The authors also
publish a Baidu Pan mirror (password `vvfe`), which is theirs and therefore carries the same
licence grant — unlike the third-party mirrors [msmt17.md](msmt17.md) §4 has to weigh.

This is the cheapest access of any large person set here: no request form, no signed
agreement, no provenance gap. The cost is entirely download time and disk.

## 5. Splits and protocol — and the camera problem

Two protocols ship in `reidbench` and neither is named on this page yet (§8):

```yaml
name:    last/test@1
query:   {split: query}          # test/query,   10,176 images over 5,805 identities
gallery: {split: gallery}        # test/gallery, 125,353 images over 5,806 + interference
exclude: [same_uid]
```

```yaml
name:    last/val@1
query:   {split: val_query}      # 100 images over 56 identities
gallery: {split: val_gallery}    # 21,279 images, 20,000 of them interference
exclude: [same_uid]
```

Under `last/test@1` there are **202,079 true query–gallery pairs**, every one of the 10,176
queries has at least one reachable answer, and **no pair is excluded by any rule** — the two
paragraphs below are why.

> **Identity 0 is not an identity, and it stays.** The release's `readme.txt`: the `000000`
> directory under both gallery splits "contains many unlabeled persons ... can be seen as
> interference samples". It is 20,275 of the test gallery's 125,353 images and 20,000 of the
> validation gallery's 21,279, and **no query carries it**. It is gallery clutter of exactly
> the kind [market1501-500k.md](market1501-500k.md) exists to add artificially, shipped here
> as part of the benchmark. So it is not excluded: dropping it would make the search easier
> than the benchmark intends. There is no junk class of Market-1501's `-1` kind, so neither
> protocol states a `pid_in` rule — one would guard against a label that cannot occur while
> implying the interference images were the thing being guarded against.

> **LaST labels no cameras, and its reference implementation invents them.** `_process_dir`
> assigns `camid = recam + i` — a running index, unique per image, with the gallery's range
> offset past the query's by `recam=len(query)`. A query camid can therefore never equal a
> gallery camid, and `same_pid_same_camid` applied to those values is guaranteed to remove
> nothing. It is a rule evaluated against fabricated data that happens to be harmless.
>
> The adapter records `camid = -1` throughout instead — the same encoding
> [occluded-reid.md](occluded-reid.md) gets, for the same reason — and both protocols omit the
> same-camera rule. **A LaST number is therefore not comparable to a Market-1501 number in the
> way two camera-labelled datasets are comparable to each other**, and the difference is that
> LaST's score is not protected by the exclusion every Market number depends on.

**The validation split is not a small test set.** Fifty-six identities cannot separate
encoders, and a `last/val@1` number does not belong in a column beside a `last/test@1` number.
It exists so that anything tuned on LaST is tuned on the split the authors set aside for it.

## 6. What it would cost us

The test pair alone is **135,529 images**, which is more than the whole of Market-1501 and
Occluded-REID and CUHK03-NP and VRIC together. At this project's measured throughputs on one
RTX 2070 Max-Q:

| encoder | img/s | test split |
|---|---:|---:|
| CLIP-B/16 @224 squash | 81.8 | ~28 min |
| C-RADIOv4-H @224 | 12.3 | ~3.1 h |
| DINOv3-H+ @224 | 9.5 | ~4.0 h |
| SigLIP2-g @256 | 5.8 | ~6.5 h |

All twelve encoder-resolution configurations currently in the study, over the test split only,
is roughly **25 GPU-hours**. The training split adds another 71,248 images and is needed only
if a head is ever fitted on LaST; the frozen and Market-fitted-head rows this project reports
do not touch it. Encoding only what the protocol scores is the saving
[vrai.md](vrai.md) documents wanting and does not yet have — here it is available from the
start, because the split boundary and the protocol boundary coincide.

The score matrix is the other cost, and it is not an estimate: `protocol.select` materialises
10,176 × 125,353 = 1.28 × 10⁹ pairs, measured at **2.55 GB** for the `rel`/`valid` pair, with
the similarity matrix a further 5.1 GB at fp32. Selection takes ~24 s and a full `measure`
pass over a dense score matrix took ~138 s in testing. That is larger than MSMT17's and is
squarely the case `measure.retrieval.blocks()` exists for.

## 7. The counts disagree, and the data settles it

Three sources, and they did not agree. The last row is counted from the release itself:

| | train images | val images | test images | sum | test identities |
|---|---:|---:|---:|---:|---:|
| Release README | 71,248 | 21,379 | 135,529 | **228,156** | 5,806 |
| Paper, Table II | 70,923 | 20,584 | 133,214 | 224,721 | 5,803 |
| Paper, stated total | — | — | — | **228,156** | — |
| **Counted** | **71,248** | **21,379** | **135,529** | **228,156** | **5,806** |

**The README is right and the paper's Table II is wrong**, on every per-split image count and
on the test identity count. The arithmetic said so before the download did: the README's
figures sum to 228,156, exactly the total the paper itself states, while the paper's own
per-split column sums to 224,721 and contradicts its own total by 3,435 images.

The validation breakdown, which no source resolved, is now settled: **100 queries and 21,279
gallery images**. The paper's 20,179 is a transposition of 21,279; that single digit is the
whole of the 1,100-image gap.

Two figures the sources do not carry at all, and both matter more than the ones they argue
about:

- **The test gallery is 5,808 directories but 5,806 identities**, and only 5,805 of those are
  queried. §10 has why.
- **20,275 of the test gallery's images are the interference class**, and 20,000 of the
  validation gallery's 21,279. The README mentions this in a one-line footnote inside the
  archive; neither the paper's table nor the repository front page mentions it at all. A
  reader who assumes the validation gallery is 21,279 images of 56 people is wrong by a factor
  of seventeen — it is 1,279 images of 56 people plus 20,000 distractors.

So `[counts]` above is counted, not quoted, and `counts_verified = true`. This is the failure
mode this directory's [README](README.md) exists to prevent, arriving from the direction it
warns about least: the numbers most people would cite are the ones printed in the paper.

## 8. Arming it

The data is on disk, the counts are verified and the adapter is tested. **Two edits remain, and
neither should be made while a sweep is running** — the moment both land, `run.py plan` gains
14 encoders × 4 heads × 1 protocol of newly-runnable work, at the cost in §6:

1. `reidbench/src/reidbench/adapters/__init__.py` — import `last` and add `"last": last` to
   `ADAPTERS`. `tests/test_adapters.py` asserts the exact key set, so it fails until updated;
   that failure is the guard working, not a nuisance.
2. this page — set `adapter = "last"` and `protocols = ["last/test@1"]`. Add `last/val@1`
   only if something is being tuned; per §5 it is not a second test set.

### 8.1 The checks that have already been done

Recorded here so they are not repeated, and so a future change that breaks one is visible:

| check | result |
|---|---|
| `[expect]` against the extracted tree | all five directory counts match |
| manifest builds | 228,156 rows in ~18 s, one expected `KNOWN_SPLITS` warning (§3) |
| identity label spaces collide? | **no.** train ∩ test ∩ val is empty over real identities, so the published labels are carried through unshifted |
| every query answerable? | yes — all 10,176 test and all 100 validation queries have ≥1 reachable true match |
| pairs excluded by any rule | **0**, by design (§5) |
| **oracle**, `last/test@1` | mAP **1.0000**, R1 1.0000 |
| **random floor**, `last/test@1` | mAP **0.000247** — 4,052× below the oracle |
| **oracle / floor**, `last/val@1` | 1.0000 / 0.001377 |

The oracle-and-floor pair is what separates "long-term re-id is hard" from "the identity parse
is silently wrong and the manifest still looks fine". On a 125,353-image gallery the floor is
very low, which makes the check more informative here than anywhere else in this collection.

The identity-collision question is the one that changed a design. The reference loader relabels
`train` from zero and leaves `test` alone, which is the signature of two independently numbered
sets — [msmt17.md](msmt17.md) §7's leak, in a dataset twice the size. An earlier version of the
adapter shifted `train` and `val` into separate ranges as a guard. Measured, the sets are
disjoint, so the shift was moving labels away from the ones every published LaST number uses
for no benefit; it is gone.

## 9. Licence and citation

**Academic research use only**, stated by the authors on the release page: *"The dataset and
code are released for academic research use only."* No redistribution, and the underlying
frames are cut from commercial films, whose copyright is not the authors' to grant — which
makes this a set to evaluate on and not one to re-publish crops from.

Contact of record: `shuxj@mail.ioa.ac.cn`.

```bibtex
@article{shu2021large,
  title={Large-Scale Spatio-Temporal Person Re-identification: Algorithm and Benchmark},
  author={Shu, Xiujun and Wang, Xiao and Zang, Xianghao and Zhang, Shiliang and Chen, Yuanqi and Li, Ge and Tian, Qi},
  journal={IEEE Transactions on Circuits and Systems for Video Technology},
  pages={4390--4403},
  year={2022}
}
```

## 10. Traps

- **One identity is spelled two ways, and directory and file name disagree on 30 files.**
  `test/gallery/005895/` holds 30 images whose names begin `005859` — a transposition in the
  release. Those 30, plus one file in `test/query`, also carry a **doubled underscore** after
  the identity, so they parse as seven fields where every other name has six. Both facts are
  the same defect and both bite:
  - reading the identity from the **file name** merges them into identity 5,859 and gives the
    gallery 5,806 identities;
  - reading it from the **directory** splits them out and gives 5,808.

  The release's own loader reads the file name, so that is what every published LaST number is
  computed on, and `adapters/last.py` does the same. A parser that splits on `_` and expects
  exactly six fields crashes on those 31 files; one that indexes positionally is worse — it
  silently reads the image id as the video id and shifts every field after it.
- **No cameras.** §5. The same-camera exclusion does not exist here, so a LaST score is not
  protected the way a Market-1501 score is. `videoid` is in the manifest and is **not** a
  camera: two frames of one video share a scene, not a viewpoint, and excluding same-video
  pairs would score a different benchmark than the published one.
- **The `000000` directory is not identity zero.** It is 20,275 interference images in the
  test gallery and 20,000 in the validation gallery, documented only in a footnote inside the
  archive's `readme.txt`. Excluding it scores an easier benchmark; treating it as an identity
  scores a nonsensical one. §5.
- **The paper's Table II is wrong.** §7. Cite this page, which counted the release.
- **`val` is 56 identities and 94% distractors.** Not a test set, and not even a small one:
  1,279 real images against 20,000 interference. §5.
- **Movie frames are not surveillance frames**, however carefully selected. Resolution,
  framing, lighting and lens are a film crew's choices; the authors filtered for
  surveillance-like appearance but did not change where the pixels came from. A cross-domain
  claim that treats LaST as a surveillance domain is claiming something the construction does
  not support.
- **Cloth-changing is the point, not a subset, and it is not labelled where you would score
  it.** Unlike CCVID there is no protocol restricting to the cloth-changing case, and there
  cannot easily be one: the `clothid` field is populated for all 71,248 training images and
  for **no** test or validation image. The single test protocol scores changed and unchanged
  clothing together. A LaST number and a `ccvid/tracklet-cloth-changing@1` number answer
  different questions.
- **The gallery is 125,353 images.** Cross-dataset comparison of absolute mAP against a
  15k-image gallery is not a difficulty comparison. §6.

## 11. Status in this project

| | |
|---|---|
| On disk | ✅ `data/last`, 228,156 images, downloaded and unpacked 2026-08-31, first-party |
| Counts | ✅ **counted from the release**, not quoted. `[expect]` matches the tree |
| `reidbench` adapter | ⚠️ **written and tested, not registered** — `adapters/last.py` exists; `ADAPTERS` does not name it |
| `reidbench` protocol | ✅ `last/test@1` and `last/val@1` ship |
| Adapter guard | ✅ oracle 1.0000, random floor 0.000247 on `last/test@1`. §8.1 |
| Provenance record | ❌ not written — `reidbench/provenance_records/last.toml` is the last missing piece |
| This page's `adapter` field | ⚠️ **empty on purpose.** `run.py plan` reports "no reidbench adapter" and nothing runs |
| Experiments | none, and none can start until §8's two edits |
