"""Sanity check: snub 24-cell + grand antiprism non-Wythoff sweep
integration finds the 4 hand-picked master kernels.

This is a self-contained verification of the NON_WYTHOFF wiring in
tools/run_wythoff_sweep.py.  Loads the cached H4 rng=2 kernel set
(ongoing_work/kernels_H4_rng2.npy) and runs the search engine on
each non-Wythoff polytope.  Asserts that the 4 master kernels (the
ones already on `main` as `output/snub24cell/*.vZome` and
`output/grand_antiprism/*.vZome`) are among the hits — at least up
to direction equivalence (positive scalar multiples are the same
projection direction).

NOTE: kernels_H4_rng2.npy was generated 2026-05-03 00:29 (432 kernels),
*before* the vectorisation rewrite of `_try_align` in commit f18f2e7
(2026-05-03 01:33).  Empirically the older code missed the
(phi^2, phi, 1, 0) zomeable direction of the 600-cell, so the vertex-
first snub-24-cell master kernel is absent from the cache.  Direct test
on the current code shows the 600-cell IS zomeable along that direction
(75 balls, R=288 B=180 Y=240 _=12).  Regenerate the cache (delete the
.npy file then run with --rng 2) before relying on this sweep for
completeness; tracked under todo `kernel-completeness-fix`.
"""
import sys, time
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "lib"))

from polytopes import snub_24cell, grand_antiprism
from search_engine import search

PHI = (1.0 + 5.0 ** 0.5) / 2.0

# Master kernels that the sweep MUST find (per output/snub24cell/RESULTS.md
# and output/grand_antiprism/RESULTS.md).
MASTERS = {
    "snub 24-cell": [
        ("cell-first",   np.array([1.0,        0.0, 0.0, 0.0])),
        ("vertex-first", np.array([PHI ** 2,   PHI, 1.0, 0.0])),
    ],
    "grand antiprism": [
        ("vertex-first", np.array([1.0, 1.0, 1.0, 1.0])),
        ("ring-first",   np.array([1.0, 0.0, 0.0, 0.0])),
    ],
}

LOADERS = {"snub 24-cell": snub_24cell, "grand antiprism": grand_antiprism}


def direction_eq(u, v, tol=1e-6):
    """True if u and v point in the same direction up to positive
    scaling (equivalently, same projection hyperplane)."""
    u = np.asarray(u, dtype=float)
    v = np.asarray(v, dtype=float)
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu < 1e-12 or nv < 1e-12:
        return nu < 1e-12 and nv < 1e-12
    return abs(abs(u @ v) / (nu * nv) - 1.0) < tol


def main():
    print(f"Loading H4 canonical cell600 rng=2 kernel cache...")
    K = np.load(ROOT / "ongoing_work" / "kernels_H4_canon600_rng2.npy")
    kernels = [K[i] for i in range(len(K))]
    print(f"  loaded {len(kernels)} kernels")
    print()

    all_ok = True
    for name, masters in MASTERS.items():
        print("=" * 70)
        print(f"  {name}")
        print("=" * 70)
        V, E = LOADERS[name]()
        print(f"  V={len(V)}  E={len(E)}")

        # --- a. confirm masters are in kernel set (positive direction match)
        print(f"  Master-kernel containment check:")
        for label, m in masters:
            in_set = any(direction_eq(m, k) for k in kernels)
            tag = "OK" if in_set else "MISSING"
            print(f"    {label:14s} {list(np.round(m, 4))}  [{tag}]")
            if not in_set:
                all_ok = False

        # --- b. run the search engine; check masters appear in hits
        print(f"  Running search on {len(kernels)} kernels...")
        t0 = time.time()
        hits = search(name, V, E, kernels, verbose=False)
        dt = time.time() - t0
        hit_kernels = [np.array(n) for (n, sig, balls) in hits]
        print(f"  {len(hits)} hits in {dt:.1f}s")
        print(f"  Master-kernel hit-set check:")
        for label, m in masters:
            in_hits = any(direction_eq(m, k) for k in hit_kernels)
            tag = "FOUND" if in_hits else "MISS!"
            print(f"    {label:14s} {list(np.round(m, 4))}  [{tag}]")
            if not in_hits:
                all_ok = False
        print()

    print("=" * 70)
    print("RESULT:", "all 4 master kernels found" if all_ok else "FAILURES above")
    print("=" * 70)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
