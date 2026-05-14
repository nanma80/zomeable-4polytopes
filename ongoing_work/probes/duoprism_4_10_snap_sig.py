"""Ground-truth (a,b,0,0)-plane snap probe for duoprism_4_10.

Bypasses lossy shape_fingerprint in group_by_shape; instead computes
robust shape_signature (5-decimal + SHA-256) directly on each
successfully-snapped 3D vertex set. Counts distinct signatures.

This is the definitive test for "is duoprism_4_10 an inf-family?"
"""
from __future__ import annotations

import hashlib
import os
import sys
import time
from collections import Counter
from itertools import product

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "lib"))

from polytopes_prismatic import duoprism  # noqa: E402
from search_engine import phi, projection_matrix, _try_align  # noqa: E402
from emit_generic import _snap_coords, _dedup_balls, PHI_F  # noqa: E402


def shape_signature(P, E, dist_decimals=5, edge_decimals=5):
    """Robust 5-decimal + SHA-256 sig (same as tools/dedup_corpus_by_shape.py)."""
    sq = (P * P).sum(axis=1)
    D2 = sq[:, None] + sq[None, :] - 2.0 * (P @ P.T)
    iu = np.triu_indices(len(P), k=1)
    d2 = np.sort(D2[iu])
    pos = d2[d2 > 1e-9]
    if pos.size == 0:
        return (len(P), len(E), "degenerate")
    s_min = float(pos[0])
    d2n = np.round(d2 / s_min, dist_decimals)
    L = np.array([float(np.linalg.norm(P[i] - P[j])) for i, j in E])
    L_min = float(L.min()) if L.size else 1.0
    L_norm = np.round(L / L_min, edge_decimals)
    edge_ms = tuple(sorted(Counter(L_norm.tolist()).items()))
    h = hashlib.sha256(d2n.tobytes()).hexdigest()[:16]
    return (len(P), len(E), h, edge_ms)


def gen_2d_dirs(rng):
    vals = sorted({round(a + b * phi, 9)
                   for a in range(-rng, rng + 1)
                   for b in range(-rng, rng + 1)})
    out = set()
    for n0, n1 in product(vals, repeat=2):
        if n0 == 0 and n1 == 0:
            continue
        sgn = 1 if n0 > 0 else (-1 if n0 < 0 else (1 if n1 > 0 else -1))
        out.add((sgn * n0, sgn * n1, 0.0, 0.0))
    return [np.array(v) for v in out]


def _default_scales():
    sqrt2 = 2.0 ** 0.5
    sqrt5 = 5.0 ** 0.5
    bases = [1.0, sqrt2, sqrt5, sqrt2 * sqrt5, PHI_F, PHI_F * sqrt2,
             PHI_F * sqrt5, sqrt2 / PHI_F, sqrt5 / PHI_F,
             PHI_F ** 2, 1.0 / PHI_F]
    ks = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20]
    out = []
    for b in bases:
        for k in ks:
            out.append(b * k)
            out.append(b / k)
    return out


SWAP_YZ = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)


def snap_test(V4, edges, n, scales):
    """Run full snap pipeline; return (P3_dedup, E_dedup) on success, else None."""
    n = np.asarray(n, dtype=float)
    Q = projection_matrix(n)
    P3 = (Q @ V4.T).T
    edges_dirs = (Q @ np.array([V4[b] - V4[a] for a, b in edges]).T)
    res = _try_align(edges_dirs)
    if res is None:
        return None
    R, _classes = res
    P3rot = (R @ P3.T).T
    P3rot = (SWAP_YZ @ P3rot.T).T
    s, snapped = _snap_coords(P3rot, scales)
    if snapped is None:
        return None
    uniq, idx_map = _dedup_balls(snapped)
    # Convert GF (a, b) tuples to floats: value = a + b*phi
    P_uniq = np.array([[float(c.a) + float(c.b) * PHI_F for c in p] for p in uniq])
    new_edges = set()
    for i, j in edges:
        a, b = idx_map[i], idx_map[j]
        if a == b:
            continue
        new_edges.add((min(a, b), max(a, b)))
    return P_uniq, sorted(new_edges)


