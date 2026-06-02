# Approximate Platonic and Archimedean zomes

This is a related non-4D collection hosted in the same repository for
convenience and shared tooling. These models are **not** zomeable orthographic
projections of 4-polytopes. They are approximate RGBY strut graph embeddings of
familiar 3D polyhedra, selected for visual/geometric quality.

**[Open the interactive gallery ->](https://nanma80.github.io/zomeable-4polytopes/output/approximate_zomes/VIEWER.html)**

## Curated models

| Target | Favorite model | Final struts |
|---|---|---|
| Tetrahedron | `tetrahedron_favorite.vZome` | `B2` x 3, `R2` x 3 |
| Cube | `cube_favorite.vZome` | `B3` x 4, `G2` x 8 |
| Octahedron | `octahedron_favorite.vZome` | `B2` x 6, `R2` x 6 |
| Icosahedron | `icosahedron_favorite.vZome` | `B3` x 6, `G2` x 24 |
| Dodecahedron | `dodecahedron_favorite.vZome` | `B3` x 6, `G2` x 24 |
| Truncated tetrahedron | `truncated_tetrahedron_favorite.vZome` | `B2` x 9, `R2` x 9 |
| Cuboctahedron | `cuboctahedron_favorite.vZome` | `B2` x 12, `R2` x 12 |
| Truncated octahedron | `truncated_octahedron_favorite.vZome` | `B2` x 18, `R2` x 18 |
| Rhombicuboctahedron | `rhombicuboctahedron_favorite.vZome` | `B3` x 24, `G2` x 24 |
| Icosidodecahedron | `icosidodecahedron_favorite.vZome` | `B3` x 12, `G2` x 48 |
| Rhombicosidodecahedron | `rhombicosidodecahedron_favorite.vZome` | `B3` x 24, `G2` x 96 |

Each favorite was scaled by a global power of `phi` so every emitted strut is in
scale 2 or 3, then translated exactly to its golden-field centroid with no
rotation or additional scaling.

## Method notes

The search compares candidate graph embeddings against the ideal geometric
target: edge-length variation, face side-length variation, face planarity,
per-corner face angles, radial balance, and convexity. Archimedean targets use
their ideal mixed face angles rather than assuming a single target angle.

Snub cube and snub dodecahedron were also searched because exact standard-vZome
realizations are not expected. The current strict searches did not find a
favorite snub model, so the curated gallery contains only the solved targets
above.

The generation scripts are in:

- [`tools/approximate_zomes/`](../tools/approximate_zomes/)

The final model files, `.shapes.json` files, and manifest are in:

- [`output/approximate_zomes/`](../output/approximate_zomes/)

## References and acknowledgements

Some of these approximation ideas are related to earlier Zometool constructions
shared in the following sources:

- Reza Sarhangi, "An Art and Technology Approach to Actively Engage Students in
  the Mathematics of the Regular Polyhedra," *Mathematics Education Trends and
  Research*, 2014, doi:10.5899/2014/metr-00060. In particular, Sarhangi shows
  classroom Zome approximations for the tetrahedron and octahedron.
- Tick Wang, [Facebook reel](https://www.facebook.com/reel/3394895470670317),
  showing related Zome polyhedron approximation constructions.

The models here are a curated computational gallery in the same spirit: standard
RGBY zome strut graphs chosen to approximate the ideal Platonic and Archimedean
targets visually and metrically.
