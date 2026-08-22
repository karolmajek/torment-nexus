---
title: "ReID in Object Detection & Tracking — Concepts, Paradigms, Failure Modes"
kb_id: reid-in-mot
type: concept / survey
domain: computer-vision, multi-object-tracking, re-identification, surveillance, sports-analytics
status: stable field overview; architecture landscape as of mid-2026
tags: [reid, mot, mtmc, data-association, appearance-embedding, tracking-by-detection, jde, sde, occlusion, open-set, hota, idf1]
supersedes: null
related: [reid-glossary, reid-mot-metrics, reid-tracking-challenges-2026h2, reid-tracking-datasets, openood-v1.5, halo-loss, matryoshka-representation-learning, disentangled-attribute-embeddings]
retrieved: 2026-08-18
confidence: high (concepts and architectures); medium (relative SOTA rankings — verify against live leaderboards)
---

# ReID in Object Detection & Tracking

## TL;DR

**Re-identification (ReID)** is the appearance-matching component of a tracking system: given a detected box, produce an embedding such that crops of the *same* physical instance are close and crops of *different* instances are far, across time, occlusion, viewpoint, and camera.

In modern trackers ReID is **one term in an association cost**, not the whole tracker. Motion and geometry usually carry short-term association; ReID earns its keep on **long gaps, re-entries, crowded scenes, and cross-camera links**.

**The three facts that explain most of the field:**
1. Detection and ReID want *opposite* things from a backbone — invariance vs. discrimination. Every joint architecture is a negotiation of that conflict.
2. On benchmarks with distinctive clothing, appearance dominates. On benchmarks with uniforms (DanceTrack, sports), appearance nearly collapses and motion dominates.
3. Cross-camera tracking (MTMC) is where ReID stops being optional — there is no motion prior across disjoint views.

---

## 1. Where ReID sits in the pipeline

```mermaid
flowchart TD
    V["Video stream / multi-camera rig"] --> DET["Detector<br/>YOLO family, DINO, RT-DETR, Mask-RCNN"]
    DET --> CROP["Box crops + confidence"]

    CROP --> APP["ReID encoder<br/>embedding f of x, unit norm, D dims"]
    DET --> MOT["Motion model<br/>Kalman filter, camera motion compensation"]

    APP --> COST["Association cost matrix"]
    MOT --> COST
    COST --> ASSIGN["Assignment<br/>Hungarian or greedy, gated"]

    ASSIGN --> TRK["Tracklets<br/>per camera, single-camera tracking"]
    TRK --> BANK["Identity gallery<br/>EMA features, tracklet pooling"]
    BANK --> APP

    TRK --> MTMC["Cross-camera clustering<br/>MTMC / MCMT"]
    MTMC --> OUT["Global IDs + trajectories"]

    classDef reid fill:#e0e7ff,stroke:#4f46e5,color:#1e1b4b
    classDef det fill:#fef3c7,stroke:#d97706,color:#78350f
    class APP,BANK,MTMC reid
    class DET,CROP det
```

**Two distinct jobs, often conflated:**

| Job | Scope | Time horizon | Dominant signal |
|---|---|---|---|
| **Short-term association** | Within one camera, frame to frame | 1–10 frames | Motion / IoU. ReID is a tiebreaker. |
| **Long-term re-association** | Within one camera, after occlusion or exit | 10–1000+ frames | ReID. Motion priors have decayed. |
| **Cross-camera (MTMC / MCMT)** | Disjoint or overlapping views | Any | ReID + spatio-temporal topology constraints. |
| **Query-based retrieval** | No video, gallery of crops | N/A | Pure ReID. This is the classic Market-1501 setting. |

> **KB rule of thumb:** if a paper reports only MOT17 numbers, its ReID component is barely being tested. MOT17 is a detection benchmark wearing a tracking costume.

---

## 2. Architecture taxonomy

