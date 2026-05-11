# bitruncated tesseract → zomeable orthographic projections

- Coxeter group: **B4**, Wythoff bitmask: **(0,1,1,0)**
- Vertices: **96**, edges: **192**
- Folder: `output/bitruncated_8cell/`

**6 distinct zomeable shapes** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `bitruncated_8cell_cell_first_truncated_octahedron.vZome` | cell_first / truncated_octahedron | 60 | `aceab99c00` |
| `bitruncated_8cell_cell_first_truncated_tetrahedron.vZome` | cell_first / truncated_tetrahedron | 96 | `3c7ea12f56` |
| `bitruncated_8cell_face_first_square.vZome` | face_first / square | 52 | `40be7cc1d7` |
| `bitruncated_8cell_oblique_00.vZome` | oblique | 96 | `26f0b7c6e6` |
| `bitruncated_8cell_oblique_01.vZome` | oblique | 96 | `df821cc628` |
| `bitruncated_8cell_oblique_02.vZome` | oblique | 96 | `80a961d9da` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "bitruncated tesseract"`).

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).


<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="bitruncated_8cell_cell_first_truncated_octahedron.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    bitruncated_8cell_cell_first_truncated_octahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="bitruncated_8cell_cell_first_truncated_tetrahedron.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    bitruncated_8cell_cell_first_truncated_tetrahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="bitruncated_8cell_face_first_square.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    bitruncated_8cell_face_first_square.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="bitruncated_8cell_oblique_00.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    bitruncated_8cell_oblique_00.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="bitruncated_8cell_oblique_01.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    bitruncated_8cell_oblique_01.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="bitruncated_8cell_oblique_02.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    bitruncated_8cell_oblique_02.vZome
 </figcaption>
</figure>

