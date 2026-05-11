# rectified 24-cell → zomeable orthographic projections

- Coxeter group: **F4**, Wythoff bitmask: **(0,1,0,0)**
- Vertices: **96**, edges: **288**
- Folder: `output/rectified_24cell/`
- Includes shapes filed under both `F₄ (0,1,0,0) = rectified 24-cell` and the equivalent `B₄ (0,1,0,1) = cantellated 16-cell` — they are the same uniform polytope (see `docs/WYTHOFF_SWEEP.md §Equivalences (B₄/F₄ overlap)`).

**3 distinct zomeable shapes** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `rectified_24cell_cell_first_cube.vZome` | cell_first / cube | 52 | `cca712ec6e` |
| `rectified_24cell_cell_first_cuboctahedron.vZome` | cell_first / cuboctahedron | 60 | `5452b20702` |
| `rectified_24cell_oblique.vZome` | oblique | 96 | `56093e7cd7` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "rectified 24-cell"`).

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/rectified_24cell/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).



<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="rectified_24cell_cell_first_cube.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    rectified_24cell_cell_first_cube.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="rectified_24cell_cell_first_cuboctahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    rectified_24cell_cell_first_cuboctahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="rectified_24cell_oblique.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    rectified_24cell_oblique.vZome
 </figcaption>
</figure>

