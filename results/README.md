# Results

Every (encoder, head, dataset, protocol) combination this project has actually run.
[`table.md`](table.md) is the way in: a status block — how much of the matrix is measured,
per encoder and per head, what the encoding cost, and what is missing or cannot run — then an
index of the datasets, then the licences. That first half is counted from the matrix rather
than from the rows, because a combination nobody ran is not a row in a results table — it is
the absence of one, and an absence is invisible in a thousand lines of numbers.

The numbers themselves live one file per dataset in [`tables/`](tables): every protocol over
that dataset, every head, and the figures. All of it is generated — edit the inputs, not the
tables. The report is split because it stopped being readable at three thousand lines: the
question anyone has is about one dataset, and now so is the file, and so is the diff when that
dataset is re-run.

A **head** is a small map trained on the frozen encoder's features and nothing else — no
gradient reaches the backbone, ever. `none` is a value of that axis rather than the absence
of one: it is the frozen encoder scored directly, and it is the row every other row in its
section is read against.

```bash
python results/run.py plan       # what would run, and why the rest would not
python results/run.py all        # run everything missing, then rewrite the table
python results/run.py table      # rewrite the table from the runs already on disk
```

Needs `reidbench` importable and, for `all`, the `encoders` extra plus a torch you installed
yourself. `run.py` falls back to the sibling `reidbench/src` checkout if the package is not
installed, so a fresh clone reproduces without an install step.

## Where each fact lives

Nothing is listed twice. `run.py` holds no dataset knowledge, no model knowledge and no
probe knowledge.

```mermaid
flowchart LR
    E["results/encoders/*.json<br/><i>an encoder spec</i>"]
    P["results/probes/*.json<br/><i>a head spec · names its train split</i>"]
    D["datasets/*.md<br/><i>```toml: adapter · dir · protocols</i>"]
    R["run.py<br/><i>the cross product</i>"]
    V["reidbench CLI<br/><i>manifest · encode · score · measure</i>"]
    PR["probe.py<br/><i>fit · apply</i>"]
    F["a feature store<br/><i>content-addressed</i>"]
    RUN["results/runs/…/results.json<br/><i>one run record</i>"]
    G["results/figures.json<br/><i>which figures, and what each asks</i>"]
    T["table.md<br/><i>summary · index · licences</i>"]
    TS["tables/&lt;dataset&gt;.md<br/><i>the numbers, one page each</i>"]

    E --> R
    P --> R
    D --> R
    R --> V
    R --> PR
    V -->|encode| F
    F -->|fit · apply| PR
    PR -->|another store| F
    F -->|score · measure| RUN
    RUN -->|reidbench render| T
    RUN -->|--pages| TS
    T -->|links| TS
    R -->|the summary block| T
    G --> TS
```

- **Add a model** — drop a JSON spec in `encoders/`. That same file is what
  `reidbench encode --encoder` consumes, so the spec is never transcribed.
- **Add a head** — drop a JSON spec in [`probes/`](probes). It names its own `train`
  dataset and split, so the matrix gains a row per encoder without `run.py` learning what a
  probe is. That same file is what `probe.py fit --spec` consumes.
- **Add a dataset** — a page in [`datasets/`](../datasets) whose ` ```toml ` block names a
  non-empty `adapter` and at least one `protocol`, and a directory on disk. Same block
  [`datasets/get.py`](../datasets/get.py) reads.
- **Change the figures** — [`figures.json`](figures.json). A view is a sort order and a
  colour over the rows that are already there: *does resolution matter, holding encoder and
  head fixed?* is sorting by encoder, head, resolution and colouring by resolution, and then
  each block of three bars is one controlled comparison. Delete a view to stop drawing it.
  Nothing is re-measured either way.
- **A row's provenance** — every `results.json` carries its own: protocol digest, manifest
  content digest, encoder spec, cache key, library versions, GPU and driver, and the git sha
  with a `dirty` flag. Nothing about a row lives only in this directory.

`plan` prints a reason for every combination that does *not* run, so the gap between what is
supported and what has been measured stays visible instead of being an empty table cell. The
same reasons head `table.md` under **Not measured**, so a reader who never runs `plan` still
sees them.

## What these numbers do not claim

