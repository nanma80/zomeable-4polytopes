# zomeable-4polytopes

Enumeration of orthographic projections of uniform 4-polytopes whose every
projected edge lies on a default-color [zometool](https://www.zometool.com/)
axis (B / Y / R / G in the icosahedral system) — i.e., projections that can
be physically built with zometool, and modeled exactly in
[vZome](https://vzome.com/).

For each polytope `P` we search kernel directions `n ∈ ℤ[φ]⁴`, project
`P → ℝ³` via `Q = I − n nᵀ/|n|²`, and keep those projections whose edge set
aligns with default zome axes. Hits are then grouped by a
rotation-and-uniform-scale-invariant fingerprint to count distinct 3D shapes.

## Results

| Polytope                      | Verts | Edges | Distinct zomeable shapes              |
|-------------------------------|-------|-------|---------------------------------------|
| 5-cell `{3,3,3}`              | 5     | 10    | **4** (saturated rng=3)               |
| 8-cell `{4,3,3}`              | 16    | 32    | **1 infinite family + 2 sporadic** ¹  |
| 16-cell `{3,3,4}`             | 8     | 24    | **6** (saturated rng=4)               |
| 24-cell `{3,4,3}`             | 24    | 96    | **3** (saturated rng=3)               |
| 120-cell `{5,3,3}`            | 600   | 1200  | **1** (saturated rng=4)               |
| 600-cell `{3,3,5}`            | 120   | 720   | **1** (saturated rng=4)               |
| Snub 24-cell                  | 96    | 432   | **2** (cell-first Tₕ, vertex-first D₃d) |
| Grand antiprism               | 100   | 500   | **2** (vertex-first D₂ₕ, ring-first D₅d) |

¹ The 8-cell infinite family is parametrized by integer pairs `(a,b)`
producing distinct rectangular cuboids. Two additional sporadic shapes
exist on zometool but are not vZome-embeddable. See
[`output/8cell/CLASSIFICATION.md`](output/8cell/CLASSIFICATION.md).

Per-polytope writeups live in `output/<polytope>/RESULTS.md` (or
`CLASSIFICATION.md` for 8-cell, `ZOMEABLE_PROJECTIONS.md` for 24-cell).

## Layout

```
zomeable-4polytopes/
├── lib/                     core search + emitter library
│   ├── polytopes.py             vertex/edge specs for all 8 polytopes
│   ├── search_engine.py         kernel-direction search
│   ├── run_search.py            CLI: run search for one polytope
│   ├── emit_generic.py          generic <Polytope4d>-based emitter
│   ├── emit_vzome.py            hand-built emitter for 24-cell
│   ├── emit_8cell.py            8-cell sporadics + inf-family
│   ├── emit_snub24.py           snub 24-cell (2 shapes)
│   └── emit_grand_antiprism.py  grand antiprism (2 shapes)
├── tools/
│   ├── fingerprint_audit.py     consistency check across all 8 polytopes
│   └── patch_origin.py          one-shot origin-ball cleanup for hand-built files
├── docs/
│   ├── SUMMARY.md               full result narrative
│   ├── METHODOLOGY.md           saturation + open questions
│   └── UNIFORM_PLAN.md          extension to all 47 convex uniform 4-polytopes
└── output/
    └── <polytope>/              .vZome files + per-polytope writeup
```

## Usage

Requires Python 3.10+ and NumPy. No other dependencies.

```bash
# Run search for one polytope
python lib/run_search.py 24cell 3
python lib/run_search.py snub24cell 4

# Re-emit vZome files
python lib/emit_vzome.py            # 24-cell (3 files)
python lib/emit_8cell.py            # 8-cell (9 files)
python lib/emit_snub24.py           # snub 24-cell (2 files)
python lib/emit_grand_antiprism.py  # grand antiprism (2 files)

# Sanity-check the classification (≈10 minutes; runs all 8 polytopes)
python tools/fingerprint_audit.py
```

The 5-cell, 16-cell, 120-cell, and 600-cell vZome files are hand-built
or constructed in vZome's UI; they are checked into `output/` and are
maintained with `tools/patch_origin.py` (idempotent).

## Acknowledgments

- Independent prior work on the 5-cell by **Scott Vorthmann** and
  **David Richter** (2007),
  https://vorth.github.io/vzome-sharing/2007/04/24/five-cell-family.html
- The **"Zometriality"** page at
  https://polytopologist.github.io/zome_pages/zometriality.htm
  for 16-cell antiprism shapes.

## License

MIT — see [LICENSE](LICENSE).
