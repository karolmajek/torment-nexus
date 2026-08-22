---
title: "Agglomerative Vision Foundation Models — RADIO, EUPE, and the Multi-Teacher Distillation Family"
kb_id: agglomerative-vfm
type: reference / model family
domain: computer-vision, foundation-models, knowledge-distillation, representation-learning
tags: [agglomerative, multi-teacher-distillation, am-radio, c-radiov4, radiov2.5, eupe, dune, unic, theia, sam-clip, amoe, dinov3, siglip2, sam3, proxy-teacher, licensing]
related: [reid-glossary, foundation-model-reid, reid-in-mot]
retrieved: 2026-08-18
confidence: high for model composition and lineage; verify parameter counts and benchmark numbers against the current model cards — this family ships releases every few months
---

# Agglomerative Vision Foundation Models

## TL;DR

**Agglomerative models distill several heterogeneous vision foundation models into one student.** The premise: CLIP-family, DINO-family, and SAM-family encoders are each excellent at one thing and mediocre at the others, and running three encoders is impractical. Merge them.

The result is repeatedly that the student **matches or beats its own teachers** on most tasks while running once instead of three times.

**Current state of the art, mid-2026:**
- **C-RADIOv4** (NVIDIA, Jan 2026) — teachers SigLIP2-g-384 + DINOv3-7B + SAM3. Commercially licensed. The strongest general-purpose entry.
- **EUPE** (Meta, Mar 2026) — flips the recipe: scale *up* to a 1.9B proxy teacher first, then scale *down*. Targets edge deployment. Research licence only.

**The name is NVIDIA's:** AM-RADIO = "Agglomerative Model — Reduce All Domains Into One". The term has since become the field's generic label.

---

## 1. The core idea

```mermaid
flowchart LR
    subgraph TEACH["Frozen heterogeneous teachers"]
        T1["Vision-language<br/>CLIP / SigLIP2<br/>→ zero-shot, VLM alignment"]
        T2["Self-supervised<br/>DINOv2 / DINOv3<br/>→ dense, geometric, spatial"]
        T3["Segmentation<br/>SAM / SAM3<br/>→ boundaries, masks"]
    end

    T1 --> D["Label-free feature-matching<br/>distillation"]
    T2 --> D
    T3 --> D

    D --> S["Single student encoder"]
    S --> ADP["Per-teacher adaptor heads<br/>can emulate each teacher's<br/>output space"]

    S --> OUT1["One forward pass"]
    S --> OUT2["Often exceeds the teachers<br/>on a majority of tasks"]
    S --> OUT3["Arbitrary resolution<br/>and aspect ratio"]

    classDef t fill:#e0e7ff,stroke:#4f46e5,color:#1e1b4b
    classDef s fill:#dcfce7,stroke:#16a34a,color:#14532d
    class T1,T2,T3 t
    class S,OUT1,OUT2,OUT3 s
```

**No labels are used.** The student matches teacher *features*, not ground-truth classes. This is what makes it cheap relative to training a foundation model from scratch.

---

## 2. Lineage

```mermaid
flowchart TD
    A["AM-RADIO — CVPR 2024, NVIDIA<br/>Distill CLIP + DINOv2 + SAM.<br/>Introduces E-RADIO, ~6x faster<br/>than teachers at matched resolution"]

    A --> B["Problems surface"]
    B --> B1["Resolution mode shift"]
    B --> B2["Teacher imbalance —<br/>loss scales differ wildly"]
    B --> B3["Idiosyncratic teacher artifacts<br/>get copied by the student"]
    B --> B4["Too many output tokens<br/>for VLM integration"]

    B2 --> C["PHI-S<br/>Distribution balancing for<br/>label-free multi-teacher distillation"]
    B1 --> D["RADIOv2.5 — CVPR 2025<br/>Multi-resolution training,<br/>mosaic augmentation,<br/>improved teacher loss balancing,<br/>token compression"]
    C --> D
    B3 --> E["FeatSharp<br/>sharper student features"]

    D --> F["C-RADIOv4 — Jan 2026<br/>New teachers: SigLIP2-g-384,<br/>DINOv3-7B, SAM3.<br/>Shift-equivariant losses,<br/>stochastic resolution, ViTDet mode,<br/>commercially permissive licence"]
    E --> F

    A -.->|"parallel lines"| P["SAM-CLIP · Apple<br/>UNIC · Naver Labs Europe<br/>Theia · robot learning<br/>SAK · DUNE"]
    D -.-> Q["AMoE / SigLino<br/>Mixture-of-Experts student,<br/>DINOv3 + SigLIP2 teachers"]
    D -.-> R["EUPE · Meta, Mar 2026<br/>proxy-teacher recipe"]
```

