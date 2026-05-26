"""Emit vZome files for 2_31 / E7-root-polytope sweep hits."""
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

spec = importlib.util.spec_from_file_location("sweep231", Path(__file__).resolve().parent / "zphi_2_31_sweep.py")
sweep231 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(sweep231)


def coeff(x: float) -> Fraction:
    if abs(x - 1.0) < 1e-9:
        return Fraction(1)
    if abs(x + 1.0) < 1e-9:
        return Fraction(-1)
    if abs(x - 0.5) < 1e-9:
        return Fraction(1, 2)
    if abs(x + 0.5) < 1e-9:
        return Fraction(-1, 2)
    if abs(x) < 1e-9:
        return Fraction(0)
    raise ValueError(x)


def gf_from_pair(pair, scale=Fraction(1)):
    return GF(Fraction(pair[0]) * scale, Fraction(pair[1]) * scale)


def project_root(root, columns):
    coords = [GF(0), GF(0), GF(0)]
    for x, col in zip(root, columns):
        q = coeff(float(x))
        if q == 0:
            continue
        for r in range(3):
            coords[r] = coords[r] + gf_from_pair(col[r], q)
    return tuple(coords)


def e7_edges(roots):
    edges = []
    for i in range(len(roots)):
        for j in range(i + 1, len(roots)):
            if abs(float(np.dot(roots[i], roots[j])) - 1.0) < 1e-9:
                edges.append((i, j))
    return edges


def emit_hit(sig, hit, out_path):
    columns = [
        tuple(tuple(int(x) for x in z) for z in c)
        for c in hit["columns"]
    ]
    roots = sweep231.build_e7_roots()
    edges = e7_edges(roots)
    projected = [project_root(root, columns) for root in roots]

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
    if bad:
        return {
            "ok": False,
            "reason": "non_zome_edges",
            "sig": sig,
            "bad": bad[:5],
            "audit": dict(audit),
        }

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
        "ok": True,
        "sig": sig,
        "file": str(out_path),
        "balls": len(points),
        "edges": len(edge_list),
        "source_edges": len(edges),
        "collapsed": collapsed,
        "audit": dict(audit),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="ongoing_work/gosset_2_31/column_sweep_2_31_R3.json")
    ap.add_argument("--out_dir", default="output/gosset_2_31_candidates")
    args = ap.parse_args()
    d = json.loads((ROOT / args.json).read_text())
    out_dir = ROOT / args.out_dir
    manifest = []
    for sig, hit in sorted(d["hits"].items()):
        out = out_dir / f"2_31_{sig}.vZome"
        audit = emit_hit(sig, hit, out)
        manifest.append(audit)
        print(sig, audit)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
