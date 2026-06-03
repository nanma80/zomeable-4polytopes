# bitruncated 120-cell hidden-cell removal

These files are derived from `output/uniform/bitruncated_120cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `bitruncated_120cell_cell_first_truncated_icosahedron.vZome` | unchanged (no derived file) | 1860 / 1860 | 3600 / 3600 | 0 | 0 |
