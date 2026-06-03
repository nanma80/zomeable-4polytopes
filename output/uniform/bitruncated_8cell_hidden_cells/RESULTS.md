# bitruncated tesseract hidden-cell removal

These files are derived from `output/uniform/bitruncated_8cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `bitruncated_8cell_cell_first_truncated_tetrahedron.vZome` | `bitruncated_8cell_cell_first_truncated_tetrahedron_front_visible.vZome` | 84 / 96 | 162 / 192 | 12 | 30 |
| `bitruncated_8cell_face_first_square.vZome` | unchanged (no derived file) | 52 / 52 | 92 / 92 | 0 | 0 |
| `bitruncated_8cell_cell_first_truncated_octahedron.vZome` | unchanged (no derived file) | 60 / 60 | 108 / 108 | 0 | 0 |
| `bitruncated_8cell_oblique_02.vZome` | `bitruncated_8cell_oblique_02_front_visible.vZome` | 81 / 96 | 150 / 192 | 15 | 42 |
| `bitruncated_8cell_oblique_00.vZome` | `bitruncated_8cell_oblique_00_front_visible.vZome` | 78 / 96 | 147 / 192 | 18 | 45 |
| `bitruncated_8cell_oblique_01.vZome` | `bitruncated_8cell_oblique_01_front_visible.vZome` | 78 / 96 | 147 / 192 | 18 | 45 |
