---
title: "MARS — video tracklets with real detector noise (and LS-VID, the larger alternative)"
kb_id: dataset-mars
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, mars, ls-vid, video-reid, tracklets, aggregation, c15]
retrieved: 2026-08-21
confidence: |
  medium — counts and layout are well established and match torchreid's expected tree; download
  links have not been exercised by this project and the Drive id is not recorded.
related: [dataset-ccvid, dataset-veri776, reid-benchmarks-datasets]
---

# MARS

> The tracklet aggregation study's dataset (C15), and the place where "how do you pool a set of
> crops" stops being a design question and becomes a measurement.

## 1. Facts

Single source of truth for this dataset's numbers, including LS-VID's, since choosing between
them is one decision (§5).

```toml
[dataset]
name = "MARS"
kind = "person / video"
role = "tracklet aggregation study (C15); auto-generated tracklets with real detector noise"
licence = "research use only — a convention, not a document anyone here has read"
licence_verified = false
commercial_ok = false
access = "gdrive"
homepage = "https://github.com/liangzheng06/MARS-evaluation"
dir = "mars"
adapter = "mars"
tracklet_by = "trackid"
frames_per_tracklet = 8
protocols = ["mars/official@1"]
checked_on = "2026-08-26"
link_verified = false
on_disk_since = "2026-08-26"
on_disk_provenance = "Frames from the Kaggle mirror `ivynyakyanying/mars-motion-analysis-and-re-identification-set`, because the ANU project page's Drive link is not a Drive link and does not resolve. The mirror ships the frames ONLY — see [fetch] manual. info/ was cloned from liangzheng06/MARS-evaluation on 2026-08-26."

[counts]
# Everything below except `identities` was read out of info/ and the extracted tree on
# 2026-08-26. `identities` is the paper's figure and counts the two unlabelled classes.
identities = 1261
tracklets = 20478
images = 1191003
cameras = 6
train_tracklets = 8298
test_tracklets = 12180
train_images = 509914
test_images = 681089
query_tracklets = 1980
query_identities = 626
junk_tracklets = 870          # pid -1; discarded by evaluation_mars.m
distractor_tracklets = 3248   # pid 0; ranked, matches nothing, costs precision
train_identities = 625
test_identities_with_tracklets = 634
train_identity_dirs = 625
test_identity_dirs = 636      # 634 real + `0000` + `00-1`
unpacked_gb_approx = 20

[counts.ls_vid]
# The alternative, documented here because it is one choice, not two datasets — see §5.
identities = 3772
tracklets = 14943
cameras = 15

[expect]
"bbox_train" = 625
"bbox_test" = 636
"info/train_name.txt" = 509914
"info/test_name.txt" = 681089

[fetch]
gdrive_id = ""
manual = """
Two halves from two places, and both are needed. The images without info/ are not a smaller
dataset — they are no dataset: the tracklet boundaries and the query index live only in info/.

  1. FRAMES. The ANU project page (zheng-lab-anu.github.io/Project/project_mars.html) offers
     what it calls a Google Drive link; it is not a Drive link and does not resolve, so there
     is no id to paste above and `get.py fetch mars` cannot work. The copy in use here came
     from the Kaggle mirror
     `ivynyakyanying/mars-motion-analysis-and-re-identification-set`, which carries the frames
     and NOTHING ELSE — no info/ — and nests them two deep as
     `OneDrive_1_2022-4-2/bbox_{train,test}/bbox_{train,test}/`. Move those two directories up
     to `data/mars/bbox_train` and `data/mars/bbox_test`; the adapter expects them at the root.
     A mirror carries no licence grant. Write down that you used one (see the
     `on_disk_provenance` field above) rather than leaving the gap undocumented.

  2. info/. Public, unambiguous, and small:
       git clone --depth 1 https://github.com/liangzheng06/MARS-evaluation
     then copy its `info/` to `data/mars/info/`. Five files, ~25 MB:
     tracks_train_info.mat, tracks_test_info.mat, query_IDX.mat, train_name.txt, test_name.txt.

Reading info/ needs scipy — MARS published its splits as MATLAB and as nothing else. That is
the `reidbench[mat]` extra, imported lazily by `adapters/mars.py` alone.
"""
```

## 2. What it is

Motion Analysis and Re-identification Set: Market-1501's cameras, but tracked. Tracklets are
**auto-generated** by DPM + GMMCP rather than hand-curated, so they contain what real tracker
output contains — drift, identity switches, and a set of distractor tracklets that belong to no
query identity at all. That noise is the reason to use it: a pooling method that only works on
clean tracklets is not a pooling method for deployment.

## 3. What is inside

```
mars/
  bbox_train/     one directory per training identity
  bbox_test/      one directory per test identity
  info/           tracks_train_info.mat, tracks_test_info.mat, query_IDX.mat,
                  train_name.txt, test_name.txt, ...
```

The `info/` directory is not optional and comes from a different place than the images do (§1).

## 4. Splits and protocol

```yaml
name:    mars/official@1
query:   {split: query}
gallery: {split: [query, gallery]}
exclude: [same_trackid, same_pid_same_camid, {pid_in: [-1]}]
```

**The gallery is every test tracklet, queries included.** `test_mars.m` sets
`label_gallery = track_test(:, 3)` — all 12,180 of them — and takes the 1,980 query tracklets
as a *subset* of that, `feat_query = video_feat_test(:, query_IDX)`. A query leaves its own
ranking through the same-camera rule, not by being held out, which is why the protocol's
gallery selector is `{split: [query, gallery]}` rather than the adapter emitting each query
twice under two uids.

