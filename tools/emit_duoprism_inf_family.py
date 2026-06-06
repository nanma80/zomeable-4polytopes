"""Emit constructive infinite-family examples for {4}x{6} and {4}x{10}.

These are exact Z[phi]^3 constructions of the inf families documented
in output/duoprisms/duoprism_4_6/RESULTS.md and
output/duoprisms/duoprism_4_10/RESULTS.md.
"""
from __future__ import annotations

import math
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from emit_vzome import (  # noqa: E402
    BLUE_DIRS,
    GREEN_DIRS,
    RED_DIRS,
    YELLOW_DIRS,
    GF,
    classify_direction,
    cross,
    emit_vzome_directional,
    gf_str,
    vkey,
)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_46 = os.path.join(ROOT, "output", "duoprisms", "duoprism_4_6")
OUT_410 = os.path.join(ROOT, "output", "duoprisms", "duoprism_4_10")

ZERO = (GF(0), GF(0), GF(0))
PHI_F = (1.0 + 5.0 ** 0.5) / 2.0


def _gf_inv(x: GF) -> GF:
    a, b = x.a, x.b
    denom = a * a + a * b - b * b
    if denom == 0:
        raise ZeroDivisionError(x)
    return GF(Fraction(a + b, denom), Fraction(-b, denom))


def _gf_float(x: GF) -> float:
    return float(x.a) + float(x.b) * PHI_F


def _vec_float(v):
    return [_gf_float(x) for x in v]


def _dot_float(u, v) -> float:
    fu = _vec_float(u)
    fv = _vec_float(v)
    return sum(a * b for a, b in zip(fu, fv))


def _add(u, v):
    return tuple(a + b for a, b in zip(u, v))


def _sub(u, v):
    return tuple(a - b for a, b in zip(u, v))


def _scale(k: GF, v):
    return tuple(k * x for x in v)


def _neg(v):
    return tuple(-x for x in v)


def _dedup_balls(balls):
    uniq = []
    idx = []
    by_key = {}
    for p in balls:
        k = vkey(p)
        if k not in by_key:
            by_key[k] = len(uniq)
            uniq.append(p)
        idx.append(by_key[k])
    return uniq, idx


def _emit_grid(balls, edges, path):
    uniq, idx = _dedup_balls(balls)
    edge_set = set()
    for i, j in edges:
        a, b = idx[i], idx[j]
        if a != b:
            edge_set.add((min(a, b), max(a, b)))
    edges3 = sorted(edge_set)
    for i, j in edges3:
        if classify_direction(uniq[i], uniq[j]) is None:
            raise RuntimeError(f"{os.path.basename(path)}: non-zome edge {i}-{j}")
    counts = emit_vzome_directional(uniq, edges3, path)
    print(f"{os.path.relpath(path, ROOT)}: {len(uniq)} balls, {len(edges3)} struts, {counts}")


