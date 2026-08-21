---
title: "Occluded-REID — the occlusion stress test that has no Duke lineage"
kb_id: dataset-occluded-reid
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, occluded-reid, occlusion, person-reid, licensing, tiff]
retrieved: 2026-08-21
confidence: |
  high — downloaded, unpacked and inspected on 2026-08-21. Every count, filename and format
  fact below was read off the extracted tree, not from documentation.
related: [dataset-msmt17, dataset-ccvid, reid-c1-eval-readiness, reid-tracking-datasets]
---

# Occluded-REID

> The occlusion stress test we can use, because it has no DukeMTMC lineage.
>
> ✅ **Fetched and verified on 2026-08-21** — the only dataset in this directory that has been
> run end to end.

## 1. Facts

Single source of truth for this dataset's numbers. Everything below was read off the extracted
tree, which makes this the one page here whose counts are observations rather than citations.

```toml
[dataset]
name = "Occluded-REID"
kind = "person / occlusion stress"
role = "occlusion stress test; the non-Duke alternative to Occluded-Duke"
licence = "academic or educational use only, explicitly NOT commercial (Sun Yat-Sen University)"
licence_verified = true
commercial_ok = false
access = "direct"
homepage = "https://github.com/tinajia2012/ICME2018_Occluded-Person-Reidentification_datasets"
dir = "occluded-reid"
adapter = ""
protocols = ["occluded-reid/occluded-vs-whole@1"]
checked_on = "2026-08-21"
link_verified = true

[counts]
identities = 200
images = 2000
images_per_identity_per_side = 5
cameras = 0               # none are labelled — see §4
files_total = 2001        # 2000 images + Readme.txt
archive_mb = 41.9
unpacked_mb = 54

[counts.sides]
occluded = 1000
whole_body = 1000

[expect]
"occluded_body_images" = 200
"whole_body_images" = 200

[fetch]
urls = [
    "https://github.com/tinajia2012/ICME2018_Occluded-Person-Reidentification_datasets/raw/master/Occluded_REID.zip",
]
sha256 = "1c8854e02db775da6a51399df4b7e02c299804850dff9985451d610fc8c6d57d"
fetched_on = "2026-08-21"
manual = """
DOWNLOADED AND VERIFIED on 2026-08-21 — the one entry here that has been run end to end.

Images are {pid:03d}_{n:02d}.tif — TIFF, not JPEG, which every glob written against this set
has to know. There are NO camera labels anywhere in the release, so a protocol over it cannot
exclude same-camera matches; the exclusion is same_uid only, occluded query vs whole-body
gallery.

The same repository also ships P-DukeMTMC-reid.zip. DO NOT TAKE IT — it is Duke-derived and
denied. `get.py` fetches only the URL listed above, by construction: there is no
"download everything in the repo" verb, and that is on purpose.
"""
```

## 2. What it is

Captured on a mobile camera: people photographed both occluded and unobstructed, with occluders
that are ordinary street furniture — cars, bicycles, walls, other people. It is small, it is not
a retrieval benchmark in the Market sense, and that is fine: it is a *drop test*. Take a probe
extracted or trained elsewhere, run it here without re-fitting, and report how much you lost.

## 3. What is inside

```
occluded-reid/
  Readme.txt
  occluded_body_images/
    001/ 001_01.tif … 001_05.tif
    002/ …
  whole_body_images/
    001/ 001_01.tif … 001_05.tif
```

**Format: TIFF (`II*\0`, little-endian), not JPEG.** Every glob written against this set has to
know that, and it is the single most likely reason a first adapter run returns zero rows.

Filenames are `{pid:03d}_{n:02d}.tif`, so identity is the directory *and* the filename prefix —
either can be parsed, and they agree. Resolution is documented as 128×64.

## 4. Splits and protocol

There is no train/query/gallery split in the release. The protocol used in the literature, and
the one to encode, is: **occluded images as query, whole-body images as gallery**, with no
training on this dataset ever — it is a zero-shot drop test.

```yaml
name:    occluded-reid/occluded-vs-whole@1
query:   {split: query}
gallery: {split: gallery}
exclude: [same_uid]
```

> **The exclusion list is short for a reason: `counts.cameras` is 0.** Nothing in the filenames,
> the directory names or the readme identifies a camera, so `same_pid_same_camid` is not
> expressible here. A protocol that silently included it would be excluding nothing while
> looking like it excluded something — exactly the class of bug that named protocol values exist
> to prevent. The name says `occluded-vs-whole`, and the absence of a camera rule is a property
> of the data, recorded once.

Every query has exactly `counts.images_per_identity_per_side` true matches in the gallery and no
query image appears in the gallery, so `same_uid` is belt-and-braces rather than load-bearing —
but it stays, because a protocol that depends on the gallery *happening* not to contain the
query is a protocol waiting to break.

## 5. How to get it

```bash
python datasets/get.py fetch occluded-reid
python datasets/get.py verify occluded-reid
```

Direct HTTPS from the authors' GitHub repository; no agreement, no form, no Drive. The URL and
the sha256 are in §1.

> ⛔ **The same repository ships `P-DukeMTMC-reid.zip`.** It is Duke-derived and denied. This
> page lists exactly one URL and `get.py` has no verb that downloads a repository, so the denial
> is enforced by there being nothing to type. `P_ETHZ.zip` is also there; we have no use for it
> and it is not listed. See [dukemtmc-denied.md](dukemtmc-denied.md).

## 6. Licence and citation

**Academic or educational use only, explicitly not commercial.** The repository carries user
agreement documents in English and Chinese; final interpretation rests with Prof. Lai's group at
Sun Yat-Sen University. One of only three pages here with `licence_verified = true`.

Practical consequence: fine for the paper, and a blocker if any of this work goes product-facing
— the same posture as EUPE among the encoders, and worth pairing in the same sentence whenever
the commercial question comes up.

```bibtex
@article{zhuo2018occluded,
  title={Occluded Person Re-identification},
  author={Zhuo, Jiaxuan and Chen, Zeyu and Lai, Jianhuang and Wang, Guangcong},
  journal={arXiv preprint arXiv:1804.02792},
  year={2018}
}
```

## 7. Traps

- **TIFF, not JPEG.** §3.
- **No camera labels.** §4 — and this changes the protocol, not just the parser.
- **The gallery is tiny.** Retrieval numbers here look generous next to MSMT17's. Report the
  *drop* from a large-gallery result, not the absolute mAP, and never put the two absolute
  numbers in one column.
- **Not Occluded-Duke.** Different datasets, similar names, and one of them is denied. If a
  baseline you compare against used Occluded-Duke, say so; do not quietly compare across the two.

## 8. Status in this project

| | |
|---|---|
| On disk | ✅ `data/occluded-reid`, verified |
| `reidbench` adapter | not written — `adapters/occluded_reid.py`, plus the regression test that `occluded-duke` still resolves denied |
| `reidbench` protocol | not written — `occluded-reid/occluded-vs-whole@1`, per §4 |
| Provenance record | not written |
| Access | done |
