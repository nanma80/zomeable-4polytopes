"""Vertex/edge specifications for the 6 convex regular 4-polytopes.

Each function returns (V, edges) where V is an Nx4 numpy array (float)
and edges is a list of (i, j) index pairs of the edges (i<j).
Where a polytope has multiple natural embeddings (e.g. dual rescalings),
multiple functions are provided.

References:
  https://en.wikipedia.org/wiki/Regular_4-polytope
  https://en.wikipedia.org/wiki/Convex_regular_4-polytope
"""
import numpy as np
from itertools import combinations, product

phi = (1 + 5**0.5) / 2


def _edges_at(V, d2, tol=1e-7):
    """All unordered index pairs whose squared Euclidean distance is d2."""
    n = len(V)
    out = []
    for i in range(n):
        for j in range(i+1, n):
            d = V[i] - V[j]
            if abs(d @ d - d2) < tol:
                out.append((i, j))
    return out


# ---------- 5-cell (4-simplex) ----------
def fivecell():
    """Regular 5-cell embedded in R^4 with one vertex on the +x4 axis
    and the opposite tetrahedral face at x4 = const < 0.

    Using integer-scaled coordinates so the embedding lives in Z[phi]^4
    (specifically Z[phi] = Z + Z*phi, since sqrt(5) = 2*phi - 1).

    v_5 = (0, 0, 0, 8*phi - 4)
    v_1 = (5, 5, 5, 1 - 2*phi)
    v_2 = (5, -5, -5, 1 - 2*phi)
    v_3 = (-5, 5, -5, 1 - 2*phi)
    v_4 = (-5, -5, 5, 1 - 2*phi)

    Squared edge length = 200 in this scale.

    Projecting along (0, 0, 0, 1) collapses v_5 to the centroid of
    v_1..v_4 (origin), giving a 'tetrahedron + center' image with all
    10 edges on default zometool axes (4 yellow + 6 green).
    """
    sqrt5 = 2 * phi - 1  # exact in float arithmetic via the standard golden-ratio definition
    v5 = [0.0, 0.0, 0.0, 4 * sqrt5]
    v1 = [ 5.0,  5.0,  5.0, -sqrt5]
    v2 = [ 5.0, -5.0, -5.0, -sqrt5]
    v3 = [-5.0,  5.0, -5.0, -sqrt5]
    v4 = [-5.0, -5.0,  5.0, -sqrt5]
    V = np.array([v1, v2, v3, v4, v5], dtype=float)
    edges = _edges_at(V, 200.0, tol=1e-5)  # all 10 pairs
    return V, edges


# ---------- 8-cell (tesseract) ----------
def tesseract():
    """8-cell: 16 vertices (+/-1)^4, edges along axis directions."""
    V = np.array(list(product((-1, 1), repeat=4)), dtype=float)
    edges = _edges_at(V, 4.0)  # squared edge length = 4 (one coord differs by 2)
    return V, edges


# ---------- 16-cell (orthoplex) ----------
def orthoplex():
    """16-cell: 8 vertices +/- e_i, edges between non-antipodal pairs."""
    V = []
    for i in range(4):
        for s in (1, -1):
            v = [0, 0, 0, 0]
            v[i] = s
            V.append(v)
    V = np.array(V, dtype=float)
    edges = _edges_at(V, 2.0)  # edge between e_i and e_j (i!=j), length sqrt(2)
    return V, edges


# ---------- 24-cell ----------
def cell24_long_root():
    """24-cell, D4 'long root' embedding: 24 vertices = (+/-1, +/-1, 0, 0) perms."""
    V = []
    for i, j in combinations(range(4), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0, 0, 0, 0]
                v[i] = si
                v[j] = sj
                V.append(v)
    V = np.array(V, dtype=float)
    edges = _edges_at(V, 2.0)
    return V, edges


def cell24_short_root():
    """24-cell, F4 dual 'short root' embedding: 8 axis vertices +/-e_i and
    16 vertices (+/-1, +/-1, +/-1, +/-1)/2.  Edge length 1."""
    V = []
    for i in range(4):
        for s in (1, -1):
            v = [0, 0, 0, 0]
            v[i] = s
            V.append(v)
    for sx in product((1, -1), repeat=4):
        V.append([s * 0.5 for s in sx])
    V = np.array(V, dtype=float)
    edges = _edges_at(V, 1.0)
    return V, edges