def _set_view(path: str, distance: float, far: float, width: float):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    old = '<ViewModel distance="50.0" far="200.0" near="0.5" parallel="false" stereoAngle="0.0" width="50.0">'
    new = (
        f'<ViewModel distance="{distance:.1f}" far="{far:.1f}" near="0.5" '
        f'parallel="false" stereoAngle="0.0" width="{width:.1f}">'
    )
    text = text.replace(old, new)
    text = text.replace(
        '<UpDirection x="0.0" y="1.0" z="0.0"/>\n'
        '      <LookDirection x="0.0" y="0.0" z="-1.0"/>',
        '<UpDirection x="-0.202" y="0.923" z="-0.280"/>\n'
        '      <LookDirection x="-0.550" y="-0.350" z="-0.760"/>',
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _duoprism_edges(p: int, q: int):
    edges = []
    for i in range(p):
        for j in range(q):
            edges.append((i * q + j, ((i + 1) % p) * q + j))
            edges.append((i * q + j, i * q + ((j + 1) % q)))
    return edges


def _emit_4x6(a: GF, b: GF, q: GF, suffix: str):
    """Emit {4}x{6} with q^2 = 3*(a^2+b^2)."""
    if q * q != GF(3) * (a * a + b * b):
        raise ValueError("expected q^2 = 3*(a^2+b^2)")

    # Two blue axes at 60 degrees, with a perpendicular yellow axis.
    p0 = (GF(2, 2), GF(0), GF(0))
    p1 = (GF(1, 1), GF(1, 2), GF(0, 1))
    height_axis = (GF(0), GF(0, -1), GF(1, 2))
    hexagon = [p0, p1, _sub(p1, p0), _neg(p0), _neg(p1), _sub(p0, p1)]

    # Normalize by 1/q so the preserved hexagon edge is one blue axis long.
    norm = _gf_inv(q)
    polygon = [_scale(norm * q, p) for p in hexagon]
    heights = [-b, a, b, -a]
    balls = [
        _add(poly, _scale(norm * GF(2) * h, height_axis))
        for h in heights
        for poly in polygon
    ]
    fname = f"duoprism_4_6_inf_family_{suffix}.vZome"
    _emit_grid(balls, _duoprism_edges(4, 6), os.path.join(OUT_46, fname))


def _green_hexagon_frame():
    """Return a regular green-axis hexagon with a perpendicular yellow axis."""
    for p0 in GREEN_DIRS:
        for p1 in GREEN_DIRS:
            if p0 == p1:
                continue
            if abs(_dot_float(p0, p1) - 0.5 * _dot_float(p0, p0)) > 1e-8:
                continue
            if abs(_dot_float(p0, p0) - _dot_float(p1, p1)) > 1e-8:
                continue
            p2 = _sub(p1, p0)
            p2_class = classify_direction(ZERO, p2)
            if p2_class is None or p2_class[0] != 'G':
                continue
            for height_axis in YELLOW_DIRS:
                if vkey(cross(p0, height_axis)) == vkey(ZERO):
                    continue
                if abs(_dot_float(p0, height_axis)) < 1e-8 and abs(_dot_float(p1, height_axis)) < 1e-8:
                    return [p0, p1, p2, _neg(p0), _neg(p1), _neg(p2)], height_axis
    raise RuntimeError("could not find green hexagon frame")


def _emit_4x6_green(a: GF, b: GF, q: GF, suffix: str, integer_scale: GF = GF(1), view=(50.0, 200.0, 50.0)):
    """Emit {4}x{6} green/yellow subfamily with 2*q^2 = 3*(a^2+b^2)."""
    if GF(2) * q * q != GF(3) * (a * a + b * b):
        raise ValueError("expected 2*q^2 = 3*(a^2+b^2)")

    hexagon, height_axis = _green_hexagon_frame()
    norm = _gf_inv(q)
    polygon = [_scale(norm * q, p) for p in hexagon]
    heights = [-b, a, b, -a]
    balls = [
        _scale(integer_scale, _add(poly, _scale(norm * GF(2) * h, height_axis)))
        for h in heights
        for poly in polygon
    ]
    fname = f"duoprism_4_6_inf_family_GY_{suffix}.vZome"
    path = os.path.join(OUT_46, fname)
    _emit_grid(balls, _duoprism_edges(4, 6), path)
    _set_view(path, *view)


def _decagon_blue_frame():
    """Return a regular decagon edge cycle in a blue-axis plane with red normal."""
    best = None
    for normal in RED_DIRS:
        dirs = []
        for d in BLUE_DIRS:
            if abs(_dot_float(normal, d)) < 1e-8:
                dirs.append(d)
                dirs.append(_neg(d))
        uniq = []
        seen = set()
        for d in dirs:
            k = vkey(d)
            if k not in seen:
                seen.add(k)
                uniq.append(d)
        if len(uniq) >= 10:
            best = (normal, uniq)
            break
    if best is None:
        raise RuntimeError("could not find blue decagon frame")

    normal, dirs = best
    ex = _vec_float(dirs[0])
    ex_len = math.sqrt(sum(x * x for x in ex))
    ex = [x / ex_len for x in ex]
    nw = _vec_float(normal)
    nw_len = math.sqrt(sum(x * x for x in nw))
    nw = [x / nw_len for x in nw]
    ey = [
        nw[1] * ex[2] - nw[2] * ex[1],
        nw[2] * ex[0] - nw[0] * ex[2],
        nw[0] * ex[1] - nw[1] * ex[0],
    ]
    ordered = []
    for d in dirs:
        fd = _vec_float(d)
        x = sum(fd[i] * ex[i] for i in range(3))
        y = sum(fd[i] * ey[i] for i in range(3))
        ordered.append((math.atan2(y, x), d))
    edges = [d for _, d in sorted(ordered)[:10]]

    vertices = []
    cur = ZERO
    for e in edges:
        vertices.append(cur)
        cur = _add(cur, e)
    if vkey(cur) != vkey(ZERO):
        raise RuntimeError("decagon edge cycle did not close")
    inv10 = GF(Fraction(1, 10), 0)
    center = tuple(sum(v[i] for v in vertices) * inv10 for i in range(3))
    return normal, [_sub(v, center) for v in vertices]


def _emit_4x10(a: GF, b: GF, c: GF, suffix: str):
    """Emit {4}x{10} with c^2 = a^2+b^2."""
    if c * c != a * a + b * b:
        raise ValueError("expected c^2 = a^2+b^2")

    height_axis, decagon = _decagon_blue_frame()
    norm = _gf_inv(c)
    beta = GF(Fraction(4, 5), Fraction(2, 5))  # 2*phi/sqrt(5)
    polygon = [_scale(norm * c, p) for p in decagon]
    heights = [-b, a, b, -a]
    balls = [
        _add(poly, _scale(norm * beta * h, height_axis))
        for h in heights
        for poly in polygon
    ]
    fname = f"duoprism_4_10_inf_family_{suffix}.vZome"
    _emit_grid(balls, _duoprism_edges(4, 10), os.path.join(OUT_410, fname))


def main():
    os.makedirs(OUT_46, exist_ok=True)
    os.makedirs(OUT_410, exist_ok=True)

    _emit_4x6(GF(2, -1), GF(-1, 3), GF(-3, 6), "a2-phi_b3phi-1")
    _emit_4x6_green(GF(-1, 2), GF(1), GF(3), "a2phi-1_b1", GF(3), (110.0, 220.0, 110.0))
    _emit_4x6_green(GF(2, 3), GF(4, 1), GF(6, 3), "a2+3phi_b4+phi", GF(-45, 30), (125.0, 240.0, 125.0))
    _emit_4x10(GF(5), GF(12), GF(13), "a5_b12")
    _emit_4x10(GF(8), GF(15), GF(17), "a8_b15")


if __name__ == "__main__":
    main()
