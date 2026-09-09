---
title: "VRIC — vehicle re-id at surveillance resolution, single-shot on both sides"
kb_id: dataset-vric
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, vric, vehicle-reid, ua-detrac, low-resolution, single-shot]
retrieved: 2026-08-26
confidence: |
  high — every count below was computed from the extracted release on 2026-08-26, not read
  from a paper, and the licence line is quoted from the archive's own README.txt. The Drive
  id is copied from the project page, which was fetched the same day.
related: [dataset-veri776, dataset-vrai, dataset-vehicleid, reid-benchmarks-datasets]
---

# VRIC

> The vehicle set that looks like actual traffic camera output: small, blurred, motion-smeared
> crops, one probe and one gallery image per identity, and nowhere to hide behind a big gallery.

## 1. Facts

Single source of truth for this dataset's numbers. Every one was counted from the extracted
tree and the three annotation files on 2026-08-26.

```toml
[dataset]
name = "VRIC"
kind = "vehicle"
role = "low-resolution vehicle re-id; the single-shot, cross-camera stress case beside VeRi-776"
licence = "research only — no redistribution, no commercial use; imagery is UA-DETRAC's and carries its owners' copyright"
licence_verified = true
commercial_ok = false
access = "gdrive"
homepage = "https://qmul-vric.github.io/"
dir = "VRIC"
adapter = "vric"
protocols = ["vric/official@1"]
checked_on = "2026-08-26"
link_verified = true

[counts]
train_identities = 2811
train_images = 54808
test_identities = 2811
probe_images = 2811
gallery_images = 2811
cameras = 120
# Every test identity has exactly one probe and exactly one gallery image, and the two are
# never from the same camera — 0 same-camera pairs across all 2,811, checked. Train and test
# identities are disjoint (0 shared ids), so the published labels need no offset.
same_camera_probe_gallery_pairs = 0
shared_train_test_identities = 0
max_images_per_train_identity = 40

[expect]
"probe_images" = 2811
"gallery_images" = 2811
"train_images" = 54808
"vric_probe.txt" = 2811
"vric_gallery.txt" = 2811
"vric_train.txt" = 54808

[fetch]
gdrive_id = "1tR5K40bqpT6icSU7eVMqL2LGmiApZ0tD"
manual = """
One Google Drive file, linked from https://qmul-vric.github.io/ . `get.py fetch vric` hands
the id to gdown. The archive has no top-level directory, so unpack it *into* `data/VRIC/`
rather than into `data/`.
"""
```

## 2. What it is

Vehicle Re-Identification in Context (Kanaci, Zhu, Gong; GCPR 2018): 60,430 vehicle crops cut
out of the **UA-DETRAC** detection and tracking benchmark. Because the boxes come from a
tracking benchmark rather than from a re-id capture rig, they are whatever the detector
produced at whatever distance the camera happened to be — tiny, blurred, motion-smeared, and
wildly varying in resolution. That variation *is* the dataset. VeRi-776 asks whether an
embedding can tell two similar cars apart; VRIC asks whether it can do so on 30-pixel-tall
crops.

## 3. What is inside

```
VRIC/
  probe_images/     2,811 query images
  gallery_images/   2,811 gallery images
  train_images/    54,808 training images
  vric_probe.txt    vric_gallery.txt    vric_train.txt
  README.txt
```

The three text files are the real interface:

```
MVI_20011_016_img00105.jpg 15 1
[image name]               [pid] [camid]
```

**The filenames do not carry the identity.** `MVI_20011` is the UA-DETRAC sequence and
`img00105` the frame; the label exists only in the annotation file. This is the opposite of
Market/VeRi convention and it is why `adapters/vric.py` reads the files rather than parsing
names.

## 4. Splits and protocol

```yaml
name:    vric/official@1
query:   {split: query}
gallery: {split: gallery}
exclude: [same_uid, same_pid_same_camid]
```

**Single-shot on both sides.** One probe, one gallery image, per test identity — so there is
exactly one correct answer per query, and mAP here equals mean reciprocal rank. It is *not*
comparable to a mAP from a multi-shot benchmark, and a table that puts VRIC's mAP in the same
column as VeRi's is comparing two different quantities.

`same_pid_same_camid` is a **verified no-op** on this release: zero probe/gallery pairs share
a camera, so nothing is excluded today. It is in the protocol so that a re-packaged or extended
copy cannot change the number without the exclusion catching it.

There is no junk and no distractor class, so nothing is dropped from the gallery. The gallery
is only 2,811 images, which makes this a *small-gallery* result — the difficulty is resolution,
not scale.

## 5. How to get it

```bash
python datasets/get.py fetch vric      # gdown, id in §1
```

## 6. Licence and citation

Research only, and **two grants stack**. The archive's own README.txt says:

> This dataset should be used for research only. Please DO NOT distribute or use it for
> commercial purpose.

and, above it:

> This dataset is research only and the license belongs to the original authors of the
> UA-Detrac benchmark.

So UA-DETRAC's terms sit underneath VRIC's, and a use that VRIC permits but UA-DETRAC does not
is still not permitted. `licence_verified = true` records that VRIC's line has been read; it
does not record that UA-DETRAC's has.

```bibtex
@inproceedings{2018gcpr-Kanaci,
  author    = {Aytac Kanaci and Xiatian Zhu and Shaogang Gong},
  title     = {Vehicle Re-Identification in Context},
  booktitle = {Pattern Recognition - 40th German Conference, {GCPR} 2018, Stuttgart, Germany},
  year      = {2018}
}
@article{DETRAC:CoRR:WenDCLCQLYL15,
  author  = {Longyin Wen and Dawei Du and Zhaowei Cai and Zhen Lei and Ming-Ching Chang and
             Honggang Qi and Jongwoo Lim and Ming-Hsuan Yang and Siwei Lyu},
  title   = {{DETRAC:} {A} New Benchmark and Protocol for Multi-Object Detection and Tracking},
  journal = {arXiv CoRR}, volume = {abs/1511.04136}, year = {2015}
}
```

## 7. Traps

- **Reading VRIC's mAP as a multi-shot mAP.** §4. One relevant item per query changes what the
  number means.
- **A 2,811-image gallery is small.** Rank-1 here and rank-1 on an 80,000-image gallery are not
  the same difficulty. Say the gallery size.
- **Train and test identities are disjoint but the numbering is one global range** — train has
  2,811 ids and test has a different 2,811. Do not assume id 15 is the same vehicle in both;
  it is not in either.
- **UA-DETRAC lineage.** A model that has seen UA-DETRAC in pretraining has seen these pixels.
  Worth a line in any provenance statement.
- **`camid` is a UA-DETRAC sequence, not a physical camera** in the way VeRi's is: 120 of them,
  many recorded at the same junction. Cross-camera here means cross-sequence.

## 8. Status in this project

| | |
|---|---|
| On disk | ✅ `data/VRIC`, unpacked and verified 2026-08-26 |
| `reidbench` adapter | ✅ `adapters/vric.py` |
| `reidbench` protocol | ✅ `vric/official@1` |
| Provenance record | ✅ `vric` |
| Experiments | ✅ **96 runs** (12 encoders x 7 heads, + the 12-run euclidean control). Best mAP **35.93** — dinov3-huge-plus + arcface-msmt17; best frozen **35.74**, the same encoder. The one dataset where a head buys almost nothing (+0.19), and where DINOv3 wins while it is last or near-last on every person set |
