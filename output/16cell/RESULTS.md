# 16-cell (orthoplex) → 3D zomeable orthographic projections

**Result: exactly 6 distinct shapes.**

The 16-cell has 8 vertices `±e_i` and 24 edges (between every pair of
non-antipodal vertices).  Edges are NOT axis-parallel (each has 2 nonzero
components), so the alignment constraint is much tighter than for the
tesseract — and the search saturates.

## Saturation evidence

| rng | candidate directions | hits | distinct shapes |
|-----|----------------------|------|-----------------|
| 2   | 1,819                | 46   | **6**           |
| 3   | 20,474               | 92   | **6**           |
| 4   | 135,750              | 154  | **6**           |

Same 6 shapes at every range tested — confidently saturated empirically.
(See `..\docs\METHODOLOGY.md` for caveats about empirical-vs-formal
saturation.)

## The 6 shapes

| # | Balls | Edge signature             | Geometry            | Example kernel n           |
|---|-------|----------------------------|---------------------|----------------------------|
| 1 | 8     | B:6,  R:12, Y:6            | square antiprism A  | (√5, 1, 1, 1)              |
| 2 | 7     | B:12, G:12                 | **octahedron + center** (vertex-first) | (1, 0, 0, 0) |
| 3 | 6     | B:6,  Y:16, (2 collapsed)  | **octahedron**      | (1, 1, 0, 0)               |
| 4 | 8     | B:6,  R:12, Y:6            | square antiprism B  | (φ²·1.618, φ²·1.618, φ²·1.618, φ⁻¹) |
| 5 | 8     | B:12, G:12                 | **cube** (cell-first) | (1, 1, 1, 1)             |
| 6 | 8     | B:6,  R:12, Y:6            | square antiprism C  | (φ³·1.382·..., 1.382, 1.382, 1.382) |

**Notes on the three "square antiprism" shapes:**  they have identical
edge color signatures `{B:6, R:12, Y:6}` but different rotation+scale-
invariant pairwise-distance fingerprints — i.e. different aspect ratios
arising from projection along the three icosahedral-axis classes
(2-fold, 3-fold, 5-fold) that correspond to the 16-cell's tetrahedral/D4
sub-symmetries.

These three shapes are the well-known **D₄ triality** of the 16-cell:
the three orbits of `2(1+i)·I` (where `I` = binary icosahedral group) under
the D₄ outer automorphism, all giving 16-cell projections with identical
strut counts (8 connectors, 6 R1 + 6 R2 + 6 Y2 + 6 B2 = 24 struts) but
distinct geometries. This matches the construction described at
<https://polytopologist.github.io/zome_pages/zometriality.htm>, which
also notes that truncating any one of the three to its edge midpoints
yields the same 24-cell zometool model — independent confirmation that
these correspond to our `24cell_triality.vZome` projection.

## The "standard" projections

- **Vertex-first** (`n = e_i`): kernel is one axis vertex; image is a
  centered octahedron (shape 2).
- **Cell-first** (`n = (1,1,1,1)`): kernel is the centroid of a tetrahedral
  cell; image is a cube (shape 5).
- **Edge-first** (`n = (1,1,0,0)`): kernel is along an edge midpoint;
  image is a flattened octahedron (shape 3).
- Three additional shapes arise from "icosahedral-coupling" directions
  (use of φ in the kernel) that the H₄ symmetry of zometool admits.

## Reproduction

```bash
cd regular_4polytopes\lib
python run_search.py 16cell 3
```

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/16cell/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).




<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="16cell_antiprism_B6R12Y6.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    16cell_antiprism_B6R12Y6.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="16cell_antiprism_R12B6Y6.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    16cell_antiprism_R12B6Y6.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="16cell_antiprism_Y6R12B6.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    16cell_antiprism_Y6R12B6.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="16cell_cell_first_cube.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    16cell_cell_first_cube.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="16cell_edge_first_squashed_octahedron.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    16cell_edge_first_squashed_octahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="16cell_vertex_first_octahedron.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    16cell_vertex_first_octahedron.vZome
 </figcaption>
</figure>

