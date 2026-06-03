# truncated tetrahedron prism hidden-cell removal

These files are derived from `output/polyhedral_prisms/truncated_tetrahedron_prism/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `face_first_square.vZome` | `face_first_square_front_visible.vZome` | 24 / 24 | 46 / 48 | 0 | 2 |
| `cell_first_truncated_tetrahedron.vZome` | unchanged (no derived file) | 12 / 12 | 18 / 18 | 0 | 0 |
