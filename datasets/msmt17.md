---
title: "MSMT17 — the primary in-domain benchmark, and its missing front door"
kb_id: dataset-msmt17
type: dataset page
domain: computer-vision, re-identification
tags: [dataset, msmt17, person-reid, access, licensing, provenance]
retrieved: 2026-08-21
confidence: |
  high — the 404 was observed directly on 2026-08-21, and the counts are the ones every
  published MSMT17 table uses.
  medium — the mirror descriptions are read from search results and repository listings, not
  from a completed download. Nothing below has been fetched.
related: [dataset-market1501, dataset-cuhk03-np, reid-benchmarks-datasets, reid-c1-eval-readiness]
---

# MSMT17

> The largest and hardest of the classic four, and the primary in-domain benchmark for C1 and C3.
>
> ⚠️ **There is currently no first-party download.** See §4.

## 1. Facts

This block is the single source of truth for MSMT17's numbers in this project. Nothing else —
no wiki page, no protocol comment, no plan document — restates them; they link here.

```toml
[dataset]
name = "MSMT17"
kind = "person"
role = "PRIMARY in-domain benchmark for C1 and C3; the hard classic set"
licence = "research use only under the authors' release agreement"
licence_verified = false
commercial_ok = false
access = "request"
homepage = "http://www.pkuvmc.com/publications/msmt17.html"
dir = "msmt17/MSMT17_V1"
adapter = ""
protocols = ["msmt17/official@1"]
checked_on = "2026-08-21"
link_verified = true      # verified GONE — see §4

[counts]
identities = 4101
images = 126441
cameras = 15

[counts.train]
identities = 1041
images = 32621

[counts.test]
identities = 3060         # identities, NOT queries — see §5
queries = 11659
gallery = 82161

[expect]
# Line counts of the four list files, which is the check that survives both layouts.
"list_train.txt" = 30248
"list_val.txt" = 2373
"list_query.txt" = 11659
"list_gallery.txt" = 82161

[fetch]
manual = """
THE OFFICIAL PAGE IS GONE. http://www.pkuvmc.com/publications/msmt17.html returned HTTP 404
on 2026-08-21, and www.pkuvmc.com serves a frameset whose dataset frame no longer resolves.
There is currently no first-party download. See §4 of this page for the three routes that
remain and what each one costs you in provenance — this is a licence decision, not a plumbing
problem, so it is deliberately not automated.
"""
```

`python datasets/get.py counts msmt17` prints the same numbers if you need them at a terminal.

## 2. What it is

Multi-Scene Multi-Time: cameras indoors and out on a campus, sampled across four days in
different weather and three time slots per day, with boxes from Faster R-CNN rather than by
hand. The scene and lighting variety is why it stayed hard while Market-1501 saturated, and why
"report MSMT17 at minimum" is the standing advice for any claim about discriminative embeddings.

## 3. What is inside

Two layouts are in circulation and both are read by every toolbox that supports this dataset:

```
msmt17/
  MSMT17_V1/                 # or MSMT17_V2 — faces blurred
    train/                   # V2: mask_train_v2/
    test/                    # V2: mask_test_v2/
    list_train.txt
    list_val.txt
    list_query.txt
    list_gallery.txt
```

The four list files are the real interface: each line is `relative/path pid`, and camera id is
parsed out of the filename. **An adapter that reads the list files works on both layouts**,
which is the reason to write it that way rather than globbing directories.

**V1 vs V2 is a reporting fact, not a preference.** V2 has blurred faces. Numbers from the two
are not interchangeable and a table must say which one it used.

## 4. How to get it — the honest version

**The official page is gone.** Every toolbox that documents MSMT17 — torchreid,
reid-strong-baseline, the EPFL confidence repo — points at that dead URL. This is not a mirror
being down; it is the first-party distribution having disappeared, which the tracking-datasets
KB anticipated when it noted that "MSMT17 access has been restricted at points".

Three routes remain, and they are not equivalent:

| Route | What it gets you | What it costs |
|---|---|---|
| **Email the authors** | the dataset under its actual release agreement, with provenance you can defend | latency, and no guarantee of a reply. Shiliang Zhang (PKU) is the contact of record |
| **A community mirror** — e.g. the Hugging Face dataset `xianpeijie/MSMT17_V1` | the same bytes, quickly | **no licence grant.** You have images whose terms you cannot point at, redistributed by someone with no evident right to redistribute them. Usable for an internal experiment; a live question for a paper, and an outright problem for anything product-facing |
| **A colleague who already signed** | a copy plus a person who can say what they agreed to | the agreement is theirs, not yours |

`get.py` deliberately does **not** automate any of these. This is a licensing decision that a
human has to make once and record; automating the mirror route would be the script quietly
making it for you.

**If you take the mirror route,** write down that you did — in this page's `[fetch] manual`
field and in any paper's data statement. A provenance gap you have written down is a
limitation; the same gap undocumented is a misrepresentation.

**Fallback if MSMT17 stays unavailable.** C1's primary in-domain slot can be re-cast as
Market-1501 (in-domain, near ceiling) plus CUHK03-NP-detected (hard) plus the cross-domain pair
between them. That is a weaker paper — the reviewer question "why no MSMT17?" is predictable —
but it is a real study, and it needs no data this project cannot get. Decide this early rather
than letting the schedule decide it.

## 5. Splits and protocol

Standard single-query retrieval, same-camera exclusion, no distractor class:

```yaml
name:    msmt17/official@1
query:   {split: query}
gallery: {split: gallery}
exclude: [same_uid, same_pid_same_camid, {pid_in: [-1]}]
```

This value already ships in `reidbench`; the adapter does not.

> **The number to not get wrong:** `counts.test.identities` is 3,060 and
> `counts.test.queries` is 11,659. Three wiki pages, one protocol comment and an early draft of
> the C1 plan all had 3,060 as the query count — a nearly 4× understatement of the scale, which
> then propagated into a memory estimate for the score matrix. That is the entire argument for
> this page existing: the number is written once, here, and everything else links.

At the real scale the materialised `rel`/`valid` pair is ~1.9 GB as bytes, which is exactly the
case `measure.retrieval.blocks()` exists for.

## 6. Licence and citation

Research use only, under the authors' release agreement — which is the document that is
currently hard to obtain, hence §4.

```bibtex
@inproceedings{wei2018person,
  title={Person Transfer GAN to Bridge Domain Gap for Person Re-Identification},
  author={Wei, Longhui and Zhang, Shiliang and Gao, Wen and Tian, Qi},
  booktitle={CVPR},
  year={2018}
}
```

## 7. Traps

- **Test identities are not queries.** §5.
- **V1 and V2 are different data.** Blurred faces change what a face-sensitive encoder sees.
- **Mirrors may be re-packed.** A mirror that reorganised directories or re-encoded JPEGs is not
  the same dataset; the manifest content digest will differ from anyone else's, and that is a
  feature — it makes the difference visible instead of silent.
- **`list_val.txt` is not free extra training data** if you intend your numbers to be
  comparable. Most published results train on `list_train.txt` alone or on train+val; say which.

## 8. Status in this project

| | |
|---|---|
| On disk | no |
| `reidbench` adapter | not written — **the C1 blocker** |
| `reidbench` protocol | `msmt17/official@1` ships |
| Provenance record | `msmt17` ships |
| Access | blocked on the §4 decision |
