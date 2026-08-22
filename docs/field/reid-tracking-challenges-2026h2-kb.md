---
title: "ReID & Tracking Challenges — Landscape for H2 2026"
kb_id: reid-tracking-challenges-2026h2
type: reference / competition landscape
domain: computer-vision, multi-object-tracking, re-identification, benchmarking
tags: [challenge, competition, leaderboard, ai-city-challenge, soccernet, macvi, animalclef, neurips-competition, eccv-2026, wacv-2027, prize, workshop]
related: [reid-in-mot, reid-mot-metrics, reid-tracking-datasets]
retrieved: 2026-08-18
confidence: medium-high — snapshot as of 18 Aug 2026. Challenge calendars move; verify every date on the linked page before planning around it.
---

# ReID & Tracking Challenges — H2 2026

## TL;DR

**The blunt answer: the 2026 ReID/tracking competition season is essentially over.** The two anchor events — AI City Challenge and SoccerNet — both closed submissions before July. What remains in H2 2026 is:

1. **Results and workshop season** — AI City at ECCV 2026 (8 Sept), AnimalCLEF at CLEF 2026 (21–24 Sept), NeurIPS competition workshops (11–12 Dec).
2. **Prep season for the 2027 cycle** — MaCVi @ WACV 2027 is accepted with challenge pages still being written; that is the main thing to watch right now.
3. **Rolling leaderboards with no deadline** — MOTChallenge, DanceTrack, SportsMOT, BDD100K, macvi.org, Kaggle late submission. These accept entries any day of the year and are the correct target if you want a number this quarter.

Also worth knowing: **NeurIPS 2026 accepted 16 competitions and none of them are ReID or tracking.** The venue for this work is CV workshops, not the ML competition track.

---

## 1. The 2026 calendar

```mermaid
timeline
    title ReID / tracking competition cycle 2026
    section H1 2026 — submission window
        Feb 1 : AnimalCLEF 2026 opens
        Apr 20 : AI City Challenge 10th edition launches, data released
        Apr 24 : SoccerNet 2026 closes
        May 7 : AnimalCLEF 2026 closes, 230 teams
        May 15 : NeurIPS competition proposals due
        May 28 : AI City evaluation server opens
    section H2 2026 — results and prep
        Jul 10 : AI City track submissions due
        Jul 24 : AI City workshop papers due
        Jul 28 : NeurIPS 2026 competitions announced, none on ReID or MOT
        Aug 15 : AI City camera-ready
        Sep 8 : AI City awards at ECCV 2026
        Sep 21 to 24 : CLEF 2026 Jena, AnimalCLEF results
        Q4 : MaCVi at WACV 2027 challenge pages expected
        Dec 11 to 12 : NeurIPS 2026 competition workshops
```

---

## 2. Status board

| Event | ReID/tracking relevance | Status at 18 Aug 2026 | Prize model |
|---|---|---|---|
| **AI City Challenge 2026** (10th, @ ECCV 2026) | Track 1 multi-camera 3D perception; Track 4 text-based person ReID; Track 6 cross-city detection | **Closed.** Submissions ended 10 Jul. Awards 8 Sept | Awards + Springer-published ECCV workshop paper |
| **SoccerNet 2026** (6th edition) | **Dropped ReID and tracking tracks this year** — lineup is action anticipation, player-centric spotting, NVS, SynLoc, VQA | **Closed** 24 Apr. Results paper posted Jul | Cash prizes per track, sponsor-funded (e.g. USD 1,000 for VQA) |
| **AnimalCLEF 2026** (LifeCLEF @ CLEF) | Individual animal ReID as unsupervised identity *discovery*; ARI scoring | **Closed** 7 May; 230 teams. Presented at CLEF, Jena, 21–24 Sept | Publication in CEUR-WS proceedings; Kaggle late submission open |
| **MaCVi @ WACV 2027** (5th) | Historically UAV maritime MOT **with ReID** on SeaDronesSee, plus USV tracking | **Accepted, challenges TBA.** Page marked work-in-progress | Workshop paper + leaderboard standing; sponsor-backed |
| **MaCVi @ CVPR 2026** | Same family | **Concluded.** Summary paper published | — |
| **NeurIPS 2026 Competition Track** | **No ReID or tracking competition among the 16 accepted** | Workshops 11–12 Dec | PMLR volume or D&B track paper |
| **ILR+G @ ECCV 2026** | Instance-level recognition incl. animal ReID and video tracking — paper workshop, financial awards for best papers | Papers, not a leaderboard challenge | Best-paper awards, student grants |
| **Kaggle wildlife ReID series** (e.g. Jaguar ReID rounds) | Camera-trap individual ReID, spurious-correlation robustness | Community competitions, rounds run intermittently | Usually kudos-only; some sponsor-funded |
| **Rolling leaderboards** | MOTChallenge, DanceTrack, SportsMOT, BDD100K, macvi.org | **Always open** | None — reputational only |

