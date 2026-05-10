# h4_600cell_rng4 probe — killed before completion

## What was attempted

`ongoing_work/probes/h4_600cell_rng4_focused.py` ran a direct rng=4 search
on the H4 600-cell (group `H4`, bitmask `(0,0,0,1)`, V=120, E=720).  The
intent: find zomeable kernel directions with larger Z[φ] integer
coefficients than the rng=2 sweep covers, which (by analogy with the
M17/B4 audit-flagged cases like rectified tesseract +3 obliques) might
reveal new shapes invisible to the rng=2 production sweep.

The script (lines numbered as committed):
1. `gen_dirs(rng=4)` — produces ~21.5 M candidate directions in Z[φ]⁴.
2. `search('600-cell', V, E, dirs4)` — single `search()` call over all dirs.
3. Snap each unique fingerprint, compute post-snap shape_signature, compare
   against `output/wythoff_sweep/**/*.vZome` plus the master regular folders.
4. Emit any genuinely-new shapes to `ongoing_work/h4_600cell_rng4/`.

Original wall-time projection in the docstring: **~19 h**.

## What actually happened

| Item | Value |
|---|---|
| Started | 2026-05-06 16:21:54 |
| Killed | 2026-05-08 15:02:34 |
| Wall clock | **46.7 h** (~2.46× the original 19 h projection) |
| CPU consumed | 175,646 s ≈ 48.8 core-hours (single-threaded by design) |
| Peak memory | 3.85 GB resident (essentially flat in the last 8+ h) |
| Last py-spy stack | `numpy.searchsorted → _check_cos_pairs → _try_align → search` (the inner cosine-pair lattice-match hot loop) |
| Progress markers | None — the script does not print any intra-`search()` progress |

## Output produced

**None.**  The script never returned from line 59 (`search()` over the
21.5 M-direction set), so:
- No `ongoing_work/h4_600cell_rng4_kernels.json`
- No `ongoing_work/h4_600cell_rng4.json`
- `ongoing_work/h4_600cell_rng4/` directory is empty (0 .vZome files).

There is no salvageable partial result.

## Why we killed it

1. **Indeterminate remaining time.**  No progress logging, no ETA possible,
   we were already 2.46× past the projection.  Memory was flat for hours
   (post-snap hits-list not growing), suggesting late-phase compute, but
   we couldn't verify.
2. **Low expected scientific yield.**  Every other H4 audit at rng≤2 has
   produced 0 genuinely-new shapes (M19.audit round 1, round 2, novel-gap
   triage all settled to alias-of-existing).  The strongest empirical
   evidence collected so far points to the (1,0,0,0)-regular kernel
   inheritance being complete at rng=2; the rng=4 probe was a stress test
   with no concrete prior reason to expect new shapes on the 600-cell
   specifically.
3. **CPU contention.**  Holding a core away from `audit_h4` polytope 5/5
   (the more structured remaining work) had no upside.

## What this leaves unanswered

- Whether any rng=4 kernel direction on the 600-cell yields a zomeable
  shape that's not in the existing manifest.  (Most likely: no.)
- Whether Z[φ] kernels with coefficients in `{-φ², -φ, -1/φ, -1, 0, 1,
  1/φ, φ, φ²}` ranges (rng=4 covers larger combinations, see
  `lib/search_engine.py: gen_dirs`) reveal new directions that the
  rng=2-only production sweep misses.

## How to resume cheaply if needed

If a future researcher wants this evidence, suggested approach:
1. **Add intra-`search()` progress logging first** so we can estimate ETA
   and not repeat the "kill blindly" situation.  Per the user's request,
   any future probe expected to take >10 min must print
   `[HH:MM:SS] kernel i/N (p%)` on a sub-loop boundary.
2. Consider running smaller `rng` first (rng=3 → ~5 M dirs; about 1/4 of
   rng=4) as an interpolation between rng=2 (cheap) and rng=4 (expensive).
3. The 600-cell is the smallest H4 polytope (V=120 E=720), so it remains
   the cheapest target for an rng=4 H4 probe.  Other H4 polytopes at
   rng=4 are projected to be days each.
4. Direct snap-fail probe: rather than full rng=4 search, target the
   specific snap-fail kernels found in the rng=2 sweep (`output/wythoff_sweep/manifest.json`
   `status=snap_failed` entries) and check whether nearby Z[φ]
   directions snap cleanly.  Much cheaper, narrower scope.

## Related todos

- `kernel-completeness-fix` (pending): the inheritance-assumption refactor.
  This probe was *one* line of evidence for that.  Its absence does not
  block kernel-completeness-fix; the rng=2 evidence collected via
  `blind_spot_audit*.py` and `audit_h4` already bounds the empirical
  uncertainty.
- `rng-sweep-extension` (pending): explicitly tracks broader-rng work.
  After this kill, that todo should note "h4_600c rng=4 attempted on
  2026-05-06 → 2026-05-08, killed at 46.7h with no result; consider
  cheaper rng=3 first."
