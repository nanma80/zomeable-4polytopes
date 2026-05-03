# Wythoff sweep status — resume notes

## State (current)
- Branch: `wip/wythoff-sweep` — fully pushed
- Step 1 (regular-polytope kernels at rng=2): complete for all four
  groups, cached at `ongoing_work/kernels_<group>_rng2.npy` (gitignored)
  - A4: 324 hits, B4: 2640, F4: 608, H4: 432
- Step 2 (Wythoff variants vs group kernels): **46 of 47** complete
  - A4: 9/9, B4: 15/15, F4: 8/8 (24-cell ≡ B4 (0,0,1,0)), H4: 14/15
  - **H4 (1,1,1,1) omnitruncated 120-cell still TODO** — see below
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
  infinite split-cuboid family.
- **B4/F4 snap_failed cases**: structural, not tunable.  These
  projections place balls in `ℤ[√2]³` (silver ratio); `√2 ∉ Q(φ)` so
  vZome cannot represent them at any rational scale.

## Open issue: H4 omnitruncated 120-cell (V=14400) — RAM blow-up

A `--bitmask 1111` background run was killed at ~43 GB RSS with no
per-polytope output, well above the safe envelope on a 64 GB box.
Diagnosis: the search is doing 432 `shape_fingerprint` calls in the
inner loop on n_balls ≈ 14400 (no symmetry-induced ball collapse for
this polytope, unlike the 7200-vertex H4 forms which dedup to ~3660
balls).  Each chunked-Gram + sort pass peaks at ~3 GB but numpy's
arena allocator never returns memory to the OS, and 432 successive
peaks accumulate into the resident-set despite the python-level
references being released.

### Suggested fix (when resuming)

Replace the "sort all pairwise squared distances" formulation in
`lib/search_engine.shape_fingerprint` with an incremental hash that
streams chunks without materialising the full distance vector.
Concretely:

1. For each chunked sub-matrix, quantise distances to 3 decimals.
2. Update a `collections.Counter` of quantised values.
3. After all chunks, hash `sorted(counter.items())` to derive
   `fp_hash`.

This drops peak per-call memory from `O(n_balls²)` to
`O(distinct_distances)` (typically `<< 100k` for these polytopes) and
removes the np.sort/np.concatenate temporaries that are pinning the
arena.  The fingerprint stays rotation+scale-invariant because the
quantised-distance multiset is unchanged.

Once that lands, re-run:
```powershell
$env:PYTHONUNBUFFERED = "1"; $env:OMP_NUM_THREADS = "8"
python -u tools\run_wythoff_sweep.py --rng 2 --group H4 --bitmask 1111 `
  --shapes-jsonl ongoing_work\shapes_rng2_H4_1111.jsonl `
  --log ongoing_work\sweep_log_rng2_H4_1111.txt 2>&1 | Tee-Object ongoing_work\sweep_log_rng2_H4_1111_console.txt
```
then append the JSONL into the main file and re-run analyze + emit
(same step list as below).

## When the H4 (1,1,1,1) job finishes
1. Append `ongoing_work/shapes_rng2_H4_1111.jsonl` to
   `ongoing_work/shapes_rng2.jsonl`.
2. `python -u tools/analyze_sweep.py --rng 2 --out-novel ongoing_work/novel_rng2.json`
3. `python -u tools/emit_novel.py --rng 2`
4. Update the H4 table row in `docs/WYTHOFF_SWEEP.md`.
5. Commit + push.

