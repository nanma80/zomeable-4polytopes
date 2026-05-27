"""Evaluate and emit rectified 5-orthoplex projections.

The rectified 5-orthoplex is the D5 root polytope with vertices
all permutations of (+/-1, +/-1, 0, 0, 0).  Its edge directions are exactly
the D5 roots.  This emitter consumes the independent rectified 5-orthoplex
raw-column sweep output.
"""
from __future__ import annotations

import argparse
import importlib.util
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

spec_col = importlib.util.spec_from_file_location(
    "col", Path(__file__).resolve().parent / "zphi_column_sweep.py"
)
col = importlib.util.module_from_spec(spec_col)
assert spec_col.loader is not None
spec_col.loader.exec_module(col)


def build_vertices():
    verts = []
    for i in range(5):
        for j in range(i + 1, 5):
            for si in (1, -1):
                for sj in (1, -1):
                    v = np.zeros(5)
                    v[i] = si
                    v[j] = sj
                    verts.append(v)
    return np.asarray(verts, dtype=float)


def build_edges(V):
    edges = []
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            if abs(float(np.dot(V[i], V[j])) - 1.0) < 1e-9:
                edges.append((i, j))
    assert len(edges) == 240
    return edges


def coeff(x: float) -> Fraction:
    if abs(x - 1.0) < 1e-9:
        return Fraction(1)
    if abs(x + 1.0) < 1e-9:
        return Fraction(-1)
    if abs(x) < 1e-9:
        return Fraction(0)
    raise ValueError(x)


def gf_from_pair(pair, scale=Fraction(1)):
    return GF(Fraction(pair[0]) * scale, Fraction(pair[1]) * scale)


def gf_mul(x: GF, y: GF) -> GF:
    return x * y


def vscale(v, s: GF):
    return tuple(gf_mul(x, s) for x in v)


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
    # columns is length 5, but col.matrix_from_columns expects length 8.
    P = np.array([[col.zfloat(columns[j][r]) for j in range(5)] for r in range(3)], dtype=float)
    g = col.ZERO_GRAM
    for c in columns:
        g = col.gram_add(g, col.outer_gram(c))
    return P / np.sqrt(col.gram_scale_float(g))


PUBLISH_INFO = {
    "N19_cf2746136c69": {
        "symmetry": "B3",
        "scale_label": "phi^2/3",
        "scale": GF(Fraction(1, 3), Fraction(1, 3)),
        "filename": "rectified_5_orthoplex_B3_19_balls.vZome",
    },
    "N21_ada25230f743": {
        "symmetry": "D4",
        "scale_label": "2*phi/3",
        "scale": GF(0, Fraction(2, 3)),
        "filename": "rectified_5_orthoplex_D4_21_balls.vZome",
    },
    "N26_5823fab6c04d": {
        "symmetry": "B3",
        "scale_label": "phi^2/3",
        "scale": GF(Fraction(1, 3), Fraction(1, 3)),
        "filename": "rectified_5_orthoplex_B3_26_balls.vZome",
    },
}


def emit_hit(sig, hit, V, edges, out_path, scale=GF(1)):
    columns = [tuple(tuple(int(x) for x in z) for z in c) for c in hit["columns"]]
    P = matrix_from_columns(columns)
    V3 = V @ P.T
    Vc = V3 - V3.mean(axis=0)
    cov = Vc.T @ Vc / max(1, len(V3) - 1)
    ev = np.linalg.eigvalsh(cov)
    sv = np.linalg.svd(Vc, compute_uv=False)
    projected = [vscale(project_vertex(v, columns), scale) for v in V]

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
        "input_sig": sig,
        "shape_sig": col.shape_sig(V3),
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
    ap.add_argument("--json", default="ongoing_work/gosset_rectified_5_orthoplex/column_sweep_rectified_5_orthoplex_R3.json")
    ap.add_argument("--out_dir", default="output/gosset_projections/rectified_5_orthoplex")
    ap.add_argument("--raw", action="store_true", help="emit raw unscaled candidate names")
    ap.add_argument("--manifest", help="optional path to write an audit manifest")
    args = ap.parse_args()
    data = json.loads((ROOT / args.json).read_text())
    V = build_vertices()
    edges = build_edges(V)
    out_dir = ROOT / args.out_dir
    manifest = []
    for sig, hit in sorted(data["hits"].items()):
        if args.raw:
            meta = {
                "scale": GF(1),
                "scale_label": "1",
                "filename": f"rectified_5_orthoplex_from_{sig}.vZome",
            }
        else:
            meta = PUBLISH_INFO[sig]
        out = out_dir / meta["filename"]
        info = emit_hit(sig, hit, V, edges, out, meta["scale"])
        info["scale_factor"] = meta["scale_label"]
        if "symmetry" in meta:
            info["symmetry"] = meta["symmetry"]
        manifest.append(info)
        print(sig, info)
    if args.manifest:
        manifest_path = ROOT / args.manifest
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
