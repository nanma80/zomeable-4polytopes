# A5 simplex family orthographic projections - methodology

Strict orthographic, zometool-buildable 3D projections of the A5 (5-simplex)
uniform family.  This note records the sweep method, the saturation result, and
the per-shape symmetry/buildability audit.

## The family

The A5 symmetry group is the symmetric group `S6` (order 720), acting on the
5-dimensional hyperplane `H = { x in R^6 : sum x_i = 0 }`.  We study the three
rectifications, with vertices given (in 6D, before centering) by the coordinate
permutations of:

| Polytope | Vertex pattern | Vertices |
|---|---|---:|
| 5-simplex (hexateron) | `(1,0,0,0,0,0)` | 6 |
| Rectified 5-simplex | `(1,1,0,0,0,0)` | 15 |
| Birectified 5-simplex | `(1,1,1,0,0,0)` | 20 |

Every edge of every A5 uniform polytope is parallel to a root `e_i - e_j`, so a
projection sends all edges to zometool axes iff every difference of projected
coordinate-images is a zome axis (or zero).

## Polytope-independent sweep

Because `S6` acts irreducibly on `H`, the centered vertex covariance of *every*
A5 polytope is proportional to the same projector `Pi_H = I_6 - (1/6) J`.  Hence
a projection `P : R^6 -> R^3` is strict-orthographic for one A5 polytope iff it
is for all of them; the exact integer condition is

```
6 * sum_i c_i c_i^T  -  s s^T  =  lambda I_3 ,   lambda != 0 ,   s = sum_i c_i
```

where `c_0 ... c_5` are the columns of `P`.  Translating the image only shifts
the model, so we gauge-fix `c_0 = 0`; the remaining columns are then zome-axis
vectors (within radius `R`) whose pairwise differences are also zome axes.  This
makes the candidate set small (zome axes, not all of `Z[phi]^3`).

The sweep (`tools/a5/zphi_a5_sweep.py`) enumerates these candidate column tuples
with exact `Z[phi]` arithmetic, keeps the isotropic ones, and dedupes hits by a
scale-and-rotation-invariant signature triple (one signature per polytope).

## Result: three geometries, saturated

R=1, R=2, and R=3 all return the **same three projection geometries**.  Applied
to each of the three polytopes, this gives nine models:

| Shape | 5-simplex | Rectified | Birectified | Notes |
|---|---|---|---|---|
| A | order 24, 5 balls | order 24, 11 balls | order 48, 14 balls | buildable (Yellow+Green), scale `phi^2/3` |
| B | order 6, 5 balls | order 6, 11 balls | order 12, 14 balls | direction-zomeable only, scale `phi^2` |
| C | order 48, 6 balls | order 48, 13 balls | order 48, 14 balls | buildable (Green + 2x Blue), scale `phi^2` |

Symmetry orders are full Euclidean point-cloud symmetries; order 48 is full
octahedral symmetry.

## Buildability

A model is *fully buildable* when, at a single scale, every edge is a standard
vZome strut length `phi^n` (or exactly double one), matched independently within
each color orbit.  Six of the nine models are fully buildable.

Shape C's 5-simplex is the cleanest example: it projects onto a **regular
octahedron**, whose 12 edges are standard Green struts and whose 3 long
diagonals are double-length Blue struts.  The octahedron edge-to-diagonal ratio
is `sqrt(2)`; because the Green orbit's base length already carries a `sqrt(2)`
factor relative to Blue, the doubling supplies the remaining factor of `sqrt(2)`
so both colors land on real parts at one scale.

Shape B mixes Blue/Yellow/Green edge lengths whose ratios are not reconcilable
to standard strut lengths at any single scale, so it is recorded as
direction-zomeable only (all edge directions are valid zome axes).

## Postprocessing

`tools/a5/build_gallery_a5.py` projects each shape, collapses coincident
vertices, centers the ball cloud on its centroid (exact golden-field), chooses a
`(num/den) * phi^n` scale preferring a pure power of phi, enlarges by `phi^2`,
deletes the auto-created origin ball when the centroid is not itself a ball, and
fits the vZome `ViewModel` to the model bounds.
