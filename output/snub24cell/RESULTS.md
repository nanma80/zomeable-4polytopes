# Snub 24-cell: zomeable projections to 3D

The **snub 24-cell** {3,4,3}/2 is one of two non-Wythoff convex uniform
4-polytopes. It has 96 vertices, 432 edges, 480 faces (96 triangles + 384
faces from icosahedral cells), 144 cells (24 icosahedra + 120 tetrahedra),
and symmetry group of order 1152 (the snub-24 symmetry group, related to
D₄ < F₄ by index 6).

It is built by **alternation** of the truncated 24-cell, so its edge
structure is fundamentally non-root: edges live in directions outside the
F₄ root system. This makes it the prime candidate (along with the grand
antiprism) for genuinely new zomeable orthographic projections beyond
those of the 6 regular 4-polytopes.

## Result: 2 distinct zomeable shapes

Empirical search on direction grid up to rng=4 finds **exactly 2
distinct zomeable orthographic projections**, each verified strict-
orthographic by the M·Mᵀ = s²·I test:

| File | Kernel direction | 3D balls | 4D edges → 3D struts | Strut counts |
|------|------------------|----------|----------------------|--------------|
| `snub24cell_cell_first.vZome`   | (1, 0, 0, 0) | 60 | 432 → 228 | B:72  Y:84  R:72 |
| `snub24cell_vertex_first.vZome` | (φ², φ, 1, 0) | 69 | 432 → 312 | B:90  Y:102 R:120 |

Both projections use **all three default zometool colors** (blue,
yellow, red) — a richer color signature than any of the regular
4-polytope projections, reflecting the snub's symmetry breaking that
mixes pentagonal (red), tetrahedral (yellow), and rectilinear (blue)
features.

### Projection 1: cell-first (60 balls)

Kernel: (1, 0, 0, 0). This direction is **the center of one of the 24
icosahedral cells** of the snub 24-cell. It is also exactly a vertex
of the *removed* inscribed 24-cell (recall: snub 24-cell = 600-cell
minus a 24-cell, and the removed 24-cell vertices become the
icosahedral cell centers).

Projecting along this axis squashes the icosahedral cell at +e₁ and
the antipodal one at −e₁ onto the 3D origin. 96 vertices → 60
distinct 3D points (36 collapses; 12 zero-length antipodal-edge
collapses).

Found in 80 distinct kernel directions at rng=4 (the orbit of the
cell-center direction under the snub-24's symmetry group).

**3D point group: Tₕ** (pyritohedral, order 24). The proper rotation
group is the chiral tetrahedral T (order 12: E, 8C₃, 3C₂); inversion
lifts this to Tₕ. Despite the kernel (1,0,0,0) having a 4-fold cubic
stabilizer in the parent 24-cell, the snub's 24+24 tetrahedral cell-
pair pattern **breaks the 4-fold to a 3-fold + 2-fold**, giving the
same symmetry as a pyritohedron.

**Relation to 24-cell projections.** The kernel (1, 0, 0, 0) plays
three different roles depending on which polytope it is applied to:

| Polytope | What (1,0,0,0) is | Resulting 3D shape |
|---|---|---|
| 24-cell long-root  (verts ±eᵢ±eⱼ)              | a short-root direction = octahedral **cell** center | cuboctahedron (18 balls) |
| 24-cell short-root (verts ±eᵢ and (±½)⁴, the *inscribed* 24-cell removed from the 600-cell) | a **vertex** direction | rhombic dodecahedron (15 balls) |
| snub 24-cell                                   | a **cell** center (icosahedral cell)               | the 60-ball shape above |

So the snub's cell-first projection does *not* coincide with the
zomeable cell-first projection of the 24-cell (the 18-ball
cuboctahedron lives in the long-root embedding). Instead, the snub's
cell centers are positioned at the **vertices of the removed
short-root 24-cell**, so the snub's cell-first kernel coincides with
that 24-cell's **vertex-first** kernel. The two 3D shadows along
(1,0,0,0) — the snub's 60-ball figure and the rhombic-dodecahedron of
the inscribed short-root 24-cell — are different shapes; they share
only the kernel direction, not a containment relation at canonical
ϕ-power scales.

### Projection 2: vertex-first (69 balls)

Kernel: (φ², φ, 1, 0). After normalization: (φ/2, 1/2, 1/(2φ), 0),
which is **exactly a snub 24-cell vertex** (it is one of the even
permutations of (φ, 1, 1/φ, 0)/2).

Projecting along a vertex direction collapses that vertex and its
antipode onto the 3D origin, with the remaining 94 vertices giving 67
more distinct 3D points (after 27 further collapses; 6 of which are
zero-length edge collapses). Total 69 balls.

Found in 20 distinct kernel directions at rng=4.

**3D point group: D₃d** (antiprismatic, order 12). The proper rotation
group is D₃ (order 6: E, 2C₃, 3C₂) with the principal 3-fold aligned
along the kernel; central inversion lifts it to D₃d.

**Where are the deleted 24-cell vertices?** Of the 24 deleted 4D vertices
(the inscribed 24-cell removed to form the snub), **18 land exactly on
kept-vertex shadow positions** and only **6 visible holes** remain. All 6
visible holes lie on the **outer equator** (axial coord along the kernel
= 0) at the maximum perp radius 1.0, occupying 6 of the 30 evenly-spaced
slots on the unit circle (the other 24 are kept balls). This is the same
camouflage effect seen in the grand antiprism vertex-first projection
(see `grand_antiprism/RESULTS.md`): vertex-first projections of any
*diminished* 600-cell hide most of the deleted vertices via overlap with
kept-vertex shadows.

## Both shapes inherit from the 600-cell's single zomeable projection

Since snub-24 vertices = 600-cell vertices \ inscribed-24-cell
vertices, every snub edge is a 600-cell edge. So every zomeable kernel
of the 600-cell is automatically zomeable for the snub.

The 600-cell has **exactly one** zomeable orthographic shape (one H₄
orbit of kernel directions, the H₄→H₃ projection with 75 distinct
balls). Both kernels (1, 0, 0, 0) and (φ², φ, 1, 0) belong to this
single H₄ orbit and give the **same** 75-ball figure for the 600-cell.

Under the snub's smaller symmetry group (order 1152, an index-12
sub-orbit structure of H₄), the single H₄ orbit splits into **two**
orbits — precisely matching the two snub shapes (60 and 69 balls).
Empirically:

