# Gosset projection methodology

This page records the method used for the related
[`output/gosset_projections/`](../output/gosset_projections/) collection.

The models are not 4-polytopes.  They are strict orthographic zomeable
projections of Gosset-family and adjacent D/E root polytopes:

| Polytope | Natural dimension | Models |
|---|---:|---:|
| 5-orthoplex (`2_11`) | 5 | 3 |
| 5-demicube (`1_21`) | 5 | 3 |
| 6-demicube (`1_31`) | 6 | 9 |
| Rectified 5-orthoplex (`t1 2_11`) | 5 | 3 |
| E6 root polytope (`1_22`) | 6 | 2 |
| `2_21` | 6 | 2 |
| `3_21` | 7 | 5 |
| `2_31` | 7 | 5 |
| `1_32` | 7 | 5 |
| `4_21` | 8 | 3 |
| `2_41` | 8 | 3 |
| `1_42` | 8 | 3 |

## Prior work

Scott Vorthmann's *Gosset's Polytopes* (2005) is prior vZome/zometool work on
Gosset-polytope models:

<https://vorth.github.io/vzome-sharing/2005/09/18/gossets-polytopes.html>

The sweep documented here was run from scratch, but this page should be cited
as earlier public work on the Gosset-polytope subject in vZome.

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
5. Collect strict rank-3 images for all relevant source polytopes.  For
   `2_21`/`3_21`/`4_21`, this means all vertex-figure embeddings inside the
   E8 model.  For `2_11`, `1_21`, `1_31`, and the rectified 5-orthoplex, the
   standalone source polytopes are checked directly; their edge directions are
   only of the `+/- e_i +/- e_j` type, so there is no E8 half-root condition.
   The 6-demicube is `1_31` in Gosset notation and uses the same standalone
   D-type demicube edge constraint as `1_21`, with six projection columns
   instead of five.
   The rectified 5-orthoplex is the D5 root polytope with vertices all
   permutations of
   `(+/-1,+/-1,0,0,0)`, so it has the same D5 root edge-direction constraints
   as `1_21`.  For `2_41`, the edge directions form the E8 root system with
   the odd spinor parity, so the direct sweep uses the same type-A constraints
   but checks odd-parity half-root sums.  For `1_42`, the edge directions are
   the full E8 root system, so the direct sweep checks both spinor parities and
   the `+/-2e_i +/-2e_j` roots.  For the E6 root polytope (`1_22`), we realize the polytope as
   the E8 roots orthogonal to an A2 subsystem and use the gauge representative
   annihilating that A2 complement.

## Saturation runs

| Range | Runtime | Leaves | Result |
|---:|---:|---:|---|
| 5-orthoplex (`2_11`), R=1 | 1.2 s | 433,289 | 3 models |
| 5-orthoplex (`2_11`), R=2 | 29.3 s | 3,702,503 | same 3 models |
| 5-orthoplex (`2_11`), R=3 | 673.9 s | 48,536,391 | same 3 models |
| 5-demicube (`1_21`), R=1 | 1.2 s | 433,289 | 3 models |
| 5-demicube (`1_21`), R=2 | 30.4 s | 3,702,503 | same 3 models |
| 5-demicube (`1_21`), R=3 | 708.5 s | 48,536,391 | same 3 models |
| 6-demicube (`1_31`), R=1 | 4.4 s | 1,370,293 | 5 models |
| 6-demicube (`1_31`), R=2 | 70.3 s | 14,183,831 | 9 models |
| 6-demicube (`1_31`), R=3 | 55.3 min | 390,832,319 | same 9 models |
| Rectified 5-orthoplex (`t1 2_11`), R=1 | 1.3 s | 433,289 | 3 models |
| Rectified 5-orthoplex (`t1 2_11`), R=2 | 32.7 s | 3,702,503 | same 3 models |
| Rectified 5-orthoplex (`t1 2_11`), R=3 | 678.4 s | 48,536,391 | same 3 models |
| `1_22`, R=1 | 1.5 s | 433,289 | 2 models |
| `1_22`, R=2 | 17.0 s | 3,702,503 | same 2 models |
| `1_22`, R=3 | 444.1 s | 48,536,391 | same 2 models |
| `2_31`, R=1 | 8.7 s | 1,370,293 | 5 models |
| `2_31`, R=2 | 79.8 s | 14,183,831 | same 5 models |
| `2_31`, R=3 | 57.2 min | 390,832,319 | same 5 models |
| `1_32` | reused `2_31` directions | n/a | 5 labelled models |
| `2_21`/`3_21`/`4_21`, R=2 | 0.98 h | 190,459,868 | all 10 labelled models |
| `2_21`/`3_21`/`4_21`, R=3 | 47.49 h | 19,816,930,273 | same 10 labelled models; no new models |
| `2_41`, R=1 | 48.7 s | 12,101,671 | 3 models |
| `2_41`, R=2 | 13.5 min | 190,459,868 | same 3 models |
| `1_42`, R=1 | 68.7 s | 12,101,671 | 3 models |
| `1_42`, R=2 | 13.8 min | 190,459,868 | same 3 models |

The R=3 leaf estimator predicted `1.960e10 +/- 1.828e8` leaves, close to the
actual `1.982e10` leaves.

## Symmetry labels

The public captions use full Euclidean point-cloud symmetry:

- `B3-symmetric` means full octahedral symmetry, full order 48.
- `D4-symmetric` means full tetragonal/dihedral symmetry, full order 16.
- `Th-symmetric` means full tetrahedral symmetry with inversion, full order 24.
- `H3-symmetric` means full icosahedral symmetry, full order 120.

