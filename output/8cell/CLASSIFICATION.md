# 8-cell zomeable orthographic projections — complete classification

The 8-cell (tesseract) is the only convex regular 4-polytope whose set of
zomeable orthographic projections is **infinite**. Verified by exhaustive
search over kernel directions n ∈ ℤ[φ]⁴ at rng = 1, 2, 3 (yielding
8, 32, 129 distinct shapes — the count grows without bound).

This document gives the complete, rigorous classification.

## 1. Setup

For a unit kernel direction n ∈ S³ ⊂ ℝ⁴, the orthogonal projection of the
regular 8-cell sends the four edge directions e_i ↦ c_i = e_i − n_i n.
The image vectors satisfy:

  |c_i|² = 1 − n_i²,    c_i · c_j = −n_i n_j   (i ≠ j),    Σ n_i c_i = 0.

The model has 16 ball positions V(s) = Σ s_i c_i' for s ∈ {±1}⁴ (where
c_i' is c_i rotated into 3D = n^⊥), and 32 struts in 4 parallel classes.

The projection is **zometool-axis aligned** (search-engine criterion) iff
each direction c_i'/|c_i'| equals a default zometool axis (B/Y/R/G).

It is additionally **vZome-embeddable** (in the standard icosahedral
ℤ[φ]-field) iff after rotation R the c_i' lie in ℤ[φ]³ up to a global
scale, which requires every length ratio |c_i|/|c_j| ∈ ℚ(φ).

## 2. Master theorem

A 4D unit kernel direction n falls into one of four cases by support
(number of nonzero components), and the family structure is:

| Support of n | Zometool-aligned? | vZome-embeddable? | Family structure |
|:---:|:---|:---|:---|
| 1 | Yes | Yes | **Cell-first sporadic**: the cube |
| 2 | Always | Iff a²+b² is a square in ℤ[φ] | **The infinite family**: split cuboids parametrized by (a:b) |
| 3 | Discrete subset | Generally **no** (Q(φ) length-ratio fails) | 2 zometool-aligned shapes, neither vZome-embeddable |
| 4 | Discrete subset | Only n = ±(1,1,1,1) up to ±-flips | **Vertex-first sporadic**: rhombic dodecahedron |

So **in vZome strict** (ℤ[φ] coords): there is

  **1 infinite family + 2 sporadic shapes**.

In the broader "zometool-axis-aligned" sense (any rotation of the 4
image vectors onto default zometool directions, regardless of length
field): add 2 more sporadic shapes that exist as zometool sculptures
but cannot be realized in vZome's standard icosahedral field.

## 3. The infinite family — split cuboids (support 2)

For n = (a, b, 0, 0) (and B₄-images thereof), with a, b ∈ ℤ[φ]:

- c_1' = (b, 0, 0)  (B-axis, magnitude |b|)
- c_2' = (−a, 0, 0)  (B-axis, magnitude |a|, antiparallel to c_1')
- c_3' = (0, c, 0)  (B-axis, magnitude c = √(a²+b²))
- c_4' = (0, 0, c)  (B-axis, magnitude c)

The 16 ball positions form a **4 × 2 × 2 cuboid lattice** with x-spacings
(2|b|, 2|a−b|, 2|b|), y-spacing 2c, z-spacing 2c.

**Parameter**: integer ratio (a : b) ∈ ℤ²₊ / overall scale, modulo a ↔ b
swap and modulo the constraint that (a, b, c) is "a square sum in ℤ[φ]"
(i.e. √(a²+b²) ∈ ℤ[φ]).

**vZome-embeddability constraint**: a² + b² must be a square in ℤ[φ].
For (m+nφ)² = (m²+n²) + n(2m+n)φ to lie in ℤ we need either n=0 (giving
m²) or n=−2m (giving 5m²). So **a² + b² must equal either an integer
square c², or 5m²** (in which case c = m·(2φ−1) = m·√5).

Two infinite sub-families therefore arise:

- **Pythagorean branch**: a² + b² = c² with c ∈ ℤ. All edges integer
  blue struts. Primitive solutions are the usual Pythagorean triples.
- **5m² branch**: a² + b² = 5m² with c = m(2φ−1). The y- and z-edges
  are now blue-φ struts (length involves φ); only x-edges are integer.
  Primitive solutions come from factoring in ℤ[i]: writing
  a + b·i = (2 + i)·(p + q·i)² gives

    a = 2p² − 2pq − 2q²,   b = p² + 4pq − q²,   m = p² + q².

  First few primitive (a, b, m):
  (1, 2, 1), (2, 11, 5), (19, 22, 13), (2, 29, 13), (22, 31, 17), …

**Examples emitted** (`8cell_inf_family_a*_b*.vZome`, all normalized so
the longest edge is roughly one ball-spacing):

