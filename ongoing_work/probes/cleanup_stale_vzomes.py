"""Delete stale .vZome files in prismatic corpus folders.

For each polytope folder, finds files NOT referenced by the current manifest
and verifies their signature matches one of the expected files before
deletion. Files with unique signatures (no match) are reported but NOT
deleted (manual review needed).
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
sys.path.insert(0, os.path.join(REPO_ROOT, "lib"))

from dedup_corpus_by_shape import parse_vzome, shape_signature  # noqa: E402


def main(dry_run: bool = False) -> None:
    m = json.load(open(os.path.join(REPO_ROOT, "output", "prismatic_manifest.json")))
    deleted = 0
    unique_stale = []
    for fam, polys in m.get("families", {}).items():
        for p in polys:
            shapes = p.get("shapes", [])
            if not shapes:
                continue
            folder = os.path.dirname(shapes[0]["path"])
            folder_abs = Path(REPO_ROOT) / folder
            if not folder_abs.is_dir():
                continue
            expected = {s["basename"] + ".vZome" for s in shapes}
            # Build sig table from expected (existing) files
            exp_sigs = {}
            for s in shapes:
                fp = Path(REPO_ROOT) / s["path"]
                if not fp.exists():
                    continue
                try:
                    P, E = parse_vzome(fp)
                    exp_sigs[shape_signature(P, E)] = s["path"]
                except Exception as exc:
                    print(f"  WARN parse {s['path']}: {exc}")
            for fn in sorted(os.listdir(folder_abs)):
                if not fn.endswith(".vZome"):
                    continue
                if fn in expected:
                    continue
                fp = folder_abs / fn
                try:
                    P, E = parse_vzome(fp)
                    sig = shape_signature(P, E)
                except Exception as exc:
                    print(f"  WARN parse stale {fp}: {exc}")
                    continue
                match = exp_sigs.get(sig)
                if match:
                    if dry_run:
                        print(f"  would delete {fp.relative_to(REPO_ROOT)} (== {match})")
                    else:
                        fp.unlink()
                        deleted += 1
                        print(f"  deleted     {fp.relative_to(REPO_ROOT)} (== {match})")
                else:
                    unique_stale.append(str(fp.relative_to(REPO_ROOT)))
                    print(f"  KEEP UNIQUE {fp.relative_to(REPO_ROOT)}  sig={sig[2][:12]}")
    print()
    print(f"Total deleted: {deleted}")
    print(f"Unique stale (kept for review): {len(unique_stale)}")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
