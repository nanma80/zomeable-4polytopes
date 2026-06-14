# truncated tetrahedron prism → zomeable orthographic projections

- Family **A** (polyhedral prism)
- 4D vertices: **24**, edges: **48**
- Folder: `output/polyhedral_prisms/truncated_tetrahedron_prism/`

**2 distinct zomeable shapes** found (rng = 4 agnostic kernel sweep).

## Shapes

| # | File | Label / direction | n_balls | Struts |
|---|------|-------------------|--------:|--------|
| 1 | `face_first_square.vZome` | face_first / square | 24 | B:24  G:24 |
| 2 | `cell_first_truncated_tetrahedron.vZome` | cell_first / truncated_tetrahedron | 12 | G:18 |

## Provenance

- Sweep driver: `tools/run_prismatic_sweep.py --family A --rng 4`
- Construction: `lib/polytopes_prismatic.py` + `lib/uniform_polyhedra.py`
- See [`docs/PRISMATIC.md`](../../../docs/PRISMATIC.md) for the full prismatic-family taxonomy and sweep summary.

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/polyhedral_prisms/truncated_tetrahedron_prism/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).

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
 <vzome-viewer src="face_first_square.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    face_first_square.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="cell_first_truncated_tetrahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    cell_first_truncated_tetrahedron.vZome
 </figcaption>
</figure>

