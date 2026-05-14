# zomeable-4polytopes

> 🌐 **Interactive site:** [**nanma80.github.io/zomeable-4polytopes**](https://nanma80.github.io/zomeable-4polytopes/) — browse all 53 zomeable polytopes with embedded vZome 3D viewers.

Enumeration of orthographic projections of convex uniform 4-polytopes
whose every projected edge lies on a default-color
[zometool](https://www.zometool.com/) axis (B / Y / R / G in the
icosahedral system) — i.e., projections that can be physically built
with zometool, and modeled exactly in [vZome](https://vzome.com/).

For each polytope `P` we enumerate kernel directions `n ∈ ℤ[φ]⁴`,
project `P → ℝ³` via `Q = I − n nᵀ/|n|²`, and keep those projections
whose edge set aligns with default zome axes. Hits are grouped up to
rotation and uniform scale to count distinct 3D shapes.

## Browse the corpus

| Category | Polytopes | Zomeable polytopes | Zomeable projections |
| -------- | --------: | -----------------: | -------------------: |
| [Regular](docs/CATEGORY_REGULAR.md) | 6 | 6 | 15 + 1 inf family ¹ |
| [Uniform](docs/CATEGORY_UNIFORM.md) *(nonprismatic)* | 41 | 28 | 73 |
| [Duoprisms](docs/CATEGORY_DUOPRISMS.md) | ∞ | 6 | 14 |
| [Polyhedral prisms](docs/CATEGORY_POLYHEDRAL_PRISMS.md) | 17 | 12 | 43 |
| [Antiprismatic prisms](docs/CATEGORY_ANTIPRISMATIC_PRISMS.md) | ∞ | 1 | 9 |
| **Total** | **∞** | **53** | **154 + 1 inf family** |

Click a category to see the per-polytope list with shape counts and
links to the **3D viewer** for every polytope.  Each viewer page lives
next to its `.vZome` files in `output/<category>/<slug>/VIEWER.md` and
renders the embedded vzome-viewer when served via
[GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/).

¹ Only the tesseract (8-cell) has an infinite family of zomeable
projections (parametrized by ℤ[φ]-Pythagorean triples); every other
polytope in the corpus saturates at a small finite count.  See
[`output/regular/8cell/CLASSIFICATION.md`](output/regular/8cell/CLASSIFICATION.md)
for the master theorem.

**These counts are not formally proven complete.** Each was obtained by
enumerating kernel directions `n ∈ ℤ[φ]⁴` over a bounded box of
coefficients, and we report the count once enlarging the box no longer
produces new shapes (*empirical saturation*). It remains possible that
a kernel direction with very large coefficients yields a previously
unseen zomeable projection. We have no formal upper bound on the
coefficient size that suffices. See
[`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for details.

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

The prismatic survey (duoprisms, polyhedral prisms, antiprismatic
prisms) is, to our knowledge, the first agnostic kernel-search census
of zomeable projections for these families.

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
│   ├── inheritance_free_sweep.py  inheritance-free matrix audit
│   ├── run_prismatic_sweep.py   prismatic-family sweep driver
│   ├── build_prismatic_results.py  generates per-polytope RESULTS.md
│   ├── build_prismatic_doc.py   generates docs/PRISMATIC.md
│   ├── build_viewer_pages.py    generates VIEWER.md + category pages
│   └── patch_origin.py          one-shot origin-ball cleanup
├── docs/
│   ├── CATEGORY_REGULAR.md           level-2 browse: regulars
│   ├── CATEGORY_UNIFORM.md           level-2 browse: uniforms
│   ├── CATEGORY_DUOPRISMS.md         level-2 browse: duoprisms
│   ├── CATEGORY_POLYHEDRAL_PRISMS.md level-2 browse: polyhedral prisms
│   ├── CATEGORY_ANTIPRISMATIC_PRISMS.md level-2 browse: antiprism prisms
│   ├── SUMMARY.md               full result narrative
│   ├── METHODOLOGY.md           saturation + open questions
│   ├── UNIFORM_PLAN.md          extension to all 47 convex uniform 4-polytopes
│   ├── WYTHOFF_SWEEP.md         Wythoff sweep results + reproduction
│   ├── PRISMATIC.md             prismatic sweep results + reproduction
│   └── INHERITANCE_FREE_SWEEP.md  corpus-completeness matrix audit
└── output/
    ├── regular/<slug>/          regular polytopes + VIEWER.md
    ├── uniform/<slug>/          Wythoff descendants + non-Wythoffian + VIEWER.md
    ├── polyhedral_prisms/<slug>/   polyhedral prisms + VIEWER.md
    ├── duoprisms/<slug>/        duoprisms + VIEWER.md
    ├── antiprismatic_prisms/<slug>/   antiprismatic prisms + VIEWER.md
    ├── wythoff_sweep_manifest.json   provenance ledger for Wythoff sweep
    └── prismatic_manifest.json       provenance ledger for prismatic sweep
```

Each polytope folder with ≥1 zomeable shape contains:

- `.vZome` files for every shape
- `VIEWER.md` — viewer-only landing page (level 3 of the browse hierarchy)
- `RESULTS.md` / `CLASSIFICATION.md` / `ZOMEABLE_PROJECTIONS.md` —
  deep-dive writeup with methodology, kernel directions, shape tables,
  and reproduction commands.

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

# Regenerate the browse pages (VIEWER.md + 5 docs/CATEGORY_*.md)
python tools/build_viewer_pages.py
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