---

## 3. The models

### 3.1 C-RADIOv4 — NVIDIA, January 2026

| Property | Detail |
|---|---|
| **Teachers** | SigLIP2-g-384, DINOv3-7B, SAM3 |
| **Sizes** | B ≈ 98M · L ≈ 320M · SO400M ≈ 431M · H ≈ 653M |
| **Resolution range** | ~128px to 1152px+, trained stochastically across it |
| **Licence** | NVIDIA Open Model License — **commercial use permitted** |
| **Access** | `torch.hub` (`c-radio_v4-h`, `c-radio_v4-so400m`) and Hugging Face |
| **Repo** | https://github.com/NVlabs/RADIO |

**Technical contributions over RADIOv2.5:**

- **Stochastic resolution training** — smooths the performance-vs-resolution curve and notably improves low-resolution behaviour, historically the weak point of distilled encoders.
- **Shift-equivariant dense loss** — teacher and student see independently shifted crops. This is the fix for a real problem: distilling large models copies their *artifacts*, not just their useful structure. SigLIP2 has border noise patterns; ViTDet-style models show window-boundary artifacts. Direct feature regression forces the student to reproduce them. Shift equivariance suppresses fixed-pattern noise.
- **Balanced summary loss** — improved angular loss normalisation between teachers, so no teacher's gradient scale dominates.
- **ViTDet mode** — optional windowed attention that sharply cuts inference time at high resolution.
- **Can replace SAM3's vision encoder** for segmentation tasks directly.

**Claimed positioning:** performance competitive with models roughly an order of magnitude larger; on ADE20k linear probing the scaling trend tracks DINOv3-7B with ~10× fewer parameters.

### 3.2 EUPE — Meta, March 2026

**Efficient Universal Perception Encoder.** From Meta Reality Labs + FAIR. The interesting one because it *disagrees with the recipe*.

```mermaid
flowchart LR
    subgraph OLD["Previous agglomerative approach"]
        O1["3 foundation teachers"] --> O2["small student directly"]
        O2 --> O3["Problem: a ViT-B does not have<br/>enough capacity to absorb<br/>three feature spaces at once"]
    end

    subgraph NEW["EUPE — scale up, then scale down"]
        N1["Stage 1<br/>PEcore + PElang + DINOv3<br/>distilled into a 1.9B PROXY TEACHER"]
        N2["Stage 2<br/>proxy → efficient student<br/>at 256x256, ~390k iters"]
        N3["Stage 3<br/>multi-resolution finetune<br/>256 / 384 / 512, ~100k iters"]
        N1 --> N2 --> N3
    end

    OLD ==>|"the fix"| NEW
    NEW --> WHY["Learning from ONE universal teacher<br/>is far easier for a small model<br/>than satisfying three masters"]

    classDef o fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    classDef n fill:#dcfce7,stroke:#16a34a,color:#14532d
    class O1,O2,O3 o
    class N1,N2,N3,WHY n
```

**Reported ViT-B scale results (86M params):**

| Benchmark | EUPE-B | Comparison |
|---|---|---|
| IN1k-KNN | 84.1 | beats PEcore-B 79.7, SigLIP2-B 83.2, DINOv3-ViT-B 83.0 |
| ADE20k mIoU | 52.4 | beats DINOv3-ViT-B 51.8 — the dense-prediction specialist |
| RealworldQA | 55.5 | beats PEcore-B 52.9, SigLIP2-B 52.5 |
| VLM tasks | — | outperforms RADIOv2.5-B and DUNE-B across the board |

**Licence:** FAIR Research License — **research use only.** This is the decisive practical difference from C-RADIOv4.
**Repo:** https://github.com/facebookresearch/EUPE · paper https://arxiv.org/abs/2603.22387

### 3.3 The wider family

