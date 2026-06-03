# truncated 24-cell hidden-cell removal

These files are derived from `output/uniform/truncated_24cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `truncated_24cell_cell_first_truncated_octahedron.vZome` | unchanged (no derived file) | 120 / 120 | 216 / 216 | 0 | 0 |
| `truncated_24cell_cell_first_cube.vZome` | unchanged (no derived file) | 96 / 96 | 176 / 176 | 0 | 0 |
| `truncated_24cell_oblique.vZome` | `truncated_24cell_oblique_front_visible.vZome` | 150 / 192 | 285 / 384 | 42 | 99 |
