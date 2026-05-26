"""Canonical nD vertex/edge sets for the Gosset polytopes 2_21 / 3_21 / 4_21,
working directly in their natural Euclidean embeddings (no 4D intermediate).

Construction (standard, e.g. Coxeter / Wikipedia "4_21 polytope"):

4_21 (E_8 root polytope, 240 vertices, 6720 edges) in 8D:
  Type A: 112 vectors (±1, ±1, 0, 0, 0, 0, 0, 0) (perm + signs)
  Type B: 128 vectors (±1/2)^8 with EVEN number of minus signs
  Common norm: |v|² = 2  for both types
  Edges: pairs (v, w) with |v-w|² = 2  ⇔  v·w = 1 (since |v|=|w|=√2).
         Total = 6720.

3_21 (E_7 minuscule polytope, 56 vertices, 756 edges):
  = vertex figure of 4_21 at any vertex v_0.  Vertices are the
    56 neighbors of v_0 in 4_21, sitting in the 7D hyperplane
    {y : v_0 · y = 1} (equivalently {x = y - v_0 : v_0·x = -1, |x|=√2}).
  Edges inherited from 4_21.

2_21 (E_6 polytope, 27 vertices, 216 edges):
  = vertex figure of 3_21 = neighbors-of-w_0 inside 3_21
    for any w_0 in 3_21.

All edges of all three polytopes have |v-w|² = 2 in the natural embedding.
"""
from __future__ import annotations
import itertools
import numpy as np


# ---------- 4_21 in 8D ----------

def _build_4_21_vertices():
    verts = []
    # 112 type-A
    for i in range(8):
        for j in range(i+1, 8):
            for si in (1, -1):
                for sj in (1, -1):
                    v = np.zeros(8, dtype=float)
                    v[i] = si
                    v[j] = sj
                    verts.append(v)
    # 128 type-B
    for signs in itertools.product((1, -1), repeat=8):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            v = np.array(signs, dtype=float) / 2
            verts.append(v)
    return np.array(verts)


def _edges_from_vertex_set(V, edge_len2=2.0, tol=1e-9):
    """All pairs (i,j) with |V_i - V_j|^2 = edge_len2."""
    N = len(V)
    edges = []
    for i in range(N):
        diff = V - V[i]
        d2 = (diff * diff).sum(axis=1)
        for j in range(i+1, N):
            if abs(d2[j] - edge_len2) < tol:
                edges.append((i, j))
    return edges


# ---------- 3_21 as vertex figure ----------

def _build_3_21_from_4_21(V8, v0):
    """3_21 vertices in 8D = neighbors of v0 in 4_21, MINUS v0.
    Returns:
      W7        : (56, 8) array of vectors x = y - v0
      idx       : indices of the 56 neighbors inside V8
    All W7 vectors satisfy v0 · x = -1 and |x|² = 2.
    They span a 7D hyperplane (v0-perp shifted)."""
    # Neighbors at distance sqrt(2) from v0
    diff = V8 - v0
    d2 = (diff * diff).sum(axis=1)
    mask = np.abs(d2 - 2.0) < 1e-9
    idx = np.where(mask)[0]
    assert len(idx) == 56, f'expected 56 neighbors, got {len(idx)}'
    W7 = (V8[idx] - v0)
    return W7, idx


# ---------- 2_21 as vertex figure of vertex figure ----------

def _build_2_21_from_3_21(W7, w0):
    """2_21 vertices = neighbors of w0 inside 3_21 (i.e. 4_21 vertices that
    are simultaneously neighbors of v0 AND neighbors of (v0 + w0)).
    Returns (X6, idx) where X6 are 27 vectors with |x|²=2 and X6 lies in
    a 6D subspace."""
    diff = W7 - w0
    d2 = (diff * diff).sum(axis=1)
    mask = np.abs(d2 - 2.0) < 1e-9
    idx = np.where(mask)[0]
    assert len(idx) == 27, f'expected 27 neighbors, got {len(idx)}'
    X6 = (W7[idx] - w0)
    return X6, idx


def _reduce_to_natural_dim(V_high, target_dim, tol=1e-9):
    """Given vertices in higher-dim ambient space whose affine hull has
    dimension target_dim, return an orthonormal-basis representation in
    target_dim. Vertices are centred at the centroid of the affine hull.
    """
    V_c = V_high - V_high.mean(axis=0)
    U, s, Vh = np.linalg.svd(V_c, full_matrices=False)
    rank = int(np.sum(s > tol))
    assert rank == target_dim, f'rank {rank} != target_dim {target_dim}'
    # Coords in the natural orthonormal basis = U * s
    return (U[:, :target_dim] * s[:target_dim])


# ---------- Public API ----------

V_421 = _build_4_21_vertices()                      # (240, 8)
E_421 = _edges_from_vertex_set(V_421)               # 6720 edges

_V0 = np.array([1, 1, 0, 0, 0, 0, 0, 0], dtype=float)  # any 4_21 vertex
V_321, IDX_321 = _build_3_21_from_4_21(V_421, _V0)  # (56, 8), 7D-affine
E_321 = _edges_from_vertex_set(V_321)               # 756 edges

# Pick a 3_21 vertex; the 'first' one in our enumeration
_W0 = V_321[0]
V_221, IDX_221 = _build_2_21_from_3_21(V_321, _W0)  # (27, 8), 6D-affine
E_221 = _edges_from_vertex_set(V_221)               # 216 edges

# Natural-dimension reductions (centred at the affine-hull centroid):
V_421_8d = V_421 - V_421.mean(axis=0)               # 8D (centred, no reduction)
V_321_7d = _reduce_to_natural_dim(V_321, 7)         # (56, 7)
V_221_6d = _reduce_to_natural_dim(V_221, 6)         # (27, 6)


def info():
    return {
        '4_21': (V_421.shape, len(E_421)),
        '3_21': (V_321.shape, len(E_321)),
        '2_21': (V_221.shape, len(E_221)),
    }


if __name__ == '__main__':
    import pprint
    pprint.pprint(info())
    # quick sanity: all vertices have norm sqrt(2)
    for name, V in [('4_21', V_421), ('3_21', V_321), ('2_21', V_221)]:
        norms2 = (V * V).sum(axis=1)
        print(f'{name}: |v|² range = [{norms2.min():.6f}, {norms2.max():.6f}]')
