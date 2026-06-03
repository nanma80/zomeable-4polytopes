# duoprism 6 6 hidden-cell removal

These files are derived from `output/duoprisms/duoprism_6_6/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `face_first_hexagon_00.vZome` | unchanged (no derived file) | 18 / 18 | 30 / 30 | 0 | 0 |
| `oblique_67.vZome` | `oblique_67_front_visible.vZome` | 32 / 36 | 60 / 72 | 4 | 12 |
