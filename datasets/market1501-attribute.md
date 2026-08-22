---
title: "Market-1501 Attribute — the labels C16's H1 probe trains against"
kb_id: dataset-market1501-attribute
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, market1501, attributes, labels, c16, disentanglement]
retrieved: 2026-08-21
confidence: |
  high — the .mat is on disk and every structural claim below (field names, label coding,
  per-split identity counts, the empty `downpurple` column) was read out of it.
related: [dataset-market1501, reid-nested-attribute-protocol, reid-reidbench-owed]
---

# Market-1501 Attribute

> A few hundred kilobytes that are useless on their own and load-bearing for C16.

## 1. Facts

Single source of truth for this dataset's numbers. Identity and image counts are
[market1501](market1501.md)'s, not restated here — this release is labels only.

```toml
[dataset]
name = "Market-1501 Attribute"
kind = "person / labels"
role = "27 attribute labels over Market-1501 identities — the C16 H1 probe targets"
licence = "annotations released by the authors for research use; the images remain Market-1501's"
licence_verified = false
commercial_ok = false
access = "direct"
homepage = "https://github.com/vana77/Market-1501_Attribute"
dir = "market1501-attribute"
adapter = ""
protocols = []
checked_on = "2026-08-22"
link_verified = true
requires = "market1501"

[counts]
attributes = 27
binary_attributes = 26            # every one except `age`
age_buckets = 4                   # young · teenager · adult · old
annotation_level = "identity"     # not per image — see §7
upper_body_colours = 8
lower_body_colours = 9
bytes = 10220

[expect]
# Nothing countable: the release is one 10 KB file, and `verify` counts directory entries or
# text lines. The sha256 below is the integrity check that fits a single-file release.

[fetch]
urls = [
    "https://github.com/vana77/Market-1501_Attribute/raw/master/market_attribute.mat",
]
sha256 = "d9fdbdd2e33ed2c4e3a073b77b1d16ac9fae5d93dd597ccd4e38bf75b2efaa95"
manual = """
Labels only — a few hundred kilobytes that must be joined onto a Market-1501 manifest as extra
columns, keyed by pid. Useless without market1501 on disk first.
"""
```

## 2. What it is

Identity-level attribute annotations over Market-1501: gender, hair length, sleeve length, lower
body clothing type and length, hat, backpack, bag, handbag, age bucket, plus the upper- and
lower-body colour flags counted in §1. Annotated **per identity**, not per image — every image of
a person inherits the same labels, which is both convenient and a limitation worth naming
(clothing that changes between cameras is not represented).

It is 10 KB. Everything expensive about it was already paid for by Market-1501; this is the part
that says what the people in those boxes look like.

## 3. What is inside

```
market1501-attribute/
  market_attribute.mat        # two structs, train and test, one row per identity
```

MATLAB v5. `market_attribute.train` and `market_attribute.test` each hold **28 fields**: the 27
attributes plus `image_index`, the identity each row belongs to. Row counts follow Market's own
split — 751 train identities, 750 test.

The fields, read out of the file:

```
age  backpack  bag  handbag  clothes  down  up  hair  hat  gender
upblack upwhite upred uppurple upyellow upgray upblue upgreen
downblack downwhite downpink downpurple downyellow downgray downblue downgreen downbrown
```

Three things about the encoding, none of them guessable and all of them able to produce a
plausible-looking wrong answer:

- **Binary labels are `1` = no and `2` = yes**, not 0/1. Cast to bool and every identity is
  positive for everything.
- **`age` is not binary.** It is a 1–4 bucket, and it is the only field that is not.
- **The two structs list their fields in a different order.** Join by field *name*; anything
  that indexes by column position gets train and test labels silently transposed.

Some forks also ship CSV exports. The `.mat` is the canonical release and is small enough that
format conversion is a non-issue.

The attributes join onto a Market-1501 manifest **as extra columns keyed by `pid`**. A
`reidbench` manifest already carries arbitrary extra columns untouched, so this needs no schema
change — it needs a join.

## 4. Splits and protocol

There is no protocol here. Attributes are *targets*, not a retrieval task, and in this project
they exist for exactly one purpose: C16's H1 hypothesis, which asks whether each concept block of
a nested attribute embedding has actually specialised to the attribute family it was supposed to.

That test is a linear probe from a block's lowest nesting level to these labels — and **the probe
trains in the experiment repo, not in `reidbench`**. What the evaluator owes is the labels; what
it must not acquire is the trainer.

## 5. How to get it

```bash
python datasets/get.py fetch market1501-attribute
```

Direct HTTPS, one file, no gate. Requires [market1501](market1501.md) to already be on disk to be
worth anything.

## 6. Licence and citation

Annotations released by the authors for research use; the images remain Market-1501's, under
Market's terms. Two licences over one dataset — the ordinary situation for a label-only release,
and the reason this is its own page rather than a section of Market's.

```bibtex
@article{lin2019improving,
  title={Improving Person Re-identification by Attribute and Identity Learning},
  author={Lin, Yutian and Zheng, Liang and Zheng, Zhedong and Wu, Yu and Yu, Zhilan and Yang, Yi},
  journal={Pattern Recognition}, year={2019}
}
```

## 7. Traps

- **Identity-level, not image-level.** Occlusion, viewpoint and lighting are invisible to these
  labels; an attribute probe scored against them cannot distinguish "the model failed" from "the
  attribute is not visible in this crop".
- **Class imbalance is past severe; some columns are empty.** `downpurple` has **zero** positive
  identities in the test split and two in train — it cannot be scored at all. The next rarest test
  columns are `downyellow` (1), `downpink` (20), `downgreen` (20), `hat` (23) out of 750. `age` is
  569/751 one bucket. Report per-attribute numbers with their support, never one average, or the
  average is reporting the majority class and hiding the columns that have no minority left.
- **The distractor identities have no attributes.** The join is on labelled `pid` only.

## 8. Status in this project

| | |
|---|---|
| On disk | ✅ |
| `reidbench` adapter | none needed — extra manifest columns, joined on `pid` |
| `reidbench` protocol | not applicable — attributes are targets, not a retrieval task |
| Provenance record | not written — `market1501-attribute` |
| In the results table | never; it produces no mAP. It earns its place when C16's H1 probe exists |
