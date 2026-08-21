---
title: "VehicleID — front/rear only, four test subsets, ten draws each"
kb_id: dataset-vehicleid
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, vehicleid, vehicle-reid, subsets, random-draws, protocol]
retrieved: 2026-08-21
confidence: |
  medium — counts and the subset structure are well established; the current PKU access page and
  its terms have not been opened by this project.
related: [dataset-veri776, dataset-veri-wild, reid-benchmarks-datasets]
---

# VehicleID

> Vehicle breadth for C2, and the dataset whose *protocol* is more interesting than its images.

## 1. Facts

Single source of truth for this dataset's numbers.

```toml
[dataset]
name = "VehicleID"
kind = "vehicle"
role = "vehicle breadth (C2); four test subsets, ten draws each — a draw is a protocol value"
licence = "research use only; PKU release agreement"
licence_verified = false
commercial_ok = false
access = "request"
homepage = "https://pkuml.org/resources/pku-vehicleid.html"
dir = "vehicleid/VehicleID_V1.0"
adapter = ""
protocols = []
checked_on = "2026-08-21"
link_verified = false

[counts]
identities = 26267
images = 221763
test_subsets = [800, 1600, 2400, 3200]
draws_per_subset = 10
gallery_images_per_identity = 1

[expect]
"image" = 221763

[fetch]
manual = """
Front/rear views only, which is the point: it tests fine-grained model discrimination rather
than viewpoint invariance. Start the access request early — the ledger flags request latency,
not download size, as the schedule risk for the vehicle lane.
"""
```

## 2. What it is

PKU's large vehicle set, captured front-on and rear-on only — never in profile. That constraint
is deliberate: with viewpoint held nearly fixed, what is left to discriminate on is fine-grained
model and instance detail, so it tests a different thing from VeRi's cross-camera viewpoint
variation.

## 3. What is inside

```
vehicleid/VehicleID_V1.0/
  image/
  train_test_split/    train_list.txt, test_list_800.txt, test_list_1600.txt,
                       test_list_2400.txt, test_list_3200.txt
  attribute/           model and colour labels for a subset
```

## 4. Splits and protocol — where the draws come in

The evaluation is not single-query retrieval. For each test subset size,
`counts.gallery_images_per_identity` image per identity is **drawn at random** into the gallery
and the rest become probes; the draw is repeated `counts.draws_per_subset` times and the results
averaged.

Two consequences for how this project handles it:

- **A draw is a protocol value, not a random seed buried in an evaluator.** Ten draws are ten
  manifests, each carrying its seed in the manifest recipe, and ten run records. The averaging is
  `stats.aggregate` over those records — the caller writes that loop, because the caller is the
  one who knows the runs are related.
- **Subset size is part of the name.** `vehicleid/test-800@1` and `vehicleid/test-3200@1` are
  different tasks with systematically different numbers; the larger the subset the lower the
  score. A table that says only "VehicleID mAP" is unreadable.

The single-image gallery per identity also means Rank-1 dominates and mAP is close to
degenerate — report both, and expect them to move together far more than on VeRi.

## 5. How to get it

`access = request`. PKU release agreement, from the homepage in §1.

**Start this request early.** The ledger flags request latency, not download size, as the
schedule risk for the vehicle lane — the same is true of [veri-wild](veri-wild.md), and both
should go out in the same week.

## 6. Licence and citation

Research use only under the PKU agreement. `licence_verified = false`.

```bibtex
@inproceedings{liu2016deep,
  title={Deep Relative Distance Learning: Tell the Difference Between Similar Vehicles},
  author={Liu, Hongye and Tian, Yonghong and Yang, Yaowei and Pang, Lu and Huang, Tiejun},
  booktitle={CVPR}, pages={2167--2175}, year={2016}
}
```

## 7. Traps

- **Unnamed subset size.** §4.
- **One draw reported as the result.** The protocol is an average over draws; a single draw has
  visible variance and picking a good one is easy to do by accident.
- **No cross-camera structure.** There is no camera id to exclude on, so the exclusion rule is
  `same_uid` only — as with [occluded-reid](occluded-reid.md), the absence is a property of the
  data and belongs in the protocol's definition, not in a flag.

## 8. Status in this project

| | |
|---|---|
| On disk | no |
| `reidbench` adapter | not written — needs the subset and draw columns |
| `reidbench` protocol | not written — four subset names |
| Provenance record | ✅ `vehicleid` |
| Access | request; **not yet started — start it** |
