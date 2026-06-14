# 120-cell → 3D zomeable orthographic projections

**Result (preliminary, rng=2): exactly 1 distinct shape.**

The 120-cell has 600 vertices and 1200 edges, with H₄ symmetry.  At
search range rng=2 we find one valid projection class:

- **330 balls** in 3D
- Edge color signature: **{R: 480, Y: 400, B: 300}** (20 of 1200 edges
  collapse).
- Example kernel: `n = (1, 1, 1, 1)` (cell-first projection, equivalent
  to projecting along a vertex of the dual 600-cell).

This is the H₄→H₃ "icosahedral projection" of the 120-cell.  Combined
with the 600-cell (which gives a 75-vertex H₃-symmetric solid), this
fits the standard pattern: H₄ polytopes have a canonical projection
into H₃-symmetric 3D zonohedra.

## Saturation

| rng | candidate directions | hits | distinct shapes |
|-----|----------------------|------|-----------------|
| 2   | 1,819                | 24   | **1**           |
| 3   | 20,474               | TBD  | TBD             |

rng=3 in progress; will update.

## Reproduction

```bash
cd regular_4polytopes\lib
python run_search.py 120cell 2
```

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/regular/120cell/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).




<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>


<style>
  .vzome-card {
    box-sizing: border-box;
    border: 1px solid #ddd;
    border-radius: 0.5rem;
    padding: 0.25rem;
    background: #fff;
    max-width: min(100%, 72dvh);
    margin: 2rem auto;
    width: 100%;
  }
  .vzome-card vzome-viewer {
    display: block;
    width: 100%;
    aspect-ratio: 1 / 1;
    height: auto;
  }
  .vzome-card figcaption {
    margin: 0.75rem 0 0.5rem;
    color: #555;
    text-align: center;
    font-style: italic;
  }
</style>

<figure class="vzome-card">
 <vzome-viewer src="120cell_H4_to_H3.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    120cell_H4_to_H3.vZome
 </figcaption>
</figure>

