# truncated icosahedron prism hidden-cell removal

These files are derived from `output/polyhedral_prisms/truncated_icosahedron_prism/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `oblique_00.vZome` | `oblique_00_front_visible.vZome` | 99 / 120 | 183 / 240 | 21 | 57 |
| `face_first_square.vZome` | unchanged (no derived file) | 64 / 64 | 118 / 118 | 0 | 0 |
| `oblique_01.vZome` | `oblique_01_front_visible.vZome` | 100 / 120 | 185 / 240 | 20 | 55 |
| `oblique_02.vZome` | `oblique_02_front_visible.vZome` | 100 / 120 | 185 / 240 | 20 | 55 |
| `cell_first_truncated_icosahedron.vZome` | unchanged (no derived file) | 60 / 60 | 90 / 90 | 0 | 0 |
