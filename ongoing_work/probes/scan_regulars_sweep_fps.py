"""Scan all existing sweep JSONLs for regular polytopes and report
their fp_hash counts, to see which regulars have shapes not yet in
master corpus or manifest.
"""
import json
import os
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(ROOT)

REGULARS = {
    ("A4", (1, 0, 0, 0)): "5cell",
    ("A4", (0, 0, 0, 1)): "5cell",
    ("B4", (1, 0, 0, 0)): "8cell",
    ("B4", (0, 0, 0, 1)): "16cell",
    ("F4", (1, 0, 0, 0)): "24cell",
    ("F4", (0, 0, 0, 1)): "24cell",
    ("H4", (1, 0, 0, 0)): "120cell",
    ("H4", (0, 0, 0, 1)): "600cell",
}

files = list((ROOT / "ongoing_work").glob("shapes_rng2*.jsonl"))
agg: dict[tuple, set[str]] = defaultdict(set)
for f in files:
    with f.open() as fh:
        for line in fh:
            rec = json.loads(line)
            key = (rec["group"], tuple(rec["bitmask"]))
            if key in REGULARS:
                for sh in rec["shapes"]:
                    agg[key].add(sh["fp_hash"])

print("Regular polytope sweep fp_hash counts:")
for key, master_dir in REGULARS.items():
    grp, bm = key
    fps = agg.get(key, set())
    print(f"  {grp} {bm} master={master_dir}: {len(fps)} fp_hashes "
          f"in sweep results")
    for fp in sorted(fps):
        print(f"    {fp}")