---

## 3. Conference/workshop challenges vs. prize challenges

The user's distinction matters, and the two categories behave very differently.

```mermaid
flowchart TD
    ROOT["Why does this challenge exist?"]

    ROOT --> A["A. Workshop-anchored<br/><i>the reward is a publication</i>"]
    ROOT --> B["B. Prize-anchored<br/><i>the reward is money</i>"]
    ROOT --> C["C. Benchmark-anchored<br/><i>the reward is a leaderboard row</i>"]

    A --> A1["AI City @ ECCV 2026<br/>MaCVi @ WACV<br/>ILR+G @ ECCV<br/>AnimalCLEF @ CLEF"]
    A --> A2["Traits:<br/>tied to conference calendar,<br/>technical report mandatory,<br/>open-source often required for awards,<br/>rigid single deadline"]

    B --> B1["SoccerNet sponsor prizes<br/>DeepSportradar @ MMSports<br/>Kaggle sponsor competitions"]
    B --> B2["Traits:<br/>industry-sponsored, modest sums<br/>typically USD 500 to 5,000,<br/>strict eligibility and licence terms,<br/>sometimes code-submission required"]

    C --> C1["MOTChallenge, DanceTrack,<br/>SportsMOT, BDD100K,<br/>macvi.org, Kaggle late submission"]
    C --> C2["Traits:<br/>no deadline, no prize,<br/>submission-count limits,<br/>the standard way to claim SOTA in a paper"]

    classDef a fill:#e0e7ff,stroke:#4f46e5,color:#1e1b4b
    classDef b fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef c fill:#d1fae5,stroke:#059669,color:#064e3b
    class A,A1,A2 a
    class B,B1,B2 b
    class C,C1,C2 c
```

### Practical implications

| Question | Workshop-anchored | Prize-anchored | Rolling leaderboard |
|---|---|---|---|
| Can I enter today? | Only in the window | Only in the window | Yes |
| What do I get? | Peer-reviewed paper, often Springer/CVF proceedings | Cash, usually modest | A row and a citation hook |
| Is open-sourcing required? | Frequently, for award eligibility | Sometimes | No |
| Cost of missing the deadline | A full year | A full year | Zero |
| Best for | Academic CV, credibility | Industry teams, students | Anyone, anytime |

> **The money is not the point.** In this field prize pools are small — three to four figures. The real currency is a workshop paper in CVF/Springer proceedings plus a defensible leaderboard number. Teams optimise for the publication, not the cheque.

---

## 4. What to actually do in H2 2026

```mermaid
flowchart TD
    Q{"What's your goal this quarter?"}

    Q -->|"I want a number in a paper<br/>this quarter"| A1["Rolling leaderboards.<br/>MOTChallenge, DanceTrack,<br/>SportsMOT, BDD100K, macvi.org.<br/>No deadline, no gatekeeping."]
    Q -->|"I want to win something<br/>in the next cycle"| A2["Watch MaCVi at WACV 2027.<br/>Build now on SeaDronesSee.<br/>Also track the AI City 2027<br/>announcement, typically spring."]
    Q -->|"I want to publish a<br/>workshop paper soon"| A3["ILR+G at ECCV 2026<br/>covers animal ReID and tracking<br/>as a paper track, plus best-paper awards."]
    Q -->|"I want to learn what<br/>just won"| A4["Read the 2026 results papers:<br/>AI City summary, SoccerNet 2026,<br/>MaCVi CVPR 2026 challenge report."]
    Q -->|"I want a low-barrier<br/>ReID competition"| A5["Kaggle wildlife ReID rounds<br/>plus AnimalCLEF late submission.<br/>Small data, real research problem."]

    classDef box fill:#f1f5f9,stroke:#475569,color:#0f172a
    class A1,A2,A3,A4,A5 box
```

