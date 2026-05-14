"""Test whether duoprism_4_6 forms an inf-family on the (a,b,0,0) kernel plane.

Hypothesis: all zomeable kernels for duoprism_4_6 have the form
(a, b, 0, 0) with (a, b) in ZZ[phi]^2 (i.e., kernel lies entirely
in the {4}-plane, leaving the {6}-plane fixed). If so, the count of
distinct shape_signatures should grow roughly linearly in the kernel
search range rng. If finite, it's sporadic.

For each rng in {1, 2, 3, 4, 5, 6}:
  - enumerate (a, b, 0, 0) kernels with |a|, |b| coefficients <= rng
  - run the zomeable-alignment test
  - compute shape_signature on the projected vertex set
  - count unique signatures (= distinct shapes up to congruence)

Reports growth and prints a representative kernel for each new shape.
"""
import sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "lib"))

import numpy as np
from itertools import product
from collections import Counter, defaultdict
import hashlib

from lib.polytopes_prismatic import duoprism
from lib.search_engine import projection_matrix, _try_align, phi

# shape_signature copied from tools/dedup_corpus_by_shape.py
def shape_signature(P, E, dist_decimals=5, edge_decimals=5):
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
    """All (a + b*phi, 0, 0, 0) and (0, c + d*phi, 0, 0) etc kernels with
    rng-bounded ZZ[phi] coords. Returns 4-tuples (n0, n1, 0, 0) where
    n0, n1 are in ZZ[phi] with int coefficients |a|, |b| <= rng.
    Excludes (0,0,0,0) and duplicates by sign flip (n and -n same direction).
    """
    vals = sorted({round(a + b * phi, 9) for a in range(-rng, rng + 1)
                                          for b in range(-rng, rng + 1)})
    out = set()
    for n0, n1 in product(vals, repeat=2):
        if n0 == 0 and n1 == 0:
            continue
        # sign canonicalisation: first nonzero positive
        if n0 != 0:
            sgn = 1 if n0 > 0 else -1
        else:
            sgn = 1 if n1 > 0 else -1
        t = (sgn * n0, sgn * n1, 0.0, 0.0)
        out.add(t)
    return [np.array(v) for v in out]


def test_kernel(V4, edges, n, tol=1e-5):
    """Project V4 along kernel n, run zomeable alignment test.
    Returns (projected_pts_3d, deduped_edges) if zomeable, else None.
    """
    n = np.asarray(n, dtype=float)
    M = projection_matrix(n)  # 3 x 4
    P = (M @ V4.T).T  # (nV, 3)
    # de-duplicate coincident points; relabel edges
    rounded = np.round(P, 9)
    seen = {}
    new_idx = []
    for row in rounded:
        key = tuple(row.tolist())
        if key not in seen:
            seen[key] = len(seen)
        new_idx.append(seen[key])
    Pdedup = np.array(list(seen.keys()))
    new_edges = []
    for i, j in edges:
        a, b = new_idx[i], new_idx[j]
        if a != b:
            new_edges.append((min(a, b), max(a, b)))
    new_edges = sorted(set(new_edges))
    if len(Pdedup) < 4 or len(new_edges) == 0:
        return None
    # build 3 x K edge displacement matrix
    disp = np.stack([Pdedup[i] - Pdedup[j] for i, j in new_edges], axis=1)
    sig = _try_align(disp, tol=tol)
    if sig is None:
        return None
    return Pdedup, new_edges


def main():
    V, edges = duoprism(4, 6)
    print(f"duoprism_4_6: V={len(V)}, E={len(edges)}")

    results = {}  # rng -> set of shape signatures
    repr_kernel = {}  # signature -> first kernel that produced it

    for rng in [1, 2, 3, 4, 5, 6]:
        dirs = gen_2d_dirs(rng)
        zomeable_kernels = []
        sigs = set()
        for n in dirs:
            out = test_kernel(V, edges, n)
            if out is None:
                continue
            P, E = out
            sig = shape_signature(P, E)
            zomeable_kernels.append((tuple(n.tolist()), sig))
            sigs.add(sig)
            if sig not in repr_kernel:
                repr_kernel[sig] = tuple(n.tolist())
        results[rng] = sigs
        print(f"\nrng={rng}: |kernels|={len(dirs):>6}  |zomeable|={len(zomeable_kernels):>5}  |distinct shapes|={len(sigs)}")
        for sig in sorted(sigs, key=lambda s: s[2]):
            n_repr = repr_kernel[sig]
            marker = "  NEW" if rng > 1 and sig not in results.get(rng - 1, set()) else ""
            print(f"   {sig[2]}  V={sig[0]:>3}  E={sig[1]:>3}   first kernel: ({n_repr[0]:+.4f}, {n_repr[1]:+.4f}, 0, 0){marker}")

    # Final summary
    print("\n=== Growth summary ===")
    for rng in sorted(results):
        print(f"  rng={rng}: {len(results[rng]):>3} distinct shapes")
    print("\nIf inf-family: count grows steadily with rng (roughly linear in rng).")
    print("If finite/sporadic: count saturates by rng=3 or 4.")


if __name__ == "__main__":
    main()
