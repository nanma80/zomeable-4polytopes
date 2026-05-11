# runcitruncated 5-cell → zomeable orthographic projections

- Coxeter group: **A4**, Wythoff bitmask: **(1,1,0,1)**
- Vertices: **60**, edges: **150**
- Folder: `output/runcitruncated_5cell/`

**4 distinct zomeable shapes** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `runcitruncated_5cell_cell_first_cuboctahedron.vZome` | cell_first / cuboctahedron | 60 | `8fb8506b88` |
| `runcitruncated_5cell_edge_first.vZome` | edge_first | 60 | `e203af4fe0` |
| `runcitruncated_5cell_face_first_triangle.vZome` | face_first / triangle | 33 | `a98cfbe1f2` |
| `runcitruncated_5cell_oblique.vZome` | oblique | 60 | `db7b74a33d` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "runcitruncated 5-cell"`).

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/runcitruncated_5cell/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).



<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="runcitruncated_5cell_cell_first_cuboctahedron.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    runcitruncated_5cell_cell_first_cuboctahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="runcitruncated_5cell_edge_first.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    runcitruncated_5cell_edge_first.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="runcitruncated_5cell_face_first_triangle.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    runcitruncated_5cell_face_first_triangle.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="runcitruncated_5cell_oblique.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    runcitruncated_5cell_oblique.vZome
 </figcaption>
</figure>

