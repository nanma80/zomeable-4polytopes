# Gosset orthographic projections

This folder is a related collection in this repository, not a 4-polytope
category.  The models are strict orthographic 3D projections of the
Gosset-family and adjacent D/E root polytopes: 5-orthoplex (`2_11`),
5-demicube (`1_21`), rectified 5-orthoplex (`t1 2_11`), E6 root polytope
(`1_22`), `2_21`, `3_21`, `2_31`, `1_32`, and `4_21`.

The thirty-one `.vZome` files are organized in per-source subfolders for
sharing and spot checking.  "Balls" counts distinct 3D ball positions in the projected vZome
model; some vertices of the original source polytope may coincide in 3D.

Open the viewer index here:

- [`VIEWER.md`](VIEWER.md)

## Models

| File | Source polytope | Balls | Symmetry |
|---:|---|---:|---|
| `2_11/2_11_B3_7_balls.vZome` | 5-orthoplex (`2_11`) | 7 | B3-symmetric |
| `2_11/2_11_D4_7_balls.vZome` | 5-orthoplex (`2_11`) | 7 | D4-symmetric |
| `2_11/2_11_B3_9_balls.vZome` | 5-orthoplex (`2_11`) | 9 | B3-symmetric |
| `1_21/1_21_B3_8_balls.vZome` | 5-demicube (`1_21`) | 8 | B3-symmetric |
| `1_21/1_21_D4_12_balls.vZome` | 5-demicube (`1_21`) | 12 | D4-symmetric |
| `1_21/1_21_B3_15_balls.vZome` | 5-demicube (`1_21`) | 15 | B3-symmetric |
| `rectified_5_orthoplex/rectified_5_orthoplex_B3_19_balls.vZome` | Rectified 5-orthoplex (`t1 2_11`) | 19 | B3-symmetric |
| `rectified_5_orthoplex/rectified_5_orthoplex_D4_21_balls.vZome` | Rectified 5-orthoplex (`t1 2_11`) | 21 | D4-symmetric |
| `rectified_5_orthoplex/rectified_5_orthoplex_B3_26_balls.vZome` | Rectified 5-orthoplex (`t1 2_11`) | 26 | B3-symmetric |
| `1_22/1_22_B3_27_balls.vZome` | E6 root polytope (`1_22`) | 27 | B3-symmetric |
| `1_22/1_22_B3_33_balls.vZome` | E6 root polytope (`1_22`) | 33 | B3-symmetric |
| `2_21/2_21_B3_15_balls.vZome` | `2_21` | 15 | B3-symmetric |
| `2_21/2_21_B3_19_balls.vZome` | `2_21` | 19 | B3-symmetric |
| `3_21/3_21_B3_14_balls.vZome` | `3_21` | 14 | B3-symmetric |
| `3_21/3_21_B3_15_balls.vZome` | `3_21` | 15 | B3-symmetric |
| `3_21/3_21_B3_19_balls.vZome` | `3_21` | 19 | B3-symmetric |
| `3_21/3_21_H3_44_balls_icosa_hull.vZome` | `3_21` | 44 | H3-symmetric |
| `3_21/3_21_H3_44_balls_dodeca_hull.vZome` | `3_21` | 44 | H3-symmetric |
| `2_31/2_31_B3_19_balls.vZome` | `2_31` | 19 | B3-symmetric |
| `2_31/2_31_B3_27_balls.vZome` | `2_31` | 27 | B3-symmetric |
| `2_31/2_31_B3_33_balls.vZome` | `2_31` | 33 | B3-symmetric |
| `2_31/2_31_H3_93_balls_hull42.vZome` | `2_31` | 93 | H3-symmetric |
| `2_31/2_31_H3_93_balls_hull30.vZome` | `2_31` | 93 | H3-symmetric |
| `1_32/1_32_B3_38_balls.vZome` | `1_32` | 38 | B3-symmetric |
| `1_32/1_32_B3_59_balls.vZome` | `1_32` | 59 | B3-symmetric |
| `1_32/1_32_B3_81_balls.vZome` | `1_32` | 81 | B3-symmetric |
| `1_32/1_32_H3_384_balls_hull32.vZome` | `1_32` | 384 | H3-symmetric |
| `1_32/1_32_H3_384_balls_hull80.vZome` | `1_32` | 384 | H3-symmetric |
| `4_21/4_21_B3_27_balls.vZome` | `4_21` | 27 | B3-symmetric |
| `4_21/4_21_B3_33_balls.vZome` | `4_21` | 33 | B3-symmetric |
| `4_21/4_21_H3_137_balls.vZome` | `4_21` | 137 | H3-symmetric |

The symmetry labels are full Euclidean point-cloud symmetries: B3 means full
octahedral symmetry (order 48), D4 means full tetragonal/dihedral symmetry
(order 16), and H3 means full icosahedral symmetry (order 120).  See
[`symmetry_analysis.json`](symmetry_analysis.json).

## Provenance

These models were found by a unified raw-column `Z[phi]^3` sweep.  The R=2
sweep recovers all ten `2_21`/`3_21`/`4_21` labelled models, including the H3
family, and the R=3 sweep found no additional distinct models.  For the
5-orthoplex (`2_11`) and 5-demicube (`1_21`), R=1, R=2, and R=3 all give the
same three models for each source.  For the E6 root polytope (`1_22`), R=1,
R=2, and R=3 all give the same two models.  For `2_31`, R=1, R=2, and R=3 all
give the same five models.  For `1_32`, evaluating those same E7 projection
directions gives five labelled models.  The rectified 5-orthoplex has the same
D5 root edge-direction constraints as `1_21`; a direct R=1/R=2/R=3 sweep gives
three labelled models.

