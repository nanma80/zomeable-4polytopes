# M19.kc — Tesseract corpus has 2 missing zomeable Z[φ]³ projections

**Date:** 2026-05-08

## Finding

The kernel-completeness sweep triage (`ongoing_work/probes/triage_b4_kc_unrec.py`)
discovered that the **master corpus folder `output/8cell/` is missing 2 zomeable
Z[φ]³ tesseract projections** that the production sweep has been finding all
along.  These are NOT brought in by the kernel-completeness fix (they were
already in the `(1,0,0,0)`-only sweep at rng=2); they're a *curatorial gap*
exposed only when post-snap shape-signature comparison was added.

## Comprehensive triage across ALL regulars

`triage_regulars_kc.py` (run 2026-05-08) emits + post-snaps every
sweep-found fp_hash for every regular bitmask, and compares against
master corpus + manifest sigs.

| group, bitmask | master corpus dir | sweep fp_hashes | result |
|---|---|---|---|
| A4 (1,0,0,0) 5-cell | output/5cell/ | 4 | 4 master_corpus_alias — complete |
| A4 (0,0,0,1) 5-cell-dual | output/5cell/ | 0 (KNOWN_DUPLICATE) | n/a |
| B4 (1,0,0,0) **tesseract** | output/8cell/ | 32 | 26 emit_fail + 3 master_alias + **3 genuinely_new fp → 2 unique sigs** |
| B4 (0,0,0,1) 16-cell | output/16cell/ | 6 | 6 master_alias — complete |
| F4 (1,0,0,0) 24-cell | output/24cell/ | 0 (KNOWN_DUPLICATE → B4 (0,0,1,0)) | n/a |
| F4 (0,0,0,1) 24-cell-dual | output/24cell/ | 0 (skipped) | n/a |
| H4 (1,0,0,0) 120-cell | output/120cell/ | 1 | 1 master_alias — complete |
| H4 (0,0,0,1) 600-cell | output/600cell/ | 1 | 1 master_alias — complete |

(For B4 (0,0,1,0) 24-cell — F4-symmetric — the kc-union sweep found 3
fp_hashes, all 3 master_alias.  So the F4 24-cell coverage path is also
complete via B4 (0,0,1,0).)

**Only the tesseract has a corpus gap** (2 missing post-snap shapes).
Note: `2c105cd47b7fbae6` (sig `88c5...`), `a0ee41c578607b71` (sig
`0934...`), `4e20907c357f1b5c` (sig `0934...`) — the latter two are
kernel-direction aliases of the same Z[φ]³ shape, so really 2 unique
shapes from 3 fp_hashes.



| post-snap sig | example pre-snap fp | label/subtype | example kernel | n_balls |
|---|---|---|---|---|
| `(16, 32, 88c5a53810074918)` | `2c105cd47b7fbae6` | `oblique` | `[0, 0.381966, 1.0, -0.618034]` | 16 |
| `(16, 32, 093484beea6aecaf)` | `a0ee41c578607b71` (also `4e20907c357f1b5c`) | `face_first square` | `[0, 0, 2.236068, 2.0]` | 16 |

Both are V=16 E=32 Z[φ]³ tesseract projections (full vertex count, no folding).
Snapped vZome files staged at:

- `ongoing_work/triage_b4_kc_emitted/tesseract/kc_triage_2c105cd47b.vZome`
- `ongoing_work/triage_b4_kc_emitted/tesseract/kc_triage_a0ee41c578.vZome`

## Why was this missed?

The `tools/run_wythoff_sweep.py` pipeline only **promotes novel shapes** to the
`output/wythoff_sweep/` folders — and "novel" is defined as "not in master corpus
or manifest".  But the master-corpus comparison was never wired up for *regular*
polytopes:

- `output/8cell/` is **hand-curated** (cell_first_cube, vertex_first_rhombic_dodec,
  plus 5 inf_family_*.vZome rational-coord parameterized projections).
- The sweep's 32 fp_hashes for tesseract were dumped to JSONL but never
  programmatically compared against master corpus.
- The novel-shape pipeline (`tools/emit_novel.py`) doesn't even include
  regulars — they're presumed to be human-curated.

## Existing tesseract corpus (output/8cell/)