**−1 is junk, 0 is a distractor**, exactly as in Market-1501. `evaluation_mars.m` does
`junk0 = find(label_gallery == -1)` and ranks everything else, so the 870 `pid == -1` tracklets
are dropped by `pid_in: [-1]` and the 3,248 `pid == 0` distractor tracklets stay in the gallery,
match nothing, and cost precision. (A secondary helper in the same repo,
`KISSME/helper/calcmAP.m`, tests `== 0` instead — it is not the script `test_mars.m` calls, and
following it would delete the distractors that are the whole point of this dataset.)

Tracklet-to-tracklet retrieval, with same-camera exclusion as usual. As with
[ccvid](ccvid.md) and [veri776](veri776.md), this needs **no second code path** — but it does
need both halves of one step: `manifest.collapse(m, by="trackid")` for the rows and
`transform.aggregate(X, trackid)` for the vectors. They agree on the uid, and afterwards there
are no tracklets, only rows and vectors, and the protocol is the same shape as every other one.
That collapse is 20,478 rows instead of 1,191,003 — the difference between a `(query, gallery)`
boolean pair that fits in memory and one that does not.

**This project evaluates at 8 frames per tracklet.** `frames_per_tracklet = 8` in §1, applied by
`splits.frames_per_group` *before* encoding, evenly spaced so the sample spans the tracklet
rather than one pose. It is the common practice in video re-id and it is what makes the sweep
affordable — but **it moves the number**, so it is a stamped manifest recipe rather than a
constant in a runner script, and every `results.json` carries the frame count that produced it.
Compare against published figures only after checking what they sampled.


What C15 actually varies is the aggregation function itself: mean, max, attention pooling,
quality-weighted. That is a caller-side loop over `transform.aggregate` variants producing
different `(uids, X)` values, each scored under one unchanged protocol — the right shape, because
the protocol is not what changed.

**The distractor tracklets matter.** They are gallery entries matching no query, and dropping
them makes every number better and less meaningful — the same argument as Market's junk boxes.

## 5. LS-VID — the alternative, and when to prefer it

The ledger says "MARS **or** LS-VID" for C15, and it is one decision, not two datasets. Counts
for both are in §1. MARS is the default here: it is more widely reported, so a new aggregation
result lands next to existing numbers, and its distractor tracklets are the property C15 is
actually testing. Prefer LS-VID if the claim is specifically about *long* sequences or day/night
variation, where MARS has little to say. Documented here rather than as its own page because
taking both is a cost with no extra claim attached.

## 6. How to get it

Two halves from two places — see §1's `manual`, which now records exactly where the copy on
this machine came from. There is **no working first-party link for the frames**: the ANU
project page offers a "Google Drive" link that is not one and does not resolve, so `get.py
fetch mars` has no id to use and says so. `info/` is a plain public clone and has no such
problem. This is the largest person-ReID download in this directory: 6.8 GB compressed,
~20 GB and 1.19 million files unpacked.

## 7. Licence and citation

Research use only. `licence_verified = false`.

```bibtex
@inproceedings{zheng2016mars,
  title={MARS: A Video Benchmark for Large-Scale Person Re-identification},
  author={Zheng, Liang and Bie, Zhi and Sun, Yifan and Wang, Jingdong and Su, Chi and Wang, Shengjin and Tian, Qi},
  booktitle={ECCV}, year={2016}
}
```

## 8. Traps

- **Images without `info/`.** §3. The obvious mirrors ship the frames alone, which looks like
  a complete download and is not one: without `query_IDX.mat` there is no query set, and any
  query set you invent is not MARS's. `adapters/mars.py` names all five `info/` files and stops
  rather than producing a manifest that looks finished.
- **`info/` is MATLAB only.** There is no text form of `query_IDX.mat`. `pip install
  reidbench[mat]`.
- **Dropping distractor tracklets.** §4.
- **Frame-level evaluation.** Scoring individual frames is an easier, different task. Aggregate.
- **8 frames per tracklet, not 58.** §4. `splits.frames_per_group` takes the 1,191,003 frames
  down to 163,404 before anything is encoded, which is the difference between 220 GPU-hours and
  30 on this machine. It moves the number and the manifest recipe says so.
- **Size.** One encoder pass over MARS is comparable to several passes over MSMT17; the C1-style
  grid does not fit here, and C15 should pick a small number of encoders on purpose.

## 9. Status in this project

| | |
|---|---|
| On disk | frames ✅ `data/mars/bbox_{train,test}`; `info/` ✅ cloned 2026-08-26 |
| `reidbench` adapter | ✅ `adapters/mars.py` — reads info/, emits `trackid`; needs the `mat` extra |
| `reidbench` protocol | ✅ `mars/official@1` |
| Provenance record | ✅ `mars` |
| Access | the project page's "Drive link" is broken; the frames here came from a Kaggle mirror and that is recorded in §1 |
| Experiments | ✅ **96 runs** (12 encoders x 7 heads, + 12 euclidean), at 8 frames per tracklet. Best mAP **72.70** — radio-so400m-224 + arcface; best frozen **23.61** (siglip2-giantopt-256). The head is worth 3x here: frozen features barely separate these encoders (7.8-8.5 for five of them) and the probe reorders the table entirely |