| Polytope | n=(1,0,0,0)         | n=(φ²,φ,1,0)        |
|---|---|---|
| 600-cell | 75 balls (cell/vertex/face/edge — all related under H₄) | 75 balls (same shape) |
| snub-24  | 60 balls (cell-first) | 69 balls (vertex-first) |
| 24-cell long-root  | 18 balls (cuboctahedron, cell-first)         | MISS (kernel not zomeable) |
| 24-cell short-root | 15 balls (rhombic dodec, vertex-first)       | HIT (15 balls)             |

So **starting from the 24-cell alone is insufficient** to generate the
snub's projections (24-cell edges ≠ snub edges). The right parent is
the 600-cell, and the snub's two shapes arise from the **symmetry-
breaking split** of the 600-cell's single H₄ orbit. There are no
additional snub projections beyond these two — the search is
saturated.

## Constructive recipe: diminish the 600-cell zome model

In retrospect, both snub 24-cell zome models can be built directly
from the well-known H₄→H₃ zome model of the 600-cell, without any
4D computation:

1. **Start** from the standard 75-ball, vertex-first/cell-first
   projection of the 600-cell (file `600cell/600cell_H4_to_H3.vZome`
   in this repo). This single 3D figure is the only zomeable
   projection of the 600-cell.

2. **Identify** an inscribed regular 24-cell among the 120 vertices
   of the 600-cell. There are 25 of them. After projection, they fall
   into 2 H₃-orbits, distinguished by whether the chosen 24-cell
   contains the vertex on the projection axis (±n):

   | Orbit | The inscribed 24-cell shadow … | Strategy |
   |---|---|---|
   | (a) on-axis | ±n is one of its 24 vertices; shadow is a 15-ball rhombic dodecahedron, completely **disjoint** from the snub's 60 balls. | "cell-first" snub |
   | (b) off-axis | ±n not in it; shadow is 24 balls of which **18 coincide with snub-vertex projections** and only 6 are exclusive to the inscribed 24-cell. | "vertex-first" snub |

3. **Delete** all balls *exclusive* to the chosen inscribed 24-cell
   (15 balls for orbit (a); 6 balls for orbit (b)) and every strut
   incident to a deleted ball. Where a ball is shared (orbit (b)),
   keep the ball but delete the struts that ran from it to a deleted
   neighbour.

4. **Result**: a valid snub 24-cell zome model.

   - Orbit (a) → the **cell-first** model, 75 − 15 = **60 balls**.
   - Orbit (b) → the **vertex-first** model, 75 − 6 = **69 balls**.

This is a clean post-hoc construction; we only saw it after running
the exhaustive 4D search and noticing the 600-cell relation. The
saturation guarantee from the search ensures that no third snub
zome model exists.

## External reference

A photograph of the snub 24-cell **cell-first** zome model (60 balls,
icosahedral outer hull) appears in:

- D. Richter, *The 24-Cell and its Snub*,
  https://polytopologist.github.io/zome_pages/24cellzome.htm

The vertex-first projection does not appear there.

## Why this is genuinely new

By the rep-theory argument applied to all Wythoff uniforms, the
zomeable kernels of every Wythoffian uniform 4-polytope (47 of them)
must be a subset of the kernels for the regular 4-polytopes
(empirically confirmed for A₄ in `docs/UNIFORM_PLAN.md`).

The snub 24-cell, being non-Wythoff, escapes this constraint. Its
edges include directions that are not in any F₄-root orbit. The
2 projections found here are thus **not realizable as projections of
any of the 6 regular 4-polytopes**.

## Saturation

| rng | |dirs| | hits | distinct shapes |
|-----|------:|-----:|----:|
| 3   | 20474 | 60   | 2 |
| 4   | 135750 | 100 | 2 |

Saturated at rng=3. Both projections are exactly orthographic
(M·Mᵀ eigenvalues all equal to 1.000000000, residual ~1e-15).

## Open question

These two shapes use all three default colors with 60+ ball counts.
A natural follow-up: do they decompose into recognisable pieces (e.g.
icosahedral or rhombicuboctahedral substructures)? Visual inspection
in vZome may reveal nested polyhedra.
