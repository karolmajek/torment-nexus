---
title: "VRAI — aerial vehicle re-id, and the benchmark that keeps its test labels"
kb_id: dataset-vrai
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, vrai, vehicle-reid, uav, aerial, withheld-labels, evalai]
retrieved: 2026-08-22
confidence: |
  high — downloaded, unpacked and inspected on 2026-08-22. Every count below except
  `counts.test.identities` was read off the extracted tree and the annotation pickles; that
  one cannot be observed here, because it is exactly the number the release withholds.
related: [dataset-veri776, dataset-vehicleid, dataset-veri-wild]
---

# VRAI

> Vehicles seen from a drone, at viewing angles no ground benchmark contains — and the only
> dataset in this directory whose **test identities are not in the download**.
>
> ✅ **Fetched and run end to end on 2026-08-22**, on the one split that can be scored locally.

## 1. Facts

Single source of truth for this dataset's numbers.

```toml
[dataset]
name = "VRAI"
kind = "vehicle / aerial (UAV)"
role = "viewpoint stress test: vehicles from above, at altitudes and angles no ground benchmark has"
licence = "research only — the release states VRAI is prohibited for any commercial use"
licence_verified = true
commercial_ok = false
access = "gdrive"
homepage = "https://github.com/JiaoBL1234/VRAI-Dataset"
dir = "VRAI"
adapter = "vrai"
protocols = ["vrai/train-cross-camera@1"]
checked_on = "2026-08-22"
link_verified = true

[counts]
cameras = 2                 # two UAVs, C1 and C2; every training identity is seen by both

[counts.train]
identities = 6302
images = 66113
trajectories = 12604        # (identity, camera) pairs — 6302 x 2, all present

[counts.test]
identities = 6720           # CITED, not observed: the labels are withheld (§3)
images = 71500
query = 15747
gallery = 55753

[counts.dev]
images = 59608
query = 3855
gallery = 55753

[counts.protocol]
# vrai/train-cross-camera@1, the only locally scorable protocol. §4.
query = 6302
gallery = 32338
positives_per_query_mean = 5.13
queries_without_a_positive = 0

[expect]
"images_train" = 66113
"images_test" = 71500
"images_dev" = 59608

[fetch]
manual = """
The download is a Google Drive FOLDER, not a file, so `get.py fetch` cannot do it: this
script drives `gdown <file-id>` and there is no file id to give it.

    pip install gdown
    gdown --folder 1S8BCBDHxXJeqyv8v6LFWS5EZHvVdrHeN -O data/VRAI

Baiduyun mirror: https://pan.baidu.com/s/1qNAMBW4VbiF9InG14BIMKA  (extraction code his6)

The folder holds images_train.tar, images_test.tar, images_dev.tar and three .pkl annotation
files. Unpack the tars in place — each contains its own top-level directory — so that
data/VRAI/ ends up with images_train/, images_test/, images_dev/ beside the pickles, then:

    python datasets/get.py verify vrai

The Drive folder also carries datasets_pkl.zip. It is NOT VRAI — it unpacks to h36m, coco,
mpii and 3dpw pose data — and nothing here reads it.
"""
```

## 2. What it is

Two UAVs, flying at 15–80 m, photographing vehicles from above. That is the whole point: the
viewpoint change between two aerial observations of one car is a change in *bearing and
altitude*, not the roughly-side-on-to-roughly-front-on change that VeRi and VehicleID
contain. Resolution is low (a typical crop here is around 320×200), the vehicles are small,
and the discriminating evidence — roof racks, sunroofs, cargo, damage — sits on surfaces that
a ground camera never sees.

The release also carries per-image annotations that most vehicle sets do not: colour, type,
four binary attributes (bumper, wheel, sky, luggage) and a list of "discriminative part"
boxes per image.

## 3. The trap that shapes everything else: the test labels are withheld

**Training filenames carry the identity. Test and dev filenames do not, and no file in the
release supplies it.**

```
images_train/00000000_0001_00000003.jpg     {id:08d}_{cam:04d}_{frame:08d}
images_test/00199XUJ_C2.jpg                 {random8}_C{cam}
images_dev/0009DI42_C1.jpg                  {random8}_C{cam}
```

