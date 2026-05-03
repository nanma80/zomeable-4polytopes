"""Run the default-color projection search for one or more polytopes."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

import numpy as np
from polytopes import POLYTOPES
from search_engine import gen_dirs, search, group_by_shape


def run_one(polytope_name, rng=3, integer_only=False):
    embeddings = POLYTOPES[polytope_name]
    dirs = gen_dirs(rng=rng, integer_only=integer_only)
    print(f"\n########## {polytope_name}  (rng={rng}, "
          f"integer_only={integer_only}, |dirs|={len(dirs)}) ##########")
    all_hits = []
    for label, fn in embeddings:
        V, E = fn()
        print(f"\n--- embedding={label}: {len(V)} verts, {len(E)} edges ---")
        hits = search(label, V, E, dirs, verbose=False)
        print(f"  hits: {len(hits)}")
        groups = group_by_shape(hits, V, E)
        print(f"  distinct shapes: {len(groups)}")
        for fp, ex in groups.items():
            n_balls, _ = fp
            n0, sig, _ = ex[0]
            print(f"    shape: {n_balls} balls, sig={sig}, "
                  f"{len(ex)} kernel directions, e.g. n={n0}")
        all_hits.append((label, V, E, hits, groups))
    return all_hits


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_search.py <polytope_name> [rng]")
        print("  polytope_name in:", list(POLYTOPES.keys()))
        sys.exit(1)
    name = sys.argv[1]
    rng = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    run_one(name, rng=rng)
