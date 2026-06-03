# rectified 5-cell hidden-cell removal

These files are derived from `output/uniform/rectified_5cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `rectified_5cell_cell_first_tetrahedron.vZome` | unchanged (no derived file) | 10 / 10 | 30 / 30 | 0 | 0 |
| `rectified_5cell_oblique_00.vZome` | `rectified_5cell_oblique_00_front_visible.vZome` | 9 / 10 | 24 / 30 | 1 | 6 |
| `rectified_5cell_oblique_01.vZome` | unchanged (no derived file) | 7 / 7 | 15 / 15 | 0 | 0 |
| `rectified_5cell_oblique_02.vZome` | `rectified_5cell_oblique_02_front_visible.vZome` | 10 / 10 | 27 / 30 | 0 | 3 |
