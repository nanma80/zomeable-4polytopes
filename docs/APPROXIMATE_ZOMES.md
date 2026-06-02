# Approximate Platonic, Archimedean, and Catalan zomes

This is a related non-4D collection hosted in the same repository for
convenience and shared tooling. These models are **not** zomeable orthographic
projections of 4-polytopes. They are approximate RGBY strut graph embeddings of
familiar 3D polyhedra, selected for visual/geometric quality.

**[Open the interactive gallery ->](https://nanma80.github.io/zomeable-4polytopes/output/approximate_zomes/VIEWER.html)**

## Curated models

### Platonic solids

| Target | Favorite model | Final struts |
|---|---|---|
| Tetrahedron | `tetrahedron_favorite.vZome` | `B2` x 3, `R2` x 3 |
| Cube | `cube_favorite.vZome` | `B3` x 4, `G2` x 8 |
| Octahedron | `octahedron_favorite.vZome` | `B2` x 6, `R2` x 6 |
| Icosahedron | `icosahedron_favorite.vZome` | `B3` x 6, `G2` x 24 |
| Dodecahedron | `dodecahedron_favorite.vZome` | `B3` x 6, `G2` x 24 |

### Archimedean solids

| Target | Favorite model | Final struts |
|---|---|---|
| Truncated tetrahedron | `truncated_tetrahedron_favorite.vZome` | `B2` x 9, `R2` x 9 |
| Cuboctahedron | `cuboctahedron_favorite.vZome` | `B2` x 12, `R2` x 12 |
| Truncated octahedron | `truncated_octahedron_favorite.vZome` | `B2` x 18, `R2` x 18 |
| Rhombicuboctahedron | `rhombicuboctahedron_favorite.vZome` | `B3` x 24, `G2` x 24 |
| Icosidodecahedron | `icosidodecahedron_favorite.vZome` | `B3` x 12, `G2` x 48 |
| Rhombicosidodecahedron | `rhombicosidodecahedron_favorite.vZome` | `B3` x 24, `G2` x 96 |

### Catalan solids

| Target | Favorite model | Final struts |
|---|---|---|
| Triakis tetrahedron | `triakis_tetrahedron_favorite.vZome` | `B2` x 3, `B3` x 3, `R2` x 3, `Y2` x 6, `Y3` x 3 |
| Rhombic dodecahedron | `rhombic_dodecahedron_favorite.vZome` | `G2` x 18, `Y3` x 6 |
| Rhombic triacontahedron | `rhombic_triacontahedron_favorite.vZome` | `G2` x 60 |
| Triakis icosahedron | `triakis_icosahedron_favorite.vZome` | `B3` x 30, `R2` x 60 |
| Pentakis dodecahedron | `pentakis_dodecahedron_favorite.vZome` | `B3` x 30, `G2` x 60 |

Each favorite was scaled by a global power of `phi` so every emitted strut is in
scale 2 or 3, then translated exactly to its golden-field centroid with no
rotation or additional scaling.

## Method notes

The search compares candidate graph embeddings against the ideal geometric
target: edge-length variation, face side-length variation, face planarity,
per-corner face angles, radial balance, and convexity. Archimedean targets use
their ideal mixed face angles rather than assuming a single target angle.

Catalan targets are generated as polar duals of the corresponding Archimedean
target geometry. Their faces are congruent but generally irregular, so the
search scores actual edge and face-side lengths against the ideal Catalan
short/long edge ratios up to one global scale instead of forcing all graph edges
or all face sides to be equal.

Of the 13 Catalan solids, the current strict one-strut searches produced
curated favorites for the five Catalan targets listed above. The other Catalan
targets emitted no favorite under the current bounds and filters; this is not a
proof that no approximate model exists.

Snub cube and snub dodecahedron were also searched because exact standard-vZome
realizations are not expected. The current strict searches did not find a
favorite snub model, so the curated gallery contains only the solved targets
above.

The generation scripts are in:

- [`tools/approximate_zomes/`](../tools/approximate_zomes/)

The 16 final model files, 16 `.shapes.json` files, and manifest are in:

- [`output/approximate_zomes/`](../output/approximate_zomes/)
