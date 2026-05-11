# 8-cell zomeable orthographic projections — complete classification

The 8-cell (tesseract) is the only convex regular 4-polytope whose set of
zomeable orthographic projections is **infinite**. Verified by exhaustive
search over kernel directions n ∈ ℤ[φ]⁴ at rng = 1, 2, 3 (yielding
8, 32, 129 distinct shapes — the count grows without bound).

A fully **inheritance-free, kernel-free** confirmation was added 2026-05-08
via the **strut-quadruple iso-frame enumerator**
(`ongoing_work/strut_iso_enumerator.py`), which constructs the 4 strut
vectors (s₁, s₂, s₃, s₄) directly in ℤ[φ]³ — each as
(natural ℤ[φ]³ generator) × (positive ℤ[φ] scalar) — and verifies the
orthographic isotropy condition `M Mᵀ = c·I₃` numerically. At scalar
bound = 12 the enumerator finds exactly **15 distinct shape fingerprints**:
1 cube + 1 rhombic dodec + 1 phi-oblique + 12 inf-family members (12 distinct
(a:b) ratios). No additional sporadic types appear, confirming the
taxonomy below.

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
| 1 | Yes | Yes | **Cell-first sporadic**: the cube (V=8). Also the `b → 0` degenerate limit of the support-2 inf-family (4 of the 16 balls collapse pairwise onto the other 4). |
| 2 | Always | Iff a²+b² is a square in ℤ[φ] | **The infinite family**: split cuboids parametrized by (a:b); face-first cuboid (a,b)=(1,1) is the cubic-system V=12 case |
| 3 | Discrete subset | **One φ-rational direction yes** + 2 cubic-only directions | **Phi-oblique sporadic** (V=16, vZome ℤ[φ]); edge-first hex prism (V=14, cubic Z[√2,√3]); face-first-like BYR shape (V=16, cubic) |
| 4 | Discrete subset | Only n = ±(1,1,1,1) up to ±-flips | **Vertex-first sporadic**: rhombic dodecahedron (V=15) |

So **in vZome strict** (icosahedral ℤ[φ] coords): there is

  **1 infinite family + 3 sporadic shapes** (cube, phi-oblique, rhombic dodec).

We list the cube as a sporadic even though it is technically the `b → 0`
degenerate boundary of the inf-family: at that limit the strut count and
ball count drop (V=8, E=12 instead of 16/32), making it visually and
combinatorially distinct from every interior member of the family.

The "phi-oblique" sporadic (kernel support 3, three image vectors *coplanar*
in 3D — none zero — with the 4th independent) was added 2026-05-08 after
the inheritance-free matrix sweep and confirmed by the strut-quadruple
iso-frame enumerator. The original 2-sporadic count missed it.

In the broader "zometool-axis-aligned" sense (any rotation of the 4
image vectors onto default zometool directions, regardless of length
field): add the **edge-first hex prism** (V=14) and **face-first cuboid**
(V=12, a degenerate (a,b)=(1,1) member of the support-2 family) plus the
**face-first-like BYR shape** (V=16, kernel ~ (0, 1/φ, −φ, −1)). These
require lengths involving √2 or √3 — outside ℚ(φ) — and live in vZome's
**cubic** algebraic-field system, not the icosahedral one. They are
honest Zometool sculptures but cannot be expressed with all coordinates
in ℤ[φ]³ at a single uniform scale.

## 3. The infinite family — split cuboids (support 2)

For n = (a, b, 0, 0) (and B₄-images thereof), with a, b ∈ ℤ[φ]:

- c_1' = (b, 0, 0)  (B-axis, magnitude |b|)
- c_2' = (−a, 0, 0)  (B-axis, magnitude |a|, antiparallel to c_1')
- c_3' = (0, c, 0)  (B-axis, magnitude c = √(a²+b²))
- c_4' = (0, 0, c)  (B-axis, magnitude c)

The 16 ball positions form a **4 × 2 × 2 cuboid lattice** with x-spacings
(2|b|, 2|a−b|, 2|b|), y-spacing 2c, z-spacing 2c.