| Model | Origin | Distinguishing idea |
|---|---|---|
| **AM-RADIO** | NVIDIA, CVPR 2024 | Originated the paradigm; E-RADIO efficient architecture |
| **RADIOv2.5** | NVIDIA, CVPR 2025 | Multi-resolution training, mosaic augmentation, token compression |
| **PHI-S** | NVIDIA | Distribution balancing across teachers with different feature statistics |
| **FeatSharp** | NVIDIA | Sharpening student feature maps |
| **SAM-CLIP** | Apple | Merges SAM and CLIP toward semantic + spatial understanding |
| **UNIC** | Naver Labs Europe | Intermediate teacher-matching projectors and **dynamic teacher selection** |
| **DUNE** | Naver | Universal-encoder distillation; a standard baseline in EUPE's tables |
| **Theia** | Robot learning | Multi-teacher distillation for robot policies; distills **patch tokens only**, unlike AM-RADIO's CLS-token approach |
| **SAK** | — | Follow-up in the same line |
| **AMoE / SigLino** | — | **Mixture-of-Experts student** distilled from DINOv3 + SigLIP2; token-balanced batching with FlexAttention masks to stabilise multi-resolution training |
| **Eagle** | — | Mixture of *encoders* for multimodal LLMs — adjacent, not strictly agglomerative |

### 3.4 What these are NOT

Frequently confused, worth separating:

| Model | What it actually is |
|---|---|
| **SigLIP 2** (Google DeepMind, Feb 2025) | A *teacher*. Contrastive VL encoder with added captioning, self-distillation, and masked-prediction objectives. ViT-B/L/So400m/g. Self-distillation ≠ multi-teacher agglomeration. |
| **DINOv3** (Meta) | A *teacher*. Self-supervised, Axial RoPE, LVD-1689M. |
| **SAM3** | A *teacher*. Promptable segmentation. |
| **TIPS / TIPSv2** (Google) | Vision-language pretraining with strong patch-text alignment. A competitor/teacher, not an agglomerative student. |
| **Perception Encoder / PEcore / PElang / PEspatial** (Meta) | A teacher family; the specialised variants come from *self*-distillation of PEcore, not from merging distinct foundation models. Used as teachers by EUPE. |

> If you are trying to recall "the Google or Meta one": Meta's agglomerative entry is **EUPE**. Google does not currently ship an agglomerative student — it ships **teachers** (SigLIP 2, TIPS).

---

## 4. The recurring engineering problems

Every paper in this line ends up fighting the same four things:

| Problem | Symptom | Fixes attempted |
|---|---|---|
| **Resolution mode shift** | Student behaves differently above/below the training resolution; low-res collapses | Multi-resolution training (RADIOv2.5), stochastic resolution (C-RADIOv4), token-balanced native-resolution batching (AMoE) |
| **Teacher imbalance** | One teacher's loss scale dominates; its capabilities crowd out the others | PHI-S distribution balancing, balanced angular summary loss, dynamic teacher selection (UNIC) |
| **Artifact inheritance** | Student reproduces the teacher's border noise or window-boundary patterns | Shift-equivariant dense loss (C-RADIOv4), FeatSharp |
| **Capacity bottleneck** | Small students cannot absorb three feature spaces | Proxy teacher (EUPE), MoE student (AMoE) |
| **Token count** | Too many output tokens for practical VLM integration | Token compression (RADIOv2.5) |

---

## 5. Choosing one

```mermaid
flowchart TD
    Q{"What is the constraint?"}

    Q -->|"Commercial product"| A1["C-RADIOv4.<br/>NVIDIA Open Model License<br/>permits commercial use.<br/>EUPE's FAIR licence does not."]
    Q -->|"Edge / on-device,<br/>ViT-B or smaller"| A2["EUPE.<br/>Explicitly designed for the<br/>capacity-constrained regime,<br/>beats RADIOv2.5-B at that scale.<br/>Research use only."]
    Q -->|"Maximum quality,<br/>compute available"| A3["C-RADIOv4-H, 653M.<br/>Strongest teacher set."]
    Q -->|"Dense prediction is<br/>the whole job"| A4["Consider DINOv3 directly.<br/>Agglomeration buys breadth;<br/>if you only need one capability<br/>the specialist may still win."]
    Q -->|"Need language alignment<br/>at the output"| A5["Verify the summary/CLS head<br/>actually retains zero-shot<br/>capability at your resolution.<br/>Not all variants do equally."]
    Q -->|"Instance-level discrimination<br/>e.g. ReID, retrieval"| A6["UNMEASURED.<br/>No published benchmark.<br/>See foundation-model-reid section 6."]

    classDef box fill:#f1f5f9,stroke:#475569,color:#0f172a
    classDef warn fill:#fef9c3,stroke:#ca8a04,color:#713f12
    class A1,A2,A3,A4,A5 box
    class A6 warn
```

