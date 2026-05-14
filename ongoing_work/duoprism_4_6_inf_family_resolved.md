# duoprism_4_6 zomeable family size by sweep depth

| rng | kernel-count budget | raw hits | dir-deduped | unique shapes (snap-eligible) | **emitted** | snap-failed |
|-----|---------------------|----------|-------------|-------------------------------|-------------|-------------|
| 2   | 332,800             | -        | -           | 85                            | **1**       | 84          |
| 3   | 2,883,150           | -        | -           | 343                           | **3**       | 340         |
| 4   | 21,523,360          | -        | -           | 743                           | **3**       | 740         |
| 5   | 107,179,440         | 14,928   | 2,604       | 1,037                         | **3**       | 1,034       |

## Conclusion

**`duoprism_4_6` is NOT an infinite family.**

The directional-zomeable subset of (a, b, 0, 0) kernels grows unboundedly
(roughly quartic in rng), but the actual snap-emittable subset is **bounded
at 3 shapes**. The rng=5 sweep (107M candidate directions, ~84 min wall on a
single Python loop) emitted exactly the same 3 shapes that rng=3 found.

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

### Verdict (reconfirmed)

**duoprism_4_6 is BOUNDED at 3 shapes on the (a,b,0,0) plane.**  Snap-count
at rng=8 is 3.7× the rng=4 count yet the shape count is unchanged.  The
three rng=4 kernels found by the production sweep are the complete set; no
new shapes will appear at higher rng.
