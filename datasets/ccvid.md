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

Single source of truth for this dataset's numbers. **These are the least verified counts in this
directory** — read from the paper, not from an extracted tree. Correct them on first fetch and
fill in the `expect` table then.

```toml
[dataset]
name = "CCVID"
kind = "person / cloth-change, video"
role = "cloth-change stress test; tracklet-shaped, needs trackid in the manifest"
licence = "research use only; released alongside Simple-CCReID, whose Apache-2.0 covers the code and not the data"
licence_verified = false
commercial_ok = false
access = "gdrive"
homepage = "https://github.com/guxinqian/Simple-CCReID"
dir = "ccvid"
adapter = ""
protocols = ["ccvid/tracklet@1", "ccvid/tracklet-cloth-changing@1"]
checked_on = "2026-08-21"
link_verified = true

[counts]
identities = 226
tracklets = 2856
frames_approx = 347000

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
# Empty on purpose: the directory names have not been observed. Fill from the download.

[fetch]
gdrive_id = ""
manual = """
The Drive file id is NOT recorded because the repository README renders its link through
GitHub's markdown and the id was not readable from the fetched page. Open
https://github.com/guxinqian/Simple-CCReID , copy the Google Drive link from the CCVID section,
and paste the id here — then `get.py fetch ccvid` works like any other Drive entry. BaiduYun is
offered as an alternative with password q0q2.

Note the licence line: Apache-2.0 covers Simple-CCReID's *code*. The video data is a separate
grant and the repo does not state it in the same place. Treat as research-only until someone
reads the release terms.
"""
```

## 2. What it is

Cloth-Changing Video re-ID, released with *Clothes-Changing Person Re-identification with RGB
Modality Only* (Gu et al., CVPR 2022). People walk past a camera in different outfits across
sessions; the point is that identity has to survive a complete change of clothing without any
auxiliary modality — no silhouette, no gait model, no skeleton. RGB only, which is what makes it
a fair test of an appearance embedding rather than of a pipeline.

## 3. What is inside

Frames grouped by identity and session, plus text files listing the tracklets per split. The
exact directory names are not restated in the repository README, so the layout is unconfirmed —
which is why `expect` in §1 is empty rather than guessed.

Each tracklet carries a clothes label as well as an identity, which is what makes the two
evaluation settings in §4 possible.

## 4. Splits and protocol

Two settings, and they answer different questions:

| Setting | Gallery | What it measures |
|---|---|---|
| **general** | everything | ordinary video ReID, same-clothes matches included |
| **cloth-changing (CC)** | same-clothes matches excluded | whether identity survives the outfit change — the number worth reporting |

In `reidbench` terms these are **two protocol values**, not a flag:
`ccvid/tracklet@1` and `ccvid/tracklet-cloth-changing@1`. The CC setting is an extra exclusion
predicate — same identity *and* same clothes id — which is the same shape as
`same_pid_same_camid` and needs no new machinery beyond a `clothid` column on the manifest.

**Tracklet handling needs no second code path.** Run `transform.aggregate(embeddings, trackid)`
first; after it there are no tracklets, only embeddings whose uids are track ids, and the
protocol is the same shape as every other one. That is exactly how `veri776/tracklet@1` already
works, and the manifest needs a `trackid` column the way VeRi's already has one.

## 5. How to get it

Google Drive, linked from the Simple-CCReID repository. **The Drive file id is not yet
recorded** — §1 says why and what to do about it.

```bash
# 1. open https://github.com/guxinqian/Simple-CCReID , copy the CCVID Drive link
# 2. paste the id into this page's [fetch] gdrive_id
python datasets/get.py fetch ccvid
```

## 6. Licence and citation

The Simple-CCReID **code** is Apache-2.0. The **data** is a separate grant and the repository
does not state its terms in the same place — treat as research-only until someone reads them,
and do not let the Apache badge on the repo page stand in for a data licence.
`licence_verified = false` for exactly this reason.

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
- **Repo licence ≠ data licence.** §6.

## 8. Status in this project

| | |
|---|---|
| On disk | no |
| `reidbench` adapter | not written — `adapters/ccvid.py`, must emit `trackid` and `clothid` |
| `reidbench` protocol | not written — two names, per §4 |
| Provenance record | not written |
| Access | blocked on one Drive id, §5 |