The authors keep the test identities and score submissions on an
[EvalAI](https://evalai.cloudcv.org) challenge. What the pickles *do* publish for the test
and dev sets is which images are queries and which are gallery — `query_order` and
`gallery_order` — plus every attribute, keyed by image name.

Three consequences, and they are the reason this page is longer than the others:

- **`reidbench` ships no `vrai/official` protocol.** It could be selected and it could not be
  scored: every test row has `pid = -1`, so `rel` would be all-false and the mAP would be a
  number that means "the labels are missing", printed as if it meant "the encoder failed".
  The gap stays visible instead.
- **The adapter still emits those rows**, with `pid = -1` and the release's own `query` /
  `gallery` / `dev_query` / `dev_gallery` splits. Features over them are exactly what an
  EvalAI submission needs; the missing piece is a submission writer, not a manifest.
- `dev_query` and `dev_gallery` are not names this package knows, so `reidbench manifest`
  prints one warning about them on every build. That warning is the design working: an
  unknown split is a warning, never an error.

The dev set is not a subset of the test set on disk. It is the authors' practice split,
**re-anonymised**: its 55,753 gallery images are the same *count* as the test gallery under
entirely different random names, and no mapping between the two is published. So the 59,608
dev files are, in all probability, pixels you already have — and there is no way to prove it
from the release.

## 4. Splits and protocol

One protocol ships, and it is over the **training** split, because that is the only split
whose identities exist on this disk.

```yaml
name:    vrai/train-cross-camera@1
query:   {split: train, camid: 1, frame: 0}
gallery: {split: train, camid: 2}
exclude: [{pid_in: [-1]}]
```

- **Cross-camera by construction.** All 6302 training identities appear under both UAVs, so
  camera 1 against camera 2 needs no same-camera junk rule — and does not list one. Nor
  `same_uid`: the two sides are disjoint camera sets, so it could not fire either. A protocol
  that lists an exclusion which excludes nothing looks like it is protecting you when it is
  not (the same argument as [occluded-reid.md](occluded-reid.md) §4, pointing the other way).
- **`frame: 0` is one image per identity.** Every one of the 12,604 (identity, camera)
  trajectories starts at frame 0 and exactly 12,604 images carry it, so the query set is the
  first frame of each camera-1 trajectory: 6302 queries, no seed to record, no random draw to
  average over. Counts and the resulting positives-per-query are in §1.
- **Zero-shot only.** These are training images. A number here is meaningful for an encoder
  that never saw VRAI, and is meaningless for one fine-tuned on it. That is a property of the
  reader, not of the protocol, which is why it is written down here.

An `@2` would be needed to change any of this; the name is immutable.

## 5. How to get it

`access = gdrive`, and it is a Drive **folder**, which `get.py` deliberately does not
imitate. The `gdown --folder` line is in §1. No form, no signed agreement, no email.

## 6. Licence and citation

**Research only; commercial use is explicitly prohibited** by the statement in the release's
README. Same practical posture as Occluded-REID: fine for the paper, a blocker the moment any
of this goes product-facing.

```bibtex
@inproceedings{Wang2019vehicle,
  title={Vehicle Re-identification in Aerial Imagery: Dataset and Approach},
  author={Wang, Peng and Jiao, Bingliang and Yang, Lu and Zhang, Shizhou and Wei, Wei and Zhang, Yanning},
  booktitle={Proc. IEEE Int. Conf. Comp. Vis.},
  year={2019}
}
```

## 7. Traps

- **The test labels are not in the download.** §3. Everything else on this list is downstream
  of it.
- **Two filename grammars in one dataset.** §3. A single regex over the whole tree matches
  the training set and silently drops 131,108 images, or matches nothing at all.
- **The attribute tables are keyed two different ways.** In `train_annotation.pkl` they map
  *identity* → label; in the test and dev pickles they map *image name* → label. Same key
  name, different key type, in one release.
- **The annotations are pickles.** Reading a VRAI root runs whatever the pickle says. The
  release ships no other format; know where your copy came from.
- **`datasets_pkl.zip` in the Drive folder is a different dataset entirely** — Human3.6M,
  COCO, MPII and 3DPW pose data, about 7.7 GB of it. Nothing here reads it and it is not a
  VRAI file.
- **Aerial numbers are not ground numbers.** A VRAI mAP and a VeRi mAP are not the same kind
  of number and do not belong in one column without the viewpoint said out loud.

## 8. Status in this project

| | |
|---|---|
| On disk | ✅ `data/VRAI`, verified |
| `reidbench` adapter | ✅ `adapters/vrai.py` |
| `reidbench` protocol | ✅ `vrai/train-cross-camera@1`, §4 |
| Provenance record | ✅ `vrai` |
| Official test protocol | ⛔ not possible offline — labels withheld, §3 |
