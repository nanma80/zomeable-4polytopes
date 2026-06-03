# icosidodecahedron prism hidden-cell removal

These files are derived from `output/polyhedral_prisms/icosidodecahedron_prism/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `oblique_00.vZome` | `oblique_00_front_visible.vZome` | 50 / 60 | 115 / 150 | 10 | 35 |
| `edge_first.vZome` | unchanged (no derived file) | 34 / 34 | 73 / 73 | 0 | 0 |
| `oblique_01.vZome` | `oblique_01_front_visible.vZome` | 50 / 60 | 115 / 150 | 10 | 35 |
| `oblique_02.vZome` | `oblique_02_front_visible.vZome` | 51 / 60 | 117 / 150 | 9 | 33 |
| `cell_first_icosidodecahedron.vZome` | unchanged (no derived file) | 30 / 30 | 60 / 60 | 0 | 0 |
