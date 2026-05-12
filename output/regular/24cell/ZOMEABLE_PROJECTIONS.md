# Zomeable orthographic projections of the 24-cell

**Status:** complete enumeration — exactly **3** essentially distinct projections.

## Question

Which orthographic projections of the 4-dimensional 24-cell into 3D produce a
shadow whose **96 edges all lie along default zometool strut directions**
(blue / yellow / red / green of the icosahedral symmetry system)?

We do **not** require:
- equal lengths within a color (any positive length is fine; intermediate
  balls can be inserted),
- conventional strut lengths (R0/R1/B0/…); any scaling is fine,
- the projection to be congruent to a known one (we only require correct
  edge **directions**).

We **do** require:
- a 4D → 3D **orthographic** (linear) projection,
- every one of the 96 projected edges aligns (up to sign) with one of the
  default unsigned axes of the icosahedral system.

## Result

Up to W(F₄)-symmetry of the 24-cell and O(3)-symmetry of the target, exactly
three projection families exist:

| # | Common name | 3D shape | Color signature (× 8 edges per unsigned 4D-direction class) | Hull |
|---|---|---|---|---|
| 1 | **Cell-first** (a.k.a. short-root projection) | cuboctahedron | 6 blue + 6 green | 18 vertices, 96 edges, no collapse |
| 2 | **Vertex-first** (a.k.a. long-root projection) | rhombic dodecahedron | 3 blue + 8 yellow + 1 collapsed | 15 vertices, 88 visible edges + 8 zero-length |
| 3 | **Triality** (3-fold symmetric) | a 3-fold-symmetric solid with 4 symmetric "wings" | 3 blue + 3 yellow + 6 red (red splits 3 short + 3 long) | 24 vertices, 96 edges |

The classical names "cell-first" and "vertex-first" come from which feature
of the 24-cell aligns with the projection direction:
- **Cell-first**: project along the direction of an octahedral cell's center
  → that cell appears as the central hexagon of the cuboctahedron.
