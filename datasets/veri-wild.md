---
title: "VERI-Wild — unconstrained vehicle ReID, day and night, over a month"
kb_id: dataset-veri-wild
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, veri-wild, vehicle-reid, night, long-term, subsets]
retrieved: 2026-08-21
confidence: |
  medium — scale and subset structure are well established in the literature; the access page and
  its terms have not been opened by this project, and nothing has been downloaded.
related: [dataset-veri776, dataset-vehicleid, reid-benchmarks-datasets]
---

# VERI-Wild

> The hardest of the three vehicle sets, and the only one that seriously tests night-time and
> long-time-span matching.

## 1. Facts

Single source of truth for this dataset's numbers.

```toml
[dataset]
name = "VERI-Wild"
kind = "vehicle"
role = "hardest vehicle set: unconstrained, day/night, long time span"
licence = "research use only; signed agreement"
licence_verified = false
commercial_ok = false
access = "request"
homepage = "https://github.com/PKU-IMRE/VERI-Wild"
dir = "veri-wild"
adapter = ""
protocols = []
checked_on = "2026-08-21"
link_verified = false

[counts]
identities = 40671
images = 416314
cameras = 174
capture_span_days = 30
test_subsets = [3000, 5000, 10000]

[expect]
# Empty until the layout has been observed.

[fetch]
manual = """
Same request pattern as VehicleID and the same schedule advice: ask early. Test subsets are by
identity count; say which one produced a number, always.
"""
```

## 2. What it is

A month of capture from a large CCTV network in an unconstrained urban area, across weather, day
and night. Where VeRi is a controlled road network and VehicleID is viewpoint-locked, VERI-Wild
is what a deployed vehicle system actually sees — which makes it the right place to look for the
failure modes the other two hide, and a poor place to expect flattering numbers.

## 3. What is inside

Images plus per-image metadata (camera id, timestamp) and the train/test split lists. The layout
has not been observed here, which is why `expect` in §1 is empty rather than guessed.

## 4. Splits and protocol

Three test subsets by identity count, exactly as [vehicleid](vehicleid.md) does it, and the same
rule applies: **the subset size is part of the protocol name**, because the numbers move a lot
between them. `veri-wild/test-3000@1` and `veri-wild/test-10000@1` are different tasks.

The timestamp metadata is the distinctive part. It supports a *time-gap* breakdown — how much
worse matching gets as the gap between probe and gallery capture grows — which is the vehicle
analogue of the long-gap recovery bins that make [soma](soma.md) interesting, and one of the few
places in this project's data where a deployment-relevant axis is directly measurable.

## 5. How to get it

`access = request`. Signed agreement, via the repository in §1. Send it early, in the same week
as the other vehicle requests. The download is large — plan for it, but the wait is the schedule
item.

## 6. Licence and citation

Research use only under a signed agreement. `licence_verified = false`.

```bibtex
@inproceedings{lou2019veriwild,
  title={VERI-Wild: A Large Dataset and a New Method for Vehicle Re-Identification in the Wild},
  author={Lou, Yihang and Bai, Yan and Liu, Jun and Wang, Shiqi and Duan, Ling-Yu},
  booktitle={CVPR}, year={2019}
}
```

## 7. Traps

- **Unnamed subset size.** §4.
- **Night images are a subpopulation, not noise.** Averaging over day and night hides the thing
  the dataset was built to expose; break the number down or say you did not.
- **Scale.** This is the largest extraction job on the board. At one forward pass per image per
  encoder per pooling per resolution, the C1 grid over this dataset is not a laptop job — price
  it against `counts.images` before committing to it.

## 8. Status in this project

| | |
|---|---|
| On disk | no |
| `reidbench` adapter | not written |
| `reidbench` protocol | not written — three subset names |
| Provenance record | not written |
| Access | request; **not yet started** |
