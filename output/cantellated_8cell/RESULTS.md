# cantellated tesseract → zomeable orthographic projections

- Coxeter group: **B4**, Wythoff bitmask: **(1,0,1,0)**
- Vertices: **96**, edges: **288**
- Folder: `output/cantellated_8cell/`

**No zomeable orthographic projection exists** for this polytope under the icosahedral-axis (`ℤ[φ]³`) snap criterion at rng ≤ 4.

The search engine found candidate kernel directions whose projected edges all aligned with default zometool axes (criterion 1, *zometool-axis-aligned*), but the resulting vertex coordinates lie in a field strictly larger than `ℤ[φ]³` — typically `ℤ[√2]³` for the `B₄`/`F₄` snap-fail family — so they fail criterion 2 (*vZome-embeddable in the icosahedral field*).

See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) (sections *Two notions of zomeable* and *Wythoff-extension shape inventory*) for the structural reason this happens, and [`output/8cell/CLASSIFICATION.md`](../8cell/CLASSIFICATION.md) for the `ℤ[φ, √n]³` field-boundary discussion that generalises to every `B₄`/`F₄` snap-fail case.

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "cantellated tesseract"`).
