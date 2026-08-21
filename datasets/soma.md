---
title: "SOMA — a tracker to validate against, and 20k synthetic identities with an unresolved licence"
kb_id: dataset-soma
type: dataset page
domain: computer-vision, re-identification, tracking
tags: [dataset, soma, tracker, synthetic, generated-images, licensing, c4]
retrieved: 2026-08-21
confidence: |
  high — the repository's licence, composition and headline numbers are read from this project's
  SOMA knowledge base entry, which was built from the README.
  medium — the synthetic set's distribution route (release asset vs. generation script) has not
  been confirmed by a download.
related: [dataset-mars, reid-contribution-ledger-2026]
---

# SOMA

> Two things in one repository, with two very different licence stories, arriving by one
> `git clone`.

## 1. Facts

Single source of truth for this entry's numbers.

```toml
[dataset]
name = "SOMA (tracker + synthetic ReID set)"
kind = "tracker / synthetic person"
role = "tracker validation host for C4; also a synthetic ReID set"
licence = "MIT for the code; the generated images are a SEPARATE and unresolved question"
licence_verified = true
commercial_ok = false     # the code is MIT; the images are the reason this is false
access = "direct"
homepage = "https://github.com/PINTO0309/soma"
dir = "soma"
adapter = "folder"
protocols = ["folder/all-vs-all@1"]
checked_on = "2026-08-21"
link_verified = false

[counts.synthetic]
identities = 500
images = 20000
images_per_identity = 40
cameras = 8
train_identities = 400
test_identities = 100
identity_overlap = 0
occluded_images_per_train_identity = 12
resolution = "128x256 RGB JPEG"

[counts.tracker]
# From this project's SOMA knowledge base; the numbers that make it worth using as a host.
hota_structure_only = 29.2
hota_with_embedder = 37.4
hota_boosttrack_baseline = 28.9
recovery_5s_soma_r = 0.44
recovery_5s_boosttrack = 0.00

[expect]
# A clone, not an archive; nothing fixed to count.

[fetch]
manual = """
git clone https://github.com/PINTO0309/soma gets the code, which is MIT and reusable.

The synthetic set's exact distribution route — release asset, external host, or a generation
script you run yourself — has not been confirmed here. Check the repository before planning
around it, and note that "you generate it yourself" would make the output-terms question in §4
yours directly rather than the author's.
"""
```

## 2. What it is

A single-author, MIT-licensed, online multi-person tracker built for deployment rather than for
leaderboards. It fuses several *weak* identity channels — box IoU, part alignment, orientation
continuity — instead of one strong embedding, and optimises for re-attaching an identity after a
multi-second occlusion, a KPI the MOT benchmarks barely measure.

Its relevance here is C4: **it is a host tracker to validate encoders inside.** Read
`counts.tracker` in §1: on CrowdTrack, BoostTrack++ recovers **none** of the identities after a
~5 s occlusion while SOMA-R recovers nearly half — *fed the same detections and the same
PersonViT embeddings*. The gap is not embedding quality; it is whether the tracker keeps a
candidate alive long enough to ask the embedding a question.

**That is why C4 must be run as a grid of {encoders} × {≥2 host trackers}**, reported as effect
size rather than as a rank correlation on one tracker. A small Market mAP difference between two
encoders is worth several points of 5 s recovery in one tracker and nothing at all in another.

## 3. What is inside

| Part | Licence | Note |
|---|---|---|
| Tracker code | **MIT** | reusable, including commercially |
| Synthetic ReID set | **unresolved** | generated with gpt-image-2; composition in §1 |

Two documented gaps are worth knowing before using the synthetic set as evidence: there is **no
scaling curve** (one identity-count × images-per-identity point, so nothing says which is the
binding constraint), and **no identity-consistency audit** — generative models drift, and nothing
reports a check that a given identity is the same person across all its images.

## 4. The licence question, which is the point of this page

The images are not a collection-consent problem like DukeMTMC. They are an **output-terms**
problem: redistributing gpt-image-2 outputs as a research dataset is a live question, and so is
publishing weights trained on them. Synthetic likenesses add a second layer.

This is the only entry here whose risk is about outputs rather than about how footage was
gathered, and it is `commercial_ok = false` for that reason even though the *code* is MIT. Read
the model output terms before these images enter any table.

Also flagged loudly: the README's own ReID numbers sit above published state of the art by a
clear margin, and the evaluation protocol, query/gallery construction and possible train/test
identity overlap are not stated. Treat them as *internal* numbers for ranking SOMA's own embedder
variants; do not cite them as ReID results. They are deliberately not recorded in §1 — this
project does not restate numbers it would not stand behind.

## 5. How to get it

```bash
git clone https://github.com/PINTO0309/soma
```

The tracker is the clone. The synthetic set's route is unconfirmed — §1's `manual`.

## 6. Licence and citation

MIT for the code. No peer-reviewed paper; the software is Zenodo-archived, so cite the archive
and the repository: `https://github.com/PINTO0309/soma`.

## 7. Traps

- **The MIT badge covers the code, not the images.** §4.
- **The README's ReID numbers are not results.** §4.
- **One tracker is not a validation.** §2 — the two-tracker grid is a design requirement, not a
  thoroughness nicety, and running C4 against SOMA alone would produce a claim its own data
  contradicts.

## 8. Status in this project

| | |
|---|---|
| On disk | no |
| `reidbench` adapter | `folder` covers the synthetic set as-is |
| `reidbench` protocol | `folder/all-vs-all@1` for a first look |
| Provenance record | not written |
| Access | a clone; the licence decision is the gate, not the download |
