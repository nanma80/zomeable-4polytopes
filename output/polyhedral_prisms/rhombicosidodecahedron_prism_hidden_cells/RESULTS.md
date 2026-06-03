# rhombicosidodecahedron prism hidden-cell removal

These files are derived from `output/polyhedral_prisms/rhombicosidodecahedron_prism/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `oblique_00.vZome` | `oblique_00_front_visible.vZome` | 105 / 120 | 245 / 300 | 15 | 55 |
| `cell_first_cube.vZome` | unchanged (no derived file) | 64 / 64 | 144 / 144 | 0 | 0 |
| `oblique_01.vZome` | `oblique_01_front_visible.vZome` | 105 / 110 | 245 / 290 | 5 | 45 |
| `oblique_02.vZome` | `oblique_02_front_visible.vZome` | 102 / 120 | 237 / 300 | 18 | 63 |
| `cell_first_rhombicosidodecahedron.vZome` | unchanged (no derived file) | 60 / 60 | 120 / 120 | 0 | 0 |
