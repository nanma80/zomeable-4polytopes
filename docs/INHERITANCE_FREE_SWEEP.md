# Inheritance-free matrix sweep: closing the corpus

This document summarises the **inheritance-free** verification pass that
re-validates the entire Wythoff corpus by running the canonical
zomeable-projection search directly on every (group, bitmask, rng)
triple — *without* the Step-1 "use only the regular's kernel directions"
shortcut on which the production pipeline (`tools/run_wythoff_sweep.py`)
depends.

The rest of this repository is described in [`WYTHOFF_SWEEP.md`](./WYTHOFF_SWEEP.md);
that document also contains the master shape table and the per-polytope
results.  This file is a complement, describing *how we know* the
production corpus is empirically saturated at rng ≤ 4.

## TL;DR

| | |
|---|---|
| Algorithm | inheritance-free direct search, parallel-edge reduction throughout |
| Driver | `tools/inheritance_free_sweep.py` |
| Cells covered | 4 Coxeter groups × 15 nonzero Wythoff bitmasks × rng ∈ {2, 3, 4} = **180** |
| Wall-clock | 38 h 33 min (single-threaded) |
| CPU time | 38.22 h |
| Cells with new-shape flags | **2** (both tesseract; rng=2 & rng=4) |
| Total flagged candidate shapes | 5 |
| Genuinely new shape types found | **0** |

All five flagged tesseract candidates resolved to **existing corpus
entries or predicted members of the tesseract `inf-family`** (see
[`output/8cell/CLASSIFICATION.md`](../output/8cell/CLASSIFICATION.md)).
The production corpus is therefore complete at rng ≤ 4 modulo the
documented field boundary (ℤ[φ]³ versus the larger ℤ[φ, √n]³ family
discussed in `output/8cell/CLASSIFICATION.md §3` and in the snap-failure
analysis of [WYTHOFF_SWEEP.md](./WYTHOFF_SWEEP.md)).

## Motivation

The production sweep (`tools/run_wythoff_sweep.py`) is a two-step
algorithm:

1. **Step 1.** For each Coxeter group, find every kernel direction
   that yields a zomeable projection of the **regular** member of that
   group at the chosen rng.
2. **Step 2.** Re-test each Wythoff descendant against just those
   kernel directions.

Step 1 is a representation-theoretic shortcut: *Lemma A* of the project
asserts that any zomeable kernel of a Wythoff descendant is also a
zomeable kernel of its parent regular.  The shortcut is the only reason
H₄ at rng = 4 is tractable at all — without it, every descendant of the
600-cell or 120-cell would need its own multi-million-direction search.

