"""V/E sanity check for all 204 prismatic polytopes in scope.

Family A: 17 polyhedral prisms (skip cube_prism = tesseract)
  Expected: |V| = 2 |V_P|, |E| = 2 |E_P| + |V_P|

Family B: 170 duoprisms {p}x{q} with 3 <= p <= q <= 20, (p,q) != (4,4)
  Expected: |V| = p*q, |E| = 2*p*q

Family C: 17 antiprismatic prisms (n in [3, 20], skip n=3 = octahedral prism)
  Expected: |V| = 4n, |E| = 10n
  (3D antiprism: 2n verts, 4n edges = n top-gon + n bot-gon + 2n zigzag.
   4D prism = 2 copies + verticals = 2*4n + 2n = 10n.)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from uniform_polyhedra import UNIFORM_POLYHEDRA, all_polyhedra, expected_VE
from polytopes_prismatic import (
    polyhedral_prism, duoprism, antiprismatic_prism,
    polyhedral_prism_slug, duoprism_slug, antiprismatic_prism_slug,
)

fail = 0
total = 0

# ---- Family A ----
print("=" * 80)
print("Family A: polyhedral prisms")
print("=" * 80)
print(f"{'slug':<40s} {'V':>5s}({'exp':>5s}) {'E':>5s}({'exp':>5s})  zphi")
print("-" * 80)
for name in all_polyhedra():
    if name == "cube":
        continue  # cube prism = tesseract
    nv_p, ne_p, zphi = expected_VE(name)
    nv_exp = 2 * nv_p
    ne_exp = 2 * ne_p + nv_p
    V, E = polyhedral_prism(name)
    slug = polyhedral_prism_slug(name)
    ok = (len(V) == nv_exp) and (len(E) == ne_exp)
    if not ok:
        fail += 1
    total += 1
    flag = "" if ok else " [FAIL]"
    print(f"{slug:<40s} {len(V):5d}({nv_exp:5d}) {len(E):5d}({ne_exp:5d})  {str(zphi):5s}{flag}")

# ---- Family B ----
print()
print("=" * 80)
print(f"Family B: duoprisms (3 <= p <= q <= 20, skip (4,4))")
print("=" * 80)
b_fail = 0
b_total = 0
for p in range(3, 21):
    for q in range(p, 21):
        if (p, q) == (4, 4):
            continue
        nv_exp = p * q
        ne_exp = 2 * p * q
        V, E = duoprism(p, q)
        ok = (len(V) == nv_exp) and (len(E) == ne_exp)
        if not ok:
            slug = duoprism_slug(p, q)
            print(f"{slug:<40s} {len(V):5d}({nv_exp:5d}) {len(E):5d}({ne_exp:5d})  [FAIL]")
            b_fail += 1
        b_total += 1
print(f"Family B: {b_total} duoprisms checked, {b_fail} failures")
fail += b_fail
total += b_total

# ---- Family C ----
print()
print("=" * 80)
print(f"Family C: antiprismatic prisms (n in [3, 20], skip n=3)")
print("=" * 80)
print(f"{'slug':<40s} {'V':>5s}({'exp':>5s}) {'E':>5s}({'exp':>5s})")
print("-" * 80)
for n in range(3, 21):
    if n == 3:
        continue  # octahedral prism = Family A
    nv_exp = 4 * n
    ne_exp = 10 * n
    V, E = antiprismatic_prism(n)
    slug = antiprismatic_prism_slug(n)
    ok = (len(V) == nv_exp) and (len(E) == ne_exp)
    if not ok:
        fail += 1
    total += 1
    flag = "" if ok else " [FAIL]"
    print(f"{slug:<40s} {len(V):5d}({nv_exp:5d}) {len(E):5d}({ne_exp:5d})  {flag}")

# ---- Summary ----
print()
print("=" * 80)
print(f"Total checked: {total} polytopes")
print(f"Total failures: {fail}")
print("=" * 80)
sys.exit(0 if fail == 0 else 1)
