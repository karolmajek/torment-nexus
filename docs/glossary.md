---
title: "Glossary — one definition per term, for the whole wiki"
kb_id: reid-glossary
type: reference / single source of truth
domain: computer-vision, re-identification, multi-camera-tracking, open-set-recognition
tags: [glossary, terminology, definitions, reid, mtmc, metrics, open-set, calibration]
retrieved: 2026-08-22
confidence: high — definitions are stable; the per-method sections follow their source papers
supersedes: the twenty per-file glossary tables that previously lived across this wiki
related: [reid-2026-index, gallery-and-evaluation, reid-mot-metrics, open-world-rejection-calibration, openood-v1.5]
---

# Glossary

**This is the only glossary in the wiki.** Every other page links a term here instead of restating it, so a
definition can be changed in one place and nowhere else. If a term is missing, add it here — do not define it
inline on the page that needed it.

A glossary entry is one line. When a term needs a whole page to explain properly, the entry says which page
owns it: [gallery-and-evaluation-kb.md](field/gallery-and-evaluation-kb.md) owns retrieval scoring,
[reid-mot-metrics-kb.md](field/reid-mot-metrics-kb.md) owns tracking metrics,
[open-world-rejection-calibration-kb.md](field/open-world-rejection-calibration-kb.md) owns rejection and
calibration, [10-taxonomy-merged.md](field/10-taxonomy-merged.md) owns the setting axes.

> **Three things this file pins down.** **Distractor** (§2.1) and **retention** (§6) each had two or more
> non-equivalent wordings scattered across the wiki; one definition each now. **FPR@95** (§4.3) had two
> *conventions* — ID-positive and OOD-positive — which name the same operating point from opposite sides;
> the entry states the operating point itself, so neither page has to be rewritten to agree.

---

## 1. Task and setting

### 1.1 What is being asked

| Term | Definition |
|---|---|
| **ReID** | Re-identification — matching the same identity across non-overlapping camera views, or across time within one view |
| **Verification (1:1)** | Are these two observations the same identity? Pair classification, not retrieval |
| **Open-set identification (1:N + reject)** | Search a gallery where the probe may match nobody; requires an accept/reject decision *and* an identification |
| **Identity discovery / online enrolment** | Decide whether an observation is a new identity the system should remember; clustering with unknown *k* |
| **Person search** | Detection and ReID performed jointly on uncropped frames, with no ground-truth boxes given |
| **Closed-set ReID** | Every probe identity is guaranteed to exist in the gallery. What standard benchmarks actually score |
| **Open-set / open-world ReID** | The probe may belong to no gallery identity. "Open-world" carries three unrelated meanings in the literature — [open-world-rejection-calibration-kb.md §1.2](field/open-world-rejection-calibration-kb.md) disambiguates them |

### 1.2 Named settings

| Term | Definition |
|---|---|
| **MTMC / MCMT** | Multi-target multi-camera tracking / multi-camera multi-target — the same thing under two naming conventions; global identities across a camera network |
| **DA-ReID** | Domain-adaptive ReID; unlabelled target data available at training time |
| **DG-ReID** | Domain-generalizable ReID; *no* target data at training time |
| **UDA** | Unsupervised domain adaptation — labelled source plus unlabelled target |
| **USL** | Fully unsupervised learning; target data only, pseudo-labels from clustering |
| **VI-ReID** | Visible–infrared ReID; a cross-modality problem |
| **CC-ReID** | Cloth-changing ReID |
| **LReID** | Lifelong ReID; sequential domains without catastrophic forgetting |
| **TBPS** | Text-based person search / text-to-image person retrieval |
| **OM-ReID** | Omni multi-modal ReID; arbitrary combinations of query modalities |
| **OmniReID** | Instruct-ReID's multi-setting ReID benchmark — a benchmark name, not the setting above |
| **Sim2Real** | Train on synthetic data, evaluate on real data |
| **Zero-shot ReID** | Using a pretrained encoder's features directly for retrieval, with no ReID training |

