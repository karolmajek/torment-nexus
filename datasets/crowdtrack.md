---
title: "CrowdTrack — the long-occlusion tracking benchmark C4 depends on, and it is public after all"
kb_id: dataset-crowdtrack
type: dataset page
domain: computer-vision, multi-object-tracking
tags: [dataset, crowdtrack, mot, tracking, occlusion, c4, soma, huggingface, licensing, access]
retrieved: 2026-08-31
confidence: |
  high — access, licence, file list, sizes and checksums are read off the Hugging Face API and a
  live ranged download on 2026-08-31, not quoted from a README. The three layout variants in §3
  and the annotation formats in §4 were parsed out of four archives fetched by HTTP Range.
  medium — the benchmark-wide counts in §1 are the paper's, not counted from disk; nothing is
  downloaded in full yet. §7 says which numbers are quoted and which are measured.
  medium — the train/test split. It is published, as directory grouping inside the Baidu share
  rather than as a table anywhere; reported present there on 2026-08-31 by the project owner and
  not verifiable from this repo, which cannot get past Baidu's password gate. The assignment
  itself is not transcribed here yet, so nothing on this page depends on it. §5.
related: [dataset-msmt17, dataset-occluded-reid, reid-soma, reid-tracking-datasets, reid-contribution-ledger-2026, reid-reidbench-owed]
---

# CrowdTrack

> 33 pedestrian tracking sequences built for the case every other MOT benchmark under-samples:
> people who leave the frame, get buried in a crowd, and come back seconds later.
>
> ✅ **Obtainable, and the licence is the most permissive in this directory.** The open question
> at [90-contribution-ledger-2026.md](../docs/project/90-contribution-ledger-2026.md) §12 — *is
> CrowdTrack obtainable?* — is closed as **yes**: Apache-2.0, public, ungated, no agreement, no
> Baidu account.
>
> ⚠️ **But the two sources are not the same dataset.** Baidu carries the official train/test
> split; the Hugging Face mirror **flattens it away** into 33 undifferentiated archives. Take the
> bytes from HF and the split from Baidu — §5, and it is the difference between a C4 number that
> can sit beside SOMA's and one that cannot.
>
> ⛔ **This is not a re-ID retrieval dataset and must never enter the run matrix.** It is
> single-camera video with per-sequence identities; `adapter` and `protocols` are empty on
> purpose. It enters through the tracker bridge for C4, or not at all. See §6.

## 1. Facts

Single source of truth for CrowdTrack's numbers in this project. Benchmark-wide counts are the
paper's; the `[counts.measured]` block is this project's own and says what it was measured on.

