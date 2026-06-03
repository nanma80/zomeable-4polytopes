# duoprism 4 6 hidden-cell removal

These files are derived from `output/duoprisms/duoprism_4_6/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `duoprism_4_6_inf_family_a5-3phi_b2-phi.vZome` | unchanged (no derived file) | 24 / 24 | 48 / 48 | 0 | 0 |
| `duoprism_4_6_inf_family_a5-3phi_b4phi-5.vZome` | unchanged (no derived file) | 24 / 24 | 48 / 48 | 0 | 0 |
| `duoprism_4_6_inf_family_aphi_b5-2phi.vZome` | unchanged (no derived file) | 24 / 24 | 48 / 48 | 0 | 0 |
| `cell_first_cube.vZome` | unchanged (no derived file) | 16 / 16 | 28 / 28 | 0 | 0 |
