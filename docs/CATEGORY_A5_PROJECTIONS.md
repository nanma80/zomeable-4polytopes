# A5 simplex family orthographic projections

This is a related non-4D collection hosted in the same repository for
convenience and shared tooling.  These models are not part of the 4-polytope
category taxonomy; they are strict orthographic zomeable projections of the
**A5 (5-simplex) uniform family** of 5-polytopes.

| Source polytope | Nodes | Vertices | Models | Viewer |
|---|---:|---:|---:|---|
| 5-simplex | `1` | 6 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/5_simplex.html) |
| Rectified 5-simplex | `2` | 15 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/rectified_5_simplex.html) |
| Birectified 5-simplex | `3` | 20 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/birectified_5_simplex.html) |
| Truncated 5-simplex | `1,2` | 30 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t12.html) |
| Cantellated 5-simplex | `1,3` | 60 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t13.html) |
| Runcinated 5-simplex | `1,4` | 60 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t14.html) |
| Stericated 5-simplex | `1,5` | 30 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t15.html) |
| Bitruncated 5-simplex | `2,3` | 60 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t23.html) |
| Bicantellated 5-simplex | `2,4` | 90 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t24.html) |
| Cantitruncated 5-simplex | `1,2,3` | 120 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t123.html) |
| Runcitruncated 5-simplex | `1,2,4` | 180 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t124.html) |
| Steritruncated 5-simplex | `1,2,5` | 120 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t125.html) |
| Runcicantellated 5-simplex | `1,3,4` | 180 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t134.html) |
| Stericantellated 5-simplex | `1,3,5` | 180 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t135.html) |
| Bicantitruncated 5-simplex | `2,3,4` | 180 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t234.html) |
| Runcicantitruncated 5-simplex | `1,2,3,4` | 360 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t1234.html) |
| Stericantitruncated 5-simplex | `1,2,3,5` | 360 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t1235.html) |
| Steriruncitruncated 5-simplex | `1,2,4,5` | 360 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t1245.html) |
| Omnitruncated 5-simplex | `1,2,3,4,5` | 720 | 3 | [3D viewer ->](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/a5_t12345.html) |

All 57 labelled models are available in this folder tree:

- [`output/a5_projections/`](../output/a5_projections/)

The ball counts on the viewer pages count distinct 3D ball positions after
projection, not vertices of the original 5-polytope.

A polytope-independent raw-column `Z[phi]^3` sweep saturates at **three distinct
projection geometries**, applied to all 19 A5 Wythoff polytopes (57 models in
total).  R=2 and R=3 return the same three geometries; R=1 finds one of them.

38 of the 57 models are fully buildable with standard vZome struts (a
phi-power strut length, or exactly double one, matched per color orbit); the
remaining 19 are direction-zomeable (every edge parallel to a zometool axis)
but not realizable at standard strut lengths.  Notably the 5-simplex projects
onto a **regular octahedron** (octahedral symmetry, order 48): its 12 edges are
standard Green struts and its 3 long diagonals are exactly double-length Blue
struts.

See [`A5_PROJECTIONS.md`](A5_PROJECTIONS.md) for the sweep method and the
symmetry/buildability audit.