---

## 2. Retrieval evaluation

Full treatment, with a worked VeRi query: [gallery-and-evaluation-kb.md](field/gallery-and-evaluation-kb.md).

### 2.1 Gallery anatomy

| Term | Definition |
|---|---|
| **Query / probe** | The image or tracklet you search with |
| **Gallery** | The set being searched and ranked; fixed in benchmarks, growing in deployment |
| **Ground truth / positives / hit** | Gallery entries carrying the query's identity that count towards the score — in most protocols, those from a *different* camera |
| **Junk** | Gallery entries excluded from scoring, earning neither reward nor penalty; in most protocols, the same identity seen by the same camera |
| **Distractor** | A gallery entry whose identity appears in no query. It can only ever be a wrong match — it raises realism and lowers scores |
| **Single-shot / multi-shot gallery** | One image per gallery identity vs. many |
| **Single-query / multi-query** | One probe image vs. a pooled set of probe images per query identity |
| **Tracklet-level evaluation** | Aggregating the frames of one track into a single query or gallery entry, e.g. via VeRi's `test_track.txt` |
| **Re-indexing** | Recomputing every stored gallery embedding after a model change |

### 2.2 Retrieval metrics

| Term | Definition |
|---|---|
| **AP** | Average precision for one query, from its precision–recall curve over the ranked gallery |
| **mAP** | Mean of AP over queries. The primary ReID number |
| **CMC** | Cumulative Matching Characteristic curve; Rank-*k* is a point on it |
| **Rank-*k*** | Fraction of queries where a correct match appears in the top *k*. Rank-1 is the headline number but ignores every other correct match |
| **mINP** | Mean Inverse Negative Penalty — the cost of retrieving the *hardest* correct match; surfaces the tail |
| **Re-ranking** | Query-adaptive post-hoc refinement of a ranked list using gallery–gallery similarity. Adds 5–10 mAP and destroys score comparability across queries; must be disclosed |
| **k-reciprocal encoding** | The standard re-ranking method — re-scoring by mutual nearest-neighbour relations between query and gallery |
| **Operating point** | The similarity threshold at which a deployed system accepts a match |

### 2.3 Protocol vocabulary

| Term | Definition |
|---|---|
| **Identity-disjoint split** | Test identities never appear in training. Mandatory for a valid ReID protocol |
| **Detected vs. labelled boxes** | Auto-detector output vs. hand-drawn boxes. Detected is harder and more realistic, and changes CUHK03 scores meaningfully |
| **Cross-dataset / direct transfer** | Train on dataset A, test on B with no fine-tuning |
| **Leave-one-dataset-out** | DG protocol: train on every source dataset but one, test on the held-out one |
| **Cloth-changing protocol** | Gallery entries wearing the same outfit as the query are excluded from scoring |

---

## 3. Tracking and multi-camera systems

Full treatment: [reid-mot-metrics-kb.md](field/reid-mot-metrics-kb.md) for the metrics,
[reid-in-mot-kb.md](field/reid-in-mot-kb.md) for ReID inside a tracker,
[40-city-scale-mtmc.md](field/40-city-scale-mtmc.md) for city-scale pipelines.

### 3.1 Pipeline pieces

| Term | Definition |
|---|---|
| **Tracklet** | A short, contiguous, single-camera, single-identity trajectory fragment, produced before global ID assignment. The atomic unit of video ReID and MTMC |
| **SCT** | Single-camera tracking; produces tracklets within one view |
| **ICA** | Inter-camera association; clusters tracklets into global identities |
| **GTA** | Global Tracklet Association — offline clustering of tracklets into identities |
| **SDE** | Separate Detection and Embedding — detector and ReID model are distinct networks |
| **JDE** | Joint Detection and Embedding — one backbone with a detection head and a ReID head |
| **Gating** | Hard rejection of implausible pairs before the assignment solver runs |
| **Camera-link model** | A learned or annotated model of which camera pairs connect, and the transit-time distribution between them |
| **BEV** | Bird's-eye view; a shared ground-plane coordinate system for multi-view fusion |
| **Online tracker** | Uses only past frames at inference. Awarded a 10% HOTA bonus in AI City |
| **Public / private detections** | Benchmark-supplied vs. self-generated detections. Comparing across the two is not a valid comparison |

