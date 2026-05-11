# cantitruncated 5-cell → zomeable orthographic projections

- Coxeter group: **A4**, Wythoff bitmask: **(1,1,1,0)**
- Vertices: **60**, edges: **120**
- Folder: `output/cantitruncated_5cell/`

**4 distinct zomeable shapes** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `cantitruncated_5cell_cell_first_truncated_tetrahedron.vZome` | cell_first / truncated_tetrahedron | 60 | `6a8e448e70` |
| `cantitruncated_5cell_oblique_00.vZome` | oblique | 60 | `6189be49ed` |
| `cantitruncated_5cell_oblique_01.vZome` | oblique | 33 | `befb910d19` |
| `cantitruncated_5cell_oblique_02.vZome` | oblique | 60 | `c1635833bd` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "cantitruncated 5-cell"`).

## 3D Viewers

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cantitruncated_5cell_cell_first_truncated_tetrahedron.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cantitruncated_5cell_cell_first_truncated_tetrahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cantitruncated_5cell_oblique_00.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cantitruncated_5cell_oblique_00.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cantitruncated_5cell_oblique_01.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cantitruncated_5cell_oblique_01.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cantitruncated_5cell_oblique_02.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cantitruncated_5cell_oblique_02.vZome
 </figcaption>
</figure>

