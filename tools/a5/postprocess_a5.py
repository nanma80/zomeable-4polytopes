"""Analyze A5 sweep hits: choose a physical phi-power scale that turns every
edge into a standard vZome strut, and compute the 3D point-cloud symmetry order.

Run from repo root.  Prints a table used to curate the published gallery.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

from emit_vzome import GF, classify_strut, vsub  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "col", ROOT / "tools" / "gosset" / "zphi_column_sweep.py"
)
col = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(col)

PHI = (1 + 5 ** 0.5) / 2
POLYS = (("5_simplex", 1), ("rectified_5_simplex", 2), ("birectified_5_simplex", 3))


def build_polytope(k):
    verts = list(itertools.combinations(range(6), k))
    V = np.zeros((len(verts), 6))
    for r, combo in enumerate(verts):
        for idx in combo:
            V[r, idx] = 1.0
    edges = []
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            if int(np.sum(np.abs(V[i] - V[j]))) == 2:
                edges.append((i, j))
    return verts, V, edges


def gf_pair(pair):
    return GF(Fraction(pair[0]), Fraction(pair[1]))


def project_point(combo, columns6):
    coords = [GF(0), GF(0), GF(0)]
    for idx in combo:
        c = columns6[idx]
        for r in range(3):
            coords[r] = coords[r] + gf_pair(c[r])
    return tuple(coords)


def candidate_scales():
    """GF scales s = (num/den) * phi^n covering plausible normalizations."""
    out = []
    for n in range(-5, 9):
        base = col_phi_pow(n)
        for den in (1, 2, 3, 4, 5, 6):
            for num in range(1, 13):
                f = Fraction(num, den)
                out.append((f"({num}/{den})*phi^{n}", GF(f * base.a, f * base.b)))
    # unique by value
    seen = {}
    for label, s in out:
        k = (s.a, s.b)
        if k not in seen:
            seen[k] = (label, s)
    return list(seen.values())


def col_phi_pow(n):
    from emit_vzome import phi_pow
    return phi_pow(n)


def all_edges_standard(points, edge_list, s: GF):
    colors = []
    for a, b in edge_list:
        pa = tuple(x * s for x in points[a])
        pb = tuple(x * s for x in points[b])
        cls = classify_strut(pa, pb)
        if cls is None:
            return None
        colors.append(cls)
    return colors


def choose_scale(points, edge_list):
    best = None
    for label, s in candidate_scales():
        colors = all_edges_standard(points, edge_list, s)
        if colors is None:
            continue
        # prefer scales with strut powers closest to 0 and small denominator
        powers = [n for _c, n in colors]
        cost = (max(abs(p) for p in powers), s.a.denominator * s.b.denominator,
                abs(s.a) + abs(s.b))
        if best is None or cost < best[0]:
            best = (cost, label, s, colors)
    return best


def symmetry_order(points_num):
    """Count orthogonal maps R (rotations+reflections) preserving the cloud."""
    P = np.asarray(points_num, dtype=float)
    P = P - P.mean(axis=0)
    n = len(P)
    # build a key set for membership testing
    keyset = {tuple(np.round(p, 6)) for p in P}

    def in_cloud(q):
        return tuple(np.round(q, 6)) in keyset

    # pick an anchor non-degenerate basis from the cloud
    norms = np.linalg.norm(P, axis=1)
    order = np.argsort(-norms)
    idx = [i for i in order if norms[i] > 1e-6]
    if len(idx) < 3:
        return 0, "degenerate"
    a0 = P[idx[0]]
    # second: not parallel
    a1 = None
    for i in idx[1:]:
        if np.linalg.norm(np.cross(a0, P[i])) > 1e-6:
            a1 = P[i]
            break
    if a1 is None:
        return 0, "planar"
    a2 = None
    for i in idx[1:]:
        M = np.array([a0, a1, P[i]])
        if abs(np.linalg.det(M)) > 1e-6:
            a2 = P[i]
            break
    if a2 is None:
        return 0, "planar"
    A = np.array([a0, a1, a2]).T  # columns are anchor vectors
    gram_a = A.T @ A

    count = 0
    # candidate images: triples of cloud points with matching Gram
    for j0 in idx:
        if abs(norms[j0] - np.linalg.norm(a0)) > 1e-6:
            continue
        for j1 in idx:
            b0, b1 = P[j0], P[j1]
            if abs(b0 @ b1 - a0 @ a1) > 1e-6:
                continue
            if abs(np.linalg.norm(b1) - np.linalg.norm(a1)) > 1e-6:
                continue
            for j2 in idx:
                b2 = P[j2]
                B = np.array([b0, b1, b2]).T
                if np.max(np.abs(B.T @ B - gram_a)) > 1e-6:
                    continue
                # solve R A = B  ->  R = B A^{-1}
                try:
                    R = B @ np.linalg.inv(A)
                except np.linalg.LinAlgError:
                    continue
                if np.max(np.abs(R @ R.T - np.eye(3))) > 1e-6:
                    continue
                if all(in_cloud(R @ p) for p in P):
                    count += 1
    return count, "ok"


def main():
    data = json.loads((ROOT / "ongoing_work/a5/column_sweep_a5_R3.json").read_text())
    rows = []
    for key, hit in sorted(data["hits"].items()):
        columns6 = [tuple(tuple(int(x) for x in z) for z in c) for c in hit["columns"]]
        for name, k in POLYS:
            verts, V, edges = build_polytope(k)
            pts = [project_point(combo, columns6) for combo in verts]
            # collapse coincident
            pidx, points, v2p = {}, [], []
            for p in pts:
                kk = col_vkey(p)
                if kk not in pidx:
                    pidx[kk] = len(points)
                    points.append(p)
                v2p.append(pidx[kk])
            edge_list = sorted({(min(v2p[i], v2p[j]), max(v2p[i], v2p[j]))
                                for i, j in edges if v2p[i] != v2p[j]})
            points_num = [[float(c.a) + float(c.b) * PHI for c in p] for p in points]
            best = choose_scale(points, edge_list)
            colordist = {}
            scale_label = None
            if best is not None:
                _cost, scale_label, _s, colors = best
                for c_, _n in colors:
                    colordist[c_] = colordist.get(c_, 0) + 1
            order, status = symmetry_order(points_num)
            rows.append({
                "family_key": key, "polytope": name, "balls": len(points),
                "edges": len(edge_list), "scale": scale_label,
                "colors": colordist, "sym_order": order, "sym_status": status,
            })
            print(f"{name:24s} balls={len(points):2d} edges={len(edge_list):2d} "
                  f"scale={scale_label} colors={colordist} sym={order}")
    (ROOT / "ongoing_work/a5/analysis.json").write_text(json.dumps(rows, indent=2))


def col_vkey(p):
    return tuple((c.a, c.b) for c in p)


if __name__ == "__main__":
    main()
