# Gosset orthographic projections

This is a related non-4D collection hosted in the same repository for
convenience and shared tooling.  These models are not part of the 4-polytope
category taxonomy; they are strict orthographic zomeable projections of
Gosset-family and adjacent D/E root polytopes.

| Source polytope | Source symmetry group | Natural dimension | Zomeable projections | Viewer |
|---|---|---:|---:|---|
| 5-orthoplex (`2_11`) | D5 | 5 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/2_11.html) |
| Rectified 5-orthoplex (`t1 2_11`) | D5 | 5 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/rectified_5_orthoplex.html) |
| 5-demicube (`1_21`) | D5 | 5 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_21.html) |
| 6-orthoplex (`3_11`) | D6 | 6 | 6 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/3_11.html) |
| 6-demicube (`1_31`) | D6 | 6 | 9 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_31.html) |
| `2_21` | E6 | 6 | 2 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/2_21.html) |
| `1_22` | E6 | 6 | 2 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_22.html) |
| 7-orthoplex (`4_11`) | D7 | 7 | 5 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/4_11.html) |
| 7-demicube (`1_41`) | D7 | 7 | 6 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_41.html) |
| `3_21` | E7 | 7 | 5 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/3_21.html) |
| `2_31` | E7 | 7 | 5 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/2_31.html) |
| `1_32` | E7 | 7 | 5 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_32.html) |
| 8-orthoplex (`5_11`) | D8 | 8 | 18 (R=2 provisional) | [page 1 ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/5_11.html) / [page 2 ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/5_11_page2.html) |
| `4_21` | E8 | 8 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/4_21.html) |
| `2_41` | E8 | 8 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/2_41.html) |
| `1_42` | E8 | 8 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_42.html) |
| 9-orthoplex (`6_11`) | D9 | 9 | 8 | [page 1 ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/6_11.html) / [page 2 ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/6_11_page2.html) |
| 10-orthoplex (`7_11`) | D10 | 10 | 9 | [page 1 ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/7_11.html) / [page 2 ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/7_11_page2.html) |
| 10-demicube (`1_71`) | D10 | 10 | 15 | [page 1 ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_71.html) / [page 2 ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/1_71_page2.html) |

All 113 labelled models are available in this folder tree:

- [`output/gosset_projections/`](../output/gosset_projections/)

The ball counts on the viewer page count distinct 3D ball positions after
projection, not vertices of the original higher-dimensional source polytope.

The newly included 8-orthoplex (`5_11`) row is provisional: R=2 found 18
models, but the R=3 sweep is still running and may add more.  The 9-orthoplex
(`6_11`) R=2 sweep matched R=1 exactly with 8 models.  The 10-orthoplex
(`7_11`) R=2 sweep also matched R=1 exactly with 9 models.

The R=2 raw-column `Z[phi]^3` sweep recovers all 10 previously published
`2_21`/`3_21`/`4_21` labelled models, including the H3 family.  The R=3 sweep
found no additional distinct models.  For the 5-demicube (`1_21`), the same
methodology finds three models and saturates already at R=1.  For the
6-demicube (`1_31`), the direct D6 demicube sweep finds nine models and
saturates through R=3.  For the 7-demicube (`1_41`), the direct D7 demicube
sweep finds six models and saturates through R=3.  For the 10-demicube (`1_71`),
the direct D10 demicube sweep finds 13 even-coset models and saturates through
R=2; the C3i and H3 matrices also contribute distinct variant pairs.  For
`1_22`, the same methodology finds two models and saturates through R=3.  For
`2_31`, it finds five models and saturates through R=3.  For `1_32`,
evaluating those same E7 projection directions gives five labelled models.
The rectified 5-orthoplex and `2_11` have the same D5 root edge-direction
constraints as `1_21`; direct R=1/R=2/R=3 sweeps give three labelled models
each.  The higher orthoplexes `3_11`, `4_11`, `5_11`, `6_11`, and `7_11` use
the same D_n constraints as the corresponding orthoplex root systems; their
current labelled model counts are 6, 5, 18, 8, and 9 respectively.  For
`2_41`, the direct odd-spinor E8-edge sweep has found three labelled models
through R=2; the R=3 confirmation run is longer.  For `1_42`, the direct
E8-edge sweep found three labelled models through R=2.  See
[`GOSSET_PROJECTIONS.md`](GOSSET_PROJECTIONS.md) for the sweep method and
symmetry audit.