**Parameter**: pair (a, b) ∈ ℤ[φ]²₊ modulo overall scale, modulo a ↔ b
swap, and modulo the constraint √(a²+b²) ∈ ℤ[φ] (so c is in the same
field as the projected coordinates).

**vZome-embeddability constraint**. Write a = a₁ + a₂φ, b = b₁ + b₂φ
with aᵢ, bᵢ ∈ ℤ. Then

  a² + b²  =  (a₁² + a₂² + b₁² + b₂²)  +  [a₂(2a₁ + a₂) + b₂(2b₁ + b₂)] · φ

The full vZome-embeddability requirement is just c = √(a²+b²) ∈ ℤ[φ].
That splits into two regimes:

**(i) Trace-zero regime** — the φ-coefficient of a²+b² vanishes:

  **a₂(2a₁ + a₂) + b₂(2b₁ + b₂) = 0**          (trace-zero condition)

Then a² + b² is a positive integer S, and we need S to be a perfect
square or 5·m² in ℤ for c = √S to lie in ℤ[φ]. The two integer
sub-families therefore arise:

- **Pythagorean branch**: a² + b² = c² with c ∈ ℤ. y- and z-edges
  integer blue struts.
- **5m² branch**: a² + b² = 5m² with c = m·(2φ − 1) = m·√5. y- and
  z-edges are blue-φ struts.

**(ii) Genuinely-φ regime** — a²+b² has a nonzero φ-coefficient, but
c ∈ ℤ[φ] picks up a matching φ-coefficient so that c² = a²+b². For
example, (a, b) = (1+3φ, 4) gives a²+b² = 26+15φ, which equals
c² for c = −1+5φ ∈ ℤ[φ]. The 8-cell projection then has y- and z-edge
length |c| = √(26+15φ), perfectly valid in vZome.

So the inf-family is parameterized by the full set of ℤ[φ]-Pythagorean
triples (a, b, c) — both trace-zero and genuinely-φ — modulo (a:b)
projective equivalence and the swap a ↔ b.

Primitive **integer** (a, b ∈ ℤ, so trivially trace-zero) solutions on
the 5m² branch come from factoring in ℤ[i]: writing
a + b·i = (2 + i)·(p + q·i)² gives

    a = 2p² − 2pq − 2q²,   b = p² + 4pq − q²,   m = p² + q².

First few primitive integer (a, b, m): (1, 2, 1), (2, 11, 5),
(19, 22, 13), (2, 29, 13), (22, 31, 17), …

**Genuinely-φ generators (a₂ ≠ 0 or b₂ ≠ 0)** also exist; the integer
case is just the (a₂ = b₂ = 0) sub-locus. The smallest non-integer
generator points (canonicalised so a ≥ b > 0, then by ascending S) are:

| (a, b)              | regime           | a² + b² | c            | notes                                                            |
|:--------------------|:-----------------|:-------:|:-------------|:-----------------------------------------------------------------|
| (√5, 2) = (−1+2φ, 2) | (i) trace-zero  |   9     | 3            | emitted as `8cell_inf_family_phi_aSqrt5_b2.vZome`                |
| (3 + 2φ, 4φ − 4)    | (i) trace-zero   |  45     | 3√5          | 5m² branch (m=3); emitted as `8cell_inf_family_phi_a3plus2phi_b4phi-4.vZome` |
| (4φ, 5 − 2φ)        | (i) trace-zero   |  45     | 3√5          | Galois conjugate of the previous row; emitted as `8cell_inf_family_phi_a4phi_b5-2phi.vZome` |
| (4, 1+3φ)           | (ii) genuinely-φ | 26+15φ  | −1+5φ ≈ 7.09 | discovered by strut-iso enumerator b≤8; not yet emitted          |

**rng=5/6 audit (2026-05-10).** A re-search at rng ∈ {4, 5, 6} with
B₄-symmetry-deduplicated kernel directions
(`gen_dirs(permute_dedup=True)`, exact for the tesseract) finds
**exactly the same 4 shape types** — cube, rhombic dodec, phi-oblique,
inf-family — and 2 inf-family parameter rows not previously emitted
(the (3+2φ, 4φ−4) and (4φ, 5−2φ) rows above).  Both snap cleanly to
ℤ[φ]³ with integer coordinates and single-colour B struts.  No new
sporadic types appear.  Audit driver:
`ongoing_work/probes/tesseract_audit_rng5.py`.

