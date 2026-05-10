# rectified 600-cell → zomeable orthographic projections

- Coxeter group: **H4**, Wythoff bitmask: **(0,0,1,0)**
- Vertices: **720**, edges: **3600**
- Folder: `output/rectified_600cell/`

**1 distinct zomeable shape** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `rectified_600cell_cell_first_icosahedron.vZome` | cell_first / icosahedron | 396 | `e690959a51` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "rectified 600-cell"`).