def main():
    V, edges = duoprism(4, 10)
    print(f"=== duoprism_4_10 (a,b,0,0) snap+sig probe ===", flush=True)
    print(f"V={len(V)}, E={len(edges)}", flush=True)
    print(flush=True)
    print("rng | dirs | aligned | snapped | distinct sigs | new_at_rng | elapsed_s", flush=True)
    print("----+------+---------+---------+---------------+------------+----------", flush=True)

    scales = _default_scales()
    sigs_per_rng = {}

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rngs", type=str, default="4,5,6,7",
                    help="comma-separated rng values to probe")
    args = ap.parse_args()
    rng_list = [int(x) for x in args.rngs.split(",") if x.strip()]

    for rng in rng_list:
        dirs = gen_2d_dirs(rng)
        t0 = time.time()
        n_aligned = 0
        n_snapped = 0
        n_error = 0
        sigs = set()
        for idx, n in enumerate(dirs):
            if idx % 50 == 0:
                el = time.time() - t0
                print(f"      rng={rng} {idx}/{len(dirs)} t={el:.0f}s sigs={len(sigs)} snap={n_snapped} err={n_error}", flush=True)
            try:
                res = snap_test(V, edges, n, scales)
            except Exception as exc:
                n_error += 1
                print(f"      ERR kernel {idx} n={n.tolist()}: {exc}", flush=True)
                res = None
            if res is None:
                try:
                    Q = projection_matrix(n)
                    edges_dirs = (Q @ np.array([V[b] - V[a] for a, b in edges]).T)
                    if _try_align(edges_dirs) is not None:
                        n_aligned += 1
                except Exception:
                    n_error += 1
                continue
            n_aligned += 1
            n_snapped += 1
            P_uniq, E_uniq = res
            try:
                sig = shape_signature(P_uniq, E_uniq)
                sigs.add(sig)
            except Exception:
                n_error += 1
        elapsed = time.time() - t0
        sigs_per_rng[rng] = sigs
        prev = sigs_per_rng.get(rng - 1, set())
        new_at_this_rng = len(sigs - prev)
        print(f" {rng:>2} | {len(dirs):>4} | {n_aligned:>7} | {n_snapped:>7} | "
              f"{len(sigs):>13} | {new_at_this_rng:>10} | {elapsed:>8.1f}  "
              f"errors={n_error}", flush=True)

        # Persist per-rng sigs so per-rng processes can be aggregated later.
        import json
        out_path = os.path.join(ROOT, "ongoing_work", f"probe_4_10_sigs_rng{rng}.json")
        try:
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump({"rng": rng, "n_dirs": len(dirs), "n_aligned": n_aligned,
                           "n_snapped": n_snapped, "n_errors": n_error,
                           "elapsed_s": round(elapsed, 2),
                           "sigs": [list(s) if isinstance(s, tuple) else s
                                    for s in sorted(sigs, key=lambda x: str(x))]},
                          fh, indent=2, default=str)
            print(f"      wrote {out_path}", flush=True)
        except Exception as exc:
            print(f"      WARN failed to write sig json: {exc}", flush=True)

    print()
    print("Verdict:")
    if len(sigs_per_rng) >= 2:
        keys = sorted(sigs_per_rng.keys())
        last_two = [len(sigs_per_rng[keys[-2]]), len(sigs_per_rng[keys[-1]])]
        if last_two[1] > last_two[0]:
            print(f"  Still growing rng={keys[-2]}->{keys[-1]} ({last_two[0]} -> {last_two[1]}).")
            print(f"  duoprism_4_10 IS likely an inf-family (in (a,b,0,0) plane).")
        else:
            print(f"  Saturated rng={keys[-2]}->{keys[-1]} ({last_two[0]} -> {last_two[1]}).")
            print(f"  duoprism_4_10 appears BOUNDED at {last_two[1]} shapes.")
    else:
        print(f"  Single rng probed: {sorted(sigs_per_rng.keys())} (need 2+ to compare).")


if __name__ == "__main__":
    main()
