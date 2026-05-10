# runcinated 24-cell → zomeable orthographic projections

- Coxeter group: **F4**, Wythoff bitmask: **(1,0,0,1)**
- Vertices: **144**, edges: **576**
- Folder: `output/runcinated_24cell/`

**No zomeable orthographic projection exists** for this polytope under the icosahedral-axis (`ℤ[φ]³`) snap criterion at rng ≤ 4.  The search engine found candidate kernel directions whose projected edges all aligned with default zometool axes (criterion 1, *zometool-axis aligned*), but the resulting vertex coordinates lie in a field strictly larger than `ℤ[φ]³` (typically `ℤ[√2]³` for `B₄`/`F₄` shapes) — i.e., they fail criterion 2, *vZome-embeddable*.

See the snap-failure analysis in [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md#wythoff-extension-shape-inventory-rng--2-full-47-of-47-polytope-records) for the structural reason this happens, and `output/8cell/CLASSIFICATION.md` for the `Z[φ, √n]³` field-boundary discussion (which generalises to all `B₄`/`F₄` snap-fail cases).

## Provenance

- Search driver: `tools/run_wythoff_sweep.py` (rng = 2 production sweep).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}; see `docs/INHERITANCE_FREE_SWEEP.md`).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search for `"source_polytope": "runcinated 24-cell"`).
