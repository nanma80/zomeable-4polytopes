# 16-cell hidden-cell removal

These files are derived from `output/regular/16cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `16cell_vertex_first_octahedron.vZome` | unchanged (no derived file) | 7 / 7 | 18 / 18 | 0 | 0 |
| `16cell_edge_first_squashed_octahedron.vZome` | unchanged (no derived file) | 6 / 6 | 13 / 13 | 0 | 0 |
| `16cell_cell_first_cube.vZome` | unchanged (no derived file) | 8 / 8 | 24 / 24 | 0 | 0 |
| `16cell_antiprism_B6R12Y6.vZome` | `16cell_antiprism_B6R12Y6_front_visible.vZome` | 8 / 8 | 21 / 24 | 0 | 3 |
| `16cell_antiprism_R12B6Y6.vZome` | `16cell_antiprism_R12B6Y6_front_visible.vZome` | 8 / 8 | 21 / 24 | 0 | 3 |
| `16cell_antiprism_Y6R12B6.vZome` | `16cell_antiprism_Y6R12B6_front_visible.vZome` | 7 / 8 | 18 / 24 | 1 | 6 |
