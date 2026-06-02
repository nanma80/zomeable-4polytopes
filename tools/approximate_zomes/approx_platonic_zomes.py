"""Experimental zomeable approximations to target Platonic solids.

This folder is intentionally separate from zomeable-4polytopes: the goal here
is not exact uniform-polytope classification, but visually useful RGBY strut
models that approximate familiar shapes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "zomeable-4polytopes"
sys.path.insert(0, str(ROOT / "lib"))

from emit_vzome import (  # noqa: E402
    GF,
    STRUT_LOOKUP,
    classify_strut,
    emit_vzome,
    phi_pow,
    vadd,
    vkey,
    vsub,
    vscale,
)


PHI = (1 + 5**0.5) / 2

PLATONIC_TARGETS = ["tetrahedron", "cube", "octahedron", "icosahedron", "dodecahedron"]
ARCHIMEDEAN_TARGETS = [
    "truncated_tetrahedron",
    "cuboctahedron",
    "truncated_cube",
    "truncated_octahedron",
    "rhombicuboctahedron",
    "truncated_cuboctahedron",
    "snub_cube",
    "icosidodecahedron",
    "truncated_dodecahedron",
    "truncated_icosahedron",
    "rhombicosidodecahedron",
    "truncated_icosidodecahedron",
    "snub_dodecahedron",
]
CATALAN_DUALS = {
    "triakis_tetrahedron": "truncated_tetrahedron",
    "rhombic_dodecahedron": "cuboctahedron",
    "triakis_octahedron": "truncated_cube",
    "tetrakis_hexahedron": "truncated_octahedron",
    "deltoidal_icositetrahedron": "rhombicuboctahedron",
    "disdyakis_dodecahedron": "truncated_cuboctahedron",
    "pentagonal_icositetrahedron": "snub_cube",
    "rhombic_triacontahedron": "icosidodecahedron",
    "triakis_icosahedron": "truncated_dodecahedron",
    "pentakis_dodecahedron": "truncated_icosahedron",
    "deltoidal_hexecontahedron": "rhombicosidodecahedron",
    "disdyakis_triacontahedron": "truncated_icosidodecahedron",
    "pentagonal_hexecontahedron": "snub_dodecahedron",
}
CATALAN_TARGETS = list(CATALAN_DUALS)
KNOWN_TARGETS = PLATONIC_TARGETS + ARCHIMEDEAN_TARGETS + CATALAN_TARGETS


def dist2(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum((a[i] - b[i]) ** 2 for i in range(3))


def sub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def norm(v):
    return math.sqrt(dot(v, v))


def regular_edges(points: list[tuple[float, float, float]]) -> list[tuple[int, int]]:
    pairs = [(dist2(points[i], points[j]), i, j) for i, j in combinations(range(len(points)), 2)]
    edge_d2 = min(d for d, _, _ in pairs if d > 1e-9)
    return [(i, j) for d, i, j in pairs if abs(d - edge_d2) < 1e-7]


def chordless_cycles(
    n_vertices: int, edges: list[tuple[int, int]], length: int
) -> list[tuple[int, ...]]:
    adj = {i: set() for i in range(n_vertices)}
    edge_set = {tuple(sorted(e)) for e in edges}
    for i, j in edges:
        adj[i].add(j)
        adj[j].add(i)

    cycles = set()

    def canonical(cyc: list[int]) -> tuple[int, ...]:
        variants = []
        for seq in (cyc, list(reversed(cyc))):
            for k in range(len(seq)):
                variants.append(tuple(seq[k:] + seq[:k]))
        return min(variants)

    def dfs(start: int, path: list[int]) -> None:
        if len(path) == length:
            if start not in adj[path[-1]]:
                return
            cyc = canonical(path)
            for i in range(length):
                for j in range(i + 2, length):
                    if i == 0 and j == length - 1:
                        continue
                    if tuple(sorted((cyc[i], cyc[j]))) in edge_set:
                        return
            cycles.add(cyc)
            return
        for nxt in adj[path[-1]]:
            if nxt < start or nxt in path:
                continue
            dfs(start, path + [nxt])

    for start in range(n_vertices):
        dfs(start, [start])
    return sorted(cycles)


def perm_parity(perm: tuple[int, ...]) -> int:
    inversions = 0
    for i in range(len(perm)):
        for j in range(i + 1, len(perm)):
            if perm[i] > perm[j]:
                inversions += 1
    return inversions % 2


def unique_float_points(points, tol: float = 1e-8) -> list[tuple[float, float, float]]:
    out = []
    for point in points:
        p = tuple(float(x) for x in point)
        if not any(norm(sub(p, q)) <= tol for q in out):
            out.append(p)
    return out


def signed_permutation_points(
    values: tuple[float, float, float],
    *,
    permutation_parity: int | None = None,
    plus_parity: int | None = None,
    predicate=None,
) -> list[tuple[float, float, float]]:
    points = []
    for perm in permutations(range(3)):
        if permutation_parity is not None and perm_parity(perm) != permutation_parity:
            continue
        base = tuple(values[i] for i in perm)
        for signs in product((1, -1), repeat=3):
            if plus_parity is not None and sum(1 for sign in signs if sign > 0) % 2 != plus_parity:
                continue
            point = tuple(signs[i] * base[i] for i in range(3))
            if predicate is None or predicate(point):
                points.append(point)
    return unique_float_points(points)


def convex_hull_graph(points: list[tuple[float, float, float]]) -> tuple[list[tuple[int, int]], list[tuple[int, ...]]]:
    import numpy as np
    from scipy.spatial import ConvexHull

    pts = np.array(points, dtype=float)
    hull = ConvexHull(pts)
    scale = max(1.0, float(np.max(np.abs(pts))))
    plane_tol = 1e-7 * scale
    grouped: list[tuple[np.ndarray, set[int]]] = []
    for simplex, equation in zip(hull.simplices, hull.equations):
        plane = np.array(equation, dtype=float)
        for value in plane:
            if abs(value) > 1e-12:
                if value < 0:
                    plane = -plane
                break
        for group_plane, vertices in grouped:
            if np.allclose(plane, group_plane, atol=plane_tol, rtol=1e-7):
                vertices.update(int(i) for i in simplex)
                break
        else:
            grouped.append((plane, {int(i) for i in simplex}))

    faces = []
    for plane, vertices in grouped:
        normal = plane[:3]
        normal = normal / np.linalg.norm(normal)
        centroid = np.mean(pts[list(vertices)], axis=0)
        first = pts[next(iter(vertices))] - centroid
        first -= np.dot(first, normal) * normal
        first_norm = np.linalg.norm(first)
        if first_norm < 1e-12:
            raise ValueError("degenerate convex-hull face")
        u = first / first_norm
        v = np.cross(normal, u)
        ordered = sorted(
            vertices,
            key=lambda idx: math.atan2(float(np.dot(pts[idx] - centroid, v)), float(np.dot(pts[idx] - centroid, u))),
        )
        faces.append(tuple(ordered))

    edges = sorted(
        {
            tuple(sorted((face[i], face[(i + 1) % len(face)])))
            for face in faces
            for i in range(len(face))
        }
    )
    faces.sort(key=lambda face: (len(face), face))
    return edges, faces


def truncate_target(base_name: str, amount: float) -> list[tuple[float, float, float]]:
    base = target(base_name)
    points = []
    for i, j in base["edges"]:
        a = base["points"][i]
        b = base["points"][j]
        points.append(tuple((1 - amount) * a[k] + amount * b[k] for k in range(3)))
        points.append(tuple(amount * a[k] + (1 - amount) * b[k] for k in range(3)))
    return unique_float_points(points)


def snub_dodecahedron_points() -> list[tuple[float, float, float]]:
    import numpy as np

    roots = np.roots([1.0, 2.0, 0.0, -(PHI**2)])
    xi = float([root.real for root in roots if abs(root.imag) < 1e-9][0])
    p = np.array(
        [
            PHI**2 - PHI**2 * xi,
            -(PHI**3) + PHI * xi + 2 * PHI * xi**2,
            xi,
        ],
        dtype=float,
    )
    m1 = np.array(
        [
            [1 / (2 * PHI), -PHI / 2, 1 / 2],
            [PHI / 2, 1 / 2, 1 / (2 * PHI)],
            [-1 / 2, 1 / (2 * PHI), PHI / 2],
        ],
        dtype=float,
    )
    m2 = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], dtype=float)
    matrices = []
    seen = set()
    frontier = [np.eye(3)]
    while frontier:
        matrix = frontier.pop()
        key = tuple(np.round(matrix.flatten(), 10))
        if key in seen:
            continue
        seen.add(key)
        matrices.append(matrix)
        frontier.extend([m1 @ matrix, m2 @ matrix])
    return unique_float_points([matrix @ p for matrix in matrices], tol=1e-7)


def archimedean_points(name: str) -> list[tuple[float, float, float]]:
    sqrt2 = math.sqrt(2)
    if name == "truncated_tetrahedron":
        return signed_permutation_points((1, 1, 3), predicate=lambda p: p[0] * p[1] * p[2] > 0)
    if name == "cuboctahedron":
        return signed_permutation_points((1, 1, 0))
    if name == "truncated_cube":
        return signed_permutation_points((1, 1 + sqrt2, 1 + sqrt2))
    if name == "truncated_octahedron":
        return signed_permutation_points((0, 1, 2))
    if name == "rhombicuboctahedron":
        return signed_permutation_points((1, 1, 1 + sqrt2))
    if name == "truncated_cuboctahedron":
        return signed_permutation_points((1, 1 + sqrt2, 1 + 2 * sqrt2))
    if name == "snub_cube":
        import numpy as np

        roots = np.roots([1.0, -1.0, -1.0, -1.0])
        tribonacci = float([root.real for root in roots if abs(root.imag) < 1e-9][0])
        return unique_float_points(
            signed_permutation_points((1, 1 / tribonacci, tribonacci), permutation_parity=0, plus_parity=0)
            + signed_permutation_points((1, 1 / tribonacci, tribonacci), permutation_parity=1, plus_parity=1)
        )
    if name == "icosidodecahedron":
        return truncate_target("icosahedron", 0.5)
    if name == "truncated_dodecahedron":
        return truncate_target("dodecahedron", (5 - math.sqrt(5)) / 10)
    if name == "truncated_icosahedron":
        return truncate_target("icosahedron", 1 / 3)
    if name == "rhombicosidodecahedron":
        points = []
        for values in ((1, 1, PHI**3), (PHI**2, PHI, 2 * PHI), (2 + PHI, 0, PHI**2)):
            points.extend(signed_permutation_points(values, permutation_parity=0))
        return unique_float_points(points)
    if name == "truncated_icosidodecahedron":
        points = []
        for values in (
            (1 / PHI, 1 / PHI, 3 + PHI),
            (2 / PHI, PHI, 1 + 2 * PHI),
            (1 / PHI, PHI**2, -1 + 3 * PHI),
            (2 * PHI - 1, 2, 2 + PHI),
            (PHI, 3, 2 * PHI),
        ):
            points.extend(signed_permutation_points(values, permutation_parity=0))
        return unique_float_points(points)
    if name == "snub_dodecahedron":
        return snub_dodecahedron_points()
    raise ValueError(f"unknown Archimedean target {name}")


def dual_points(data: dict) -> list[tuple[float, float, float]]:
    points = data["points"]
    out = []
    for face in data["faces"]:
        face_points = [points[i] for i in face]
        center = centroid(face_points)
        normal = (0.0, 0.0, 0.0)
        for i in range(len(face_points)):
            normal = tuple(
                normal[k] + cross(face_points[i], face_points[(i + 1) % len(face_points)])[k]
                for k in range(3)
            )
        n = norm(normal)
        if n < 1e-12:
            raise ValueError(f"degenerate dual face in {data['name']}")
        normal = tuple(x / n for x in normal)
        if dot(normal, center) < 0:
            normal = tuple(-x for x in normal)
        offset = dot(normal, center)
        if offset <= 1e-12:
            raise ValueError(f"bad dual offset in {data['name']}: {offset}")
        out.append(tuple(x / offset for x in normal))
    return unique_float_points(out, tol=1e-7)


def catalan_points(name: str) -> list[tuple[float, float, float]]:
    arch_name = CATALAN_DUALS[name]
    return dual_points(target(arch_name))


def add_ideal_face_angles(data: dict) -> dict:
    face_angles = []
    points = data["points"]
    for face in data["faces"]:
        angles = []
        for i, vertex in enumerate(face):
            prev_pt = points[face[i - 1]]
            this_pt = points[vertex]
            next_pt = points[face[(i + 1) % len(face)]]
            a = sub(prev_pt, this_pt)
            b = sub(next_pt, this_pt)
            denom = norm(a) * norm(b)
            if denom < 1e-12:
                angles.append(math.pi)
            else:
                c = max(-1.0, min(1.0, dot(a, b) / denom))
                angles.append(math.acos(c))
        face_angles.append(tuple(angles))
    data["face_angles"] = face_angles
    return data


EXPECTED_TARGET_COUNTS = {
    "tetrahedron": (4, 6, {3: 4}),
    "cube": (8, 12, {4: 6}),
    "octahedron": (6, 12, {3: 8}),
    "icosahedron": (12, 30, {3: 20}),
    "dodecahedron": (20, 30, {5: 12}),
    "truncated_tetrahedron": (12, 18, {3: 4, 6: 4}),
    "cuboctahedron": (12, 24, {3: 8, 4: 6}),
    "truncated_cube": (24, 36, {3: 8, 8: 6}),
    "truncated_octahedron": (24, 36, {4: 6, 6: 8}),
    "rhombicuboctahedron": (24, 48, {3: 8, 4: 18}),
    "truncated_cuboctahedron": (48, 72, {4: 12, 6: 8, 8: 6}),
    "snub_cube": (24, 60, {3: 32, 4: 6}),
    "icosidodecahedron": (30, 60, {3: 20, 5: 12}),
    "truncated_dodecahedron": (60, 90, {3: 20, 10: 12}),
    "truncated_icosahedron": (60, 90, {5: 12, 6: 20}),
    "rhombicosidodecahedron": (60, 120, {3: 20, 4: 30, 5: 12}),
    "truncated_icosidodecahedron": (120, 180, {4: 30, 6: 20, 10: 12}),
    "snub_dodecahedron": (60, 150, {3: 80, 5: 12}),
    "triakis_tetrahedron": (8, 18, {3: 12}),
    "rhombic_dodecahedron": (14, 24, {4: 12}),
    "triakis_octahedron": (14, 36, {3: 24}),
    "tetrakis_hexahedron": (14, 36, {3: 24}),
    "deltoidal_icositetrahedron": (26, 48, {4: 24}),
    "disdyakis_dodecahedron": (26, 72, {3: 48}),
    "pentagonal_icositetrahedron": (38, 60, {5: 24}),
    "rhombic_triacontahedron": (32, 60, {4: 30}),
    "triakis_icosahedron": (32, 90, {3: 60}),
    "pentakis_dodecahedron": (32, 90, {3: 60}),
    "deltoidal_hexecontahedron": (62, 120, {4: 60}),
    "disdyakis_triacontahedron": (62, 180, {3: 120}),
    "pentagonal_hexecontahedron": (92, 150, {5: 60}),
}


def target_count_summary(data: dict) -> dict:
    face_sizes: dict[int, int] = {}
    for face in data["faces"]:
        face_sizes[len(face)] = face_sizes.get(len(face), 0) + 1
    return {"vertices": len(data["points"]), "edges": len(data["edges"]), "face_sizes": dict(sorted(face_sizes.items()))}


def verify_target(name: str) -> dict:
    data = target(name)
    summary = target_count_summary(data)
    expected = EXPECTED_TARGET_COUNTS.get(name)
    if expected is not None:
        expected_vertices, expected_edges, expected_face_sizes = expected
        if (
            summary["vertices"] != expected_vertices
            or summary["edges"] != expected_edges
            or summary["face_sizes"] != expected_face_sizes
        ):
            raise ValueError(f"{name} count mismatch: {summary} != {expected}")

    edge_lengths = [math.sqrt(dist2(data["points"][i], data["points"][j])) for i, j in data["edges"]]
    radii = [norm(point) for point in data["points"]]
    regular_face_errors = []
    for face_index, face in enumerate(data["faces"]):
        sides = [
            math.sqrt(dist2(data["points"][face[i]], data["points"][face[(i + 1) % len(face)]]))
            for i in range(len(face))
        ]
        regular_face_errors.append(rel_range(sides))
        target_angle = math.pi * (len(face) - 2) / len(face)
        regular_face_errors.extend(abs(angle - target_angle) for angle in data["face_angles"][face_index])

    return {
        **summary,
        "edge_ratio": max(edge_lengths) / min(edge_lengths),
        "radius_range": rel_range(radii),
        "max_regular_face_error": max(regular_face_errors) if regular_face_errors else 0.0,
    }


def expand_targets(names: list[str]) -> list[str]:
    out = []
    for name in names:
        if name in {"archimedean", "all_archimedean"}:
            out.extend(ARCHIMEDEAN_TARGETS)
        elif name in {"catalan", "all_catalan"}:
            out.extend(CATALAN_TARGETS)
        elif name in {"platonic", "all_platonic"}:
            out.extend(PLATONIC_TARGETS)
        elif name == "all":
            out.extend(KNOWN_TARGETS)
        else:
            out.append(name)
    return out


def target(name: str) -> dict:
    if name in ARCHIMEDEAN_TARGETS:
        points = archimedean_points(name)
        edges, faces = convex_hull_graph(points)
        return add_ideal_face_angles({"name": name, "points": points, "edges": edges, "faces": faces})

    if name in CATALAN_TARGETS:
        points = catalan_points(name)
        edges, faces = convex_hull_graph(points)
        return add_ideal_face_angles({"name": name, "points": points, "edges": edges, "faces": faces})

    if name == "tetrahedron":
        points = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
        face_len = 3
    elif name == "cube":
        points = list(product((-1, 1), repeat=3))
        face_len = 4
    elif name == "octahedron":
        points = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        face_len = 3
    elif name == "icosahedron":
        points = []
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                points.extend([(0, s1, s2 * PHI), (s1, s2 * PHI, 0), (s2 * PHI, 0, s1)])
        face_len = 3
    elif name == "dodecahedron":
        inv = 1 / PHI
        points = list(product((-1, 1), repeat=3))
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                points.extend([(0, s1 * inv, s2 * PHI), (s1 * inv, s2 * PHI, 0), (s2 * PHI, 0, s1 * inv)])
        face_len = 5
    else:
        raise ValueError(f"unknown target {name}")

    points = [tuple(float(x) for x in p) for p in points]
    edges = regular_edges(points)
    faces = chordless_cycles(len(points), edges, face_len)
    return add_ideal_face_angles({"name": name, "points": points, "edges": edges, "faces": faces})


def face_planarity(points, face: tuple[int, ...]) -> float:
    if len(face) <= 3:
        return 0.0
    p0, p1, p2 = (points[i] for i in face[:3])
    normal = cross(sub(p1, p0), sub(p2, p0))
    n = norm(normal)
    if n < 1e-12:
        return float("inf")
    distances = [abs(dot(sub(points[i], p0), normal)) / n for i in face]
    return math.sqrt(sum(d * d for d in distances) / len(distances))


def centroid(points: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    return tuple(sum(p[i] for p in points) / len(points) for i in range(3))


def radial_cv(points: list[tuple[float, float, float]]) -> tuple[float, float]:
    c = centroid(points)
    radii = [norm(sub(p, c)) for p in points]
    mean = sum(radii) / len(radii)
    min_ratio = min(radii) / mean if mean > 1e-12 else 0.0
    radial_range = (max(radii) - min(radii)) / mean if mean > 1e-12 else float("inf")
    return coeff_var(radii), min_ratio, radial_range


def convexity_violation(points: list[tuple[float, float, float]], faces: list[tuple[int, ...]], mean_edge: float) -> float:
    """Return normalized face-support violation.

    A convex polyhedron has every non-face vertex on one side of each face
    plane.  Positive values mean at least one face plane has vertices on both
    sides, which catches inside-poked or self-crossing approximations that can
    still have good local edge/angle metrics.
    """

    if mean_edge <= 1e-12:
        return float("inf")
    worst = 0.0
    all_indices = set(range(len(points)))
    for face in faces:
        p0, p1, p2 = (points[i] for i in face[:3])
        normal = cross(sub(p1, p0), sub(p2, p0))
        n = norm(normal)
        if n < 1e-12:
            return float("inf")
        non_face = all_indices.difference(face)
        distances = [dot(sub(points[i], p0), normal) / n for i in non_face]
        pos = max([d for d in distances if d > 0.0], default=0.0)
        neg = max([-d for d in distances if d < 0.0], default=0.0)
        if pos > 1e-9 and neg > 1e-9:
            worst = max(worst, min(pos, neg) / mean_edge)
    return worst


def coeff_var(values: list[float]) -> float:
    mean = sum(values) / len(values)
    if abs(mean) < 1e-12:
        return float("inf")
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(var) / mean


def rel_range(values: list[float]) -> float:
    mean = sum(values) / len(values)
    if abs(mean) < 1e-12:
        return float("inf")
    return (max(values) - min(values)) / mean


def score_embedding(target_data: dict, points: list[tuple[float, float, float]]) -> dict:
    edges = target_data["edges"]
    faces = target_data["faces"]
    ideal_face_angles = target_data.get("face_angles", [])
    ideal_points = target_data["points"]
    edge_lengths = [math.sqrt(dist2(points[i], points[j])) for i, j in edges]
    ideal_edge_lengths = [math.sqrt(dist2(ideal_points[i], ideal_points[j])) for i, j in edges]
    edge_ratios = [
        actual / ideal if ideal > 1e-12 else float("inf")
        for actual, ideal in zip(edge_lengths, ideal_edge_lengths)
    ]
    face_side_cvs = []
    face_side_ranges = []
    face_plane = []
    face_angle_rms = []
    face_angle_ranges = []
    for face_index, face in enumerate(faces):
        sides = [
            math.sqrt(dist2(points[face[i]], points[face[(i + 1) % len(face)]]))
            for i in range(len(face))
        ]
        ideal_sides = [
            math.sqrt(dist2(ideal_points[face[i]], ideal_points[face[(i + 1) % len(face)]]))
            for i in range(len(face))
        ]
        side_ratios = [
            actual / ideal if ideal > 1e-12 else float("inf")
            for actual, ideal in zip(sides, ideal_sides)
        ]
        face_side_cvs.append(coeff_var(side_ratios))
        face_side_ranges.append(rel_range(side_ratios))
        face_plane.append(face_planarity(points, face))
        angles = []
        for i in range(len(face)):
            prev_pt = points[face[i - 1]]
            this_pt = points[face[i]]
            next_pt = points[face[(i + 1) % len(face)]]
            a = sub(prev_pt, this_pt)
            b = sub(next_pt, this_pt)
            denom = norm(a) * norm(b)
            if denom < 1e-12:
                angles.append(math.pi)
            else:
                c = max(-1.0, min(1.0, dot(a, b) / denom))
                angles.append(math.acos(c))
        if face_index < len(ideal_face_angles) and len(ideal_face_angles[face_index]) == len(angles):
            errors = [a - ideal for a, ideal in zip(angles, ideal_face_angles[face_index])]
        else:
            target_angle = math.pi * (len(face) - 2) / len(face)
            errors = [a - target_angle for a in angles]
        face_angle_rms.append(math.sqrt(sum(e * e for e in errors) / len(errors)))
        face_angle_ranges.append(max(angles) - min(angles))
    mean_edge = sum(edge_lengths) / len(edge_lengths)
    mean_edge_ratio = sum(edge_ratios) / len(edge_ratios)
    normalized_plane = [x / mean_edge for x in face_plane]
    r_cv, min_r_ratio, r_range = radial_cv(points)
    convex_bad = convexity_violation(points, faces, mean_edge)
    vertex_edge_error = [0.0 for _ in points]
    for edge_index, (i, j) in enumerate(edges):
        err = abs(edge_ratios[edge_index] / mean_edge_ratio - 1.0)
        vertex_edge_error[i] += err
        vertex_edge_error[j] += err
    total_vertex_error = sum(vertex_edge_error)
    max_vertex_share = max(vertex_edge_error) / total_vertex_error if total_vertex_error > 1e-12 else 0.0
    return {
        "target": target_data["name"],
        "vertices": len(points),
        "edges": len(edges),
        "faces": len(faces),
        "edge_length_cv": coeff_var(edge_ratios),
        "edge_length_range": rel_range(edge_ratios),
        "max_face_side_cv": max(face_side_cvs) if face_side_cvs else 0.0,
        "max_face_side_range": max(face_side_ranges) if face_side_ranges else 0.0,
        "max_face_planarity_error_over_edge": max(normalized_plane) if normalized_plane else 0.0,
        "max_face_angle_rms_deg": math.degrees(max(face_angle_rms) if face_angle_rms else 0.0),
        "max_face_angle_range_deg": math.degrees(max(face_angle_ranges) if face_angle_ranges else 0.0),
        "radial_cv": r_cv,
        "min_radius_ratio": min_r_ratio,
        "radial_range": r_range,
        "max_vertex_edge_error_share": max_vertex_share,
        "convexity_violation": convex_bad,
    }


def gf_num(x: GF) -> float:
    return float(x.a) + float(x.b) * PHI


def gf_points_to_float(points) -> list[tuple[float, float, float]]:
    return [tuple(gf_num(c) for c in p) for p in points]


def audit_struts(points, edges, edge_lookup: dict | None = None) -> dict:
    counts: dict[str, int] = {}
    missing = 0
    composite_edges = 0
    segments = 0
    for i, j in edges:
        if edge_lookup is None:
            c = classify_strut(points[i], points[j])
            if c is None:
                missing += 1
            else:
                counts[f"{c[0]}{c[1]}"] = counts.get(f"{c[0]}{c[1]}", 0) + 1
                segments += 1
        else:
            edge = edge_lookup.get(vkey(vsub(points[j], points[i])))
            if edge is None:
                missing += 1
                continue
            segments += len(edge.segments)
            if len(edge.segments) > 1:
                composite_edges += 1
            for segment in edge.segments:
                label = f"{segment.color}{segment.scale}"
                counts[label] = counts.get(label, 0) + 1
    return {
        "missing": missing,
        "counts": dict(sorted(counts.items())),
        "polyhedron_edges": len(edges),
        "strut_segments": segments,
        "composite_edges": composite_edges,
    }


def key_to_point(k):
    return tuple(GF(a, b) for a, b in k)


def gf_coord(x: GF) -> list[str]:
    return [str(x.a), str(x.b)]


def gf_point_json(p) -> list[list[str]]:
    return [gf_coord(c) for c in p]


def strut_vectors(min_scale: int, max_scale: int):
    vectors = []
    seen = set()
    for k, (color, scale) in STRUT_LOOKUP.items():
        if min_scale <= scale <= max_scale and k not in seen:
            seen.add(k)
            vectors.append((k, key_to_point(k), color, scale, math.sqrt(gf_dist2_float(key_to_point(k)))))
    vectors.sort(key=lambda item: (item[4], item[2], item[3], repr(item[0])))
    return vectors


@dataclass(frozen=True)
class EdgeSegment:
    vector: tuple[GF, GF, GF]
    color: str
    scale: int


@dataclass(frozen=True)
class EdgeVector:
    key: tuple
    vector: tuple[GF, GF, GF]
    length: float
    segments: tuple[EdgeSegment, ...]

    @property
    def primary_color(self) -> str:
        return self.segments[0].color

    @property
    def scale_label(self) -> str:
        return "+".join(str(segment.scale) for segment in self.segments)


def edge_vectors(min_scale: int, max_scale: int, max_edge_struts: int = 1) -> list[EdgeVector]:
    if max_edge_struts not in (1, 2):
        raise ValueError("max_edge_struts must be 1 or 2")

    singles: list[EdgeVector] = []
    by_ray: dict[tuple, list[EdgeSegment]] = {}
    by_key: dict[tuple, EdgeVector] = {}

    def add_edge(edge: EdgeVector) -> None:
        old = by_key.get(edge.key)
        if old is None or len(edge.segments) < len(old.segments):
            by_key[edge.key] = edge

    for k, v, color, scale, length in strut_vectors(min_scale, max_scale):
        segment = EdgeSegment(v, color, scale)
        edge = EdgeVector(k, v, length, (segment,))
        singles.append(edge)
        add_edge(edge)
        base = vscale(v, phi_pow(-scale))
        by_ray.setdefault((color, vkey(base)), []).append(segment)

    if max_edge_struts == 2:
        for segments in by_ray.values():
            segments.sort(key=lambda item: (item.scale, vkey(item.vector)))
            for i, first in enumerate(segments):
                for second in segments[i:]:
                    vector = vadd(first.vector, second.vector)
                    key = vkey(vector)
                    add_edge(
                        EdgeVector(
                            key,
                            vector,
                            math.sqrt(gf_dist2_float(vector)),
                            (first, second),
                        )
                    )

    return sorted(
        by_key.values(),
        key=lambda item: (
            item.length,
            item.primary_color,
            len(item.segments),
            item.scale_label,
            repr(item.key),
        ),
    )


def gf_dist2_float(v) -> float:
    return sum(gf_num(c) ** 2 for c in v)


def within_bound_key(k, bound: float) -> bool:
    return max(abs(gf_num(GF(a, b))) for a, b in (k[0], k[1], k[2])) <= bound


def relabeled_target(name: str) -> dict:
    t = target(name)
    adj = {i: set() for i in range(len(t["points"]))}
    for i, j in t["edges"]:
        adj[i].add(j)
        adj[j].add(i)
    a, b = t["edges"][0]
    order = [a, b]
    seen = {a, b}
    cursor = 0
    while cursor < len(order):
        for nxt in sorted(adj[order[cursor]]):
            if nxt not in seen:
                seen.add(nxt)
                order.append(nxt)
        cursor += 1
    old_to_new = {old: new for new, old in enumerate(order)}
    points = [t["points"][old] for old in order]
    edges = sorted(tuple(sorted((old_to_new[i], old_to_new[j]))) for i, j in t["edges"])
    faces = [tuple(old_to_new[i] for i in face) for face in t["faces"]]
    return add_ideal_face_angles({"name": name, "points": points, "edges": edges, "faces": faces})


def objective_from_score(score: dict, struts: dict) -> float:
    diversity_bonus = 0.015 * max(0, len(struts["counts"]) - 1)
    return (
        0.5 * score["edge_length_cv"]
        + 1.8 * score["edge_length_range"]
        + 0.9 * score["max_face_side_cv"]
        + 2.4 * score["max_face_side_range"]
        + 2.0 * score["max_face_planarity_error_over_edge"]
        + 0.006 * score["max_face_angle_rms_deg"]
        + 0.012 * score["max_face_angle_range_deg"]
        + 0.6 * score["radial_cv"]
        + 4.0 * score["radial_range"]
        + 0.8 * score["max_vertex_edge_error_share"]
        + 10.0 * score["convexity_violation"]
        + 12.0 * max(0.0, 0.82 - score["min_radius_ratio"])
        - diversity_bonus
    )


def passes_fairness(score: dict) -> bool:
    return (
        score["edge_length_cv"] <= 0.28
        and score["edge_length_range"] <= 0.56
        and score["max_face_side_cv"] <= 0.22
        and score["max_face_side_range"] <= 0.48
        and score["max_face_planarity_error_over_edge"] <= 0.32
        and score["max_face_angle_rms_deg"] <= 24.0
        and score["max_face_angle_range_deg"] <= 54.0
        and score["radial_cv"] <= 0.18
        and score["min_radius_ratio"] >= 0.65
        and score["radial_range"] <= 0.46
        and score["max_vertex_edge_error_share"] <= 0.38
        and score["convexity_violation"] <= 0.02
    )


class ZomeEmbeddingSearch:
    def __init__(
        self,
        target_name: str,
        out_dir: Path,
        *,
        min_scale: int = -2,
        max_scale: int = 1,
        coord_bound: float = 18.0,
        branch_cap: int = 64,
        keep: int = 24,
        time_limit: float = 120.0,
        max_initial_edges: int = 96,
        candidate_error_limit: float = 0.75,
        require_fairness: bool = True,
        progress_interval_sec: float = 60.0,
        seed_edge_ratio_limit: float = 0.0,
        seed_scale: int | None = None,
        one_seed_per_color: bool = False,
        edge_length_ratio_limit: float = 0.0,
        edge_angle_tolerance_deg: float = 0.0,
        max_edge_struts: int = 1,
    ) -> None:
        self.target = relabeled_target(target_name)
        self.out_dir = out_dir
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.coord_bound = coord_bound
        self.branch_cap = branch_cap
        self.keep = keep
        self.time_limit = time_limit
        self.max_initial_edges = max_initial_edges
        self.candidate_error_limit = candidate_error_limit
        self.require_fairness = require_fairness
        self.progress_interval_sec = progress_interval_sec
        self.seed_edge_ratio_limit = seed_edge_ratio_limit
        self.seed_scale = seed_scale
        self.one_seed_per_color = one_seed_per_color
        self.edge_length_ratio_limit = edge_length_ratio_limit
        self.edge_angle_tolerance_deg = edge_angle_tolerance_deg
        self.max_edge_struts = max_edge_struts
        self.seed_edge_length = 0.0
        self.seed_edge_scale_ratio = 0.0
        self.struts = edge_vectors(min_scale, max_scale, max_edge_struts)
        self.edge_lookup = {edge.key: edge for edge in self.struts}
        self.neighbor_cache: dict[tuple, frozenset] = {}
        self.point_cache: dict[tuple, tuple[GF, GF, GF]] = {}
        self.results: dict[str, dict] = {}
        self.nodes = 0
        self.completed = 0
        self.started = 0.0
        self.last_progress = 0.0
        self.current_initial_edge_index = 0
        self.initial_edge_count = 0
        self.current_depth = 0
        self.second_level_vertex = None
        self.second_level_candidate_index = 0
        self.second_level_candidate_count = 0
        self.progress_path = out_dir / target_name / "progress.json"

        n = len(self.target["points"])
        self.adj = {i: set() for i in range(n)}
        for i, j in self.target["edges"]:
            self.adj[i].add(j)
            self.adj[j].add(i)
        self.target_dists = {
            tuple(sorted((i, j))): math.sqrt(dist2(self.target["points"][i], self.target["points"][j]))
            for i, j in combinations(range(n), 2)
        }

    def point(self, k):
        if k not in self.point_cache:
            self.point_cache[k] = key_to_point(k)
        return self.point_cache[k]

    def neighbors(self, k):
        if k in self.neighbor_cache:
            return self.neighbor_cache[k]
        p = self.point(k)
        out = []
        for edge in self.struts:
            q = vkey(vadd(p, edge.vector))
            if within_bound_key(q, self.coord_bound):
                out.append(q)
        self.neighbor_cache[k] = frozenset(out)
        return self.neighbor_cache[k]

    def initial_edges(self):
        chosen = []
        by_type = {}
        for edge in self.struts:
            if self.seed_scale is not None and not any(
                segment.scale == self.seed_scale for segment in edge.segments
            ):
                continue
            # Keep one orientation per +/- pair, then interleave by color/scale/length.
            if repr(edge.key) > repr(vkey(tuple(-c for c in edge.vector))):
                continue
            key = (edge.primary_color, edge.scale_label, len(edge.segments))
            by_type.setdefault(key, []).append(edge)
        for group in by_type.values():
            chosen.extend(group[: max(4, self.max_initial_edges // max(1, len(by_type)))])
        chosen.sort(
            key=lambda item: (
                item.length,
                item.primary_color,
                len(item.segments),
                item.scale_label,
                repr(item.key),
            )
        )
        if self.one_seed_per_color:
            by_color = {}
            for item in chosen:
                by_color.setdefault(item.primary_color, item)
            chosen = [by_color[color] for color in sorted(by_color)]
        return chosen[: self.max_initial_edges]

    def candidate_error(self, idx: int, cand, placed: dict[int, tuple], scale: float) -> float:
        cp = tuple(gf_num(c) for c in self.point(cand))
        logs = []
        for j, jk in placed.items():
            td = self.target_dists[tuple(sorted((idx, j)))]
            if td < 1e-12:
                continue
            jd = math.sqrt(gf_dist2_float(tuple(self.point(cand)[a] - self.point(jk)[a] for a in range(3))))
            if jd < 1e-12:
                return float("inf")
            logs.append(math.log(jd / (scale * td)))
        if not logs:
            return 0.0
        return math.sqrt(sum(x * x for x in logs) / len(logs))

    def graph_edge_lengths_fit_seed(self, idx: int, cand, placed: dict[int, tuple]) -> bool:
        if self.seed_edge_ratio_limit <= 0.0 or self.seed_edge_length <= 0.0:
            return True
        cand_point = self.point(cand)
        for j in self.adj[idx]:
            if j not in placed:
                continue
            edge_length = math.sqrt(
                gf_dist2_float(tuple(cand_point[a] - self.point(placed[j])[a] for a in range(3)))
            )
            ideal_length = self.target_dists[tuple(sorted((idx, j)))]
            if ideal_length <= 1e-12 or self.seed_edge_scale_ratio <= 1e-12:
                return False
            edge_scale_ratio = edge_length / ideal_length
            ratio = max(edge_scale_ratio, self.seed_edge_scale_ratio) / min(
                edge_scale_ratio, self.seed_edge_scale_ratio
            )
            if ratio > self.seed_edge_ratio_limit:
                return False
        return True

    def graph_edge_lengths_fit_global(self, idx: int, cand, placed: dict[int, tuple]) -> bool:
        if self.edge_length_ratio_limit <= 0.0:
            return True
        lengths = []
        cand_point = self.point(cand)
        for a, b in self.target["edges"]:
            if a == idx and b in placed:
                p, q = cand_point, self.point(placed[b])
            elif b == idx and a in placed:
                p, q = cand_point, self.point(placed[a])
            elif a in placed and b in placed:
                p, q = self.point(placed[a]), self.point(placed[b])
            else:
                continue
            actual = math.sqrt(gf_dist2_float(tuple(p[i] - q[i] for i in range(3))))
            ideal = self.target_dists[tuple(sorted((a, b)))]
            if ideal <= 1e-12:
                return False
            lengths.append(actual / ideal)
        if len(lengths) < 2:
            return True
        return max(lengths) / min(lengths) <= self.edge_length_ratio_limit

    @staticmethod
    def angle_deg_at(center, a, b) -> float | None:
        va = [a[i] - center[i] for i in range(3)]
        vb = [b[i] - center[i] for i in range(3)]
        la = math.sqrt(sum(x * x for x in va))
        lb = math.sqrt(sum(x * x for x in vb))
        if la < 1e-12 or lb < 1e-12:
            return None
        cosang = max(-1.0, min(1.0, sum(va[i] * vb[i] for i in range(3)) / (la * lb)))
        return math.degrees(math.acos(cosang))

    def graph_edge_angles_fit_target(self, idx: int, cand, placed: dict[int, tuple]) -> bool:
        if self.edge_angle_tolerance_deg <= 0.0:
            return True
        cand_float = tuple(gf_num(c) for c in self.point(cand))
        placed_float = {
            vertex: tuple(gf_num(c) for c in self.point(key))
            for vertex, key in placed.items()
        }
        target_points = self.target["points"]
        for center in self.adj[idx]:
            if center not in placed:
                continue
            for other in self.adj[center]:
                if other == idx or other not in placed:
                    continue
                actual = self.angle_deg_at(placed_float[center], cand_float, placed_float[other])
                target_angle = self.angle_deg_at(target_points[center], target_points[idx], target_points[other])
                if actual is None or target_angle is None:
                    return False
                if abs(actual - target_angle) > self.edge_angle_tolerance_deg:
                    return False
        return True

    def face_progress(self, idx: int, placed: dict[int, tuple]) -> tuple[int, bool]:
        best = 0
        closes_face = False
        for face in self.target["faces"]:
            if idx not in face:
                continue
            progress = 1 + sum(vertex in placed for vertex in face)
            best = max(best, progress)
            closes_face = closes_face or progress == len(face)
        return best, closes_face

    def choose_vertex(self, placed: dict[int, tuple], used: set[tuple], scale: float):
        best = None
        n = len(self.target["points"])
        for idx in range(n):
            if idx in placed:
                continue
            placed_neighbors = [j for j in self.adj[idx] if j in placed]
            if not placed_neighbors:
                continue
            cand_set = None
            for j in placed_neighbors:
                neigh = self.neighbors(placed[j])
                cand_set = set(neigh) if cand_set is None else cand_set & neigh
            if cand_set is None:
                continue
            cands = [c for c in cand_set if c not in used]
            if not cands:
                return idx, []
            ranked = []
            for c in cands:
                if not self.graph_edge_lengths_fit_seed(idx, c, placed):
                    continue
                if not self.graph_edge_lengths_fit_global(idx, c, placed):
                    continue
                if not self.graph_edge_angles_fit_target(idx, c, placed):
                    continue
                err = self.candidate_error(idx, c, placed, scale)
                if err <= self.candidate_error_limit:
                    ranked.append((err, c))
            ranked.sort(key=lambda x: (x[0], repr(x[1])))
            limited = [c for _, c in ranked[: self.branch_cap]]
            face_progress, closes_face = self.face_progress(idx, placed)
            item = (idx, limited, len(placed_neighbors), len(limited), face_progress, closes_face)
            if (
                best is None
                or item[5] > best[5]
                or (item[5] == best[5] and item[4] > best[4])
                or (item[5] == best[5] and item[4] == best[4] and item[2] > best[2])
                or (item[5] == best[5] and item[4] == best[4] and item[2] == best[2] and item[3] < best[3])
            ):
                best = item
        if best is None:
            return None, []
        return best[0], best[1]

    def is_regular_exact(self, score: dict) -> bool:
        return (
            score["edge_length_cv"] < 1e-8
            and score["max_face_side_cv"] < 1e-8
            and score["max_face_planarity_error_over_edge"] < 1e-8
            and score["max_face_angle_rms_deg"] < 1e-6
        )

    def final_score(self, score: dict, struts: dict) -> float:
        return objective_from_score(score, struts)

    def candidate_hash(self, points, score: dict) -> str:
        return geometry_hash(points, score)


def geometry_hash(points: list[tuple[float, float, float]], score: dict) -> str:
    """Hash by intrinsic distances, ignoring global rotation/reflection."""

    ds = []
    for i, j in combinations(range(len(points)), 2):
        ds.append(math.sqrt(dist2(points[i], points[j])))
    positive = [d for d in ds if d > 1e-9]
    unit = sum(positive) / len(positive)
    payload = json.dumps(
        {
            "distances": [round(d / unit, 7) for d in sorted(ds)],
            "edge_cv": round(score["edge_length_cv"], 7),
            "angle": round(score["max_face_angle_rms_deg"], 5),
            "angle_range": round(score["max_face_angle_range_deg"], 5),
            "radial": round(score["radial_cv"], 7),
            "radial_range": round(score["radial_range"], 7),
            "convex": round(score["convexity_violation"], 7),
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


class ZomeEmbeddingSearch(ZomeEmbeddingSearch):
    def candidate_hash(self, points, score: dict) -> str:
        return geometry_hash(points, score)

    def _old_candidate_hash(self, points, score: dict) -> str:
        ds = []
        for i, j in combinations(range(len(points)), 2):
            ds.append(round(math.sqrt(dist2(points[i], points[j])), 8))
        payload = json.dumps(
            {
                "d": sorted(ds),
                "edge_cv": round(score["edge_length_cv"], 8),
                "angle": round(score["max_face_angle_rms_deg"], 6),
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def accept(self, placed: dict[int, tuple]) -> None:
        keys = [placed[i] for i in range(len(placed))]
        gf_points = [self.point(k) for k in keys]
        points = gf_points_to_float(gf_points)
        score = score_embedding(self.target, points)
        struts = audit_struts(gf_points, self.target["edges"], self.edge_lookup)
        if struts["missing"] != 0 or self.is_regular_exact(score):
            return
        fairness_passed = passes_fairness(score)
        if self.require_fairness and not fairness_passed:
            return
        h = self.candidate_hash(points, score)
        item = {
            "hash": h,
            "target": self.target["name"],
            "score": score,
            "struts": struts,
            "objective": self.final_score(score, struts),
            "vertices_golden": [gf_point_json(p) for p in gf_points],
            "edges": self.target["edges"],
            "fairness_passed": fairness_passed,
            "method": "from-scratch zome graph search",
        }
        old = self.results.get(h)
        if old is None or item["objective"] < old["objective"]:
            self.results[h] = item
        if len(self.results) > self.keep * 8:
            best = sorted(self.results.values(), key=lambda r: r["objective"])[: self.keep * 4]
            self.results = {r["hash"]: r for r in best}

    def write_progress(self, phase: str, extra: dict | None = None) -> None:
        self.progress_path.parent.mkdir(parents=True, exist_ok=True)
        now = time.time()
        elapsed = now - self.started if self.started else 0.0
        node_rate = self.nodes / elapsed if elapsed > 0 else 0.0
        completed_rate = self.completed / elapsed if elapsed > 0 else 0.0
        remaining_sec = max(0.0, self.time_limit - elapsed) if phase != "done" else 0.0
        data = {
            "target": self.target["name"],
            "phase": phase,
            "elapsed_sec": elapsed,
            "remaining_time_limit_sec": remaining_sec,
            "nodes": self.nodes,
            "nodes_per_sec": node_rate,
            "completed": self.completed,
            "completed_per_sec": completed_rate,
            "kept": len(self.results),
            "current_depth": self.current_depth,
            "initial_edge_index": self.current_initial_edge_index,
            "initial_edge_count": self.initial_edge_count,
            "initial_edge_fraction": (
                self.current_initial_edge_index / self.initial_edge_count if self.initial_edge_count else 0.0
            ),
            "second_level_vertex": self.second_level_vertex,
            "second_level_candidate_index": self.second_level_candidate_index,
            "second_level_candidate_count": self.second_level_candidate_count,
            "second_level_fraction": (
                self.second_level_candidate_index / self.second_level_candidate_count
                if self.second_level_candidate_count
                else 0.0
            ),
            "params": {
                "min_scale": self.min_scale,
                "max_scale": self.max_scale,
                "coord_bound": self.coord_bound,
                "branch_cap": self.branch_cap,
                "max_initial_edges": self.max_initial_edges,
                "candidate_error_limit": self.candidate_error_limit,
                "require_fairness": self.require_fairness,
                "progress_interval_sec": self.progress_interval_sec,
                "seed_edge_ratio_limit": self.seed_edge_ratio_limit,
                "seed_scale": self.seed_scale,
                "one_seed_per_color": self.one_seed_per_color,
                "edge_length_ratio_limit": self.edge_length_ratio_limit,
                "edge_angle_tolerance_deg": self.edge_angle_tolerance_deg,
                "max_edge_struts": self.max_edge_struts,
            },
        }
        if extra:
            data.update(extra)
        self.progress_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(
            "progress "
            + json.dumps(
                {
                    "target": data["target"],
                    "phase": phase,
                    "elapsed_sec": round(elapsed, 1),
                    "remaining_sec": round(remaining_sec, 1),
                    "nodes": self.nodes,
                    "completed": self.completed,
                    "kept": len(self.results),
                    "depth": self.current_depth,
                    "initial_edge": f"{self.current_initial_edge_index}/{self.initial_edge_count}",
                    "second_level": f"{self.second_level_candidate_index}/{self.second_level_candidate_count}",
                },
                sort_keys=True,
            ),
            flush=True,
        )

    def backtrack(self, placed: dict[int, tuple], used: set[tuple], scale: float) -> None:
        if time.time() - self.started > self.time_limit:
            raise TimeoutError
        self.nodes += 1
        self.current_depth = max(self.current_depth, len(placed))
        if time.time() - self.last_progress >= self.progress_interval_sec:
            self.last_progress = time.time()
            self.write_progress("searching")
        if len(placed) == len(self.target["points"]):
            self.completed += 1
            self.accept(placed)
            return
        idx, candidates = self.choose_vertex(placed, used, scale)
        if idx is None or not candidates:
            return
        is_second_level = len(placed) == 2
        if is_second_level:
            self.second_level_vertex = idx
            self.second_level_candidate_count = len(candidates)
            self.second_level_candidate_index = 0
            self.last_progress = time.time()
            self.write_progress("searching")
        for cand_index, cand in enumerate(candidates, 1):
            if is_second_level:
                self.second_level_candidate_index = cand_index
            placed[idx] = cand
            used.add(cand)
            self.backtrack(placed, used, scale)
            used.remove(cand)
            del placed[idx]

    def run(self) -> list[dict]:
        self.started = time.time()
        origin = vkey((GF(0), GF(0), GF(0)))
        first_edges = self.initial_edges()
        self.initial_edge_count = len(first_edges)
        self.current_initial_edge_index = 0
        self.write_progress("starting", {"initial_edges": len(first_edges)})
        for pos, edge in enumerate(first_edges):
            self.current_initial_edge_index = pos + 1
            self.second_level_vertex = None
            self.second_level_candidate_index = 0
            self.second_level_candidate_count = 0
            self.seed_edge_length = edge.length
            self.seed_edge_scale_ratio = edge.length / self.target_dists[(0, 1)]
            if time.time() - self.started > self.time_limit:
                break
            scale = self.seed_edge_scale_ratio
            try:
                self.backtrack({0: origin, 1: edge.key}, {origin, edge.key}, scale)
            except TimeoutError:
                break
            if time.time() - self.last_progress >= self.progress_interval_sec:
                self.last_progress = time.time()
                self.write_progress(
                    "searching",
                    {
                        "initial_edge_index": pos,
                        "initial_edge_color": edge.primary_color,
                        "initial_edge_scale": edge.scale_label,
                        "initial_edge_struts": len(edge.segments),
                    },
                )
        best = sorted(self.results.values(), key=lambda r: r["objective"])[: self.keep]
        self.write_progress("done", {"emitted": len(best)})
        return best


def expand_edges_for_emission(points, edges, edge_lookup: dict) -> tuple[list, list[tuple[int, int]]]:
    out_points = list(points)
    point_to_index = {vkey(point): idx for idx, point in enumerate(out_points)}
    out_edges: list[tuple[int, int]] = []

    def point_index(point) -> int:
        key = vkey(point)
        idx = point_to_index.get(key)
        if idx is None:
            idx = len(out_points)
            out_points.append(point)
            point_to_index[key] = idx
        return idx

    for i, j in edges:
        edge = edge_lookup.get(vkey(vsub(points[j], points[i])))
        if edge is None:
            out_edges.append((i, j))
            continue
        start = i
        cursor = points[i]
        for segment in edge.segments[:-1]:
            cursor = vadd(cursor, segment.vector)
            mid = point_index(cursor)
            out_edges.append((start, mid))
            start = mid
        out_edges.append((start, j))
    return out_points, out_edges


def emit_search_results(
    results: list[dict],
    target_name: str,
    out_dir: Path,
    emit_scale_power: int = 2,
    edge_lookup: dict | None = None,
) -> dict:
    target_dir = out_dir / target_name
    target_dir.mkdir(parents=True, exist_ok=True)
    for old in target_dir.glob("*.vZome"):
        old.unlink()
    emit_scale = phi_pow(emit_scale_power)
    emitted = []
    for rank, result in enumerate(results, 1):
        points = [
            tuple(GF(Fraction(coord[0]), Fraction(coord[1])) for coord in vertex)
            for vertex in result["vertices_golden"]
        ]
        emit_points = points
        emit_edges = result["edges"]
        if edge_lookup is not None:
            emit_points, emit_edges = expand_edges_for_emission(points, result["edges"], edge_lookup)
        scaled_points = [vscale(p, emit_scale) for p in emit_points]
        filename = f"{target_name}_approx_{rank:02d}_{result['hash']}.vZome"
        emit_vzome(scaled_points, emit_edges, target_dir / filename)
        out = dict(result)
        out["file"] = filename
        out["emit_scale_power"] = emit_scale_power
        out["emitted_balls"] = len(emit_points)
        out["emitted_struts"] = len(emit_edges)
        emitted.append(out)
    manifest = {
        "target": target_name,
        "purpose": "Approximate, non-exact RGBY zomeable realization of the Platonic graph.",
        "emit_scale_power": emit_scale_power,
        "models": emitted,
    }
    (target_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def run_search(args) -> dict:
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    all_manifest = {
        "purpose": "Approximate non-exact RGBY zomeable Platonic-solid graph models.",
        "note": (
            "Exact vZome Platonic solids are known; this experiment intentionally "
            "keeps non-exact realizations that score close to regular in edge "
            "length, face side lengths, face planarity, and face angles."
        ),
        "targets": {},
    }
    for name in expand_targets(args.targets):
        search = ZomeEmbeddingSearch(
            name,
            out_dir,
            min_scale=args.min_scale,
            max_scale=args.max_scale,
            coord_bound=args.coord_bound,
            branch_cap=args.branch_cap,
            keep=args.keep,
            time_limit=args.seconds_per_target,
            max_initial_edges=args.max_initial_edges,
            candidate_error_limit=args.candidate_error_limit,
            require_fairness=not args.allow_rough_scratch,
            progress_interval_sec=args.progress_interval_sec,
            seed_edge_ratio_limit=args.seed_edge_ratio_limit,
            seed_scale=args.seed_scale,
            one_seed_per_color=args.one_seed_per_color,
            edge_length_ratio_limit=args.edge_length_ratio_limit,
            edge_angle_tolerance_deg=args.edge_angle_tolerance_deg,
            max_edge_struts=args.max_edge_struts,
        )
        results = search.run()
        if len(results) < args.keep and not args.no_exact_fallback:
            fallback = approximate_from_exact(name, args.keep, out_dir, args)
            if not fallback and not results:
                fallback = approximate_from_exact(
                    name,
                    max(3, min(args.keep, 6)),
                    out_dir,
                    args,
                    require_fairness=False,
                )
            if fallback:
                merged = {r["hash"]: r for r in results}
                merged.update({r["hash"]: r for r in fallback})
                results = sorted(merged.values(), key=lambda r: r["objective"])[: args.keep]
        manifest = emit_search_results(results, name, out_dir, args.emit_scale_power, search.edge_lookup)
        all_manifest["targets"][name] = {
            "count": len(manifest["models"]),
            "best_objective": manifest["models"][0]["objective"] if manifest["models"] else None,
            "models": [m["file"] for m in manifest["models"]],
        }
    (out_dir / "manifest.json").write_text(json.dumps(all_manifest, indent=2) + "\n", encoding="utf-8")
    return all_manifest


def seed_tetrahedron():
    points = [
        (GF(1), GF(1), GF(1)),
        (GF(1), GF(-1), GF(-1)),
        (GF(-1), GF(1), GF(-1)),
        (GF(-1), GF(-1), GF(1)),
    ]
    return points, target("tetrahedron")["edges"]


def seed_cube():
    step = (GF(2), GF(2), GF(0))
    points = []
    for x, y, z in product((0, 1), repeat=3):
        points.append((step[0] * x, step[1] * y, step[0] * z))
    return points, target("cube")["edges"]


def seed_octahedron():
    points = [
        (GF(0), GF(0), GF(0)),
        (GF(0), GF(4), GF(0)),
        (GF(2), GF(2), GF(0)),
        (GF(-2), GF(2), GF(0)),
        (GF(0), GF(2), GF(2)),
        (GF(0), GF(2), GF(-2)),
    ]
    return points, target("octahedron")["edges"]


def zome_graph_points(max_steps: int = 1, min_scale: int = -2, max_scale: int = 2):
    origin = (GF(0), GF(0), GF(0))
    levels = [{vkey(origin)}]
    seen = {vkey(origin)}
    struts = [v for _, v, _, _, _ in strut_vectors(min_scale, max_scale)]
    for _ in range(max_steps):
        nxt = set()
        for k in levels[-1]:
            p = key_to_point(k)
            for s in struts:
                q = vkey(vadd(p, s))
                if q not in seen:
                    seen.add(q)
                    nxt.add(q)
        levels.append(nxt)
    return [key_to_point(k) for k in seen]


def exact_regular_candidates(name: str):
    seeds = []
    if name == "tetrahedron":
        points, edges = seed_tetrahedron()
        seeds.append({"points": points, "edges": edges, "faces": target(name)["faces"]})
    elif name == "cube":
        points, edges = seed_cube()
        seeds.append({"points": points, "edges": edges, "faces": target(name)["faces"]})
    elif name == "octahedron":
        points, edges = seed_octahedron()
        seeds.append({"points": points, "edges": edges, "faces": target(name)["faces"]})

    # Discover exact small-coordinate candidates for the larger Platonic graphs
    # from the zome graph.  These are used only as parents for deformations.
    if name in {"icosahedron", "dodecahedron"}:
        t = target(name)
        pts = zome_graph_points(max_steps=1, min_scale=-2, max_scale=2)
        by_count: dict[float, list] = {}
        for p in pts:
            key = round(gf_dist2_float(p), 8)
            by_count.setdefault(key, []).append(p)
        for group in by_count.values():
            if len(group) == len(t["points"]):
                gf_points = sorted(group, key=lambda p: repr(vkey(p)))
                float_points = gf_points_to_float(gf_points)
                edges = regular_edges(float_points)
                if len(edges) != len(t["edges"]):
                    continue
                faces = chordless_cycles(len(gf_points), edges, len(t["faces"][0]))
                if len(faces) != len(t["faces"]):
                    continue
                graph = {"name": name, "points": float_points, "edges": edges, "faces": faces}
                if audit_struts(gf_points, edges)["missing"] == 0:
                    score = score_embedding(graph, float_points)
                    if (
                        score["edge_length_cv"] < 1e-8
                        and score["max_face_side_cv"] < 1e-8
                        and score["max_face_angle_rms_deg"] < 1e-6
                    ):
                        seeds.append({"points": gf_points, "edges": edges, "faces": faces})
    return seeds


def mat_vec(matrix, point):
    return tuple(sum((matrix[row][col] * point[col] for col in range(3)), GF(0)) for row in range(3))


def gf_matrix_candidates():
    one = GF(1)
    zero = GF(0)
    eps_values = [phi_pow(-3), -phi_pow(-3), phi_pow(-2), -phi_pow(-2), phi_pow(-1), -phi_pow(-1)]
    scales = [
        (one, one, phi_pow(1)),
        (one, one, phi_pow(-1)),
        (one, phi_pow(1), phi_pow(-1)),
        (phi_pow(1), phi_pow(-1), one),
    ]

    matrices = []
    for diag in scales:
        matrices.append(tuple(tuple(diag[i] if i == j else zero for j in range(3)) for i in range(3)))
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            for eps in eps_values:
                matrix = [[one if r == c else zero for c in range(3)] for r in range(3)]
                matrix[i][j] = eps
                matrices.append(tuple(tuple(row) for row in matrix))
    for diag in scales:
        for i in range(3):
            for j in range(3):
                if i == j:
                    continue
                for eps in eps_values[:4]:
                    matrix = [[diag[r] if r == c else zero for c in range(3)] for r in range(3)]
                    matrix[i][j] = eps
                    matrices.append(tuple(tuple(row) for row in matrix))
    return matrices


def moved_vertex_count(original, moved) -> int:
    return sum(1 for p, q in zip(original, moved) if vkey(p) != vkey(q))


def add_result(
    results: dict[str, dict],
    name: str,
    graph: dict,
    points,
    edges,
    method: str,
    moved_vertices: int,
    require_fairness: bool = True,
) -> None:
    if moved_vertices < 3:
        return
    if len({vkey(p) for p in points}) != len(points):
        return
    struts = audit_struts(points, edges)
    if struts["missing"] != 0:
        return
    float_points = gf_points_to_float(points)
    score = score_embedding(graph, float_points)
    fairness_passed = passes_fairness(score)
    if require_fairness and not fairness_passed:
        return
    h = geometry_hash(float_points, score)
    item = {
        "hash": h,
        "target": name,
        "score": score,
        "struts": struts,
        "objective": objective_from_score(score, struts),
        "vertices_golden": [gf_point_json(p) for p in points],
        "edges": edges,
        "method": method,
        "moved_vertices": moved_vertices,
        "fairness_passed": fairness_passed,
    }
    old = results.get(h)
    if old is None or item["objective"] < old["objective"]:
        results[h] = item


def linear_deformations(name: str, parent: dict, graph: dict, results: dict[str, dict], require_fairness: bool = True) -> None:
    parent_points = parent["points"]
    for matrix in gf_matrix_candidates():
        moved = [mat_vec(matrix, p) for p in parent_points]
        add_result(
            results,
            name,
            graph,
            moved,
            parent["edges"],
            "global GF linear deformation from exact parent",
            moved_vertex_count(parent_points, moved),
            require_fairness,
        )


def distributed_vertex_deformations(
    name: str,
    parent: dict,
    graph: dict,
    results: dict[str, dict],
    require_fairness: bool = True,
    *,
    move_min_scale: int = -3,
    move_max_scale: int = 0,
    max_move_length: float = 2.4,
    options_per_vertex: int = 2,
    max_moved_vertices: int = 5,
    max_checked_sets: int = 350,
    max_checked_products: int = 6000,
) -> None:
    parent_points = parent["points"]
    edges = parent["edges"]
    n = len(parent_points)
    adj = {i: set() for i in range(n)}
    for i, j in edges:
        adj[i].add(j)
        adj[j].add(i)

    moves = [v for _, v, _, _, length in strut_vectors(move_min_scale, move_max_scale) if length <= max_move_length]
    replacements: dict[int, list] = {}
    for vertex_idx in range(n):
        options = []
        for move in moves:
            for sign in (1, -1):
                q = vadd(parent_points[vertex_idx], tuple(sign * c for c in move))
                if vkey(q) == vkey(parent_points[vertex_idx]) or vkey(q) in {vkey(p) for p in parent_points}:
                    continue
                if all(classify_strut(q, parent_points[nb]) is not None for nb in adj[vertex_idx]):
                    move_len = math.sqrt(gf_dist2_float(tuple(q[i] - parent_points[vertex_idx][i] for i in range(3))))
                    options.append((move_len, q))
        options = sorted({vkey(q): (move_len, q) for move_len, q in options}.values(), key=lambda item: item[0])
        if options:
            replacements[vertex_idx] = [q for _, q in options[:options_per_vertex]]

    min_moved = 3
    checked_sets = 0
    checked_products = 0
    for size in range(min_moved, min(max_moved_vertices, n) + 1):
        for vertices in combinations(sorted(replacements), size):
            if any(b in adj[a] for a, b in combinations(vertices, 2)):
                continue
            checked_sets += 1
            if checked_sets > max_checked_sets:
                return
            for choices in product(*(replacements[v] for v in vertices)):
                checked_products += 1
                if checked_products > max_checked_products:
                    return
                moved = list(parent_points)
                for vertex_idx, q in zip(vertices, choices):
                    moved[vertex_idx] = q
                add_result(
                    results,
                    name,
                    graph,
                    moved,
                    edges,
                    f"distributed {size}-vertex zome deformation from exact parent",
                    size,
                    require_fairness,
                )


def approximate_from_exact(name: str, keep: int, out_dir: Path, args, require_fairness: bool = True) -> list[dict]:
    """Generate non-exact approximations by local zome-graph deformations.

    This intentionally starts from exact zomeable Platonic parents, then moves
    vertices by zome struts while preserving all target graph edges as struts.
    """

    parents = exact_regular_candidates(name)
    results: dict[str, dict] = {}
    for parent in parents:
        parent_points = parent["points"]
        edges = parent["edges"]
        graph = {
            "name": name,
            "points": gf_points_to_float(parent_points),
            "edges": edges,
            "faces": parent["faces"],
        }
        linear_deformations(name, parent, graph, results, require_fairness)
        distributed_vertex_deformations(
            name,
            parent,
            graph,
            results,
            require_fairness,
            move_min_scale=args.deform_min_scale,
            move_max_scale=args.deform_max_scale,
            max_move_length=args.deform_max_move_length,
            options_per_vertex=args.deform_options_per_vertex,
            max_moved_vertices=args.deform_max_moved_vertices,
            max_checked_sets=args.deform_max_checked_sets,
            max_checked_products=args.deform_max_checked_products,
        )
    best = sorted(results.values(), key=lambda r: r["objective"])[:keep]
    if best:
        emit_search_results(best, name, out_dir)
    return best


def emit_seeds(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "purpose": "calibration seeds for approximate RGBY Platonic searches",
        "note": (
            "These seeds are exact/simple zomeable baselines, not the final goal. "
            "The approximation search should prefer visually close non-exact models."
        ),
        "targets": {},
        "models": [],
    }
    for name in PLATONIC_TARGETS:
        t = target(name)
        manifest["targets"][name] = {
            "vertices": len(t["points"]),
            "edges": len(t["edges"]),
            "faces": len(t["faces"]),
            "face_size": len(t["faces"][0]) if t["faces"] else None,
        }

    for name, builder in (("tetrahedron_green_exact_seed", seed_tetrahedron), ("cube_blue_exact_seed", seed_cube)):
        points, edges = builder()
        target_name = name.split("_")[0]
        out_path = out_dir / f"{name}.vZome"
        emit_vzome(points, edges, out_path)
        manifest["models"].append(
            {
                "file": out_path.name,
                "target": target_name,
                "struts": audit_struts(points, edges),
                "score": score_embedding(target(target_name), gf_points_to_float(points)),
            }
        )

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-seeds", action="store_true", help="emit initial exact calibration seeds")
    parser.add_argument("--search", action="store_true", help="run approximate non-exact Platonic/Archimedean searches")
    parser.add_argument("--verify-targets", action="store_true", help="verify target geometry/counts without searching")
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument(
        "--targets",
        nargs="+",
        default=PLATONIC_TARGETS,
        help="target names, or aliases: platonic, archimedean, catalan, all_platonic, all_archimedean, all_catalan, all",
    )
    parser.add_argument("--min-scale", type=int, default=-2)
    parser.add_argument("--max-scale", type=int, default=1)
    parser.add_argument("--coord-bound", type=float, default=18.0)
    parser.add_argument("--branch-cap", type=int, default=64)
    parser.add_argument("--keep", type=int, default=20)
    parser.add_argument("--seconds-per-target", type=float, default=120.0)
    parser.add_argument("--max-initial-edges", type=int, default=96)
    parser.add_argument("--emit-scale-power", type=int, default=2)
    parser.add_argument("--candidate-error-limit", type=float, default=0.75)
    parser.add_argument("--progress-interval-sec", type=float, default=60.0)
    parser.add_argument(
        "--seed-edge-ratio-limit",
        type=float,
        default=0.0,
        help="early-prune graph edges longer than this factor from the initial seed edge; 0 disables",
    )
    parser.add_argument(
        "--seed-scale",
        type=int,
        default=None,
        help="only use initial seed edges at this phi scale; e.g. 0 tries B0/G0/R0/Y0 representatives",
    )
    parser.add_argument(
        "--one-seed-per-color",
        action="store_true",
        help="for initial edges, keep one canonical direction for each available strut color",
    )
    parser.add_argument(
        "--edge-length-ratio-limit",
        type=float,
        default=0.0,
        help="early-prune if all placed graph-edge lengths exceed this max/min ratio; 0 disables",
    )
    parser.add_argument(
        "--edge-angle-tolerance-deg",
        type=float,
        default=0.0,
        help="early-prune incident graph-edge angles farther than this many degrees from target; 0 disables",
    )
    parser.add_argument(
        "--max-edge-struts",
        type=int,
        choices=(1, 2),
        default=1,
        help="allow each target graph edge to be a path of one or two collinear standard struts",
    )
    parser.add_argument(
        "--allow-rough-scratch",
        action="store_true",
        help="keep from-scratch candidates even when they miss the fairness gates",
    )
    parser.add_argument(
        "--no-exact-fallback",
        action="store_true",
        help="do not add exact-parent deformation candidates when direct search is sparse",
    )
    parser.add_argument("--deform-min-scale", type=int, default=-3)
    parser.add_argument("--deform-max-scale", type=int, default=0)
    parser.add_argument("--deform-max-move-length", type=float, default=2.4)
    parser.add_argument("--deform-options-per-vertex", type=int, default=2)
    parser.add_argument("--deform-max-moved-vertices", type=int, default=5)
    parser.add_argument("--deform-max-checked-sets", type=int, default=350)
    parser.add_argument("--deform-max-checked-products", type=int, default=6000)
    args = parser.parse_args()
    if args.search:
        manifest = run_search(args)
        print(json.dumps(manifest, indent=2))
    elif args.verify_targets:
        verified = {name: verify_target(name) for name in expand_targets(args.targets)}
        print(json.dumps(verified, indent=2))
    elif args.emit_seeds:
        manifest = emit_seeds(args.out)
        print(json.dumps(manifest, indent=2))
    else:
        for name in KNOWN_TARGETS:
            t = target(name)
            face_sizes = target_count_summary(t)["face_sizes"]
            print(f"{name}: V={len(t['points'])} E={len(t['edges'])} F={len(t['faces'])} faces={face_sizes}")


if __name__ == "__main__":
    main()
