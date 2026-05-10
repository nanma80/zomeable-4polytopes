# Wythoff sweep status — resume notes

## Terminology pointer
The codebase identifier `novel` (e.g. `tools/emit_novel.py`,
`novel_rng2.json`, the `[NOVEL]` tag in `analyze_sweep.py`) means
*"Wythoff projection whose 3D shape is not congruent to any of the 6
regulars' own projections"* — a redundancy filter only.  Under the
stronger structural definition ("a shape NOT obtainable by projecting
some Wythoff variant under a kernel inherited from a regular"), the set
is **provably empty by Lemma A**, so all 60 corpus shapes are
**natural Wythoff extensions** of regular polytope projections.  See
`docs/WYTHOFF_SWEEP.md#terminology-natural-vs-novel`.

## State (current)
- Branch: `wip/wythoff-sweep` — fully pushed
- Step 1 (regular-polytope kernels at rng=2): complete for all four
  groups, cached at `ongoing_work/kernels_<group>_rng2.npy` (gitignored)
  - A4: 324 hits, B4: 2640, F4: 608, H4: 432
- Step 2 (Wythoff variants vs group kernels): **47 of 47** complete
  - A4: 9/9, B4: 15/15, F4: 8/8 (24-cell ≡ B4 (0,0,1,0)), H4: 15/15
- Aggregate JSONL: `ongoing_work/shapes_rng2.jsonl` (49 records)
- Natural-extension inventory (legacy filename
  `ongoing_work/novel_rng2.json`): 235 distinct fp_hashes (raw); 164
  after Stage A (kernel-direction dedup); **60 distinct after Stage B
  (3D shape-congruence dedup)**
- vZome output: `output/wythoff_sweep/` — 60 .vZome files in
  per-polytope subfolders + manifest.json
  (per-group distinct after dedup: A4 32, B4 13, F4 2, H4 13)
- Census documented in `docs/WYTHOFF_SWEEP.md`.

## Resolved caveats
- **B4 tesseract 32 shapes** (regular tesseract analysis at
  `output/8cell/CLASSIFICATION.md`, separate from the Wythoff sweep):
  previously documented as a structural truncation of an infinite
  split-cuboid family.  Re-investigated with the new direction-dedup
  tool: of the 32, one is a spurious duplicate from Stage A of the
  fp_hash bug (see below); the post-Stage-A count is 31 (1 sporadic
  + 30 cuboid).  Stage B (3D shape-congruence) has *not* been re-run
  on this regular-tesseract catalogue; if applied it would likely
  collapse further (most of the 30 cuboid kernels are H4-orbit-
  equivalent).
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
  distance now lands within √φ ≈ 1.27 of a 30/φ² ≈ 11.5-zome-unit
  target across all 164 .vZome files.  ``tools/rescale_corpus.py``
  applies an in-place φᵏ rescale via integer ZZ[φ] transforms when the
  whole corpus needs to be uniformly rescaled (the user requested an
  additional φ⁻² scale-down for visual aesthetics; commit e6133dd).
- **Output organisation**: `tools/emit_novel.py` now writes each
  natural-extension shape into a subfolder named for the polytope's
  common name (e.g. `omnitruncated_120-cell/`), making the output tree
  browsable by Wythoff form.
- **Filenames**: `<label>[_<idx>]_<hash>.vZome`, where `label` is the
  kernel-direction classification (`vertex_first`, `cell_first_<celltype>`,
  `face_first_<polygon>`, `edge_first`, `oblique`).  Computed by
  `lib/polytope_features.py` (4D ConvexHull on V → cell groups by
  hyperplane → SVD-projected 3D ConvexHull → face groups → cell name
  via face-signature lookup).  Applied corpus-wide via
  `tools/rename_corpus.py`; wired into `tools/emit_novel.py` for future
  emits.
- **Spurious-fp_hash bug** has *two* failure modes; both now handled.
  `shape_fingerprint`'s SVD basis in `projection_matrix(n)` has a
  degenerate eigenvalue 1.0 (mult. 3), so its 3D output basis is
  sensitive to small FP noise in `n̂`.

  *Stage A — scalar-multiple kernels.*  Kernels that are positive
  scalar multiples of one another (e.g. `k` and `φ²·k`) round to
  slightly different unit vectors after low-precision storage and
  produce slightly different fp_hashes despite projecting to the SAME
  3D shape.  Effects: step-1 hit lists 3.5–7× over-counted (raw vs.
  distinct directions: A4 324→65, B4 2640→760, F4 608→120, H4 432→60);
  step-2 manifest had ~21% spurious duplicates (208→164 ok shapes).
  Fixes: direction-dedup in `find_group_kernels`,
  `emit_novel._dedup_by_direction`, repair via
  `tools/dedup_corpus_by_direction.py`.

  *Stage B — H4-orbit-equivalent kernels.*  Kernels that are *not*
  scalar multiples but lie in the same symmetry-group orbit produce
  rotation-related (rigid-motion equivalent) 3D shapes; their
  pairwise-distance multisets agree to FP precision but
  `shape_fingerprint`'s 3-decimal binning shifts on boundary values,
  yielding distinct fp_hashes.  This was the bigger bug: **104 of 164
  ok shapes were rigid-motion duplicates**, including 38→1 for the
  H₄ omnitruncated 120-cell.  Fixes:
    1. `tools/dedup_corpus_by_shape.py` reads each emitted .vZome,
       computes a robust geometric signature (sorted normalised
       pairwise-distance multiset + edge-length multiset), groups by
       (group, bitmask, signature), keeps the smallest-|kernel|
       canonical entry, deletes the rest, updates the manifest.
       Repaired the existing corpus in place; backup preserved at
       `manifest.json.preshapededup.bak`.  Idempotent.
    2. `tools/emit_novel.py` now invokes `dedup_manifest_by_shape`
       as a final post-emission pass, so future runs cannot leak
       orbit-equivalent duplicates into the corpus.
    3. `tools/audit_shape_duplicates.py` is the inspection-only
       counterpart (reports without deleting).

  The B4 tesseract "32 shapes" remark above belongs to the regular-
  tesseract catalogue and is *not* in the Wythoff sweep manifest;
  Stage B has not been applied there yet.

