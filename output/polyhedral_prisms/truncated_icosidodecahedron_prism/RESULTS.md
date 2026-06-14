# truncated icosidodecahedron prism → zomeable orthographic projections

- Family **A** (polyhedral prism)
- 4D vertices: **240**, edges: **480**
- Folder: `output/polyhedral_prisms/truncated_icosidodecahedron_prism/`

**5 distinct zomeable shapes** found (rng = 4 agnostic kernel sweep).

## Shapes

| # | File | Label / direction | n_balls | Struts |
|---|------|-------------------|--------:|--------|
| 1 | `oblique_00.vZome` | oblique | 240 | B:120  R:240  Y:120 |
| 2 | `cell_first_cube.vZome` | cell_first / cube | 120 | B:84  R:96  Y:48 |
| 3 | `oblique_01.vZome` | oblique | 240 | B:120  R:240  Y:120 |
| 4 | `oblique_02.vZome` | oblique | 240 | B:72  R:144  Y:264 |
| 5 | `cell_first_truncated_icosidodecahedron.vZome` | cell_first / truncated_icosidodecahedron | 120 | B:180 |

## Provenance

- Sweep driver: `tools/run_prismatic_sweep.py --family A --rng 4`
- Construction: `lib/polytopes_prismatic.py` + `lib/uniform_polyhedra.py`
- See [`docs/PRISMATIC.md`](../../../docs/PRISMATIC.md) for the full prismatic-family taxonomy and sweep summary.

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/polyhedral_prisms/truncated_icosidodecahedron_prism/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).

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
 <vzome-viewer src="oblique_00.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    oblique_00.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="cell_first_cube.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    cell_first_cube.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="oblique_01.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    oblique_01.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="oblique_02.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    oblique_02.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="cell_first_truncated_icosidodecahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    cell_first_truncated_icosidodecahedron.vZome
 </figcaption>
</figure>

