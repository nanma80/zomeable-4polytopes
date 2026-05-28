"""Build the published A5-family gallery from the sweep hits.

For every (shape, polytope) pair this:
  1. projects the polytope with the sweep's exact Z[phi] columns (c_0 = 0);
  2. collapses coincident vertices into balls;
  3. centers the ball cloud on its centroid (exact golden-field arithmetic);
  4. chooses a scale s = (num/den) * phi^n -- preferring a pure power of phi --
     that turns as many edges as possible into standard vZome struts (a strut
     length phi^m or exactly double one, matched per color orbit);
  5. writes a vZome file with the centered+scaled balls, the edges, an explicit
     delete of the auto-created origin ball (since the centroid is generally not
     a ball), and a <Viewing> block fitted to the model bounds.

The directions of every edge are genuine zome axes (verified BAD == 0 by the
sweep/emit), so all nine models are strict-orthographic zome-direction
projections; the per-color strut multiples are recorded in the manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

from emit_vzome import (  # noqa: E402
    GF,
    HEADER,
    FOOTER,
    classify_direction,
    classify_strut,
    phi_pow,
    pt_str,
    vkey,
    vsub,
)

spec = importlib.util.spec_from_file_location(
    "col", ROOT / "tools" / "gosset" / "zphi_column_sweep.py"
)
col = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(col)

PHI = (1 + 5 ** 0.5) / 2
POLYS = (("5_simplex", 1), ("rectified_5_simplex", 2), ("birectified_5_simplex", 3))
HALF = GF(Fraction(1, 2), 0)


def build_polytope(k: int):
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
    return verts, edges


def gf_pair(pair):
    return GF(Fraction(pair[0]), Fraction(pair[1]))


def project_point(combo, columns6):
    coords = [GF(0), GF(0), GF(0)]
    for idx in combo:
        c = columns6[idx]
        for r in range(3):
            coords[r] = coords[r] + gf_pair(c[r])
    return tuple(coords)


def collapse(verts, edges, columns6):
    """Return (points, edge_list) with coincident vertices merged."""
    pidx, points, v2p = {}, [], []
    for combo in verts:
        p = project_point(combo, columns6)
        kk = vkey(p)
        if kk not in pidx:
            pidx[kk] = len(points)
            points.append(p)
        v2p.append(pidx[kk])
    edge_list = sorted(
        {(min(v2p[i], v2p[j]), max(v2p[i], v2p[j])) for i, j in edges if v2p[i] != v2p[j]}
    )
    return points, edge_list


def centroid(points):
    n = len(points)
    acc = [GF(0), GF(0), GF(0)]
    for p in points:
        for r in range(3):
            acc[r] = acc[r] + p[r]
    inv = GF(Fraction(1, n), 0)
    return tuple(acc[r] * inv for r in range(3))


def recenter(points):
    c = centroid(points)
    return [tuple(p[r] - c[r] for r in range(3)) for p in points]


def scale_points(points, s: GF):
    return [tuple(p[r] * s for r in range(3)) for p in points]


def candidate_scales():
    out, seen = [], set()
    for n in range(-6, 9):
        base = phi_pow(n)
        for den in (1, 2, 3, 4, 5, 6):
            for num in range(1, 13):
                f = Fraction(num, den)
                s = GF(f * base.a, f * base.b)
                key = (s.a, s.b)
                if key in seen:
                    continue
                seen.add(key)
                out.append((num, den, n, s))
    return out


def classify_edge(vec, s: GF):
    """Classify scaled edge as standard (mult 1) or double (mult 2) strut."""
    scaled = tuple(x * s for x in vec)
    c = classify_strut((GF(0), GF(0), GF(0)), scaled)
    if c is not None:
        return (c[0], c[1], 1)
    half = tuple(x * HALF for x in scaled)
    c = classify_strut((GF(0), GF(0), GF(0)), half)
    if c is not None:
        return (c[0], c[1], 2)
    return None


def choose_scale(points, edge_list):
    raw_vecs = [vsub(points[b], points[a]) for a, b in edge_list]
    best = None
    for num, den, n, s in candidate_scales():
        classes = [classify_edge(v, s) for v in raw_vecs]
        n_std = sum(1 for c in classes if c is not None and c[2] == 1)
        n_dbl = sum(1 for c in classes if c is not None and c[2] == 2)
        n_hit = n_std + n_dbl
        powers = [c[1] for c in classes if c is not None]
        spread = (max(powers) - min(powers)) if powers else 99
        # Prefer: more standard/double matches; then all single (no doubles);
        # then a pure power of phi (den == 1); then tight power spread; then
        # small coefficients.
        cost = (
            -n_hit,
            n_dbl,
            0 if den == 1 else 1,
            spread,
            den,
            abs(n),
            num,
        )
        if best is None or cost < best[0]:
            best = (cost, num, den, n, s, classes, n_std, n_dbl)
    return best


def scale_label(num, den, n):
    base = "phi" if n == 1 else (f"phi^{n}" if n != 0 else "1")
    if n == 0:
        core = "1"
    else:
        core = base
    if num == 1 and den == 1:
        return core if n != 0 else "1"
    if den == 1:
        return f"{num}*{core}" if n != 0 else f"{num}"
    if num == 1:
        return f"{core}/{den}" if n != 0 else f"1/{den}"
    return f"{num}*{core}/{den}" if n != 0 else f"{num}/{den}"


def view_block(points_num):
    mins = [min(p[i] for p in points_num) for i in range(3)]
    maxs = [max(p[i] for p in points_num) for i in range(3)]
    center = [(mins[i] + maxs[i]) / 2 for i in range(3)]
    radius = max(
        math.sqrt(sum((p[i] - center[i]) ** 2 for i in range(3))) for p in points_num
    )
    # Gosset-proportional framing: camera ~8x the bounding-sphere radius back,
    # so the model sits comfortably small in the initial view (not cramped).
    width = max(1.0, 8.0 * radius)
    distance = width
    near = max(0.1, distance / 100.0)
    far = 4.0 * distance
    return (
        "  <Viewing>\n"
        f'    <ViewModel distance="{distance:.6f}" far="{far:.6f}" near="{near:.6f}" '
        f'parallel="false" stereoAngle="0.0" width="{width:.6f}">\n'
        f'      <LookAtPoint x="{center[0]:.6f}" y="{center[1]:.6f}" z="{center[2]:.6f}"/>\n'
        '      <UpDirection x="0.0" y="1.0" z="0.0"/>\n'
        '      <LookDirection x="0.0" y="0.0" z="-1.0"/>\n'
        "    </ViewModel>\n"
        "  </Viewing>\n"
    )


# FOOTER without its built-in static <Viewing> block, so we can inject a fitted one.
def footer_with_view(view: str) -> str:
    import re

    return re.sub(r"\s*<Viewing>.*?</Viewing>\n", "\n" + view, FOOTER, count=1, flags=16)


def to_num(points):
    return [[float(c.a) + float(c.b) * PHI for c in p] for p in points]


def emit(points, edge_list, classes, out_path):
    points_num = to_num(points)
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
    xml += "  </EditHistory>\n"
    xml += footer_with_view(view_block(points_num))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(xml, encoding="utf-8")


def symmetry_order(points_num):
    P = np.asarray(points_num, dtype=float)
    P = P - P.mean(axis=0)
    norms = np.linalg.norm(P, axis=1)
    idx = [i for i in np.argsort(-norms) if norms[i] > 1e-6]
    if len(idx) < 3:
        return 0
    keyset = {tuple(np.round(p, 6)) for p in P}
    a0 = P[idx[0]]
    a1 = next((P[i] for i in idx[1:] if np.linalg.norm(np.cross(a0, P[i])) > 1e-6), None)
    if a1 is None:
        return 0
    a2 = next(
        (P[i] for i in idx[1:] if abs(np.linalg.det(np.array([a0, a1, P[i]]))) > 1e-6),
        None,
    )
    if a2 is None:
        return 0
    A = np.array([a0, a1, a2]).T
    gram_a = A.T @ A
    Ainv = np.linalg.inv(A)
    count = 0
    for j0 in idx:
        if abs(norms[j0] - np.linalg.norm(a0)) > 1e-6:
            continue
        for j1 in idx:
            b0, b1 = P[j0], P[j1]
            if abs(b0 @ b1 - a0 @ a1) > 1e-6 or abs(norms[j1] - np.linalg.norm(a1)) > 1e-6:
                continue
            for j2 in idx:
                B = np.array([b0, b1, P[j2]]).T
                if np.max(np.abs(B.T @ B - gram_a)) > 1e-6:
                    continue
                R = B @ Ainv
                if np.max(np.abs(R @ R.T - np.eye(3))) > 1e-6:
                    continue
                if all(tuple(np.round(R @ p, 6)) in keyset for p in P):
                    count += 1
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="ongoing_work/a5/column_sweep_a5_R3.json")
    ap.add_argument("--out_dir", default="output/a5_projections")
    ap.add_argument(
        "--extra_phi_power",
        type=int,
        default=2,
        help="multiply every chosen scale by phi^k (default 2) to enlarge models",
    )
    args = ap.parse_args()

    data = json.loads((ROOT / args.json).read_text())
    out_root = ROOT / args.out_dir
    manifest = []
    scale_items = []

    for key, hit in sorted(data["hits"].items()):
        columns6 = [tuple(tuple(int(x) for x in z) for z in c) for c in hit["columns"]]
        khash = hashlib.sha1(key.encode()).hexdigest()[:6]
        for name, k in POLYS:
            verts, edges = build_polytope(k)
            points, edge_list = collapse(verts, edges, columns6)
            best = choose_scale(points, edge_list)
            _cost, num, den, n, s, classes, n_std, n_dbl = best

            # Enlarge by an extra power of phi (shifts every strut power
            # uniformly, so standard/double classification is preserved).
            k = args.extra_phi_power
            if k:
                n += k
                s = s * phi_pow(k)

            centered = recenter(points)
            scaled = scale_points(centered, s)

            sym = symmetry_order(to_num(scaled))
            fname = f"{name}_sym{sym}_{len(points)}balls_{khash}.vZome"
            sub = name
            out_path = out_root / sub / fname
            emit(scaled, edge_list, classes, out_path)

            # direction audit on final coords (sanity)
            bad = 0
            color_dirs = {}
            for a, b in edge_list:
                cd = classify_direction(scaled[a], scaled[b])
                if cd is None or cd[0] == "_":
                    bad += 1
                else:
                    color_dirs[cd[0]] = color_dirs.get(cd[0], 0) + 1
            strut_colors = {}
            non_standard = 0
            for c in classes:
                if c is None:
                    non_standard += 1
                else:
                    tag = f"{c[0]}{'(x2)' if c[2] == 2 else ''}"
                    strut_colors[tag] = strut_colors.get(tag, 0) + 1

            rel = str(out_path.relative_to(out_root)).replace("\\", "/")
            row = {
                "file": rel,
                "family_key": key,
                "polytope": name,
                "balls": len(points),
                "edges": len(edge_list),
                "symmetry_order": sym,
                "scale": scale_label(num, den, n),
                "zphi_pair": [
                    str(s.a) if s.a.denominator == 1 else f"{s.a.numerator}/{s.a.denominator}",
                    str(s.b) if s.b.denominator == 1 else f"{s.b.numerator}/{s.b.denominator}",
                ],
                "strut_colors": strut_colors,
                "direction_colors": color_dirs,
                "edges_standard": n_std,
                "edges_double": n_dbl,
                "edges_direction_only": non_standard,
                "bad_directions": bad,
                "fully_buildable": non_standard == 0,
            }
            manifest.append(row)
            scale_items.append(
                {
                    "file": rel,
                    "scale_factor": scale_label(num, den, n),
                    "zphi_pair": row["zphi_pair"],
                    "strut_colors": strut_colors,
                    "fully_buildable": non_standard == 0,
                }
            )
            print(
                f"{name:24s} {khash} balls={len(points):2d} edges={len(edge_list):2d} "
                f"sym={sym:2d} scale={row['scale']:<12s} struts={strut_colors} "
                f"dir_only={non_standard} BAD={bad}"
            )

    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out_root / "physical_scale_factors_a5.json").write_text(
        json.dumps(
            {
                "note": "Scales chosen so each edge becomes a standard vZome phi-power "
                "strut length (or exactly double one), matched per color orbit. "
                "Models are centered on the ball centroid; the auto-created origin "
                "ball is deleted. Pure powers of phi are preferred where possible.",
                "items": scale_items,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    ok = sum(1 for m in manifest if m["fully_buildable"])
    print(f"\n{len(manifest)} models written, {ok} fully standard-strut buildable")
    print(f"Wrote {out_root}")


if __name__ == "__main__":
    main()
