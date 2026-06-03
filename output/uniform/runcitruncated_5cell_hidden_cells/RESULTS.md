# runcitruncated 5-cell hidden-cell removal

These files are derived from `output/uniform/runcitruncated_5cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `runcitruncated_5cell_cell_first_cuboctahedron.vZome` | `runcitruncated_5cell_cell_first_cuboctahedron_front_visible.vZome` | 48 / 60 | 108 / 150 | 12 | 42 |
| `runcitruncated_5cell_oblique_02.vZome` | unchanged (no derived file) | 33 / 33 | 69 / 69 | 0 | 0 |
| `runcitruncated_5cell_oblique_01.vZome` | `runcitruncated_5cell_oblique_01_front_visible.vZome` | 48 / 60 | 111 / 150 | 12 | 39 |
| `runcitruncated_5cell_oblique_00.vZome` | `runcitruncated_5cell_oblique_00_front_visible.vZome` | 50 / 60 | 112 / 150 | 10 | 38 |
