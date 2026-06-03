# bitruncated 5-cell hidden-cell removal

These files are derived from `output/uniform/bitruncated_5cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `bitruncated_5cell_oblique_00.vZome` | `bitruncated_5cell_oblique_00_front_visible.vZome` | 27 / 30 | 51 / 60 | 3 | 9 |
| `bitruncated_5cell_cell_first_truncated_tetrahedron.vZome` | `bitruncated_5cell_cell_first_truncated_tetrahedron_front_visible.vZome` | 30 / 30 | 54 / 60 | 0 | 6 |
| `bitruncated_5cell_oblique_01.vZome` | `bitruncated_5cell_oblique_01_front_visible.vZome` | 27 / 30 | 51 / 60 | 3 | 9 |
| `bitruncated_5cell_face_first_hexagon.vZome` | unchanged (no derived file) | 18 / 18 | 30 / 30 | 0 | 0 |
