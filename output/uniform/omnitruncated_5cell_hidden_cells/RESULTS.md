# omnitruncated 5-cell hidden-cell removal

These files are derived from `output/uniform/omnitruncated_5cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `omnitruncated_5cell_cell_first_truncated_octahedron.vZome` | `omnitruncated_5cell_cell_first_truncated_octahedron_front_visible.vZome` | 96 / 96 | 180 / 204 | 0 | 24 |
| `omnitruncated_5cell_oblique_01.vZome` | `omnitruncated_5cell_oblique_01_front_visible.vZome` | 96 / 120 | 180 / 240 | 24 | 60 |
| `omnitruncated_5cell_oblique_00.vZome` | `omnitruncated_5cell_oblique_00_front_visible.vZome` | 96 / 120 | 180 / 240 | 24 | 60 |
| `omnitruncated_5cell_face_first_hexagon.vZome` | unchanged (no derived file) | 60 / 60 | 108 / 108 | 0 | 0 |