---

## 6. Evaluation blind spots

The benchmark suite this family reports is remarkably consistent — and remarkably narrow:

- ImageNet classification / KNN
- ADE20k semantic segmentation linear probing
- COCO detection
- Probe3D depth and surface normals
- VLM integration — LLaVA-class, TextVQA, GQA, POPE, RealworldQA
- SPair correspondence

**What is never measured:**

| Missing axis | Why it matters |
|---|---|
| **Instance-level discrimination** | Retrieval, ReID, individual identification. Category semantics ≠ instance identity. |
| **Fine-grained / long-tail retrieval** | The tail is where distillation loss is least constrained. |
| **Calibration and OOD rejection** | See [openood-v1.5](openood-kb.md): foundation-model feature geometry is not well served by ResNet-era scoring functions, and v1.5 flags this as open. Nobody reports ECE or AUROC for these backbones. |
| **Temporal consistency** | Tracking needs frame-to-frame embedding stability, not just per-frame quality. |
| **Small-crop behaviour** | Stochastic resolution training targets this, but it is validated on segmentation, not on 128×64 person crops. |

This is a genuine opportunity: the evaluation gap is wide and the models are public.

---

## 7. Licensing — read before you build

| Model | Licence | Commercial? |
|---|---|---|
| C-RADIOv4 (all sizes) | NVIDIA Open Model License Agreement | **Yes** |
| EUPE | FAIR Research License | **No** — research only |
| DINOv3 / SAM3 / SigLIP2 | Varies by model; check each card | Mixed |

Teacher licences do not automatically constrain the student, but they are worth checking if you plan to redistribute derived weights. For surveillance and biometric-identification products this sits alongside GDPR and EU AI Act obligations — treat it as a design input, not a legal afterthought.

---

## 8. Terms

Defined once, in **[glossary.md](../glossary.md)** — never here. Used on this page:

[Agglomerative model](../glossary.md#51-backbone-families) · [Multi-teacher distillation](../glossary.md#51-backbone-families) · [Label-free distillation](../glossary.md#51-backbone-families) · [Adaptor head](../glossary.md#51-backbone-families) ·
[Proxy teacher](../glossary.md#51-backbone-families) · [Resolution mode shift](../glossary.md#51-backbone-families) · [Shift equivariance](../glossary.md#51-backbone-families) · [ViTDet mode](../glossary.md#51-backbone-families) ·
[Token compression](../glossary.md#51-backbone-families) · [PHI-S](../glossary.md#51-backbone-families) · [Summary token](../glossary.md#51-backbone-families)

---

## 9. Sources

- AM-RADIO (CVPR 2024) — https://arxiv.org/abs/2312.06709
- RADIOv2.5 (CVPR 2025) — https://arxiv.org/abs/2412.07679
- RADIO repository incl. C-RADIOv4 tech report — https://github.com/NVlabs/RADIO
- C-RADIOv4 model cards — https://huggingface.co/nvidia/C-RADIOv4-H · https://huggingface.co/nvidia/C-RADIOv4-SO400M
- EUPE (Meta, Mar 2026) — https://arxiv.org/abs/2603.22387 · https://github.com/facebookresearch/EUPE
- SigLIP 2 (Google DeepMind) — https://arxiv.org/abs/2502.14786
- AMoE / agglomerative MoE — https://arxiv.org/abs/2512.20157
- Companion entries: [foundation-model-reid](foundation-model-reid-kb.md), [reid-in-mot](reid-in-mot-kb.md), [openood-v1.5](openood-kb.md)

---

## 10. Retrieval hints

Answers: *what is an agglomerative vision foundation model · what is C-RADIOv4 · what teachers does C-RADIOv4 use · AM-RADIO vs RADIOv2.5 vs C-RADIOv4 · what is EUPE · Meta agglomerative encoder · is SigLIP2 agglomerative · what is a proxy teacher · UNIC Theia SAM-CLIP DUNE · multi-teacher distillation problems · resolution mode shift · can I use C-RADIOv4 commercially · which agglomerative model for edge devices.*

**Single most quotable fact:** C-RADIOv4 distills SigLIP2-g-384, DINOv3-7B, and SAM3 into a single commercially-licensed encoder of 98M–653M parameters, while Meta's EUPE argues the opposite recipe for small students — scale *up* to a 1.9B proxy teacher first, then distill down, because a ViT-B cannot absorb three feature spaces at once.
