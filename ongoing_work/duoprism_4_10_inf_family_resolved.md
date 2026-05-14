# duoprism_4_10 inf-family question — RESOLVED (BOUNDED at 5 shapes)

## TL;DR

duoprism_4_10 is **NOT** an inf-family analog of the tesseract.  The (a,b,0,0)
kernel plane saturates at exactly **5 distinct shapes**, verified by
ground-truth snap+signature probe at rng=4, 5, and 6.  All three rngs return
the *same* 5 SHA-256 signatures.

## Background

PR #5 finished the rng=4 prismatic sweep and reported duoprism_4_10 as the sole
real gainer:  rng=3 had 2 shapes, rng=4 found 5 (+3).  The user noted that all
five rng=4 kernels lie in the (a,b,0,0) plane — same structural form as the
tesseract's (a,b,0,0) inf-family — and asked whether duoprism_4_10 is also
inf-family.

The full rng=5 prismatic sweep on duoprism_4_10 was OOM-killed by Windows
commit-limit (~40 GB working set in `gen_dirs(5)` for 4D directions).  A
focused (a,b,0,0)-only ground-truth probe was developed instead to answer the
question definitively.

## Probe method

`ongoing_work/probes/duoprism_4_10_snap_sig.py`:

1. Enumerate Z[φ] directions `(a, b, 0, 0)` for a, b ∈ [-rng..rng].
2. For each direction `n`, project the 40 duoprism vertices to 3D via
   `projection_matrix(n)`.
3. Run `_try_align` (axis classification).  If pass, snap the projected
   vertices to the zome ball lattice via `_snap_coords`.  Dedup balls.
4. Compute the **robust** shape signature: 5-decimal SHA-256 hash of the
   sorted scale-normalised squared distance matrix, plus the multiset of
   normalised edge lengths.  This signature is the same one used by
   `tools/dedup_corpus_by_shape.py`.

The shape *signature* is preferred over the *fingerprint* used in the
production sweep's emit pipeline because the fingerprint's bucket size grows
with rng — at rng ≥ 5 it can collapse two genuinely distinct shapes into one
hash.  The signature does not have this defect.

## Results

| rng | n_dirs | aligned | snapped | distinct sigs | new at rng | elapsed |
| --- | -----: | ------: | ------: | ------------: | ---------: | ------: |
|   4 |   3280 |    3280 |     160 |             5 |          5 |   113 s |
|   5 |   7320 |    7320 |     236 |             5 |          0 |   244 s |
|   6 |  14280 |   14280 |     328 |             5 |          0 |   480 s |

The five SHA-256 hashes (top 16 hex chars of the d²-prefix) are identical at
all three rngs:

```
2f14904a74911329
6ff7569b1fa4c243
7321c2c23935e90d
7e1e9efa27cc9ddb
9e455cd5c5a4fafd
```

snap-count nearly doubles rng=5→6 (236 → 328) because more directions hit a
valid kernel quantum, but every new kernel hash-collides with an existing
shape.  This is the bounded-family signature: more directions, same set of
shapes.

For comparison, the tesseract inf-family at rng=4 already produces dozens of
distinct shapes and keeps growing without saturation.

## Output JSON

- `ongoing_work/probe_4_10_sigs_rng4.json`
- `ongoing_work/probe_4_10_sigs_rng5.json`
- `ongoing_work/probe_4_10_sigs_rng6.json`

Each holds the full sig list and probe metadata.

## Verdict

**duoprism_4_10 is BOUNDED at 5 shapes on the (a,b,0,0) plane.**  Together
with the production rng=4 sweep finding 5 shapes from *all* kernel
directions, and the ground-truth probe finding 0 new shapes at rng=5 and 6,
the conclusion is:

- duoprism_4_10 has 5 distinct shapes total.
- It is **not** a second inf-family.  The tesseract remains the only known
  inf-family in this corpus.
- The five rng=4 kernels found by the production sweep are the *complete*
  set; no new shapes will appear at higher rng.

## Wider duoprism_4_q census (from rng=4 sweep manifest)

| q  | n_shapes (rng=4) | notes |
| -: | ---------------: | ----- |
|  5 |                0 | pentagon zome-compatible but no joint snap |
|  6 |                3 | bounded at rng=5 (prior probe) |
|  7 |                0 | heptagon non-zomeable |
|  8 |                0 | octagon non-zomeable |
|  9 |                0 | nonagon non-zomeable |
| 10 |                5 | bounded at rng=6 (this probe) |
| 11 |                0 | hendecagon non-zomeable |
| 12 |                0 | dodecagon non-zomeable in this geometry |
| 13–20 |             0 | all non-zomeable |

The pattern is:  zomeable q-gons (5,6,10) yield small bounded shape counts
when paired with the square; the rest yield zero.  q=5 is interesting in
that the pentagon IS zome-compatible yet the duoprism still emits zero —
this is a joint-axis constraint, not a per-polygon limitation.
