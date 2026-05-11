# runcinated 120-cell → zomeable orthographic projections

- Coxeter group: **H4**, Wythoff bitmask: **(1,0,0,1)**
- Vertices: **2400**, edges: **7200**
- Folder: `output/runcinated_120cell/`

**1 distinct zomeable shape** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `runcinated_120cell_cell_first_dodecahedron.vZome` | cell_first / dodecahedron | 1260 | `4bd3daf2ff` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "runcinated 120-cell"`).

## 3D Viewers

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="runcinated_120cell_cell_first_dodecahedron.vZome" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    runcinated_120cell_cell_first_dodecahedron.vZome
 </figcaption>
</figure>

