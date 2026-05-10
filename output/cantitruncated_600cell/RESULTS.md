# cantitruncated 600-cell → zomeable orthographic projections

- Coxeter group: **H4**, Wythoff bitmask: **(0,1,1,1)**
- Vertices: **7224**, edges: **14508**
- Folder: `output/cantitruncated_600cell/`

**1 distinct zomeable shape** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `cantitruncated_600cell_cell_first_truncated_icosahedron.vZome` | cell_first / truncated_icosahedron | 3660 | `1dd1965c7d` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "cantitruncated 600-cell"`).
