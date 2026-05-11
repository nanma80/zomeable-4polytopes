# Grand antiprism: zomeable projections to 3D

The **grand antiprism** is one of two non-Wythoff convex uniform 4-polytopes
(the other is the snub 24-cell). It has 100 vertices, 500 edges, 720
triangular faces, and 320 cells (300 tetrahedra + 20 pentagonal antiprisms),
with symmetry group of order 400 (the "ionic-diminished" subgroup of H₄
that stabilises a Hopf pair of great decagons in the 600-cell).

It is constructed by **diminishing the 600-cell**: remove 20 vertices that
form two interlocking great decagons on mutually-orthogonal Hopf circles.
The 20 pentagonal-antiprism cells fill in around the two removed Hopf rings.

Discovered by Conway and Guy (1965) by computer search.

## Result: 2 distinct zomeable shapes

Empirical search on a ℤ[φ]⁴ direction grid up to rng=4 finds **exactly 2
distinct zomeable orthographic projections**, each verified strict-
orthographic by the M·Mᵀ = s²·I test:

| File | Kernel direction | 3D balls | 4D edges → 3D struts (collapsed) | Strut counts |
|------|------------------|---------:|----------------------------------|--------------|
| `grand_antiprism_vertex_first.vZome` | (1, 1, 1, 1) | 71 | 500 → 342 (8 collapse)  | B:102 Y:104 R:136 |
| `grand_antiprism_ring_first.vZome`   | (1, 0, 0, 0) | 60 | 500 → 260 (10 collapse) | B:80  Y:80  R:100 |

Both projections use **all three default zometool colors** (blue, yellow,
red) — the same rich signature as the snub 24-cell.

Saturation confirmed: same 2 shapes at rng=2 (1819 dirs, 30 hits), rng=3
(20474 dirs, 60 hits), rng=4 (135750 dirs, 100 hits).

### Projection 1: vertex-first (71 balls)

Kernel: (1, 1, 1, 1). The unit vector (½, ½, ½, ½) **is a vertex of the GA**
(a tesseract-vertex of the parent 600-cell that survives diminishing).

This is the antipodal-pair-vertex-first projection. Eight of the 500 edges
collapse to zero length; the remaining 492 → 342 distinct 3D struts.

**3D point group: D₂ₕ** (order 8). The proper rotation group is **D₂**
(Klein 4-group with three perpendicular C₂ axes); central inversion lifts
this to D₂ₕ. The 3-fold rotation around (1,1,1,1) that exists in H₄ is
**broken** by the GA's diminishing pattern — the 400-element GA stabilizer
of (1,1,1,1) only retains the three coordinate-pair-swap C₂'s.

**Where are the deleted ring vertices?** Of the 20 deleted 4D vertices,
**16 land exactly on kept-vertex shadow positions** (hidden by overlap from
the 4D antipodal collapse + dense 600-cell shadow), and only **4 visible
holes** remain. All 4 visible holes lie on the **outer equator** (axial
coord along (1,1,1,1) = 0) at the maximum perp radius 1.0. The equator
hosts 26 kept balls + 4 holes evenly spaced among 30 slots on the unit
circle. So the only direct evidence of the two removed pentagonal-antiprism
rings, in this projection, is **4 missing balls on the outermost equator**.

The same camouflage effect occurs in the snub 24-cell vertex-first
projection (18 of 24 deletions hidden, 6 visible on the outer equator);
see `snub_24cell/RESULTS.md`. In general, vertex-first projections of any
*diminished* 600-cell hide most deletions because (i) opposite-hemisphere
vertices project onto each other and (ii) the 600-cell shadow is
densely degenerate (75 positions for 120 vertices). This makes the
diminishing pattern hard to read by eye in vertex-first models; cell-
first or ring-first projections expose deletions at multiple radii and
are visually more revealing.

### Projection 2: pentagonal-antiprism-ring axis (60 balls)

Kernel: (1, 0, 0, 0). This direction is **a vertex of one of the two
removed Hopf decagons** — specifically (1,0,0,0) was deleted to form the
GA. So this is the axis of one of the two pentagonal-antiprism rings.

