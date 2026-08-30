---
title: "CCVID — cloth-change, RGB only, and tracklet-shaped"
kb_id: dataset-ccvid
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, ccvid, cloth-change, video, tracklet, person-reid]
retrieved: 2026-08-21
confidence: |
  medium — the repository, licence line and citation were read on 2026-08-21; the Drive file id
  was not extractable from the rendered page, and the tracklet split counts come from the CVPR
  2022 paper rather than from a download. Verify both on first fetch.
related: [dataset-occluded-reid, dataset-mars, reid-benchmarks-datasets, reid-reidbench-owed]
---

# CCVID

> The second half of C1's stress pair, and the first dataset in this project that is genuinely
> video-shaped.

## 1. Facts

Single source of truth for this dataset's numbers. Every one below was counted from the release
itself on 2026-08-26 — the three split files and the extracted tree — replacing the paper-read
figures this page carried until then. The tracklet counts the paper gives were all correct.

```toml
[dataset]
name = "CCVID"
kind = "person / cloth-change, video"
role = "cloth-change stress test; tracklet-shaped, needs trackid in the manifest"
licence = "CC BY-NC-SA 4.0, stated in the archive's own readme.txt; FVG's terms sit underneath and were not separately read"
licence_verified = true
commercial_ok = false
access = "gdrive"
homepage = "https://github.com/guxinqian/Simple-CCReID"
dir = "CCVID"
adapter = "ccvid"
tracklet_by = "trackid"
frames_per_tracklet = 8
protocols = ["ccvid/tracklet@1", "ccvid/tracklet-cloth-changing@1"]
checked_on = "2026-08-26"
link_verified = true
on_disk_since = "2026-08-26"

[counts]
identities = 226
tracklets = 2856
frames = 347833
# The clothes labels are per-identity, so the number of real outfits is the number of distinct
# (identity, label) pairs — not the number of distinct label strings, which is 11 in train and
# 20 in the test half and would understate it by more than an order of magnitude.
train_outfits = 159
test_outfits = 321

[counts.tracklets_per_session]
session1 = 1764
session2 = 948
session3 = 144

[counts.train]
identities = 75
tracklets = 948

[counts.query]
identities = 151
tracklets = 834

[counts.gallery]
identities = 151
tracklets = 1074

[expect]
"train.txt" = 948
"query.txt" = 834
"gallery.txt" = 1074
"session1" = 1764
"session2" = 948
"session3" = 144

[fetch]
gdrive_id = ""
manual = """
Still not recorded: the repository README renders its Drive link through GitHub's markdown and
the id was not readable from the fetched page, so `get.py fetch ccvid` cannot run. It has not
been needed — a copy arrived as CCVID.zip and was unpacked on 2026-08-26 — but the id is worth
filling in for reproducibility. Open https://github.com/guxinqian/Simple-CCReID , copy the Drive
link from the CCVID section, and paste the id here. BaiduYun is offered as an alternative with
password q0q2.

The archive unpacks to a top-level `CCVID/`, so extract it into `data/` and not into
`data/CCVID/`.

The licence question is CLOSED and the answer was inside the archive all along: `CCVID/readme.txt`
states CC BY-NC-SA 4.0 and requires face mosaicking in any visualisation. Apache-2.0 covers
Simple-CCReID's code and was never the data licence. See §6.
"""
```

## 2. What it is

Cloth-Changing Video re-ID, released with *Clothes-Changing Person Re-identification with RGB
Modality Only* (Gu et al., CVPR 2022). People walk past a camera in different outfits across
sessions; the point is that identity has to survive a complete change of clothing without any
auxiliary modality — no silhouette, no gait model, no skeleton. RGB only, which is what makes it
a fair test of an appearance embedding rather than of a pipeline.

## 3. What is inside

```
CCVID/
  session1/  1,764 tracklet directories, each holding 00001.jpg, 00002.jpg, …
  session2/    948
  session3/    144
  train.txt  query.txt  gallery.txt
  readme.txt
```

Each line of a split file is one **tracklet**, tab-separated:

```
session1/001_01	001	u0_l0_s0_c0_a0
[tracklet directory]	[pid]	[clothes label]
```

`u`, `l`, `s`, `c`, `a` are tops, bottoms, shoes, carrying status and accessories, and the digit
after each is *this identity's* n-th such item. So the label is only meaningful within a person:
20 distinct strings across the test half stand for 321 actual outfits, and `001_u0…` and
`002_u0…` are different clothes. The real key is `"{pid}_{label}"`, which is what the release's
own loader uses and what `adapters/ccvid.py` puts in the `clothes_id` column.

**`camid` is a convention, not a room.** The directory's second field is 1..12 in every session;
session 3 is a different recording setup, so its cameras are shifted by 12. That is what the
CCVID loader does, and a number computed under a different camera map is a different number.

The three split files are disjoint — 2,856 tracklet paths, 2,856 unique — which the adapter
checks rather than assumes.

## 4. Splits and protocol

Two settings, and they answer different questions:

| Setting | Gallery | What it measures |
|---|---|---|
| **general** | everything | ordinary video ReID, same-clothes matches included |
| **cloth-changing (CC)** | same-clothes matches excluded | whether identity survives the outfit change — the number worth reporting |

In `reidbench` terms these are **two protocol values**, not a flag:

