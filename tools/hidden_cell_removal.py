"""Generate front-visible derived models by removing hidden 4D cells.

Prototype targets: truncated 16-cell and snub 24-cell.  The derived .vZome
files are filtered copies of the existing full projections: surviving ShowPoint
and JoinPointPair commands are copied verbatim, and hidden ones are omitted.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "lib"
sys.path.insert(0, str(LIB))

from search_engine import _try_align, projection_matrix  # noqa: E402
from wythoff import build_polytope  # noqa: E402
from polytopes import phi, snub_24cell, grand_antiprism  # noqa: E402
from prismatic_polytopes import get_registry  # noqa: E402
from emit_generic import _iter_alignments  # noqa: E402

PHI = (1 + math.sqrt(5)) / 2
SHOW_RE = re.compile(r'<ShowPoint\s+point="([^"]+)"\s*/>')
JOIN_RE = re.compile(r'<JoinPointPair\s+start="([^"]+)"\s+end="([^"]+)"\s*/>')


def frac_value(token: str) -> float:
    if "/" in token:
        num, den = token.split("/", 1)
        return float(num) / float(den)
    return float(token)


def point_value(point: str) -> np.ndarray:
    toks = point.split()
    if len(toks) != 6:
        raise ValueError(f"Expected 6 golden-coordinate tokens, got {point!r}")
    return np.array(
        [frac_value(toks[i]) + frac_value(toks[i + 1]) * PHI for i in (0, 2, 4)],
        dtype=float,
    )


def snap_zphi_float(x: float, tol: float = 1e-5, limit: int = 30) -> float:
    best = (abs(x), 0.0)
    for b in range(-limit, limit + 1):
        a = round(x - b * PHI)
        if abs(a) > limit:
            continue
        value = a + b * PHI
        err = abs(x - value)
        if err < best[0]:
            best = (err, value)
    return best[1] if best[0] <= tol else float(x)


def snap_kernel(kernel: list[float] | tuple[float, ...] | np.ndarray) -> np.ndarray:
    return np.array([snap_zphi_float(float(x)) for x in kernel], dtype=float)


def parse_vzome(path: Path) -> tuple[str, list[str], list[tuple[str, str]]]:
    text = path.read_text(encoding="utf-8")
    points = SHOW_RE.findall(text)
    joins = JOIN_RE.findall(text)
    return text, points, joins


def canonical_pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a <= b else (b, a)


def grouped_cells(V: np.ndarray, decimals: int = 8) -> list[dict]:
    hull = ConvexHull(V, qhull_options="Qt")
    groups: dict[tuple[float, ...], list[int]] = defaultdict(list)
    for idx, eq in enumerate(hull.equations):
        normal = eq[:-1].copy()
        offset = float(eq[-1])
        norm = float(np.linalg.norm(normal))
        if norm == 0:
            raise ValueError("ConvexHull returned zero normal")
        normal /= norm
        offset /= norm
        # ConvexHull orients equations so interior satisfies normal.x + offset <= 0.
        key = tuple(np.round(np.r_[normal, offset], decimals).tolist())
        groups[key].append(idx)

    cells = []
    for key, simplex_indices in groups.items():
        verts: set[int] = set()
        for simplex_index in simplex_indices:
            verts.update(int(i) for i in hull.simplices[simplex_index])
        normal = np.array(key[:4], dtype=float)
        cells.append({"normal": normal, "vertices": frozenset(verts)})
    return cells


def visible_4d_sets(
    V: np.ndarray,
    E: list[tuple[int, int]],
    cells: list[dict],
    kernel: np.ndarray,
    tol: float,
) -> tuple[set[int], set[tuple[int, int]], dict]:
    k = kernel / np.linalg.norm(kernel)
    visible_cells = [cell for cell in cells if float(cell["normal"] @ k) >= -tol]
    hidden_cells = [cell for cell in cells if float(cell["normal"] @ k) < -tol]
    visible_vertices: set[int] = set()
    visible_edges: set[tuple[int, int]] = set()
    edge_set = {canonical_pair(i, j) for i, j in E}
    for cell in visible_cells:
        verts = sorted(cell["vertices"])
        visible_vertices.update(verts)
        for a_pos, a in enumerate(verts):
            for b in verts[a_pos + 1 :]:
                pair = canonical_pair(a, b)
                if pair in edge_set:
                    visible_edges.add(pair)
    stats = {
        "cells_total": len(cells),
        "cells_visible_front_or_equator": len(visible_cells),
        "cells_hidden_back": len(hidden_cells),
        "vertices_4d_visible": len(visible_vertices),
        "edges_4d_visible": len(visible_edges),
    }
    return visible_vertices, visible_edges, stats


def projected_vertices(V: np.ndarray, E: list[tuple[int, int]], kernel: np.ndarray) -> np.ndarray:
    Q = projection_matrix(kernel)
    edge_displacements = np.array([V[j] - V[i] for i, j in E], dtype=float).T
    result = _try_align(Q @ edge_displacements)
    if result is None:
        raise ValueError(f"Could not align projection for kernel {kernel.tolist()}")
    R, _ = result
    return (R @ (Q @ V.T)).T


def _cluster_projected_points(X: np.ndarray, tol: float = 1e-5) -> tuple[np.ndarray, list[int]]:
    reps: list[np.ndarray] = []
    vertex_to_rep: list[int] = []
    for point in X:
        for idx, rep in enumerate(reps):
            if float(np.linalg.norm(point - rep)) <= tol:
                vertex_to_rep.append(idx)
                break
        else:
            reps.append(point)
            vertex_to_rep.append(len(reps) - 1)
    return np.array(reps, dtype=float), vertex_to_rep


def _distance_matrix(points: np.ndarray) -> np.ndarray:
    diff = points[:, None, :] - points[None, :, :]
    return np.linalg.norm(diff, axis=2)


def _normalise_distances(D: np.ndarray) -> np.ndarray:
    positives = D[D > 1e-8]
    if positives.size == 0:
        return D.copy()
    return D / float(positives.min())


def _fit_similarity(source: np.ndarray, target: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    source_center = source.mean(axis=0)
    target_center = target.mean(axis=0)
    source_centered = source - source_center
    target_centered = target - target_center
    H = source_centered.T @ target_centered
    U, singular_values, Vt = np.linalg.svd(H)
    orthogonal = Vt.T @ U.T
    scale = float(singular_values.sum() / np.sum(source_centered * source_centered))
    translation = target_center - scale * (orthogonal @ source_center)
    return scale, orthogonal, translation


def _apply_similarity(points: np.ndarray, scale: float, orthogonal: np.ndarray, translation: np.ndarray) -> np.ndarray:
    return (scale * (orthogonal @ points.T)).T + translation


def _match_collapsed_points(
    X_balls: np.ndarray,
    Y: np.ndarray,
    tol: float,
    profile_tol: float = 1e-4,
) -> tuple[list[int], float]:
    if len(X_balls) != len(Y):
        raise ValueError(f"Collapsed projected points {len(X_balls)} != emitted ShowPoints {len(Y)}")
    n = len(X_balls)
    DX = _normalise_distances(_distance_matrix(X_balls))
    DY = _normalise_distances(_distance_matrix(Y))
    profiles_x = [np.sort(DX[i]) for i in range(n)]
    profiles_y = [np.sort(DY[i]) for i in range(n)]
    candidates = [
        [
            j
            for j, profile in enumerate(profiles_y)
            if float(np.max(np.abs(profile - profiles_x[i]))) <= profile_tol
        ]
        for i in range(n)
    ]
    if any(not c for c in candidates):
        raise ValueError("Distance-profile matching found an unmatched point")

    anchor_order = sorted(range(n), key=lambda i: len(candidates[i]))
    anchors: list[int] = []
    for idx in anchor_order:
        trial = anchors + [idx]
        if len(trial) == 1:
            anchors = trial
        else:
            rank = np.linalg.matrix_rank(X_balls[trial] - X_balls[trial][0], tol=1e-8)
            if rank >= min(3, len(trial) - 1):
                anchors = trial
        if len(anchors) == 4:
            break
    if len(anchors) < 4:
        raise ValueError("Could not choose four affine-independent anchors")

    assignment = [-1] * len(anchors)
    used: set[int] = set()

    def verify_from_anchors() -> tuple[list[int], float] | None:
        source = X_balls[anchors]
        target = Y[assignment]
        scale, orthogonal, translation = _fit_similarity(source, target)
        transformed = _apply_similarity(X_balls, scale, orthogonal, translation)
        distances = np.linalg.norm(transformed[:, None, :] - Y[None, :, :], axis=2)
        nearest = distances.argmin(axis=1)
        residual = float(distances.min(axis=1).max())
        if residual > tol or len(set(int(i) for i in nearest)) != n:
            return None
        # Check the inverse nearest relation too, so no emitted point is skipped.
        inverse_distances = np.linalg.norm(Y[:, None, :] - transformed[None, :, :], axis=2)
        if float(inverse_distances.min(axis=1).max()) > tol:
            return None
        return [int(i) for i in nearest], residual

    def backtrack(pos: int) -> tuple[list[int], float] | None:
        if pos == len(anchors):
            return verify_from_anchors()
        x_idx = anchors[pos]
        for y_idx in candidates[x_idx]:
            if y_idx in used:
                continue
            ok = True
            for prev_pos in range(pos):
                prev_x = anchors[prev_pos]
                prev_y = assignment[prev_pos]
                if abs(DX[x_idx, prev_x] - DY[y_idx, prev_y]) > 1e-6:
                    ok = False
                    break
            if not ok:
                continue
            assignment[pos] = y_idx
            used.add(y_idx)
            result = backtrack(pos + 1)
            if result is not None:
                return result
            used.remove(y_idx)
            assignment[pos] = -1
        return None

    result = backtrack(0)
    if result is None:
        raise ValueError("Could not find a similarity matching projected points to ShowPoints")
    return result


def map_vertices_to_points(
    X: np.ndarray,
    point_strings: list[str],
    tol: float = 1e-6,
) -> tuple[list[int], float]:
    Y = np.array([point_value(point) for point in point_strings], dtype=float)
    X_balls, vertex_to_ball = _cluster_projected_points(X)
    ball_to_point, residual = _match_collapsed_points(X_balls, Y, tol)
    return [ball_to_point[ball_idx] for ball_idx in vertex_to_ball], residual


def map_vertices_to_points_ordered(
    V: np.ndarray,
    E: list[tuple[int, int]],
    kernel: np.ndarray,
    point_strings: list[str],
    tol: float,
) -> tuple[list[int], float] | None:
    """Match via the same ordered alignment path used by emit_generic.

    Most corpus files were emitted by project_and_emit(), which preserves the
    first-occurrence order of collapsed projected vertices.  Replaying its
    edge-axis alignments avoids the O(n^2) distance-profile matcher and is much
    more reliable for highly symmetric H4 models.
    """
    Y = np.array([point_value(point) for point in point_strings], dtype=float)
    Q = projection_matrix(kernel)
    P3 = (Q @ V.T).T
    edge_dirs = Q @ np.array([V[b] - V[a] for a, b in E], dtype=float).T
    swap_yz = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)
    for R, _classes in _iter_alignments(edge_dirs):
        X = (R @ P3.T).T
        X = (swap_yz @ X.T).T
        X_balls, vertex_to_ball = _cluster_projected_points(X)
        if len(X_balls) != len(Y):
            continue
        scale, orthogonal, translation = _fit_similarity(X_balls, Y)
        transformed = _apply_similarity(X_balls, scale, orthogonal, translation)
        residual = float(np.linalg.norm(transformed - Y, axis=1).max())
        if residual <= tol:
            return vertex_to_ball, residual
    return None


def filter_vzome(
    text: str,
    point_strings: list[str],
    kept_point_indices: set[int],
    kept_join_indices: set[tuple[int, int]],
) -> tuple[str, int, int]:
    point_to_index = {point: i for i, point in enumerate(point_strings)}
    kept_point_strings = {point_strings[i] for i in kept_point_indices}
    kept_lines = []
    kept_show = 0
    kept_join = 0
    edit_command_count = 0
    in_edit_history = False
    for line in text.splitlines():
        if "<EditHistory" in line:
            in_edit_history = True
            kept_lines.append(line)
            continue
        if "</EditHistory>" in line:
            in_edit_history = False
            kept_lines.append(line)
            continue
        show = SHOW_RE.search(line)
        if show:
            if show.group(1) in kept_point_strings:
                kept_lines.append(line)
                kept_show += 1
                edit_command_count += 1
            continue
        join = JOIN_RE.search(line)
        if join:
            a = point_to_index.get(join.group(1))
            b = point_to_index.get(join.group(2))
            if a is not None and b is not None and canonical_pair(a, b) in kept_join_indices:
                kept_lines.append(line)
                kept_join += 1
                edit_command_count += 1
            continue
        kept_lines.append(line)
        stripped = line.strip()
        if in_edit_history and stripped.startswith("<") and stripped.endswith("/>"):
            edit_command_count += 1
    filtered = "\n".join(kept_lines) + "\n"
    filtered = re.sub(
        r'(<EditHistory\s+editNumber=")\d+(")',
        rf"\g<1>{edit_command_count}\2",
        filtered,
        count=1,
    )
    return filtered, kept_show, kept_join


def wythoff_records() -> list[dict]:
    manifest = json.loads((ROOT / "output" / "wythoff_sweep_manifest.json").read_text(encoding="utf-8"))
    return [
        record
        for record in manifest["shapes"]
        if record.get("status") == "ok"
        and record.get("file", "").startswith("uniform/")
    ]


def truncated_16cell_records() -> list[dict]:
    return [
        record
        for record in wythoff_records()
        if record.get("status") == "ok"
        and record.get("file", "").startswith("uniform/truncated_16cell/")
        and record.get("source_polytope") == "truncated 16-cell"
    ]


def snub_24cell_records() -> list[dict]:
    return [
        {
            "source_file": "uniform/snub_24cell/snub_24cell_cell_first.vZome",
            "file": "uniform/snub_24cell/snub_24cell_cell_first.vZome",
            "kernel": [1.0, 0.0, 0.0, 0.0],
            "label": "cell_first",
            "label_subtype": "icosahedron",
            "source_polytope": "snub 24-cell",
            "status": "ok",
        },
        {
            "source_file": "uniform/snub_24cell/snub_24cell_vertex_first.vZome",
            "file": "uniform/snub_24cell/snub_24cell_vertex_first.vZome",
            "kernel": [phi**2, phi, 1.0, 0.0],
            "label": "vertex_first",
            "label_subtype": None,
            "source_polytope": "snub 24-cell",
            "status": "ok",
        },
    ]


def grand_antiprism_records() -> list[dict]:
    return [
        {
            "file": "uniform/grand_antiprism/grand_antiprism_vertex_first.vZome",
            "kernel": [1.0, 1.0, 1.0, 1.0],
            "label": "vertex_first",
            "label_subtype": None,
            "source_polytope": "grand antiprism",
            "status": "ok",
        },
        {
            "file": "uniform/grand_antiprism/grand_antiprism_ring_first.vZome",
            "kernel": [1.0, 0.0, 0.0, 0.0],
            "label": "ring_first",
            "label_subtype": "pentagonal_antiprism",
            "source_polytope": "grand antiprism",
            "status": "ok",
        },
    ]


def regular_sets() -> list[dict]:
    inv_phi2 = 1.0 / (phi * phi)
    sqrt5 = 2.0 * phi - 1.0
    phi3 = phi**3
    return [
        {
            "key": "regular_8cell",
            "title": "8-cell",
            "source_folder": "regular/8cell",
            "out_folder": "regular/8cell_hidden_cells",
            "loader": lambda: build_polytope("B4", (1, 0, 0, 0)),
            "records": [
                {"file": "regular/8cell/8cell_cell_first_cube.vZome", "kernel": [0.0, 0.0, 0.0, 1.0], "label": "cell_first", "source_polytope": "8-cell"},
                {"file": "regular/8cell/8cell_vertex_first_rhombic_dodec.vZome", "kernel": [1.0, -1.0, -1.0, 1.0], "label": "vertex_first", "source_polytope": "8-cell"},
                {"file": "regular/8cell/8cell_phi_oblique.vZome", "kernel": [0.0, 1.0 / phi, -phi, -1.0], "label": "oblique", "source_polytope": "8-cell"},
                *[
                    {
                        "file": f"regular/8cell/8cell_inf_family_a{a}_b{b}.vZome",
                        "kernel": [float(a), float(b), 0.0, 0.0],
                        "label": "infinite_family_sample",
                        "source_polytope": "8-cell",
                    }
                    for a, b in [(1, 2), (3, 4), (5, 12), (8, 15), (2, 11), (19, 22), (2, 29)]
                ],
                {"file": "regular/8cell/8cell_inf_family_phi_aSqrt5_b2.vZome", "kernel": [sqrt5, 2.0, 0.0, 0.0], "label": "infinite_family_sample", "source_polytope": "8-cell"},
                {"file": "regular/8cell/8cell_inf_family_phi_a3plus2phi_b4phi-4.vZome", "kernel": [3.0 + 2.0 * phi, 4.0 * phi - 4.0, 0.0, 0.0], "label": "infinite_family_sample", "source_polytope": "8-cell"},
                {"file": "regular/8cell/8cell_inf_family_phi_a4phi_b5-2phi.vZome", "kernel": [4.0 * phi, 5.0 - 2.0 * phi, 0.0, 0.0], "label": "infinite_family_sample", "source_polytope": "8-cell"},
            ],
        },
        {
            "key": "regular_5cell",
            "title": "5-cell",
            "source_folder": "regular/5cell",
            "out_folder": "regular/5cell_hidden_cells",
            "loader": lambda: build_polytope("A4", (1, 0, 0, 0)),
            "records": [
                {"file": "regular/5cell/5cell_vertex_first_tet_plus_center.vZome", "kernel": [-sqrt5, -sqrt5, -sqrt5, 1.0], "label": "vertex_first", "source_polytope": "5-cell"},
                {"file": "regular/5cell/5cell_5ball_Y4B2R4.vZome", "kernel": [0.0, 0.0, inv_phi2, -inv_phi2], "label": "oblique", "source_polytope": "5-cell"},
                {"file": "regular/5cell/5cell_5ball_R6Y1B3.vZome", "kernel": [inv_phi2, inv_phi2, -inv_phi2, -phi], "label": "oblique", "source_polytope": "5-cell"},
                {"file": "regular/5cell/5cell_4ball_Y6B3.vZome", "kernel": [-1.0, -1.0, -1.0, sqrt5], "label": "oblique", "source_polytope": "5-cell"},
            ],
        },
        {
            "key": "regular_16cell",
            "title": "16-cell",
            "source_folder": "regular/16cell",
            "out_folder": "regular/16cell_hidden_cells",
            "loader": lambda: build_polytope("B4", (0, 0, 0, 1)),
            "records": [
                {"file": "regular/16cell/16cell_vertex_first_octahedron.vZome", "kernel": [1.0, 0.0, 0.0, 0.0], "label": "vertex_first", "source_polytope": "16-cell"},
                {"file": "regular/16cell/16cell_edge_first_squashed_octahedron.vZome", "kernel": [1.0, 1.0, 0.0, 0.0], "label": "edge_first", "source_polytope": "16-cell"},
                {"file": "regular/16cell/16cell_cell_first_cube.vZome", "kernel": [1.0, 1.0, 1.0, 1.0], "label": "cell_first", "source_polytope": "16-cell"},
                {"file": "regular/16cell/16cell_antiprism_B6R12Y6.vZome", "kernel": [2.0 * phi3, 2.0, -2.0 * phi3, 2.0 * phi3], "label": "oblique", "source_polytope": "16-cell"},
                {"file": "regular/16cell/16cell_antiprism_R12B6Y6.vZome", "kernel": [inv_phi2, 3.0 * phi - 4.0, -inv_phi2, inv_phi2], "label": "oblique", "source_polytope": "16-cell"},
                {"file": "regular/16cell/16cell_antiprism_Y6R12B6.vZome", "kernel": [1.0 + 2.0 * phi3, sqrt5, sqrt5, -sqrt5], "label": "oblique", "source_polytope": "16-cell"},
            ],
        },
        {
            "key": "regular_24cell",
            "title": "24-cell",
            "source_folder": "regular/24cell",
            "out_folder": "regular/24cell_hidden_cells",
            "loader": lambda: build_polytope("F4", (1, 0, 0, 0)),
            "records": [
                {"file": "regular/24cell/24cell_short_root_cuboctahedron.vZome", "kernel": [1.0, 0.0, 0.0, 0.0], "label": "short_root", "source_polytope": "24-cell"},
                {"file": "regular/24cell/24cell_long_root_rhombic_dodecahedron.vZome", "kernel": [1.0, -1.0, 0.0, 0.0], "label": "long_root", "source_polytope": "24-cell"},
                {"file": "regular/24cell/24cell_triality.vZome", "kernel": [inv_phi2, inv_phi2, -inv_phi2, -phi], "label": "triality", "source_polytope": "24-cell"},
            ],
        },
        {
            "key": "regular_120cell",
            "title": "120-cell",
            "source_folder": "regular/120cell",
            "out_folder": "regular/120cell_hidden_cells",
            "loader": lambda: build_polytope("H4", (1, 0, 0, 0)),
            "records": [
                {"file": "regular/120cell/120cell_H4_to_H3.vZome", "kernel": [1.0, 1.0, 1.0, 1.0], "label": "H4_to_H3", "source_polytope": "120-cell"},
            ],
        },
        {
            "key": "regular_600cell",
            "title": "600-cell",
            "source_folder": "regular/600cell",
            "out_folder": "regular/600cell_hidden_cells",
            "loader": lambda: build_polytope("H4", (0, 0, 0, 1)),
            "records": [
                {"file": "regular/600cell/600cell_H4_to_H3.vZome", "kernel": [1.0, 0.0, 0.0, 0.0], "label": "H4_to_H3", "source_polytope": "600-cell"},
            ],
        },
    ]


def prismatic_sets() -> list[dict]:
    manifest = json.loads((ROOT / "output" / "prismatic_manifest.json").read_text(encoding="utf-8"))
    registry = {entry["slug"]: entry for entry in get_registry(None)}
    result = []
    for family_rows in manifest["families"].values():
        for poly_row in family_rows:
            shapes = poly_row.get("shapes", [])
            if not shapes:
                continue
            slug = poly_row["slug"]
            entry = registry[slug]
            first_path = Path(shapes[0]["path"])
            source_folder = str(first_path.parent.relative_to("output")).replace("\\", "/")
            records = []
            for shape in shapes:
                path = str(Path(shape["path"]).relative_to("output")).replace("\\", "/")
                kernel = shape["kernel"]
                if kernel is None and shape.get("label") == "cell_first" and shape.get("subtype") == "cube" and slug.startswith("duoprism_4_"):
                    kernel = [0.0, 0.0, 0.0, 1.0]
                records.append(
                    {
                        "file": path,
                        "kernel": kernel,
                        "label": shape.get("label"),
                        "label_subtype": shape.get("subtype"),
                        "source_polytope": slug.replace("_", " "),
                    }
                )
            result.append(
                {
                    "key": f"prismatic_{slug}",
                    "title": slug.replace("_", " "),
                    "source_folder": source_folder,
                    "out_folder": f"{source_folder}_hidden_cells",
                    "loader": entry["builder"],
                    "records": records,
                }
            )
    return result


def wythoff_sets() -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in wythoff_records():
        folder = str(Path(record["file"]).parent).replace("\\", "/")
        grouped[folder].append(record)
    result = []
    for folder, records in sorted(grouped.items()):
        first = records[0]
        slug = Path(folder).name
        result.append(
            {
                "key": f"wythoff_{slug}",
                "title": first.get("source_polytope", slug),
                "source_folder": folder,
                "out_folder": f"{folder}_hidden_cells",
                "loader": lambda group=first["group"], bitmask=tuple(first["bitmask"]): build_polytope(group, bitmask),
                "records": records,
            }
        )
    return result


def non_wythoff_sets() -> list[dict]:
    return [
        {
            "key": "snub_24cell",
            "title": "Snub 24-cell",
            "source_folder": "uniform/snub_24cell",
            "out_folder": "uniform/snub_24cell_hidden_cells",
            "loader": snub_24cell,
            "records": snub_24cell_records(),
        },
        {
            "key": "grand_antiprism",
            "title": "Grand antiprism",
            "source_folder": "uniform/grand_antiprism",
            "out_folder": "uniform/grand_antiprism_hidden_cells",
            "loader": grand_antiprism,
            "records": grand_antiprism_records(),
        },
    ]


TARGETS = {
    "truncated_16cell": {
        "title": "Truncated 16-cell",
        "source_folder": "truncated_16cell",
        "out_folder": "truncated_16cell_hidden_cells",
        "loader": lambda: build_polytope("B4", (0, 0, 1, 1)),
        "records": truncated_16cell_records,
        "expected": (48, 120, 24),
    },
    "snub_24cell": {
        "title": "Snub 24-cell",
        "source_folder": "snub_24cell",
        "out_folder": "snub_24cell_hidden_cells",
        "loader": snub_24cell,
        "records": snub_24cell_records,
        "expected": (96, 432, 144),
    },
}


def all_shape_sets() -> list[dict]:
    keyed: dict[str, dict] = {}
    for shape_set in regular_sets() + wythoff_sets() + non_wythoff_sets() + prismatic_sets():
        keyed[shape_set["key"]] = shape_set
    return [keyed[key] for key in sorted(keyed)]


def process_record(
    record: dict,
    V: np.ndarray,
    E: list[tuple[int, int]],
    cells: list[dict],
    out_dir: Path,
    tol: float,
    map_tol: float,
) -> dict:
    in_path = ROOT / "output" / record["file"]
    text, point_strings, joins = parse_vzome(in_path)
    join_point_to_indices = {
        canonical_pair(point_strings.index(a), point_strings.index(b))
        for a, b in joins
    }
    kernel = snap_kernel(record["kernel"])
    visible_vertices, visible_edges, cell_stats = visible_4d_sets(V, E, cells, kernel, tol)
    ordered_match = map_vertices_to_points_ordered(V, E, kernel, point_strings, map_tol)
    if ordered_match is not None:
        vertex_to_point, residual = ordered_match
    elif len(point_strings) <= 800:
        X = projected_vertices(V, E, kernel)
        vertex_to_point, residual = map_vertices_to_points(X, point_strings, tol=map_tol)
    else:
        raise ValueError(
            "Could not replay emitter alignment, and fallback matcher is disabled "
            f"for {len(point_strings)} ShowPoints"
        )

    kept_point_indices = {vertex_to_point[v] for v in visible_vertices}
    kept_join_indices: set[tuple[int, int]] = set()
    for edge in visible_edges:
        a = vertex_to_point[edge[0]]
        b = vertex_to_point[edge[1]]
        if a == b:
            continue
        pair = canonical_pair(a, b)
        if pair in join_point_to_indices:
            kept_join_indices.add(pair)

    out_name = in_path.name.replace(".vZome", "_front_visible.vZome")
    out_path = out_dir / out_name
    filtered, kept_show, kept_join = filter_vzome(
        text, point_strings, kept_point_indices, kept_join_indices
    )
    removed_balls = len(point_strings) - kept_show
    removed_edges = len(joins) - kept_join
    unchanged = removed_balls == 0 and removed_edges == 0
    if unchanged:
        if out_path.exists():
            out_path.unlink()
        emitted_file = None
    else:
        out_path.write_text(filtered, encoding="utf-8")
        emitted_file = out_name

    if not kept_point_indices.issubset(set(range(len(point_strings)))):
        raise AssertionError("Kept point index outside original point set")
    if not kept_join_indices.issubset(join_point_to_indices):
        raise AssertionError("Derived join set is not a subset of original joins")

    return {
        "source_file": record["file"],
        "file": emitted_file,
        "label": record.get("label"),
        "label_subtype": record.get("label_subtype"),
        "status": "unchanged" if unchanged else "written",
        "unchanged": unchanged,
        "kernel_positive_side": [float(x) for x in kernel],
        "source_balls": len(point_strings),
        "source_edges": len(joins),
        "front_visible_balls": kept_show,
        "front_visible_edges": kept_join,
        "removed_balls": removed_balls,
        "removed_edges": removed_edges,
        "vertex_to_showpoint_max_residual": residual,
        **cell_stats,
    }


def write_pages(out_dir: Path, rows: list[dict], target: dict) -> None:
    table = [
        "| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |",
        "|---|---|---:|---:|---:|---:|",
    ]
    figures = []
    for row in rows:
        if row.get("status") == "failed":
            table.append(
                f"| `{Path(str(row.get('source_file'))).name}` | failed: `{row.get('error', '')}` | "
                "| - | - | - | - |"
            )
            continue
        file_cell = f"`{row['file']}`" if row.get("file") else "unchanged (no derived file)"
        table.append(
            f"| `{Path(row['source_file']).name}` | {file_cell} | "
            f"{row['front_visible_balls']} / {row['source_balls']} | "
            f"{row['front_visible_edges']} / {row['source_edges']} | "
            f"{row['removed_balls']} | {row['removed_edges']} |"
        )
        if row.get("file"):
            figures.append(
                f'''<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="{row['file']}" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">{row['file']}</figcaption>
</figure>
'''
            )
    title = target["title"]
    source_folder = target["source_folder"]
    out_folder = target["out_folder"]
    source_rel = Path(os.path.relpath(ROOT / "output" / source_folder, out_dir)).as_posix()
    readme = f"""# {title} hidden-cell removal