```toml
[dataset]
name = "CrowdTrack"
kind = "pedestrian multi-object tracking"
role = "C4 host benchmark — long-gap identity recovery, the property MOT17 and MOT20 lack"
licence = "Apache-2.0"
licence_verified = true
commercial_ok = true
access = "direct"
homepage = "https://github.com/loseevaya/CrowdTrack"
mirror = "https://huggingface.co/datasets/Loseevaya/CrowdTrack"
paper = "https://arxiv.org/abs/2507.02479"
dir = "crowdtrack"
# EMPTY ON PURPOSE, and for a different reason than LaST's. LaST is a re-ID dataset held back;
# CrowdTrack is not a re-ID dataset at all. There is no protocol shape here for `run.py plan` to
# fill, and inventing one would be inventing a benchmark. §6.
adapter = ""
protocols = []
checked_on = "2026-08-31"
link_verified = true
counts_verified = false
# §5. The official Baidu share groups the sequences into train and test, so the split IS
# published — as packaging, not as a table in the paper. The HF mirror this page fetches from
# flattens it away, so the assignment has to be carried across by hand and is not here yet.
split_published = true
split_in_mirror = false
split_transcribed = false

[counts]
# Paper (arXiv 2507.02479, Table 1). NOT counted from disk — nothing is downloaded in full.
sequences = 33
frames = 34564
boxes = 703000
trajectories = 5185
avg_trajectories_per_video = 158
fps = 20
train_videos = 17
test_videos = 16             # the assignment lives in the Baidu share's directory grouping, §5

[counts.archives]
# Read off the HF tree API on 2026-08-31. 35 files for 33 sequences: track0033 ships twice.
files = 35
total_gb = 31.99
tar_gz = 4                   # track0001-0004
zip = 29                     # track0005-0033
sevenzip = 1                 # track0033.7z, a duplicate of track0033.zip

[counts.measured]
# This project's own numbers, parsed out of track0001's gt file on 2026-08-31 by ranged HTTP
# read. ONE sequence of 33. Do not generalise these; they are here as an existence proof for §7.
measured_on = "track0001"
frames = 799
boxes = 15096
identities = 53
boxes_per_frame = 18.9
id_gaps = 240                # an identity absent for >=1 frame, then annotated again
id_gaps_over_5s = 21         # >=100 frames at the paper's 20 fps
longest_gap_frames = 324     # ~16.2 s

[fetch]
# HF resolve URLs, public and unauthenticated: 302 to the CDN with user_id=public, and the CDN
# honours Range. Verified on 2026-08-31 by a 206 Partial Content on track0020.zip and on the
# malformed track0025..zip. `get.py fetch` will work unmodified; see the warnings in `manual`.
base = "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/"
urls = [
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0001.tar.gz",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0002.tar.gz",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0003.tar.gz",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0004.tar.gz",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0005.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0006.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0007.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0008.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0009.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0010.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0011.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0012.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0013.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0014.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0015.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0016.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0017.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0018.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0019.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0020.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0021.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0022.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0023.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0024.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0025..zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0026.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0027.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0028.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0029.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0030.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0031.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0032.zip",
    "https://huggingface.co/datasets/Loseevaya/CrowdTrack/resolve/main/track0033.zip",
]
manual = """
NOT DOWNLOADED. Everything above is verified remotely; nothing is on disk. 32 GB.

track0033.7z is DELIBERATELY NOT LISTED. It is a second copy of track0033 (411,590,468 bytes
against the zip's 411,634,921) and `get.py` cannot unpack 7z anyway — it would download 412 MB
and then warn. One sequence, one archive, and the zip is the one every other sequence uses.

Three traps that will bite a first fetch, all confirmed on 2026-08-31:

1. track0025..zip really is spelled with two dots. It is not a typo in this file; it is a typo
   in the release, and the URL 206s exactly as written. Do not "fix" it.
2. track0033.zip has NO top-level directory — its members are bare `track0033_000000.jpg` at the
   archive root. Every other zip wraps its frames in `trackNNNN/`. Extracting all archives into
   one target therefore sprays track0033's 1,630 files loose beside the 32 sequence directories.
   Unpack it into `crowdtrack/track0033/` by hand, or teach the adapter to tolerate both.
3. The four .tar.gz archives carry a DIFFERENT internal layout and a DIFFERENT annotation format
   from the 29 zips. This is not a packaging detail; it is two parsers. §3 and §4.

sha256 for all 35 files is on the HF tree API as the LFS oid, recorded in [checksums] below.
Those are HF's, not ours: confirm against what `get.py` prints on a real download before
treating any of them as verified.
"""

[checksums]
# HF LFS oids (sha256 of file content), read from the tree API on 2026-08-31. UNCONFIRMED
# locally — see [fetch].manual.
"track0001.tar.gz" = "4495bf73717195d6f4c6c5a987c3dc53778c96a05ce73df05ebfb0b77f485b1d"
"track0002.tar.gz" = "91b90665fe94a226fd164c7976f70750acd9fc7bcf87ce35bdaae0caa54f2090"
"track0003.tar.gz" = "a901115c22fdd21c28c1dab02fec2b003a922ae3fa0dcde0567259fb564c7176"
"track0004.tar.gz" = "439a750ec287607863a594985daa31af4fe1d4739a2957a1fde9ae0877d44373"
"track0005.zip" = "83e3a2bf571aebfb0636ef754314a19f021711e004a41971256a4b758bb18b63"
"track0006.zip" = "94dc15588514be2584e1c8c20391a767dabf582baf65a57599192881bd5470bf"
"track0007.zip" = "bbfc4b31f24420da81508df51312c7004b06baf2fc40ebff9e06a05c8c503a78"
"track0008.zip" = "8671708768a2bf182ccf60883a8e2c1a51075e147df92b7604581cb43b826b8a"
"track0009.zip" = "6bdddfbff93887ab6093c14ceb818862f55e225610771f4ab4da6604674703b2"
"track0010.zip" = "394390efaaf2607fd3c7a1db7038a7aa663cc9660ab02b206aa72bafad154f86"
"track0011.zip" = "574151b384cf934e5f8b23576eeca7803e75663a73783fe0e21d011685bd567b"
"track0012.zip" = "6a035252611b01336ae68fa2b59367f1de05693e2a0d9609cfe708ab7419551d"
"track0013.zip" = "234ab613c6af1cb4a9ba61703a62a13d5c57405c212b0809fc551575cfd163e3"
"track0014.zip" = "bb0ee6297c90abd356dd09537ead74b05f3895134b28ab2b522bdf5898969e96"
"track0015.zip" = "da3479514e46e9ce6eb9d5b0082b9a7dc38c1c7ceb97fb5347e26aa193d8478c"
"track0016.zip" = "942b9a61d11cb3673281196e1f301b30e3ccce6ed36bf55d06bed85f72957620"
"track0017.zip" = "36458284d395b4c6f5913ebcc44ebc00e5f0f71c90b4fcc79b4913265de1ac1f"
"track0018.zip" = "bd7c16665b2f3fa244cbb9fd22cac999a11320ae63cbcbe0e9c873600df70523"
"track0019.zip" = "25abc41ac39e4f609ccd7aa13fc201b4c1d7bffb9bc889b199498fc9c275d392"
"track0020.zip" = "4db99d58012650c5422247d856c7bc0a0a97625960d0ea0b2cedef1b2d055d43"
"track0021.zip" = "0c4fb7e8ae5a01ebe498bdd4bf63300632aebfd80c44d2217548a6aa9a6ba629"
"track0022.zip" = "03b80c29abb99c88691e4a693f3a705b1f49bd3d7bcdcbe52fb304eddda75c4f"
"track0023.zip" = "b20740fb4d5833aea8ba5e5cdd727e3deb69ed8ca83348ed4e9cbe2cf3c9af05"
"track0024.zip" = "5ea264f42255d87ac8ab20b29155221b1f15fd58b4a1604afd1ec9594b4885fe"
"track0025..zip" = "d79214aeadaf0686e4836ab18fff08511a366cbdc77383b8241cb42b0ba82e54"
"track0026.zip" = "1ce9acb9f48137cb92c7f2b54aa77a1009e1343562d7b05967358d494bfae019"
"track0027.zip" = "4ef941b02fa6c97ff35892bb7ccde5df19bd98eddde1d8232c28a4d09714745d"
"track0028.zip" = "c692436929be3c0292bffe65e95abedb74aeeaf50b1c6ddd16f05e06fe12fb58"
"track0029.zip" = "2da5b3ea7dcea78270e31ba004b8dcf37667e3f0101e8b9dd193703ebe6c90de"
"track0030.zip" = "bb8f460044f081443fcd45689c70a28dcb5ecf564e49652af717dc12e8b5344c"
"track0031.zip" = "1be250f112fa8c450706b7298004b1e748cf16ec2b61f3a90d08267cd415011f"
"track0032.zip" = "9325567412da760d0a15225bc52f8588a0695fb5769004199f8d7fb1825cc204"
"track0033.zip" = "42526786f647d606c1597a2dbd8d144b5ef1b47cdc7689324a5d66a7e9323d9a"
"track0033.7z" = "751bc53c7a24fd83bfc9ea1590bf14fff7d025ddcc799dcf9b03af7721ac6ed0"
```

