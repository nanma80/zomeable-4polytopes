# duoprism_4_10 inf-family question — corrected: infinite family exists

## 2026-05-29 correction

The boundedness verdict below is **incorrect**.  The focused snap/signature
probe was a false negative caused by the finite alignment/scale search; it did
not constitute a constructive classification of the inf family.

The emitted representatives are:

```text
output/duoprisms/duoprism_4_10/duoprism_4_10_inf_family_a5_b12.vZome
output/duoprisms/duoprism_4_10/duoprism_4_10_inf_family_a8_b15.vZome
```

For `{4} x {10}`, the preserved decagon can use blue edge axes in a plane
perpendicular to a red axis.  The decagon edge length is `1/phi` for the unit
radius model, and the blue/red length ratio is `2/sqrt(5)`, which lies in
`Q(phi)` because `sqrt(5)=2phi-1`.  Therefore the tesseract support-2 arithmetic
condition transfers:

```text
c = sqrt(a^2+b^2) in Q(phi).
```

For any such `(a,b,c)`, scale the blue decagon edge frame by `c` and put the
four square layers on the red height axis with scalar

```text
beta = phi * |blue| / |red| = 2phi/sqrt(5) = (4+2phi)/5.
```

The square edges have height differences proportional to `a+b` and `a-b`, so
they remain `Q(phi)` multiples of that red axis.  Example: `(a,b,c)=(3,4,5)`
gives a valid zome-axis `{4} x {10}` projection, and the usual infinite
`Q(phi)` Pythagorean triples give infinitely many projective ratios.

The old rng tables remain useful as diagnostics for that particular probe, but
the "bounded at 5 shapes" interpretation is not valid.  The old text is
retained below only as historical context.

## Superseded TL;DR

**Superseded:** `duoprism_4_10` was previously thought not to be an inf-family
analog of the tesseract.  The finite `(a,b,0,0)` snap probe saturated at 5
signatures, but that saturation was not a proof of boundedness.

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
|   7 |  25312 |   25312 |     444 |             5 |          0 |   854 s |
|   8 |  41760 |   41760 |     576 |             5 |          0 |  1388 s |

The five SHA-256 hashes (top 16 hex chars of the d²-prefix) are identical at
all five rngs:

```
2f14904a74911329
6ff7569b1fa4c243
7321c2c23935e90d
7e1e9efa27cc9ddb
9e455cd5c5a4fafd
```

The finite probe's snap-count kept growing with rng (160 → 236 → 328 → 444 →
576) because more directions hit a valid kernel quantum, but every new kernel
hash-collided with an existing probe signature.  This looked like a
bounded-family signature, but it only described the subset reached by that
probe's snap/alignment branch.

For comparison, the tesseract inf-family at rng=4 already produces dozens of
distinct shapes and keeps growing without saturation.

## Output JSON

- `ongoing_work/probe_4_10_sigs_rng{4,5,6}.json` (legacy q=10-only probe)
- `ongoing_work/probe_4q_sigs_q10_ab00_rng{4,7,8}.json` (generalised probe)

Each holds the full sig list and probe metadata.

## Superseded verdict

**Superseded: `duoprism_4_10` is not bounded at 5 shapes.**  The exact
construction above gives a genuine infinite family; the finite probe only
measured the subset reachable by its snap/alignment branch.

## Wider duoprism_4_q census (from rng=4 sweep manifest)

| q  | n_shapes (rng=4) | notes |
| -: | ---------------: | ----- |
|  5 |                0 | pentagon zome-compatible but no joint snap |
|  6 |                3 | finite-probe signatures at rng=5; exact infinite family now known |
|  7 |                0 | heptagon non-zomeable |
|  8 |                0 | octagon non-zomeable |
|  9 |                0 | nonagon non-zomeable |
| 10 |                5 | finite-probe signatures at rng=8; exact infinite family now known |
| 11 |                0 | hendecagon non-zomeable |
| 12 |                0 | dodecagon non-zomeable in this geometry |
| 13–20 |             0 | all non-zomeable |

The finite-probe pattern was: zomeable q-gons (5,6,10) yielded small apparent
shape counts when paired with the square; the rest yielded zero.  q=5 remains
interesting because the pentagon IS zome-compatible yet the duoprism emitted
zero in that sweep — this is a joint-axis constraint, not a per-polygon
limitation.