```mermaid
flowchart TD
    ROOT["How does the tracker get identity?"]

    ROOT --> M["A. Motion-only<br/><i>no appearance model at all</i>"]
    ROOT --> SDE["B. SDE — Separate Detection & Embedding<br/><i>two networks, two forward passes</i>"]
    ROOT --> JDE["C. JDE — Joint Detection & Embedding<br/><i>one backbone, two heads</i>"]
    ROOT --> Q["D. Query / attention-based<br/><i>identity is implicit in a persistent query</i>"]
    ROOT --> FM["E. Foundation-model trackers<br/><i>promptable segmentation + memory</i>"]

    M --> M1["SORT, ByteTrack, OC-SORT<br/>Kalman + IoU, low-score box recovery"]
    SDE --> S1["DeepSORT, StrongSORT,<br/>BoT-SORT, Deep OC-SORT<br/>plug in any ReID model"]
    JDE --> J1["JDE, FairMOT, CSTrack<br/>shared features, ReID head"]
    Q --> Q1["TrackFormer, MOTR, MeMOTR,<br/>MOTRv2 — track queries persist"]
    FM --> F1["SAM2 / SAMURAI-style,<br/>often bolted to an explicit ReID module"]

    classDef a fill:#d1fae5,stroke:#059669,color:#064e3b
    classDef b fill:#e0e7ff,stroke:#4f46e5,color:#1e1b4b
    classDef c fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef d fill:#fce7f3,stroke:#db2777,color:#831843
    class M,M1 a
    class SDE,S1 b
    class JDE,J1 c
    class Q,Q1,FM,F1 d
```

### Trade-off table

| Family | ReID quality | Speed | Retrainable per-domain? | Typical use |
|---|---|---|---|---|
| Motion-only | none | fastest | n/a | High-framerate, low-occlusion, uniform-clothing scenes |
| **SDE** | best — ReID model chosen freely | 2 forward passes | yes, independently | Production surveillance, MTMC, competition entries |
| **JDE** | compromised by task conflict | 1 forward pass | coupled retraining | Edge / embedded, real-time constraints |
| Query-based | implicit, hard to inspect | medium | end-to-end only | Research; strong on short-term, weaker on long re-entry |
| Foundation-model | depends on bolted-on ReID | slow | prompt/finetune | Long single-object tracking, novel domains |

**Why SDE won back the competition leaderboards:** decoupling lets you swap a domain-specific ReID encoder (e.g., a sports-jersey model, a wildlife MegaDescriptor) without touching the detector, and lets you train the ReID model on cheap crop-level labels instead of expensive tracking annotations.

---

## 3. The detection / ReID objective conflict

This is the single most cited structural problem in joint architectures.

```mermaid
flowchart LR
    subgraph DETG["Detector wants"]
        D1["Intra-class INVARIANCE<br/>every person maps near<br/>the same 'person' region"]
        D2["Coarse, low-dim,<br/>semantically pooled features"]
    end
    subgraph REIDG["ReID wants"]
        R1["Intra-class DISCRIMINATION<br/>every person maps to<br/>their own point"]
        R2["Fine-grained, high-dim,<br/>spatially detailed features"]
    end
    subgraph CONF["Conflicts in a shared backbone"]
        C1["Anchor ambiguity:<br/>one anchor, many identities"]
        C2["Feature-scale mismatch:<br/>detection needs multi-scale,<br/>ReID needs consistent scale"]
        C3["Dimension mismatch:<br/>ReID overfits at high D<br/>on small tracking datasets"]
    end
    DETG --> CONF
    REIDG --> CONF
    CONF --> FIX["Mitigations:<br/>anchor-free heads, low-dim ReID head,<br/>gradient balancing, or just go SDE"]
```

Practical mitigations, in ascending order of how much they actually work:
1. **Anchor-free detection heads** — removes the one-anchor-many-identities ambiguity.
2. **Low-dimensional ReID head** (64–128 D instead of 512–2048) — reduces overfitting on small MOT training sets.
3. **Uncertainty-based loss weighting** between the detection and ReID losses.
4. **Just use SDE.** The compute cost is real but the accuracy gap is larger.

---

## 4. The association cost — where ReID actually enters

A tracklet $T_i$ with gallery embedding $g_i$ and a detection $d_j$ with embedding $e_j$:

```
C[i][j] = lambda * d_app(g_i, e_j) + (1 - lambda) * d_motion(T_i, d_j)
```

- `d_app` — cosine distance, typically on L2-normalized embeddings.
- `d_motion` — IoU, GIoU, or Mahalanobis distance under the Kalman covariance.
- **Gating** — hard-reject pairs beyond a motion or appearance threshold *before* assignment. Gating usually matters more than the exact λ.

