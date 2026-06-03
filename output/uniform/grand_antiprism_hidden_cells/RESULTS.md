# Grand antiprism hidden-cell removal

These files are derived from `output/uniform/grand_antiprism/` by removing
balls and struts belonging only to 4D cells hidden from the positive side of
each projection kernel.  Surviving `.vZome` commands are copied from the
original files; the derived models should therefore be the old models with
some balls/edges removed and no moved geometry.

Equatorial cells are kept.  A cell is removed only when its outward normal has
strictly negative dot product with the chosen kernel direction.

| Source | Front-visible file | Balls | Edges | Removed balls | Removed edges |
|---|---|---:|---:|---:|---:|
| `grand_antiprism_vertex_first.vZome` | `grand_antiprism_vertex_first_front_visible.vZome` | 67 / 71 | 288 / 342 | 4 | 54 |
| `grand_antiprism_ring_first.vZome` | unchanged (no derived file) | 60 / 60 | 260 / 260 | 0 | 0 |
