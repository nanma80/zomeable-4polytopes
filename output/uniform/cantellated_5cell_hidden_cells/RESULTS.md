# cantellated 5-cell hidden-cell removal

These files are derived from `output/uniform/cantellated_5cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `cantellated_5cell_oblique_00.vZome` | `cantellated_5cell_oblique_00_front_visible.vZome` | 27 / 30 | 72 / 90 | 3 | 18 |
| `cantellated_5cell_oblique_02.vZome` | `cantellated_5cell_oblique_02_front_visible.vZome` | 27 / 30 | 73 / 90 | 3 | 17 |
| `cantellated_5cell_cell_first_octahedron.vZome` | `cantellated_5cell_cell_first_octahedron_front_visible.vZome` | 30 / 30 | 78 / 90 | 0 | 12 |
| `cantellated_5cell_oblique_01.vZome` | unchanged (no derived file) | 18 / 18 | 42 / 42 | 0 | 0 |
