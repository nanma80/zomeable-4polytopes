"""3D vertex/edge specifications for the 18 convex uniform polyhedra.

Each function returns (V, edges) where V is an Nx3 numpy float array and
edges is a list of (i, j) index pairs.  Used to construct polyhedral
prisms (4D = P x [0, 1]) in `polytopes_prismatic.py`.

Of the 18 polyhedra:
  13 embed in ZZ[phi]^3 with their canonical coordinates:
    tetrahedron, cube, octahedron, dodecahedron, icosahedron,
    truncated_tetrahedron, truncated_octahedron, truncated_dodecahedron,
    truncated_icosahedron, cuboctahedron, icosidodecahedron,
    rhombicosidodecahedron, truncated_icosidodecahedron
  5 require quadratic extensions (sqrt(2) or tribonacci constant) so are
  NOT in ZZ[phi]^3 and never produce zomeable projections of their prism:
    truncated_cube         (sqrt(2))
    rhombicuboctahedron    (sqrt(2))
    truncated_cuboctahedron (sqrt(2))
    snub_cube              (tribonacci)
    snub_dodecahedron      (tribonacci)

Vertex/edge counts follow Wikipedia.
"""

from __future__ import annotations

from itertools import permutations, product

import numpy as np


phi = (1.0 + 5.0 ** 0.5) / 2.0


# ---------------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------------- #
def _edges_at(V, d2, tol=1e-5):
    """All unordered index pairs whose squared Euclidean distance is d2."""
    n = len(V)
    out = []
    for i in range(n):
        for j in range(i + 1, n):
            d = V[i] - V[j]
            if abs(d @ d - d2) < tol:
                out.append((i, j))
    return out


def _edges_min(V, tol=1e-5):
    """Find pairs whose squared distance equals the minimum nonzero pair distance."""
    n = len(V)
    if n < 2:
        return []
    dmin2 = float("inf")
    for i in range(n):
        for j in range(i + 1, n):
            d = V[i] - V[j]
            d2 = float(d @ d)
            if d2 > tol and d2 < dmin2:
                dmin2 = d2
    return _edges_at(V, dmin2, tol=max(tol, dmin2 * 1e-9))


def _signed_perms(seq, even_only=False, even_signs_only=False):
    """All (signed permutations) of seq.  Returns list of 3-tuples.

    even_only=True keeps only even permutations of seq.
    even_signs_only=True keeps only sign patterns with an even number of (-1)s.
    """
    out = set()
    seq = tuple(seq)
    for p in permutations(range(3)):
        # parity
        sgn = 1
        for i in range(3):
            for j in range(i + 1, 3):
                if p[i] > p[j]:
                    sgn *= -1
        if even_only and sgn != 1:
            continue
        permuted = tuple(seq[p[k]] for k in range(3))
        for signs in product((1, -1), repeat=3):
            if even_signs_only:
                neg_count = sum(1 for s in signs if s == -1)
                if neg_count % 2 != 0:
                    continue
            v = tuple(signs[k] * permuted[k] for k in range(3))
            out.add(v)
    return [list(v) for v in out]


def _even_perms_signed(seq):
    """All even permutations of seq with all sign choices.  Wikipedia 'even permutations of (±a,±b,±c)' style."""
    return _signed_perms(seq, even_only=True, even_signs_only=False)


# ---------------------------------------------------------------------- #
# 5 Platonic
# ---------------------------------------------------------------------- #
def tetrahedron():
    V = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], dtype=float)
    edges = _edges_at(V, 8.0)  # L = 2*sqrt(2)
    return V, edges


def cube():
    V = np.array(list(product((-1.0, 1.0), repeat=3)), dtype=float)
    edges = _edges_at(V, 4.0)  # L = 2
    return V, edges


def octahedron():
    V = []
    for i in range(3):
        for s in (1, -1):
            v = [0, 0, 0]
            v[i] = s
            V.append(v)
    V = np.array(V, dtype=float)
    edges = _edges_at(V, 2.0)  # L = sqrt(2)
    return V, edges