### 3.2 Tracking metrics

| Term | Definition |
|---|---|
| **HOTA** | Higher Order Tracking Accuracy; √(DetA·AssA), averaged over localisation thresholds α. The default ranking key |
| **DetA / AssA / LocA** | HOTA's detection / association / localisation sub-scores. Report these, not just the composite |
| **IDF1** | Identity F1 after a global bipartite matching between ground-truth and predicted trajectories. Primary key for most MTMC leaderboards |
| **IDTP / IDFP / IDFN** | Identity-consistent true positives / false positives / false negatives |
| **MOTA / MOTP** | CLEAR MOT accuracy `1 − (FN + FP + IDSW)/GT` and mean localisation precision. MOTA is dominated by detector errors and is not comparable across datasets |
| **IDSW** | Identity switch — a raw count, not normalised, so meaningless in isolation |
| **sw/TP** | Identity switches per true positive; a rate-normalised IDSW that stays comparable when trackers emit different detection counts |
| **MT / ML / Frag** | Mostly Tracked / Mostly Lost (% of GT trajectories covered >80% / <20%) and trajectory fragmentation count |
| **TrackEval** | The community-standard implementation of these metrics. Use it rather than reimplementing |

### 3.3 Clustering metrics for identity discovery

| Term | Definition |
|---|---|
| **ARI** | Adjusted Rand Index — chance-corrected pairwise clustering agreement; penalises over-splitting and over-merging alike. The scoring metric for AnimalCLEF 2026 |
| **NMI** | Normalised mutual information; information-theoretic, more forgiving of over-splitting than ARI |
| **Purity / BCubed** | Interpretable cluster-quality measures, easy to game with many small clusters |
| **OWTA** | Open-world tracking accuracy — unknown-detection recall combined with association accuracy |

### 3.4 Simulation and challenge infrastructure

| Term | Definition |
|---|---|
| **AMR** | Autonomous mobile robot; a tracked class in the warehouse benchmarks |
| **Omniverse / Isaac Sim** | NVIDIA simulation stack used to generate the synthetic training corpora |
| **Cosmos Transfer** | Generative model used in the AI City 2026 data pipeline to diversify synthetic renders |

---

## 4. Open-set, rejection and calibration

Full treatment: [open-world-rejection-calibration-kb.md](field/open-world-rejection-calibration-kb.md); the OOD
benchmark discipline is in [openood-kb.md](field/openood-kb.md).

### 4.1 Distribution vocabulary

| Term | Definition |
|---|---|
| **ID** | In-distribution — a label in the model's known set, with no covariate shift. In ReID: a probe whose identity is enrolled |
| **OOD** | Out-of-distribution — semantically novel. In ReID: an unenrolled identity |
| **csID** | Covariate-shifted in-distribution — a *known* identity under corruption, restyling, a new camera, new lighting or new clothing. **Must be accepted, not rejected.** ReID has no native name for this, which is exactly why domain shift and unknown identity get confused in practice |
| **Near-OOD / hard-OOD** | Semantically close to ID — an unenrolled person at the same site with similar appearance. The hard case |
| **Far-OOD / easy-OOD** | Semantically distant — a different site, or a non-person crop. Largely solved at scale |
| **Full-spectrum detection** | Scoring OOD generalization (accept csID) and OOD detection (reject OOD) jointly |
| **OSR** | Open-set recognition — a parallel literature pursuing the same goal as OOD detection |
| **Openness** | Scheirer's formalisation of how open a problem is, from the ratio of training to test classes |

### 4.2 Rejection mechanisms

