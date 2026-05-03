"""Emit two .vZome files for the 24-cell -> 3D projections that land
entirely on default-color zometool struts.

Family A (short-root, e.g. n = e_4):
    project (a,b,c,d) -> (a,b,c)
    96 edges -> 6 blue + 6 green directions, no collapse.
    18 distinct 3D balls.
    Coords scaled by phi^2 = 2+2*phi so each strut is a standard B0/G0 part.

Family B (long-root, n = (1,-1,0,0)/sqrt(2)):
    project (a,b,c,d) -> (a+b, c+d, d-c)   (already includes rotation + sqrt(2) rescale)
    96 edges -> 88 surviving + 8 collapsed; survivors are
    +-2*e_i (blue, B-scale -2) and (+-1,+-1,+-1) (yellow, Y-scale -2).
    15 distinct 3D balls.

Both outputs are validated edge-by-edge against the icosahedral-system
standard strut lookup before being written.
"""

import os
from fractions import Fraction
from itertools import product
from pathlib import Path

# ---------------------------------------------------------------------------
# Golden-field arithmetic (a + b * phi, phi^2 = phi + 1)
# ---------------------------------------------------------------------------

class GF:
    __slots__ = ('a', 'b')
    def __init__(self, a, b=0):
        self.a = a if isinstance(a, Fraction) else Fraction(a)
        self.b = b if isinstance(b, Fraction) else Fraction(b)
    def __add__(s, o):
        if isinstance(o, GF): return GF(s.a + o.a, s.b + o.b)
        return GF(s.a + o, s.b)
    def __sub__(s, o):
        if isinstance(o, GF): return GF(s.a - o.a, s.b - o.b)
        return GF(s.a - o, s.b)
    def __neg__(s): return GF(-s.a, -s.b)
    def __mul__(s, o):
        if not isinstance(o, GF): o = GF(o)
        return GF(s.a*o.a + s.b*o.b,
                  s.a*o.b + s.b*o.a + s.b*o.b)
    __radd__ = __add__
    __rmul__ = __mul__
    def __eq__(s, o):
        if isinstance(o, GF): return s.a == o.a and s.b == o.b
        return s.a == o and s.b == 0
    def __hash__(s): return hash((s.a, s.b))

PHI  = GF(0, 1)
ONE  = GF(1, 0)
ZERO = GF(0, 0)

def phi_pow(n):
    g = ONE
    if n >= 0:
        for _ in range(n): g = g * PHI
    else:
        inv = GF(-1, 1)              # phi^-1 = phi - 1
        for _ in range(-n): g = g * inv
    return g

def V(x, y, z):
    return (x if isinstance(x, GF) else GF(x),
            y if isinstance(y, GF) else GF(y),
            z if isinstance(z, GF) else GF(z))

