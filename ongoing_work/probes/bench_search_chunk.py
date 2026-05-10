"""Benchmark + regression test for the search-engine prefilter optimisation.

Compares `lib.search_engine.search()` with the production chunk=512 vs a
candidate chunk=16 in `_check_cos_pairs`.  Runs both on a fixed set of
polytopes at rng=2 and asserts the hit set is identical, then reports
wall-time speedup.

Why this is correctness-preserving: `_check_cos_pairs` is a pure
necessary-condition check on a Gram matrix.  Smaller chunk size makes
the early-exit fire earlier; the rejection criterion is unchanged.
With chunk=16 there are more Python-level iterations but each chunk
materialises a 16xK temp instead of 512xK, and rejection happens
~32x sooner at the floor case (K cosines per chunk vs 512*K).

Usage:
    python ongoing_work/probes/bench_search_chunk.py
"""
import json
import sys
import time
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

import numpy as np

import wythoff as wy
import search_engine as se


CASES = [
    # (label, group, bitmask)  -- ordered small to large
    ("A4 omnitr 5c",   "A4", (1, 1, 1, 1)),  # E=240
    ("F4 rect 24c",    "F4", (0, 1, 0, 0)),  # E=288
    ("F4 trunc 24c",   "F4", (1, 1, 0, 0)),  # E=288
    ("F4 runc 24c",    "F4", (1, 0, 0, 1)),  # E=576
    ("F4 omnitr 24c",  "F4", (1, 1, 1, 1)),  # E=1152
]


def run_one(label, group, bitmask, rng=2, chunk=512):
    """Run a full `search()` with the given chunk size; return (hits_set, elapsed)."""
    se._cos_pair_chunk_override = chunk
    V, E = wy.build_polytope(group, bitmask)
    dirs = se.gen_dirs(rng=rng)
    t0 = time.time()
    hits = se.search(label, V, E, dirs, verbose=False)
    elapsed = time.time() - t0
    # Hits are list of (n_tuple, sig_dict, n_balls); compare on n_tuple+sig+balls.
    hit_set = frozenset(
        (h[0], tuple(sorted(h[1].items())), h[2]) for h in hits
    )
    return hit_set, elapsed, len(dirs)


def main():
    print("Patching lib.search_engine._check_cos_pairs to read chunk from"
          " a module-level override (`_cos_pair_chunk_override`).")
    print()

    # Monkey-patch _check_cos_pairs to read chunk from a module-level
    # attribute, so we can test multiple chunk sizes without reloading.
    orig_chunk_val = 512  # production default

    def patched_check_cos_pairs(U, tol=1e-5):
        K = U.shape[1]
        chunk = getattr(se, "_cos_pair_chunk_override", orig_chunk_val)
        allowed = se._ALLOWED_COS
        n_allowed = len(allowed)
        for i in range(0, K, chunk):
            Ub = U[:, i:i + chunk]
            Cb = np.abs(Ub.T @ U)
            b = Ub.shape[1]
            j_idx = np.arange(K)
            i_idx = np.arange(i, i + b)[:, None]
            keep = j_idx[None, :] > i_idx
            cos_use = Cb[keep]
            if cos_use.size == 0:
                continue
            idx = np.searchsorted(allowed, cos_use)
            idx_clip = np.clip(idx, 1, n_allowed - 1)
            diff = np.minimum(np.abs(allowed[idx_clip - 1] - cos_use),
                              np.abs(allowed[idx_clip] - cos_use))
            if np.any(diff > tol):
                return False
        return True

    se._check_cos_pairs = patched_check_cos_pairs

    print(f"{'case':22s} {'K':>5s} {'ndirs':>6s} {'chunk':>6s} {'hits':>5s} {'time':>10s}")
    print("-" * 70)

    summary = []
    for label, group, bitmask in CASES:
        rng = 2
        # Warmup numpy / blas with a tiny call (avoid cold-cache bias on first case)
        # Test chunk=512 (production)
        hits_512, t_512, ndirs = run_one(label, group, bitmask, rng=rng, chunk=512)

        # Test chunk=16 (candidate)
        hits_16, t_16, _ = run_one(label, group, bitmask, rng=rng, chunk=16)

        V, E = wy.build_polytope(group, bitmask)
        K = len(E)

        same = (hits_512 == hits_16)
        speedup = t_512 / t_16 if t_16 > 0 else float('nan')

        print(f"{label:22s} {K:5d} {ndirs:6d}   512  {len(hits_512):5d}  {t_512:8.2f}s")
        print(f"{label:22s} {K:5d} {ndirs:6d}    16  {len(hits_16):5d}  {t_16:8.2f}s  {speedup:.2f}x  same={same}")
        if not same:
            print(f"  !!! HITS DIFFER !!!")
            print(f"      only in chunk=512: {sorted(hits_512 - hits_16)[:3]}")
            print(f"      only in chunk=16:  {sorted(hits_16 - hits_512)[:3]}")
        summary.append({
            "label": label, "K": K, "ndirs": ndirs,
            "n_hits_512": len(hits_512), "n_hits_16": len(hits_16),
            "t_512_s": round(t_512, 3), "t_16_s": round(t_16, 3),
            "speedup": round(speedup, 2), "hits_identical": same,
        })

    # Persist for the commit message / log.
    out = os.path.join(os.path.dirname(__file__), "..",
                       "bench_search_chunk_results.json")
    with open(os.path.normpath(out), "w") as f:
        json.dump(summary, f, indent=2)
    print()
    print(f"summary written to {os.path.normpath(out)}")
    all_ok = all(s["hits_identical"] for s in summary)
    print(f"\nALL CORRECT: {all_ok}")
    if not all_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
