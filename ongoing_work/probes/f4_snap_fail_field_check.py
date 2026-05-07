"""F4 snap-fail field investigation.

Three F4 polytopes have kernels that pass _try_align but fail _snap_coords:
  - cantellated 24-cell (1,0,1,0):     k = [0, 0, 1/phi^2, -1/phi^2]
  - runcinated 24-cell (1,0,0,1):      k = [0, 0, 0, 2*phi]    (3.236)
  - runcitruncated 24-cell (1,1,0,1):  k = [0, 0, 0, 2*phi]    (3.236)

(Note: the doc previously said "[0,0,0,2*phi^2]" but the actual numeric
3.236068 = 2*phi, not 2*phi^2 = 5.236068.  Likely a typo in WYTHOFF_SWEEP.md
that should be corrected.)

Hypothesis: the projected 3D vertex coordinates lie in the field
ZZ[phi, sqrt(3)] (or some other extension of ZZ[phi]), not in ZZ[phi]
itself.  vZome can only represent ZZ[phi]^3 in its golden-zome field, so
emit_generic._snap_coords cannot find an integer/rational scaling that
puts all vertices in ZZ[phi].

Method: build each F4 polytope, project along its snap-fail kernel,
take the 3D vertex coords, and inspect whether each coord is consistent
with a + b*phi (ZZ[phi]) or requires extra factors of sqrt(2), sqrt(3),
sqrt(5) etc.  A clean test: scale-normalise so the smallest edge
length squared is 1, then check whether each unique value among vertex
coordinates and edge length squareds factors as p + q*phi for small
rational p, q.  If yes -> ZZ[phi].  If we need an extra factor of sqrt(3)
to get integer coefficients, the field is ZZ[phi, sqrt(3)].
"""
import sys
import numpy as np
from pathlib import Path
from fractions import Fraction
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

from wythoff import build_polytope
from emit_generic import projection_matrix

PHI = (1.0 + 5.0 ** 0.5) / 2.0
SQRT3 = 3.0 ** 0.5
SQRT2 = 2.0 ** 0.5
SQRT5 = 5.0 ** 0.5

# F4 snap-fail cases (matches blind_spot_triage.json + manifest snap_failed entries)
F4_SNAP_FAIL = [
    ("F4", "cantellated 24-cell",      (1, 0, 1, 0),   [0.0, 0.0, 1/PHI**2, -1/PHI**2],   "[0, 0, 1/phi^2, -1/phi^2]"),
    ("F4", "runcinated 24-cell",       (1, 0, 0, 1),   [0.0, 0.0, 0.0,       2 * PHI],     "[0, 0, 0, 2*phi]"),
    ("F4", "runcitruncated 24-cell",   (1, 1, 0, 1),   [0.0, 0.0, 0.0,       2 * PHI],     "[0, 0, 0, 2*phi]"),
]

# Sample B4 snap-fail cases for the same 3 magic kernels (taken from manifest
# snap_failed entries).  These probe whether the field obstruction is intrinsic
# to the kernel direction, regardless of which Coxeter group hosts the polytope.
B4_SNAP_FAIL = [
    ("B4", "cantellated tesseract",   (1, 0, 1, 0), [5.0**0.5, -5.0**0.5, -5.0**0.5, 5.0**0.5],  "[sqrt5, -sqrt5, -sqrt5, sqrt5]"),
    ("B4", "runcinated tesseract",    (1, 0, 0, 1), [0.0, 0.0, 0.0, 2 * PHI],                    "[0, 0, 0, 2*phi]"),
    ("B4", "runcitruncated 16-cell",  (1, 0, 1, 1), [0.0, 0.0, 1/PHI**2, -1/PHI**2],             "[0, 0, 1/phi^2, -1/phi^2]"),
]

ALL_CASES = F4_SNAP_FAIL + B4_SNAP_FAIL


def try_zphi_decompose(x, denom_max=24, num_max=24, tol=1e-5):
    """Try to write x as (p + q*phi) / r for small integers p, q, r.
    Returns (p, q, r) tuple or None.  Searches r in 1..denom_max,
    prefering smaller r, then smaller |p|+|q|."""
    for r in range(1, denom_max + 1):
        xr = x * r
        # Search in order of increasing |p| so simpler matches win.
        for abs_p in range(0, num_max + 1):
            for sign in (1, -1) if abs_p else (1,):
                p = sign * abs_p
                q_float = (xr - p) / PHI
                q = round(q_float)
                if abs(q) > num_max:
                    continue
                if abs((p + q * PHI) - xr) < tol:
                    return (p, q, r)
    return None


def try_sqrt3_phi_decompose(x, denom_max=24, num_max=4, tol=1e-5):
    """Try to write x as (p + q*phi + r*sqrt3 + s*phi*sqrt3) / d
    for small integers p, q, r, s, d.  Returns tuple or None.
    Iteration order prefers small d and small |r|+|s|."""
    for d in range(1, denom_max + 1):
        xd = x * d
        for abs_r in range(0, num_max + 1):
            for sgn_r in (1, -1) if abs_r else (1,):
                r_int = sgn_r * abs_r
                for abs_s in range(0, num_max + 1):
                    for sgn_s in (1, -1) if abs_s else (1,):
                        s_int = sgn_s * abs_s
                        resid = xd - (r_int + s_int * PHI) * SQRT3
                        pq = try_zphi_decompose(resid, denom_max=1, num_max=num_max * 4, tol=tol)
                        if pq is not None:
                            p_int, q_int, _ = pq
                            return (p_int, q_int, r_int, s_int, d)
    return None


