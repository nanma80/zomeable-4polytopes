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
| 8-orthoplex (`5_11`) | D8 | 8 | 18 | [page 1 ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/5_11.html) / [page 2 ->](https://nanma80.github.io/zomeable-4polytopes/output/gosset_projections/5_11_page2.html) |
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

The listed counts are bounded numerical search results.  Follow-up higher-bound
checks have not produced additional distinct published models for the completed
families, but—as elsewhere in this repository—this is empirical saturation
rather than a formal proof.

For implementation details, including the exact search bounds and family-by-family
audit notes, see
[`GOSSET_PROJECTIONS.md`](GOSSET_PROJECTIONS.md) for the sweep method and
symmetry audit.