def dodecahedron():
    """Vertices: cube (±1,±1,±1) ∪ even permutations of (0, ±1/φ, ±φ).  Edge L=2/φ."""
    V = list(product((-1.0, 1.0), repeat=3))
    iphi = 1.0 / phi
    V.extend(_even_perms_signed((0.0, iphi, phi)))
    V = np.array(V, dtype=float)
    edges = _edges_min(V)
    return V, edges


def icosahedron():
    """Vertices: even permutations of (0, ±1, ±φ).  Edge L=2."""
    V = np.array(_even_perms_signed((0.0, 1.0, phi)), dtype=float)
    edges = _edges_at(V, 4.0)
    return V, edges


# ---------------------------------------------------------------------- #
# 13 Archimedean
# ---------------------------------------------------------------------- #
def truncated_tetrahedron():
    """Vertices: 12 points 2*v_i + v_j for the 4 tetrahedron vertices, i != j.
    Equivalently: all permutations of (1,1,3) with sign-product = +1."""
    base = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    V = []
    for i, vi in enumerate(base):
        for j, vj in enumerate(base):
            if i == j:
                continue
            V.append([2 * vi[k] + vj[k] for k in range(3)])
    V = np.array(V, dtype=float)
    edges = _edges_min(V)
    return V, edges


def truncated_cube():
    """sqrt(2)-dependent.  Vertices: permutations of (±xi, ±1, ±1), xi = sqrt(2) - 1."""
    xi = 2.0 ** 0.5 - 1.0
    V = _signed_perms((xi, 1.0, 1.0))
    V = np.array(V, dtype=float)
    edges = _edges_min(V)
    return V, edges


def truncated_octahedron():
    """Permutations of (0, ±1, ±2).  Edge L=sqrt(2)."""
    V = _signed_perms((0.0, 1.0, 2.0))
    V = np.array(V, dtype=float)
    edges = _edges_at(V, 2.0)
    return V, edges


def truncated_dodecahedron():
    """Even permutations of (0, ±1/φ, ±(2+φ)), (±1/φ, ±φ, ±2φ), (±φ, ±2, ±(φ+1)).
    Edge L = 2/φ^2 (after scaling)."""
    iphi = 1.0 / phi
    V = []
    V.extend(_even_perms_signed((0.0, iphi, 2.0 + phi)))
    V.extend(_even_perms_signed((iphi, phi, 2.0 * phi)))
    V.extend(_even_perms_signed((phi, 2.0, phi + 1.0)))
    V = np.array(V, dtype=float)
    edges = _edges_min(V)
    return V, edges


def truncated_icosahedron():
    """Even permutations of (0, ±1, ±3φ), (±1, ±(2+φ), ±2φ), (±φ, ±2, ±(2φ+1)).  Edge L=2."""
    V = []
    V.extend(_even_perms_signed((0.0, 1.0, 3.0 * phi)))
    V.extend(_even_perms_signed((1.0, 2.0 + phi, 2.0 * phi)))
    V.extend(_even_perms_signed((phi, 2.0, 2.0 * phi + 1.0)))
    V = np.array(V, dtype=float)
    edges = _edges_at(V, 4.0)
    return V, edges


def cuboctahedron():
    """Permutations of (±1, ±1, 0).  Edge L=sqrt(2)."""
    V = _signed_perms((1.0, 1.0, 0.0))
    V = np.array(V, dtype=float)
    edges = _edges_at(V, 2.0)
    return V, edges


def icosidodecahedron():
    """(0, 0, ±φ) perm + even-perms of (±1/2, ±φ/2, ±φ^2/2).  Edge L=1."""
    V = []
    # Axial vertices: ±φ on each axis
    for i in range(3):
        for s in (1, -1):
            v = [0.0, 0.0, 0.0]
            v[i] = s * phi
            V.append(v)
    # Even permutations of (1/2, φ/2, φ^2/2) with all sign choices
    V.extend(_even_perms_signed((0.5, 0.5 * phi, 0.5 * phi * phi)))
    V = np.array(V, dtype=float)
    edges = _edges_at(V, 1.0)
    return V, edges