The table is **seven frozen general-purpose checkpoints, none of them trained on
re-identification** — two agglomerative students, their two teacher families at two scales
each, and CLIP — over fourteen encoder-resolution specs, each scored directly and through six
heads fitted on two training splits. Two of those specs are the same CLIP weights at the same
size under two preprocessing geometries, which is why `resize` is a column, and two
(`tipsv2-448`, `siglip2-384`) have specs but no runs, which is the whole of the matrix's
140-cell gap. Live counts are the summary block of [`table.md`](table.md), which is generated;
nothing below restates them. It validates the pipeline end to end, ranks encoders within a
dataset, and answers the teacher ablation in
[92-protocol-agglomerative-probe.md](../docs/project/92-protocol-agglomerative-probe.md) §14:

- **no backbone here was trained for ReID, and none was trained at all.** CLIP ViT-B/16
  learned from image-text pairs; C-RADIOv4 distils SigLIP2-g-384, DINOv3-7B and SAM3 into one
  backbone. Every `head` row is a 512-d affine map fitted on frozen features in under a
  minute; no gradient has ever reached a backbone in this directory;
- **`head: none` rows are zero-shot; every other row is not, and *where* it was fitted is
  half the number.** The three recipes — `pca`, `linear`, `arcface` — are each fitted twice,
  on `market1501/train` (12,936 images, 751 identities, disjoint from the 750 test identities)
  and on `msmt17/train`, giving the six `*` and `*-msmt17` head stems. A row is a **supervised
  in-domain** number on the dataset its head was fitted on and **cross-domain transfer**
  everywhere else, with no target-domain label ever seen. Two different claims, one column
  apart, which is why the column exists — and the swap is worth ±0.27 mAP for ArcFace against
  ±0.006 for PCA, measured both directions in
  [94-head-fit-domain-and-decision-metrics.md](../docs/project/94-head-fit-domain-and-decision-metrics.md);
- **the rows are not comparable across protocols either, which is why the table nests.**
  `tables/<dataset>.md` is a section per protocol: the `#` column, the emphasised best value
  and the figures are all per protocol. CCVID ships two —
  `ccvid/tracklet@1` and `ccvid/tracklet-cloth-changing@1`, which differ by one exclusion —
  and the same identity is easier to find when nobody changed clothes, so a single table over
  both would bold a cloth-changing row's easier twin and call it the better system;
- **the rows are not comparable across datasets, and `render` says so on every run.**
  Occluded-REID searches roughly a thousand whole-body images; Market searches 15,913; VRAI
  searches 32,338. A gallery sixteen or thirty times larger is most of the gap between 0.52 R1
  and 0.18 or 0.22, before any question of difficulty;
- Occluded-REID ships **no standard split** — the whole set is used, occluded probes against
  whole-body gallery, per `occluded-reid/occluded-vs-whole@1` — and it labels **no cameras**,
  so the same-camera junk rule that every Market number depends on does not exist there;
- **VRAI's rows are over its *training* split, and cannot be otherwise.** The release withholds
  the test identities and scores them on EvalAI, so `vrai/train-cross-camera@1` queries the
  first frame of each camera-1 trajectory against every camera-2 training image. That is a
  legitimate zero-shot number for an encoder that never saw VRAI and a meaningless one for
  anything fine-tuned on it — **including the head rows, which are safe here for exactly one
  reason: no head in this directory has seen a VRAI image.** A head fitted on VRAI could not
  be reported on this protocol at all. It is also aerial: 0.2152 R1 against Market's 0.1838 is
  a viewpoint difference as much as a gallery-size one, and neither belongs in a sentence with
  the other without saying so;
- **only the CLIP row's licence is unverified**, and `reidbench check` says so on every run:
  timm's code is Apache-2.0, its weights are not. Both C-RADIOv4 checkpoints carry a verified
  NVIDIA Open Model License, which is why the licence column under the metrics is not uniform;
- **`items_per_second` in a run record measures a machine, not a model.** The
  market1501 x C-RADIOv4-H@224 cell first recorded 2.2 img/s against 12.8 for the same encoder
  on VRAI, because another process held ~3.5 GB of the 8 GB card while it ran; re-extracting
  on a quiet card gave 12.3. The metrics never moved — same weights, same arithmetic, same
  cache key — which is exactly why a throughput figure needs its own scepticism.