| Term | Definition |
|---|---|
| **OOD score** | A scalar `s(x)`, thresholded to give a binary ID/OOD decision |
| **Post-hoc method** | An inference-time scoring function requiring no retraining. OpenOOD calls its implementations **postprocessors** |
| **Abstain class** | An explicit "none of the above" output — a virtual K+1 class; parameter-free in HALO's construction, where it is pinned to the origin |
| **Ratio test** | Reject using the ratio or margin between the best and second-best match. From SIFT; applies directly to gallery scores and is almost never reported in ReID |
| **Outlier Exposure (OE)** | Training against auxiliary outlier data to sharpen the ID/OOD boundary |
| **Selective prediction / risk–coverage** | Framework in which the model may abstain; risk is plotted against the fraction of inputs answered |
| **Conformal prediction** | Distribution-free construction of prediction sets with a coverage guarantee under exchangeability |
| **Cohort / AS-norm** | Score normalisation against an impostor cohort, making scores comparable across probes |

### 4.3 Operating-point and calibration metrics

| Term | Definition |
|---|---|
| **AUROC / AUPR** | Threshold-free ranking quality of the accept/reject score |
| **FPR@95** | The false-alarm rate on OOD inputs once the threshold is set to admit 95% of ID inputs. Lower is better. Written *FPR at 95% TPR* where ID is the positive class ([halo-loss-kb.md](field/halo-loss-kb.md), [70-open-problems-2026.md](field/70-open-problems-2026.md)) and *FPR at 95% TNR* where OOD is ([openood-kb.md](field/openood-kb.md)) — same operating point, opposite sign conventions. Check which one a table means before comparing numbers |
| **FMR** | False match rate per comparison. Face vendors quote it at 1e-6; ReID papers quote nothing |
| **FPIR** | False positive identification rate — fraction of non-mated searches returning any candidate above threshold. Accumulates over gallery size: `FPIR(N) ≈ N · FMR` |
| **FNIR** | False negative identification rate — fraction of mated searches where the true mate falls below threshold or outside rank R |
| **DIR@FAR** | Detection and identification rate at a given false accept rate (Liao 2014) |
| **TTR / FTR** | True / false target recognition rate (Zheng 2016) — the watchlist framing of the same pair |
| **EER** | Equal error rate; the DET-curve point where the two error rates coincide |
| **minDCF** | Minimum detection cost function — a cost-weighted operating point with an explicit target prior |
| **Cllr / minCllr** | Log-likelihood-ratio cost, and its value after ideal recalibration. The difference is the miscalibration loss |
| **ECE** | Expected Calibration Error — the binned gap between stated confidence and actual accuracy. Lower is better |
| **BAKS / BAUS** | Balanced accuracy on known / unknown (new) individuals; AnimalCLEF ranks by their geometric mean |

### 4.4 Population and benchmark terms

| Term | Definition |
|---|---|
| **Mated / non-mated probe** | A probe whose identity is / is not enrolled in the gallery (biometrics terminology) |
| **Biometric menagerie** | Doddington's per-subject difficulty taxonomy: sheep, goats, lambs, wolves |
| **SSB-hard / NINCO** | Curated hard near-OOD sets for ImageNet; NINCO was built to remove label noise present in older OOD sets |

---

## 5. Representations and backbones

### 5.1 Backbone families

| Term | Definition |
|---|---|
| **Foundation model** | A large pretrained model producing broadly reusable representations |
| **Agglomerative model** | A student distilled from multiple heterogeneous foundation teachers (RADIO, EUPE, DUNE) |
| **Multi-teacher distillation** | Training one student to match several teachers' features simultaneously |
| **Label-free distillation** | Matching teacher features rather than ground-truth labels; no annotation needed |
| **Adaptor head** | A per-teacher projection letting the student emulate that teacher's output space |
| **Proxy teacher** | EUPE's intermediate high-capacity model, which unifies knowledge before compression |
| **PHI-S** | Distribution-balancing method for normalising heterogeneous teacher feature statistics |
| **Summary token** | The global / CLS-style output, as distinct from dense patch tokens |
| **Token compression** | Reducing output token count for practical VLM integration |
| **Resolution mode shift** | Degradation when inference resolution differs from training resolution |
| **Shift equivariance** | Translating the input translates the features predictably; used to suppress fixed-pattern artifacts |
| **ViTDet mode** | Windowed-attention inference, for cheaper high-resolution processing |
| **MegaDescriptor / MiewID** | The standard pretrained wildlife individual-ReID encoders |

