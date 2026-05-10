# output/

vZome files for every zomeable orthographic projection in this project,
one subfolder per polytope.  See the [top-level README](../README.md)
for per-polytope shape counts and the regulars↔uniforms breakdown.

Each subfolder has its own `RESULTS.md` describing its shapes and
kernel directions, with two historical exceptions kept under their
original filenames:
[`8cell/CLASSIFICATION.md`](8cell/CLASSIFICATION.md) and
[`24cell/ZOMEABLE_PROJECTIONS.md`](24cell/ZOMEABLE_PROJECTIONS.md).

Provenance for every sweep-generated shape file — parent kernel,
fingerprint hash, source polytope, Coxeter group, Wythoff bitmask, and
rng — lives in
[`wythoff_sweep_manifest.json`](wythoff_sweep_manifest.json).  The 13
Wythoff descendants that snap-fail in ℤ[φ]³ at rng ≤ 4 are recorded
as `status=snap_failed` entries in the manifest and do not have their
own subfolder; see
[`../docs/WYTHOFF_SWEEP.md`](../docs/WYTHOFF_SWEEP.md) for the
group-theoretic analysis.
