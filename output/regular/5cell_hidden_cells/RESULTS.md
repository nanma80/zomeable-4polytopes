# 5-cell hidden-cell removal

These files are derived from `output/regular/5cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `5cell_vertex_first_tet_plus_center.vZome` | `5cell_vertex_first_tet_plus_center_front_visible.vZome` | 4 / 5 | 6 / 10 | 1 | 4 |
| `5cell_5ball_Y4B2R4.vZome` | unchanged (no derived file) | 5 / 5 | 10 / 10 | 0 | 0 |
| `5cell_5ball_R6Y1B3.vZome` | `5cell_5ball_R6Y1B3_front_visible.vZome` | 5 / 5 | 9 / 10 | 0 | 1 |
| `5cell_4ball_Y6B3.vZome` | unchanged (no derived file) | 4 / 4 | 6 / 6 | 0 | 0 |