def vadd(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def vsub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def vscale(a, s): return (a[0]*s, a[1]*s, a[2]*s)
def vkey(a):
    return ((a[0].a, a[0].b), (a[1].a, a[1].b), (a[2].a, a[2].b))

# ---------------------------------------------------------------------------
# Icosahedral rotation group, 60 elements
# ---------------------------------------------------------------------------

def mvmul(M, v):
    return (M[0][0]*v[0] + M[0][1]*v[1] + M[0][2]*v[2],
            M[1][0]*v[0] + M[1][1]*v[1] + M[1][2]*v[2],
            M[2][0]*v[0] + M[2][1]*v[1] + M[2][2]*v[2])

def mmmul(A, B):
    return tuple(
        tuple(sum((A[i][k]*B[k][j] for k in range(3)), GF(0))
              for j in range(3))
        for i in range(3))

def m_id():
    return ((GF(1),GF(0),GF(0)), (GF(0),GF(1),GF(0)), (GF(0),GF(0),GF(1)))

def mkey(M):
    return tuple((c.a, c.b) for row in M for c in row)

half_g   = GF(Fraction(1,2), 0)
neg_half = GF(Fraction(-1,2), 0)
phi_h    = GF(0, Fraction(1,2))
phim1_h  = GF(Fraction(-1,2), Fraction(1,2))

g5 = ((half_g,  -phi_h,   phim1_h),
      (phi_h,    phim1_h, neg_half),
      (phim1_h,  half_g,  phi_h))
g3 = ((GF(0), GF(1), GF(0)),
      (GF(0), GF(0), GF(1)),
      (GF(1), GF(0), GF(0)))
g2 = ((GF(1), GF(0),  GF(0)),
      (GF(0), GF(-1), GF(0)),
      (GF(0), GF(0),  GF(-1)))

def gen_group(gens):
    seen = {mkey(m_id()): m_id()}
    frontier = [m_id()]
    while frontier:
        nxt = []
        for M in frontier:
            for g in gens:
                M2 = mmmul(g, M)
                k = mkey(M2)
                if k not in seen:
                    seen[k] = M2
                    nxt.append(M2)
        frontier = nxt
    return list(seen.values())

GROUP = gen_group([g2, g3, g5])
assert len(GROUP) == 60

# ---------------------------------------------------------------------------
# Color orbits and standard-strut lookup
# ---------------------------------------------------------------------------

B0_proto = V(GF(2,2), 0,        0)
Y0_proto = V(GF(1,1), GF(1,1),  GF(1,1))
R0_proto = V(0,       GF(1,2),  GF(1,1))
G0_proto = V(GF(2,2), GF(2,2),  0)

def orbit(v):
    seen = {}
    for M in GROUP:
        u = mvmul(M, v)
        seen[vkey(u)] = u
    return list(seen.values())

BLUE_DIRS   = orbit(B0_proto);   assert len(BLUE_DIRS)   == 30
YELLOW_DIRS = orbit(Y0_proto);   assert len(YELLOW_DIRS) == 20
RED_DIRS    = orbit(R0_proto);   assert len(RED_DIRS)    == 12
GREEN_DIRS  = orbit(G0_proto);   assert len(GREEN_DIRS)  == 60

def scaled_orbit(dirs, n):
    fac = phi_pow(n)
    return [vscale(v, fac) for v in dirs]

STRUT_LOOKUP = {}
for color, dirs in [('B', BLUE_DIRS), ('Y', YELLOW_DIRS),
                    ('R', RED_DIRS), ('G', GREEN_DIRS)]:
    for n in range(-3, 7):
        for v in scaled_orbit(dirs, n):
            STRUT_LOOKUP[vkey(v)] = (color, n)

def classify_strut(start, end):
    return STRUT_LOOKUP.get(vkey(vsub(end, start)))

# Direction-only classifier: returns (color, parallel_unit_dir) if edge is
# parallel to any default unsigned axis (any positive GF scaling), else None.
# Exact length doesn't need to match any conventional strut.
COLOR_DIRS = [('B', BLUE_DIRS), ('Y', YELLOW_DIRS),
              ('R', RED_DIRS),  ('G', GREEN_DIRS)]

def cross(u, v):
    return (u[1]*v[2] - u[2]*v[1],
            u[2]*v[0] - u[0]*v[2],
            u[0]*v[1] - u[1]*v[0])

ZEROV = (GF(0), GF(0), GF(0))

def classify_direction(start, end):
    e = vsub(end, start)
    if vkey(e) == vkey(ZEROV): return ('_', None)
    for color, dirs in COLOR_DIRS:
        for d in dirs:
            if vkey(cross(e, d)) == vkey(ZEROV):
                return (color, d)
    return None

# ---------------------------------------------------------------------------
# XML emission
# ---------------------------------------------------------------------------

def gf_str(g):
    def fmt(x):
        x = x if isinstance(x, Fraction) else Fraction(x)
        return str(x.numerator) if x.denominator == 1 \
               else f"{x.numerator}/{x.denominator}"
    return f"{fmt(g.a)} {fmt(g.b)}"

def pt_str(v):
    return f"{gf_str(v[0])} {gf_str(v[1])} {gf_str(v[2])}"

HEADER = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<vzome:vZome xmlns:vzome="http://xml.vzome.com/vZome/4.0.0/" buildNumber="111" coreVersion="7.0" field="golden" version="7.1">
'''

FOOTER = '''  <notes/>
  <sceneModel ambientLight="41,41,41" background="175,200,220">
    <directionalLight color="235,235,228" x="1.0" y="-1.0" z="-1.0"/>
    <directionalLight color="228,228,235" x="-1.0" y="0.0" z="0.0"/>
    <directionalLight color="30,30,30" x="0.0" y="0.0" z="-1.0"/>
  </sceneModel>
  <Viewing>
    <ViewModel distance="50.0" far="200.0" near="0.5" parallel="false" stereoAngle="0.0" width="50.0">
      <LookAtPoint x="0.0" y="0.0" z="0.0"/>
      <UpDirection x="0.0" y="1.0" z="0.0"/>
      <LookDirection x="0.0" y="0.0" z="-1.0"/>
    </ViewModel>
  </Viewing>
  <SymmetrySystem name="icosahedral" renderingStyle="solid connectors">
    <Direction color="0,142,194"  name="blue"   orbit="[[0,0,1],[0,0,1]]"/>
    <Direction color="0,153,63"   name="green"  orbit="[[2,-1,1],[5,-3,1]]"/>
    <Direction color="217,18,24"  name="red"    orbit="[[-1,1,1],[0,0,1]]"/>
    <Direction color="255,179,26" name="yellow" orbit="[[0,0,1],[2,-1,1]]"/>
  </SymmetrySystem>
  <OtherSymmetries/>
  <Tools/>
</vzome:vZome>
'''

def emit_vzome(verts, edges, path):
    audit = []
    for (i, j) in edges:
        c = classify_strut(verts[i], verts[j])
        if c is None:
            raise ValueError(
                f"Non-standard strut {i}->{j}: "
                f"{pt_str(verts[i])}  ->  {pt_str(verts[j])}")
        audit.append(c)

    cmds  = [f'    <ShowPoint point="{pt_str(v)}"/>' for v in verts]
    cmds += [f'    <JoinPointPair start="{pt_str(verts[i])}" '
             f'end="{pt_str(verts[j])}"/>' for (i, j) in edges]

    # vZome auto-creates an origin ball on document load. If no emitted
    # vertex is at the origin, delete it so users don't have to do so manually.
    origin_str = "0 0 0 0 0 0"
    if not any(pt_str(v) == origin_str for v in verts):
        cmds.append(f'    <SelectManifestation point="{origin_str}"/>')
        cmds.append('    <Delete/>')

    xml  = HEADER
    xml += f'  <EditHistory editNumber="{len(cmds)}" lastStickyEdit="-1">\n'
    xml += '\n'.join(cmds) + '\n'
    xml += '  </EditHistory>\n' + FOOTER
    Path(path).write_text(xml, encoding='utf-8')

    counts = {}
    for c, n in audit:
        counts[(c, n)] = counts.get((c, n), 0) + 1
    return counts

def emit_vzome_directional(verts, edges, path):
    """Like emit_vzome but only checks that each edge is parallel to a
    default-color axis; exact strut length need not match B0/B1/etc."""
    audit = []
    for (i, j) in edges:
        c = classify_direction(verts[i], verts[j])
        if c is None:
            raise ValueError(
                f"Edge {i}->{j} not parallel to any default axis: "
                f"{pt_str(verts[i])}  ->  {pt_str(verts[j])}")
        audit.append(c[0])

    cmds  = [f'    <ShowPoint point="{pt_str(v)}"/>' for v in verts]
    cmds += [f'    <JoinPointPair start="{pt_str(verts[i])}" '
             f'end="{pt_str(verts[j])}"/>' for (i, j) in edges]

    # vZome auto-creates an origin ball on document load. If no emitted
    # vertex is at the origin, delete it so users don't have to do so manually.
    origin_str = "0 0 0 0 0 0"
    if not any(pt_str(v) == origin_str for v in verts):
        cmds.append(f'    <SelectManifestation point="{origin_str}"/>')
        cmds.append('    <Delete/>')

    xml  = HEADER
    xml += f'  <EditHistory editNumber="{len(cmds)}" lastStickyEdit="-1">\n'
    xml += '\n'.join(cmds) + '\n'
    xml += '  </EditHistory>\n' + FOOTER
    Path(path).write_text(xml, encoding='utf-8')

    counts = {}
    for c in audit: counts[c] = counts.get(c, 0) + 1
    return counts

# ---------------------------------------------------------------------------
# 24-cell vertices and edges (D_4 representation)
# ---------------------------------------------------------------------------

def v_d4_24cell():
    verts = []
    for i in range(4):
        for j in range(i+1, 4):
            for si in (1, -1):
                for sj in (1, -1):
                    v = [0, 0, 0, 0]
                    v[i] = si; v[j] = sj
                    verts.append(tuple(v))
    assert len(verts) == 24
    return verts

def edges_24cell(verts):
    edges = []
    n = len(verts)
    for i in range(n):
        for j in range(i+1, n):
            d = tuple(verts[i][k] - verts[j][k] for k in range(4))
            if sum(x*x for x in d) == 2:
                edges.append((i, j))
    assert len(edges) == 96
    return edges

# ---------------------------------------------------------------------------
# Projection helpers + ball/edge dedup in 3D (golden field)
# ---------------------------------------------------------------------------

def project_short_root(p):
    # drop x4; scale by phi^2 = 2 + 2*phi to land on B0/G0 prototypes
    s = GF(2, 2)
    return (GF(p[0]) * s, GF(p[1]) * s, GF(p[2]) * s)

def project_long_root(p):
    # (a,b,c,d) -> (a+b, c+d, d-c); raw map gives B(-2)/Y(-2).
    # Scale by phi^4 so struts land on B2/Y2 (long enough for physical builds).
    a, b, c, d = p
    s = phi_pow(4)
    return (GF(a + b) * s, GF(c + d) * s, GF(d - c) * s)

# ---------------------------------------------------------------------------
# Short-root 24-cell + triality projection (mode 'a': Hamilton left-mult by
# q = (0, 1, phi, phi^2), drop k-component).
# ---------------------------------------------------------------------------

def v_short_root_24cell():
    """Short-root 24-cell: 8 axis vertices + 16 half-integer vertices."""
    verts = []
    # 8 axis vertices: +- e_i  (scale by 2 to keep half-integers integral)
    for i in range(4):
        for s in (1, -1):
            v = [0, 0, 0, 0]
            v[i] = s * 2
            verts.append(tuple(v))
    # 16 half-integer vertices: (+-1, +-1, +-1, +-1)
    for sx in product((1, -1), repeat=4):
        verts.append(sx)
    assert len(verts) == 24
    return verts

def edges_short_root_24cell(verts):
    """Edges of short-root 24-cell: pairs at squared-distance 4 in this
    integer-doubled coordinate system (i.e. true distance 2 ⇒ doubled = 4
    for axis-axis,  3+1=4 for axis-half pairs, 4 for half-half pairs)."""
    edges = []
    n = len(verts)
    for i in range(n):
        for j in range(i+1, n):
            d2 = sum((verts[i][k]-verts[j][k])**2 for k in range(4))
            if d2 == 4:
                edges.append((i, j))
    assert len(edges) == 96, f"expected 96, got {len(edges)}"
    return edges

def project_triality(p):
    """Orthographic projection of the 24-cell along the triality direction.

    Equivalent to right-multiplying the source quaternion by
    q = (0, 1, phi, phi^2) and dropping the real component.

    Hamilton product (p)(q) for q = (0, 1, phi, phi^2):
        i :  v0 + phi^2 * v2 - phi * v3
        j :  phi * v0 - phi^2 * v1 + v3
        k :  phi^2 * v0 + phi * v1 - v2
    """
    v0, v1, v2, v3 = (GF(p[0]), GF(p[1]), GF(p[2]), GF(p[3]))
    p1 = PHI
    p2 = PHI * PHI
    x = v0 + p2*v2 - p1*v3
    y = p1*v0 - p2*v1 + v3
    z = p2*v0 + p1*v1 - v2
    return (x, y, z)

def build_3d_model(v4, e4, project):
    verts3, idx = [], {}
    def get(p3):
        k = vkey(p3)
        if k not in idx:
            idx[k] = len(verts3)
            verts3.append(p3)
        return idx[k]
    p3_of = [project(v) for v in v4]
    edge_set = {}
    collapsed = 0
    for (i, j) in e4:
        a, b = p3_of[i], p3_of[j]
        if vkey(a) == vkey(b):
            collapsed += 1
            continue
        ia, ib = get(a), get(b)
        key = (min(ia, ib), max(ia, ib))
        edge_set[key] = (ia, ib)
    return verts3, list(edge_set.values()), collapsed

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    out_dir = Path(os.path.join(os.path.dirname(__file__), '..', 'output', '24cell'))
    out_dir.mkdir(parents=True, exist_ok=True)
    v4 = v_d4_24cell()
    e4 = edges_24cell(v4)

    print("=== Family A: short-root projection (n = e_4) ===")
    verts, edges, coll = build_3d_model(v4, e4, project_short_root)
    print(f"  3D balls : {len(verts)}")
    print(f"  3D struts: {len(edges)} (collapsed 4D edges: {coll})")
    counts = emit_vzome(verts, edges,
                        out_dir / "24cell_short_root_cuboctahedron.vZome")
    print(f"  strut audit: {dict(sorted(counts.items()))}")

    print()
    print("=== Family B: long-root projection (n = (1,-1,0,0)/sqrt(2)) ===")
    verts, edges, coll = build_3d_model(v4, e4, project_long_root)
    print(f"  3D balls : {len(verts)}")
    print(f"  3D struts: {len(edges)} (collapsed 4D edges: {coll})")
    counts = emit_vzome(verts, edges,
                        out_dir / "24cell_long_root_rhombic_dodecahedron.vZome")
    print(f"  strut audit: {dict(sorted(counts.items()))}")

    print()
    print("=== Family C: triality projection (short-root, q=(0,1,phi,phi^2)) ===")
    v4s = v_short_root_24cell()
    e4s = edges_short_root_24cell(v4s)
    verts, edges, coll = build_3d_model(v4s, e4s, project_triality)
    print(f"  3D balls : {len(verts)}")
    print(f"  3D struts: {len(edges)} (collapsed 4D edges: {coll})")
    counts = emit_vzome_directional(
        verts, edges,
        out_dir / "24cell_triality.vZome")
    print(f"  direction audit: {dict(sorted(counts.items()))}")

if __name__ == '__main__':
    main()
