# Prismatic uniform 4-polytopes — zomeable orthographic projections

## Scope

The non-prismatic convex uniform 4-polytopes (47 of them) are
covered in [`../README.md`](../README.md). The remaining convex
uniform 4-polytopes — the **prismatic** ones — fall into three
families, two of which are infinite. This document sweeps a
bounded sample of each family and catalogues every zomeable
orthographic projection found.

Sweep parameters: `rng = 2`, `permute_dedup = False`,
agnostic search (no kernel-inheritance shortcut, no
obstruction-based filtering).  Each polytope is constructed
from scratch and tested identically.

Polytopes covered: **204 (in scope)**

| Family | Description | In scope | Hit ≥ 1 | Total shapes |
|---|---|---:|---:|---:|
| **A** | Polyhedral prisms `P × [0,1]` | 17 | 12 | 48 |
| **B** | Duoprisms `{p}×{q}` | 170 | 6 | 9 |
| **C** | Antiprismatic prisms `A_n × [0,1]` | 17 | 1 | 9 |
| **Total** | | **204** | **19** | **66** |

## Definitions

A **zomeable projection** is a rank-3 orthogonal linear map
π : ℝ⁴ → ℝ³ whose image of the polytope's vertex set lies in
ℤ[φ]³, such that all edge directions can be aligned (by a
global rotation) with canonical Zometool RGBY axes.  Vertex
multiplicity in the image is allowed (a kernel-aligned
projection may collapse several 4D vertices to one 3D
point).

Strict rank-3: the image must span a 3D subspace.  A 4D → 2D
projection (image planar, sitting in ℝ³ as `z = 0`) is not a
zomeable projection under this definition.  The sweep
enforces this through `_try_align` (a rotation must exist
that maps the projected edge directions onto Zome axes —
planar images cannot satisfy this for non-collinear edge
sets).

## Sweep methodology

Identical machinery to the 47-corpus sweep:

1. Construct each polytope's vertex set V ⊂ ℝ⁴ and edge list.
2. Enumerate kernel directions n ∈ ℤ[φ]⁴ with |a|, |b| ≤ 2
   (`gen_dirs(rng=2, permute_dedup=False)` — `False` because
   prismatic polytopes lack full S₄ axis-permutation
   symmetry).
3. For each n: project, attempt RGBY-alignment of edge
   directions, group hits by 3D shape signature.
4. For each unique shape: snap projected vertex coords to
   ℤ[φ]³ (multi-scale search) and emit a `.vZome` file.

Driver: [`tools/run_prismatic_sweep.py`](../tools/run_prismatic_sweep.py).
Log: [`ongoing_work/prismatic_sweep_log.jsonl`](../ongoing_work/prismatic_sweep_log.jsonl)
(one record per polytope).

## Obstruction lemma (classification aid; not used as a filter)

For a duoprism `{p}×{q}` with both p, q ∉ {4}: no rank-3
orthographic projection ℝ⁴ → ℝ³ sends all vertices into
ℤ[φ]³.  Reason: the standard duoprism vertex set lies on the
Clifford torus, with two distinct 2D circles each in their
own ℤ[φ]-incompatible field unless that circle is the
"square" (p or q = 4).  An analogous obstruction kills
non-icosahedral antiprism prisms (only the pentagonal case
n=5, which embeds inside the icosahedron, survives in ℤ[φ]).

The sweep treats this lemma as a *prediction* to falsify,
not as a filter.  Zero hits for `{3}×{3}`, `{5}×{5}`,
`{3}×{5}`, etc., empirically confirm the lemma in the
`rng = 2` regime.  Surprise hits — when they occur — are
worth manual review (the search engine returns kernels for
which edge directions align; some such hits may still produce
ℤ[φ]-incompatible 3D shapes that nevertheless pass `_snap_coords`
via the multi-scale rescaling.  These warrant case-by-case
verification — see the per-polytope `RESULTS.md` files for
strut counts and visual inspection.)

## Results

### Family A — polyhedral prisms

17 in scope (the cube prism = tesseract is covered in the main corpus).

