# truncated 16-cell → zomeable orthographic projections

- Coxeter group: **B4**, Wythoff bitmask: **(0,0,1,1)**
- Vertices: **48**, edges: **120**
- Folder: `output/uniform/truncated_16cell/`

**6 distinct zomeable shapes** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `truncated_16cell_cell_first_octahedron.vZome` | cell_first / octahedron | 36 | `bb5b56af58` |
| `truncated_16cell_cell_first_truncated_tetrahedron.vZome` | cell_first / truncated_tetrahedron | 48 | `bebffceea5` |
| `truncated_16cell_edge_first.vZome` | edge_first | 28 | `30ce845d3f` |
| `truncated_16cell_oblique_00.vZome` | oblique | 48 | `9d18eb2806` |
| `truncated_16cell_oblique_01.vZome` | oblique | 48 | `ccdfd208c9` |
| `truncated_16cell_oblique_02.vZome` | oblique | 48 | `2c50f047a8` |

Each `.vZome` document records the projected 3D balls and struts for a specific
kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for
the master taxonomy, the search methodology, and the per-shape strut counts
(B/Y/R/G zometool axes).

## Hidden-cell removal prototype

A derived front-visible set is available in
[`../truncated_16cell_hidden_cells/`](../truncated_16cell_hidden_cells/).
Those models are filtered copies of the full projections: they keep the same
ball/strut coordinates and remove only elements belonging solely to cells hidden
from the positive side of the projection kernel.

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "truncated 16-cell"`).

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/uniform/truncated_16cell/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).



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
 <vzome-viewer src="truncated_16cell_cell_first_octahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    truncated_16cell_cell_first_octahedron.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="truncated_16cell_cell_first_truncated_tetrahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    truncated_16cell_cell_first_truncated_tetrahedron.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="truncated_16cell_edge_first.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    truncated_16cell_edge_first.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="truncated_16cell_oblique_00.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    truncated_16cell_oblique_00.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="truncated_16cell_oblique_01.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    truncated_16cell_oblique_01.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="truncated_16cell_oblique_02.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    truncated_16cell_oblique_02.vZome
 </figcaption>
</figure>
