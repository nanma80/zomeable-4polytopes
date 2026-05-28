# A5 simplex family orthographic projections

This is a related non-4D collection hosted in the same repository for
convenience and shared tooling.  These models are not part of the 4-polytope
category taxonomy; they are strict orthographic zomeable projections of the
**A5 (5-simplex) uniform family** of 5-polytopes.

| Source polytope | Vertices | Natural dimension | Models | Viewer |
|---|---:|---:|---:|---|
| 5-simplex (hexateron) | 6 | 5 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/5_simplex.html) |
| Rectified 5-simplex | 15 | 5 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/rectified_5_simplex.html) |
| Birectified 5-simplex | 20 | 5 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/birectified_5_simplex.html) |

All 9 labelled models are available in this folder tree:

- [`output/a5_projections/`](../output/a5_projections/)

The ball counts on the viewer pages count distinct 3D ball positions after
projection, not vertices of the original 5-polytope.

A polytope-independent raw-column `Z[phi]^3` sweep saturates at **three distinct
projection geometries**, applied to each of the three rectifications (nine
models in total).  R=1, R=2, and R=3 all return the same three geometries.

Six of the nine models are fully buildable with standard vZome struts (a
phi-power strut length, or exactly double one, matched per color orbit); the
remaining three are direction-zomeable (every edge parallel to a zometool axis)
but not realizable at standard strut lengths.  Notably the 5-simplex projects
onto a **regular octahedron** (octahedral symmetry, order 48): its 12 edges are
standard Green struts and its 3 long diagonals are exactly double-length Blue
struts.

See [`A5_PROJECTIONS.md`](A5_PROJECTIONS.md) for the sweep method and the
symmetry/buildability audit.
