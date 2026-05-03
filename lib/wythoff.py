"""Coxeter/Wythoff generator for uniform 4-polytopes.

For each of the rank-4 Coxeter groups A4, B4, F4, H4, we:
  1. Build unit-length simple roots from the Coxeter matrix via
     Cholesky decomposition of the Gram matrix G_ij = -cos(pi/m_ij)
     (with G_ii = 1).
  2. Compute the regular polytope (bitmask 1000) in this Cholesky frame.
  3. Orthogonally Procrustes-align that to the canonical embedding from
     lib.polytopes (the same frame used by lib.search_engine).
  4. Apply the resulting rotation to every Wythoff variant of the same
     group, so all polytopes live in the canonical frame.

This way kernel directions in the lib.search_engine Z[phi]^4
enumeration align geometrically with the "vertex-first / cell-first /
edge-first" projections that we found for the regulars.
"""
import numpy as np
from typing import Tuple, List


phi = (1 + 5 ** 0.5) / 2


# ---- Coxeter matrices for the rank-4 groups of interest ----------------
COXETER_MATRICES = {
    "A4": np.array([
        [1, 3, 2, 2],
        [3, 1, 3, 2],
        [2, 3, 1, 3],
        [2, 2, 3, 1],
    ]),
    "B4": np.array([
        [1, 4, 2, 2],
        [4, 1, 3, 2],
        [2, 3, 1, 3],
        [2, 2, 3, 1],
    ]),
    "D4": np.array([
        [1, 3, 2, 2],
        [3, 1, 3, 3],
        [2, 3, 1, 2],
        [2, 3, 2, 1],
    ]),
    "F4": np.array([
        [1, 3, 2, 2],
        [3, 1, 4, 2],
        [2, 4, 1, 3],
        [2, 2, 3, 1],
    ]),
    "H4": np.array([
        [1, 5, 2, 2],
        [5, 1, 3, 2],
        [2, 3, 1, 3],
        [2, 2, 3, 1],
    ]),
}


def simple_roots(group: str) -> np.ndarray:
    """Unit-length simple roots in the Cholesky frame."""
    M = COXETER_MATRICES[group]
    n = M.shape[0]
    G = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            G[i, j] = 1.0 if i == j else -np.cos(np.pi / M[i, j])
    return np.linalg.cholesky(G)