### 5.2 Probing a frozen backbone

| Term | Definition |
|---|---|
| **Linear probing** | Freeze the backbone, train only a linear head — isolates what the representation already encodes |
| **Attention probing** | Probe with *C* learnable queries cross-attending the feature map; used when a representation lacks cross-image semantic alignment |
| **Instance discrimination** | Separating individual instances rather than categories — what ReID actually needs |

### 5.3 Structure inside the embedding

| Term | Definition |
|---|---|
| **Disentangled representation** | Distinct, ideally independent factors of variation (colour, shape, pose, identity) encoded in separable parts of the vector |
| **Concept subspace / concept block** | A named or emergent slice of an embedding corresponding to one semantic factor |
| **Slot attention** | Input tokens compete, via softmax over a small set of learned query slots, to be assigned to one of *K* slots which then aggregate them. The mechanism behind DiCo's part-level slots |
| **Prototype dictionary** | A shared learned set of vectors that a concept block projects onto via attention, grounding the same concept index across modalities without ever labelling what that concept is |
| **Appearance code / structure code** | DG-Net / IS-GAN's two-way split: identity-related (appearance) vs. identity-unrelated (structure, pose, background) features |
| **Concept whitening** | A layer replacement that decorrelates a latent space and rotates its axes onto pre-chosen concepts, using small probe example sets |
| **Concept Activation Vector (CAV)** | The normal to the linear boundary separating a frozen model's activations on concept-positive vs. concept-negative examples. A purely post-hoc probing tool |
| **Concept Bottleneck Model** | The ML lineage (Koh et al., ICML 2020) forcing prediction through a layer of named, human-interpretable concept neurons, enabling test-time human correction of a wrong concept |
| **Soft biometric** | A non-identifying attribute (gender, clothing, accessories) used as an auxiliary label |

### 5.4 Architecture components

| Term | Definition |
|---|---|
| **BNNeck** | A batch-norm layer between the feature used for triplet loss and the feature used for ID loss, letting each operate in its preferred space |
| **Side information embedding (SIE)** | Learnable tokens encoding camera or viewpoint identity, added to the transformer input (TransReID) |
| **IBN** | Instance-Batch Normalization; a fixed channel split between IN and BN |
| **MoE** | Mixture of Experts; specialised subnetworks plus a gating or voting mechanism |

---

## 6. Training, adaptation and transfer

| Term | Definition |
|---|---|
| **PEFT** | Parameter-efficient fine-tuning — LoRA, adapters or prompt tuning instead of updating all weights |
| **Prompt learning** | Learning continuous text tokens rather than writing prompts; CLIP-ReID's core mechanism |
| **Pseudo-caption** | Automatically generated text for an uncaptioned image corpus, enabling vision-language pretraining |
| **Human-centric pretraining** | Pretraining specifically on person imagery, to close the ImageNet-to-person domain gap |
| **Domain gap** | The distribution distance between training and deployment data that costs accuracy at transfer time |
| **Fine-tuning distortion** | Degradation of pretrained features under full fine-tuning, harming OOD performance |
| **Layer-wise LR decay** | Lower learning rates for earlier layers; the standard mitigation for fine-tuning distortion |
| **Catastrophic forgetting** | Loss of previously acquired capability when training on new data |
| **Retention** | Target-domain score as a fraction of source-domain score; the honest measure of transfer. Previously written both *performance retention* and *retention ratio* — one quantity, one name |
| **Re-indexing-free** | A continual-learning property whereby an updated model stays compatible with the existing embedding index, so no re-indexing (§2.1) is needed |
| **Pseudo-label clustering** | Assigning identity labels by clustering unlabelled target embeddings, then training on them |
| **Non-trivial sampling** | Selecting training examples that are informative rather than redundant (ReID-R) |
| **Training-as-a-Service** | Infrastructure pattern where models train against data that never leaves the provider's platform |