def try_sqrt2_phi_decompose(x, denom_max=24, num_max=8, tol=1e-5):
    """Try to write x as (p + q*phi + r*sqrt2 + s*phi*sqrt2) / d
    for small integers p, q, r, s, d.  Iteration order prefers
    small d and small |r|+|s|."""
    for d in range(1, denom_max + 1):
        xd = x * d
        for abs_r in range(0, num_max + 1):
            for sgn_r in (1, -1) if abs_r else (1,):
                r_int = sgn_r * abs_r
                for abs_s in range(0, num_max + 1):
                    for sgn_s in (1, -1) if abs_s else (1,):
                        s_int = sgn_s * abs_s
                        resid = xd - (r_int + s_int * PHI) * SQRT2
                        pq = try_zphi_decompose(resid, denom_max=1, num_max=num_max * 4, tol=tol)
                        if pq is not None:
                            p_int, q_int, _ = pq
                            return (p_int, q_int, r_int, s_int, d)
    return None


def proj_vertices(V4, kernel_4):
    """Project (n,4) array V4 along kernel_4 onto its 3-perp."""
    n = np.asarray(kernel_4, dtype=float)
    Q = projection_matrix(n)            # 3x4
    return (V4 @ Q.T)                   # (n, 3)


for group, name, bm, kvec, kdesc in ALL_CASES:
    print("=" * 70)
    print(f"{group} {name}  bm={bm}  kernel={kdesc}")
    print("=" * 70)
    V4, E_idx = build_polytope(group, bm)
    V4 = np.asarray(V4, dtype=float)
    print(f"V4 = {len(V4)} vertices (4D, F4 cholesky_aligned basis)")

    P3 = proj_vertices(V4, kvec)        # (n, 3) projected vertices
    print(f"P3 = {P3.shape}  proj along kernel")

    # Edge lengths squared in 3D
    edge_lens2 = np.array([
        float(np.dot(P3[a] - P3[b], P3[a] - P3[b]))
        for (a, b) in E_idx
    ])
    L2_min = edge_lens2[edge_lens2 > 1e-10].min()
    L2_norm = edge_lens2 / L2_min
    print(f"  edges: {len(E_idx)}, smallest non-zero L2 = {L2_min:.6f}")
    uniq_L2 = sorted(set(round(x, 6) for x in L2_norm))
    print(f"  distinct normalised L2 values: {len(uniq_L2)}")
    for v in uniq_L2[:12]:
        zphi = try_zphi_decompose(v)
        z3p  = try_sqrt3_phi_decompose(v) if zphi is None else None
        if zphi:
            (p, q, r) = zphi
            phi_str = "" if q == 0 else (f" + {q}phi" if q > 0 else f" - {-q}phi")
            tag = f"= ({p}{phi_str})/{r}" if r > 1 else f"= {p}{phi_str}"
            print(f"    L2_norm={v:>10.6f}  ZZ[phi]: {tag}")
        elif z3p:
            (p, q, r, s, d) = z3p
            print(f"    L2_norm={v:>10.6f}  ZZ[phi,sqrt3]: ({p} + {q}phi + ({r} + {s}phi)*sqrt3)/{d}")
        else:
            print(f"    L2_norm={v:>10.6f}  NEITHER ZZ[phi] NOR ZZ[phi,sqrt3]")

    # Also check: is sqrt(L2_min) * P3 in ZZ[phi]^3?  i.e. divide all coords
    # by the natural-units scale.  Pick the "natural" scale = sqrt(L2_min/2)
    # so smallest edge has length sqrt(2) (a common F4-edge convention).
    # Try a few rescale factors.
    scale = np.sqrt(L2_min)
    P3n = P3 / scale
    coords_flat = P3n.flatten()
    # Group floats by 6-decimal representative but keep one exact float each
    rep_for = {}
    for c in coords_flat:
        key = round(float(c), 6)
        if key not in rep_for:
            rep_for[key] = float(c)
    coord_uniq = sorted(rep_for.keys())
    print(f"  vertex coords (rescaled, /sqrt(L2_min)): {len(coord_uniq)} distinct values")
    n_zphi = n_z3p = n_z2p = n_neither = 0
    sample_neither = []
    z2_examples = []
    for v_key in coord_uniq:
        v = rep_for[v_key]   # exact float
        if abs(v) < 1e-9:
            n_zphi += 1
            continue
        z = try_zphi_decompose(v)
        if z is not None:
            n_zphi += 1
        else:
            z2 = try_sqrt2_phi_decompose(v)
            if z2 is not None:
                n_z2p += 1
                if len(z2_examples) < 5:
                    z2_examples.append((v_key, z2))
            else:
                z3 = try_sqrt3_phi_decompose(v)
                if z3 is not None:
                    n_z3p += 1
                else:
                    n_neither += 1
                    if len(sample_neither) < 5:
                        sample_neither.append(v_key)
    print(f"    in ZZ[phi]:        {n_zphi}")
    print(f"    in ZZ[phi,sqrt2]:  {n_z2p}")
    if z2_examples:
        for vk, (p, q, r, s, d) in z2_examples:
            phi_part = "" if q == 0 else (f" + {q}phi" if q > 0 else f" - {-q}phi")
            sqrt2_p = "" if (r == 0 and s == 0) else (
                f" + ({r}{(' + '+str(s)+'phi') if s>0 else ((' - '+str(-s)+'phi') if s<0 else '')})*sqrt2"
            )
            denom = "" if d == 1 else f"  / {d}"
            print(f"      e.g. {vk:>10.6f} = ({p}{phi_part}{sqrt2_p}){denom}")
    print(f"    in ZZ[phi,sqrt3]:  {n_z3p}")
    print(f"    in neither:        {n_neither}", end="")
    if sample_neither:
        print(f"  (samples: {sample_neither})")
    else:
        print()
    print()
