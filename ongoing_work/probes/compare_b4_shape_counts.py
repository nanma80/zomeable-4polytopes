"""Compare per-polytope shape counts: manifest vs old sweep vs new sweep."""
import json
from collections import defaultdict

m = json.load(open("output/wythoff_sweep/manifest.json"))
by_pol = defaultdict(set)
for s in m["shapes"]:
    if s["group"] == "B4":
        key = tuple(s["bitmask"])
        by_pol[key].add(s["fp_hash"])

OLD = {  # from sweep_log_rng2_B4_backfill.txt
    (1,0,0,0): 32, (0,1,0,0): 3, (1,1,0,0): 3, (0,0,1,0): 2,
    (1,0,1,0): 3, (0,1,1,0): 3, (1,1,1,0): 3, (0,0,0,1): 3,
    (1,0,0,1): 3, (0,1,0,1): 2, (1,1,0,1): 3, (0,0,1,1): 3,
    (1,0,1,1): 3, (0,1,1,1): 2, (1,1,1,1): 3,
}
NEW = {  # from sweep_log_rng2_B4_kernel_completeness.txt
    (1,0,0,0): 31, (0,1,0,0): 6, (1,1,0,0): 3, (0,0,1,0): 3,
    (1,0,1,0): 3, (0,1,1,0): 6, (1,1,1,0): 3, (0,0,0,1): 6,
    (1,0,0,1): 3, (0,1,0,1): 4, (1,1,0,1): 3, (0,0,1,1): 6,
    (1,0,1,1): 3, (0,1,1,1): 4, (1,1,1,1): 3,
}

print(f"{'bitmask':14s} {'manifest':>9s} {'old':>5s} {'new':>5s} {'delta':>6s}")
for bm in sorted(OLD):
    mf = len(by_pol[bm])
    o = OLD[bm]
    n = NEW[bm]
    star = " <-- match" if n == mf else (" *MISMATCH*" if n != mf else "")
    print(f"  {str(bm):12s}  {mf:>9d} {o:>5d} {n:>5d} {n-o:>6d}{star}")