**Highest-leverage single action:** the MaCVi @ WACV 2027 challenge tracks are not published yet but the benchmark family is stable. The UAV maritime MOT-with-ReID track has run in three prior editions on SeaDronesSee. Building against the existing public leaderboard now means you are ready on day one instead of week six.

---

## 5. Notable structural trends in the 2026 cycle

1. **Sim2Real is the framing everywhere.** Four of six AI City 2026 tracks are explicitly synthetic-train / real-test. Large synthetic corpora — hundreds of hours, over a thousand virtual cameras — are now the default training substrate, and the competition is about closing the domain gap, not about squeezing the last point out of real annotations.
2. **Classic ReID tracks are being retired in favour of harder framings.** SoccerNet dropped its ReID and tracking tracks entirely for 2026. AI City replaced image-to-image person ReID with *text-based* person retrieval including behaviour descriptions. Rank-1 saturation on classic benchmarks is the driver.
3. **Identity *discovery* is replacing identity *retrieval*.** AnimalCLEF 2026 scores clustering with ARI rather than gallery retrieval with mAP, because the deployed problem is building the gallery, not querying it. Expect this framing to spread to person ReID.
4. **Privacy-constrained data access is now infrastructure.** AI City Track 6 runs on a privacy-preserved training-as-a-service platform with hidden benchmark data, rather than distributing video. Expect more of this under EU AI Act pressure.
5. **Reproducibility gates are tightening.** Dockerised submissions and mandatory open-sourcing for award candidates are now standard in the AI City rules.
6. **ReID/MOT is absent from the general ML competition venues.** Zero of NeurIPS 2026's 16 competitions touch it. The field's competitive infrastructure lives entirely in CVF workshops.

---

## 6. Verification checklist

Before committing effort to any challenge in this document:

- [ ] Open the official page — dates in this KB are a **snapshot of 18 Aug 2026** and challenge calendars slip routinely.
- [ ] Check whether the track still exists this edition. SoccerNet dropping ReID is the cautionary example.
- [ ] Read the rules for external-data and pretrained-model restrictions **before** training anything.
- [ ] Confirm the evaluation platform and its submission-count limits (EvalAI, CodaBench, Kaggle, custom server). Several communities migrated EvalAI → CodaBench in 2026.
- [ ] Check award eligibility conditions — open-source release, Dockerised inference, and paper submission are common prerequisites.
- [ ] Check the licence on the challenge data for downstream use after the competition ends.

---

## 7. Canonical links

| Resource | URL |
|---|---|
| AI City Challenge | https://www.aicitychallenge.org/ |
| AI City 2026 awards | https://www.aicitychallenge.org/2026-challenge-awards/ |
| SoccerNet challenges | https://www.soccer-net.org/challenges |
| SoccerNet 2026 results paper | https://arxiv.org/abs/2607.07320 |
| MaCVi initiative | https://macvi.org/ |
| MaCVi @ WACV 2027 | https://macvi.org/workshop/macvi27 |
| MaCVi CVPR 2026 challenge report | https://arxiv.org/abs/2604.13244 |
| AnimalCLEF 2026 | https://www.imageclef.org/AnimalCLEF2026 |
| NeurIPS 2026 competitions | https://blog.neurips.cc/2026/07/28/neurips-2026-competitions-announced/ |
| ILR+G @ ECCV 2026 | https://ilr-workshop.github.io/ECCVW2026/ |
| MOTChallenge | https://motchallenge.net/ |

---

## 8. Retrieval hints

Answers: *are there open ReID challenges right now · what tracking competitions are running in late 2026 · AI City Challenge 2026 tracks and deadlines · did SoccerNet have a ReID track in 2026 · MaCVi WACV 2027 · AnimalCLEF 2026 · are there NeurIPS competitions on tracking · which challenges have prize money · workshop challenge vs Kaggle prize · where can I submit to a tracking leaderboard with no deadline · what should I prepare for the 2027 cycle.*

**Single most quotable fact:** as of August 2026 no major person-ReID or MOT challenge is accepting submissions — AI City closed 10 July and SoccerNet dropped its ReID and tracking tracks entirely — so the only live options are permanently-open leaderboards like MOTChallenge and preparation for MaCVi @ WACV 2027.
