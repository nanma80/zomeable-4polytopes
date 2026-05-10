# Zomeable orthographic projections of uniform 4-polytopes

This project enumerates all distinct 3D shapes obtainable by orthographic
projection of each convex regular 4-polytope, such that **every projected
edge lies on a default-color zometool axis** (B / Y / R / G in the
icosahedral system).

## Master result

The 8 polytopes documented below are the **regulars + non-Wythoff** corpus.
For the full Wythoff family (47 unique convex uniform 4-polytopes including
all of the rectified / truncated / cantellated / runcinated descendants),
see [`WYTHOFF_SWEEP.md`](WYTHOFF_SWEEP.md) and the inheritance-free
corpus-completeness audit in [`INHERITANCE_FREE_SWEEP.md`](INHERITANCE_FREE_SWEEP.md).

| Polytope        | Verts | Edges | Distinct shapes | Notes                             |
|-----------------|-------|-------|-----------------|-----------------------------------|
| 5-cell  {3,3,3} | 5     | 10    | **4**           | saturated rng=3; matches Richter/Vorthmann 2007 |
| 8-cell  {4,3,3} | 16    | 32    | **1 inf family + 3 sporadic** | inf family = split cuboids parametrized by ℤ[φ]-Pythagorean triples (a:b) with a²+b²=c²∈ℤ[φ]; sporadics = cube, rhombic dodec, phi-oblique (V=16, kernel support 3) |
| 16-cell {3,3,4} | 8     | 24    | **6**           | saturated rng=4                   |
| 24-cell {3,4,3} | 24    | 96    | **3**           | saturated rng=3                   |
| 120-cell {5,3,3}| 600   | 1200  | **1**           | saturated rng=3 (330-ball image)  |
| 600-cell {3,3,5}| 120   | 720   | **1**           | saturated rng=4 (75-ball image)   |
| Snub 24-cell    | 96    | 432   | **2**           | cell-first Tₕ, vertex-first D₃d   |
| Grand antiprism | 100   | 500   | **2**           | vertex-first D₂ₕ, ring-first D₅d  |

(See per-polytope `RESULTS.md` files under `output/<polytope>/` for details.)

## Methodology

For each polytope P:

1. Embed P in ℝ⁴ with rational/algebraic vertices.
2. Enumerate kernel directions `n ∈ ℤ[φ]⁴` with `|a|, |b| ≤ rng` for each
   component `a + bφ`, deduplicated by sign-flip-per-axis and decreasing
   magnitude.
3. For each direction, compute the 3×4 orthographic projection matrix Q,
   project all edges to 3D, check whether all `|cos∠|` between projected
   edge directions are among the 40 allowed values for default-axis pairs,
   then attempt to align two non-parallel edges to a chosen default-axis
   pair and verify all remaining edges land on default axes.
4. Group hits by **rotation+uniform-scale-invariant shape fingerprint**
   (sorted multiset of normalized pairwise squared distances).
5. Increase rng until shape count stabilizes ("saturation").

See `METHODOLOGY.md` for caveats about empirical-vs-formal saturation.

## Code layout

```
zomeable-4polytopes\
├── lib\
│   ├── polytopes.py             vertex/edge specifications for all 8 polytopes
│   ├── search_engine.py         generic kernel-direction search
│   ├── run_search.py            CLI runner: python lib/run_search.py <name> [rng]
│   ├── emit_generic.py          generic <Polytope4d>-based emitter
│   ├── emit_vzome.py            hand-built emitter (24-cell)
│   ├── emit_8cell.py            8-cell emitter
│   ├── emit_snub24.py           snub 24-cell emitter
│   └── emit_grand_antiprism.py  grand antiprism emitter
├── tools\
│   ├── fingerprint_audit.py     cross-polytope consistency check
│   └── patch_origin.py          idempotent origin-ball cleanup
├── docs\
│   ├── SUMMARY.md               this file
│   ├── METHODOLOGY.md           saturation & open questions
│   ├── UNIFORM_PLAN.md          extension to all 47 convex uniform 4-polytopes
│   ├── WYTHOFF_SWEEP.md         Wythoff-family corpus: methodology, taxonomy, per-polytope tables
│   └── INHERITANCE_FREE_SWEEP.md  38-hour matrix sweep auditing the Wythoff corpus for completeness
└── output\
    ├── 5cell\           RESULTS.md  + 4 .vZome files
    ├── 8cell\           CLASSIFICATION.md + 9 .vZome files
    ├── 16cell\          RESULTS.md  + 6 .vZome files
    ├── 24cell\          ZOMEABLE_PROJECTIONS.md + 3 .vZome files
    ├── 120cell\         RESULTS.md  + 1 .vZome file
    ├── 600cell\         RESULTS.md  + 1 .vZome file
    ├── snub24cell\      RESULTS.md  + 2 .vZome files
    ├── grand_antiprism\ RESULTS.md  + 2 .vZome files
    ├── <wythoff descendants>\    39 folders (e.g. rectified_5cell, bitruncated_8cell,
    │                             omnitruncated_120cell, …), each with RESULTS.md
    │                             plus 0–3 .vZome files — see WYTHOFF_SWEEP.md
    └── wythoff_sweep_manifest.json   provenance ledger for the 69 Wythoff-descendant .vZome files
```

