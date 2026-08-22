# datasets — what we read, where it comes from, and what it costs

Thirteen datasets, one page each, and a runner that reads those pages. Nothing here is part of
`reidbench`: that package refuses to download, unpack, mirror or auto-repair anything, and this
directory is where that refusal gets its counterpart.

```
datasets/
  <name>.md         one page per dataset — prose, plus a ```toml block that IS the data
  get.py            a runner over those pages: ls · show · counts · fetch · verify
```

## One number, one place

**Every count lives in exactly one file: the ```toml block near the top of that dataset's page.**
Not in a registry beside it, not in a wiki table, not in a protocol comment. `get.py` parses the
same block a human reads, so the runner and the prose cannot disagree — there is nothing to keep
in sync, because there is only one copy.

This is not tidiness. Before the rule existed, MSMT17's query count appeared in six places and
**three of them had it wrong in the same way** — carrying the test-*identity* count as if it were
the query count, understating the scale by nearly 4× and propagating into a memory estimate for
the score matrix. Wiki pages, protocol comments and plan documents now link here instead.

Anything that needs a number at a terminal:

```bash
python datasets/get.py counts msmt17
```

## Use

```bash
python datasets/get.py ls                 # everything, its licence posture, whether it is on disk
python datasets/get.py show msmt17        # one dataset in full, including what cannot be automated
python datasets/get.py counts veri776     # just the numbers
python datasets/get.py fetch occluded-reid
python datasets/get.py verify --all       # layout and file counts against what the pages declare
```

Adding a dataset is a new page with a ```toml block. `get.py` never changes.

Needs **Python 3.11+** (`tomllib`) and nothing else. The system `py` on this machine is 3.7 —
use `reidbench/.venv/Scripts/python.exe` or any modern interpreter. `gdown` is optional and is
shelled out to for Google Drive entries; without it the script prints the command rather than
imitating it badly.

The data root is `./data`, overridden by `$REID_DATA_ROOT` or `--root`. `data/` is gitignored.

If datasets already live elsewhere on this machine — VeRi-776 does — point the root at them
rather than copying: `REID_DATA_ROOT=/path/to/collection python datasets/get.py verify --all`.
`verify` never writes, so it is safe to run against a directory you care about.

## The four access kinds, and why the table is honest about them

| kind | what happens | which |
|---|---|---|
| `direct` | plain HTTPS; `fetch` downloads, checksums, unpacks, and prints the sha256 to record | occluded-reid, market1501-attribute, soma |
| `gdrive` | Drive file id is on the page; `fetch` delegates to `gdown` or prints the link | cuhk03-np, ccvid, mars, vrai (a *folder*, so the page prints `gdown --folder`) |
| `request` | a human signs an agreement and emails an author. No automation exists or is pretended | msmt17, market1501, market1501-500k, veri776, vehicleid, veri-wild |
| `denied` | refused, loudly, with no override flag | everything with DukeMTMC lineage |

**Six of thirteen are `request`.** That is the real shape of this field's data access, and it is
the schedule risk worth planning around: the download is minutes, the agreement is weeks. Start
the vehicle requests (VeRi-776, VehicleID, VERI-Wild) before you need them.

## The denial

DukeMTMC and every derivative — DukeMTMC-reID, DukeMTMC-VideoReID, Occluded-Duke,
P-DukeMTMC-reID — are denied permanently. The parent dataset was withdrawn over how
surveillance footage of students was collected and distributed; derivatives inherit the
problem, and reviewers increasingly flag their use.

`get.py` refuses to fetch, locate or describe them, exits 3, and offers the alternative.
`verify` additionally reports a denied dataset that is already sitting on disk. There is no
override flag, which is the same decision `reidbench.provenance` makes independently — neither
imports the other, because both have to be able to stand alone. The refusal text the script
prints is read from the denial page's own `toml` block, so the code and the reasoning are one
string rather than two copies of one.

This bites in one concrete place: the Occluded-ReID repository also ships
`P-DukeMTMC-reid.zip` next to the file we want. The registry lists exactly one URL for that
entry and `get.py` has no "download the repo" verb.

Full reasoning, the enforcement points, and a substitute for every Duke-derived dataset:
**[dukemtmc-denied.md](dukemtmc-denied.md)**.

## Status, 2026-08-22

| dataset | role | access | on disk |
|---|---|---|---|
| [market1501](market1501.md) | person, in-domain secondary | request | ✅ **fetched, verified and run** |
| [market1501-500k](market1501-500k.md) | +500,000 gallery distractors; a scale axis, not a difficulty one | request | downloaded, not yet linked into the Market root |
| [market1501-attribute](market1501-attribute.md) | 27 attribute labels (C16 H1) | direct | ✅ **fetched and read** |
| [msmt17](msmt17.md) | **person, in-domain primary** | request — **source is gone**, see the page | — |
| [cuhk03-np](cuhk03-np.md) | person, hard cross-domain | gdrive | — |
| [occluded-reid](occluded-reid.md) | occlusion stress | direct | ✅ **fetched and verified** |
| [ccvid](ccvid.md) | cloth-change, video | gdrive (id not yet recorded) | — |
| [veri776](veri776.md) | vehicle; **this project's evaluation oracle** | request | present, adapter ships |
| [vehicleid](vehicleid.md) | vehicle breadth | request | — |
| [veri-wild](veri-wild.md) | vehicle, hardest | request | — |
| [vrai](vrai.md) | vehicle, aerial (UAV); test labels withheld | gdrive | ✅ **fetched, verified and run** |
| [mars](mars.md) | video tracklets (C15) | gdrive | — |
| [soma](soma.md) | tracker host + synthetic set (C4) | direct | — |

`licence_verified = false` on most entries is not laziness — it means the licence text has not
been read by anyone in this project on the date recorded, and it should be read before a number
from that dataset enters a paper. Five entries are `true`: CUHK03-NP, Occluded-REID and SOMA,
whose terms were read on 2026-08-21, and VRAI and Market-1501, read on 2026-08-22 — Market's
terms ship inside its own archive, in `readme.txt`, which is why that one could be closed
without leaving the disk. Market-1501 +500k stays `false` on purpose: its archive carries no
licence text at all, and an inherited licence must not read as a verified one.
