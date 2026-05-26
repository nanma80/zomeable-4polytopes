"""Evaluate and emit 1_32 / 576-vertex E7 Wythoff orbit projections.

The 1_32 polytope has the same unoriented edge-direction set as the E7 root
polytope (2_31): all E7 roots.  Therefore the raw-column zomeability
constraints are identical to the completed 2_31 sweep.  This script reuses the
2_31 sweep hits and evaluates/emits the corresponding 1_32 source models.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

from emit_vzome import GF, HEADER, FOOTER, classify_direction, pt_str, vkey, vsub  # noqa: E402

spec_col = importlib.util.spec_from_file_location("col", Path(__file__).resolve().parent / "zphi_column_sweep.py")
col = importlib.util.module_from_spec(spec_col)
assert spec_col.loader is not None
spec_col.loader.exec_module(col)


SIMPLE_E7 = np.array([
    [0, 0, 1, -1, 0, 0, 0, 0],
    [0, 0, 0, 1, -1, 0, 0, 0],
    [0, 0, 0, 0, 1, -1, 0, 0],
    [0, 0, 0, 0, 0, 1, -1, 0],
    [0, 0, 0, 0, 0, 0, 1, -1],
    [0, 0, 0, 0, 0, 0, 1, 1],
    [0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, 0.5],
], dtype=float)


def reflection(x, a):
    return x - (x @ a) * a


def build_1_32_vertices():
    """Weyl orbit of the fundamental weight with orbit size 576."""
    weights = np.linalg.inv(SIMPLE_E7 @ SIMPLE_E7.T) @ SIMPLE_E7
    w = weights[5]
    seen = {tuple(np.round(w, 10)): w}
    stack = [w]
    while stack:
        x = stack.pop()
        for a in SIMPLE_E7:
            y = reflection(x, a)
            k = tuple(np.round(y, 10))
            if k not in seen:
                seen[k] = y
                stack.append(y)
    V = np.asarray(list(seen.values()), dtype=float)
    assert V.shape == (576, 8)
    return V


def edges_by_shortest_distance(V):
    vals = []
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            vals.append(float(np.sum((V[i] - V[j]) ** 2)))
    min_d2 = min(v for v in vals if v > 1e-10)
    edges = []
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            if abs(float(np.sum((V[i] - V[j]) ** 2)) - min_d2) < 1e-8:
                edges.append((i, j))
    assert len(edges) == 10080
    return edges


def coeff(x: float) -> Fraction:
    # Orbit coordinates are rational with denominator dividing 4 in this basis.
    q = Fraction(str(round(float(x), 10))).limit_denominator(24)
    if abs(float(q) - float(x)) > 1e-8:
        raise ValueError(x)
    return q


def gf_from_pair(pair, scale=Fraction(1)):
    return GF(Fraction(pair[0]) * scale, Fraction(pair[1]) * scale)


def project_vertex(vertex, columns):
    coords = [GF(0), GF(0), GF(0)]
    for x, c in zip(vertex, columns):
        q = coeff(float(x))
        if q == 0:
            continue
        for r in range(3):
            coords[r] = coords[r] + gf_from_pair(c[r], q)
    return tuple(coords)


def matrix_from_columns(columns):
    g = col.ZERO_GRAM
    for c in columns:
        g = col.gram_add(g, col.outer_gram(c))
    return col.matrix_from_columns(columns, g)


def shape_sig(V3, decimals=4):
    return col.shape_sig(V3, decimals=decimals)


def evaluate_hit(sig, hit, V, edges, out_path):
    columns = [
        tuple(tuple(int(x) for x in z) for z in c)
        for c in hit["columns"]
    ]
    P = matrix_from_columns(columns)
    V3 = V @ P.T
    Vc = V3 - V3.mean(axis=0)
    cov = Vc.T @ Vc / max(1, len(V3) - 1)
    ev = np.linalg.eigvalsh(cov)
    sv = np.linalg.svd(Vc, compute_uv=False)
    projected = [project_vertex(v, columns) for v in V]

    point_index = {}
    points = []
    vertex_to_point = []
    for p in projected:
        k = vkey(p)
        if k not in point_index:
            point_index[k] = len(points)
            points.append(p)
        vertex_to_point.append(point_index[k])

    edge_set = set()
    collapsed = 0
    for i, j in edges:
        a = vertex_to_point[i]
        b = vertex_to_point[j]
        if a == b:
            collapsed += 1
            continue
        edge_set.add((min(a, b), max(a, b)))
    edge_list = sorted(edge_set)

    audit = Counter()
    bad = []
    for a, b in edge_list:
        c = classify_direction(points[a], points[b])
        if c is None or c[0] == "_":
            audit["BAD"] += 1
            bad.append((a, b, pt_str(vsub(points[b], points[a]))))
        else:
            audit[c[0]] += 1

    if not bad:
        cmds = [f'    <ShowPoint point="{pt_str(p)}"/>' for p in points]
        cmds += [
            f'    <JoinPointPair start="{pt_str(points[a])}" end="{pt_str(points[b])}"/>'
            for a, b in edge_list
        ]
        origin = "0 0 0 0 0 0"
        if not any(pt_str(p) == origin for p in points):
            cmds.append(f'    <SelectManifestation point="{origin}"/>')
            cmds.append("    <Delete/>")
        xml = HEADER
        xml += f'  <EditHistory editNumber="{len(cmds)}" lastStickyEdit="-1">\n'
        xml += "\n".join(cmds) + "\n"
        xml += "  </EditHistory>\n" + FOOTER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(xml, encoding="utf-8")

    return {
        "ok": not bad,
        "sig": sig,
        "shape_sig": shape_sig(V3),
        "file": str(out_path),
        "balls": len(points),
        "visible_edges": len(edge_list),
        "source_edges": len(edges),
        "collapsed": collapsed,
        "audit": dict(audit),
        "bad": bad[:5],
        "cov_eigs": [float(x) for x in ev],
        "rank_singular_values": [float(x) for x in sv],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="ongoing_work/gosset_2_31/column_sweep_2_31_R3.json")
    ap.add_argument("--out_dir", default="output/gosset_1_32_candidates")
    args = ap.parse_args()
    data = json.loads((ROOT / args.json).read_text())
    V = build_1_32_vertices()
    edges = edges_by_shortest_distance(V)
    out_dir = ROOT / args.out_dir
    manifest = []
    for sig, hit in sorted(data["hits"].items()):
        out = out_dir / f"1_32_from_{sig}.vZome"
        info = evaluate_hit(sig, hit, V, edges, out)
        manifest.append(info)
        print(sig, info)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
