# output/

vZome files for every zomeable orthographic projection in this project,
organised into category subfolders:

- [`regular/`](regular/) — the 6 convex regular 4-polytopes
  (5-cell, 8-cell, 16-cell, 24-cell, 120-cell, 600-cell).
- [`uniform/`](uniform/) — 28 non-regular convex uniform 4-polytopes
  (rectified, truncated, bitruncated, cantellated, cantitruncated,
  runcinated, runcitruncated, omnitruncated, snub_24cell, grand_antiprism).
- [`polyhedral_prisms/`](polyhedral_prisms/) — 12 polyhedral prisms
  `P × [0,1]` (Family A of prismatic uniform 4-polytopes).
- [`duoprisms/`](duoprisms/) — 6 duoprisms `{p}×{q}`
  (Family B).
- [`antiprismatic_prisms/`](antiprismatic_prisms/) — 1 antiprismatic
  prism (Family C: the pentagonal-antiprism prism).
- [`gosset_projections/`](gosset_projections/) — related non-4D collection:
  strict orthographic zomeable projections of Gosset-family and adjacent D/E
  root polytopes including 5-orthoplex (`2_11`), 5-demicube (`1_21`),
  rectified 5-orthoplex (`t1 2_11`), `2_21`, `1_22`, `3_21`, `2_31`,
  `1_32`, `4_21`, and `2_41`.

Each polytope subfolder has its own `RESULTS.md` describing its shapes
and kernel directions, with two historical exceptions kept under
their original filenames:
[`regular/8cell/CLASSIFICATION.md`](regular/8cell/CLASSIFICATION.md)
and
[`regular/24cell/ZOMEABLE_PROJECTIONS.md`](regular/24cell/ZOMEABLE_PROJECTIONS.md).

Provenance for the 47-polytope Wythoff-sweep corpus (the regulars +
uniforms) lives in
[`wythoff_sweep_manifest.json`](wythoff_sweep_manifest.json).  The 13
Wythoff descendants that snap-fail in ℤ[φ]³ at rng ≤ 4 are recorded
as `status=snap_failed` entries in the manifest and do not have their
own subfolder; see
[`../docs/WYTHOFF_SWEEP.md`](../docs/WYTHOFF_SWEEP.md) for the
group-theoretic analysis.

Provenance for the 204-polytope prismatic sweep
(Families A/B/C above) lives in
[`prismatic_manifest.json`](prismatic_manifest.json); see
[`../docs/PRISMATIC.md`](../docs/PRISMATIC.md) for the methodology
and the 19 emitting polytopes.  A post-sweep snap-alignment audit recovered
four additional prismatic models whose edge directions were found originally
but whose first valid alignment did not snap to exact ℤ[φ]³ coordinates.

The Gosset projection files are intentionally kept as a parallel related
category rather than folded into the 4-polytope taxonomy; see
[`../docs/CATEGORY_GOSSET_PROJECTIONS.md`](../docs/CATEGORY_GOSSET_PROJECTIONS.md).
