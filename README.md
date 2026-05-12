# zomeable-4polytopes

Enumeration of orthographic projections of uniform 4-polytopes whose every
projected edge lies on a default-color [zometool](https://www.zometool.com/)
axis (B / Y / R / G in the icosahedral system) — i.e., projections that can
be physically built with zometool, and modeled exactly in
[vZome](https://vzome.com/).

For each polytope `P` we enumerate kernel directions `n ∈ ℤ[φ]⁴`,
project `P → ℝ³` via `Q = I − n nᵀ/|n|²`, and keep those projections
whose edge set aligns with default zome axes. Hits are grouped up to
rotation and uniform scale to count distinct 3D shapes.

## Regular polytopes

| Polytope          | Distinct zomeable shapes |
|-------------------|--------------------------|
| 5-cell `{3,3,3}`  | **4** — vertex-first + 3 oblique |
| 8-cell `{4,3,3}`  | **1 infinite family + 3 sporadic** ¹ — cell-first, vertex-first, phi-oblique, inf family of cuboids |
| 16-cell `{3,3,4}` | **6** — vertex-first, cell-first, edge-first, 3 triality |
| 24-cell `{3,4,3}` | **3** — cell-first, vertex-first, triality |
| 120-cell `{5,3,3}`| **1** — cell-first |
| 600-cell `{3,3,5}`| **1** — vertex-first |

vZome files for every shape above are in [`output/<polytope>/`](output/).

**These counts are not formally proven complete.** Each was obtained by
enumerating kernel directions `n ∈ ℤ[φ]⁴` over a bounded box of
coefficients, and we report the count once enlarging the box no longer
produces new shapes (*empirical saturation*). It remains possible that a
kernel direction with very large coefficients yields a previously unseen
zomeable projection. We have no formal upper bound on the coefficient
size that suffices. See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for
details.

¹ The 8-cell infinite family is parametrized by ℤ[φ]-Pythagorean
triples `(a, b, c)` with `a² + b² = c²` (both integer-Pythagorean and
genuinely-φ branches), producing distinct rectangular cuboids. The
three sporadics are the cell-first cube (V=8 — also the degenerate
`b → 0` boundary of the inf-family, but listed separately because the
ball/strut counts drop), the vertex-first rhombic
dodecahedron (V=15), and the phi-oblique sporadic (V=16, kernel
`(0, 1/φ², 1, −1/φ)` — three image vectors coplanar, 4th independent).
Three further canonical projections — edge-first hex prism, face-first
4×2 cuboid, face-first-like BYR shape — exist as zometool sculptures
in vZome's *cubic* algebraic-field system but cannot be expressed
in the icosahedral ℤ[φ] field. See
[`output/regular/8cell/CLASSIFICATION.md`](output/regular/8cell/CLASSIFICATION.md).

Per-polytope writeups live in `output/<polytope>/RESULTS.md` (or
`CLASSIFICATION.md` for 8-cell, `ZOMEABLE_PROJECTIONS.md` for 24-cell).

## Uniform polytopes

The remaining 41 convex uniform 4-polytopes split into 2 non-Wythoffian
uniforms (snub 24-cell, grand antiprism) and 39 Wythoff descendants of
the four rank-4 Coxeter groups (A₄, B₄, F₄, H₄).  The Wythoff
descendants are obtained from a regular polytope by *ringing* one or
more nodes of the regular's Coxeter diagram (rectification, truncation,
cantellation, runcination, etc.).  The two non-Wythoffian uniforms are
obtained from the 600-cell by *diminishing*: the snub 24-cell removes
the 24 vertices of an inscribed 24-cell (leaving 96), and the grand
antiprism removes two perpendicular decagonal rings of 10 vertices each
(leaving 100).

Every zomeable projection of a Wythoff descendant we have found is
**inherited** from a zomeable projection of its parent regular: the
sweep ([`tools/run_wythoff_sweep.py`](tools/run_wythoff_sweep.py))
takes each regular's good kernels and applies them to every Wythoff
variant in that regular's Coxeter group.  An exhaustive
**inheritance-free matrix audit**
([`docs/INHERITANCE_FREE_SWEEP.md`](docs/INHERITANCE_FREE_SWEEP.md))
empirically confirms this inheritance scheme is complete: searching
each descendant from scratch — with no parent-regular kernel
inheritance — finds zero zomeable projections outside the inherited
corpus.  So the Wythoff descendants do not give rise to genuinely new
zome shapes beyond what the regulars + standard Wythoff operations
produce; the value of the corpus is the explicit catalogue.  The same
inheritance pattern applies to the non-Wythoffian pair via diminishing
rather than ringing: all 4 of their kernels are 600-cell special
directions (vertex or removed-sub-polytope axes), and the projected
vertex coordinates are literally the corresponding 600-cell coordinates
restricted to the surviving subset.

| Polytope                  | Distinct zomeable shapes | Inherits from |
|---------------------------|:---:|:---:|
| **non-Wythoffian** *(diminishings of the 600-cell)* |||
| snub 24-cell              | **2** — cell-first, vertex-first   | 600-cell ³ |
| grand antiprism           | **2** — vertex-first, ring-first   | 600-cell ³ |
| **A₄ descendants** |||
| rectified 5-cell          | 4 | 5-cell — vertex + 3 oblique |
| truncated 5-cell          | 4 | 5-cell — vertex + 3 oblique |
| bitruncated 5-cell        | 4 | 5-cell — vertex + 3 oblique |
| cantellated 5-cell        | 4 | 5-cell — vertex + 3 oblique |
| cantitruncated 5-cell     | 4 | 5-cell — vertex + 3 oblique |
| runcinated 5-cell         | 4 | 5-cell — vertex + 3 oblique |
| runcitruncated 5-cell     | 4 | 5-cell — vertex + 3 oblique |
| omnitruncated 5-cell      | 4 | 5-cell — vertex + 3 oblique |
| **B₄ descendants** |||
| rectified 8-cell          | 6 | 16-cell ⁴ — vertex/cell/edge + 3 triality |
| bitruncated 8-cell        | 6 | 16-cell ²⁴ — vertex/cell/edge + 3 triality |
| truncated 16-cell         | 6 | 16-cell — vertex/cell/edge + 3 triality |
| **F₄ descendants** |||
| rectified 24-cell         | 3 | 24-cell — cell + vertex + triality |
| truncated 24-cell         | 3 | 24-cell — cell + vertex + triality |
| **H₄ descendants** |||
| rectified 120-cell        | 1 | 120-cell |
| truncated 120-cell        | 1 | 120-cell |
| cantellated 120-cell      | 1 | 120-cell |
| cantitruncated 120-cell   | 1 | 120-cell |
| runcitruncated 120-cell   | 1 | 120-cell |
| bitruncated 120-cell      | 1 | 120-cell, 600-cell ² |
| runcinated 120-cell       | 1 | 120-cell, 600-cell ² |
| omnitruncated 120-cell    | 1 | 120-cell, 600-cell ² |
| rectified 600-cell        | 1 | 600-cell |
| truncated 600-cell        | 1 | 600-cell |
| cantellated 600-cell      | 1 | 600-cell |
| cantitruncated 600-cell   | 1 | 600-cell |
| runcitruncated 600-cell   | 1 | 600-cell |

vZome files for every shape above are in [`output/<polytope>/`](output/).

**Totals:** 69 zomeable shapes across 26 of the 39 Wythoff descendants,
plus 4 shapes for the 2 non-Wythoffian uniforms — 73 total.  The 13
Wythoff descendants with **0** shapes have no zomeable orthographic
projection in the icosahedral `ℤ[φ]³` field — their natural projections
fall in `ℤ[√2]³`, the field of B₄/F₄, which is outside this project's
icosahedral scope.  See
[`docs/WYTHOFF_SWEEP.md`](docs/WYTHOFF_SWEEP.md) for the full
methodology, per-polytope shape descriptions, and B₄/F₄ equivalences.

² *Self-dual under the 8-cell↔16-cell (resp. 120-cell↔600-cell)
duality:* the Wythoff bitmask is palindromic, so the same polytope is
reached starting from either parent regular.  Filed under the "8-cell"
(resp. "120-cell") name by convention.

³ *Inherited from the 600-cell by diminishing,* not by Wythoffian
ringing.  All 4 emitted projections use a 600-cell vertex direction as
the kernel: for snub 24-cell, `(1,0,0,0)` (a removed-24-cell vertex,
i.e. centre of one icosahedral cell) and `(φ², φ, 1, 0)` (a surviving
600-cell vertex); for grand antiprism, `(1,1,1,1)` (a surviving
tesseract vertex of the 600-cell) and `(1,0,0,0)` (a removed
Hopf-decagon vertex = pentagonal-antiprism-ring axis).  Edges that the
diminishing introduces stay zomeable for these 4 shapes empirically,
but that is checked per shape rather than guaranteed automatically by
the inheritance.

⁴ *Kernel set traces to the 16-cell despite the descendant's
"8-cell"-side Wythoff name.*  Rectified 8-cell and bitruncated 8-cell
both have vertex sets equal to the 16-cell edge midpoints (resp. a
related 16-cell-aligned orbit), so the 6 zomeable kernels match the
16-cell's 6 master projection directions exactly.  The 3 D₄-triality
(antiprism) directions are 16-cell-aligned only — they do not yield a
zomeable projection of the bare tesseract.  The 3 standard axes
(16-cell vertex/cell/edge = tesseract cell/vertex/face) are shared B₄
axes naturally accessible from either parent.  See
[`docs/WYTHOFF_SWEEP.md`](docs/WYTHOFF_SWEEP.md#oblique-kernel-inheritance-every-oblique_vzome-is-a-parents-master-projection)
for the explicit kernel↔master-file map.

## Prismatic uniform 4-polytopes

The 204 prismatic convex uniform 4-polytopes in scope (17 polyhedral
prisms minus the tesseract, 170 duoprisms `{p}×{q}` with
`3 ≤ p ≤ q ≤ 20` minus `(4,4)`, and 17 antiprismatic prisms with
`4 ≤ n ≤ 20`) were swept with the identical agnostic kernel-search
machinery used for the 47-corpus.  No filtering by obstruction
arguments: every polytope was tested at `rng = 2` with
`permute_dedup = False`.

| Family | Description | In scope | Hit ≥ 1 | Total shapes |
|---|---|---:|---:|---:|
| **A** | Polyhedral prisms `P × [0,1]`        | 17  | 12 | 48 |
| **B** | Duoprisms `{p}×{q}`                  | 170 |  6 |  9 |
| **C** | Antiprismatic prisms `A_n × [0,1]`   | 17  |  1 |  9 |
| **Total** |                                  | **204** | **19** | **66** |

Notable surprise hits in Family B (the naive obstruction lemma —
"every `{p}×{q}` with both `p, q ≠ 4` projects only to ℝ²" — would
have predicted these to be impossible, but the agnostic sweep finds
genuine rank-3 projections through clever rotations):

- `{3}×{6}`, `{4}×{6}`, `{6}×{6}`, `{4}×{10}`, `{5}×{10}`, `{10}×{10}`

The only Family C hit is `5_antiprismatic_prism` (pentagonal-antiprism
prism), via the icosahedral embedding of the pentagonal antiprism (10
non-polar icosahedron vertices).  All `n ≠ 5` antiprism prisms in
scope produce zero zomeable projections, confirming that
non-icosahedral antiprisms have no ℤ[φ]³ embedding.

Full per-polytope tables, RESULTS.md links and vZome viewer embeds
live in [`docs/PRISMATIC.md`](docs/PRISMATIC.md) and the per-polytope
`output/<slug>/RESULTS.md` files.

## Prior work and novelty

Standard "vertex-first / cell-first / edge-first" zome projections of
the six convex regular 4-polytopes are folklore — easy to construct by
hand and well-known to the zometool community. The shapes below have
been published or built independently; our enumeration confirms them.

- **5-cell** — Scott Vorthmann & David Richter, *Five-cell family*
  (2007),
  https://vorth.github.io/vzome-sharing/2007/04/24/five-cell-family.html
  — all 4 shapes match ours exactly.
- **16-cell triality** (the 3 square antiprisms) — *Zometriality*,
  https://polytopologist.github.io/zome_pages/zometriality.htm
  — the three antiprism shapes match ours; the page's observation
  that truncating any one to its edge midpoints yields the same
  24-cell zometool model is an independent consistency check with our
  `24cell_triality.vZome`.
- **Snub 24-cell, cell-first** — D. Richter, *The 24-Cell and its
  Snub*,
  https://polytopologist.github.io/zome_pages/24cellzome.htm
  — photograph of the cell-first zome model (60 balls, icosahedral
  outer hull).
- **Grand antiprism, ring-first** — Scott Vorthmann, *Grand antiprism*
  vZome model (2006),
  https://vorth.github.io/vzome-sharing/2006/02/24/grand-antiprism.html
  — same projection as our `grand_antiprism_ring_first.vZome`,
  verified equivalent ball-by-ball.

To our knowledge, the following results are new:

- **8-cell** — the infinite family of zometool-buildable cuboids
  (parameterized by ℤ[φ]-Pythagorean triples), the **phi-oblique
  sporadic** (V=16, kernel support 3, three image vectors coplanar),
  and the cubic-system canonical projections (edge-first hex prism,
  face-first cuboid, BYR shape) that are not embeddable in the
  icosahedral ℤ[φ] field
  (see [`output/regular/8cell/CLASSIFICATION.md`](output/regular/8cell/CLASSIFICATION.md)).
- **Snub 24-cell, vertex-first** — does not appear in Richter's page or
  any source we could find.
- **Grand antiprism, vertex-first** — not in Vorthmann (2006) or other
  sources we could find.
- **Completeness for each polytope** — empirical proofs that the listed
  counts saturate (caveat above).

## References

- J. H. Conway and M. J. T. Guy, "Four-dimensional Archimedean
  polytopes," Proc. Colloquium on Convexity, Copenhagen, 1965 (origin
  of the grand antiprism).
- Wikipedia, [Grand antiprism](https://en.wikipedia.org/wiki/Grand_antiprism).

## Layout

```
zomeable-4polytopes/
├── lib/                     core search + emitter library
│   ├── polytopes.py             vertex/edge specs for all 8 polytopes
│   ├── wythoff.py               Wythoff construction for A4/B4/F4/H4
│   ├── search_engine.py         kernel-direction search (vectorised)
│   ├── run_search.py            CLI: run search for one polytope
│   ├── emit_generic.py          generic <Polytope4d>-based emitter
│   ├── emit_vzome.py            hand-built emitter for 24-cell
│   ├── emit_8cell.py            8-cell sporadics + inf-family
│   ├── emit_snub24.py           snub 24-cell (2 shapes)
│   └── emit_grand_antiprism.py  grand antiprism (2 shapes)
├── tools/
│   ├── fingerprint_audit.py     consistency check across all 8 polytopes
│   ├── run_wythoff_sweep.py     Wythoff sweep over A4/B4/F4/H4
│   ├── analyze_sweep.py         label sweep shapes vs. regular references
│   ├── emit_novel.py            emit .vZome per novel sweep shape
│   ├── inheritance_free_sweep.py  inheritance-free matrix audit (corpus completeness)
│   └── patch_origin.py          one-shot origin-ball cleanup for hand-built files
├── docs/
│   ├── SUMMARY.md               full result narrative
│   ├── METHODOLOGY.md           saturation + open questions
│   ├── UNIFORM_PLAN.md          extension to all 47 convex uniform 4-polytopes
│   ├── WYTHOFF_SWEEP.md         results + reproduction for the Wythoff sweep
│   └── INHERITANCE_FREE_SWEEP.md  38h matrix-sweep audit of corpus completeness
└── output/
    ├── <polytope>/              .vZome files + per-polytope writeup
    │                            (47 folders: 8 master + 39 Wythoff descendants)
    └── wythoff_sweep_manifest.json   provenance ledger for the 69 Wythoff .vZome files
```

## Usage

Requires Python 3.10+ and NumPy. No other dependencies.

```bash
# Run search for one polytope
python lib/run_search.py 24cell 3
python lib/run_search.py snub_24cell 4

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

The [zometool](https://www.zometool.com/) construction system and
[vZome](https://vzome.com/) (Scott Vorthmann) made this work possible.
See *Prior work and novelty* above for citations to specific shapes
already known.

## License

MIT — see [LICENSE](LICENSE).
