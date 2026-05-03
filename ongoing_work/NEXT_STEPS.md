# Resume Wythoff sweep on new machine

## State at pause
- Branch: `wip/wythoff-sweep` (commit 1997f6d + this file)
- Step 1 (regular-polytope kernels at rng=2): **complete** for A4/B4/F4/H4
  - A4: 324 hits, B4: 2640, F4: 608, H4: 432
- Step 2 (Wythoff variants vs group kernels): **partial**
  - All 9 A4 forms: done
  - All 15 B4 forms: done
  - F4: 4 of 9 done (rectified, truncated, cantellated, bitruncated 24-cell)
  - F4 remaining: cantitruncated, runcinated, runcitruncated, omnitruncated 24-cell, snub-24 (which is B4 (0,0,1,0) duplicate, already covered)
  - H4: 0 of 15 done
- Partial log: `ongoing_work/sweep_log_rng2_run1.txt`

## Caveats observed in partial results
- **B4 tesseract reports 32 distinct shapes** at rng=2 (vs 3 for all other B4 forms).
  This is suspect — likely the search hits include kernels that coincidentally
  match for the highly-symmetric tesseract but not its derivatives. Needs
  manual review when sweep resumes.
- F4 cantellated 24-cell took 1469s (24 min) — H4 forms with similar V/E
  counts (cantellated 600-cell, omnitruncated 120-cell ~14400 verts) will
  likely take many hours each. Consider:
  1. Reducing kernel set with shape-fingerprint dedup *before* step 2
  2. Running per-group separately (--group F4, --group H4)
  3. Caching step 1 kernels to disk

## To resume
```powershell
cd zomeable-4polytopes
git checkout wip/wythoff-sweep
git pull
# Recommended: refactor run_wythoff_sweep.py first to:
#  (a) accept --group A4|B4|F4|H4
#  (b) cache step 1 kernels to ongoing_work/kernels_<group>.npy
#  (c) skip already-done polytopes if log exists
# Then:
python tools/run_wythoff_sweep.py --group F4 --rng 2
python tools/run_wythoff_sweep.py --group H4 --rng 2
```

## Then
- Identify novel shapes (compare against the 8 known: 6 regulars + snub24 + GA)
- Emit .vZome files for novel shapes (`tools/emit_*.py` patterns)
- Update README results table
- Document census in `docs/WYTHOFF_SWEEP.md`
