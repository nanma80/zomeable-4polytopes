"""Constructors for the three families of convex uniform prismatic 4-polytopes.

Family A: polyhedral prisms        P x [0, 1] for each of 18 uniform polyhedra
Family B: duoprisms                {p} x {q} for p, q >= 3, (p,q) != (4,4)
Family C: antiprismatic prisms     A_n x [0, 1] for n >= 3

All constructors return (V, edges) as (np.ndarray[float, shape (N,4)],
list[tuple[int, int]]).  Coordinates may include non-ZZ[phi] irrationals
when the underlying 3D shape (snub cube, hexagon, etc.) requires them.
The kernel sweep is agnostic to coordinate ring; non-ZZ[phi]^4 inputs
simply yield zero zomeable projections.

Naming convention for output folder slugs:
  polyhedral_prism(name)    -> f"{name}_prism"             (e.g. "icosahedron_prism")
  duoprism(p, q)            -> f"duoprism_{min(p,q)}_{max(p,q)}"
  antiprismatic_prism(n)    -> f"{n}_antiprismatic_prism"
"""

from __future__ import annotations

import math
import numpy as np

from uniform_polyhedra import get_polyhedron, expected_VE


# ---------------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------------- #
def _edges_at(V, d2, tol=1e-5):
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
    return _edges_at(V, dmin2, tol=max(tol, abs(dmin2) * 1e-9))


# ---------------------------------------------------------------------- #
# Family A: polyhedral prism
# ---------------------------------------------------------------------- #
def polyhedral_prism(name: str, h: float | None = None):
    """4D polytope P x [-h, +h] where P is the named uniform polyhedron.

    Returns (V_4d, edges_4d).  V_4d has shape (2 * |V_P|, 4).

    Edge structure:
      * |E_P| edges at z = +h (top face copy)
      * |E_P| edges at z = -h (bottom face copy)
      * |V_P| vertical edges connecting (v, +h) to (v, -h)
    Total: 2 |E_P| + |V_P|.

    By default chooses h so the vertical edge length equals the
    polyhedron's smallest edge length, making the prism a *uniform*
    4-polytope (all edges equal length).
    """
    V3, edges3 = get_polyhedron(name)
    # Default h = (edge_length of P) / 2 so vertical edge = polyhedron edge
    if h is None:
        # smallest pairwise distance in V3
        n = len(V3)
        dmin2 = float("inf")
        for i in range(n):
            for j in range(i + 1, n):
                d = V3[i] - V3[j]
                d2 = float(d @ d)
                if 1e-12 < d2 < dmin2:
                    dmin2 = d2
        h = 0.5 * math.sqrt(dmin2)
    nv3 = len(V3)
    V4 = np.zeros((2 * nv3, 4), dtype=float)
    V4[:nv3, :3] = V3
    V4[:nv3, 3] = +h
    V4[nv3:, :3] = V3
    V4[nv3:, 3] = -h
    edges = []
    # top copy
    for (i, j) in edges3:
        edges.append((i, j))
    # bottom copy
    for (i, j) in edges3:
        edges.append((i + nv3, j + nv3))
    # vertical struts
    for i in range(nv3):
        edges.append((i, i + nv3))
    return V4, edges


# ---------------------------------------------------------------------- #
# Family B: duoprism {p} x {q}
# ---------------------------------------------------------------------- #
def duoprism(p: int, q: int):
    """{p}-gon x {q}-gon in R^4.

    Vertices: (cos(2*pi*i/p), sin(2*pi*i/p), cos(2*pi*j/q), sin(2*pi*j/q))
    for i in [0, p), j in [0, q).  Total p*q vertices.

    Edges:
      i -> (i+1) mod p, same j:    pq edges    (along p-polygon direction)
      j -> (j+1) mod q, same i:    pq edges    (along q-polygon direction)
    Total: 2*p*q edges.
    """
    if p < 3 or q < 3:
        raise ValueError(f"duoprism requires p,q >= 3, got ({p},{q})")
    V = np.zeros((p * q, 4), dtype=float)
    angle_p = [2.0 * math.pi * i / p for i in range(p)]
    angle_q = [2.0 * math.pi * j / q for j in range(q)]
    cos_p = [math.cos(a) for a in angle_p]
    sin_p = [math.sin(a) for a in angle_p]
    cos_q = [math.cos(a) for a in angle_q]
    sin_q = [math.sin(a) for a in angle_q]
    idx = lambda i, j: i * q + j
    for i in range(p):
        for j in range(q):
            V[idx(i, j)] = [cos_p[i], sin_p[i], cos_q[j], sin_q[j]]
    edges = []
    for i in range(p):
        for j in range(q):
            edges.append((idx(i, j), idx((i + 1) % p, j)))
            edges.append((idx(i, j), idx(i, (j + 1) % q)))
    # remove possible duplicates (won't happen for p>=3,q>=3)
    edges = [(min(a, b), max(a, b)) for (a, b) in edges]
    edges = sorted(set(edges))
    return V, edges


