"""Emit vZome files for 2_41 sweep hits."""
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

spec_col = importlib.util.spec_from_file_location(
    "col", Path(__file__).resolve().parent / "zphi_column_sweep.py"
)
col = importlib.util.module_from_spec(spec_col)
assert spec_col.loader is not None
spec_col.loader.exec_module(col)


def build_vertices():
    verts: set[tuple[int, ...]] = set()
    for i in range(8):
        for s in (4, -4):
            v = [0] * 8
            v[i] = s
            verts.add(tuple(v))
    for inds in itertools.combinations(range(8), 4):
        for signs in itertools.product((2, -2), repeat=4):
            v = [0] * 8
            for i, s in zip(inds, signs):
                v[i] = s
            verts.add(tuple(v))
    for pos3 in range(8):
        for signs in itertools.product((1, -1), repeat=8):
            if sum(1 for s in signs if s < 0) % 2 == 0:
                verts.add(tuple((3 if i == pos3 else 1) * s for i, s in enumerate(signs)))
    V = np.asarray(sorted(verts), dtype=float)
    assert V.shape == (2160, 8)
    return V


def build_edges(V):
    edges = []
    for i in range(len(V)):
        d2 = np.sum((V[i + 1:] - V[i]) ** 2, axis=1)
        for off in np.where(np.abs(d2 - 8.0) < 1e-9)[0]:
            edges.append((i, i + 1 + int(off)))
    assert len(edges) == 69120
    return edges


def coeff(x: float) -> Fraction:
    q = Fraction(str(round(float(x), 10))).limit_denominator(8)
    if abs(float(q) - float(x)) > 1e-8:
        raise ValueError(x)
    return q


def gf_from_pair(pair, scale=Fraction(1)):
    return GF(Fraction(pair[0]) * scale, Fraction(pair[1]) * scale)


def vscale(v, s: GF):
    return tuple(x * s for x in v)


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


PUBLISH_INFO = {
    "N65_1d8629f4e5b7": {
        "scale_label": "1/4",
        "scale": GF(Fraction(1, 4), 0),
        "filename": "2_41_B3_65_balls.vZome",
    },
    "N93_1c70aede7272": {
        "scale_label": "1/4",
        "scale": GF(Fraction(1, 4), 0),
        "filename": "2_41_B3_93_balls.vZome",
    },
    "N921_cb19e4987e4f": {
        "scale_label": "1/4",
        "scale": GF(Fraction(1, 4), 0),
        "filename": "2_41_H3_921_balls.vZome",
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
    ap.add_argument("--json", default="ongoing_work/gosset_2_41/column_sweep_2_41_R2.json")
    ap.add_argument("--out_dir", default="output/gosset_projections/2_41")
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
                "filename": f"2_41_from_{sig}.vZome",
            }
        else:
            meta = PUBLISH_INFO[sig]
        out = out_dir / meta["filename"]
        info = emit_hit(sig, hit, V, edges, out, meta["scale"])
        info["scale_factor"] = meta["scale_label"]
        manifest.append(info)
        print(sig, info)
    if args.manifest:
        manifest_path = ROOT / args.manifest
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
