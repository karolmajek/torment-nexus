---
title: "Market-1501 Attribute — the labels C16's H1 probe trains against"
kb_id: dataset-market1501-attribute
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, market1501, attributes, labels, c16, disentanglement]
retrieved: 2026-08-21
confidence: |
  medium — the repository and the attribute count are well established in the literature; the
  exact field names and file format have not been downloaded and checked by this project.
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
role = "binary attribute labels over Market-1501 identities — the C16 H1 probe targets"
licence = "annotations released by the authors for research use; the images remain Market-1501's"
licence_verified = false
commercial_ok = false
access = "direct"
homepage = "https://github.com/vana77/Market-1501_Attribute"
dir = "market1501-attribute"
adapter = ""
protocols = []
checked_on = "2026-08-21"
link_verified = false
requires = "market1501"

[counts]
attributes = 27
annotation_level = "identity"     # not per image — see §7
upper_body_colours = 8
lower_body_colours = 9

[expect]
# One .mat file; filled in once the download has been seen.

[fetch]
urls = [
    "https://github.com/vana77/Market-1501_Attribute/raw/master/market_attribute.mat",
]
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

## 3. What is inside

```
market1501-attribute/
  market_attribute.mat        # train and test structs, one row per identity
```

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

Direct HTTPS. Requires [market1501](market1501.md) to already be on disk to be worth anything.

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
- **Class imbalance is severe.** Several colour flags are true for a handful of identities.
  Report per-attribute numbers, not one average, or the average will be reporting the majority
  class.
- **The distractor identities have no attributes.** The join is on labelled `pid` only.

## 8. Status in this project

| | |
|---|---|
| On disk | no |
| `reidbench` adapter | none needed — extra manifest columns, joined on `pid` |
| `reidbench` protocol | not applicable |
| Provenance record | not written — `market1501-attribute` |
| Access | one `fetch`, after Market-1501 exists |
