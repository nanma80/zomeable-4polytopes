"""Emit the canonical zomeable rigid-projection 8-cell vZome models.

Classification (verified by exhaustive search at rng=1, 2, 3):

  ONE infinite family + FOUR sporadic shapes.

The infinite family arises when the 4D kernel direction n has support 2
(exactly 2 nonzero components). Then two image vectors c_i' end up
antiparallel on a single 3D B axis, while the other two image vectors are
unit vectors on the perpendicular 3D B axes. Result: a 4x2x2 ball cuboid
parametrized by the integer ratio a:b (the ratio of the 2 nonzero kernel
components).

The 4 sporadic shapes have kernel support 1, 3, 4 (with 3 and 4 being
isolated arithmetic coincidences):

  Sporadic A  - n along coord axis  (support 1)  -> the cube (8 balls)
  Sporadic B  - n in coord 3-plane                -> 14-ball BBBY shape
  Sporadic C  - n in coord 3-plane                -> 16-ball BBYR shape
  Sporadic D  - n with all 4 nonzero, equal mag   -> rhombic dodecahedron
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from emit_vzome import GF, V, vadd, vscale, vkey, classify_direction, emit_vzome_directional, ZERO, ONE, PHI
from polytopes import tesseract

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '8cell')
os.makedirs(OUT, exist_ok=True)

# Default zometool blue-strut length factor for visible spacing.
SCALE = GF(2, 2)


def emit_skew_zonotope(c_list, fname, norm=ONE):
    """Emit 8-cell zonotope from 4 generator vectors c_1..c_4.

    Each c_i is rescaled by SCALE / norm for visible, comparable ball spacing.
    `norm` should be the max ZZ[phi] component magnitude across c_list, so
    the longest edge is roughly the same size across emitted models.
    """
    from fractions import Fraction
    if isinstance(norm, int):
        norm = GF(Fraction(1, norm), 0)
        factor = SCALE * norm
    else:
        # norm is a GF; compute SCALE / norm using (a+b*phi)^-1 in Q(phi).
        # (a+b*phi)*(a+b-b*phi) = a^2+ab-b^2  (since phi^2 = phi+1)
        a, b = norm.a, norm.b
        denom = a*a + a*b - b*b
        inv_norm = GF(Fraction(a + b, denom), Fraction(-b, denom))
        factor = SCALE * inv_norm
    c_list = [tuple(x * factor for x in c) for c in c_list]
    raw = []
    for s_bits in range(16):
        s = [(1 if (s_bits >> i) & 1 else -1) for i in range(4)]
        acc = (ZERO, ZERO, ZERO)
        for i in range(4):
            acc = vadd(acc, vscale(c_list[i], s[i]))
        raw.append((tuple(s), acc))
    uniq = []
    pos_to_idx = {}
    for s, p in raw:
        k = vkey(p)
        if k not in pos_to_idx:
            pos_to_idx[k] = len(uniq)
            uniq.append(p)
    s_to_idx = {s: pos_to_idx[vkey(p)] for s, p in raw}
    edges3 = set()
    for s_bits in range(16):
        s = tuple((1 if (s_bits >> i) & 1 else -1) for i in range(4))
        for i in range(4):
            s2 = list(s); s2[i] = -s2[i]; s2 = tuple(s2)
            a, b = s_to_idx[s], s_to_idx[s2]
            if a != b:
                edges3.add((min(a, b), max(a, b)))
    edges3 = sorted(edges3)
    for i, j in edges3:
        if classify_direction(uniq[i], uniq[j]) is None:
            raise RuntimeError(f"Edge {i}-{j} not on a default axis")
    counts = emit_vzome_directional(uniq, edges3, os.path.join(OUT, fname))
    print(f"  {fname}: {len(uniq)} balls, {len(edges3)} struts, {counts}")


# =====================================================================
# Sporadic A: the cube. Kernel n = (0, 0, 0, 1), c_4 collapses.
# =====================================================================
print("Sporadic A (cube, support 1):")
emit_skew_zonotope(
    [V(1, 0, 0), V(0, 1, 0), V(0, 0, 1), V(0, 0, 0)],
    "8cell_cell_first_cube.vZome"
)


# =====================================================================
# Infinite family: cuboids from kernel n = (a, b, 0, 0).
# After projection: c_1' = (b, 0, 0), c_2' = (-a, 0, 0),
#                   c_3' = (0, c, 0), c_4' = (0, 0, c)
# where c = sqrt(a^2 + b^2). For ZZ[phi] embedding need c in ZZ[phi].
# Solutions: integer Pythagorean triples (a, b, c) and a^2+b^2 = 5*square.
# We omit overall scale and the 1/SCALE factor; just give the ratio.
# =====================================================================
print("\nInfinite family (split cuboids, support 2):")
# (a, b, c) where c^2 = a^2 + b^2, c representable in ZZ[phi].
examples = [
    # (a, b, c_in_ZZphi, norm),  comment
    ((1, 2), GF(-1, 2), 2,  "(a:b)=1:2  c=sqrt(5)=2*phi-1"),    # 1+4=5=(2*phi-1)^2
    ((3, 4), GF(5, 0),  5,  "(a:b)=3:4  c=5"),                  # 9+16=25=5^2 (Pythagorean)
    ((5, 12), GF(13, 0),13, "(a:b)=5:12 c=13"),                 # Pythagorean
    ((8, 15), GF(17, 0),17, "(a:b)=8:15 c=17"),                 # Pythagorean
    # Non-Pythagorean: a^2+b^2 = 5*m^2, c = m*(2*phi-1) = GF(-m, 2m).
    ((2, 11), GF(-5, 10), GF(-5, 10),  "(a:b)=2:11  c=5*sqrt(5)=5*(2*phi-1)"),
    ((19, 22), GF(-13, 26), GF(-13, 26), "(a:b)=19:22 c=13*sqrt(5)=13*(2*phi-1)"),
    ((2, 29), GF(-13, 26), GF(-13, 26),  "(a:b)=2:29  c=13*sqrt(5)=13*(2*phi-1)"),
]
for (a, b), c, norm, desc in examples:
    print(f"  -- {desc}")
    emit_skew_zonotope(
        [V(b, 0, 0), V(-a, 0, 0),
         (ZERO, c, ZERO), (ZERO, ZERO, c)],
        f"8cell_inf_family_a{a}_b{b}.vZome",
        norm=norm,
    )


# =====================================================================
# Sporadic D: rhombic dodecahedron. Kernel n = (1, -1, -1, 1).
# After projection: 4 image vectors of equal magnitude in tetrahedral
# arrangement. They land on the 4 cube body-diagonals (Y axes).
# This is the ONLY non-cube vZome-embeddable sporadic shape: kernels
# with support 3 give magnitude ratios involving sqrt(2)/sqrt(3),
# which are not in Q(phi).
# =====================================================================
print("\nSporadic D (rhombic dodecahedron, kernel support 4):")
emit_skew_zonotope(
    [V(1, 1, 1), V(1, -1, -1), V(-1, 1, -1), V(-1, -1, 1)],
    "8cell_vertex_first_rhombic_dodec.vZome"
)

print("\nDone. Files in:", OUT)
