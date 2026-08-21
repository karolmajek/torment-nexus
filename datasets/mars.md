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
licence = "research use only"
licence_verified = false
commercial_ok = false
access = "gdrive"
homepage = "https://github.com/liangzheng06/MARS-evaluation"
dir = "mars"
adapter = ""
protocols = []
checked_on = "2026-08-21"
link_verified = false

[counts]
identities = 1261
tracklets = 20478
images = 1191003
cameras = 6
distractor_tracklets_approx = 3200
train_identity_dirs = 625
test_identity_dirs = 636
unpacked_gb_approx = 20

[counts.ls_vid]
# The alternative, documented here because it is one choice, not two datasets — see §5.
identities = 3772
tracklets = 14943
cameras = 15

[expect]
"bbox_train" = 625
"bbox_test" = 636

[fetch]
gdrive_id = ""
manual = """
Two halves, and both are needed:
  1. bbox_train/ and bbox_test/ image archives from Liang Zheng's MARS project page
     (Google Drive / BaiduYun) — paste the id above once you have it;
  2. the info/ split metadata: git clone https://github.com/liangzheng06/MARS-evaluation
     and take info/.
The images without info/ are useless: the tracklet boundaries and the query index live there.
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

Tracklet-to-tracklet retrieval, with same-camera exclusion as usual. As with
[ccvid](ccvid.md) and [veri776](veri776.md), this needs **no second code path** — run
`transform.aggregate(X, trackid)` and afterwards there are no tracklets, only embeddings whose
uids are track ids, and the protocol is the same shape as every other one.

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

Two halves from two places — see §1's `manual`. The Drive id for the image archives is **not
recorded**; fill it in from the project page on first fetch. This is the largest person-ReID
download in this directory.

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

- **Images without `info/`.** §3.
- **Dropping distractor tracklets.** §4.
- **Frame-level evaluation.** Scoring individual frames is an easier, different task. Aggregate.
- **Size.** One encoder pass over MARS is comparable to several passes over MSMT17; the C1-style
  grid does not fit here, and C15 should pick a small number of encoders on purpose.

## 9. Status in this project

| | |
|---|---|
| On disk | no |
| `reidbench` adapter | not written — must emit `trackid` |
| `reidbench` protocol | not written |
| Provenance record | not written |
| Access | Drive id not yet recorded; `info/` is a plain clone |