### Gallery / feature-bank management

| Strategy | Description | When to use |
|---|---|---|
| **Last observation** | Keep only the most recent embedding | Fast-changing appearance, short tracks |
| **EMA update** | `g ← α·g + (1−α)·e`, α ≈ 0.9 | Default in StrongSORT / BoT-SORT lineage |
| **Feature bank** | Keep last *k* embeddings, match against min-distance | Occlusion-heavy scenes |
| **Tracklet pooling** | Average or attention-pool all confident frames | Offline / two-stage MTMC |
| **Global tracklet association (GTA)** | Cluster whole tracklets offline after single-camera tracking | Competition pipelines, sports |

> **Trap:** EMA silently absorbs occluder appearance. Update the gallery only on high-confidence, low-occlusion, high-IoU-consistency detections, or identities drift into each other.

---

## 5. When ReID helps and when it doesn't

```mermaid
flowchart TD
    Q{"Does appearance carry identity<br/>in this domain?"}

    Q -->|"Distinctive clothing,<br/>street surveillance"| A["ReID dominates.<br/>MOT17/20, MSMT17, MTMC"]
    Q -->|"Uniforms, identical agents,<br/>fast non-linear motion"| B["ReID nearly useless.<br/>DanceTrack, SportsMOT.<br/>Motion + jersey OCR instead"]
    Q -->|"Disjoint cameras"| C["ReID is the ONLY signal.<br/>No motion prior crosses the gap"]
    Q -->|"Tiny objects, aerial,<br/>maritime, low resolution"| D["ReID degrades hard.<br/>Use platform metadata:<br/>GPS, altitude, gimbal pose"]
    Q -->|"Same individual, different day,<br/>different clothes"| E["Clothes-changing ReID.<br/>Gait, body shape, face, soft biometrics"]

    classDef good fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef bad fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class A,C good
    class B,D,E bad
```

