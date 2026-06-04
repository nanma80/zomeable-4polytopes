from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))

from emit_vzome import (  # noqa: E402
    FOOTER,
    HEADER,
    GF,
    classify_direction,
    classify_strut,
    phi_pow,
    pt_str,
    vkey,
    vscale,
    vsub,
)


ZERO = (GF(0), GF(0), GF(0))


def add(u, v):
    return tuple(u[i] + v[i] for i in range(3))


def gf_from_pair(pair):
    return GF(pair[0], pair[1])


def orthoplex_vertices(n: int):
    vertices = []
    for i in range(n):
        for s in (1, -1):
            vertices.append((i, s))
    return vertices


def orthoplex_edges(vertices):
    edges = []
    for i, (ai, _as) in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            bi, _bs = vertices[j]
            if ai != bi:
                edges.append((i, j))
    return edges


def project_vertex(vertex, columns, scale):
    axis, sign = vertex
    p = tuple(gf_from_pair(x) for x in columns[axis])
    if sign < 0:
        p = vscale(p, GF(-1))
    return vscale(p, scale)


def projected_model(columns, scale, n):
    vertices = orthoplex_vertices(n)
    source_edges = orthoplex_edges(vertices)
    points = []
    point_index = {}
    v_to_p = []
    for v in vertices:
        p = project_vertex(v, columns, scale)
        k = vkey(p)
        if k not in point_index:
            point_index[k] = len(points)
            points.append(p)
        v_to_p.append(point_index[k])

    edge_set = set()
    collapsed = 0
    for i, j in source_edges:
        a, b = v_to_p[i], v_to_p[j]
        if a == b:
            collapsed += 1
        else:
            edge_set.add((min(a, b), max(a, b)))
    return points, sorted(edge_set), collapsed, len(source_edges)


def classify_edge(points, a, b):
    c = classify_strut(points[a], points[b])
    if c is not None:
        return (a, b), c, False
    c = classify_strut(points[b], points[a])
    if c is not None:
        return (b, a), c, False
    half_edge = vscale(vsub(points[b], points[a]), GF(Fraction(1, 2)))
    c = classify_strut(ZERO, half_edge) or classify_strut(half_edge, ZERO)
    if c is not None:
        return (a, b), c, True
    return (a, b), None, False


def audit_scale(columns, scale, n):
    points, edges, collapsed, source_edge_count = projected_model(columns, scale, n)
    oriented = []
    standard_counts = Counter()
    doubled_counts = Counter()
    direction_counts = Counter()
    bad = []
    for a, b in edges:
        d = classify_direction(points[a], points[b]) or classify_direction(points[b], points[a])
        if d is not None:
            direction_counts[d[0]] += 1
        oe, c, doubled = classify_edge(points, a, b)
        if c is None:
            bad.append((a, b, pt_str(vsub(points[b], points[a]))))
            continue
        oriented.append(oe)
        key = f"{c[0]}{c[1]}"
        if doubled:
            doubled_counts[key] += 1
        else:
            standard_counts[key] += 1
    return {
        "points": points,
        "edges": edges,
        "oriented_edges": oriented,
        "collapsed": collapsed,
        "source_edge_count": source_edge_count,
        "standard_counts": standard_counts,
        "doubled_counts": doubled_counts,
        "direction_counts": direction_counts,
        "bad": bad,
    }


def scale_candidates():
    rationals = [
        Fraction(1),
        Fraction(2),
        Fraction(4),
        Fraction(1, 2),
        Fraction(1, 4),
        Fraction(1, 3),
        Fraction(2, 3),
        Fraction(4, 3),
        Fraction(1, 6),
    ]
    for r in rationals:
        for k in range(-4, 10):
            yield f"{r}*phi^{k}", GF(r) * phi_pow(k)


def strut_scale_index(label):
    return int(label[1:])


def scale_score(audit):
    counts = Counter()
    counts.update(audit["standard_counts"])
    counts.update(audit["doubled_counts"])
    indices = [strut_scale_index(k) for k in counts]
    if not indices:
        return (0, 0, 0, 0, 0)
    mn = min(indices)
    mx = max(indices)
    too_short_penalty = max(0, 2 - mn)
    too_long_penalty = max(0, mx - 4)
    return (
        1 if audit["doubled_counts"] else 0,
        too_short_penalty,
        too_long_penalty,
        abs(mn - 2),
        mx,
    )


def choose_scale(columns, n):
    best = None
    for label, scale in scale_candidates():
        audit = audit_scale(columns, scale, n)
        if audit["bad"]:
            continue
        candidate = (scale_score(audit), label, scale, audit)
        if best is None or candidate[0] < best[0]:
            best = candidate
    if best is not None:
        _, label, scale, audit = best
        return label, scale, audit
    label, scale = "1*phi^0", GF(1)
    audit = audit_scale(columns, scale, n)
    return label, scale, audit


def write_vzome(points, edges, out_path):
    cmds = [f'    <ShowPoint point="{pt_str(p)}"/>' for p in points]
    cmds += [
        f'    <JoinPointPair start="{pt_str(points[a])}" end="{pt_str(points[b])}"/>'
        for a, b in edges
    ]
    origin = "0 0 0 0 0 0"
    if not any(pt_str(p) == origin for p in points):
        cmds.append(f'    <SelectManifestation point="{origin}"/>')
        cmds.append("    <Delete/>")
    xml = HEADER
    xml += f'  <EditHistory editNumber="{len(cmds)}" lastStickyEdit="-1">\n'
    xml += "\n".join(cmds) + "\n"
    xml += "  </EditHistory>\n" + FOOTER
    out_path.write_text(xml, encoding="utf-8")


def default_symbol(n: int):
    known = {5: "2_11", 6: "3_11", 7: "4_11", 10: "7_11"}
    return known.get(n, f"{n}_orthoplex")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--symbol", default=None)
    args = ap.parse_args()

    symbol = args.symbol or default_symbol(args.n)
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for idx, (sig, hit) in enumerate(sorted(data["hits"].items(), key=lambda item: (item[1]["N"], item[0])), start=1):
        columns = hit["columns"]
        scale_label, _scale, audit = choose_scale(columns, args.n)
        if audit["bad"]:
            raise SystemExit(f"{sig}: could not postprocess all edges; first bad={audit['bad'][:3]}")
        slug = f"{idx:02d}_{sig}_{len(audit['points'])}_balls"
        out = out_dir / f"{symbol}_{slug}.vZome"
        emit_edges = audit["edges"] if audit["doubled_counts"] else audit["oriented_edges"]
        write_vzome(audit["points"], emit_edges, out)
        manifest.append(
            {
                "signature": sig,
                "file": str(out),
                "polytope": f"{args.n}-orthoplex",
                "gosset_symbol": symbol,
                "balls": len(audit["points"]),
                "visible_edges": len(audit["edges"]),
                "source_edges": audit["source_edge_count"],
                "collapsed_edges": audit["collapsed"],
                "physical_scale": scale_label,
                "standard_struts": dict(sorted(audit["standard_counts"].items())),
                "doubled_standard_struts": dict(sorted(audit["doubled_counts"].items())),
                "direction_counts": dict(sorted(audit["direction_counts"].items())),
            }
        )
        print(
            sig,
            "->",
            out,
            "scale",
            scale_label,
            "standard",
            dict(audit["standard_counts"]),
            "doubled",
            dict(audit["doubled_counts"]),
        )

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {len(manifest)} files under {out_dir}")


if __name__ == "__main__":
    main()
