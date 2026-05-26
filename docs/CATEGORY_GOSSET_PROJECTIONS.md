# Gosset orthographic projections

This is a related non-4D collection hosted in the same repository for
convenience and shared tooling.  These models are not part of the 4-polytope
category taxonomy; they are strict orthographic zomeable projections of the
Gosset-family polytopes 5-demicube (`1_21`), `2_21`, `1_22`, `3_21`, and
`2_31`, and `4_21`.

| Source polytope | Natural dimension | Models | Viewer |
|---|---:|---:|---|
| 5-demicube (`1_21`) | 5 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/VIEWER.html#1_21) |
| `2_21` | 6 | 2 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/VIEWER.html#2_21) |
| `1_22` | 6 | 2 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/VIEWER.html#1_22) |
| `3_21` | 7 | 5 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/VIEWER.html#3_21) |
| `2_31` | 7 | 5 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/VIEWER.html#2_31) |
| `4_21` | 8 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/VIEWER.html#4_21) |

All 20 labelled models are available in a flat folder:

- [`output/gosset_projections/`](../output/gosset_projections/)

The ball counts on the viewer page count distinct 3D ball positions after
projection, not vertices of the original higher-dimensional Gosset polytope.
Fourteen models have full B3/octahedral point-cloud symmetry; one 5-demicube
(`1_21`) model has full D4/tetragonal point-cloud symmetry; the two `3_21`
N=44 models, the two `2_31` N=93 models, and the `4_21` N=137 model have full
H3/icosahedral symmetry.

The R=2 raw-column `Z[phi]^3` sweep recovers all 10 previously published
`2_21`/`3_21`/`4_21` labelled models, including the H3 family.  The R=3 sweep
found no additional distinct models.  For the 5-demicube (`1_21`), the same
methodology finds three models and saturates already at R=1.  For `1_22`, the
same methodology finds two models and saturates through R=3.  For `2_31`, it
finds five models and saturates through R=3.
See [`GOSSET_PROJECTIONS.md`](GOSSET_PROJECTIONS.md) for the sweep method and
symmetry audit.