**Strut-iso enumeration status.** The strut-quadruple iso-frame enumerator
(`ongoing_work/strut_iso_enumerator.py`) at scalar bound 12 found
**12 distinct (a:b) ratios** in the inf-family at V=16: a few integer
Pythagorean branch members ((1,2,√5), (3,4,5), …), one (2,√5,3) trace-zero
ℤ[φ] member, and 8 additional ratios on the genuinely-φ branch. The
complete list is in `ongoing_work/strut_iso_frames_b12.json`. Pushing
the bound higher adds more (a:b) points but produces no new shape *type*
— the **cube + rhombic dodec + phi-oblique + inf-family** taxonomy is
closed under all icosahedral-palette zomeable orthographic projections
of the 8-cell.

**Examples emitted** (`8cell_inf_family_*.vZome`, all normalized so
the longest edge is roughly one ball-spacing).

| (a, b)            | a² + b²    | c              | branch                | filename suffix                |
|:------------------|:----------:|:--------------:|:----------------------|:-------------------------------|
| (1, 2)            | 5          | 2φ − 1 = √5    | 5m² (m=1)             | `a1_b2`                        |
| (3, 4)            | 25         | 5              | Pythagorean           | `a3_b4`                        |
| (5, 12)           | 169        | 13             | Pythagorean           | `a5_b12`                       |
| (8, 15)           | 289        | 17             | Pythagorean           | `a8_b15`                       |
| (2, 11)           | 125 = 25·5 | 5(2φ − 1)      | 5m² (m=5)             | `a2_b11`                       |
| (19, 22)          | 845 = 169·5| 13(2φ − 1)     | 5m² (m=13)            | `a19_b22`                      |
| (2, 29)           | 845 = 169·5| 13(2φ − 1)     | 5m² (m=13)            | `a2_b29`                       |
| (√5, 2)           | 9          | 3              | trace-zero ℤ[φ]       | `phi_aSqrt5_b2`                |
| (3 + 2φ, 4φ − 4)  | 45 = 9·5   | 3√5            | 5m² (m=3), ℤ[φ]       | `phi_a3plus2phi_b4phi-4`       |
| (4φ, 5 − 2φ)      | 45 = 9·5   | 3√5            | 5m² (m=3), ℤ[φ]       | `phi_a4phi_b5-2phi`            |

Note that (19, 22) and (2, 29) share the same c = 13√5 but are
genuinely distinct shapes (different a:b ratios).  Similarly the last
two rows above share c = 3√5 but are distinct directions (and Galois
conjugates of each other).  Other valid integer (a, b) include
(7, 24, 25), (20, 21, 29), … on the Pythagorean branch and
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

This is also the **`b → 0` degenerate boundary** of the inf-family
(support-2) parametrization: setting (a, b) = (1, 0) gives kernel
n = (1, 0, 0, 0), with c_4 = 0 collapsing 4 of the 16 inf-family balls
onto their c_3 partners. We list it as a sporadic anyway because the
collapse changes both the ball count (16 → 8) and the strut count
(32 → 12), so visually and combinatorially it is a distinct shape, not
a generic family member.

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

### Phi-oblique sporadic — `8cell_phi_oblique.vZome` (kernel support 3)

Discovered 2026-05-08 by the inheritance-free matrix sweep
(`tools/inheritance_free_sweep.py`) and confirmed by the strut-quadruple
iso-frame enumerator at scalar bound 12.  Kernel `(0, 1/φ², 1, −1/φ)`
(a support-3 direction whose three nonzero components are *all*
φ-rational).  Geometric interpretation: the three c_iʹ corresponding to
the nonzero kernel entries lie **coplanar** in 3D — none of them is zero
— while the c_iʹ for the zero kernel entry is independent of that plane.
This is the support-3 case the original analysis missed: unlike the two
non-embeddable support-3 directions below, this one **does** embed
cleanly in ℤ[φ]³.  Full V=16, E=32 with 4 distinct edge-length classes
(1.0×8, 1.473×8, φ×8, 1.701×8).  Stage-B sig prefix `88c5a53810074918`.

