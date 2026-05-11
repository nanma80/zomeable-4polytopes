# 600-cell → 3D zomeable orthographic projections

**Result: exactly 1 distinct shape.**

The 600-cell has 120 vertices and 720 edges, with H₄ symmetry.  Under
orthographic projection to 3D, all valid default-color projections give
the same shape: a **75-vertex H₃-symmetric polytope** with edge color
signature **{R: 288, B: 180, Y: 240}** (12 of the 720 edges collapse).

This is the famous H₄→H₃ "icosahedral projection" of the 600-cell.

## Saturation

| rng | candidate directions | hits | distinct shapes |
|-----|----------------------|------|-----------------|
| 2   | 1,819                | 30   | **1**           |
| 3   | 20,474               | 60   | **1**           |
| 4   | 135,750              | 100  | **1**           |

Stable at 1 shape.  All hits represent ℤ[φ]⁴ lattice points on a
single orbit under the H₄ symmetry of the 600-cell.

## The shape

- 75 balls in 3D (H₃-symmetric arrangement: outer + middle + inner shells).
- 708 default-color struts: 288 red + 240 yellow + 180 blue.
- 12 edges of the 600-cell project to length-zero (interior coincidences).

Example kernel direction: `n = (1, 0, 0, 0)` (vertex-first projection)
or `n = (1, 1, 1, 1)` (cell-first); both give the same image up to 3D
rotation.

## Methodology note

This polytope provoked a fingerprint-stability bug in the search
infrastructure: numerically scaled-equivalent kernel directions can
produce 3D images that differ by a 3D rotation arising from SVD basis
ambiguity (degenerate singular values).  The fix was to use a more
generous tolerance in vertex deduplication (1e-3 instead of 1e-5)
when computing the rotation+scale-invariant fingerprint.

After the fix, 600-cell saturates cleanly at 1 shape.

## Reproduction

```bash
cd regular_4polytopes\lib
python run_search.py 600cell 3
```

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/600cell/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).




<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="600cell_H4_to_H3.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    600cell_H4_to_H3.vZome
 </figcaption>
</figure>