---

## 7. Imaging conditions

| Term | Definition |
|---|---|
| **Ground sampling distance** | Real-world size represented by one pixel; the limiting quantity in aerial ReID |
| **Nadir view** | Straight-down camera angle (90° pitch); the hardest aerial viewpoint |
| **Amodal box** | Full extent of an object including its occluded part, as opposed to the visible extent |
| **Apparent motion** | Motion observable in the image plane, i.e. optical flow; distinct from true 3-D scene motion |

---

## 8. Method-specific terms

These belong to one paper or one system. They live here anyway, so that there is one place to look up any
term used in this wiki.

### 8.1 Matryoshka Representation Learning (MRL)

Owning page: [mrl-kb.md](field/mrl-kb.md).


| Term | Definition |
|---|---|
| **`M`** | The nesting set — the dimensionalities explicitly optimized. `\|M\| ≤ ⌊log d⌋` |
| **`c_m`** | Relative importance weight for nesting size `m`; set to 1 for all `m` in the paper |
| **MRL–E** | Efficient MRL. Classifier heads are column slices of one shared `W`; roughly half the classifier parameters |
| **MRL–AC** | Adaptive Classification. A confidence-thresholded cascade over prefixes of a single vector |
| **MRL–AR** | Adaptive Retrieval. Shortlist at `D_s`, rerank at `D_r` |
| **`D_s` / `D_r`** | Shortlist dimensionality / rerank dimensionality |
| **Funnel retrieval** | Multi-stage AR that grows dimensionality while shrinking the shortlist, removing the `D_s`/`D_r` choice |
| **FF** | Fixed Feature — the baseline of independently trained low-dimensional models |
| **Interpolation property** | Accuracy at dimensions *not* in `M` lies smoothly between neighbouring optimized sizes |
| **ImageNet-4K** | Retrieval benchmark introduced by the MRL paper: ~4.2M database images, ~200K queries, 4202 classes |
| **Matryoshka-Adaptor** | Post-hoc transform giving nesting properties to frozen or black-box embeddings |
| **Quality-adaptive nesting** | This wiki's name for the DAME-style idea of allocating dimensions by per-sample information content |

### 8.2 HALO

Owning page: [halo-loss-kb.md](field/halo-loss-kb.md).


| Term | Definition |
|---|---|
| **Attention sink** | A dummy token absorbing surplus attention mass in Transformers; conceptual ancestor of the abstain class |
| **Register token** | An explicitly added dummy token providing an attention dump when magnitude-based sinks are suppressed |
| **Magnitude bullying** | Winning the softmax competition by inflating vector norms rather than improving alignment |
| **Radial explosion** | The optimizer pushing features infinitely far from the origin to saturate softmax |
| **Shift-invariance** | The property of softmax whereby adding a constant to every logit in a row leaves probabilities unchanged |
| **Soap bubble** | Metaphor for a high-dimensional Gaussian, whose mass concentrates on a thin outer shell |
| **RBF** | Radial Basis Function kernel; similarity as a function of distance |
| **TFSD** | Teacher-Free Self-Distillation; soft targets built from the model's own negative-class distances |

### 8.3 FlowFeat

Owning page: [flowfeat-kb.md](field/flowfeat-kb.md).


