"""Probe whether rng=3 finds new kernel directions for the regulars
beyond what rng=2 already finds.

For each (group, bitmask) regular, runs Step-1 kernel search at rng=3
and compares the dedup'd kernel-direction set to the cached rng=2 set.

Reports: |rng3_kernels|, |rng2_kernels|, |new in rng3 not in rng2|.

If the deltas are zero across all 8 regulars, rng=3 is unlikely to
surface novel shapes from descendants either. Otherwise, the new
directions justify a full rng=3 sweep.

Single-threaded by design (one regular at a time, one BLAS thread)
so it can run alongside the audit_h4_large probe without contention.
"""
from __future__ import annotations

import os
# Cap BLAS threads to avoid contending with audit_h4_large.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import time
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from lib.search_engine import gen_dirs, search  # type: ignore
from lib import wythoff  # type: ignore


REGULARS = [
    ("A4", (1, 0, 0, 0), "5-cell"),
    ("A4", (0, 0, 0, 1), "5-cell-dual"),
    ("B4", (1, 0, 0, 0), "tesseract"),
    ("B4", (0, 0, 0, 1), "16-cell"),
    ("F4", (1, 0, 0, 0), "24-cell"),
    ("F4", (0, 0, 0, 1), "24-cell-dual"),
    ("H4", (1, 0, 0, 0), "120-cell"),
    ("H4", (0, 0, 0, 1), "600-cell"),
]


def _dedup_dirs(kernels: np.ndarray) -> np.ndarray:
    """Dedup unit-vector directions modulo sign, with rounding."""
    if kernels.size == 0:
        return kernels
    keys = set()
    keep = []
    for k in kernels:
        v = np.asarray(k, dtype=float)
        n = float(np.linalg.norm(v))
        if n < 1e-9:
            continue
        u = v / n
        sig = tuple(np.round(u, 6))
        sig_neg = tuple(-x for x in sig)
        key = sig if sig <= sig_neg else sig_neg
        if key in keys:
            continue
        keys.add(key)
        keep.append(v)
    return np.array(keep) if keep else np.zeros((0, 4))


def _direction_set(kernels: np.ndarray) -> set:
    out = set()
    for k in kernels:
        v = np.asarray(k, dtype=float)
        n = float(np.linalg.norm(v))
        if n < 1e-9:
            continue
        u = v / n
        sig = tuple(np.round(u, 5))
        sig_neg = tuple(-x for x in sig)
        out.add(sig if sig <= sig_neg else sig_neg)
    return out


def main():
    print("Generating rng=2 dirs...")
    t0 = time.time()
    dirs2 = gen_dirs(rng=2, permute_dedup=False)
    print(f"  rng=2: {len(dirs2)} dirs ({time.time()-t0:.1f}s)")

    print("Generating rng=3 dirs...")
    t0 = time.time()
    dirs3 = gen_dirs(rng=3, permute_dedup=False)
    print(f"  rng=3: {len(dirs3)} dirs ({time.time()-t0:.1f}s)")

    results = []
    for grp, bm, name in REGULARS:
        print(f"\n--- {grp} {bm} {name} ---")
        V, edges = wythoff.build_polytope(grp, bm)
        print(f"  V={len(V)} E={len(edges)}")

        # rng=2
        t0 = time.time()
        hits2 = search(f"{name}_rng2", V, edges, dirs2, verbose=False)
        kernels2 = np.array([h[0] for h in hits2]) if hits2 else np.zeros((0, 4))
        ded2 = _dedup_dirs(kernels2)
        dt2 = time.time() - t0
        print(f"  rng=2: {len(hits2)} hits, {len(ded2)} dedup'd kernels ({dt2:.1f}s)")

        # rng=3
        t0 = time.time()
        hits3 = search(f"{name}_rng3", V, edges, dirs3, verbose=False)
        kernels3 = np.array([h[0] for h in hits3]) if hits3 else np.zeros((0, 4))
        ded3 = _dedup_dirs(kernels3)
        dt3 = time.time() - t0
        print(f"  rng=3: {len(hits3)} hits, {len(ded3)} dedup'd kernels ({dt3:.1f}s)")

        s2 = _direction_set(ded2)
        s3 = _direction_set(ded3)
        new = s3 - s2
        gone = s2 - s3
        print(f"  delta: rng3 has {len(new)} NEW directions; {len(gone)} gone")

        results.append({
            "group": grp,
            "bitmask": bm,
            "name": name,
            "V": len(V),
            "E": len(edges),
            "rng2_hits": len(hits2),
            "rng3_hits": len(hits3),
            "rng2_kernels": len(ded2),
            "rng3_kernels": len(ded3),
            "new_in_rng3": len(new),
            "gone_from_rng3": len(gone),
            "rng2_seconds": dt2,
            "rng3_seconds": dt3,
        })

    print("\n=== SUMMARY ===")
    print(f"{'group':<5} {'bitmask':<14} {'name':<14} {'V':>5} {'r2K':>5} {'r3K':>5} {'new':>4} {'gone':>4} {'r3_sec':>7}")
    for r in results:
        print(f"{r['group']:<5} {str(r['bitmask']):<14} {r['name']:<14} "
              f"{r['V']:>5} {r['rng2_kernels']:>5} {r['rng3_kernels']:>5} "
              f"{r['new_in_rng3']:>4} {r['gone_from_rng3']:>4} {r['rng3_seconds']:>7.1f}")

    import json
    out = ROOT / "ongoing_work" / "probe_regulars_rng3.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
