# Gosset orthographic projections

This folder is a related collection in this repository, not a 4-polytope
category.  The models are strict orthographic 3D projections of the Gosset
polytopes `1_21`, `2_21`, `3_21`, and `4_21`, whose natural dimensions are 5,
6, 7, and 8 respectively.

The thirteen `.vZome` files are kept in a flat structure for sharing and spot
checking.  "Balls" counts distinct 3D ball positions in the projected vZome
model; some vertices of the original Gosset polytope may coincide in 3D.

Open the single-page gallery here:

- [`VIEWER.md`](VIEWER.md)

## Models

| File | Source polytope | Balls | Symmetry |
|---:|---|---:|---|
| `11_...vZome` | `1_21` | 8 | B3-symmetric |
| `12_...vZome` | `1_21` | 12 | D4-symmetric |
| `13_...vZome` | `1_21` | 15 | B3-symmetric |
| `01_...vZome` | `2_21` | 15 | B3-symmetric |
| `02_...vZome` | `2_21` | 19 | B3-symmetric |
| `03_...vZome` | `3_21` | 14 | B3-symmetric |
| `04_...vZome` | `3_21` | 15 | B3-symmetric |
| `05_...vZome` | `3_21` | 19 | B3-symmetric |
| `06_...vZome` | `3_21` | 44 | H3-symmetric |
| `07_...vZome` | `3_21` | 44 | H3-symmetric |
| `08_...vZome` | `4_21` | 27 | B3-symmetric |
| `09_...vZome` | `4_21` | 33 | B3-symmetric |
| `10_...vZome` | `4_21` | 137 | H3-symmetric |

The symmetry labels are full Euclidean point-cloud symmetries: B3 means full
octahedral symmetry (order 48), D4 means full tetragonal/dihedral symmetry
(order 16), and H3 means full icosahedral symmetry (order 120).  See
[`symmetry_analysis.json`](symmetry_analysis.json).

## Provenance

These models were found by a unified raw-column `Z[phi]^3` sweep.  The R=2
sweep recovers all ten `2_21`/`3_21`/`4_21` labelled models, including the H3
family, and the R=3 sweep found no additional distinct models.  For `1_21`,
R=1, R=2, and R=3 all give the same three models.

