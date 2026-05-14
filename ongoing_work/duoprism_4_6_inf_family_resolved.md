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
