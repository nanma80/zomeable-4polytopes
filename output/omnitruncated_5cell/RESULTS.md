# omnitruncated 5-cell → zomeable orthographic projections

- Coxeter group: **A4**, Wythoff bitmask: **(1,1,1,1)**
- Vertices: **120**, edges: **240**
- Folder: `output/omnitruncated_5cell/`

**4 distinct zomeable shapes** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `omnitruncated_5cell_cell_first_truncated_octahedron.vZome` | cell_first / truncated_octahedron | 96 | `94c404ee6a` |
| `omnitruncated_5cell_face_first_hexagon.vZome` | face_first / hexagon | 60 | `c94790ed91` |
| `omnitruncated_5cell_face_first_square.vZome` | face_first / square | 120 | `9f73b85175` |
| `omnitruncated_5cell_oblique.vZome` | oblique | 120 | `9f354d53ae` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "omnitruncated 5-cell"`).
