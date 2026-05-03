# Wythoff sweep status — resume notes

## State (current)
- Branch: `wip/wythoff-sweep` — fully pushed
- Step 1 (regular-polytope kernels at rng=2): complete for all four
  groups, cached at `ongoing_work/kernels_<group>_rng2.npy` (gitignored)
  - A4: 324 hits, B4: 2640, F4: 608, H4: 432
- Step 2 (Wythoff variants vs group kernels): **46 of 47** complete
  - A4: 9/9, B4: 15/15, F4: 8/8 (24-cell ≡ B4 (0,0,1,0)), H4: 14/15
  - Last polytope still running on the 24-core box: H4 (1,1,1,1)
    omnitruncated 120-cell (V=14400, E=28800).  Background shell:
    `h4_1111`, log: `ongoing_work/sweep_log_rng2_H4_1111.txt`,
    JSONL: `ongoing_work/shapes_rng2_H4_1111.jsonl`.  Expected to
    complete in another few hours.
- Aggregate JSONL: `ongoing_work/shapes_rng2.jsonl` (48 records)
- Novel inventory: `ongoing_work/novel_rng2.json` — 170 distinct novel
  fp_hashes
- vZome output: `output/wythoff_sweep/` — 143 .vZome files +
  manifest.json (snap rates: A4 100%, B4 38%, F4 35%, H4 100%)
- Census documented in `docs/WYTHOFF_SWEEP.md`; reproduction commands
  in the README.

## Resolved caveats
- **B4 tesseract 32 shapes**: confirmed correct, not a bug.  Documented
  in `output/8cell/CLASSIFICATION.md` as the rng=2 truncation of an
  infinite split-cuboid family.  A B4-only consequence of the
  4D-coordinate-aligned tesseract edge directions.
- **B4/F4 snap_failed cases**: structural, not tunable.  These
  projections place balls in `ℤ[√2]³` (silver ratio); `√2 ∉ Q(φ)` so
  vZome cannot represent them at any rational scale.

## When the H4 (1,1,1,1) job finishes
1. Append `ongoing_work/shapes_rng2_H4_1111.jsonl` to
   `ongoing_work/shapes_rng2.jsonl`.
2. `python -u tools/analyze_sweep.py --rng 2 --out-novel ongoing_work/novel_rng2.json`
3. `python -u tools/emit_novel.py --rng 2`
4. Update the H4 table row in `docs/WYTHOFF_SWEEP.md`.
5. Commit + push.
