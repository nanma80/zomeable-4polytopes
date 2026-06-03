# Snub 24-cell hidden-cell removal

These files are derived from `output/uniform/snub_24cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `snub_24cell_cell_first.vZome` | unchanged (no derived file) | 60 / 60 | 228 / 228 | 0 | 0 |
| `snub_24cell_vertex_first.vZome` | `snub_24cell_vertex_first_front_visible.vZome` | 63 / 69 | 246 / 312 | 6 | 66 |