def rhombicuboctahedron():
    """Permutations of (±1, ±1, ±(1+sqrt(2))).  Edge L=2."""
    a = 1.0 + 2.0 ** 0.5
    V = _signed_perms((1.0, 1.0, a))
    V = np.array(V, dtype=float)
    edges = _edges_min(V)
    return V, edges


def truncated_cuboctahedron():
    """Permutations of (±1, ±(1+sqrt(2)), ±(1+2*sqrt(2))).  Edge L=2."""
    sq2 = 2.0 ** 0.5
    a = 1.0 + sq2
    b = 1.0 + 2.0 * sq2
    V = _signed_perms((1.0, a, b))
    V = np.array(V, dtype=float)
    edges = _edges_min(V)
    return V, edges


def rhombicosidodecahedron():
    """Even perms of (±1, ±1, ±φ^3), (±φ^2, ±φ, ±2φ), (±(2+φ), 0, ±φ^2).  Edge L=2."""
    phi2 = phi * phi
    phi3 = phi2 * phi
    V = []
    V.extend(_even_perms_signed((1.0, 1.0, phi3)))
    V.extend(_even_perms_signed((phi2, phi, 2.0 * phi)))
    V.extend(_even_perms_signed((2.0 + phi, 0.0, phi2)))
    V = np.array(V, dtype=float)
    edges = _edges_min(V)
    return V, edges


def truncated_icosidodecahedron():
    """Even perms of 5 triples (Wikipedia).  120 vertices."""
    iphi = 1.0 / phi
    phi2 = phi * phi
    V = []
    V.extend(_even_perms_signed((iphi, iphi, 3.0 + phi)))
    V.extend(_even_perms_signed((2.0 * iphi, phi, 1.0 + 2.0 * phi)))
    V.extend(_even_perms_signed((iphi, phi2, 3.0 * phi - 1.0)))
    V.extend(_even_perms_signed((2.0 * phi - 1.0, 2.0, 2.0 + phi)))
    V.extend(_even_perms_signed((phi, 3.0, 2.0 * phi)))
    V = np.array(V, dtype=float)
    edges = _edges_min(V)
    return V, edges


def snub_cube():
    """Tribonacci-extension.  Vertices: even perms of (±1, ±xi, ±1/xi) with
    even minus-sign count, plus odd perms with odd minus-sign count.
    xi ≈ 1.83928 is the real root of t^3 - t^2 - t - 1 = 0."""
    xi = ((1.0 + (19.0 - 3.0 * 33.0 ** 0.5) ** (1.0 / 3.0)
           + (19.0 + 3.0 * 33.0 ** 0.5) ** (1.0 / 3.0)) / 3.0)
    base = (1.0, xi, 1.0 / xi)
    V = set()
    for p in permutations(range(3)):
        sgn = 1
        for i in range(3):
            for j in range(i + 1, 3):
                if p[i] > p[j]:
                    sgn *= -1
        even_perm = (sgn == 1)
        permuted = tuple(base[p[k]] for k in range(3))
        for signs in product((1, -1), repeat=3):
            neg = sum(1 for s in signs if s == -1)
            even_signs = (neg % 2 == 0)
            if even_perm == even_signs:
                v = tuple(signs[k] * permuted[k] for k in range(3))
                V.add(v)
    V = np.array(sorted(V), dtype=float)
    edges = _edges_min(V)
    return V, edges


