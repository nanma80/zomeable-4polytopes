# rectified 24-cell hidden-cell removal

These files are derived from `output/uniform/rectified_24cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `rectified_24cell_cell_first_cuboctahedron.vZome` | unchanged (no derived file) | 60 / 60 | 156 / 156 | 0 | 0 |
| `rectified_24cell_cell_first_cube.vZome` | unchanged (no derived file) | 52 / 52 | 132 / 132 | 0 | 0 |
| `rectified_24cell_oblique.vZome` | `rectified_24cell_oblique_front_visible.vZome` | 78 / 96 | 213 / 288 | 18 | 75 |
