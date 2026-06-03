# runcinated 5-cell hidden-cell removal

These files are derived from `output/uniform/runcinated_5cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `runcinated_5cell_oblique_00.vZome` | `runcinated_5cell_oblique_00_front_visible.vZome` | 17 / 20 | 45 / 60 | 3 | 15 |
| `runcinated_5cell_oblique_01.vZome` | `runcinated_5cell_oblique_01_front_visible.vZome` | 18 / 20 | 47 / 60 | 2 | 13 |
| `runcinated_5cell_vertex_first.vZome` | unchanged (no derived file) | 13 / 13 | 30 / 30 | 0 | 0 |
| `runcinated_5cell_cell_first_tetrahedron.vZome` | `runcinated_5cell_cell_first_tetrahedron_front_visible.vZome` | 16 / 20 | 42 / 60 | 4 | 18 |
