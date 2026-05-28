"""Emit vZome files for A5-family (5-simplex) sweep hits.

Consumes the polytope-independent sweep output (zphi_a5_sweep.py) and, for each
projection P (6 columns, c_0 = 0), applies P to each of the 19 A5 Wythoff
polytopes, classifies every edge against the exact zome direction orbits,
and writes a vZome file when every edge is a genuine zome strut.

Vertices are represented in 6D with integer coordinates; the projected
coordinate of a vertex is the GF-exact weighted sum of the columns.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import hashlib
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

from emit_vzome import GF, HEADER, FOOTER, classify_direction, pt_str, vkey, vsub  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "col", ROOT / "tools" / "gosset" / "zphi_column_sweep.py"
)
col = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(col)

from family import POLYS, build_polytope  # noqa: E402


def gf_from_pair(pair, scale=Fraction(1)):
    return GF(Fraction(pair[0]) * scale, Fraction(pair[1]) * scale)


def vscale(v, s: GF):
    return tuple(x * s for x in v)


def project_vertex(vertex, columns6, scale: GF):
    coords = [GF(0), GF(0), GF(0)]
    for idx, weight in enumerate(vertex):
        if weight == 0:
            continue
        c = columns6[idx]
        for r in range(3):
            coords[r] = coords[r] + gf_from_pair(c[r]) * weight
    return vscale(tuple(coords), scale)


def matrix_from_columns6(columns6):
    return np.array(
        [[col.zfloat(columns6[j][r]) for j in range(6)] for r in range(3)],
        dtype=float,
    )


def emit_one(name, columns6, out_path, scale: GF):
    verts, V, edges = build_polytope(name)
    P = matrix_from_columns6(columns6)
    V3 = V @ P.T
    Vc = V3 - V3.mean(axis=0)
    cov = Vc.T @ Vc / max(1, len(V3) - 1)
    ev = np.linalg.eigvalsh(cov)
    sv = np.linalg.svd(Vc, compute_uv=False)

    projected = [project_vertex(combo, columns6, scale) for combo in verts]
    point_index = {}
    points = []
    vertex_to_point = []
    for p in projected:
        kk = vkey(p)
        if kk not in point_index:
            point_index[kk] = len(points)
            points.append(p)
        vertex_to_point.append(point_index[kk])

    edge_set = set()
    collapsed = 0
    for i, j in edges:
        a, b = vertex_to_point[i], vertex_to_point[j]
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

    ok = not bad
    if ok:
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
        "ok": ok,
        "polytope": name,
        "file": str(out_path) if ok else None,
        "balls": len(points),
        "visible_edges": len(edge_list),
        "source_edges": len(edges),
        "collapsed": collapsed,
        "shape_sig": col.shape_sig(V3),
        "audit": dict(audit),
        "bad": bad[:5],
        "cov_eigs": [float(x) for x in ev],
        "rank_singular_values": [float(x) for x in sv],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="ongoing_work/a5/column_sweep_a5_R3.json")
    ap.add_argument("--out_dir", default="output/a5_candidates")
    ap.add_argument("--manifest", default="output/a5_candidates/manifest.json")
    args = ap.parse_args()

    data = json.loads((ROOT / args.json).read_text())
    out_dir = ROOT / args.out_dir
    manifest = []
    for key, hit in sorted(data["hits"].items()):
        columns6 = [tuple(tuple(int(x) for x in z) for z in c) for c in hit["columns"]]
        # short stable id from the full 19-polytope family key.
        khash = hashlib.sha1(key.encode()).hexdigest()[:6]
        hid = khash
        for poly in POLYS:
            name = poly["slug"]
            out = out_dir / f"{name}_{hid}.vZome"
            info = emit_one(name, columns6, out, GF(1))
            info["family_key"] = key
            manifest.append(info)
            print(name, hid, {kk: info[kk] for kk in ("ok", "balls", "visible_edges", "collapsed", "audit")})

    manifest_path = ROOT / args.manifest
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    ok_count = sum(1 for m in manifest if m["ok"])
    print(f"\n{ok_count}/{len(manifest)} polytope projections zomeable (BAD==0)")


if __name__ == "__main__":
    main()
