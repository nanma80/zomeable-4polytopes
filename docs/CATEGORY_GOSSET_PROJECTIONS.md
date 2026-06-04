# Gosset orthographic projections

This is a related non-4D collection hosted in the same repository for
convenience and shared tooling.  These models are not part of the 4-polytope
category taxonomy; they are strict orthographic zomeable projections of
Gosset-family and adjacent D/E root polytopes.

| Source polytope | Natural dimension | Zomeable projections | Viewer |
|---|---:|---:|---|
| 5-orthoplex (`2_11`) | 5 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/2_11.html) |
| 5-demicube (`1_21`) | 5 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_21.html) |
| 6-demicube (`1_31`) | 6 | 9 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_31.html) |
| Rectified 5-orthoplex (`t1 2_11`) | 5 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/rectified_5_orthoplex.html) |
| `2_21` | 6 | 2 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/2_21.html) |
| `1_22` | 6 | 2 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_22.html) |
| `3_21` | 7 | 5 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/3_21.html) |
| `2_31` | 7 | 5 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/2_31.html) |
| `1_32` | 7 | 5 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_32.html) |
| `4_21` | 8 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/4_21.html) |
| `2_41` | 8 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/2_41.html) |
| `1_42` | 8 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_42.html) |

All 46 labelled models are available in this folder tree:

- [`output/gosset_projections/`](../output/gosset_projections/)

The ball counts on the viewer page count distinct 3D ball positions after
projection, not vertices of the original higher-dimensional source polytope.
Twenty-nine models have full B3/octahedral point-cloud symmetry; four models have
full D4/tetragonal point-cloud symmetry; two `1_31` models have full
Th/tetrahedral-with-inversion symmetry; the two `1_31` N=32 models, the two `3_21`
N=44 models, the two `2_31` N=93 models, the two `1_32` 384-ball models, the `4_21` N=137 model, the `2_41` N=921 model, and the `1_42` N=5936 model have full
H3/icosahedral symmetry.

The R=2 raw-column `Z[phi]^3` sweep recovers all 10 previously published
`2_21`/`3_21`/`4_21` labelled models, including the H3 family.  The R=3 sweep
found no additional distinct models.  For the 5-demicube (`1_21`), the same
methodology finds three models and saturates already at R=1.  For the
6-demicube (`1_31`), the direct D6 demicube sweep finds nine models and
saturates through R=3.  For `1_22`, the
same methodology finds two models and saturates through R=3.  For `2_31`, it
finds five models and saturates through R=3.  For `1_32`, evaluating those
same E7 projection directions gives five labelled models.  The rectified
5-orthoplex and `2_11` have the same D5 root edge-direction constraints as
`1_21`; direct R=1/R=2/R=3 sweeps give three labelled models each.
For `2_41`, the direct odd-spinor E8-edge sweep has found three labelled models
through R=2; the R=3 confirmation run is longer.
For `1_42`, the direct E8-edge sweep found three labelled models through R=2.
See [`GOSSET_PROJECTIONS.md`](GOSSET_PROJECTIONS.md) for the sweep method and
symmetry audit.