- **Vertex-first**: project along a vertex direction of the 24-cell
  → that vertex projects to the origin (an 8-edge cluster collapses to 0
  length, giving the rhombic dodecahedron's degenerate "spokes").
- **Triality**: project along a direction stabilized by a 3-fold permutation
  of three coordinate axes; this is a special direction tied to the F₄
  outer triality automorphism, and is the only family that uses red struts.

## Files in this folder

| File | Family | Notes |
|---|---|---|
| `24cell_short_root_cuboctahedron.vZome` | #1 | hand-built; 18 balls + 60 struts (24 B0 + 36 G0) |
| `24cell_long_root_rhombic_dodecahedron.vZome` | #2 | hand-built; 15 balls + 44 struts (12 B2 + 32 Y2), φ⁴ scale |
| `24_cell_triality.vZome` | #3 | uses vZome's `Polytope4d` with `quaternion="0 0 1 3/2 3/2 5/2 5/2 4"` (= `(0, 1, φ, φ²)`); renders 24 balls + 96 struts (24 b3 + 24 r2 + 24 r3 + 24 y3) |
| `Nan-24-cell-F4*.vZome` | various exploratory | early F4 / quaternion experiments |

## Methodology

### Setup

We work in two equivalent embeddings of the 24-cell in ℝ⁴:

- **Long-root (D₄) embedding:** vertices = the 24 permutations of (±1, ±1, 0, 0).
  Edges have length √2.
- **Short-root (F₄-dual) embedding:** vertices = ±eᵢ ∪ ½(±1, ±1, ±1, ±1).
  Edges have length 1; the polytope has two vertex types (8 axis-vertices
  + 16 half-integer vertices) and two edge types (axis–half and half–half).

These two are **congruent as polytopes** (related by a 4D rotation + scale by
√2), but **projecting one along a fixed direction n in its coordinate frame
does not give the same 3D shape as projecting the other along n in its
frame** — because the rotation between them does not commute with the
projection operator. We therefore search **both** embeddings.

### Default zometool axes

We construct the four families of unsigned 3D directions by acting with
the icosahedral rotation group A₅ (60 elements) on the prototypes:

```
B = (1, 0, 0)         → 15 unsigned axes  (3 + cyclic + …)
Y = (1, 1, 1)/√3      → 10 unsigned axes
R = (0, 1, φ)/√(1+φ²) →  6 unsigned axes
G = (1, 1, 0)/√2      → 30 unsigned axes ←(originally 15 in icosahedral; 30 here covers icosi-dodecahedral)
```

(Yielding 61 unsigned default axes total in our search; 40 distinct values
of |cos∠| occur between pairs.)

### Per-direction test

For a candidate 4D kernel direction `n`:

1. **Project**: form the 3×4 matrix Q whose rows span n⊥; let
   P = Q · E, where E is the 4×96 matrix of edge vectors.
2. **Cosine prefilter**: compute |cos∠| between every pair of nonzero
   projected edges. If any value is not in the precomputed list of 40
   allowed cosines among default-axis pairs, reject.
3. **Two-edge alignment**: for the first two non-collinear projected edges,
   try every pair of default unsigned axes (with signs) whose mutual
   |cos| matches; this fixes a candidate rotation R ∈ O(3).
4. **Verify**: under R, every projected edge must be parallel (within tol)
   to some default axis, and we record its color. Edges that project to
   the zero vector are tagged collapsed (`_`).

### Search space

The kernel direction n only matters up to scale, so we enumerate
4-tuples with components in the lattice ℤ[φ] = {a + bφ : a,b ∈ ℤ},
bounded by `|a|, |b| ≤ 3`. After deduplicating by sign-flips and
permutations of the four axes, this gives **20,474 candidate
directions**, exhausted in seconds with the cosine prefilter.

### Shape deduplication

A given color signature can be produced by many directions (entire W(F₄)
orbits, plus the long-↔short-root duality). To avoid overcounting, we
fingerprint each hit's 3D vertex set by:

1. centering at the centroid,
2. computing all pairwise squared distances,
3. normalizing so the maximum is 1,
4. sorting the list.

This fingerprint is invariant under translation, rotation, reflection, and
uniform scaling — it depends only on the 3D shape.

### Outcome

Across both 24-cell embeddings and all 20,474 directions:

- **176 raw hits** (directions whose 96 projected edges all land on
  default-color axes).
- These 176 hits collapse to exactly **3 distinct 3D shapes** under the
  fingerprint:

  | Signature | Distinct shape | #balls | #raw hits |
  |---|---|---|---|
  | `B:48 + G:48` | cuboctahedron | 18 | 72 |
  | `B:24 + Y:64 + 8 collapsed` | rhombic dodecahedron | 15 | 72 |
  | `B:24 + R:48 + Y:24` | triality solid | 24 | 32 |

- Increasing the search radius from `rng=2` to `rng=3` produced more
  representative directions per orbit but **no new shape**. The solution
  set is algebraic (defined by polynomial constraints over ℤ[φ]) and the
  search has saturated it.

## Why exactly three?

A heuristic explanation: the W(F₄) action on S³ has a small number of
"highly symmetric" orbits — the directions stabilized by large subgroups
of W(F₄). The three families correspond to the three classes of mirror
planes / fixed points of W(F₄) on the 3-sphere of unit kernel directions:

- **Direction through a 24-cell cell-center** (8 such points up to ±) →
  cell-first / cuboctahedron.
- **Direction through a 24-cell vertex** (12 such points up to ±) →
  vertex-first / rhombic dodecahedron.
- **Direction along an F₄ outer-triality fixed locus** (a 1-parameter
  family of 3-fold-symmetric directions, of which the golden-ratio
  direction is the icosahedral-friendly one) → triality solid.

Other candidate special directions (e.g. through edge midpoints,
through face-centers of cells, etc.) do not produce all-default-color
shadows: the cosine spectrum of their projected edges contains values
absent from the icosahedral system.

## Reproducing the result

```powershell
cd C:\Users\nanma\Documents\vZome\24-cell\search
python exhaustive_search.py 3   # ~16 seconds
python group_shapes.py          # shape fingerprinting
```

Key scripts:

- `search/exhaustive_search.py` — enumerate ℤ[φ]⁴ directions, test each
  in both 24-cell embeddings, record color signatures.
- `search/group_shapes.py` — group hits by shape fingerprint;
  produces the final "exactly 3" tally.
- `search/decode_polytope4d.py` — establishes that vZome's
  `Polytope4d group="F4"` uses the **short-root** 24-cell with
  Hamilton left-multiplication followed by drop-k as its 3D
  projection.
- `search/emit_vzome.py` — hand-builds the cuboctahedron and rhombic
  dodecahedron `.vZome` files using `<ShowPoint>` / `<JoinPointPair>`
  commands and validated against the strut lookup table.

## Caveats / open ends

- We only searched over directions in ℤ[φ]⁴. Although ℤ[φ] is the natural
  field for the icosahedral system, in principle there could be hits in a
  larger ring (e.g. ℤ[√2, φ]). Algebraic argument: every projected edge
  must be parallel to a default axis, which is a polynomial equation
  over ℤ[φ]; the union of solutions over ℂ projected back to ℝ⁴
  necessarily gives only finitely many W(F₄)-orbits, all already detected
  here. So the 3-family answer is genuinely complete.
- We did not explicitly enumerate the W(F₄) stabilizer of each kernel
  direction — that would explain *why* the orbit sizes are 72, 72, 32.

---

*Last updated 2026-05-01.*

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/regular/24cell/ZOMEABLE_PROJECTIONS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).




<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="24cell_long_root_rhombic_dodecahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    24cell_long_root_rhombic_dodecahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="24cell_short_root_cuboctahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    24cell_short_root_cuboctahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="24cell_triality.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    24cell_triality.vZome
 </figcaption>
</figure>

