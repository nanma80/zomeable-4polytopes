# icosahedron prism hidden-cell removal

These files are derived from `output/polyhedral_prisms/icosahedron_prism/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `oblique_00.vZome` | `oblique_00_front_visible.vZome` | 21 / 24 | 57 / 72 | 3 | 15 |
| `face_first_square.vZome` | unchanged (no derived file) | 16 / 16 | 38 / 38 | 0 | 0 |
| `oblique_01.vZome` | `oblique_01_front_visible.vZome` | 23 / 24 | 61 / 72 | 1 | 11 |
| `oblique_02.vZome` | `oblique_02_front_visible.vZome` | 23 / 24 | 61 / 72 | 1 | 11 |
| `cell_first_icosahedron.vZome` | unchanged (no derived file) | 12 / 12 | 30 / 30 | 0 | 0 |
