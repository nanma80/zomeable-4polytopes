# truncated 16-cell hidden-cell removal

These files are derived from `output/uniform/truncated_16cell/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `truncated_16cell_edge_first.vZome` | unchanged (no derived file) | 28 / 28 | 57 / 57 | 0 | 0 |
| `truncated_16cell_cell_first_octahedron.vZome` | unchanged (no derived file) | 36 / 36 | 78 / 78 | 0 | 0 |
| `truncated_16cell_cell_first_truncated_tetrahedron.vZome` | `truncated_16cell_cell_first_truncated_tetrahedron_front_visible.vZome` | 48 / 48 | 108 / 120 | 0 | 12 |
| `truncated_16cell_oblique_00.vZome` | `truncated_16cell_oblique_00_front_visible.vZome` | 42 / 48 | 93 / 120 | 6 | 27 |
| `truncated_16cell_oblique_01.vZome` | `truncated_16cell_oblique_01_front_visible.vZome` | 42 / 48 | 93 / 120 | 6 | 27 |
| `truncated_16cell_oblique_02.vZome` | `truncated_16cell_oblique_02_front_visible.vZome` | 39 / 48 | 90 / 120 | 9 | 30 |