def snub_dodecahedron():
    """Tribonacci-extension snub dodecahedron.  60 vertices.

    Construction via Wikipedia: even permutations of cyclic combinations
    involving phi and the snub-related constant xi where
    xi^3 = xi + 1, alpha = xi - 1/xi, beta = xi*phi + phi^2 + phi/xi.

    Implementation note: this is complex; we use the parameterisation
    given on Wikipedia's snub dodecahedron page.
    """
    # snub dodecahedron constant: root of x^3 - 2x = phi (Wikipedia notation)
    # Solving numerically:
    from numpy.polynomial import polynomial as P
    coeffs = [-phi, -2.0, 0.0, 1.0]  # x^3 - 2x - phi
    roots = np.roots(coeffs[::-1])
    real_roots = [r.real for r in roots if abs(r.imag) < 1e-9]
    xi = max(real_roots)  # ≈ 1.7155615
    alpha = xi - 1.0 / xi
    beta = xi * phi + phi * phi + phi / xi
    # 60 vertices: 12 cyclic permutations of (±2α, ±2, ±2β), 12 of
    # (±(α + β/φ + φ), ±(-αφ + β + 1/φ), ±(α/φ + βφ - 1)), 12 of
    # (±(-α/φ + βφ + 1), ±(-α + β/φ - φ), ±(αφ + β - 1/φ)),
    # 12 of (±(-α/φ + βφ - 1), ±(α - β/φ - φ), ±(αφ + β + 1/φ)),
    # 12 of (±(α + β/φ - φ), ±(αφ - β + 1/φ), ±(α/φ + βφ + 1)).
    iphi = 1.0 / phi
    bases = [
        (2.0 * alpha, 2.0, 2.0 * beta),
        (alpha + beta * iphi + phi,    -alpha * phi + beta + iphi,    alpha * iphi + beta * phi - 1.0),
        (-alpha * iphi + beta * phi + 1.0, -alpha + beta * iphi - phi, alpha * phi + beta - iphi),
        (-alpha * iphi + beta * phi - 1.0, alpha - beta * iphi - phi,  alpha * phi + beta + iphi),
        (alpha + beta * iphi - phi,    alpha * phi - beta + iphi,    alpha * iphi + beta * phi + 1.0),
    ]
    V = []
    for b in bases:
        # cyclic permutations (= 3 even permutations)
        for shift in range(3):
            cb = tuple(b[(k + shift) % 3] for k in range(3))
            for signs in product((1, -1), repeat=3):
                # even-sign-parity selection (one chirality):
                neg = sum(1 for s in signs if s == -1)
                if neg % 2 == 0:
                    V.append([signs[k] * cb[k] for k in range(3)])
    V = np.array(V, dtype=float)
    edges = _edges_min(V)
    return V, edges


# ---------------------------------------------------------------------- #
# Registry
# ---------------------------------------------------------------------- #
UNIFORM_POLYHEDRA = {
    # Platonic
    "tetrahedron":              (tetrahedron,              4,  6,  True),
    "cube":                     (cube,                     8, 12,  True),
    "octahedron":               (octahedron,               6, 12,  True),
    "dodecahedron":             (dodecahedron,            20, 30,  True),
    "icosahedron":              (icosahedron,             12, 30,  True),
    # Archimedean (zomeable in ZZ[phi]^3)
    "truncated_tetrahedron":    (truncated_tetrahedron,   12, 18,  True),
    "truncated_octahedron":     (truncated_octahedron,    24, 36,  True),
    "truncated_dodecahedron":   (truncated_dodecahedron,  60, 90,  True),
    "truncated_icosahedron":    (truncated_icosahedron,   60, 90,  True),
    "cuboctahedron":            (cuboctahedron,           12, 24,  True),
    "icosidodecahedron":        (icosidodecahedron,       30, 60,  True),
    "rhombicosidodecahedron":   (rhombicosidodecahedron,  60, 120, True),
    "truncated_icosidodecahedron": (truncated_icosidodecahedron, 120, 180, True),
    # Archimedean (NON-ZZ[phi]^3)
    "truncated_cube":           (truncated_cube,          24, 36,  False),
    "rhombicuboctahedron":      (rhombicuboctahedron,     24, 48,  False),
    "truncated_cuboctahedron":  (truncated_cuboctahedron, 48, 72,  False),
    "snub_cube":                (snub_cube,               24, 60,  False),
    "snub_dodecahedron":        (snub_dodecahedron,       60, 150, False),
}


def get_polyhedron(name: str):
    """Return (V, edges) for the named polyhedron."""
    return UNIFORM_POLYHEDRA[name][0]()


def expected_VE(name: str):
    """Return (V_count, E_count, is_zphi3)."""
    _, nv, ne, zphi = UNIFORM_POLYHEDRA[name]
    return nv, ne, zphi


def all_polyhedra():
    return list(UNIFORM_POLYHEDRA.keys())