| File | V | E | post-snap sig | parseable |
|---|---|---|---|---|
| `8cell_cell_first_cube.vZome` | 8 | 12 | `a39e6d81f909a25b` | yes |
| `8cell_vertex_first_rhombic_dodec.vZome` | 15 | 32 | `d6b0c39fff08a0cf` | yes |
| `8cell_inf_family_a1_b2.vZome` | 16 | 32 | `3ff0df8f4b8d45a2` | yes |
| `8cell_inf_family_a19_b22.vZome` | n/a | n/a | n/a | NO (`82/65` rational coord) |
| `8cell_inf_family_a2_b11.vZome` | n/a | n/a | n/a | NO (rational) |
| `8cell_inf_family_a2_b29.vZome` | n/a | n/a | n/a | NO (rational) |
| `8cell_inf_family_a3_b4.vZome` | n/a | n/a | n/a | NO (rational) |
| `8cell_inf_family_a5_b12.vZome` | n/a | n/a | n/a | NO (rational) |
| `8cell_inf_family_a8_b15.vZome` | n/a | n/a | n/a | NO (rational) |

The 6 inf_family `.vZome` files use `Q\(non-Z[φ]\)` rational coords (e.g.
`-18/25`, `82/65`); they won't be congruent to the new Z[φ]³ shapes.

## Verification trail

1. Built `ongoing_work/master_corpus_signatures.json` cache for all parseable
   master-corpus `.vZome` files (`build_master_corpus_signatures.py`).  22
   entries across 8 polytope folders.
2. Ran `triage_b4_kc_unrec.py`: emitted each unrecognised B4 fp_hash via
   `emit_one`, computed post-snap `shape_signature`, compared vs master corpus
   + manifest.
3. **53 unrecognised B4 fp_hashes** (sweep total minus manifest+aliases):
   - 30 `emit_fail` (could not snap to Z[φ]³ — search-engine false positives)
   - 12 `master_corpus_alias` (e.g. cube, rhombic-dodec, 16-cell antiprisms,
     24-cell triality)
   - 9 `manifest_alias` (rect tess oblique_00..02, bitr tess oblique_00..02,
     trunc 16-cell oblique_00..02)
   - **2 `genuinely_new` for tesseract** (this finding)
4. Cross-verified by `Path("output").rglob("*.vZome")` + `shape_signature`:
   no existing file in `output/` matches the 2 new sigs (`88c5...`,
   `0934...`).
5. Confirmed both fp_hashes were present in the **OLD** `(1,0,0,0)`-only B4
   sweep (`shapes_rng2_B4.jsonl` from 2026-05-03) — i.e. **NOT** introduced by
   the kernel-completeness fix; they've been in sweep output since the
   original Wythoff-sweep ran.

## Decision required

These 2 shapes are real Z[φ]³ tesseract projections that meet the same
zomeable criteria as `8cell_cell_first_cube.vZome` and
`8cell_vertex_first_rhombic_dodec.vZome`.  Adding them is a *corpus extension*,
not a sweep bug.  Possible names (using the existing 8cell naming scheme):

| sig | suggested filename |
|---|---|
| `88c5...` | `8cell_oblique_<unique>.vZome` |
| `0934...` | `8cell_face_first_square.vZome` |

**User action**: decide whether to add these 2 files to `output/8cell/` and
under what filenames.  This was deferred from the autonomous session
(2026-05-08) because corpus extensions are curatorial decisions.

## Methodology consequence

The sweep should have a **regular-polytope gap-detection pass** as part of
the standard pipeline:

1. After running the sweep, for each regular polytope in the work-list,
   triage its sweep fp_hashes via `emit_one` + `shape_signature`.
2. Compare against master corpus (`output/<polytope>/*.vZome`) and manifest.
3. Report unrecognised post-snap sigs as "regular-corpus gap candidates".

This same audit should be re-run for **A4 5-cell** (4 fp_hashes — likely
all in `output/5cell/`), **F4 24-cell** (skipped by KNOWN_DUPLICATES at
sweep time, would need fresh run), **H4 120-cell** (1 fp_hash), **H4
600-cell** (1 fp_hash).  Likely outcome: most regulars are complete or
have only 1-2 missing canonicals.

## Files referenced

- `ongoing_work/probes/build_master_corpus_signatures.py`
- `ongoing_work/probes/triage_b4_kc_unrec.py`
- `ongoing_work/probes/scan_regulars_sweep_fps.py`
- `ongoing_work/master_corpus_signatures.json`
- `ongoing_work/triage_b4_kc_unrec.json`
- `ongoing_work/triage_b4_kc_emitted/tesseract/` (staged .vZome files)
- `ongoing_work/shapes_rng2_B4.jsonl` (May 3 old sweep — also has these fp_hashes)
- `ongoing_work/shapes_rng2_B4_kc.jsonl` (May 8 new sweep with kc-fix)