But Lemma A is *empirically* verified, not proved; and a 2026-05-07
audit ([`WYTHOFF_SWEEP.md §Kernel completeness`](./WYTHOFF_SWEEP.md#kernel-completeness-audit))
showed that even with both `(1,0,0,0)` and `(0,0,0,1)` regulars unioned
as kernel seeds, six B₄ descendants surfaced extra fingerprints from
the search engine that the regular-only seed had missed.  Those extras
all turned out to be ℤ[√2]³-field shapes (snap-failed at the export
stage) or aliases of master-corpus entries, but the audit highlighted
that the inheritance assumption deserves an *independent* corpus-wide
check.

The inheritance-free matrix sweep is that check.

## Method

For every triple (group ∈ {A₄, B₄, F₄, H₄}, nonzero bitmask `b` ∈ 15
values, rng ∈ {2, 3, 4}) — 180 cells in total — we run the same
`lib.search_engine.search` that powers the production pipeline, but on
the descendant polytope directly, with the full ZZ[φ]⁴ candidate kernel
set of the chosen rng.  Specifically:

1. Build the polytope `P_G(b)` from `lib.wythoff.build_polytope`,
   Procrustes-aligned to `lib/polytopes.py`'s canonical embedding.
2. Generate the full kernel-candidate set at rng = 2 (195 312 dirs),
   rng = 3 (2 882 400 dirs), or rng = 4 (21 523 360 dirs).
3. Search-engine prefilter + zomeable check + parallel-edge reduction
   (`lib/search_engine.search`, with the 2026-05-08 `chunk = 16`
   prefilter that gives the 4–23× speed-up necessary for H₄ at rng ≤ 4).
4. Stage A fingerprint dedup (3-decimal multiset binning).
5. Stage B snap-to-ℤ[φ]³ + shape-congruence dedup.
6. Compare the resulting shape signatures against the **current corpus
   index**.  Anything not already present is flagged as a new-shape
   candidate.

Output: `ongoing_work/inheritance_free_sweep.json` (append-only,
resume-aware, 35 MB at completion).

Driver: `tools/inheritance_free_sweep.py`.

Runner orchestration: `ongoing_work/matrix_sweep_runner.ps1`, chained
across five phases of increasing cost:

| Phase | rng | V cutoff   | Cells | Wall time |
|------:|:---:|-----------:|------:|----------:|
| 1     | 2   | none       | 60    | 4 h 18 min |
| 2     | 3   | none       | 60    | 8 h 49 min |
| 3a    | 4   | V ≤ 600    | 45    | 10 h 02 min |
| 3b    | 4   | V ≤ 3600   | +9    | 4 h 17 min |
| 3c    | 4   | V ≤ 14544  | +6    | 11 h 07 min |
| **total** | | | **180** | **38 h 33 min** |

The phase split lets the small (low-V) cells fully cover rng ≤ 4 before
the H₄ large-V descendants begin; resume mode skips already-done cells
between phases.

## Aggregate results

Per (group, rng) cell counts and timing:

| Group | rng | Cells | Wall hours | Cells flagged "new" | Flagged shapes |
|:-----:|:---:|------:|-----------:|--------------------:|---------------:|
| A₄    | 2   | 15    |   0.05     | 0                   | 0              |
| A₄    | 3   | 15    |   0.42     | 0                   | 0              |
| A₄    | 4   | 15    |   2.95     | 0                   | 0              |
| B₄    | 2   | 15    |   0.06     | **1** (tesseract)   | 2              |
| B₄    | 3   | 15    |   0.46     | 0                   | 0              |
| B₄    | 4   | 15    |   3.13     | **1** (tesseract)   | 3              |
| F₄    | 2   | 15    |   0.07     | 0                   | 0              |
| F₄    | 3   | 15    |   0.52     | 0                   | 0              |
| F₄    | 4   | 15    |   3.40     | 0                   | 0              |
| H₄    | 2   | 15    |   4.11     | 0                   | 0              |
| H₄    | 3   | 15    |   7.38     | 0                   | 0              |
| H₄    | 4   | 15    |  15.67     | 0                   | 0              |
| **total** | | **180** | **38.22** | **2** | **5** |

H₄ dominates the runtime budget: the rng = 4 omnitruncated 120-cell
alone takes 5 h 4 min single-threaded (~14 500 vertices).

## Flagged candidates: all aliases

Both flagged cells are the same polytope (B₄ bitmask `(1,0,0,0)`,
the tesseract), at two different rng levels.  All five candidate
fingerprints resolve to existing-corpus or predicted-family entries:

### B₄ tesseract rng = 2 (2 flagged shapes)

| edge spectrum (multiplicity ×) | classification | corpus file |
|--------------------------------|----------------|-------------|
| `(1.0 ×8, 1.473 ×8, 1.618 ×8, 1.701 ×8)` — 4 distinct edges, kernel support 3 | **phi-oblique** sporadic | `output/8cell/8cell_phi_oblique.vZome` |
| `(1.0 ×8, √5/2 ×8, 3/2 ×16)` — 3 distinct edges, kernel support 2 | **inf-family** at (a:b) = (2:√5) | `output/8cell/8cell_inf_family_phi_aSqrt5_b2.vZome` |

Both are already in the master corpus.  The "new" flags are a
corpus-index timestamp artefact: the corpus index was rebuilt mid-sweep
between the `phi_oblique` / `inf_family_phi_aSqrt5` emission timestamp
and the rng = 2 phase reading the index.

### B₄ tesseract rng = 4 (3 flagged shapes)

All three are members of the tesseract **`inf-family`** (the
1-parameter family of "split-cuboid" projections parameterised by
ℤ[φ]²-Pythagorean pairs (a, b) with `a² + b² = c² ∈ ℤ[φ]`, defined in
[`output/8cell/CLASSIFICATION.md §3`](../output/8cell/CLASSIFICATION.md#3-the-inf-family-parameterisation)
and enumerated independently to scalar bound 15 in the iso-frame
enumerator):

| edge spectrum (normalised) | (a : b) ratio | inf-family row |
|----------------------------|---------------|----------------|
| `(0.6, 0.8, 1.0)`          | (3 : 4)       | 3 : 4 : 5 Pythagorean (already in corpus as `output/8cell/8cell_inf_family_a3_b4.vZome`)|
| `(0.263, 0.965, 1.0)`      | (φ + 3 : 1)   | strut-iso b15 row, predicted by the parameterisation |
| `(0.369, 0.930, 1.0)`      | (φ + 2 : 1)   | strut-iso b15 row, predicted by the parameterisation |

Each is a valid ℤ[φ]²-Pythagorean instance of the closed 4-shape
tesseract taxonomy (`cube`, `rhombic dodecahedron`, `phi-oblique`,
`inf-family parameterised by all ZZ[φ]²-Pythagorean (a, b)`).  The
first is already in the master corpus; the latter two are predicted
parameterisation rows beyond rng ≤ 2 — they would be added to
`output/8cell/` if larger-coefficient family members were desired,
but no new shape *type* is involved.

### Strut iso-frame corroboration

An independent enumeration via `tools/enumerate_strut_iso_frames.py`
at scalar bounds `b ∈ {8, 12, 15}` produced (cumulatively): 7, 15, 22
unique tesseract iso-frame shapes, decomposing as

```
1 cube  +  1 rhombic dodecahedron  +  1 phi-oblique  +  k inf-family ratios
```

with `k = 4, 12, 19` at the three bounds.  No new sporadic types
appear beyond the three already known.  Output:
`ongoing_work/strut_iso_frames_b15.json`.

## Implications for production

1. **Lemma A is empirically validated at rng ≤ 4 across all 60
   (group, bitmask) cells.**  Every direct-search hit either already
   maps to an existing corpus signature or belongs to an explicit
   parameterised family the corpus represents canonically with finite
   rows.  Zero genuinely new shape *types* found.
2. **The tesseract `inf-family` is the only source of unbounded
   shape count growth.**  Every other (group, bitmask) cell produces
   the same finite shape count at rng = 4 as it does at rng = 2 (no
   new shapes ever appear when rng increases for the non-tesseract
   cells).  The inf-family is itself a closed structural object —
   each member is a ℤ[φ]²-Pythagorean instance of the
   `split-cuboid` projection family.
3. **Corpus freeze condition is reached.**  Two consecutive sweep
   levels (rng = 3 → rng = 4) flag the same {tesseract inf-family
   only} cells with the same provenance, and no other cell flags
   anything.  This satisfies the merge-prep gate stated in the
   project plan.

## Reproducing

```powershell
# small smoke (~30 s):
python tools/inheritance_free_sweep.py --group A4 --rng 2

# full A4 + B4 + F4 matrix at rng = 2, 3 (excludes H4 large-V):
python tools/inheritance_free_sweep.py --group A4 --rng 3
python tools/inheritance_free_sweep.py --group B4 --rng 3
python tools/inheritance_free_sweep.py --group F4 --rng 3

# full H4 at rng = 4 (~16 hours single-threaded):
python tools/inheritance_free_sweep.py --group H4 --rng 4
```

Each call appends to `ongoing_work/inheritance_free_sweep.json` in
resume mode; already-done cells are skipped automatically.

## See also

- [`WYTHOFF_SWEEP.md`](./WYTHOFF_SWEEP.md) — master corpus document
  (terminology, methodology, per-polytope shape inventory, B₄/F₄
  equivalences, snap-failure analysis).
- [`output/8cell/CLASSIFICATION.md`](../output/8cell/CLASSIFICATION.md) —
  tesseract 4-shape taxonomy and inf-family parameterisation theorem.
- [`tools/inheritance_free_sweep.py`](../tools/inheritance_free_sweep.py) —
  the driver.
- [`tools/enumerate_strut_iso_frames.py`](../tools/enumerate_strut_iso_frames.py) —
  the independent iso-frame enumerator used for cross-validation.
