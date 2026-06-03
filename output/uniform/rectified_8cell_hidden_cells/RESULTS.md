# rectified tesseract hidden-cell removal

These files are derived from `output/uniform/rectified_8cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `rectified_8cell_face_first_square.vZome` | unchanged (no derived file) | 20 / 20 | 48 / 48 | 0 | 0 |
| `rectified_8cell_cell_first_cuboctahedron.vZome` | unchanged (no derived file) | 20 / 20 | 48 / 48 | 0 | 0 |
| `rectified_8cell_cell_first_tetrahedron.vZome` | `rectified_8cell_cell_first_tetrahedron_front_visible.vZome` | 28 / 32 | 78 / 96 | 4 | 18 |
| `rectified_8cell_oblique_00.vZome` | `rectified_8cell_oblique_00_front_visible.vZome` | 28 / 32 | 75 / 96 | 4 | 21 |
| `rectified_8cell_oblique_01.vZome` | `rectified_8cell_oblique_01_front_visible.vZome` | 28 / 32 | 75 / 96 | 4 | 21 |
| `rectified_8cell_oblique_02.vZome` | `rectified_8cell_oblique_02_front_visible.vZome` | 29 / 32 | 78 / 96 | 3 | 18 |
