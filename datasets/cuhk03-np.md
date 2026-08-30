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
dir = "CUHK03/archive"
adapter = "cuhk03-detected"
protocols = ["cuhk03/detected-767@1"]
checked_on = "2026-08-25"
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
"images_detected" = 14097
"images_labeled" = 14096

[fetch]
gdrive_id = "1pBCIAGSZ81pgvqjC-lUHtl0OYV1icgkz"
manual = """
ON DISK 2026-08-25, but NOT in the layout the drive id above serves. What is here is the
*original* release — flat `images_detected/` and `images_labeled/` directories of PNGs named
{group}_{pid}_{camid}_{index}.png — together with the new-protocol split files:
`cuhk03_new_protocol_config_{detected,labeled}.mat` and the derived
`splits_new_{detected,labeled}.json` / `splits_classic_{detected,labeled}.json`.

That is a better starting point than the Market-format NP release this page used to assume,
because the classic splits ship alongside the new ones. The adapter reads the JSON, not the
.mat, so no scipy or h5py is needed. Provenance of this particular unpack is not recorded
here because it was not downloaded by `get.py fetch`.

The counts in [counts] were measured against this tree, not copied from a paper.
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
CUHK03/archive/
  images_detected/                       14,097 png   flat; {group}_{pid}_{camid}_{index}.png
  images_labeled/                        14,096 png   flat; same convention
  splits_new_detected.json                            767/700, the protocol below
  splits_new_labeled.json
  splits_classic_detected.json                        the 20-split classic protocol
  splits_classic_labeled.json
  cuhk03_new_protocol_config_detected.mat             the same split, unread
  cuhk03_new_protocol_config_labeled.mat
  cuhk03_release/cuhk-03.mat                          the original archive, unread
```

### Both packagings are on this disk, and they are the same data

`data/cuhk03-np/` holds the **CUHK03-NP release** — the widely circulated repackaging into
Market-1501 directories, renamed `{pid:04d}_c{camid}_{index}.png` with a global identity:

```
cuhk03-np/
  detected/  bounding_box_train/ 7,365   query/ 1,400   bounding_box_test/ 5,332
  labeled/   bounding_box_train/ 7,368   query/ 1,400   bounding_box_test/ 5,328
```

**Verified equal to the archive tree by decoding every image**, because the release re-encoded
the PNGs and so shares *no bytes* with it at all — a checksum comparison says they are unrelated
and is wrong. On pixels: all 14,097 detected images present in both, **0** images in a different
split, and the identity and (identity, camera) partitions **1:1 in both directions** across all
1,467 identities and 2,934 identity-camera pairs.

So the two are one dataset in two boxes. `reidbench` reads both — `cuhk03-detected` for the
archive tree, `cuhk03-np-detected` for the release — and they produce the same science and
different `uid`s, since a uid carries a relative path. **Feature caches do not transfer between
them; results do.** Everything measured here used the archive tree; re-running the release would
buy nothing but a second set of identical numbers.

There are no `bounding_box_train/` directories *in the archive tree*: there, the split is data,
not directory structure.
`verify` checks the two image directories; the per-split counts in §1 under `counts.detected`
and `counts.labeled` are what the adapter reproduces from the JSON, and they match the
published protocol exactly.

Every image is used exactly once — no file appears in two splits, and none is left over.

## 4. Splits and protocol — two names, never a flag

Two CUHK03 protocols are in circulation and they are not comparable:

| Protocol | What it is | Reads |
|---|---|---|
| **new protocol (767/700)** | one split, identity-disjoint, Market-format | lower — the harder and now-standard one |
| **classic 20 random splits** | a 1,367/100 split, twenty of them, results averaged | higher, and averaged over 20 runs |

`reidbench` carries these as **separate protocol values with separate names** —
`cuhk03/detected-767@1` and `cuhk03/labeled-767@1` ship today; a classic-20 value would be
`cuhk03/detected-classic-20split@1` and is not written, though `splits_classic_*.json` is on
disk for whoever wants it. Never a flag on one value.
The reasoning is the same as `veri776/naive-no-exclusion@1`: a reader who cannot see which
protocol produced a number will assume the flattering one, and a boolean parameter left at its
default is invisible in a results file.

Multiply that by detected-vs-labelled and there are four numbers that can all be called
"CUHK03 mAP". State two facts every time: **detected**, and **767**.

## 5. How to get it

Google Drive, no agreement. The file id is in §1.

```bash
python datasets/get.py verify cuhk03-np
```

`fetch` would serve the Market-format NP release, which is *not* what is on disk here (§1
[fetch]). Do not run it over this tree expecting a match.

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

- **The split file's `pid` is not an identity.** `splits_new_*.json` renumbers identities from
  zero *within each split*, so train `pid` 3 and query `pid` 3 are different people — 377 of the
  767 training labels collide with a test label this way. An adapter that trusts that column
  puts identities in both the training split and the gallery without any file appearing twice,
  which raises every number and looks like nothing. `adapters/cuhk03.py` takes the identity from
  the filename, which is stable across splits, and the entry's `pid`/`camid` fields are read for
  nothing at all.
- **`{group}` is part of the identity and of the camera.** CUHK03 is five camera pairs, each
  numbering its people and its two cameras from one. Person 001 of group 1 is not person 001 of
  group 3, and their cameras are unrelated. The adapter encodes `pid = group*1000 + n` and
  `camid = group*10 + c`.
- **Detected vs labelled.** Labelled is easier; mixing them across a table is a classic silent
  inflation. Both directories are in `expect` so `verify` can confirm which you have, and the
  two variants are separate adapters with separate uid namespaces so they cannot pool.
- **767 vs classic-20.** §4.
- **Small gallery.** An order of magnitude smaller than MSMT17's — absolute mAP is not comparable
  across the two, only the drop is.
- **The `.mat` route wastes a day** for the same numbers.

## 8. Status in this project

| | |
|---|---|
| On disk | ✅ `data/CUHK03/archive` (measured) and `data/cuhk03-np` (the release; proven identical, not re-run) |
| `reidbench` adapter | ✅ `adapters/cuhk03.py` — `cuhk03-detected`, `cuhk03-labeled`, and `cuhk03-np-detected`, `cuhk03-np-labeled` for the release packaging |
| `reidbench` protocol | ✅ `cuhk03/detected-767@1`, `cuhk03/labeled-767@1` |
| Provenance record | not written |
| Measured | ✅ [results/tables/cuhk03-np.md](../results/tables/cuhk03-np.md) |
