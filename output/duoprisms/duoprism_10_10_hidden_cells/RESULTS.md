# duoprism 10 10 hidden-cell removal

These files are derived from `output/duoprisms/duoprism_10_10/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `face_first_decagon_00.vZome` | unchanged (no derived file) | 50 / 50 | 90 / 90 | 0 | 0 |
| `oblique_56.vZome` | `oblique_56_front_visible.vZome` | 84 / 96 | 160 / 198 | 12 | 38 |
