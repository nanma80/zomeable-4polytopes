# Wythoff sweep status — resume notes

## State (current)
- Branch: `wip/wythoff-sweep` — fully pushed
- Step 1 (regular-polytope kernels at rng=2): complete for all four
  groups, cached at `ongoing_work/kernels_<group>_rng2.npy` (gitignored)
  - A4: 324 hits, B4: 2640, F4: 608, H4: 432
- Step 2 (Wythoff variants vs group kernels): **47 of 47** complete
  - A4: 9/9, B4: 15/15, F4: 8/8 (24-cell ≡ B4 (0,0,1,0)), H4: 15/15
- Aggregate JSONL: `ongoing_work/shapes_rng2.jsonl` (49 records)
- Novel inventory: `ongoing_work/novel_rng2.json` — 235 distinct novel
  fp_hashes
- vZome output: `output/wythoff_sweep/` — 208 .vZome files in
  per-polytope subfolders + manifest.json
  (snap rates: A4 100%, B4 38%, F4 35%, H4 100%)
- Census documented in `docs/WYTHOFF_SWEEP.md`.

## Resolved caveats
- **B4 tesseract 32 shapes**: confirmed correct, not a bug.  Documented
  in `output/8cell/CLASSIFICATION.md` as the rng=2 truncation of an
  infinite split-cuboid family.
- **B4/F4 snap_failed cases**: structural, not tunable.  These
  projections place balls in `ℤ[√2]³` (silver ratio); `√2 ∉ Q(φ)` so
  vZome cannot represent them at any rational scale.
- **H4 omnitruncated 120-cell (V=14400) RAM blow-up**: solved with
  the multiset shape-fingerprint path in
  `lib/search_engine.shape_fingerprint` (gates on `n_balls > 5000`).
  The original sort-tuple path peaked at ~43 GB RSS; the bincount
  multiset path stays under ~600 MB.  Run completed in 137 min CPU
  with 65 distinct shapes from 432 hits.
- **Inconsistent strut/ball ratio across the corpus**: solved with
  per-file `φᵏ` post-snap normalisation in
  `lib/emit_generic._normalize_scale`.  Smallest pairwise vertex
  distance now lands within √φ ≈ 1.27 of a 30-zome-unit target across
  all 208 .vZome files.
- **Output organisation**: `tools/emit_novel.py` now writes each
  novel shape into a subfolder named for the polytope's common name
  (e.g. `omnitruncated_120-cell/`), making the output tree browsable
  by Wythoff form.

