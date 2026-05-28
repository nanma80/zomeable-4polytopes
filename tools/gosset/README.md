# Gosset projection sweep scripts

This folder contains the reproducibility scripts for
`output/gosset_projections/`, kept separate from the 4-polytope sweep tools.

The main algorithm is a raw-column `Z[phi]^3` sweep:

```text
P = [c_0 ... c_7],  c_i in Z[phi]^3
```

It enforces:

1. E8 type-A root zomeability: `c_i + c_j` and `c_i - c_j` lie on zome axes
   or collapse.
2. Strict orthographicity: `P P^T = c I_3`.
3. E8 type-B half-root zomeability.
4. Final strict/rank/dedup checks for all `2_21`, `3_21`, and `4_21`
   embeddings.

Useful entry points:

- `zphi_column_sweep.py` — run the R=1/R=2/R=3 sweep.
- `zphi_2_11_sweep.py` / `zphi_2_11_emit.py` — 5-orthoplex (`2_11`)
  standalone sweep and emission.
- `zphi_1_21_sweep.py` / `zphi_1_21_emit.py` — 5-demicube (`1_21`)
  standalone sweep and emission.
- `zphi_rectified_5_orthoplex_sweep.py` /
  `zphi_rectified_5_orthoplex_emit.py` — rectified 5-orthoplex (`t1 2_11`)
  standalone sweep and emission.
- `zphi_1_22_sweep.py` / `zphi_1_22_emit.py` — E6 root polytope (`1_22`)
  standalone sweep and emission.
- `zphi_1_32_emit.py` — evaluate and emit `1_32` models from the completed
  `2_31` projection directions.
- `zphi_2_41_sweep.py` / `zphi_2_41_emit.py` — direct odd-spinor E8-edge
  sweep and emission for `2_41`.
- `zphi_column_postprocess.py` — compare sweep JSON output against curated
  `.vZome` files.
- `zphi_full_dedup.py` — full Euclidean point-cloud dedup.
- `zphi_r3_leaf_estimator.py` — estimator used for the R=3 leaf count.
- `zphi_r4_profile.py` — memory-safe rough R=4 profile.
- `scale_vzome_phi.py` and `fit_vzome_view.py` — presentation helpers.
  For newly emitted Gosset-style models, also choose a physical scale so edge
  lengths become standard `phi^n` strut lengths or exactly double them.

The helper modules `lib/gosset_polytopes.py` and `lib/zometool_axes.py` are
ported with these scripts.

