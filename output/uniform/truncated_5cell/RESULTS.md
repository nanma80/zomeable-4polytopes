# truncated 5-cell → zomeable orthographic projections

- Coxeter group: **A4**, Wythoff bitmask: **(1,1,0,0)**
- Vertices: **20**, edges: **40**
- Folder: `output/uniform/truncated_5cell/`

**4 distinct zomeable shapes** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `truncated_5cell_cell_first_tetrahedron.vZome` | cell_first / tetrahedron | 20 | `82123904b0` |
| `truncated_5cell_oblique_00.vZome` | oblique | 20 | `7df137dba4` |
| `truncated_5cell_oblique_01.vZome` | oblique | 20 | `9fee63fe24` |
| `truncated_5cell_oblique_02.vZome` | oblique | 13 | `cd65b76a7d` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "truncated 5-cell"`).

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/uniform/truncated_5cell/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).



<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="truncated_5cell_cell_first_tetrahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    truncated_5cell_cell_first_tetrahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="truncated_5cell_oblique_00.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    truncated_5cell_oblique_00.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="truncated_5cell_oblique_01.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    truncated_5cell_oblique_01.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="truncated_5cell_oblique_02.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    truncated_5cell_oblique_02.vZome
 </figcaption>
</figure>

