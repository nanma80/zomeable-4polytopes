# Gosset projection methodology

This page records the method used for the related
[`output/gosset_projections/`](../output/gosset_projections/) collection.

The models are not 4-polytopes.  They are strict orthographic zomeable
projections of the Gosset polytopes:

| Polytope | Natural dimension | Models |
|---|---:|---:|
| `2_21` | 6 | 2 |
| `3_21` | 7 | 5 |
| `4_21` | 8 | 3 |

## Raw-column sweep

The successful unified sweep searches the raw columns of a projection matrix

```text
P = [c_0 ... c_7],  c_i in Z[phi]^3.
```

For a coefficient range `R`, each coordinate of each column is
`a + b phi` with `|a| <= R` and `|b| <= R`.

The sweep is not targeted at the H3 cases.  It uses only the E8 root
constraints and strict orthographicity:

1. For E8 roots of the form `+/- e_i +/- e_j`, require `c_i + c_j` and
   `c_i - c_j` to be parallel to zometool axes or to collapse.
2. Enumerate compatible 8-column tuples.
3. Require exact `P P^T = c I_3` in `Z[phi]`.
4. Check the 128 half-root sums of E8.
5. Collect strict rank-3 images for all `4_21`, all `3_21` vertex figures,
   and all `2_21` vertex figures.

## Saturation runs

| Range | Runtime | Leaves | Result |
|---:|---:|---:|---|
| R=2 | 0.98 h | 190,459,868 | all 10 labelled models |
| R=3 | 47.49 h | 19,816,930,273 | same 10 labelled models; no new models |

The R=3 leaf estimator predicted `1.960e10 +/- 1.828e8` leaves, close to the
actual `1.982e10` leaves.

## Symmetry labels

The public captions use full Euclidean point-cloud symmetry:

- `B3-symmetric` means full octahedral symmetry, full order 48.
- `H3-symmetric` means full icosahedral symmetry, full order 120.

The computed symmetry audit is in
[`output/gosset_projections/symmetry_analysis.json`](../output/gosset_projections/symmetry_analysis.json).

