# probe_regulars_rng3 — abandoned 2026-05-08

## Goal

Verify whether rng=3 finds new kernel directions for the 8 regular
4-polytope bitmasks (A4/B4/F4/H4 × (1,0,0,0)/(0,0,0,1)) beyond the
rng=2 set already cached.

If rng=3 had added kernels, that would justify a full rng=3
descendant sweep.

## Why abandoned

`search()` per-direction Python overhead dominates at any size.
Estimated per-search runtime:

| polytope | rng=2 dirs (195K) | rng=3 dirs (2.88M) |
|---|---|---|
| A4 5-cell K=10 | ~5-10 min | ~75-150 min |
| H4 120-cell K=1200 | ~10-15 min | ~150-200 min |

At ~100-300 µs Python+numpy overhead per direction (dominated by
`projection_matrix()`'s 4×1 SVD plus `_try_align` setup), the 8
regulars × rng=3 would be 10-20 hours wall.  Killed at A4 5-cell
rng=2 having burned 874s CPU.

## Next steps if revisited

1. **Vectorise `search()` per-direction**: batch many directions through
   a single numpy/LAPACK call (matrix SVDs of stacked 4×1 vectors,
   batched cos-pair tests).  This is the right structural fix and
   would speed BOTH rng=2 and rng=3 by 10-100x.

2. **Empirical alternative**: trust the existing kernel-completeness
   evidence (rng=2 audits found 0 genuinely new shapes for any group)
   and skip rng=3 entirely.  Rationale: descendants only inherit from
   regulars; if the kernel set is closed at rng=2 (no new kernels at
   higher rng), descendants gain no new shapes.

## Status

Skipping rng=3 work for now (option 2 above).  Will revisit if
search() is vectorised.
