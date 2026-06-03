# truncated icosidodecahedron prism hidden-cell removal

These files are derived from `output/polyhedral_prisms/truncated_icosidodecahedron_prism/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `oblique_00.vZome` | `oblique_00_front_visible.vZome` | 200 / 240 | 375 / 480 | 40 | 105 |
| `cell_first_cube.vZome` | unchanged (no derived file) | 120 / 120 | 228 / 228 | 0 | 0 |
| `oblique_01.vZome` | `oblique_01_front_visible.vZome` | 200 / 240 | 375 / 480 | 40 | 105 |
| `oblique_02.vZome` | `oblique_02_front_visible.vZome` | 198 / 240 | 369 / 480 | 42 | 111 |
| `cell_first_truncated_icosidodecahedron.vZome` | unchanged (no derived file) | 120 / 120 | 180 / 180 | 0 | 0 |