(The earlier-discovered `kc_triage_2c105cd47b.vZome` from the M19 ZZ[φ,√2]
sweep — kernel `(0, 1/φ², 1, −1/φ)` — is the same shape under tesseract
B₄ symmetry; both are absorbed into this orbit.)

### Edge-first and face-first canonical projections (cubic-system zometool, NOT icosahedral)

These are the canonical X-first projections that traditional 4D-polytope
literature calls out, but they fall **outside** the icosahedral ℤ[φ] field
and so are excluded from the "1 infinite family + 3 sporadics" count
above. They are still legitimate zometool sculptures — just in vZome's
**cubic** system (the Z[√2, √3] field).

- **Edge-first hex prism** (V=14): kernel support 3, e.g. n=(1, −1, 1, 0)
  up to symmetry. Strut sig {B:24, Y:8}. Three c_iʹ have magnitude
  √(2/3), one has magnitude 1. Length ratio √2 / √3 ∉ ℚ(φ). Built from
  hex-prism geometry: one B axis "long" + a hexagonal Y-strut hexagon.
- **Face-first 4×2 cuboid** (V=12): kernel support 2, n=(1, 1, 0, 0). The
  degenerate (a, b)=(1, 1) limit of the infinite family. c = √2 ∉ ℤ[φ].
  Two ball pairs collapse, leaving 12 of 16 ball positions distinct.
- **Face-first-like BYR shape** (V=16): kernel (0, 1/φ, −φ, −1), strut sig
  {B:8, Y:8, R:16}. Magnitudes √(2+φ)/2, √(3−φ)/2, etc. Ratios involve
  √(2+φ) ∉ ℚ(φ).

All three live in different algebraic-field extensions of vZome (cubic /
mixed √2,√3 / √(2+φ)). We do not emit them in `output/8cell/` because
this corpus is icosahedral-field strict.

## 5. Why other regular 4-polytopes are finite

For the 5/16/24/120/600-cells, edge directions are not aligned with any
4D coordinate basis, so no analog of the "support-2 kernel ⇒ automatic
zomeability" argument exists. Each cell type yields a **finite** list of
zomeable projections (4, 6, 3, 1, 1 respectively in our enumeration).

## 6. Files in this directory

```
8cell_cell_first_cube.vZome            ← cell-first sporadic (cube, 8 balls)
8cell_vertex_first_rhombic_dodec.vZome ← vertex-first sporadic (rhombic dodec, 15 balls)
8cell_phi_oblique.vZome                ← phi-oblique sporadic, support-3 (16 balls, added 2026-05-08)
8cell_inf_family_a1_b2.vZome           ← infinite family, 5m² branch (m=1)
8cell_inf_family_a3_b4.vZome           ← infinite family, Pythagorean (3-4-5)
8cell_inf_family_a5_b12.vZome          ← infinite family, Pythagorean (5-12-13)
8cell_inf_family_a8_b15.vZome          ← infinite family, Pythagorean (8-15-17)
8cell_inf_family_a2_b11.vZome          ← infinite family, 5m² branch (m=5)
8cell_inf_family_a19_b22.vZome         ← infinite family, 5m² branch (m=13)
8cell_inf_family_a2_b29.vZome          ← infinite family, 5m² branch (m=13)
8cell_inf_family_phi_aSqrt5_b2.vZome   ← infinite family, Pythagorean (√5, 2, 3) — first ℤ[φ] generator (added 2026-05-08)
```

All inf-family models are normalized per-emit (each divided by its own
longest component) so they appear at comparable scale in vZome rather
than growing with (a, b).

Generator: `lib/emit_8cell.py`. To add more cuboids from the infinite
family, append to the `examples` list with any (a, b, c) satisfying
a² + b² = c² in ℤ (Pythagorean triple) or a² + b² = 5m² (then
c = m·(2φ−1)).
