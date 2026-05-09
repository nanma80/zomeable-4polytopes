"""Benchmark + regression test for the parallel-edge-class reduction in
`lib.search_engine.search()`.

Edges that are scalar multiples of each other in 4D contribute zero
information to either the `_check_cos_pairs` necessary-condition test
(intra-class pairs are always |1.0| -> always allowed) or to the
classify-each-edge loop in `_try_align` (`_classify_dir` only depends
on direction, so all class members get the same axis label).  Hence
keeping one representative per parallel class is *lossless*: the hit
set for a given polytope at a given rng must be identical to the
pre-optimization hit set.

This probe runs the new `search()` (parallel-edge reduction enabled)
against a saved-vs-recomputed comparison.  Specifically:

  1. For a small set of polytopes (5cell omnitr, 24-cell rect/trunc/
     runc/omnitr), runs the new `search()` and snapshots the hit set.
  2. Runs a "reference" version that monkey-patches search to bypass
     the reduction (one rep per actual edge).  Asserts hits identical.
  3. Reports speedup.

Usage:
    python ongoing_work/probes/bench_parallel_edge_reduction.py
"""
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

import numpy as np

import wythoff as wy
import search_engine as se


CASES = [
    ("A4 omnitr 5c",   "A4", (1, 1, 1, 1)),
    ("F4 rect 24c",    "F4", (0, 1, 0, 0)),
    ("F4 trunc 24c",   "F4", (1, 1, 0, 0)),
    ("F4 runc 24c",    "F4", (1, 0, 0, 1)),
    ("F4 omnitr 24c",  "F4", (1, 1, 1, 1)),
]


def hits_to_set(hits):
    """Hits are list of (n_tuple, sig_dict, n_balls)."""
    return frozenset(
        (h[0], tuple(sorted(h[1].items())), h[2]) for h in hits
    )


def search_no_reduction(rep_name, V, edges, dirs, tol=1e-5, verbose=False):
    """Reference: search() without parallel-edge reduction (every edge
    is its own class)."""
    found = []
    t0 = time.time()
    E = np.array([V[b] - V[a] for (a, b) in edges]).T
    for n in dirs:
        if np.linalg.norm(n) < 1e-9:
            continue
        Q = se.projection_matrix(n)
        P = Q @ E
        res = se._try_align(P, tol=tol)
        if res is None:
            continue
        R, classes = res
        sig = dict(Counter(classes))
        Vp = (Q @ V.T).T
        balls = set(tuple(np.round(p, 4)) for p in Vp)
        found.append((tuple(np.round(n, 6)), sig, len(balls)))
    return found, time.time() - t0


def main():
    print(f"{'case':22s} {'K_full':>7s} {'K_reps':>7s} {'reduction':>10s} "
          f"{'ndirs':>6s} {'hits':>5s} {'t_red':>8s} {'t_ref':>8s} {'speedup':>8s} ok")
    print("-" * 110)

    summary = []
    for label, group, bitmask in CASES:
        V, E = wy.build_polytope(group, bitmask)
        K_full = len(E)
        # Direction-class count
        Earr = np.array([V[b] - V[a] for (a, b) in E]).T
        rep_idx, _ = se._edge_dir_classes(Earr)
        K_reps = len(rep_idx)
        rng = 2
        dirs = se.gen_dirs(rng=rng)

        # New (reduced) path
        t0 = time.time()
        hits_new = se.search(label, V, E, dirs, verbose=False)
        t_new = time.time() - t0
        hs_new = hits_to_set(hits_new)

        # Reference (no reduction) path
        hits_ref, t_ref = search_no_reduction(
            label, V, E, dirs, verbose=False
        )
        hs_ref = hits_to_set(hits_ref)

        same = (hs_new == hs_ref)
        speedup = t_ref / t_new if t_new > 0 else float('nan')
        red_pct = 100.0 * K_reps / max(K_full, 1)

        ok = "OK" if same else "FAIL"
        print(f"{label:22s} {K_full:7d} {K_reps:7d} {red_pct:9.1f}% "
              f"{len(dirs):6d} {len(hits_new):5d} "
              f"{t_new:7.2f}s {t_ref:7.2f}s {speedup:7.2f}x  {ok}")
        if not same:
            print(f"    !!! HIT-SET MISMATCH !!!")
            print(f"    only-in-new: {sorted(hs_new - hs_ref)[:3]}")
            print(f"    only-in-ref: {sorted(hs_ref - hs_new)[:3]}")
        summary.append({
            "label": label, "K_full": K_full, "K_reps": K_reps,
            "ndirs": len(dirs), "n_hits": len(hits_new),
            "t_new_s": round(t_new, 3), "t_ref_s": round(t_ref, 3),
            "speedup": round(speedup, 2), "ok": same,
        })

    out = ROOT / "ongoing_work" / "bench_parallel_edge_reduction_results.json"
    out.write_text(json.dumps(summary, indent=2))
    print(f"\nsummary written to {out}")
    all_ok = all(s["ok"] for s in summary)
    print(f"\nALL CORRECT: {all_ok}")
    if not all_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