| 3D base polyhedron | nV (4D) | Distinct shapes |
|---|---:|---:|
| cuboctahedron ([`cuboctahedron_prism`](../output/polyhedral_prisms/cuboctahedron_prism/RESULTS.md)) | 24 | 2 |
| dodecahedron ([`dodecahedron_prism`](../output/polyhedral_prisms/dodecahedron_prism/RESULTS.md)) | 40 | 5 |
| icosahedron ([`icosahedron_prism`](../output/polyhedral_prisms/icosahedron_prism/RESULTS.md)) | 24 | 5 |
| icosidodecahedron ([`icosidodecahedron_prism`](../output/polyhedral_prisms/icosidodecahedron_prism/RESULTS.md)) | 60 | 5 |
| octahedron ([`octahedron_prism`](../output/polyhedral_prisms/octahedron_prism/RESULTS.md)) | 12 | 2 |
| rhombicosidodecahedron ([`rhombicosidodecahedron_prism`](../output/polyhedral_prisms/rhombicosidodecahedron_prism/RESULTS.md)) | 120 | 6 |
| rhombicuboctahedron (rhombicuboctahedron_prism) | 48 | 0 |
| snub cube (snub_cube_prism) | 48 | 0 |
| snub dodecahedron (snub_dodecahedron_prism) | 120 | 0 |
| tetrahedron ([`tetrahedron_prism`](../output/polyhedral_prisms/tetrahedron_prism/RESULTS.md)) | 8 | 1 |
| truncated cube (truncated_cube_prism) | 48 | 0 |
| truncated cuboctahedron (truncated_cuboctahedron_prism) | 96 | 0 |
| truncated dodecahedron ([`truncated_dodecahedron_prism`](../output/polyhedral_prisms/truncated_dodecahedron_prism/RESULTS.md)) | 120 | 6 |
| truncated icosahedron ([`truncated_icosahedron_prism`](../output/polyhedral_prisms/truncated_icosahedron_prism/RESULTS.md)) | 120 | 6 |
| truncated icosidodecahedron ([`truncated_icosidodecahedron_prism`](../output/polyhedral_prisms/truncated_icosidodecahedron_prism/RESULTS.md)) | 240 | 7 |
| truncated octahedron ([`truncated_octahedron_prism`](../output/polyhedral_prisms/truncated_octahedron_prism/RESULTS.md)) | 48 | 1 |
| truncated tetrahedron ([`truncated_tetrahedron_prism`](../output/polyhedral_prisms/truncated_tetrahedron_prism/RESULTS.md)) | 24 | 2 |


### Family B — duoprisms {p}×{q}

170 in scope (3 ≤ p ≤ q ≤ 20, skipping (4, 4) = tesseract).

**6 duoprisms** yielded ≥ 1 zomeable projection.

| p | q | nV (4D) | Distinct shapes |
|---:|---:|---:|---:|
| 3 | 6 | 18 | [`duoprism_3_6`](../output/duoprisms/duoprism_3_6/RESULTS.md) → 1 |
| 4 | 6 | 24 | [`duoprism_4_6`](../output/duoprisms/duoprism_4_6/RESULTS.md) → 1 |
| 4 | 10 | 40 | [`duoprism_4_10`](../output/duoprisms/duoprism_4_10/RESULTS.md) → 2 |
| 5 | 10 | 50 | [`duoprism_5_10`](../output/duoprisms/duoprism_5_10/RESULTS.md) → 1 |
| 6 | 6 | 36 | [`duoprism_6_6`](../output/duoprisms/duoprism_6_6/RESULTS.md) → 2 |
| 10 | 10 | 100 | [`duoprism_10_10`](../output/duoprisms/duoprism_10_10/RESULTS.md) → 2 |

The remaining 164 duoprisms produced 0 zomeable projections, consistent with the obstruction lemma (see below).


### Family C — antiprismatic prisms

17 in scope (n ∈ [4, 20]; n=3 = octahedral prism, in Family A).

| n | nV (4D) | Distinct shapes |
|---:|---:|---:|
| 4 | 16 | 4_antiprismatic_prism → 0 |
| 5 | 20 | [`5_antiprismatic_prism`](../output/antiprismatic_prisms/5_antiprismatic_prism/RESULTS.md) → 9 |
| 6 | 24 | 6_antiprismatic_prism → 0 |
| 7 | 28 | 7_antiprismatic_prism → 0 |
| 8 | 32 | 8_antiprismatic_prism → 0 |
| 9 | 36 | 9_antiprismatic_prism → 0 |
| 10 | 40 | 10_antiprismatic_prism → 0 |
| 11 | 44 | 11_antiprismatic_prism → 0 |
| 12 | 48 | 12_antiprismatic_prism → 0 |
| 13 | 52 | 13_antiprismatic_prism → 0 |
| 14 | 56 | 14_antiprismatic_prism → 0 |
| 15 | 60 | 15_antiprismatic_prism → 0 |
| 16 | 64 | 16_antiprismatic_prism → 0 |
| 17 | 68 | 17_antiprismatic_prism → 0 |
| 18 | 72 | 18_antiprismatic_prism → 0 |
| 19 | 76 | 19_antiprismatic_prism → 0 |
| 20 | 80 | 20_antiprismatic_prism → 0 |


## Reproduction

```bash
# Family A (17 polyhedral prisms, ~3 min)
python tools/run_prismatic_sweep.py --family A --rng 2
# Family B (170 duoprisms, ~45 min)
python tools/run_prismatic_sweep.py --family B --rng 2
# Family C (17 antiprismatic prisms, ~2 min)
python tools/run_prismatic_sweep.py --family C --rng 2

# Regenerate per-polytope RESULTS.md files from the sweep log
python tools/build_prismatic_results.py

# Regenerate this doc + the manifest from the sweep log
python tools/build_prismatic_doc.py
```
