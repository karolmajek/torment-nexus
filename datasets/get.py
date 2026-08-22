#!/usr/bin/env python3
"""A runner over the dataset pages. It holds no dataset knowledge of its own.

    python datasets/get.py ls
    python datasets/get.py show msmt17
    python datasets/get.py fetch occluded-reid
    python datasets/get.py verify cuhk03-np
    python datasets/get.py verify --all
    python datasets/get.py counts msmt17          # the numbers, for pasting nowhere

Every fact about a dataset — url, licence, layout, every count — lives in exactly one place:
the ```toml block at the top of datasets/<name>.md. That page is what a human reads and what
this script parses, so there is no registry to drift out of step with the prose beside it.
A number that is not in that block is a number this project does not claim.

This file knows five things: how to find that block, how to pull an HTTPS URL, how to count
what landed on disk, how to refuse, and nothing else. Adding a dataset is a new page.

The root defaults to ./data, and $REID_DATA_ROOT overrides it. Nothing here writes outside
the root, and nothing here deletes.

Python 3.11+ (tomllib). No third-party imports; `gdown` is shelled out to if present and
merely *named* if not, because a Google Drive download this script fakes badly is worse than
one it hands to a tool that does it properly.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tomllib
import zipfile
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent

# The pages are UTF-8 and say so in em-dashes and section marks; a cp1252 console would turn
# those into replacement characters, which makes a licence warning look like corruption.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OK, WARN, BAD = "ok", "warning", "error"

FENCE = re.compile(r"^```toml\s*$(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
"""The first ```toml fence in a page is that page's data block. One convention, no parser."""


# ------------------------------------------------------------------------------- the pages


def read_page(path: Path) -> dict[str, Any]:
    """One page -> its data block. The prose around it is for humans and is not read."""
    match = FENCE.search(path.read_text(encoding="utf-8"))
    if match is None:
        raise SystemExit(f"{path} has no ```toml data block; every dataset page needs one")
    block = tomllib.loads(match.group(1))
    block.setdefault("dataset", {}).setdefault("id", path.stem)
    block["page"] = path.name
    return block


def load() -> dict[str, dict[str, Any]]:
    """Every page in this directory that carries a data block, keyed by dataset id."""
    pages: dict[str, dict[str, Any]] = {}
    for path in sorted(HERE.glob("*.md")):
        if path.name == "README.md":
            continue
        block = read_page(path)
        if "denied" in block:
            pages["_denied"] = block
            continue
        pages[block["dataset"]["id"]] = block
    return pages


def entry(pages: dict[str, dict[str, Any]], name: str) -> dict[str, Any]:
    if name not in pages:
        known = ", ".join(sorted(k for k in pages if not k.startswith("_")))
        raise SystemExit(f"unknown dataset {name!r}\nknown: {known}")
    return pages[name]


def root_of(args: argparse.Namespace, pages: dict[str, dict[str, Any]]) -> Path:
    fallback = pages.get("_denied", {}).get("policy", {}).get("default_root", "data")
    chosen = args.root or os.environ.get("REID_DATA_ROOT") or fallback
    return Path(chosen).expanduser().resolve()