# ---------------------------------------------------------------------- #
# Family C: n-gonal antiprismatic prism
# ---------------------------------------------------------------------- #
def _pentagonal_antiprism_icosahedral():
    """Pentagonal antiprism in ZZ[phi]^3 as the 10 non-polar vertices of a
    canonical icosahedron.

    Icosahedron vertices: (0, +-1, +-phi), (+-1, +-phi, 0), (+-phi, 0, +-1).
    Picking a 5-fold axis through (0, 1, phi) and (0, -1, -phi) leaves 10
    non-polar vertices that form a regular pentagonal antiprism with edge
    length 2 (matching the icosahedron edge length).
    """
    p = (1.0 + 5.0 ** 0.5) / 2.0
    all_v = [
        (0, +1, +p), (0, +1, -p), (0, -1, +p), (0, -1, -p),
        (+1, +p, 0), (+1, -p, 0), (-1, +p, 0), (-1, -p, 0),
        (+p, 0, +1), (+p, 0, -1), (-p, 0, +1), (-p, 0, -1),
    ]
    poles = {(0, +1, +p), (0, -1, -p)}
    non_polar = [v for v in all_v if v not in poles]
    return np.array(non_polar, dtype=float)


def antiprismatic_prism(n: int):
    """n-gonal antiprismatic prism: (A_n) x [-h, +h] where A_n is the
    3D n-antiprism.

    Special case n=5: use the icosahedral embedding (10 non-polar
    icosahedron vertices, all in ZZ[phi]^3) with prism height h4 = 1
    (matching half the icosahedron edge length). This embedding is the
    one that can yield zomeable projections in the 4D sweep.

    General n: standard cylindrical antiprism + cylindrical prism. For
    n != 5, the 3D antiprism is not embeddable in ZZ[phi]^3 anyway
    (cos/sin(pi/n) require quadratic extensions outside ZZ[phi]), so
    these will simply yield zero zomeable projections from the sweep.

    Vertices (4n total):
      * 3D antiprism vertices at w = +h4: 2n verts
      * 3D antiprism vertices at w = -h4: 2n verts
    """
    if n < 3:
        raise ValueError(f"antiprismatic_prism requires n >= 3, got {n}")

    if n == 5:
        # Icosahedral PAP embedding in ZZ[phi]^3.
        V3 = _pentagonal_antiprism_icosahedral()
        # Edge length on icosahedron = 2, so antiprism edge = 2, prism
        # half-height = 1 makes the 4D prism uniform.
        h4 = 1.0
        edge_d2 = 4.0
        # Build full 4D coords first, then detect 4D edges geometrically
        # below.
    else:
        edge_ng = 2.0 * math.sin(math.pi / n)
        h3 = math.sqrt(max(0.0,
                           (math.cos(math.pi / n) - math.cos(2.0 * math.pi / n)) / 2.0))
        h4 = edge_ng / 2.0
        V3 = []
        for i in range(n):
            a = 2.0 * math.pi * i / n
            V3.append([math.cos(a), math.sin(a), -h3])
            # bottom (n verts)
        for i in range(n):
            a = 2.0 * math.pi * i / n + math.pi / n
            V3.append([math.cos(a), math.sin(a), +h3])
            # top (n verts)
        V3 = np.array(V3, dtype=float)
        edge_d2 = edge_ng * edge_ng

    n3 = len(V3)
    V4 = np.zeros((2 * n3, 4), dtype=float)
    V4[:n3, :3] = V3
    V4[:n3, 3] = +h4
    V4[n3:, :3] = V3
    V4[n3:, 3] = -h4

    # Compute edges geometrically by minimum 4D distance.
    # In the icosahedral PAP, all antiprism edges have length 2 and the
    # prism's vertical struts also have length 2 (since 2*h4 = 2). So all
    # 4D edges share the same length, and a single distance-based scan
    # captures all of them. For cylindrical antiprisms the antiprism
    # edges and prism verticals have the same length too (since
    # h4 = edge_ng/2 makes the vertical strut length 2*h4 = edge_ng).
    edges = []
    nV = len(V4)
    d2 = 0.0
    # Find the actual minimum pair distance squared
    min_d2 = None
    for i in range(nV):
        for j in range(i + 1, nV):
            d = V4[i] - V4[j]
            v = float(d @ d)
            if v > 1e-9 and (min_d2 is None or v < min_d2 - 1e-9):
                min_d2 = v
    for i in range(nV):
        for j in range(i + 1, nV):
            d = V4[i] - V4[j]
            v = float(d @ d)
            if abs(v - min_d2) < 1e-6:
                edges.append((i, j))
    return V4, edges


# ---------------------------------------------------------------------- #
# Slug helpers
# ---------------------------------------------------------------------- #
def polyhedral_prism_slug(name: str) -> str:
    return f"{name}_prism"


def duoprism_slug(p: int, q: int) -> str:
    pp, qq = (p, q) if p <= q else (q, p)
    return f"duoprism_{pp}_{qq}"


def antiprismatic_prism_slug(n: int) -> str:
    return f"{n}_antiprismatic_prism"