| Term | Definition |
|---|---|
| **Motion profile** | The distribution of plausible velocities at a pixel (Shi & Malik, 1998). The thing FlowFeat embeds |
| **Motion stochasticity** | One image is compatible with many future motions — the obstacle that kills naïve flow regression |
| **A\*** | The per-sample optimal linear (in code: affine) operator mapping features to flow; solved in closed form by ridge regression on the EMA teacher's features, never learned |
| **Ridge parameter γ** | L2 penalty on A\*; γ = 1.0. The most load-bearing hyperparameter (−7.6 J&F when weakened) |
| **Focal gradient matching** | Second-order loss weighted by `1 − e^{−∇u/σ}`, so it acts only at motion discontinuities. Source of boundary sharpness |
| **Mean teacher / EMA** | The teacher decoder is an exponential moving average of the student decoder (Tarvainen & Valpola, 2017) |
| **DPT** | Dense Prediction Transformer decoder (Ranftl et al.); reads 4 intermediate ViT blocks via hooks and fuses them to full resolution. FlowFeat's only trainable module |
| **FlowFeat++** | Post-hoc PAMR mask refinement driven by FlowFeat affinities instead of RGB intensities. No training |
| **Linear probing (VOS)** | Fit a linear classifier on frame 1's ground-truth mask, apply it unchanged to the rest of the video. Non-autoregressive, effectively few-shot |
| **Local KNN** | Caron-style label propagation for VOS; autoregressive and known to be hyperparameter-brittle |
| **J&F** | DAVIS metric: mean of region similarity J_m (IoU) and contour accuracy F_m |
| **FeatUp / LoftUp** | Prior and concurrent feature upsamplers — bilateral-filter-based and coordinate-based (SAM-supervised). FlowFeat's headline baselines |
| **SEA-RAFT / RAFT / SMURF** | Optical flow networks used as the frozen teacher; SMURF is itself unsupervised, enabling a fully label-free pipeline |

### 8.4 SOMA

Owning page: [soma-kb.md](field/soma-kb.md).


| Term | Definition |
|---|---|
| **SOMA / SOMA-R** | The tracker without / with a crop ReID embedder |
| **Wholebody detector** | Detector emitting body box plus parts, keypoints, head orientation and attributes in one pass |
| **Assembly** | Grouping raw part detections into per-person groups via bone joining |
| **Anatomical token** | Per-person structured record consumed by the tracker, including a synthesised amodal box |
| **Ghost coasting** | Keeping an unmatched track alive without detections, past normal motion-prediction validity |
| **Embedding-only revival** | Re-attaching a ghost purely on appearance similarity, with no geometric support |
| **Long-gap recovery bin** | Fraction of occlusion episodes of a given duration after which the original identity is restored |
| **Fairness pairing** | Feeding every ReID-enabled row of a table the identical cached features and identical detections, so a row-to-row difference is attributable to the tracker alone |
| **Per-frame whitening** | Normalising embeddings using statistics over the people visible in the current frame (OSNet path; web runtime requires ≥4 valid embeddings). Transductive — it has no single-crop retrieval equivalent |
| **token-IN** | Token-level instance normalisation, used in the PersonViT variant |
| **CrowdTrack** | Crowded-scene MOT benchmark with roughly 19× more 5-second occlusion episodes than MOT17 |

---

## 9. Sources

Definitions follow the pages that own each area — [gallery-and-evaluation-kb.md](field/gallery-and-evaluation-kb.md),
[reid-mot-metrics-kb.md](field/reid-mot-metrics-kb.md),
[open-world-rejection-calibration-kb.md](field/open-world-rejection-calibration-kb.md),
[openood-kb.md](field/openood-kb.md), [10-taxonomy-merged.md](field/10-taxonomy-merged.md) — and the per-method pages
cited in §8. Those pages carry the primary citations. This file carries no numbers, so nothing in it can
disagree with a dataset page or a results table.

---

## 10. Retrieval hints

Answers: *what does this term mean · what is csID · MTMC vs MCMT · junk vs distractor · is FPR@95 at 95% TPR
or TNR · what is mINP · what is FPIR · what does BNNeck do · what is a tracklet · what is retention ratio ·
what is an abstain class · what is a summary token.*

**Single most quotable fact:** the wiki has exactly one glossary, because a term defined twice is a bug — the
two copies drift, as *distractor* and *retention* both had before this file existed.