These files are derived from `output/{source_folder}/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

{chr(10).join(table)}
"""
    (out_dir / "RESULTS.md").write_text(readme, encoding="utf-8")
    if figures:
        viewer_body = "\n".join(figures)
    else:
        viewer_body = "All front-visible variants are unchanged, so no derived `.vZome` files are emitted."
    viewer = f"""# {title} hidden-cell removal

➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/{out_folder}/VIEWER.html)** to interact with the derived front-visible models.

For the original full projections, see [`{source_rel}/VIEWER.md`]({source_rel}/VIEWER.md).

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

{viewer_body}
"""
    (out_dir / "VIEWER.md").write_text(viewer, encoding="utf-8")


def process_shape_set(shape_set: dict, tol: float, map_tol: float, clean: bool = True) -> dict:
    out_dir = ROOT / "output" / shape_set["out_folder"]
    out_dir.mkdir(parents=True, exist_ok=True)
    if clean:
        for old in out_dir.glob("*.vZome"):
            old.unlink()
    rows = []
    set_status = "ok"
    try:
        V, E = shape_set["loader"]()
        cells = grouped_cells(V)
        cell_count = len(cells)
    except Exception as exc:
        return {
            "key": shape_set["key"],
            "title": shape_set["title"],
            "source_folder": shape_set["source_folder"],
            "out_folder": shape_set["out_folder"],
            "status": "failed",
            "error": repr(exc),
            "models": [],
        }
    for record in shape_set["records"]:
        try:
            row = process_record(record, V, E, cells, out_dir, tol, map_tol)
        except Exception as exc:
            row = {
                "source_file": record.get("file"),
                "label": record.get("label"),
                "label_subtype": record.get("label_subtype"),
                "status": "failed",
                "error": repr(exc),
            }
            set_status = "partial_failed"
        rows.append(row)
    manifest = {
        "key": shape_set["key"],
        "title": shape_set["title"],
        "source_folder": shape_set["source_folder"],
        "out_folder": shape_set["out_folder"],
        "vertices_4d": len(V),
        "edges_4d": len(E),
        "cells_4d": cell_count,
        "models": rows,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_pages(out_dir, rows, shape_set)
    return {
        "key": shape_set["key"],
        "title": shape_set["title"],
        "source_folder": shape_set["source_folder"],
        "out_folder": shape_set["out_folder"],
        "status": set_status,
        "vertices_4d": len(V),
        "edges_4d": len(E),
        "cells_4d": cell_count,
        "models": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target",
        default="all",
        help="Shape-set key to process, or 'all'. Use --list-targets to inspect keys.",
    )
    parser.add_argument("--list-targets", action="store_true")
    parser.add_argument(
        "--out",
        default=None,
        help="Override output folder for a single target.",
    )
    parser.add_argument("--tol", type=float, default=1e-8)
    parser.add_argument(
        "--map-tol",
        type=float,
        default=1e-3,
        help="Numeric tolerance for matching rounded manifest kernels back to emitted ShowPoint coordinates.",
    )
    args = parser.parse_args()

    sets = all_shape_sets()
    by_key = {shape_set["key"]: shape_set for shape_set in sets}
    aliases = {
        "truncated_16cell": "wythoff_truncated_16cell",
        "snub_24cell": "snub_24cell",
        "grand_antiprism": "grand_antiprism",
    }
    if args.list_targets:
        for key in sorted(by_key):
            shape_set = by_key[key]
            print(f"{key}\t{shape_set['source_folder']}\t{len(shape_set['records'])}")
        return
    target_key = aliases.get(args.target, args.target)
    if args.target == "all":
        selected = sets
    elif target_key in by_key:
        selected = [by_key[target_key]]
        if args.out:
            selected[0] = {**selected[0], "out_folder": args.out.removeprefix("output/").replace("\\", "/")}
    else:
        raise SystemExit(f"Unknown target {args.target!r}. Use --list-targets.")

    results = [process_shape_set(shape_set, args.tol, args.map_tol) for shape_set in selected]
    summary = {
        "schema": "hidden_cell_removal.v1",
        "layout": "sibling hidden_cells folders; unchanged variants omit derived .vZome files",
        "targets": results,
    }
    (ROOT / "output" / "hidden_cell_removal_manifest.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "targets": len(results),
                "models": sum(len(r.get("models", [])) for r in results),
                "written": sum(1 for r in results for m in r.get("models", []) if m.get("status") == "written"),
                "unchanged": sum(1 for r in results for m in r.get("models", []) if m.get("status") == "unchanged"),
                "failed": sum(1 for r in results for m in r.get("models", []) if m.get("status") == "failed"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
