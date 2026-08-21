---
title: "VeRi-776 — the vehicle benchmark that is this project's evaluation oracle"
kb_id: dataset-veri776
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, veri776, vehicle-reid, oracle, gt-index, junk-index, validation]
retrieved: 2026-08-21
confidence: |
  high — the layout, the index files and the published numbers are pinned by `reidbench`'s
  adapter, its `veri776/official@1` protocol and two tests that run against a real root.
  medium — the current access procedure; the request flow has not been re-run recently.
related: [dataset-vehicleid, dataset-veri-wild, gallery-and-evaluation, reid-c1-eval-readiness]
---

# VeRi-776

> Present on disk, adapter shipped — and the most valuable dataset in this project for a reason
> that has nothing to do with vehicles.

## 1. Facts

Single source of truth for this dataset's numbers, including the oracle pair counts in §3.

```toml
[dataset]
name = "VeRi-776"
kind = "vehicle"
role = "the oracle: reidbench's published-number reproduction and its gt_index/jk_index test"
licence = "research use only under a signed agreement"
licence_verified = false
commercial_ok = false
access = "request"
homepage = "https://github.com/JDAI-CV/VeRidataset"
dir = "veri776/VeRi"
adapter = "veri776"
protocols = ["veri776/official@1", "veri776/tracklet@1", "veri776/naive-no-exclusion@1"]
checked_on = "2026-08-21"
link_verified = false

[counts]
identities = 776
images = 49357
cameras = 20

[counts.train]
identities = 576
images = 37778

[counts.query]
identities = 200
images = 1678

[counts.gallery]
identities = 200
images = 11579

[counts.oracle]
# The authors' own per-query enumeration, which is what makes this the cheapest oracle here.
gt_pairs = 107106
junk_pairs = 11589
pairs_total = 118695

[counts.published]
# Reproduced to the fourth decimal on 2026-08-21 from C-RADIOv4-H summary features.
mAP = 0.4531
R1 = 0.7253
R5 = 0.8564

[expect]
"image_train" = 37778
"image_test" = 11579
"image_query" = 1678
"gt_index.txt" = 1678
"jk_index.txt" = 1678

[fetch]
manual = """
Sign the agreement linked from the VeRidataset repo and email it to the authors; they reply with
a download link. Already on disk in this project — this page exists so the layout check and the
licence fact are written down, not because it needs fetching again. If your copy lives outside
./data, point REID_DATA_ROOT at it; verify never writes.
"""
```

## 2. What it is

Vehicles crossing a road network, captured over 24 hours, with each vehicle seen by several
cameras. Vehicle ReID's difficulty is the inverse of person ReID's: intra-class variation is low
and *inter*-class variation is lower still, because thousands of cars are the same model in the
same colour. The signal is in stickers, damage, roof racks and plates.

## 3. Why it is the oracle

**`gt_index.txt` and `jk_index.txt` are the authors' own per-query enumeration** of which gallery
entries are ground truth and which are junk, as 1-based indices into `name_test.txt`. That makes
them a direct, per-pair check on the exclusion rule:

```
rel & valid   ==  gt_index     same vehicle, different camera
rel & ~valid  ==  jk_index     same vehicle, same camera
```

Both hold exactly, for every query, with zero disagreements — `counts.oracle.pairs_total`
boolean comparisons rather than one scalar. Three properties make this the cheapest and best
oracle in the project:

- **It needs no encoder.** A dataset root is enough; it runs on a laptop in seconds.
- **It checks pairs, not a number.** A published mAP can be reproduced by two errors cancelling.
- **It tests the layer most likely to be wrong.** mAP is pinned by a hand-computed AP test; what
  *produces* `rel` and `valid` is the exclusion rule, and an exclusion rule is right or wrong per
  pair.

Run under `veri776/naive-no-exclusion@1` it fails on every query, on both files — which is the
check that the check is worth something. The published retrieval numbers reproduce too; they are
in §1 under `counts.published`.

## 4. What is inside

```
veri776/VeRi/
  image_train/
  image_query/
  image_test/
  gt_index.txt
  jk_index.txt
  name_test.txt
  test_track.txt
```

`test_track.txt` groups gallery images into tracklets, which is what `veri776/tracklet@1`
consumes after `transform.aggregate`. Counts are in §1.

## 5. Splits and protocol

Three named values ship:

| Name | What it is |
|---|---|
| `veri776/official@1` | single-query, same-camera exclusion, junk rule |
| `veri776/tracklet@1` | tracklet-level, after `transform.aggregate(X, trackid)` |
| `veri776/naive-no-exclusion@1` | **the bug, on purpose** — no exclusion at all |

The third one is not a mistake left in the tree. Switching the junk rule off requires asking for
it *by name*; there is no `exclude_same_camera=False` to leave unset, and the near-perfect
Rank-1 it produces is the shape of the single most common from-scratch evaluator bug.

## 6. How to get it

`access = request`. Sign the agreement linked from the dataset repository and email it to the
authors. Already on disk here.

## 7. Licence and citation

Research use only under a signed agreement. `licence_verified = false` — the agreement was
signed before this page existed and its text has not been re-read into this project.

```bibtex
@article{liu2017provid,
  title={PROVID: Progressive and Multimodal Vehicle Reidentification for Large-Scale Urban Surveillance},
  author={Liu, Xinchen and Liu, Wu and Mei, Tao and Ma, Huadong},
  journal={IEEE Transactions on Multimedia}, volume={20}, number={3}, pages={645--658}, year={2017}
}
```

## 8. Traps

- **The training image count is cited two ways in the wild**, including in this repository's own
  top-level README before it was pointed here. `counts.train.images` is what the release
  contains and what `verify` checks — if your copy disagrees, that is a finding about your copy.
- **Tracklet vs image level.** VeRi is routinely reported both ways and the numbers differ a lot.
- **It is a vehicle dataset.** Its value to a person-ReID paper is as an evaluator oracle and a
  breadth row, not as evidence about people.

## 9. Status in this project

| | |
|---|---|
| On disk | ✅ |
| `reidbench` adapter | ✅ `adapters/veri776.py` |
| `reidbench` protocol | ✅ three values, §5 |
| Provenance record | ✅ `veri776` |
| Tests | ✅ `test_veri_gt_index.py`, `test_veri_golden.py` |