## Two notions of "zomeable"

Two distinct criteria show up; the 8-cell case forced us to make the
distinction explicit:

1. **Zometool-axis-aligned** (the search-engine criterion). Every
   projected edge direction is one of the 31 default zome axes (B, Y, R,
   G families). Equivalent to: the 4 image vectors `c_i` can be rotated
   so each unit-vector lies on a default axis.
2. **vZome-embeddable** (the strict criterion). Additionally, after
   rotation, every ball coordinate lies in ℤ[φ]³ (up to a single global
   scale). Equivalent to: every length ratio `|c_i|/|c_j|` is in ℚ(φ).

The search engine reports criterion 1. Criterion 2 is verified at emit
time by the per-strut `classify_direction` check in `emit_vzome.py`
(every directed strut must match a `(B/Y/R/G)i_proto * GF(...)`).

Most polytopes satisfy 1 ⇔ 2 because their geometry forces the
length ratios to be in ℚ(φ) automatically. The 8-cell breaks this:
the search finds support-3 kernels (e.g. `n = (1,−1,1,0)`) whose 4
image vectors all align with default axes but have length ratios
`√2/√3 ∉ ℚ(φ)` or `√(2+φ) ∉ ℚ(φ)` — so they exist as zometool
sculptures but cannot be expressed in vZome's standard icosahedral
field. We **do not** emit such cases.

## vZome embedding gotchas (learned from 8-cell hand-built emission)

- **Per-model normalization**: vZome strut radii are fixed by family,
  not length. If models in a family have wildly different edge lengths
  (e.g. inf-family cuboids with growing (a,b,c) parameters), struts will
  appear thinner and thinner. Solution: divide each model's generators
  by its own max component magnitude before applying the global SCALE
  (see `lib/emit_8cell.py`'s `emit_skew_zonotope(..., norm=...)`).
- **GF inverse formula** in ℚ(φ):  `1/(a + bφ) = ((a+b) − bφ) / (a²+ab−b²)`.
  Useful for normalization when the longest edge is itself a non-integer
  ZZ[φ] value like `2φ−1 = √5`.
- **Verification at emit time**: always run `classify_direction` on
  every directed strut. A match means the strut lies on a default axis
  AND the length factor is in ℤ[φ]; a `None` result means the model is
  not vZome-embeddable.
- **SCALE choice**: the conventional ball spacing is `SCALE = GF(2,2)`
  (= 2+2φ, the zometool blue-strut length unit). Smaller SCALEs put
  balls too close; larger ones make models unwieldy.

## vZome files emitted

All non-hand-built files use vZome's `<Polytope4d>` element with a
specific Coxeter group + wythoff index + quaternion. The quaternion `q`
is derived from the kernel direction `n` of the projection by
`q = conj(n) = (n_w, -n_i, -n_j, -n_k)` (vZome's projection is
`v ↦ imag(v · q)`, kernel = span(conj(q))).

| Polytope | Group / wythoff | Files |
|----------|----------------|-------|
| 5-cell   | A4 / 1000      | 5cell/5cell_*.vZome  (4 files)         |
| 16-cell  | B4/C4 / 1000   | 16cell/16cell_*.vZome (6 files)        |
| 24-cell  | F4 / 1000      | 24cell/*.vZome (3 hand-built)          |
| 120-cell | H4 / 1000      | 120cell/120cell_H4_to_H3.vZome         |
| 600-cell | H4 / 0001      | 600cell/600cell_H4_to_H3.vZome         |

**Caveat**: kernel directions in our search embedding may differ from
vZome's internal embedding (vZome uses a Coxeter group's standard
realization). The emitted files were built using each polytope's
standard ℤ[φ] embedding, which matches vZome for {16,24,120,600}-cells
but may need reframing for the 5-cell. Each file should be opened in
vZome and verified to render with default-color struts; shapes that fail
need either (a) a different quaternion in the same family, or (b) a
hand-built `<ShowPoint>`/`<JoinPointPair>` model (see
`24cell/search/emit_vzome.py` for the pattern).

## Status

- All 6 polytopes' shape counts: ✓ known.
- 24-cell hand-built `.vZome`s: ✓ verified by user.
- Non-24-cell `.vZome`s (12 files): emitted via `emit_polytope4d.py`,
  pending user verification in vZome.

## External references

Independent prior work corroborating our enumerations:

- **5-cell** (4 shapes): Scott Vorthmann & David Richter,
  <https://vorth.github.io/vzome-sharing/2007/04/24/five-cell-family.html>
  (2007). Their 4 zomeable projections of the regular 5-cell match ours
  exactly. See `5cell/RESULTS.md` for the file-by-file mapping.
- **16-cell** (3 antiprism shapes): "Zometriality" page at
  <https://polytopologist.github.io/zome_pages/zometriality.htm>. The
  three 16-cell antiprisms shown there match our `16cell_antiprism_*.vZome`
  files; truncating any one of them to its edge midpoints yields the
  same 24-cell zometool model, an independent consistency check.

