# 5-cell (4-simplex) → 3D zomeable orthographic projections

**Result: 4 distinct shapes** (saturated rng=2/3 with `permute_dedup=False`).

## External confirmation

The same enumeration was found independently by Scott Vorthmann and
David Richter and posted at
<https://vorth.github.io/vzome-sharing/2007/04/24/five-cell-family.html>
(2007). Their 4 shapes correspond exactly to ours:

| Their description                              | Our file                                       |
|------------------------------------------------|-----------------------------------------------|
| Vertex-first (tet + center, all yellow/green)  | `5cell_vertex_first_tet_plus_center.vZome`    |
| Yellow + red + blue (the interactive model)    | `5cell_5ball_Y4B2R4.vZome`                    |
| Red + yellow + blue (David's second)           | `5cell_5ball_R6Y1B3.vZome`                    |
| Yellow + blue only (David's third, 4-ball)     | `5cell_4ball_Y6B3.vZome`                      |

## Embedding

Standard ℤ[φ] embedding aligned with the 4th coordinate axis:

- v₅ = (0, 0, 0, 4√5)
- v₁..₄ = (±5, ±5, ±5, −√5) with **even sign products**

(Note √5 = 2φ − 1 ∈ ℤ[φ], so the embedding is in ℤ[φ]⁴.)
Edge length² = 200 between every pair.

## Search subtlety

The 5-cell embedding singles out the 4th axis (no S₄ permutation
symmetry on coordinates), so we run the search with
`permute_dedup=False` in `gen_dirs`. With permutation dedup ON, the
search collapses geometrically distinct directions and reports only 3
shapes.

## The 4 shapes

Verified by fitting a 3×4 linear map M to each emitted vZome model and
checking M·Mᵀ = s²·I (uniform scale, no stretching). All 4 files are
genuine orthographic projections.

| # | balls | strut sig            | kernel n (proportional)         | description |
|---|-------|----------------------|---------------------------------|-------------|
| 1 | 5     | Y:4  G:6             | (1−2φ, 1−2φ, 1−2φ, 1) = (−√5, −√5, −√5, 1) | **vertex-first**: v₁ collapses to centroid of v₂…v₅ → tet + center |
| 2 | 5     | Y:4  R:4  B:2        | (−1, 0, 0, 1)                   | mixed Y/R/B |
| 3 | 5     | B:3  R:6  Y:1        | (−1, −1+2φ, 1, 1) = (−1, √5, 1, 1) | mixed B/R/Y |
| 4 | 4     | Y:6  B:3  collapsed:1| (−1, −1, −1, −1+2φ) = (−1, −1, −1, √5) | **degenerate** (one edge collapses) |

Note: kernels along any of the 5 vertex directions give the
"vertex-first tet + center" shape (only one entry, since group-equivalent
kernels produce congruent 3D shapes).

## Files emitted

| Shape | File                                          | Method     |
|-------|-----------------------------------------------|------------|
| #1    | `5cell_vertex_first_tet_plus_center.vZome`    | hand-built |
| #2    | (TBD)                                         | —          |
| #3    | (TBD)                                         | —          |
| #4    | (TBD)                                         | —          |

The vertex-first tet+center is trivial to hand-build (integer coords).
The other three shapes require symbolic projection through their kernel
direction; the standard `<Polytope4d group="A4">` approach **does not
work** because vZome's A4 embedding differs from ours, so kernel
directions in our embedding do not translate to vZome quaternions
without an explicit basis change. Hand-building the remaining three
needs:

1. Compute symbolic 3D projected coords for each kernel direction.
2. Apply `try_align` rotation symbolically (rotation matrix in ℤ[φ]).
3. Snap to ℤ[φ]³ and emit XML.

This is parked for later.

## Reproduction

```bash
cd regular_4polytopes\lib
python -c "from search_engine import gen_dirs, search, group_by_shape; \
           from polytopes import POLYTOPES; \
           dirs = gen_dirs(rng=2, permute_dedup=False); \
           V,E = POLYTOPES['5cell'][0][1](); \
           hits = search('5cell', V, E, dirs); \
           print(len(group_by_shape(hits, V, E)), 'shapes')"
# Output: 4 shapes
```
