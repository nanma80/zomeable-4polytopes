# duoprism 4 10 hidden-cell removal

These files are derived from `output/duoprisms/duoprism_4_10/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `duoprism_4_10_inf_family_a2phi-3_b2-phi.vZome` | unchanged (no derived file) | 40 / 40 | 80 / 80 | 0 | 0 |
| `duoprism_4_10_inf_family_aphi_b4phi-1.vZome` | unchanged (no derived file) | 40 / 40 | 80 / 80 | 0 | 0 |
| `duoprism_4_10_inf_family_a4phi-3_b4+3phi.vZome` | unchanged (no derived file) | 40 / 40 | 80 / 80 | 0 | 0 |
| `duoprism_4_10_inf_family_a2phi-3_b1+phi.vZome` | unchanged (no derived file) | 40 / 40 | 80 / 80 | 0 | 0 |
| `duoprism_4_10_inf_family_aphi-1_b3+4phi.vZome` | unchanged (no derived file) | 40 / 40 | 80 / 80 | 0 | 0 |
| `cell_first_cube.vZome` | unchanged (no derived file) | 24 / 24 | 44 / 44 | 0 | 0 |
