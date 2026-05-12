"""Reorganize output/ into category subfolders.

Usage:
    python ongoing_work/reorganize_output.py            # dry run
    python ongoing_work/reorganize_output.py --apply    # actually move

Moves each polytope subfolder into one of:
    output/regular/, output/uniform/, output/polyhedral_prisms/,
    output/duoprisms/, output/antiprismatic_prisms/
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "output"

REGULARS = {"5cell", "8cell", "16cell", "24cell", "120cell", "600cell"}

CATEGORY_FOLDERS = [
    "regular",
    "uniform",
    "polyhedral_prisms",
    "duoprisms",
    "antiprismatic_prisms",
]


def categorize(slug: str) -> str:
    if slug in REGULARS:
        return "regular"
    if slug.startswith("duoprism_"):
        return "duoprisms"
    if slug.endswith("_antiprismatic_prism"):
        return "antiprismatic_prisms"
    if slug.endswith("_prism"):
        return "polyhedral_prisms"
    return "uniform"


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=REPO, check=check, capture_output=True, text=True)


def find_subfolders():
    return sorted(p for p in OUT.iterdir() if p.is_dir() and p.name not in CATEGORY_FOLDERS)


def find_empty(subfolders):
    return [p for p in subfolders if not any(p.rglob("*")) or all(q.is_dir() for q in p.rglob("*"))]


def has_files(p: Path) -> bool:
    return any(q.is_file() for q in p.rglob("*"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="apply changes (else dry-run)")
    args = ap.parse_args()

    subfolders = find_subfolders()
    moves = []
    empties = []
    for sf in subfolders:
        if has_files(sf):
            cat = categorize(sf.name)
            moves.append((sf, OUT / cat / sf.name))
        else:
            empties.append(sf)

    print(f"Found {len(subfolders)} polytope subfolders.")
    print(f"  Non-empty (will move): {len(moves)}")
    print(f"  Empty (will delete): {len(empties)}")
    by_cat = {}
    for _, dest in moves:
        cat = dest.parent.name
        by_cat[cat] = by_cat.get(cat, 0) + 1
    print(f"  By category: {by_cat}")
    print()

    if not args.apply:
        print("[dry-run] add --apply to execute")
        for sf, dest in moves[:5]:
            print(f"  would: git mv {sf.relative_to(REPO)} {dest.relative_to(REPO)}")
        print(f"  ... ({len(moves)} total moves)")
        for sf in empties[:5]:
            print(f"  would: rm -rf {sf.relative_to(REPO)}")
        print(f"  ... ({len(empties)} total deletions)")
        return

    # 1. Delete empty folders (they're untracked)
    for sf in empties:
        try:
            sf.rmdir()
            print(f"  rmdir {sf.relative_to(REPO)}")
        except OSError as e:
            print(f"  WARN: rmdir failed for {sf}: {e}")

    # 2. Create category folders
    for cat in CATEGORY_FOLDERS:
        (OUT / cat).mkdir(exist_ok=True)

    # 3. git mv each non-empty folder
    for sf, dest in moves:
        rel_src = str(sf.relative_to(REPO)).replace("\\", "/")
        rel_dest = str(dest.relative_to(REPO)).replace("\\", "/")
        res = git("mv", rel_src, rel_dest, check=False)
        if res.returncode != 0:
            print(f"  git mv failed: {res.stderr.strip()}; trying os move")
            sf.rename(dest)
        else:
            print(f"  git mv {rel_src} -> {rel_dest}")

    print(f"\nDone. {len(moves)} moved, {len(empties)} deleted.")


if __name__ == "__main__":
    main()
