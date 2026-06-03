# 5 antiprismatic prism hidden-cell removal

These files are derived from `output/antiprismatic_prisms/5_antiprismatic_prism/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `oblique_00.vZome` | `oblique_00_front_visible.vZome` | 18 / 20 | 41 / 50 | 2 | 9 |
| `oblique_01.vZome` | `oblique_01_front_visible.vZome` | 16 / 16 | 35 / 36 | 0 | 1 |
| `face_first_square.vZome` | unchanged (no derived file) | 12 / 12 | 24 / 24 | 0 | 0 |
| `oblique_02.vZome` | `oblique_02_front_visible.vZome` | 19 / 20 | 43 / 50 | 1 | 7 |
| `oblique_03.vZome` | `oblique_03_front_visible.vZome` | 19 / 20 | 43 / 50 | 1 | 7 |
| `oblique_04.vZome` | `oblique_04_front_visible.vZome` | 18 / 20 | 41 / 50 | 2 | 9 |
| `oblique_05.vZome` | `oblique_05_front_visible.vZome` | 20 / 20 | 45 / 50 | 0 | 5 |
| `cell_first_pentagonal_antiprism.vZome` | unchanged (no derived file) | 10 / 10 | 20 / 20 | 0 | 0 |
| `oblique_06.vZome` | `oblique_06_front_visible.vZome` | 20 / 20 | 45 / 50 | 0 | 5 |
