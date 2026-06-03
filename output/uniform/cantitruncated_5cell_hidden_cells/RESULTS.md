# cantitruncated 5-cell hidden-cell removal

These files are derived from `output/uniform/cantitruncated_5cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `cantitruncated_5cell_oblique_00.vZome` | `cantitruncated_5cell_oblique_00_front_visible.vZome` | 51 / 60 | 96 / 120 | 9 | 24 |
| `cantitruncated_5cell_cell_first_truncated_tetrahedron.vZome` | `cantitruncated_5cell_cell_first_truncated_tetrahedron_front_visible.vZome` | 60 / 60 | 108 / 120 | 0 | 12 |
| `cantitruncated_5cell_oblique_01.vZome` | unchanged (no derived file) | 33 / 33 | 57 / 57 | 0 | 0 |
| `cantitruncated_5cell_oblique_02.vZome` | `cantitruncated_5cell_oblique_02_front_visible.vZome` | 54 / 60 | 100 / 120 | 6 | 20 |
