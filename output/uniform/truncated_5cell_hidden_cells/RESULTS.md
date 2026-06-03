# truncated 5-cell hidden-cell removal

These files are derived from `output/uniform/truncated_5cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `truncated_5cell_oblique_00.vZome` | `truncated_5cell_oblique_00_front_visible.vZome` | 20 / 20 | 37 / 40 | 0 | 3 |
| `truncated_5cell_cell_first_tetrahedron.vZome` | unchanged (no derived file) | 20 / 20 | 40 / 40 | 0 | 0 |
| `truncated_5cell_oblique_01.vZome` | `truncated_5cell_oblique_01_front_visible.vZome` | 18 / 20 | 33 / 40 | 2 | 7 |
| `truncated_5cell_oblique_02.vZome` | unchanged (no derived file) | 13 / 13 | 21 / 21 | 0 | 0 |
