# rectified 5-cell → zomeable orthographic projections

- Coxeter group: **A4**, Wythoff bitmask: **(0,1,0,0)**
- Vertices: **10**, edges: **30**
- Folder: `output/rectified_5cell/`

**4 distinct zomeable shapes** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `rectified_5cell_cell_first_tetrahedron.vZome` | cell_first / tetrahedron | 10 | `18db22bc8b` |
| `rectified_5cell_oblique_00.vZome` | oblique | 10 | `4fe32006bf` |
| `rectified_5cell_oblique_01.vZome` | oblique | 7 | `55abe81889` |
| `rectified_5cell_oblique_02.vZome` | oblique | 10 | `c2ff97e546` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "rectified 5-cell"`).

## 3D Viewers

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="rectified_5cell_cell_first_tetrahedron.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    rectified_5cell_cell_first_tetrahedron.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="rectified_5cell_oblique_00.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    rectified_5cell_oblique_00.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="rectified_5cell_oblique_01.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    rectified_5cell_oblique_01.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="rectified_5cell_oblique_02.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    rectified_5cell_oblique_02.vZome
 </figcaption>
</figure>

