# duoprism_4_6 inf-family question — corrected: infinite family exists

## 2026-05-29 correction

The earlier boundedness verdict below is **incorrect**.  It was based on the
finite snap/signature probe and its fixed alignment/scale search, not on a
constructive classification of the inf family.  The emitted
representative is:

```text
output/duoprisms/duoprism_4_6/duoprism_4_6_inf_family_a2-phi_b3phi-1.vZome
```

For `{4} x {6}` with kernel `n=(a,b,0,0)`, the preserved hexagon plane can use
two blue edge axes at 60 degrees; the perpendicular square-height axis is
yellow.  The blue/yellow length ratio contributes a `sqrt(3)` factor, so the
right snap condition is not the tesseract condition

```text
sqrt(a^2+b^2) in Q(phi),
```

but rather

```text
sqrt(3*(a^2+b^2)) in Q(phi).
```

This conic has `Q(phi)` points, for example

```text
a = 2 - phi,  b = -1 + 3 phi,
3*(a^2+b^2) = 45 = (3*sqrt(5))^2.
```

Using the blue hexagon edge frame scaled by `sqrt(3*(a^2+b^2))` and the yellow
height axis scaled by `2a`/`2b` gives all duoprism edges on zome axes.  Since a
conic over `Q(phi)` with one point has infinitely many points, `{4} x {6}` has
an inf family, though it is a **different arithmetic branch**
from the tesseract support-2 family.

The old rng tables remain useful as diagnostics for that particular probe, but
the "bounded at 3 shapes" interpretation is a false negative of the snap search.
The old text is retained below only as historical context.

| rng | kernel-count budget | raw hits | dir-deduped | unique shapes (snap-eligible) | **emitted** | snap-failed |
|-----|---------------------|----------|-------------|-------------------------------|-------------|-------------|
| 2   | 332,800             | -        | -           | 85                            | **1**       | 84          |
| 3   | 2,883,150           | -        | -           | 343                           | **3**       | 340         |
| 4   | 21,523,360          | -        | -           | 743                           | **3**       | 740         |
| 5   | 107,179,440         | 14,928   | 2,604       | 1,037                         | **3**       | 1,034       |

## Superseded conclusion

**Superseded: `duoprism_4_6` was previously thought not to be an infinite
family.**

The old finite probe found that its directional-zomeable subset of
`(a,b,0,0)` kernels grew quickly with `rng`, but its snap-emittable subset
stalled at 3 shapes.  That measured a limitation of the probe's snap/alignment
branch, not the mathematical family.

All 3 emitted kernels at every rng have form `(a, b, 0, 0)` — kernel lives
in the {4}-plane, hexagonal plane fully preserved. Geometrically these are
the 4 stacked regular hexagons at heights (±a, ±b).

The 3 emitted kernels are an independent low-norm `k₁` plus a Galois pair
`k₂` / `k₃` (under σ: φ → 1-φ).

## Contrast with `duoprism_4_10`

| rng | emit |
|-----|------|
| 3   | 2    |
| 4   | 5    |

`duoprism_4_10` *is* still growing at rng=4 (+3). It is now the
infinite-family candidate worth probing at rng=5 next.

## Reference

- Probe to summarise: `ongoing_work/probes/rng5_4_6_summary.py`
- Raw log: `ongoing_work/prismatic_rng4_progress.log` (rng=4),
  `ongoing_work/duoprism_4_6_rng5_progress.log` (rng=5)
- Records in `ongoing_work/prismatic_sweep_log.jsonl`,
  tagged with `"rng": 5` for the rng=5 record.

## Addendum — ground-truth snap+signature probe (rng=4..8)

A separate ground-truth (a,b,0,0)-plane snap+signature probe
(`ongoing_work/probes/duoprism_4q_snap_sig.py`) was run at rng=4..8 to
independently confirm saturation.  This uses the robust 5-decimal SHA-256
shape signature (the same one used by `tools/dedup_corpus_by_shape.py`),
which does *not* have the fingerprint-collapse defect at high rng.

| rng | n_dirs | aligned | snapped | distinct sigs | new at rng | elapsed |
| --- | -----: | ------: | ------: | ------------: | ---------: | ------: |
|   4 |   3280 |    3280 |     104 |             3 |          3 |   110 s |
|   5 |   7320 |    7320 |     160 |             3 |          0 |   238 s |
|   6 |  14280 |   14280 |     224 |             3 |          0 |   465 s |
|   7 |  25312 |   25312 |     304 |             3 |          0 |   820 s |
|   8 |  41760 |   41760 |     384 |             3 |          0 |  1382 s |

The three SHA-256 hashes (top 16 hex chars) are identical at every rng:

```
7fcae3177a93bf9b
c3f32d1a4889bc9a
f0de356895a7e439
```

snap-count grows monotonically with rng (104 → 384) because more directions
hit a valid kernel quantum, but every new kernel hash-collides with one of
the three existing shapes.

### Output JSON

- `ongoing_work/probe_4q_sigs_q6_ab00_rng{4,5,6,7,8}.json`

### Superseded verdict

**Superseded: the rng probe saturated at 3 probe signatures, but this was not a
proof of boundedness.**  The exact construction above gives a genuine infinite
family outside the probe's successful snap/alignment branch.