**The DanceTrack lesson (2022, still the field's sharpest correction):** a benchmark where every subject wears near-identical costumes and moves non-linearly caused appearance-heavy trackers to lose most of their advantage. This established that MOT17 gains had been partly a clothing-diversity artifact.

**The ByteTrack lesson:** recovering *low-confidence* detections and associating them by motion alone beat many appearance-based trackers on MOT17. Detection quality and box recall are often the real bottleneck, not the embedding.

---

## 6. Open problems as of 2026

| Problem | Why it is hard | Where it shows up |
|---|---|---|
| **Clothes-changing / long-term ReID** | The dominant visual cue is the one that changed | PRCC, LTCC, DeepChange, CCVID |
| **Open-set / unknown identities** | Closed-set retrieval always returns a rank-1. A deployed system must say "not in gallery" | See §7 — calibration/OOD link |
| **Cross-view: aerial ↔ ground** | Extreme viewpoint and resolution gap | AG-ReID, UAV-Human, SeaDronesSee |
| **Sim2Real** | Synthetic training data is now cheap; the domain gap is not | AI City 2026 Tracks 1/2/4 are all explicitly Sim2Real |
| **Text-to-person retrieval** | Cross-modal alignment; behaviour descriptions not just appearance | CUHK-PEDES, ICFG-PEDES, AI City Track 4 |
| **Identity discovery (no gallery)** | Clustering with unknown *k*, scored by ARI not mAP | AnimalCLEF 2026 |
| **Edge deployment** | ReID is a per-box forward pass; cost scales with crowd density | MaCVi embedded subtracks |
| **Privacy / legal** | GDPR, EU AI Act treat biometric identification as high-risk; some classic datasets have been withdrawn | DukeMTMC retraction; Hafnia privacy-preserved track |
| **Foundation-model ReID** | Strong generic encoders — DINOv2, CLIP — are not automatically good instance discriminators | Active research direction |

---

## 7. Link to calibration and OOD detection

Open-set ReID is structurally the same problem as OOD rejection in classification, and the same failure mode appears: **an unconstrained similarity score saturates and the system confidently returns a wrong rank-1 for an identity that was never enrolled.**

```mermaid
flowchart LR
    subgraph CLS["Classification framing"]
        C1["Softmax over K classes"] --> C2["No 'none of the above'"]
        C2 --> C3["Overconfident on OOD input"]
    end
    subgraph REID["ReID framing"]
        R1["Cosine similarity to<br/>gallery of K identities"] --> R2["Rank-1 always exists"]
        R2 --> R3["Confident false match<br/>on an unenrolled person"]
    end
    CLS -.-> FIX
    REID -.-> FIX
    FIX["Shared remedies:<br/>bounded distance-based scores,<br/>explicit abstain / reject option,<br/>threshold calibrated on a validation split,<br/>report FPR at fixed TPR — not just rank-1"]
```

- See **[halo-loss](halo-loss-kb.md)** for a distance-based logit formulation with a parameter-free abstain class — directly transferable to an open-set ReID head.
- See **[openood-v1.5](openood-kb.md)** for evaluation discipline: never tune the rejection threshold on the test gallery, report an operating-point metric (FPR@95) alongside a threshold-free one (AUROC), and stratify near vs. far distractors. The near/far OOD split maps cleanly onto *hard distractor* vs. *easy distractor* identities.

---

## 8. Minimal working recipe

For a new domain, in order:

1. **Fix detection first.** Measure DetA in isolation. Most "tracking failures" are missed boxes.
2. **Baseline with motion only** (ByteTrack / OC-SORT). This is your floor and it is often surprisingly high.
3. **Add an off-the-shelf ReID encoder** in SDE mode. Measure the AssA delta. If it is under ~2 points, appearance is not your bottleneck — stop.
4. **Fine-tune the ReID encoder on domain crops** with ArcFace or triplet + label smoothing. Crop-level labels are far cheaper than tracking labels.
5. **Add camera motion compensation** before touching anything more exotic. On moving platforms this beats better embeddings.
6. **Tune gating thresholds on a validation split**, never on test.
7. **Only then** consider tracklet-level offline association, re-ranking, or ensembles.

---

## 9. Terms

Defined once, in **[glossary.md](../glossary.md)** — never here. Used on this page:

[ReID](../glossary.md#11-what-is-being-asked) · [Open-set ReID](../glossary.md#11-what-is-being-asked) · [Person search](../glossary.md#11-what-is-being-asked) · [MTMC / MCMT](../glossary.md#12-named-settings) ·
[Gallery](../glossary.md#21-gallery-anatomy) · [Query / probe](../glossary.md#21-gallery-anatomy) · [Distractor](../glossary.md#21-gallery-anatomy) · [CMC](../glossary.md#22-retrieval-metrics) ·
[Re-ranking](../glossary.md#22-retrieval-metrics) · [SDE](../glossary.md#31-pipeline-pieces) · [JDE](../glossary.md#31-pipeline-pieces) · [SCT](../glossary.md#31-pipeline-pieces) ·
[Tracklet](../glossary.md#31-pipeline-pieces) · [GTA](../glossary.md#31-pipeline-pieces) · [Gating](../glossary.md#31-pipeline-pieces)

---

## 10. Sources and pointers

- MOTChallenge benchmark family — https://motchallenge.net/
- TrackEval, the reference metric implementation — https://github.com/JonathonLuiten/TrackEval
- AI City Challenge, 10th edition at ECCV 2026 — https://www.aicitychallenge.org/
- MaCVi maritime tracking + ReID benchmarks — https://macvi.org/
- SoccerNet sports tracking / game-state reconstruction — https://www.soccer-net.org/
- Companion KB entries: [reid-mot-metrics](reid-mot-metrics-kb.md), [reid-tracking-challenges-2026h2](reid-tracking-challenges-2026h2-kb.md), [reid-tracking-datasets](reid-tracking-datasets-kb.md)

---

## 11. Retrieval hints

Answers: *what is ReID in tracking · SDE vs JDE · why does my tracker switch IDs · does appearance help on DanceTrack · how do I combine motion and appearance cost · what is a feature bank / EMA gallery · why is joint detection and ReID hard · what is MTMC · open-set re-identification · clothes-changing ReID · how do I start a tracking project in a new domain.*

**Single most quotable fact:** detection wants intra-class invariance and ReID wants intra-class discrimination, so every joint detection-and-embedding architecture is a negotiation of directly opposed objectives — which is why separate-embedding pipelines still win most competitions.