## 2. What it is, and why this project cares

33 pedestrian sequences shot in unconstrained daily environments, fixed and moving camera, with
one stated design goal: **difficult samples**. Occlusion, crowding, motion blur, scale change,
and — the part that matters here — identities that disappear for long stretches and come back.

Every other tracking benchmark in [reid-tracking-datasets-kb.md](../docs/field/reid-tracking-datasets-kb.md)
under-samples exactly that. [soma-kb.md](../docs/field/soma-kb.md) records the comparison:
**MOT17 contains 7 ground-truth 4–6 s occlusion episodes in the entire benchmark; CrowdTrack has
roughly 133.** That claim was a citation when it was written. §7 is the first time this project
has checked any of it against the data.

CrowdTrack is smaller than DanceTrack and carries fewer boxes than MOT20. It is not here for
scale. It is here because it is the only benchmark on the board where the question C4 asks —
*does a better frozen embedding actually recover an identity after a five-second gap?* — has
enough positive examples to answer.

| | MOT17 | MOT20 | DanceTrack | **CrowdTrack** |
|---|---|---|---|---|
| videos | 14 | 8 | 100 | **33** |
| avg trajectories/video | 96 | 432 | 9 | **158** |
| boxes (k) | 292 | 1,652 | 880 | **703** |
| frames | 11,235 | 13,410 | 105,855 | **34,564** |
| fps | 30 | 25 | 20 | **20** |