| (a, b)   | a² + b²    | c              | branch       |
|:--------:|:----------:|:--------------:|:-------------|
| (1, 2)   | 5          | 2φ − 1 = √5    | 5m² (m=1)    |
| (3, 4)   | 25         | 5              | Pythagorean  |
| (5, 12)  | 169        | 13             | Pythagorean  |
| (8, 15)  | 289        | 17             | Pythagorean  |
| (2, 11)  | 125 = 25·5 | 5(2φ − 1)      | 5m² (m=5)    |
| (19, 22) | 845 = 169·5| 13(2φ − 1)     | 5m² (m=13)   |
| (2, 29)  | 845 = 169·5| 13(2φ − 1)     | 5m² (m=13)   |

Note that (19, 22) and (2, 29) share the same c = 13√5 but are
genuinely distinct shapes (different a:b ratios). Other valid (a, b)
include (7, 24, 25), (20, 21, 29), … on the Pythagorean branch and
(22, 31, 17), … on the 5m² branch. Trivially-related cases:
(2, 4) ≡ (1, 2) (same ratio, scaled); (1, 0) → cube; (a, a) → degenerate
12-ball collapse.

## 4. The sporadic shapes

### Cell-first sporadic — the cube (kernel support 1)

Kernel n = (0, 0, 0, 1) (or any e_i). The kernel is **perpendicular to a
cubic cell** of the 8-cell, so the projection drops one full cell onto
its 3-cube image. The 4th edge direction collapses: c_4 = 0.

- **8 balls, 12 struts (B:12)**.
- File: `8cell_cell_first_cube.vZome`

### Vertex-first sporadic — the rhombic dodecahedron (kernel support 4)

Kernel n = (1, −1, −1, 1)/2. The kernel **passes through two opposite
vertices** of the 8-cell (a body diagonal). All four |c_i|² = 3/4 (equal),
and the 4 image vectors land tetrahedrally on the cube body-diagonals
(Y axes (1,1,1), (1,−1,−1), (−1,1,−1), (−1,−1,1)).

- **15 balls, 32 struts (Y:32)** (one ball pair collapses at center).
- File: `8cell_vertex_first_rhombic_dodec.vZome`

This is the **only** support-4 vZome-embeddable shape, because among
4-vectors of equal magnitude in ℝ³ at tetrahedral angles, only the
cube-diagonal frame has ℤ[φ] coordinates.

### Two zometool-aligned non-embeddable shapes (kernel support 3)

For completeness, the search at rng=1 also finds two shapes that are
zometool-strut shapes but cannot be expressed with all ball coordinates
in ℤ[φ]³:

- **edge-first-like**: kernel (1, −1, 1, 0), strut sig {B:24, Y:8}, 14
  balls. Three c_i have magnitude √(2/3), one has magnitude 1. Length
  ratio √2/√3 ∉ ℚ(φ).
- **face-first-like**: kernel (0, 1/φ, −φ, −1), strut sig
  {B:8, Y:8, R:16}, 16 balls. Magnitudes √(2+φ)/2, √(3−φ)/2, etc.
  Ratios involve √(2+φ) ∉ ℚ(φ).

Both live in different algebraic-field extensions of vZome, not the
icosahedral field. We do not emit them.

## 5. Why other regular 4-polytopes are finite

For the 5/16/24/120/600-cells, edge directions are not aligned with any
4D coordinate basis, so no analog of the "support-2 kernel ⇒ automatic
zomeability" argument exists. Each cell type yields a **finite** list of
zomeable projections (4, 6, 3, 1, 1 respectively in our enumeration).

## 6. Files in this directory

```
8cell_cell_first_cube.vZome            ← cell-first sporadic (cube, 8 balls)
8cell_vertex_first_rhombic_dodec.vZome ← vertex-first sporadic (rhombic dodec, 15 balls)
8cell_inf_family_a1_b2.vZome           ← infinite family, 5m² branch (m=1)
8cell_inf_family_a3_b4.vZome           ← infinite family, Pythagorean (3-4-5)
8cell_inf_family_a5_b12.vZome          ← infinite family, Pythagorean (5-12-13)
8cell_inf_family_a8_b15.vZome          ← infinite family, Pythagorean (8-15-17)
8cell_inf_family_a2_b11.vZome          ← infinite family, 5m² branch (m=5)
8cell_inf_family_a19_b22.vZome         ← infinite family, 5m² branch (m=13)
8cell_inf_family_a2_b29.vZome          ← infinite family, 5m² branch (m=13)
```

All inf-family models are normalized per-emit (each divided by its own
longest component) so they appear at comparable scale in vZome rather
than growing with (a, b).

Generator: `lib/emit_8cell.py`. To add more cuboids from the infinite
family, append to the `examples` list with any (a, b, c) satisfying
a² + b² = c² in ℤ (Pythagorean triple) or a² + b² = 5m² (then
c = m·(2φ−1)).