## What they do show

Within one dataset every row shares a protocol digest and a manifest digest, so the encoder
comparison is the one thing here that is sound:

- **an agglomerative backbone is worth 1.5x to 5.6x CLIP's mAP, frozen.** Market 0.063 vs
  0.029, Occluded-REID 0.456 vs 0.312, VRAI 0.174 vs 0.031 — no ReID training on either side.
  Read against the *squashed* CLIP row: the centre-cropped one it used to be read against was
  seeing 45% of each person, and the old "2.5x to 7x" was partly measuring that;
- **H and SO400M are one choice on people and two on vehicles.** Market 0.061 vs 0.063 and
  Occluded-REID 0.456 vs 0.444 are ties; VRAI is 0.174 vs 0.149, H ahead by 17% relative for
  1.6x the compute. Aerial vehicles are where the extra 222M parameters land;
- **input size matters, and aspect ratio does not explain where.** On 64x128 person crops,
  224x224 and 256x128 are within noise frozen (0.0610 vs 0.0592, 0.4560 vs 0.4466) while 2:1
  runs 1.6x faster, so 2:1 is the better trade; on VRAI the same change costs 21% relative
  (0.1739 -> 0.1376). The tempting reading — that 2:1 wins because it matches a person crop's
  shape — is **false**, and this table contains its own counterexample. Market and
  Occluded-REID both ship images that are *every one of them* exactly 64x128, identical median
  size and identical 2.00 aspect, and with an ArcFace head they prefer opposite input sizes:
  256x128 on Market (0.7181 vs 0.7087) and 224x224 on Occluded-REID (0.6459 vs 0.6220, about
  five times that set's seed noise). CUHK03, at a much taller 2.97, prefers 2:1 by *more* than
  Market does (+6.8% vs +1.3%), not less. Two mechanisms were tested against these four
  datasets — aspect match and token count — and both fail; what the rows support is the plain
  regularity that **2:1 usually wins on person crops and loses on vehicles**, with no mechanism
  established;
- **`native` loses on every person dataset and wins only on vehicles**, and on two of the
  four it is not even native: Market and Occluded-REID have a coefficient of variation of
  **0.00** in image area — every file is exactly 64x128 — so "native" there is a fixed 32-token
  resolution wearing a misleading label. With an ArcFace head it costs 22% on Market, 29% on
  Occluded-REID and 27% on CUHK03, and gains 7% on VRAI. Note that CUHK03 gives it ~102 tokens
  against Market's 32 and it still loses by more, so token starvation does not account for it
  either; nor does image heterogeneity, since VRAI is by far the most heterogeneous set (CoV
  1.13) and is the only one where native wins. Feeding each image at its own size, snapped to
  the model's grid and capped at 512:

  | | Market | Occluded-REID | VRAI |
  |---|---|---|---|
  | H, 224x224 -> native | 0.0610 -> 0.0443 | 0.4560 -> 0.3385 | 0.1739 -> **0.1936** |
  | SO400M, 224x224 -> native | 0.0628 -> 0.0472 | 0.4436 -> 0.3404 | 0.1489 -> **0.1603** |

  Native for a person crop *is* 64x128 — 32 tokens, below the ~128px floor C-RADIOv4 was
  trained across — and costs about a quarter of the mAP while running 4.3x faster (53.9 vs
  12.3 img/s). Native for a VRAI crop is a median 295x202, inside that range, and gains 11%
  for 2.6x the cost. The variable that moved is resolution, not resampling: upsampling a
  small crop to 224 is not a distortion to be avoided, it is how the crop reaches a size the
  encoder was trained to read.

The gallery-size effect that the second bullet has to hand-wave is exactly what
[market1501-500k](../datasets/market1501-500k.md) exists to measure directly: same queries,
same model, same rules, a gallery 27x larger. **It ran on 2026-09-08**, and the effect is
large and not uniform: against its own plain-Market row, an encoder retains **0.53 to 0.84**
of its mAP, and retention rises with how supervised the head is — 0.53-0.70 at `head = none`
or `pca`, 0.59-0.84 with ArcFace. So a stronger head buys two things a single-gallery
benchmark cannot separate: a higher score, and a slower decay as the gallery grows. Numbers
per cell in [`tables/market1501-500k.md`](tables/market1501-500k.md).

## What a head does to all of that

The four columns below are the four datasets this section was first written against, and
every head in them is fitted on `market1501/train` — so one column is in-domain and three are
transfer. That asymmetry turns out to be the single most important variable in this table; the
`*-msmt17` head stems added later measure it from the other side, in
[94](../docs/project/94-head-fit-domain-and-decision-metrics.md). C-RADIOv4-H at 224x224, mAP:

| | Market (in-domain) | Occluded-REID (transfer) | VRAI (transfer) |
|---|---|---|---|
| `none` — frozen | 0.0610 | 0.4560 | 0.1739 |
| `pca` — 512-d, no labels | 0.0690 | 0.4563 | 0.1625 |
| `linear` | 0.3998 | 0.6241 | 0.1711 |
| `arcface` | **0.7087** | **0.6459** | **0.2276** |

- **the whole gain is the labels, and the PCA control is what proves it.** `pca` fits on the
  same 12,936 images, produces the same 512-d embedding, and uses none of the identities: it
  moves Market 0.0610 -> 0.0690 and Occluded-REID 0.4560 -> 0.4563, and *loses* on VRAI. Every
  head number therefore has a matched control that isolates the 2560 -> 512 bottleneck, and
  the bottleneck is worth nothing. Without this row, "ArcFace beats frozen" would be
  indistinguishable from "512 dimensions are enough";
- **a frozen agglomerative backbone plus one affine layer is a real ReID system.** Market
  0.7181 mAP / 0.8872 R1 (H at 256x128, ArcFace) is the first number in this repository that
  may be compared with a published one, because it is produced the way published ones are:
  fitted on the training split, evaluated on `market1501/official@1`. It does not beat a
  tuned specialist, and it costs one forward pass over 12,936 cached crops plus 29 seconds of
  head fitting on an RTX 2070 Max-Q;
- **angular margin beats cross-entropy everywhere it converges, and by most where it was
  fitted.** Market 0.7087 vs 0.3998 is a 1.8x gap; Occluded-REID 0.6459 vs 0.6241 and VRAI
  0.2276 vs 0.1711 are narrower. ArcFace optimises the cosine geometry the retrieval metric
  reads and the linear head does not, which matters most where the head is asked about the
  identities it was fitted on;
- **the head transfers out of its domain, including out of its *object class*.** The same
  Market-person head is worth +42% relative on Occluded-REID and **+31% on aerial vehicles**
  (0.1739 -> 0.2276), with no vehicle label ever seen. Whatever it learned is not "what a
  person looks like" — it is a metric geometry that instance discrimination reuses. The
  matched `pca` row on VRAI *falls* (0.1625), so this is not the bottleneck either;
- **probing does not merely widen the gap between backbones, it reorders them.** Frozen,
  C-RADIOv4-H leads squashed CLIP on Market by 2.1x mAP; with the same ArcFace head it leads by
  **2.5x** (0.7087 vs 0.2887). More importantly the *ranking itself* changes: SigLIP2-g is the
  best encoder in this table on Market frozen (0.1051, ahead of every C-RADIOv4) and fourth
  once probed (0.6077). A fitted head multiplies frozen Market mAP by 11-13x for DINOv3 and
  C-RADIOv4 and by only 5.8-6.7x for SigLIP2, whose contrastive objective already optimised its
  cosine geometry directly. **Frozen-cosine benchmarking systematically flatters contrastively
  trained encoders**, and this table would have named a different winner without a head;
- **every head converges except CLIP's, and most of CLIP's failure was the crop.** All were
  given the identical 100-epoch budget, fixed on train accuracy before any retrieval number was
  read. Every C-RADIOv4 configuration ends at 0.9998 or better train top-1 over the 751 training
  identities, DINOv3 reaches 1.0000 at both scales and SigLIP2 0.9911-0.9987. Centre-cropped
  CLIP reaches 0.9557 linear and **0.7073** ArcFace — but the *same weights on whole crops*
  reach 0.9955 and **0.9319**. The earlier reading here, that an angular margin cannot separate
  751 identities in CLIP's frozen space, was substantially measuring a preprocessing choice; it
  survives only as the narrower claim that CLIP alone still fails to saturate;
- **the head reorders the resolution finding without contradicting it.** 224x224 and 256x128
  were within noise frozen; with ArcFace, 2:1 wins on Market for both checkpoints (0.7181 vs
  0.7087 for H, 0.7177 vs 0.6957 for SO400M) while still running 1.6x faster, so 2:1 stops
  being a tie and becomes the choice. `native` stays worst on person crops (0.5593) and best
  on VRAI (0.2441), exactly as it was frozen — resolution relative to the trained range is
  still the variable, and a trained head does not rescue 32 tokens;
- **H and SO400M stay one choice on people and two on vehicles.** With ArcFace at 224x224,
  Market is 0.7087 vs 0.6957 and Occluded-REID 0.6459 vs 0.6510 — inside 2% and pointing in
  opposite directions; VRAI is 0.2276 vs 0.2068, H ahead by 10% relative. The head did not
  change which size to buy.

**Probe-training noise is not what separates any of these rows.** Refitting the H@224 ArcFace
head at seeds 1 and 2 and rescoring all three datasets gives mAP 0.7087 / 0.7087 / 0.7084 on
Market (sd 0.0002), 0.6459 / 0.6513 / 0.6414 on Occluded-REID (sd 0.0050, its 1,000 queries
are the noisiest set here) and 0.2276 / 0.2284 / 0.2294 on VRAI (sd 0.0009). The smallest
effect claimed above is roughly twenty times the largest of those. Reproduce with
`probe.py fit --spec` over a copy of `probes/arcface.json` with `seed` changed, then `apply`,
`score` and `measure`; the run records are not kept, because a noise estimate is a
measurement about the table rather than a row in it.

## What the teacher ablation says

C-RADIOv4 distils SigLIP2-g, DINOv3-7B and SAM3, and six of the encoder specs here are that
student and those teachers — so the table answers the question the distillation raises:
**does agglomerating teachers cost you the instance-level margin ReID depends on?**

**That reading lives in one place, and it is not this one:**
[92-protocol-agglomerative-probe.md](../docs/project/92-protocol-agglomerative-probe.md) §14,
where it belongs beside the hypotheses it settles. In one line each, so you know whether to
open it:

| Finding | Where |
|---|---|
| The student's advantage is in-domain and only in-domain — it beats its literal teacher on Market and ties or loses on all three transfer sets | [92 §14.3](../docs/project/92-protocol-agglomerative-probe.md) |
| Where it wins, it wins on mINP — the instance margin distillation was predicted to erode | [92 §14.3](../docs/project/92-protocol-agglomerative-probe.md) |
| The transfer loss has a shape: regression to the teacher mean, bracketed by the teachers on every transfer set | [92 §14.4](../docs/project/92-protocol-agglomerative-probe.md) |
| Frozen-cosine evaluation picks a different winner than a probed one, because it flatters contrastively trained encoders | [92 §14.5](../docs/project/92-protocol-agglomerative-probe.md) |
| DINOv3's angular margin does not transfer — ArcFace loses to a linear head in its space, cross-domain | [92 §14.6](../docs/project/92-protocol-agglomerative-probe.md) |
| Retention falsifies H4, and is the first finding seen from the other side rather than a second one | [92 §14.7](../docs/project/92-protocol-agglomerative-probe.md) |

The per-cell numbers behind all of it are generated, in [`tables/`](tables) — not retyped here
and not retyped there.

The `resize` column exists because of this ablation. timm's eval transform short-side-resizes
and centre-crops, which on a 64x128 person crop keeps the middle 45% of the body; the torchhub
path every C-RADIOv4 row uses does not. Run on timm's default the teachers would have carried a
handicap worth up to 66% of their probed Market mAP that C-RADIOv4 never paid, and this section
would have reported the opposite conclusion with the same confidence.

**Before the first CUHK03 number was read, the adapter was checked against an oracle.** Scoring
*perfect* features under `cuhk03/detected-767@1` gives mAP 1.0000 and *random* ones 0.0022
(Market: 1.0000 and 0.0015), which is what distinguishes a hard dataset from a broken adapter —
CLIP's frozen 0.0073 on CUHK03 is 3.3x its floor where on Market it is 19x. Worth two lines for
any adapter added here.

The licence table under the metrics is generated with them, not maintained beside them.