*The paper's Table 1, quoted. The MOT17/MOT20/DanceTrack rows are its figures, not ones this
project verified.*

## 3. What is inside — three layouts, not one

Parsed on 2026-08-31 out of four archives read by HTTP Range without downloading them in full:
track0001 (tar.gz), track0005, track0020 and track0033 (zip). The mapping below is inferred from
those four; sequences not listed are assumed to follow their archive type and **nobody has
checked**.

**Lane A — `track0001.tar.gz` … `track0004.tar.gz`.** MOT-shaped, PNG frames, separate gt file:

```
track0001/
  gt/track0001.txt
  img/track0001_000000.png … track0001_000798.png
```

**Lane B — `track0005.zip` … `track0032.zip`.** No gt file at all. JPEG frames, and a *per-frame*
JSON sidecar carrying that frame's boxes:

```
track0020/
  track0020_000000.jpg
  track0020_000000.json
  … 419 pairs
```

**Lane C — `track0033.zip`.** Lane B without the wrapping directory. Members are bare
`track0033_000000.jpg` at the archive root. See `[fetch].manual` trap 2.

## 4. Annotation formats — also two, and neither is MOTChallenge

**Lane A, `gt/trackNNNN.txt`.** Space-separated, six columns, frame index zero-based and
zero-padded:

```
00000 1 1532.1266968325792 444.3438914027149 28.506787330316683 79.18552036199094
00000 2 1495.0226244343892 440.27149321266967 49.321266968325745 110.85972850678735
```

`frame id x y w h`. This is **not** the MOTChallenge format, which is comma-separated, ten
columns, one-based, and carries `conf,class,visibility`. A loader pointed at this expecting
`gt.txt` semantics will parse the width as a confidence and silently produce nonsense.

**Lane B/C, per-frame `.json`.** LabelMe 4.5.6, straight out of the annotation tool:

```json
{"version": "4.5.6", "flags": {},
 "shapes": [{"label": "1",
             "points": [[19.02, 356.04], [210.08, 817.83]],
             "group_id": null, "shape_type": "rectangle", "flags": {}}],
 "imagePath": "track0020_000414.jpg", "imageHeight": 1080, "imageWidth": 1920}
```

Three things a reader has to know:

- **`label` is the track ID**, persistent across frames within the sequence. Frames 414–418 of
  track0020 all carry the same 15 labels; label `9` is absent from all five, which is what an
  occluded identity looks like here.
- **`points` is two corners, not `x y w h`.** `[[x1,y1],[x2,y2]]`. Converting to the Lane A
  convention is `w = x2-x1, h = y2-y1`, and getting this backwards is the second silent-nonsense
  failure mode after the column-count one.
- `imageHeight`/`imageWidth` are per frame, so resolution is not constant across the release and
  should not be assumed. track0020 is 1920×1080.

There is **no `seqinfo.ini`** anywhere, so frame rate is the paper's global 20 fps and is not
recorded per sequence. Every "seconds of occlusion" number in this project rests on that.