def denied_ids(pages: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return pages.get("_denied", {}).get("denied", {})


def is_denied(pages: dict[str, dict[str, Any]], name: str) -> bool:
    return name.lower() in {i.lower() for i in denied_ids(pages).get("ids", [])}


def missing(page: dict[str, Any], root: Path) -> list[str]:
    """What the page says the release contains and the disk does not have.

    Presence, not counts — `verify` does counts. The distinction matters because two pages
    can name the same `dir` and differ by one entry inside it, which is exactly what
    Market-1501 and its +500k gallery do: the root being there is not the dataset being
    there.
    """
    base = root / page["dataset"]["dir"]
    if not base.is_dir():
        return [str(base)]
    wanted = page.get("expect", {})
    return [str(base / name) for name in wanted if not (base / name).exists()]


# ------------------------------------------------------------------------------- reporting


def say(level: str, message: str) -> None:
    mark = {OK: "  ok  ", WARN: " warn ", BAD: " FAIL "}[level]
    print(f"[{mark}] {message}")


def _flatten(node: Any, prefix: str = "") -> list[tuple[str, Any]]:
    """Nested count tables -> dotted rows, so `counts` prints whatever a page happens to carry."""
    rows: list[tuple[str, Any]] = []
    for key, value in node.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            rows.extend(_flatten(value, f"{name}."))
        else:
            rows.append((name, value))
    return rows


# ----------------------------------------------------------------------------------- verbs


def cmd_ls(args: argparse.Namespace) -> int:
    pages = load()
    root = root_of(args, pages)
    header = ("dataset", "kind", "access", "comm", "on disk", "page")
    rows = []
    for name in sorted(k for k in pages if not k.startswith("_")):
        item = pages[name]["dataset"]
        present = not missing(pages[name], root)
        rows.append(
            (
                name,
                item.get("kind", ""),
                item.get("access", ""),
                "yes" if item.get("commercial_ok") else "no",
                "present" if present else "-",
                pages[name]["page"],
            )
        )
    widths = [max(len(str(r[i])) for r in [header, *rows]) for i in range(len(header))]
    print("  ".join(h.ljust(w) for h, w in zip(header, widths)))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print("  ".join(str(c).ljust(w) for c, w in zip(row, widths)))
    print(f"\nroot: {root}")
    denied = denied_ids(pages)
    print(f"denied: {', '.join(denied.get('ids', []))}\n  {denied.get('reason', '')}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    pages = load()
    if is_denied(pages, args.name):
        return _refuse(pages, args.name)
    block = entry(pages, args.name)
    item = block["dataset"]
    root = root_of(args, pages)
    print(f"{item['name']}  ({args.name})   ->  datasets/{block['page']}")
    print(f"  role        {item.get('role', '')}")
    print(f"  licence     {item.get('licence', '')}")
    print(f"              licence_verified={item.get('licence_verified')} commercial_ok={item.get('commercial_ok')}")
    print(f"  access      {item.get('access')}   link_verified={item.get('link_verified')} (checked {item.get('checked_on')})")
    print(f"  homepage    {item.get('homepage', '')}")
    absent = missing(block, root)
    print(f"  on disk     {root / item['dir']}   {'present' if not absent else 'MISSING'}")
    for path in absent:
        print(f"              missing: {path}")
    print(f"  reidbench   adapter={item.get('adapter') or '(none yet)'}  protocols={item.get('protocols') or []}")
    for url in block.get("fetch", {}).get("urls", []):
        print(f"  url         {url}")
    if block.get("fetch", {}).get("gdrive_id"):
        print(f"  gdrive      {block['fetch']['gdrive_id']}")
    if block.get("fetch", {}).get("sha256"):
        print(f"  sha256      {block['fetch']['sha256']}")
    if block.get("counts"):
        print("\n  counts")
        for key, value in _flatten(block["counts"]):
            print(f"    {key:<28} {value:>10,}" if isinstance(value, int) else f"    {key:<28} {value}")
    if block.get("fetch", {}).get("manual"):
        print("\n" + block["fetch"]["manual"].strip())
    return 0


def cmd_counts(args: argparse.Namespace) -> int:
    """The numbers, so nothing else has to hold a copy of them."""
    pages = load()
    block = entry(pages, args.name)
    for key, value in _flatten(block.get("counts", {})):
        print(f"{key:<32} {value:>12,}" if isinstance(value, int) else f"{key:<32} {value}")
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    pages = load()
    if is_denied(pages, args.name):
        return _refuse(pages, args.name)
    block = entry(pages, args.name)
    item, fetch = block["dataset"], block.get("fetch", {})
    root = root_of(args, pages)
    target = root / item["dir"]
    access = item.get("access")

    if target.is_dir() and not args.force:
        say(OK, f"{target} already exists; nothing to do (--force to fetch anyway)")
        return 0

    if access == "request":
        say(WARN, f"{item['name']} cannot be automated: it needs a signed agreement or an email.")
        print(f"\n  homepage: {item.get('homepage')}\n")
        print((fetch.get("manual") or "").strip())
        print(f"\n  when it arrives, unpack it to: {target}")
        return 2

    downloads = root / "_downloads"
    downloads.mkdir(parents=True, exist_ok=True)

    if access == "gdrive":
        return _fetch_gdrive(item, fetch, downloads, target)
    if access == "direct":
        return _fetch_direct(item, fetch, downloads, target)

    say(BAD, f"unknown access kind {access!r} for {args.name}")
    return 1


def cmd_verify(args: argparse.Namespace) -> int:
    pages = load()
    root = root_of(args, pages)
    names = sorted(k for k in pages if not k.startswith("_")) if args.all else [args.name]
    worst = 0

    for name in names:
        block = entry(pages, name)
        item = block["dataset"]
        base = root / item["dir"]
        print(f"\n{item['name']}  ->  {base}")
        if not base.is_dir():
            say(WARN, "not on disk")
            continue
        expect = block.get("expect", {})
        if not expect:
            say(WARN, "the page records no expected counts; presence is all that can be checked")
            continue
        for relative, wanted in expect.items():
            got = _count(base / relative)
            if got is None:
                say(BAD, f"{relative}: missing")
                worst = max(worst, 1)
            elif got != wanted:
                say(BAD, f"{relative}: {got}, expected {wanted}  (datasets/{block['page']})")
                worst = max(worst, 1)
            else:
                say(OK, f"{relative}: {got}")

    for denied in denied_ids(pages).get("ids", []):
        for found in root.glob(f"**/*{denied}*"):
            say(BAD, f"DENIED dataset present on disk: {found}")
            print(f"         {denied_ids(pages).get('reason')}")
            worst = max(worst, 1)

    return worst


# ------------------------------------------------------------------------------- machinery


def _refuse(pages: dict[str, dict[str, Any]], name: str) -> int:
    denied = denied_ids(pages)
    say(BAD, f"{name} is denied and this script will not fetch, locate or describe it.")
    print(f"  reason: {denied.get('reason')}")
    print(f"  use instead: {denied.get('use_instead')}")
    print("  There is no override flag. If you need one, the answer is a different dataset.")
    return 3


IGNORED = {"Thumbs.db", ".DS_Store"}
"""Not data. The Market-1501 archive genuinely ships four `Thumbs.db` files, so counting
directory entries naively puts every `expect` in that page one over — a page correction for
something no dataset author meant to release."""


def _count(path: Path) -> int | None:
    """Entries in a directory, or lines in a .txt file. One rule, decided by the path."""
    if path.suffix == ".txt":
        if not path.is_file():
            return None
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return sum(1 for line in handle if line.strip())
    if not path.is_dir():
        return None
    return sum(1 for entry in path.iterdir() if entry.name not in IGNORED)


def _download(url: str, into: Path) -> Path:
    name = url.rstrip("/").split("/")[-1] or "download"
    destination = into / name
    if destination.exists():
        say(OK, f"already downloaded: {destination}")
        return destination

    say(OK, f"GET {url}")
    request = Request(url, headers={"User-Agent": "torment-nexus-datasets/1"})
    digest = hashlib.sha256()
    temporary = destination.with_suffix(destination.suffix + ".part")
    with urlopen(request) as response, temporary.open("wb") as handle:  # noqa: S310
        total = int(response.headers.get("Content-Length") or 0)
        seen = 0
        while chunk := response.read(1 << 20):
            handle.write(chunk)
            digest.update(chunk)
            seen += len(chunk)
            if total:
                print(f"\r      {seen / 1e6:8.1f} / {total / 1e6:.1f} MB", end="", flush=True)
        print()
    temporary.rename(destination)
    say(OK, f"sha256 {digest.hexdigest()}  <- record it on the page")
    return destination


def _extract(archive: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    say(OK, f"extracting {archive.name} -> {target}")
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.namelist():
                if member.startswith(("/", "..")) or ".." in Path(member).parts:
                    raise SystemExit(f"refusing path-traversing member {member!r} in {archive}")
            bundle.extractall(target)
        return
    if archive.suffixes[-2:] in ([".tar", ".gz"], [".tar", ".bz2"]) or archive.suffix == ".tar":
        with tarfile.open(archive) as bundle:
            for member in bundle.getmembers():
                if member.name.startswith(("/", "..")) or ".." in Path(member.name).parts:
                    raise SystemExit(f"refusing path-traversing member {member.name!r}")
            bundle.extractall(target)
        return
    say(WARN, f"{archive.name} is not an archive this script unpacks; it is in {archive.parent}")


def _fetch_direct(
    item: dict[str, Any], fetch: dict[str, Any], downloads: Path, target: Path
) -> int:
    urls = fetch.get("urls") or []
    if not urls:
        say(BAD, f"{item['id']} is marked access=direct but its page records no urls")
        return 1
    for url in urls:
        archive = _download(url, downloads)
        if archive.suffix in {".zip", ".tar", ".gz", ".bz2"}:
            _extract(archive, target)
        else:
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy2(archive, target / archive.name)
    say(OK, f"{item['name']} is in {target}")
    print(f"      now run:  python datasets/get.py verify {item['id']}")
    return 0


def _fetch_gdrive(
    item: dict[str, Any], fetch: dict[str, Any], downloads: Path, target: Path
) -> int:
    file_id = fetch.get("gdrive_id")
    if not file_id:
        say(WARN, f"{item['id']}'s page records no gdrive_id yet.")
        print((fetch.get("manual") or "").strip())
        return 2

    url = f"https://drive.google.com/uc?id={file_id}"
    if shutil.which("gdown") is None:
        say(WARN, "gdown is not on PATH, and this script will not imitate it.")
        print(f"\n  pip install gdown && gdown {file_id} -O {downloads}\n  or open: {url}")
        print(f"  then unpack into: {target}")
        return 2

    say(OK, f"gdown {file_id}")
    result = subprocess.run(["gdown", file_id, "-O", str(downloads)], check=False)  # noqa: S603, S607
    if result.returncode != 0:
        say(BAD, f"gdown exited {result.returncode}; large Drive files sometimes need a browser")
        print(f"  open: {url}")
        return result.returncode

    archives = sorted(downloads.glob("*.zip")) + sorted(downloads.glob("*.tar*"))
    if not archives:
        say(WARN, f"nothing archive-shaped landed in {downloads}; unpack it into {target} yourself")
        return 2
    _extract(max(archives, key=lambda p: p.stat().st_mtime), target)
    print(f"      now run:  python datasets/get.py verify {item['id']}")
    return 0


# ------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="get.py", description=__doc__.split("\n")[0])
    parser.add_argument("--root", help="data root; default $REID_DATA_ROOT or ./data")
    sub = parser.add_subparsers(dest="verb", required=True)

    sub.add_parser("ls", help="every dataset, its licence posture and whether it is on disk")

    show = sub.add_parser("show", help="everything one dataset's page declares")
    show.add_argument("name")

    counts = sub.add_parser("counts", help="one dataset's numbers, so nothing else copies them")
    counts.add_argument("name")

    fetch = sub.add_parser("fetch", help="download what can be downloaded; say what cannot")
    fetch.add_argument("name")
    fetch.add_argument("--force", action="store_true", help="fetch even if the target exists")

    verify = sub.add_parser("verify", help="check the layout and the counts on disk")
    verify.add_argument("name", nargs="?")
    verify.add_argument("--all", action="store_true")

    args = parser.parse_args(argv)
    if args.verb == "verify" and not args.all and not args.name:
        parser.error("verify needs a dataset name or --all")

    verbs = {"ls": cmd_ls, "show": cmd_show, "counts": cmd_counts, "fetch": cmd_fetch, "verify": cmd_verify}
    return verbs[args.verb](args)


if __name__ == "__main__":
    sys.exit(main())