```yaml
name:    ccvid/tracklet@1
query:   {split: query}
gallery: {split: gallery}
exclude: [same_trackid, same_pid_same_camid]

name:    ccvid/tracklet-cloth-changing@1
query:   {split: query}
gallery: {split: gallery}
exclude: [same_trackid, same_pid_same_camid, {same: clothes_id}]
```

The CC setting is one extra exclusion predicate and no new machinery. `{same: clothes_id}` is
the generic "equal on this column" predicate — added for CCVID, useful to anything with a
private rule of that shape — and because `clothes_id` is `"{pid}_{label}"`, same-clothes already
implies same-person, so a single equality expresses the whole rule.

Two names rather than one name and a flag, because the two numbers are not comparable and must
not share a column.

**Tracklet handling needs no second code path — but it does need both halves.**

```python
tracks = manifest.collapse(m, by="trackid")        # 2,856 rows, not 347,833
uids, X = transform.aggregate(uids, X, trackid)    # the vectors that match them
```

The two agree on the uid (the track id as a string), so after them there are no tracklets, only
rows and vectors, and the protocol is the same shape as every other one. **Do not select a
tracklet protocol over the frame-level manifest**: `select` materialises a `(query, gallery)`
boolean pair, which at frame level here is 116,799 × 112,421 — about 26 GB across `rel` and
`valid`, to answer a question about 834 tracklets.

**This project evaluates at 8 frames per tracklet.** `frames_per_tracklet = 8` in §1, applied by
`splits.frames_per_group` *before* encoding, evenly spaced so the sample spans the tracklet
rather than one pose. It is the common practice in video re-id and it is what makes the sweep
affordable — but **it moves the number**, so it is a stamped manifest recipe rather than a
constant in a runner script, and every `results.json` carries the frame count that produced it.
Compare against published figures only after checking what they sampled.

`collapse` keeps only columns that hold one value per tracklet, so `pid`, `camid`, `split` and
`clothes_id` survive and `relpath` does not. That is why the collapsed manifest cannot be fed
back to `encode`: you encode frames, then aggregate.

## 5. How to get it

Google Drive, linked from the Simple-CCReID repository. A copy is already unpacked at
`data/CCVID`; the Drive id is still **not recorded**, so `get.py fetch ccvid` cannot re-fetch
it. §1 says what to do about that.

```bash
# 1. open https://github.com/guxinqian/Simple-CCReID , copy the CCVID Drive link
# 2. paste the id into this page's [fetch] gdrive_id
python datasets/get.py fetch ccvid
```

## 6. Licence and citation

**Closed on 2026-08-26, from the archive's own `readme.txt`** — which is where the terms were
all along, not in the repository:

> Using this dataset should accept and agree to be bound by the terms and conditions of the
> CC BYNC-SA 4.0 license.
> Visualizing the data from FVG should mosaic the face area.

So: **CC BY-NC-SA 4.0**. Non-commercial, share-alike, attribution. The Apache-2.0 badge on the
Simple-CCReID repository covers the *code* and never covered the data; reading it as a data
licence was the error this page previously warned about and could not resolve.

Two things do not follow from that line, and both matter:

- **The face-mosaic requirement is a publication constraint, not a footnote.** Any figure,
  poster or slide showing CCVID frames has to mosaic the face area. Plan for it before the
  qualitative-results figure is due.
- **FVG's terms sit underneath.** CCVID is built from the raw video of the FVG gait dataset
  (`github.com/ziyuanzhangtony/GaitNet-CVPR2019`). CCVID's authors granted CC BY-NC-SA over
  what they assembled; nobody in this project has read FVG's own grant. `licence_verified = true`
  records that CCVID's line has been read, not that FVG's has.

```bibtex
@inproceedings{gu2022CAL,
  title={Clothes-Changing Person Re-identification with RGB Modality Only},
  author={Gu, Xinqian and Chang, Hong and Ma, Bingpeng and Bai, Shutao and Shan, Shiguang and Chen, Xilin},
  booktitle={CVPR}, year={2022}
}
```

## 7. Traps

- **Reporting the general setting as a cloth-change result.** The general number is much higher
  and is not what anybody means by cloth-change performance. Name the setting in the table.
- **Frame-level numbers on a tracklet dataset.** Scoring individual frames against a frame
  gallery is a different, easier task than tracklet-to-tracklet. Aggregate first.
- **Few identities.** Report the drop from a large-gallery result and give a confidence interval
  — `stats.ci` on the per-query AP column costs nothing here.
- **Repo licence ≠ data licence.** §6 — now answered: CC BY-NC-SA 4.0, from the archive.
- **Faces must be mosaicked in any visualisation.** §6.
- **8 frames per tracklet, not 122.** §4. A number computed over all frames is a different
  number; `results.json` records which.
- **Clothes labels are per-identity.** Counting distinct label strings gives 20 outfits where
  there are 321. Key on `"{pid}_{label}"`, which is what `clothes_id` holds.

## 8. Status in this project

| | |
|---|---|
| On disk | ✅ `data/CCVID`, unpacked 2026-08-26 |
| `reidbench` adapter | ✅ `adapters/ccvid.py` — one row per frame, with `trackid` and `clothes_id` |
| `reidbench` protocol | ✅ `ccvid/tracklet@1` and `ccvid/tracklet-cloth-changing@1` |
| Provenance record | ✅ `ccvid` |
| Access | the copy is here; the Drive id is still unrecorded (§5), which only affects re-fetching |
| Experiments | none run yet |
