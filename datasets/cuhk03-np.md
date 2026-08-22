---
title: "CUHK03-NP — hard cross-domain, detected boxes, and two protocols in circulation"
kb_id: dataset-cuhk03-np
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, cuhk03, cuhk03-np, detected-boxes, protocol-split, person-reid]
retrieved: 2026-08-21
confidence: |
  high — counts, layout, download ids and citation requirements read from the CUHK03-NP README
  on 2026-08-21.
  medium — the classic-20-split structure is not restated in that README; nothing has been
  downloaded.
related: [dataset-msmt17, dataset-market1501, reid-benchmarks-datasets, reid-reidbench-owed]
---

# CUHK03-NP (detected)

> The hard cross-domain target. Two things about it are traps rather than details:
> *detected vs labelled*, and *which of the two splits*.

## 1. Facts

Single source of truth for this dataset's numbers.

```toml
[dataset]
name = "CUHK03-NP (detected)"
kind = "person"
role = "hard cross-domain target; detected boxes only, never labelled"
licence = "research use only; cite both Li 2014 and Zhong 2017"
licence_verified = true
commercial_ok = false
access = "gdrive"
homepage = "https://github.com/zhunzhong07/person-re-ranking/tree/master/CUHK03-NP"
dir = "cuhk03-np"
adapter = ""
protocols = ["cuhk03/detected-767@1"]
checked_on = "2026-08-21"
link_verified = true

[counts]
identities = 1467
images = 14097

[counts.new_protocol]
train_identities = 767
test_identities = 700

[counts.detected]
train = 7365
query = 1400
gallery = 5332

[counts.labeled]
train = 7368
query = 1400
gallery = 5328

[expect]
"detected/bounding_box_train" = 7365
"detected/query" = 1400
"detected/bounding_box_test" = 5332
"labeled/bounding_box_train" = 7368
"labeled/query" = 1400
"labeled/bounding_box_test" = 5328

[fetch]
gdrive_id = "1pBCIAGSZ81pgvqjC-lUHtl0OYV1icgkz"
manual = """
The NP release is already in Market-1501 folder format, which is why it is the one to take.
The original .mat release (drive id 0B7TOZKXmIjU3OUhfd3BPaVRHZVE) needs the two
cuhk03_new_protocol_config_*.mat split files on top and is not worth the trouble.

Take detected/. labeled/ is systematically easier and mixing the two silently is one of the
field's standard reporting errors. Baidu Yun links for both are in the README if Drive is
rate-limiting.
"""
```

## 2. What it is

CUHK03 ships each identity twice — once with hand-drawn boxes, once with DPM-detector boxes.
The detected boxes are misaligned, cropped and occasionally wrong, which is what real detector
output looks like, and they score systematically lower. **We use detected. Always.**

"NP" is the *new protocol* of Zhong et al. (2017), which re-splits the dataset by identity and —
this is why it is the version to take — republishes it in **Market-1501 folder format**, so an
adapter that already reads Market needs almost nothing new.

## 3. What is inside

```
cuhk03-np/
  detected/
    bounding_box_train/
    query/
    bounding_box_test/
  labeled/
    bounding_box_train/
    query/
    bounding_box_test/
```

Per-directory image counts are in §1 under `counts.detected` and `counts.labeled`; `verify`
checks them against the extracted tree.

## 4. Splits and protocol — two names, never a flag

Two CUHK03 protocols are in circulation and they are not comparable:

| Protocol | What it is | Reads |
|---|---|---|
| **new protocol (767/700)** | one split, identity-disjoint, Market-format | lower — the harder and now-standard one |
| **classic 20 random splits** | a 1,367/100 split, twenty of them, results averaged | higher, and averaged over 20 runs |

`reidbench` will carry these as **two protocol values with two names** —
`cuhk03/detected-767@1` and `cuhk03/detected-classic-20split@1` — never as a flag on one value.
The reasoning is the same as `veri776/naive-no-exclusion@1`: a reader who cannot see which
protocol produced a number will assume the flattering one, and a boolean parameter left at its
default is invisible in a results file.

Multiply that by detected-vs-labelled and there are four numbers that can all be called
"CUHK03 mAP". State two facts every time: **detected**, and **767**.

## 5. How to get it

Google Drive, no agreement. The file id is in §1.

```bash
python datasets/get.py fetch cuhk03-np      # delegates to gdown; prints the link if absent
python datasets/get.py verify cuhk03-np
```

## 6. Licence and citation

Research use. The README requires **both** citations — the original dataset and the new
protocol; citing only one is the common error and the README is explicit about it.

```bibtex
@inproceedings{li2014deepreid,
  title={DeepReID: Deep Filter Pairing Neural Network for Person Re-identification},
  author={Li, Wei and Zhao, Rui and Xiao, Tong and Wang, Xiaogang},
  booktitle={CVPR}, year={2014}
}
@inproceedings{zhong2017re,
  title={Re-ranking Person Re-identification with k-reciprocal Encoding},
  author={Zhong, Zhun and Zheng, Liang and Cao, Donglin and Li, Shaozi},
  booktitle={CVPR}, year={2017}
}
```

## 7. Traps

- **Detected vs labelled.** Labelled is easier; mixing them across a table is a classic silent
  inflation. Both directories are in `expect` so `verify` can confirm which you have, and the
  adapter should read `detected/` only.
- **767 vs classic-20.** §4.
- **Small gallery.** An order of magnitude smaller than MSMT17's — absolute mAP is not comparable
  across the two, only the drop is.
- **The `.mat` route wastes a day** for the same numbers.

## 8. Status in this project

| | |
|---|---|
| On disk | no |
| `reidbench` adapter | not written — `adapters/cuhk03.py`, detected only |
| `reidbench` protocol | not written — two names, per §4 |
| Provenance record | not written |
| Access | Drive id recorded; one `fetch` away |
