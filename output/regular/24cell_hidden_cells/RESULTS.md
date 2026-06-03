# 24-cell hidden-cell removal

These files are derived from `output/regular/24cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `24cell_short_root_cuboctahedron.vZome` | unchanged (no derived file) | 18 / 18 | 60 / 60 | 0 | 0 |
| `24cell_long_root_rhombic_dodecahedron.vZome` | unchanged (no derived file) | 15 / 15 | 44 / 44 | 0 | 0 |
| `24cell_triality.vZome` | `24cell_triality_front_visible.vZome` | 21 / 24 | 72 / 96 | 3 | 24 |
