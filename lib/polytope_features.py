"""Feature extraction for 4D convex polytopes used by the Wythoff sweep.

Given a polytope's 4D vertex set V and edge list E, this module extracts
the *feature directions* (unit vectors from the centroid through each
vertex / edge midpoint / 2-face centroid / 3-cell centroid) and,
where applicable, classifies the cell or face by its standard polytope
name (tetrahedron, truncated_tetrahedron, hexagonal_prism, ...).

This lets us classify a kernel direction k against a polytope's
features as one of:

    vertex_first
    cell_first[_<celltype>]
    face_first[_<polygon>]
    edge_first
    oblique

(in priority order).

Implementation: scipy.spatial.ConvexHull on the 4D vertices gives
3-cell facets (tetrahedral simplices, grouped by hyperplane equation
into actual polyhedral cells).  For each cell, the vertices are
projected via SVD into a 3D frame in their hyperplane and a 3D
ConvexHull gives the 2D faces of that cell (similarly grouped by
hyperplane).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, List, Tuple

import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.qhull import QhullError


# ---------------------------------------------------------------------------
# Lookup tables: face-vector -> standard polyhedron / polygon name.
# ---------------------------------------------------------------------------

POLYGON_NAMES = {
    3: "triangle",
    4: "square",
    5: "pentagon",
    6: "hexagon",
    8: "octagon",
    10: "decagon",
}

# Each cell is identified by the multiset of its face polygons.
# Stored as a sorted tuple of (n_sides, count) pairs.
CELL_NAMES = {
    ((3, 4),): "tetrahedron",
    ((4, 6),): "cube",
    ((3, 8),): "octahedron",
    ((3, 20),): "icosahedron",
    ((5, 12),): "dodecahedron",
    ((3, 4), (6, 4)): "truncated_tetrahedron",
    ((3, 8), (8, 6)): "truncated_cube",
    ((4, 6), (6, 8)): "truncated_octahedron",
    ((3, 20), (10, 12)): "truncated_dodecahedron",
    ((5, 12), (6, 20)): "truncated_icosahedron",
    ((3, 8), (4, 6)): "cuboctahedron",
    ((3, 20), (5, 12)): "icosidodecahedron",
    ((3, 8), (4, 18)): "rhombicuboctahedron",
    ((3, 20), (4, 30), (5, 12)): "rhombicosidodecahedron",
    ((4, 12), (6, 8), (8, 6)): "truncated_cuboctahedron",
    ((4, 30), (6, 20), (10, 12)): "truncated_icosidodecahedron",
    ((3, 2), (4, 3)): "triangular_prism",
    ((4, 5), (5, 2)): "pentagonal_prism",
    ((4, 6), (6, 2)): "hexagonal_prism",
    ((4, 7), (7, 2)): "heptagonal_prism",
    ((4, 8), (8, 2)): "octagonal_prism",
    ((4, 9), (9, 2)): "enneagonal_prism",
    ((4, 10), (10, 2)): "decagonal_prism",
    # n-gonal antiprism for n>=4 (n=3 antiprism = octahedron, listed above).
    ((3, 8), (4, 2)): "square_antiprism",
    ((3, 10), (5, 2)): "pentagonal_antiprism",
    ((3, 12), (6, 2)): "hexagonal_antiprism",
    ((3, 14), (7, 2)): "heptagonal_antiprism",
    ((3, 16), (8, 2)): "octagonal_antiprism",
    ((3, 18), (9, 2)): "enneagonal_antiprism",
    ((3, 20), (10, 2)): "decagonal_antiprism",
}


def _polygon_name(n: int) -> str:
    return POLYGON_NAMES.get(n, f"polygon{n}")


def _cell_name_from_face_sig(face_sig: Tuple[Tuple[int, int], ...],
                             n_vertices: int) -> str:
    """face_sig: sorted tuple of (n_sides, count).  Returns a known
    polyhedron name or a fallback ``polyV{n}_F{n}``."""
    name = CELL_NAMES.get(face_sig)
    if name is not None:
        return name
    n_faces = sum(c for _, c in face_sig)
    return f"polyV{n_vertices}F{n_faces}"


# ---------------------------------------------------------------------------
# ConvexHull helpers.
# ---------------------------------------------------------------------------

def _group_simplices_by_hyperplane(
    equations: np.ndarray,
    tol_decimals: int = 5,
) -> List[List[int]]:
    """Group simplex indices whose hyperplane equation rounds to the same
    quantised tuple.  Returns a list of index lists."""
    groups: dict[tuple, list[int]] = defaultdict(list)
    for i, eq in enumerate(equations):
        key = tuple(np.round(eq, tol_decimals).tolist())
        groups[key].append(i)
    return list(groups.values())


def _project_to_3d(V_global: np.ndarray,
                   vertex_indices: Iterable[int]
                   ) -> Tuple[np.ndarray, np.ndarray]:
    """Project V_global[vertex_indices] (which lie in a 3D hyperplane of
    R^4) into a 3D frame on that hyperplane.

    Returns (coords3 (N, 3), centroid_4d (4,))."""
    pts = V_global[list(vertex_indices)]
    centroid = pts.mean(axis=0)
    centered = pts - centroid
    _, _, Vt = np.linalg.svd(centered, full_matrices=False)
    coords3 = centered @ Vt[:3].T
    return coords3, centroid


# ---------------------------------------------------------------------------
# Feature extraction.
# ---------------------------------------------------------------------------

class PolytopeFeatures:
    """Bundle of feature directions for a 4D polytope.

    Attributes (each direction is a 4-vector in the same coord system
    as ``V``; not necessarily unit):

        vertex_dirs:    (n_v, 4)
        edge_mid_dirs:  (n_e, 4)
        face_dirs:      list of (centroid (4,), polygon_name)
        cell_dirs:      list of (centroid (4,), cell_name)
    """

    def __init__(self, vertex_dirs, edge_mid_dirs, face_dirs, cell_dirs):
        self.vertex_dirs = np.asarray(vertex_dirs, dtype=float)
        self.edge_mid_dirs = np.asarray(edge_mid_dirs, dtype=float)
        self.face_dirs = list(face_dirs)
        self.cell_dirs = list(cell_dirs)


def extract_features(V, E,
                     hull_tol_decimals: int = 5,
                     skip_cells_above: int | None = None
                     ) -> PolytopeFeatures:
    """Extract feature directions and cell/face types for a 4D convex
    polytope.

    Parameters
    ----------
    V : (n, 4) array-like
        4D vertices, in any frame (need not be unit-radius).  The
        polytope is assumed to be the convex hull of V (uniform
        polytopes always satisfy this).
    E : iterable of (i, j)
        Edge indices into V.  Used only for edge-midpoint directions.
    hull_tol_decimals : int
        Quantisation for grouping simplices by hyperplane.
    skip_cells_above : int or None
        If set, skip cell/face extraction when len(V) exceeds this
        value (ConvexHull on very large 4D point sets can be slow).
        Only vertex and edge features will be filled.
    """
    V = np.asarray(V, dtype=float)
    n = len(V)
    edge_mids = np.array([0.5 * (V[i] + V[j]) for (i, j) in E],
                         dtype=float) if len(E) else np.zeros((0, 4))

    if skip_cells_above is not None and n > skip_cells_above:
        return PolytopeFeatures(V, edge_mids, [], [])

    try:
        hull = ConvexHull(V, qhull_options="Qt")
    except QhullError:
        return PolytopeFeatures(V, edge_mids, [], [])

    # Group 4D simplices into 3D cells by hyperplane equation.
    cell_groups = _group_simplices_by_hyperplane(
        hull.equations, hull_tol_decimals)

    cell_dirs: list[tuple[np.ndarray, str]] = []
    face_dirs: list[tuple[np.ndarray, str]] = []
    seen_face_keys: set[tuple[int, ...]] = set()

    for sidxs in cell_groups:
        verts = set()
        for s in sidxs:
            verts.update(int(i) for i in hull.simplices[s])
        verts = sorted(verts)
        if len(verts) < 4:
            continue
        cell_centroid = V[verts].mean(axis=0)

        # Project this cell's vertices to 3D and run a 3D hull.
        try:
            coords3, _ = _project_to_3d(V, verts)
            h3 = ConvexHull(coords3, qhull_options="Qt")
        except (QhullError, np.linalg.LinAlgError):
            continue
        face_groups = _group_simplices_by_hyperplane(
            h3.equations, hull_tol_decimals)

        face_sig: dict[int, int] = defaultdict(int)
        for fsimps in face_groups:
            local_verts = set()
            for s in fsimps:
                local_verts.update(int(i) for i in h3.simplices[s])
            local_verts = sorted(local_verts)
            n_sides = len(local_verts)
            face_sig[n_sides] += 1
            global_idxs = tuple(sorted(verts[i] for i in local_verts))
            if global_idxs in seen_face_keys:
                continue
            seen_face_keys.add(global_idxs)
            face_centroid = V[list(global_idxs)].mean(axis=0)
            face_dirs.append((face_centroid, _polygon_name(n_sides)))

        face_sig_tuple = tuple(sorted(face_sig.items()))
        cell_name = _cell_name_from_face_sig(face_sig_tuple, len(verts))
        cell_dirs.append((cell_centroid, cell_name))

    return PolytopeFeatures(V, edge_mids, face_dirs, cell_dirs)


# ---------------------------------------------------------------------------
# Kernel classification.
# ---------------------------------------------------------------------------

def _is_parallel(k_unit: np.ndarray, d: np.ndarray, tol: float) -> bool:
    nd = float(np.linalg.norm(d))
    if nd < 1e-12:
        return False
    cos = float(k_unit @ d) / nd
    # Parallel here means *positive* cosine ~ +1.  For non-centrally-
    # symmetric polytopes (e.g. 5-cell) the antipodal direction lies
    # through a cell centroid, not a vertex, so we want each feature
    # listed only on the side where it actually points.
    return cos > 1.0 - tol


def classify_kernel(kernel,
                    features: PolytopeFeatures,
                    tol: float = 5e-3
                    ) -> Tuple[str, str | None]:
    """Classify kernel direction ``k`` against a polytope's features.

    Returns a (label, subtype_or_None) pair.  Priority order:
    vertex_first > cell_first > face_first > edge_first > oblique.
    """
    k = np.asarray(kernel, dtype=float)
    nk = float(np.linalg.norm(k))
    if nk < 1e-12:
        return ("oblique", None)
    ku = k / nk

    for v in features.vertex_dirs:
        if _is_parallel(ku, v, tol):
            return ("vertex_first", None)
    for c, ctype in features.cell_dirs:
        if _is_parallel(ku, c, tol):
            return ("cell_first", ctype)
    for f, ftype in features.face_dirs:
        if _is_parallel(ku, f, tol):
            return ("face_first", ftype)
    for em in features.edge_mid_dirs:
        if _is_parallel(ku, em, tol):
            return ("edge_first", None)
    return ("oblique", None)


# ---------------------------------------------------------------------------
# Filename helpers.
# ---------------------------------------------------------------------------

def label_basename(label: str, subtype: str | None,
                   index: int | None = None) -> str:
    """Build a filename slug from a (label, subtype) pair, optionally
    suffixed with ``_<index>`` to disambiguate multiple shapes that
    classify identically within the same polytope."""
    if label == "oblique":
        idx_str = f"_{index:02d}" if index is not None else ""
        return f"oblique{idx_str}"
    if subtype:
        base = f"{label}_{subtype}"
    else:
        base = label
    if index is not None:
        return f"{base}_{index:02d}"
    return base
