"""Generic emitter: numerically project + try_align, then snap to ZZ[phi]^3.

Given a 4D polytope (verts V, edges E) and a kernel direction n, this:
  1. Computes the orthonormal projection (lib/search_engine.projection_matrix).
  2. Finds rotation R via _try_align that puts all edges on default zometool axes.
  3. Applies R to projected vertices.
  4. Searches a small set of multiplicative scales `s` such that all components
     of s * (R @ projection) snap exactly to a + b*phi for small integer (a, b).
  5. Verifies all 4D edges, after dedup, classify on default axes.
  6. Emits a .vZome file via emit_vzome_directional.

Snap tolerance is 1e-6 in floating-point distance to a + b*phi (a, b ∈ Z, |a|, |b| <= 60).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from fractions import Fraction
from emit_vzome import GF, emit_vzome_directional, classify_direction
from search_engine import projection_matrix, _try_align

PHI_F = (1.0 + 5.0 ** 0.5) / 2.0


def _snap_zphi(x, tol=1e-6, N=80):
    """Find integers (a, b) with |a|, |b| <= N s.t. x ≈ a + b*phi.
    Returns (a, b) or None.
    """
    # phi is irrational. For any x, search lattice. Use the trick: pick b first
    # by writing b ≈ (x - a) / phi for some a, then verify.
    # Simpler: for each b in [-N, N], a = round(x - b*phi); check error.
    best = None
    for b in range(-N, N + 1):
        a = round(x - b * PHI_F)
        if abs(a) > N:
            continue
        err = abs(x - (a + b * PHI_F))
        if err < tol and (best is None or err < best[2]):
            best = (a, b, err)
    if best is None:
        return None
    return GF(best[0], best[1])


def _snap_coords(coords3, scales_to_try):
    """Try each scale `s` until ALL coords snap to ZZ[phi]. Returns (s, list[tuple[GF,GF,GF]])."""
    for s in scales_to_try:
        ok = True
        snapped = []
        for p in coords3:
            sp = []
            for c in p:
                g = _snap_zphi(s * c)
                if g is None:
                    ok = False
                    break
                sp.append(g)
            if not ok:
                break
            snapped.append(tuple(sp))
        if ok:
            return s, snapped
    return None, None


def _dedup_balls(balls):
    """Dedup ZZ[phi]^3 ball coords; return uniq list and idx_map."""
    uniq = []
    idx_map = []
    for b in balls:
        found = -1
        for i, q in enumerate(uniq):
            if all(b[k] == q[k] for k in range(3)):
                found = i
                break
        if found >= 0:
            idx_map.append(found)
        else:
            idx_map.append(len(uniq))
            uniq.append(b)
    return uniq, idx_map


def project_and_emit(name, V4, E4, n, out_path,
                     extra_scale=GF(2, 2),
                     scales_to_try=None,
                     verbose=True):
    """Project V4 (Nx4) along kernel n, snap, emit .vZome.

    extra_scale: outer GF multiplier applied AFTER snapping, to ensure visible
        strut sizes (default 2 + 2*phi = phi^2 * 2, matches 24-cell convention).
    scales_to_try: list of float scales s; we try s * coords.snap → ZZ[phi].
        Defaults to a useful set covering common irrationals.
    """
    V4 = np.asarray(V4, dtype=float)
    n = np.asarray(n, dtype=float)
    Q = projection_matrix(n)
    P3 = (Q @ V4.T).T  # Nx3 numerical
    edges_dirs = (Q @ np.array([V4[b] - V4[a] for a, b in E4]).T)
    res = _try_align(edges_dirs)
    if res is None:
        raise RuntimeError(f"{name}: kernel n={n.tolist()} NOT alignable")
    R, classes = res
    if verbose:
        from collections import Counter
        print(f"  align ok, sig={dict(Counter(classes))}")
    P3rot = (R @ P3.T).T

    # search_engine and emit_vzome use icosahedral groups that are mirror-related
    # (their Y-orbits contain (0,phi^2,1) vs (0,1,phi^2) — opposite cyclic).
    # A coordinate swap reconciles them. Pick swap_yz as canonical.
    SWAP_YZ = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)
    P3rot = (SWAP_YZ @ P3rot.T).T

    if scales_to_try is None:
        # Common normalising factors that arise from orthonormal projection of
        # ZZ[phi] vectors. PHI^k handles golden, sqrt2/sqrt5 handle root-2/root-5
        # cases. We multiply by integer multiples up to 30 for size.
        sqrt2 = 2.0 ** 0.5
        sqrt5 = 5.0 ** 0.5
        bases = [1.0, sqrt2, sqrt5, sqrt2 * sqrt5, PHI_F, PHI_F * sqrt2,
                 PHI_F * sqrt5, sqrt2 / PHI_F, sqrt5 / PHI_F,
                 PHI_F ** 2, 1.0 / PHI_F]
        ks = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20]
        scales_to_try = []
        for b in bases:
            for k in ks:
                scales_to_try.append(b * k)
                scales_to_try.append(b / k)

    s, snapped = _snap_coords(P3rot, scales_to_try)
    if snapped is None:
        # diagnostic
        if verbose:
            print(f"  numerical 3D rotated coords (failed to snap):")
            for p in P3rot[:5]:
                print(f"    {p.round(6)}")
        raise RuntimeError(f"{name}: could not snap coords to ZZ[phi]^3")
    if verbose:
        print(f"  snap scale s={s:.6f}")

    # Apply outer extra_scale for visible struts
    snapped = [tuple(c * extra_scale for c in p) for p in snapped]

    uniq, idx_map = _dedup_balls(snapped)

    edges3_set = set()
    for i, j in E4:
        a, b = idx_map[i], idx_map[j]
        if a == b:
            continue
        edges3_set.add((min(a, b), max(a, b)))
    edges3 = sorted(edges3_set)

    # Verify each edge classifies
    all_ok = True
    for i, j in edges3:
        c = classify_direction(uniq[i], uniq[j])
        if c is None:
            all_ok = False
            if verbose:
                print(f"  EDGE {i}-{j} fails classify_direction!")
                print(f"    {uniq[i]} -> {uniq[j]}")
    if not all_ok:
        raise RuntimeError(f"{name}: edge classification failed")

    if verbose:
        print(f"  {len(uniq)} balls, {len(edges3)} 3D edges")
    counts = emit_vzome_directional(uniq, edges3, out_path)
    if verbose:
        print(f"  emitted: {out_path}")
        print(f"  strut counts: {counts}")
    return counts