The computed symmetry audit is in
[`output/gosset_projections/symmetry_analysis.json`](../output/gosset_projections/symmetry_analysis.json).

## Relation between the B3-symmetric models

The B3-symmetric models are related through the usual vertex-figure chain

```text
5-demicube (1_21) -> 2_21 -> 3_21 -> 4_21.
```

The same raw-column projection can produce compatible strict images for several
members of this chain.  Under such a projection, vertices of the larger Gosset
polytope may coincide in 3D, so a larger source polytope can produce a
degenerate image whose visible ball arrangement agrees with a smaller source
polytope's image.

In the computed R=2/R=3 data, the B3 cases split into two projection branches:

| Branch | `2_21` image | `3_21` image(s) | `4_21` image |
|---|---|---|---|
| A | 15 balls | 15 balls | 27 balls |
| B | 19 balls | 19 balls and 14 balls | 33 balls |

Branch A is the simplest inherited family: the same B3 projection gives the
15-ball `2_21` and `3_21` images and the 27-ball `4_21` image.

Branch B explains the apparent extra B3 model for `3_21`.  The same projection
branch gives the 19-ball `2_21` image, the 19-ball `3_21` image, and the
33-ball `4_21` image; but after choosing this B3 projection, the `3_21`
vertex figures inside `4_21` split into more than one orbit under the remaining
B3 symmetry.  One orbit gives the inherited 19-ball image, while another orbit
gives the 14-ball cube-hull image.  Thus the 14-ball `3_21` model is not an
unrelated projection direction; it is another degeneration within the same B3
projection branch.

The regular 5-orthoplex (`2_11`) adds three labelled models: two B3-symmetric
models with 7 and 9 balls, and one D4-symmetric model with 7 balls.  The
5-demicube (`1_21`) member adds three models.  Its 15-ball B3 model is the
same visible point-cloud geometry as the 15-ball branch above; the 8-ball B3
model and 12-ball D4 model are specific lower-dimensional degenerations of the
5-demicube and do not match the current `2_21`/`3_21`/`4_21` gallery models.

The rectified 5-orthoplex fits the notation as the first rectification of
`2_11`, so a compact label is `t1 2_11`.  It is the D5 root polytope /
rectified pentacross (`t1{3,3,3,4}`), while unmodified `2_11` is the regular
5-orthoplex.  Since its 240 edges use the same D5 root directions as the
5-demicube, the direct R=1/R=2/R=3 sweep gives three labelled models with 19,
21, and 26 balls.

The E6 root polytope (`1_22`) contributes two labelled B3 models.  Their
visible point-cloud geometries agree with the `4_21` 27-ball and 33-ball B3
models, but the source polytope and source edge set are different, so the
gallery keeps them as separate labelled models.

The `2_31` member contributes five labelled models.  Three are B3-symmetric
degenerations with 19, 27, and 33 balls; two are H3-symmetric 93-ball models
with different convex hulls.  As with `1_22`, some visible geometries agree
with existing smaller entries, but the `2_31` source polytope and its edge set
are distinct, so they are listed separately.

The `1_32` member has the same E7 root edge-direction constraints as `2_31`,
so no separate projection-direction search is needed.  Evaluating the completed
`2_31` projection directions on the 576-vertex `1_32` source gives five
labelled models: three B3-symmetric models with 38, 59, and 81 balls, and two
H3-symmetric 384-ball models.

The 6-demicube (`1_31`, demihexeract) is the next demicube after `1_21`.
Its direct D6 demicube sweep gives nine labelled models through R=3: four
B3-symmetric projections with 8, 13, 14, and 15 balls; one D4-symmetric
projection with 12 balls; two Th-symmetric projections with 32 balls; and two
H3-symmetric projections with 32 balls.

The H3- and Th-symmetric `1_31` projections use the following exact 6x3
matrices, shown up to overall scale as the raw sweep matrices multiplied by
`1/(3phi)`; the emitted `.vZome` files apply their physical post-scales.

```text
1_31_H3_32_balls_a:
[
  [-phi, -1,    0   ],
  [-phi,  1,    0   ],
  [-1,    0,   -phi ],
  [-1,    0,    phi ],
  [ 0,   -phi, -1   ],
  [ 0,    phi, -1   ],
]

1_31_H3_32_balls_b:
[
  [-phi, -1,    0   ],
  [-phi,  1,    0   ],
  [-1,    0,   -phi ],
  [-1,    0,    phi ],
  [ 0,   -phi, -1   ],
  [ 0,   -phi,  1   ],
]

1_31_Th_32_balls_a:
[
  [-phi,    0,       -1/phi ],
  [-phi,    0,        1/phi ],
  [-1/phi, -phi,      0     ],
  [-1/phi,  phi,      0     ],
  [ 0,     -1/phi,   -phi   ],
  [ 0,      1/phi,   -phi   ],
]

1_31_Th_32_balls_b:
[
  [-phi,    0,       -1/phi ],
  [-phi,    0,        1/phi ],
  [-1/phi, -phi,      0     ],
  [-1/phi,  phi,      0     ],
  [ 0,     -1/phi,   -phi   ],
  [ 0,     -1/phi,    phi   ],
]
```

The `2_41` member uses the E8 root directions with odd spinor parity.  The
direct parity-correct sweep gives three labelled models through R=2: two
B3-symmetric projections with 65 and 93 balls, and one H3-symmetric projection
with 921 balls.

The `1_42` member uses the full E8 root directions.  The direct sweep gives
three labelled models through R=2: two B3-symmetric projections with 169 and
251 balls, and one H3-symmetric projection with 5936 balls.
