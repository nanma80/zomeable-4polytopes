# 8-cell hidden-cell removal

These files are derived from `output/regular/8cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `8cell_cell_first_cube.vZome` | unchanged (no derived file) | 8 / 8 | 12 / 12 | 0 | 0 |
| `8cell_vertex_first_rhombic_dodec.vZome` | `8cell_vertex_first_rhombic_dodec_front_visible.vZome` | 15 / 15 | 28 / 32 | 0 | 4 |
| `8cell_phi_oblique.vZome` | `8cell_phi_oblique_front_visible.vZome` | 16 / 16 | 31 / 32 | 0 | 1 |
| `8cell_inf_family_a1_b2.vZome` | unchanged (no derived file) | 16 / 16 | 32 / 32 | 0 | 0 |
| `8cell_inf_family_a3_b4.vZome` | unchanged (no derived file) | 16 / 16 | 32 / 32 | 0 | 0 |
| `8cell_inf_family_a5_b12.vZome` | unchanged (no derived file) | 16 / 16 | 32 / 32 | 0 | 0 |
| `8cell_inf_family_a8_b15.vZome` | unchanged (no derived file) | 16 / 16 | 32 / 32 | 0 | 0 |
| `8cell_inf_family_a2_b11.vZome` | unchanged (no derived file) | 16 / 16 | 32 / 32 | 0 | 0 |
| `8cell_inf_family_a19_b22.vZome` | unchanged (no derived file) | 16 / 16 | 32 / 32 | 0 | 0 |
| `8cell_inf_family_a2_b29.vZome` | unchanged (no derived file) | 16 / 16 | 32 / 32 | 0 | 0 |
| `8cell_inf_family_phi_aSqrt5_b2.vZome` | unchanged (no derived file) | 16 / 16 | 32 / 32 | 0 | 0 |
| `8cell_inf_family_phi_a3plus2phi_b4phi-4.vZome` | unchanged (no derived file) | 16 / 16 | 32 / 32 | 0 | 0 |
| `8cell_inf_family_phi_a4phi_b5-2phi.vZome` | unchanged (no derived file) | 16 / 16 | 32 / 32 | 0 | 0 |
