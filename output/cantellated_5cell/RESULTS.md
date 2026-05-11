# cantellated 5-cell → zomeable orthographic projections

- Coxeter group: **A4**, Wythoff bitmask: **(1,0,1,0)**
- Vertices: **30**, edges: **90**
- Folder: `output/cantellated_5cell/`

**4 distinct zomeable shapes** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `cantellated_5cell_cell_first_octahedron.vZome` | cell_first / octahedron | 30 | `e1d5c7a081` |
| `cantellated_5cell_face_first_square.vZome` | face_first / square | 30 | `a6537a898e` |
| `cantellated_5cell_oblique_00.vZome` | oblique | 30 | `1c346b0e6a` |
| `cantellated_5cell_oblique_01.vZome` | oblique | 18 | `e7d00a6967` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "cantellated 5-cell"`).

## 3D Viewers

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cantellated_5cell_cell_first_octahedron.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cantellated_5cell_cell_first_octahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cantellated_5cell_face_first_square.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cantellated_5cell_face_first_square.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cantellated_5cell_oblique_00.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cantellated_5cell_oblique_00.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cantellated_5cell_oblique_01.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cantellated_5cell_oblique_01.vZome
 </figcaption>
</figure>

