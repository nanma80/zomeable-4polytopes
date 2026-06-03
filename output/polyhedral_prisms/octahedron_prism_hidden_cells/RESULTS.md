# octahedron prism hidden-cell removal

These files are derived from `output/polyhedral_prisms/octahedron_prism/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `edge_first.vZome` | unchanged (no derived file) | 10 / 10 | 21 / 21 | 0 | 0 |
| `cell_first_octahedron.vZome` | unchanged (no derived file) | 6 / 6 | 12 / 12 | 0 | 0 |