Looking down this axis, the projection inherits clean 5-fold symmetry
because the two removed Hopf decagons sit in **mutually orthogonal
2-planes** (Wikipedia: "the two rings are mutually perpendicular, in a
structure similar to a duoprism"). The 15 deletions from the 600-cell
shadow are distributed:
- 1 at origin (kernel + antipode collapse)
- 2 at distance sin 36° = 0.5878
- 2 at distance sin 72° = 0.9511
- 10 at unit distance (the *other*, perpendicular, Hopf decagon
  projects faithfully as a regular decagon)

This signature matches Scott Vorthmann's 2006 vZome model exactly
(see "External reference" below).

**3D point group: D₅d** (order 20 = pentagonal antiprismatic group: C₅ +
5 perpendicular C₂'s + inversion + S₁₀ + 5 σd). The proper rotation group
is **D₅** (order 10). All 15 holes are visible: 1 at origin + 2 + 2 + 10
laid out at 5 distinct radii.

## Both shapes inherit from the 600-cell's single zomeable projection

Just as for the snub 24-cell, both GA shapes are **subsets** of the
600-cell's unique 75-ball zomeable projection (`600cell/600cell_H4_to_H3.vZome`):

| Kernel | 600-cell balls | GA balls | GA-only | 600-only (deleted) |
|---|---:|---:|---:|---:|
| (1,1,1,1)  | 75 | 71 | 0 | 4 |
| (1,0,0,0)  | 75 | 60 | 0 | 15 |

The single H₄-orbit of zomeable kernel directions for the 600-cell
splits under the order-400 GA symmetry into (at least) **two orbits**,
giving the two shapes. There are no GA-only zomeable kernels (the
empirical search saturates at 2 shapes).

## Constructive recipe: diminish the 600-cell zome model

The simplest mental construction:

1. **Start** with the unique 75-ball 600-cell zome model (H₄ → H₃ Coxeter
   plane projection): `600cell/600cell_H4_to_H3.vZome`.
2. **Identify** the projected images (under the chosen kernel) of the
   20 GA-removed vertices. Since orthogonal projection is many-to-one,
   most removed vertices coincide with kept-vertex projections; only
   a small number of balls (4 or 15) are "exclusive" to the removed
   set in the 3D shadow.
3. **Delete those exclusive balls** (and their incident struts) to
   obtain the GA model.

For the **vertex-first** kernel (1,1,1,1): 4 balls are deleted.

For the **ring-first** kernel (1,0,0,0): 15 balls are deleted, including
the origin (where ±(1,0,0,0) collapse to). The other 14 form the
characteristic 2/2/10 pentagonal pattern described above.

## Construction note: orthogonal Hopf decagons (canonical)

Per Wikipedia: *"20 stacked pentagonal antiprisms occur in two disjoint
rings of 10 antiprisms each. The antiprisms in each ring are joined to
each other via their pentagonal faces. The two rings are mutually
perpendicular, in a structure similar to a duoprism."*

This is implemented in `lib/polytopes.py::grand_antiprism()` by enumerating
all 72 great decagons of the 600-cell and finding a pair satisfying
**both**:

1. **Disjoint vertex sets** with **0 cross-edges** (decagon 2-planes
   completely orthogonal in 4D ⇒ all cross-distances = √2 ≠ 1/φ).
2. **Uniform vertex degree 10** in the kept subgraph (vertex-transitive
   ⇒ canonical GA, not an isomerism).

Counts in the 600-cell:
- 72 great decagons total.
- 396 disjoint pairs with 0 cross-edges (yielding 100-vertex 500-edge
  subsets), but only **36 of these are true GA inscriptions** (uniform
  deg 10). The other 360 are non-Hopf isomerisms with degree
  distribution {8:20, 10:60, 12:20} — they have 100 verts and 500
  edges *by accident* and are NOT vertex-transitive.

The 36 valid pairs match the expected H₄-orbit size of inscribed GAs:
|H₄|/|GA stabiliser| = 14400/400 = 36.

## Comparison with snub 24-cell

| | Snub 24-cell | Grand antiprism |
|---|---|---|
| Construction | 600-cell minus 24-cell verts | 600-cell minus 2 perpendicular Hopf decagons |
| Removed verts | 24 | 20 |
| Verts | 96 | 100 |
| Edges | 432 | 500 |
| Symmetry order | 1152 | 400 |
| #zomeable shapes | 2 | 2 |
| Shape A balls | 60 (cell-first) | 71 (vertex-first) |
| Shape B balls | 69 (vertex-first) | 60 (ring-first) |
| Both inherit from 600-cell? | Yes | Yes |
| Genuinely new directions? | No (all kernels are 600-cell H₄ kernels) | No (same) |

Both non-Wythoff polytopes give exactly **2 zomeable projections each**,
and in both cases all kernel directions are inherited from the 600-cell's
single H₄-orbit zomeable kernel — the smaller symmetry just splits that
orbit into 2 sub-orbits.

### 3D point groups in detail

All four 4D polytopes here are centrally symmetric, so the 3D shadows all
contain the inversion -I. The proper rotation group (chiral 3D symmetry)
and the full point group are:

| Projection | Proper rotations | Full point group | Description |
|---|---|---|---|
| Snub 24-cell cell-first   | T (order 12: E, 8C₃, 3C₂)  | **Tₕ**  (order 24) | Pyritohedral. None of the four C₃ axes is aligned with the kernel; they pass through 4 pairs of icosahedral cells off-axis. |
| Snub 24-cell vertex-first | D₃ (order 6: E, 2C₃, 3C₂)  | **D₃d** (order 12) | Antiprismatic; principal C₃ aligned with the kernel (φ²,φ,1,0). |
| GA vertex-first           | D₂ (order 4: E, 3C₂)       | **D₂ₕ** (order 8)  | The H₄ 3-fold around (1,1,1,1) is broken by the GA's two-decagon diminishing pattern; only three coord-pair-swap C₂'s survive. |
| GA ring-first             | D₅ (order 10: E, 4C₅, 5C₂) | **D₅d** (order 20) | Pentagonal antiprismatic; aligned with the surviving ring (the perpendicular removed decagon is normal to the projection, so its 5-fold drives the symmetry). |

## Methodology / files

- Vertex/edge construction: `lib/polytopes.py::grand_antiprism()`.
  Enumerates all 72 great decagons, picks the first orthogonal-Hopf pair
  (0 cross-edges, uniform degree 10) — guarantees canonical GA.
- Search: `lib/search_engine.py` (`gen_dirs`, `search`, `group_by_shape`).
- Emission: `lib/emit_grand_antiprism.py` → `lib/emit_generic.py`
  with `extra_scale = GF(3, 5) = φ⁵` (gives B2/Y2/R1/R2 standard
  zometool sizes, matching the snub 24-cell models).
- Both vZome models verified at emit time by `classify_direction`
  (every strut on a default zometool axis).

## External reference

Scott Vorthmann (vZome's author) published a vZome model of the
grand antiprism in 2006:
[https://vorth.github.io/vzome-sharing/2006/02/24/grand-antiprism.html](https://vorth.github.io/vzome-sharing/2006/02/24/grand-antiprism.html)

His model uses the **ring-first** projection (kernel along a
pentagonal-antiprism ring axis), the same as our
`grand_antiprism_ring_first.vZome`. Verified equivalent: his 600-cell-
shadow deletion pattern (1@origin + 2@sin36° + 2@sin72° + 10@1.0 = 15
balls) matches ours exactly. He uses vZome's built-in `UniformH4Polytope`
operation (with `polytope.index = 1` for the 600-cell and a
left-isoclinic quaternion to reorient), then deletes the 20 ring vertices.
Our approach reaches the same configuration by direct enumeration of
orthogonal Hopf-decagon pairs in the 4D vertex set.

## Reference

- Wikipedia, [Grand antiprism](https://en.wikipedia.org/wiki/Grand_antiprism).
- J. H. Conway and M. J. T. Guy, "Four-dimensional Archimedean polytopes",
  Proc. Colloquium on Convexity, Copenhagen 1965.
- S. Vorthmann, vZome example (2006), see link above.

## 3D Viewers

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="grand_antiprism_ring_first.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    grand_antiprism_ring_first.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="grand_antiprism_vertex_first.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    grand_antiprism_vertex_first.vZome
 </figcaption>
</figure>