# ---------- 600-cell ----------
def cell600():
    """600-cell: 120 vertices = 24-cell vertices (short-root scale) plus 96
    'snub' vertices = even permutations of (+/-1/2, +/-phi/2, +/-1/(2 phi), 0).

    Edge length = 1/phi (when the 24-cell vertices form the short-root inner shell).
    Reference: Coxeter, Regular Polytopes."""
    V = []
    # 8 axis verts +/- e_i (radius 1)
    for i in range(4):
        for s in (1, -1):
            v = [0, 0, 0, 0]
            v[i] = s
            V.append(v)
    # 16 verts (+/-1, +/-1, +/-1, +/-1)/2 (radius 1)
    for sx in product((1, -1), repeat=4):
        V.append([s * 0.5 for s in sx])
    # 96 'snub' verts: even permutations of (+/-phi, +/-1, +/-1/phi, 0)/2
    base = [phi, 1.0, 1.0 / phi, 0.0]
    # Determine the 12 even permutations of [a,b,c,d] (Klein four-group orbit
    # under A_4 acting on positions).
    from itertools import permutations
    perms = []
    seen = set()
    for p in permutations(range(4)):
        # parity
        sign = 1
        for i in range(4):
            for j in range(i+1, 4):
                if p[i] > p[j]:
                    sign *= -1
        if sign == 1:
            perms.append(p)
    assert len(perms) == 12
    for p in perms:
        for sx in product((1, -1), repeat=3):  # only sign the 3 nonzero entries
            v = [0.0, 0.0, 0.0, 0.0]
            sx_full = list(sx) + [1]  # placeholder for the zero entry
            # locate which output position holds the zero
            for k in range(4):
                src = p.index(k)
                v[k] = sx_full[src] * base[src] / 2 if base[src] != 0 else 0.0
            V.append(v)
    V = np.array(V, dtype=float)
    # Verify radius
    radii = np.linalg.norm(V, axis=1)
    assert np.allclose(radii, 1.0), f"600-cell radii not 1: {set(np.round(radii, 6))}"
    # Edge length: 1/phi
    edges = _edges_at(V, (1.0 / phi) ** 2, tol=1e-6)
    return V, edges


# ---------- 120-cell ----------
def cell120():
    """120-cell: 600 vertices.  Standard coordinates, even permutations of:
        (0, 0, +/-2, +/-2)                  -- 24
        (+/-1, +/-1, +/-1, +/-sqrt(5))      -- 64
        (+/-phi^-2, +/-phi, +/-phi, +/-phi) -- 64
        (+/-phi^-1, +/-phi^-1, +/-phi^-1, +/-phi^2) -- 64
    plus all even permutations of:
        (0, +/-phi^-2, +/-1, +/-phi^2)      -- 96
        (0, +/-phi^-1, +/-phi, +/-sqrt(5))  -- 96
        (+/-phi^-1, +/-1, +/-phi, +/-2)     -- 192
    Total = 24+64+64+64+96+96+192 = 600.  Radius = 2*sqrt(2).  Edge = 3-sqrt(5) = 2/phi^2.
    Reference: https://en.wikipedia.org/wiki/120-cell"""
    from itertools import permutations
    sqrt5 = 5 ** 0.5
    iphi = 1 / phi
    iphi2 = 1 / (phi * phi)
    phi2 = phi * phi

    def even_perms(seq):
        out = []
        for p in permutations(range(4)):
            sign = 1
            for i in range(4):
                for j in range(i+1, 4):
                    if p[i] > p[j]:
                        sign *= -1
            if sign == 1:
                out.append([seq[p.index(k)] for k in range(4)])
        # dedup
        return list({tuple(x) for x in out})

    def all_signs(seq):
        out = set()
        for s in product((1, -1), repeat=4):
            out.add(tuple(si * vi for si, vi in zip(s, seq)))
        return list(out)

    V = set()
    # all permutations sets (24-cell-like outer parts) -- ALL permutations
    for tup in [(0, 0, 2, 2), (1, 1, 1, sqrt5),
                (iphi2, phi, phi, phi),
                (iphi, iphi, iphi, phi2)]:
        for p in permutations(tup):
            for s in all_signs(p):
                V.add(tuple(round(x, 12) for x in s))
    # even permutations sets
    for tup in [(0, iphi2, 1, phi2),
                (0, iphi, phi, sqrt5),
                (iphi, 1, phi, 2)]:
        for ep in even_perms(tup):
            for s in all_signs(ep):
                V.add(tuple(round(x, 12) for x in s))
    V = np.array(sorted(V), dtype=float)
    radii = np.linalg.norm(V, axis=1)
    assert np.allclose(radii, np.sqrt(8)), f"120-cell radii: {set(np.round(radii,4))}"
    # Edge length squared = (3 - sqrt(5))^2 = 14 - 6 sqrt(5)
    edge2 = (3 - sqrt5) ** 2
    edges = _edges_at(V, edge2, tol=1e-5)
    return V, edges


# ---------- snub 24-cell (non-Wythoff!) ----------
def snub_24cell():
    """Snub 24-cell {3,4,3}/2: 96 vertices = the 96 of the 600-cell's
    120 vertices that are NOT in the inscribed 24-cell. Equivalently,
    even permutations of (+/-phi, +/-1, +/-1/phi, 0)/2, on radius-1 sphere.

    Symmetry: D4 (order 1152), index 6 in F4. Non-Wythoff.
    96 vertices, 432 edges (all of length 1/phi, same as 600-cell).
    Reference: https://en.wikipedia.org/wiki/Snub_24-cell"""
    from itertools import permutations
    base = [phi, 1.0, 1.0 / phi, 0.0]
    # 12 even permutations of [a,b,c,d]
    even_perms = []
    for p in permutations(range(4)):
        sign = 1
        for i in range(4):
            for j in range(i+1, 4):
                if p[i] > p[j]:
                    sign *= -1
        if sign == 1:
            even_perms.append(p)
    assert len(even_perms) == 12
    V = []
    for p in even_perms:
        for sx in product((1, -1), repeat=3):
            v = [0.0, 0.0, 0.0, 0.0]
            sx_full = list(sx) + [1]  # placeholder for the zero entry
            for k in range(4):
                src = p.index(k)
                v[k] = sx_full[src] * base[src] / 2 if base[src] != 0 else 0.0
            V.append(v)
    V = np.array(V, dtype=float)
    radii = np.linalg.norm(V, axis=1)
    assert np.allclose(radii, 1.0), f"snub 24-cell radii not 1: {set(np.round(radii, 6))}"
    edges = _edges_at(V, (1.0 / phi) ** 2, tol=1e-6)
    return V, edges