## 5. Splits — preserved at source, destroyed by the mirror

The paper states **17 training videos and 16 test videos**, "balanced across video count,
tracklets, and pedestrian annotations". It does not print the assignment, and neither does the
GitHub README.

**The Baidu Cloud share does.** It carries the sequences grouped into train and test; the split
is packaging, not documentation, which is why reading the paper for it was always going to fail.
The **Hugging Face mirror flattens that grouping away** — 33 archives named `track0001`–
`track0033` in one flat namespace, with nothing recording which side each came from.

> ⚠️ **So the two sources are not interchangeable, and the more convenient one is the lossy one.**
> Everything §9 says about HF being public, ungated and Apache-2.0 still holds; it is the right
> place to get 32 GB of bytes. It is *not* the right place to learn what the benchmark is. A
> project that took the easy download and stopped there would have silently lost the split and
> then reported an all-33-sequence number as if it were comparable.

This matters because [soma-kb.md](../docs/field/soma-kb.md) records every SOMA benchmark number
as measured on `data/CrowdTrack/train`. A C4 run over all 33 sequences measures something else
and must never be put in a column beside them.

**The cheap resolution, and the reason this is no longer a real blocker:** what has to come from
Baidu is *the directory listing*, not the data. Two lists of sequence names — 17 and 16 — are a
few hundred bytes. Record them on this page, pull the 32 GB from HF as §9 describes, and apply
the split locally. That decouples "needs a Baidu account" from "needs 32 GB through Baidu's
throttled browser download", and it is why the ledger risk closed rather than moved.

Status: **reported present on Baidu on 2026-08-31 by the project owner, who could open the
share; not transcribed here yet.** This page will not guess at the assignment — a wrong split is
worse than a missing one, because it looks reproducible. The two lists go in a `[splits]` block
below `[counts]` the moment someone reads them off the share.

Route if the listing turns out to be unreadable after all: SOMA's `soma-eval` cache code
enumerates `data/CrowdTrack/train`. If it hardcodes a sequence list, that list *is* the split
this project should use for a C4 comparison, whatever the release says — because matching SOMA's
numbers is the entire point of the exercise.

**Why this could not be checked from here.** `pan.baidu.com/s/1iArSnByE5tEPwlHrKpnWFg?pwd=crtr`
redirects to `/share/init` (the password gate), and the listing API answers
`{"errno":9019,"errmsg":"need verify"}` without a Baidu session. Confirmed 2026-08-31. Reading
this share needs a human with an account; it is not automatable from this repo.

## 6. Why there is no adapter and no protocol

CrowdTrack is single-camera video. Identities are scoped to their own sequence and no identity
crosses sequences, so there is no cross-camera query/gallery structure for a `reidbench` protocol
to express — the same structural objection that keeps MOT17 and MOT20 out, recorded in
[00-index-reid-2026.md](../docs/00-index-reid-2026.md) as *pure single-camera MOT is out of
scope*. Building a retrieval protocol on it would mean inventing a benchmark and reporting
numbers nobody else has.

It enters this project through **the tracker bridge for C4** — encoder in, HOTA/AssA/long-gap
recovery out — which [38-reidbench-owed.md](../docs/project/38-reidbench-owed.md) lists as
unbuilt on purpose. `adapter` and `protocols` stay empty until that decision changes. `get.py`
will list, fetch and verify this page regardless; that is the point of `access = "direct"` and it
costs nothing.

## 7. What this project measured, and what it means

One sequence, track0001, parsed from its gt file by ranged read. Numbers are in
`[counts.measured]`; the reason they are here is this:

> **21 identity gaps of 100+ frames — 5+ seconds at 20 fps — in a single 799-frame sequence.**

[soma-kb.md](../docs/field/soma-kb.md) puts MOT17's total at 7 such episodes across the whole
14-sequence benchmark. One CrowdTrack sequence has three times that. The longest gap in
track0001 is 324 frames, about 16 seconds.

