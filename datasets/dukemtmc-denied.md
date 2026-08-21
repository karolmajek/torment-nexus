---
title: "DukeMTMC and every derivative — denied, with no override flag"
kb_id: dataset-dukemtmc-denied
type: dataset page / policy
domain: computer-vision, re-identification, research-ethics
tags: [dataset, dukemtmc, denied, ethics, licensing, policy, occluded-duke]
retrieved: 2026-08-21
confidence: |
  high — the retraction and its reasons are settled fact, and the denial is enforced in two
  independent places in this project's code.
related: [dataset-occluded-reid, dataset-msmt17, reid-tracking-datasets, reid-benchmarks-datasets]
---

# DukeMTMC — denied

> **Do not download it. Do not accept a copy. Do not cite a number produced from it as ours.**
> This page exists so the reason is written down once, and so the alternatives are one click
> away from the refusal.

## 1. What is denied

This block is the policy, and `get.py` reads it — the refusal in the code and the reason on this
page are the same text, not two copies of it.

```toml
[denied]
ids = [
    "dukemtmc",
    "dukemtmc-reid",
    "dukemtmc-videoreid",
    "occluded-duke",
    "p-dukemtmc-reid",
    "duke-mtmc",
]
reason = "DukeMTMC lineage — withdrawn dataset, non-consensual collection, denied with no override"
use_instead = "occluded-reid for occlusion; msmt17 or market1501 for a second person domain"

[policy]
default_root = "data"
```

| Denied | What it is |
|---|---|
| `DukeMTMC` | the parent multi-camera tracking dataset |
| `DukeMTMC-reID` | the ReID crop derivative — the "Duke" in almost every classic-four table |
| `DukeMTMC-VideoReID` | the video derivative |
| `Occluded-Duke` | the occlusion benchmark built on it |
| `P-DukeMTMC-reID` | the partial/occluded derivative shipped beside Occluded-REID |

The denial is on **lineage**, not on the name. A future derivative under a new name is denied by
the same rule.

## 2. Why

DukeMTMC was withdrawn by its authors over how the data was collected and distributed:
surveillance footage of students on a university campus, gathered without meaningful consent and
redistributed for research use worldwide. The retraction is the most important licensing fact in
this field, and derivatives inherit the problem — cropping people out of withdrawn footage does
not launder the footage.

The practical layer, for anyone weighing this as a cost/benefit: reviewers increasingly flag its
use, and EU AI Act compliance review treats non-consensual biometric collection as a live issue
rather than a historical one. But the practical layer is not why it is denied here. It is denied
because the people in those frames did not agree to be in them.

## 3. How the denial is enforced

Two places, independently, neither importing the other:

| Where | What it does |
|---|---|
| `datasets/get.py` | `fetch`, `show` and `ls` refuse by name and exit 3; `verify` reports a denied dataset found anywhere under the data root |
| `reidbench.provenance` | `deny_if_denied(dataset)` is called **inside every adapter**, so a denied dataset cannot enter a manifest |

**There is no override flag in either.** That is a design decision, tested by reading the module's
own source — because the absence of a feature is otherwise untestable. A flag would mean the
denial holds only until somebody is in a hurry.

The `reidbench` copy exists separately because that package has to stand alone: someone who
installs the wheel gets the denial without this repository.

## 4. The trap that actually comes up

The Occluded-REID download — a dataset we *do* use — lives in a repository that also ships
`P-DukeMTMC-reid.zip`. The registry lists exactly one URL for that entry, and `get.py` has no
verb that downloads a repository, so the denial is enforced by there being nothing to type.

The second trap is comparison rather than download: a baseline you are comparing against may
report Occluded-Duke numbers. Say so explicitly rather than quietly putting them in the same
column as an Occluded-REID number. They are different datasets.

## 5. What to use instead

| Instead of | Use | Page |
|---|---|---|
| DukeMTMC-reID as a second person domain | MSMT17, or Market-1501 | [msmt17.md](msmt17.md), [market1501.md](market1501.md) |
| Occluded-Duke | Occluded-REID | [occluded-reid.md](occluded-reid.md) |
| DukeMTMC-VideoReID | MARS, or CCVID for cloth-change | [mars.md](mars.md), [ccvid.md](ccvid.md) |
| DukeMTMC for MTMC tracking | WILDTRACK, or the MTMC_Tracking corpora | — |

Every one of these is a real substitute. The denial costs this project a comparison row, not a
capability.

## 6. If someone hands you a copy

Say no, and say why in one sentence without making it a conversation. If it is already on the
machine, `python datasets/get.py verify --all` will find it and name the path — deleting it is
the whole remediation.
