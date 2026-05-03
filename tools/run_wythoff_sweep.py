"""Run the Wythoff sweep over all 47 convex uniform 4-polytopes.

Strategy (rep-theoretic shortcut):
  For each Coxeter group G in {A4, B4, F4, H4}, the zomeable kernel
  directions of any G-Wythoff polytope must lie among those of the
  regular G-polytope (the bitmask 1000 form), as shown empirically for
  the regular cases.  So we:

  1. Find the working kernels for each regular polytope at moderate
     range (rng=3).
  2. For every (group, bitmask), test only those kernels against the
     polytope's vertex/edge data.
  3. Group hits by shape fingerprint.
  4. Print the census.

Usage:
    python -m tools.run_wythoff_sweep [--rng N]
"""
import sys
import os
import time
import argparse
from collections import defaultdict

# Allow running as a module or directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from wythoff import build_polytope
from uniform_polytopes import all_uniform_polytopes, KNOWN_DUPLICATES
from search_engine import gen_dirs, search, group_by_shape


GROUPS = ("A4", "B4", "F4", "H4")
REGULAR_BITMASK = (1, 0, 0, 0)


def find_group_kernels(group, rng):
    """Find the kernel directions that yield zomeable projections for
    the regular polytope of `group`.  Returns a list of tuples (n, V, E)."""
    V, E = build_polytope(group, REGULAR_BITMASK)
    dirs = gen_dirs(rng=rng, integer_only=False, permute_dedup=False)
    print(f"  [{group}] regular: |V|={len(V)}, |E|={len(E)}, "
          f"trying {len(dirs)} dirs...")
    t0 = time.time()
    import numpy as np
    hits = search(group + "_regular", V, E, dirs, verbose=False)
    print(f"  [{group}] {len(hits)} hits in {time.time()-t0:.1f}s")
    return [np.array(n) for (n, sig, balls) in hits]


def test_polytope_against_kernels(group, bitmask, name, kernels):
    """For each kernel direction in `kernels`, test whether projecting
    `(group, bitmask)` produces a zomeable image.  Returns hit list."""
    V, E = build_polytope(group, bitmask)
    # Re-run the search machinery on these kernels only.
    hits = search(name, V, E, kernels, verbose=False)
    groups = group_by_shape(hits, V, E)
    return V, E, hits, groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rng", type=int, default=3,
                    help="kernel-direction range for the regular-polytope search")
    args = ap.parse_args()

    # 1. Find kernels for each regular
    print("=" * 70)
    print("Step 1: kernels of regular polytopes")
    print("=" * 70)
    group_kernels = {}
    for g in GROUPS:
        group_kernels[g] = find_group_kernels(g, args.rng)
    print()

    # 2. Test all Wythoff combos
    print("=" * 70)
    print("Step 2: test each Wythoff combo against group kernels")
    print("=" * 70)
    results = []
    for group, b, name in all_uniform_polytopes():
        if (group, b) in KNOWN_DUPLICATES:
            results.append((group, b, name, "DUP", None, None, None))
            continue
        kernels = group_kernels[group]
        t0 = time.time()
        try:
            V, E, hits, shape_groups = test_polytope_against_kernels(
                group, b, name, kernels)
        except RuntimeError as e:
            results.append((group, b, name, f"ERR: {e}", None, None, None))
            continue
        dt = time.time() - t0
        print(f"  {group} {b}  {name:30s}  V={len(V):5d} E={len(E):5d}  "
              f"hits={len(hits):4d}  shapes={len(shape_groups)}  ({dt:.1f}s)")
        results.append((group, b, name, len(V), len(E), len(hits),
                        shape_groups))

    # 3. Census
    print()
    print("=" * 70)
    print("Step 3: census")
    print("=" * 70)
    print(f"{'group':4s} {'bitmask':10s} {'name':30s} {'V':>5s} {'E':>5s} "
          f"{'hits':>5s} {'shapes':>7s}")
    total_shapes = 0
    for r in results:
        group, b, name = r[:3]
        if r[3] == "DUP":
            print(f"  {group} {str(b):10s} {name:30s}  [DUP]")
            continue
        if isinstance(r[3], str):
            print(f"  {group} {str(b):10s} {name:30s}  {r[3]}")
            continue
        _, _, _, V_n, E_n, hit_n, sg = r
        print(f"  {group} {str(b):10s} {name:30s} {V_n:5d} {E_n:5d} "
              f"{hit_n:5d} {len(sg):7d}")
        total_shapes += len(sg)
    print()
    print(f"Total distinct shapes across all 47 unique Wythoff forms: "
          f"{total_shapes}")


if __name__ == "__main__":
    main()