This does not confirm the "~133" figure — that is a benchmark-wide count over a specific duration
window, computed some other way, and 33 sequences at track0001's rate would give far more than
133. **The direction is confirmed and the magnitude is not**, which is exactly what
[soma-kb.md](../docs/field/soma-kb.md) already claimed for it ("checkable, and the direction is
certainly right"). Anyone quoting 133 should still compute it themselves once the data lands.

## 8. Licence

**Apache-2.0**, declared on the GitHub repository and on the Hugging Face dataset card, both
under the authors' own account. `commercial_ok = true`.

That makes CrowdTrack **the most permissively licensed dataset in this directory** — every person
re-ID set here is academic-use-only or worse, and the vehicle sets require an agreement. If any
part of this work goes product-facing, the tracking-validation lane is the one lane that does not
become a licence problem. Worth saying out loud in the paper's data section.

The usual caveat applies and applies harder to a crowd dataset: Apache-2.0 is a *copyright*
licence and says nothing about the privacy interest of the several thousand identifiable
pedestrians in these 34,564 frames. It is not a GDPR clearance. See the scope note in
[00-index-reid-2026.md](../docs/00-index-reid-2026.md) on the regulatory layer this project
deliberately does not cover.

## 9. Access

The official download in the GitHub README is **Baidu Cloud** (`pan.baidu.com`, password `crtr`),
which needs a Baidu account and is a real barrier from Europe. The Hugging Face mirror is the
same authors' — `Loseevaya` on HF is `loseevaya` on GitHub, the account the paper names — and has
none of that.

**Use both, for different things.** Bytes from HF, split from Baidu; the mirror is complete in
data and lossy in structure, per §5. One visit to the share to read two directory listings is the
whole of what Baidu is needed for.

```bash
python datasets/get.py show crowdtrack
python datasets/get.py fetch crowdtrack     # 32 GB over 33 archives; read [fetch].manual first
python datasets/get.py verify crowdtrack
```

Verified on 2026-08-31: repo public, `gated: false`, `private: false`; resolve URLs 302 to
`us.aws.cdn.hf.co` with `user_id=public` and no credential; the CDN returns `206 Partial Content`
on a Range request. No token, no login, no agreement.

## 10. Citation

```bibtex
@article{crowdtrack2025,
  title={CrowdTrack: A Benchmark for Difficult Multiple Pedestrian Tracking in Real Scenarios},
  journal={arXiv preprint arXiv:2507.02479},
  year={2025}
}
```

*Author list not transcribed — fill it from the paper before this reaches a bibliography.*

## 11. Traps

- **Two annotation formats in one release.** §4. Neither is MOTChallenge.
- **`points` is corners, `gt.txt` is `x y w h`.** §4. Silent nonsense either way round.
- **`track0025..zip`** is spelled with two dots at source. §1 `[fetch].manual`.
- **`track0033.zip` has no top-level directory.** It will spray 1,630 files into whatever
  directory you extract it in.
- **`track0033.7z` is a duplicate.** Not listed, not needed, and `get.py` cannot unpack 7z.
- **No `seqinfo.ini`, no per-sequence fps.** Every occlusion duration rests on the paper's 20.
- **The convenient download is the lossy one.** §5. HF has the bytes and *not* the train/test
  split; Baidu has both. Fetching from HF alone and running all 33 sequences produces a number
  that cannot be compared with any published CrowdTrack result, and nothing will warn you.
- **Not a re-ID dataset.** §6. If it ever appears in `results/table.md`, something went wrong.

## 12. Status in this project

| | |
|---|---|
| Obtainable | ✅ **yes** — public, ungated, Apache-2.0, verified 2026-08-31 |
| On disk | ✖ not downloaded (32 GB) |
| Counts verified | ✖ paper-quoted; one sequence measured remotely, §7 |
| Split known | 🚧 **exists on Baidu, not in the HF mirror, not yet transcribed here**, §5 |
| `reidbench` adapter | ✖ none, on purpose, §6 |
| `reidbench` protocol | ✖ none, on purpose, §6 |
| Provenance record | ✖ n/a — not an encoder |
| Gates | C4 (tracker validation via SOMA), [90-contribution-ledger-2026.md](../docs/project/90-contribution-ledger-2026.md) §9.4 |