def reflect(v: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Reflect v across the hyperplane normal to unit-length r."""
    return v - 2.0 * (v @ r) * r


def wythoff_seed(roots: np.ndarray, bitmask: Tuple[int, ...]) -> np.ndarray:
    """Solve r_i . v = b_i (unit roots)."""
    b = np.array(bitmask, dtype=float)
    return np.linalg.solve(roots, b)


def orbit(seed: np.ndarray, roots: np.ndarray, tol_decimals: int = 8,
          max_size: int = 20000) -> np.ndarray:
    found = [seed.copy()]
    keys = {tuple(np.round(seed, tol_decimals))}
    frontier = [seed.copy()]
    while frontier:
        new_frontier = []
        for v in frontier:
            for r in roots:
                w = reflect(v, r)
                k = tuple(np.round(w, tol_decimals))
                if k not in keys:
                    keys.add(k)
                    found.append(w)
                    new_frontier.append(w)
                    if len(found) > max_size:
                        raise RuntimeError(
                            f"orbit exceeded max_size={max_size}")
        frontier = new_frontier
    return np.array(found)



# ---- Procrustes calibration: align Cholesky-frame to canonical frame --
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

_CALIB_CACHE = {}


def _canonical_regular(group: str):
    import polytopes as P
    if group == "A4":
        return P.fivecell()
    if group == "B4":
        return P.tesseract()
    if group == "F4":
        return P.cell24_long_root()
    if group == "H4":
        return P.cell120()
    raise ValueError(group)


def _kabsch(P_pts: np.ndarray, Q_pts: np.ndarray) -> np.ndarray:
    """Optimal rotation R (in O(d)) such that P @ R.T ~= Q."""
    H = P_pts.T @ Q_pts
    U, _, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0:
        Vt[-1] *= -1
        R = Vt.T @ U.T
    return R


def _is_set_match(A: np.ndarray, B: np.ndarray, tol: float = 1e-3) -> bool:
    if len(A) != len(B):
        return False
    used = np.zeros(len(B), dtype=bool)
    for a in A:
        d = np.linalg.norm(B - a, axis=1)
        d = np.where(used, np.inf, d)
        k = int(np.argmin(d))
        if d[k] > tol:
            return False
        used[k] = True
    return bool(used.all())


def _procrustes_rotation(V_src: np.ndarray, V_dst: np.ndarray,
                         tol: float = 1e-3):
    """Find scale s, rotation R such that s * V_src @ R.T == V_dst (as set)."""
    n = len(V_src)
    if len(V_dst) != n:
        raise ValueError("vertex count mismatch")
    s_src = np.sqrt(np.mean(np.sum(V_src ** 2, axis=1)))
    s_dst = np.sqrt(np.mean(np.sum(V_dst ** 2, axis=1)))
    scale = s_dst / s_src
    Vs = V_src * scale

    # Pick 4 affinely independent reference points in Vs
    refs = [0]
    for k in range(1, n):
        rows = [Vs[i] - Vs[refs[0]] for i in refs[1:]] + [Vs[k] - Vs[refs[0]]]
        if np.linalg.matrix_rank(np.array(rows), tol=1e-6) == len(refs):
            refs.append(k)
            if len(refs) == 4:
                break
    if len(refs) < 4:
        raise RuntimeError("vertex set is not 4D")

    # Required pairwise distances
    D_src = np.array([[np.linalg.norm(Vs[i] - Vs[j]) for j in refs] for i in refs])
    # Required norms
    norms_src = np.array([np.linalg.norm(Vs[i]) for i in refs])
    norms_dst = np.linalg.norm(V_dst, axis=1)

    # Per-reference candidate sets in V_dst (matching norm)
    cands = []
    for i in range(4):
        cands.append(np.where(np.abs(norms_dst - norms_src[i]) < tol)[0])

    # Pairwise distance lookup
    D_dst_all = np.linalg.norm(V_dst[:, None, :] - V_dst[None, :, :], axis=2)

    P_pts = np.array([Vs[i] for i in refs])
    n_tested = 0
    MAX_TESTS = 5000
    for c0 in cands[0]:
        for c1 in cands[1]:
            if c1 == c0: continue
            if abs(D_dst_all[c0, c1] - D_src[0, 1]) > tol: continue
            for c2 in cands[2]:
                if c2 in (c0, c1): continue
                if abs(D_dst_all[c0, c2] - D_src[0, 2]) > tol: continue
                if abs(D_dst_all[c1, c2] - D_src[1, 2]) > tol: continue
                for c3 in cands[3]:
                    if c3 in (c0, c1, c2): continue
                    if abs(D_dst_all[c0, c3] - D_src[0, 3]) > tol: continue
                    if abs(D_dst_all[c1, c3] - D_src[1, 3]) > tol: continue
                    if abs(D_dst_all[c2, c3] - D_src[2, 3]) > tol: continue
                    Q_pts = np.array([V_dst[i] for i in (c0, c1, c2, c3)])
                    R = _kabsch(P_pts, Q_pts)
                    V_test = Vs @ R.T
                    if _is_set_match(V_test, V_dst, tol):
                        return R, scale
                    n_tested += 1
                    if n_tested > MAX_TESTS:
                        raise RuntimeError(f"Procrustes: too many candidates tested (n={n})")
    raise RuntimeError(f"No Procrustes match found (n={n}, tested={n_tested})")


def _get_calibration(group: str):
    if group in _CALIB_CACHE:
        return _CALIB_CACHE[group]
    roots = simple_roots(group)
    seed = wythoff_seed(roots, (1, 0, 0, 0))
    V_chol = orbit(seed, roots)
    V_canon, _ = _canonical_regular(group)
    R, scale = _procrustes_rotation(V_chol, V_canon)
    _CALIB_CACHE[group] = (R, scale)
    return R, scale


def build_polytope(group: str, bitmask, canonicalize: bool = True,
                   tol: float = 1e-6):
    if sum(bitmask) == 0:
        raise ValueError("bitmask must have at least one ringed node")
    roots = simple_roots(group)
    seed = wythoff_seed(roots, bitmask)
    V = orbit(seed, roots)
    n = len(V)
    keys = {tuple(np.round(v, 8)): idx for idx, v in enumerate(V)}
    edge_set = set()
    seed_idx = keys[tuple(np.round(seed, 8))]
    for i, b in enumerate(bitmask):
        if b == 0:
            continue
        v_other = reflect(seed, roots[i])
        other_idx = keys[tuple(np.round(v_other, 8))]
        d = V[seed_idx] - V[other_idx]
        d2 = float(d @ d)
        for p in range(n):
            for q in range(p + 1, n):
                dd = V[p] - V[q]
                if abs(dd @ dd - d2) < tol:
                    edge_set.add((p, q))

    if canonicalize:
        R, scale = _get_calibration(group)
        V = (V * scale) @ R.T

    return V, sorted(edge_set)


REGULAR_BITMASKS = {
    "5cell":     ("A4", (1, 0, 0, 0)),
    "tesseract": ("B4", (1, 0, 0, 0)),
    "16cell":    ("B4", (0, 0, 0, 1)),
    "24cell":    ("F4", (1, 0, 0, 0)),
    "120cell":   ("H4", (1, 0, 0, 0)),
    "600cell":   ("H4", (0, 0, 0, 1)),
}
EXPECTED = {
    "5cell": (5, 10), "tesseract": (16, 32), "16cell": (8, 24),
    "24cell": (24, 96), "120cell": (600, 1200), "600cell": (120, 720),
}


def _self_test():
    print("Wythoff generator self-test (canonical frame):")
    for name, (group, mask) in REGULAR_BITMASKS.items():
        try:
            V, E = build_polytope(group, mask)
            nv, ne = EXPECTED[name]
            ok = (len(V) == nv and len(E) == ne)
            print(f"  {'OK  ' if ok else 'FAIL'} {name:10s} ({group}, {mask}): "
                  f"{len(V)}v (exp {nv}), {len(E)}e (exp {ne})")
        except Exception as e:
            print(f"  ERR  {name:10s}: {e}")


if __name__ == "__main__":
    _self_test()