def grand_antiprism():
    """Grand antiprism: 100 vertices, 500 edges. Diminished 600-cell formed
    by removing 20 vertices that lie on two interlocking decagonal Hopf
    rings (great decagons with no edge connecting them).

    Symmetry: order 400 (the "ionic-diminished" subgroup of H4).
    Non-Wythoff. Discovered by Conway-Guy 1965.
    Reference: https://en.wikipedia.org/wiki/Grand_antiprism"""
    V600, E600 = cell600()
    V = np.array(V600); n = len(V)
    cos36 = phi / 2.0
    # Enumerate great decagons: 2-planes through origin containing 10 vertices.
    decagons = set()
    for i in range(n):
        for j in range(i + 1, n):
            if abs(V[i] @ V[j] - cos36) < 1e-6:
                v = V[i]; w = V[j]
                e1 = v
                wp = w - cos36 * v
                e2 = wp / np.linalg.norm(wp)
                members = []
                for k in range(n):
                    a = V[k] @ e1; b = V[k] @ e2
                    resid = V[k] - a * e1 - b * e2
                    if np.linalg.norm(resid) < 1e-6 and abs(a * a + b * b - 1) < 1e-6:
                        members.append(k)
                if len(members) == 10:
                    decagons.add(frozenset(members))
    dec_list = sorted(decagons, key=lambda d: tuple(sorted(d)))
    # Pick the first disjoint pair of Hopf-orthogonal decagons that yields
    # the canonical GA (uniform vertex degree 10). Equivalently: 0 cross-
    # edges between the two decagons AND each kept vertex incident to
    # exactly 2 removed vertices in the parent 600-cell. There are 36 such
    # inscribed GAs in the 600-cell. Note: requiring "500 within-kept edges"
    # alone is NOT sufficient — 360 non-Hopf disjoint pairs happen to give
    # 500 edges with degree distribution (8,20)+(10,60)+(12,20), which is
    # NOT vertex-transitive and NOT GA.
    edge_lookup = set()
    for (a, b) in E600:
        edge_lookup.add((a, b)); edge_lookup.add((b, a))
    chosen = None
    for i in range(len(dec_list)):
        for j in range(i + 1, len(dec_list)):
            if dec_list[i] & dec_list[j]:
                continue
            # 0 cross-edges (necessary for orthogonal Hopf pair)
            cross = sum(1 for a in dec_list[i] for b in dec_list[j]
                        if (a, b) in edge_lookup)
            if cross != 0:
                continue
            # uniform degree 10 (sufficient: vertex-transitive GA)
            rem = dec_list[i] | dec_list[j]
            deg = {k: 0 for k in range(n) if k not in rem}
            for (a, b) in E600:
                if a in deg and b in deg:
                    deg[a] += 1; deg[b] += 1
            if all(d == 10 for d in deg.values()):
                chosen = rem
                break
        if chosen is not None:
            break
    if chosen is None:
        raise RuntimeError("grand_antiprism: no canonical orthogonal Hopf "
                           "decagon pair found")
    kept = [k for k in range(n) if k not in chosen]
    idx_map = {old: new for new, old in enumerate(kept)}
    V_GA = V[kept]
    E_GA = [(idx_map[a], idx_map[b]) for (a, b) in E600
            if a in idx_map and b in idx_map]
    assert len(V_GA) == 100, f"GA verts: {len(V_GA)}"
    assert len(E_GA) == 500, f"GA edges: {len(E_GA)}"
    return V_GA, E_GA


# Catalogue
POLYTOPES = {
    "5cell":          [("standard", fivecell)],
    "8cell":          [("tesseract", tesseract)],
    "16cell":         [("orthoplex", orthoplex)],
    "24cell":         [("long_root", cell24_long_root),
                       ("short_root", cell24_short_root)],
    "120cell":        [("standard", cell120)],
    "600cell":        [("standard", cell600)],
    "snub24cell":     [("standard", snub_24cell)],
    "grand_antiprism":[("standard", grand_antiprism)],
}


if __name__ == "__main__":
    # Self-test: print vertex/edge counts for each polytope.
    for name, embeddings in POLYTOPES.items():
        for label, fn in embeddings:
            V, E = fn()
            print(f"  {name:8s} ({label:12s}): {len(V):4d} verts, {len(E):5d} edges")
