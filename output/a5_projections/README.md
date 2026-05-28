# A5 simplex family projections

Strict orthographic 3D projections of the A5 (5-simplex) uniform family: the 5-simplex, rectified 5-simplex, and birectified 5-simplex.

The 9 `.vZome` files are organized in per-polytope subfolders.  "Balls" counts distinct 3D ball positions in the projected vZome model.

Open the viewer index here:

- [`VIEWER.md`](VIEWER.md)

## Models

| File | Source polytope | Balls | Symmetry order | Scale | Colors | Buildable |
|---:|---|---:|---:|---|---|:---:|
| `5_simplex/5_simplex_sym48_6balls_53a41b.vZome` | 5-simplex (hexateron) | 6 | 48 | `phi^2` | B(x2)x3, Gx12 | yes |
| `5_simplex/5_simplex_sym24_5balls_4fb6eb.vZome` | 5-simplex (hexateron) | 5 | 24 | `phi^2/3` | Gx6, Yx4 | yes |
| `5_simplex/5_simplex_sym6_5balls_cfe09c.vZome` | 5-simplex (hexateron) | 5 | 6 | `phi^2` | Bx3, Gx3, Yx4 | direction-only |
| `rectified_5_simplex/rectified_5_simplex_sym48_13balls_53a41b.vZome` | Rectified 5-simplex | 13 | 48 | `phi^2` | B(x2)x12, Gx36 | yes |
| `rectified_5_simplex/rectified_5_simplex_sym24_11balls_4fb6eb.vZome` | Rectified 5-simplex | 11 | 24 | `phi^2/3` | Gx18, Yx16 | yes |
| `rectified_5_simplex/rectified_5_simplex_sym6_11balls_cfe09c.vZome` | Rectified 5-simplex | 11 | 6 | `phi^2` | Bx9, Gx9, Yx16 | direction-only |
| `birectified_5_simplex/birectified_5_simplex_sym48_14balls_4fb6eb.vZome` | Birectified 5-simplex | 14 | 48 | `phi^2/3` | Gx24, Yx24 | yes |
| `birectified_5_simplex/birectified_5_simplex_sym48_14balls_53a41b.vZome` | Birectified 5-simplex | 14 | 48 | `phi^2` | B(x2)x15, Gx36 | yes |
| `birectified_5_simplex/birectified_5_simplex_sym12_14balls_cfe09c.vZome` | Birectified 5-simplex | 14 | 12 | `phi^2` | Bx12, Gx12, Yx24 | direction-only |

6 of 9 models are fully buildable with standard vZome struts (a phi-power strut length, or exactly double one, matched per color orbit); every model is direction-zomeable (all edges parallel to a zometool axis).  Models are centered on the ball centroid, scaled by a power of phi, and the auto-created origin ball is deleted.

## Provenance

Found by a polytope-independent raw-column `Z[phi]^3` sweep that enumerates every strict-orthographic projection whose columns and pairwise column differences are zometool axes.  R=1, R=2, and R=3 all saturate at the same three projection geometries.  See [`../../docs/A5_PROJECTIONS.md`](../../docs/A5_PROJECTIONS.md).
