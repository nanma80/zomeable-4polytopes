# bitruncated 5-cell → zomeable orthographic projections

- Coxeter group: **A4**, Wythoff bitmask: **(0,1,1,0)**
- Vertices: **30**, edges: **60**
- Folder: `output/bitruncated_5cell/`

**4 distinct zomeable shapes** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `bitruncated_5cell_cell_first_truncated_tetrahedron.vZome` | cell_first / truncated_tetrahedron | 30 | `467bb01461` |
| `bitruncated_5cell_face_first_hexagon.vZome` | face_first / hexagon | 18 | `be9338e636` |
| `bitruncated_5cell_oblique_00.vZome` | oblique | 30 | `190a7b1c71` |
| `bitruncated_5cell_oblique_01.vZome` | oblique | 30 | `9e2d21191f` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "bitruncated 5-cell"`).

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/bitruncated_5cell/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).



<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="bitruncated_5cell_cell_first_truncated_tetrahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    bitruncated_5cell_cell_first_truncated_tetrahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="bitruncated_5cell_face_first_hexagon.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    bitruncated_5cell_face_first_hexagon.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="bitruncated_5cell_oblique_00.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    bitruncated_5cell_oblique_00.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="bitruncated_5cell_oblique_01.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    bitruncated_5cell_oblique_01.vZome
 </figcaption>
</figure>

