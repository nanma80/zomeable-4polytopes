# Prismatic uniform 4-polytopes — zomeable orthographic projections

## Scope

The non-prismatic convex uniform 4-polytopes (47 of them) are
covered in [`../README.md`](../README.md). The remaining convex
uniform 4-polytopes — the **prismatic** ones — fall into three
families, two of which are infinite. This document sweeps a
bounded sample of each family and catalogues every zomeable
orthographic projection found.

Sweep parameters: `rng = 3`, `permute_dedup = False`,
agnostic search (no kernel-inheritance shortcut, no
obstruction-based filtering).  Each polytope is constructed
from scratch and tested identically.

Polytopes covered: **204 (in scope)**

| Family | Description | In scope | Hit ≥ 1 | Total shapes |
|---|---|---:|---:|---:|
| **A** | Polyhedral prisms `P × [0,1]` | 17 | 12 | 45 |
| **B** | Duoprisms `{p}×{q}` | 170 | 6 | 8 + 2 inf families |
| **C** | Antiprismatic prisms `A_n × [0,1]` | 17 | 1 | 9 |
| **Total** | | **204** | **19** | **62 + 2 inf families** |

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

## Methodology

Identical machinery to the 47-corpus sweep:

1. Construct each polytope's vertex set V ⊂ ℝ⁴ and edge list.
2. Enumerate kernel directions n ∈ ℤ[φ]⁴ with |a|, |b| ≤ 3
   (`gen_dirs(rng=3, permute_dedup=False)` — `False` because
   prismatic polytopes lack full S₄ axis-permutation
   symmetry).
3. For each n: project, attempt RGBY-alignment of edge
   directions, group hits by 3D shape signature.
4. For each unique shape: snap projected vertex coords to
   ℤ[φ]³ (multi-scale search) and emit a `.vZome` file.

Constructive follow-up (2026-05-29): the finite snap/signature probes for
`{4}×{6}` and `{4}×{10}` missed inf families, because their fixed
alignment/scale search was not a proof of boundedness.  The exact emitter
`tools/emit_duoprism_inf_family.py` now emits representative members directly
from the arithmetic conditions below.

Post-audit note: the original generic emitter stopped after the first valid
edge-axis alignment.  Some symmetric projections have multiple valid alignments,
where only a later alignment gives exact ℤ[φ]³ vertex coordinates.  The emitter
now tries all valid alignments before declaring `snap_failed`.  Rechecking the
feature-aligned snap failures recovered four additional models:
`tetrahedron_prism/face_first_square`, `truncated_octahedron_prism/cell_first_cube`,
`duoprism_4_6/cell_first_cube`, and `duoprism_4_10/cell_first_cube`.

Driver: [`tools/run_prismatic_sweep.py`](../tools/run_prismatic_sweep.py).
Log: [`ongoing_work/prismatic_sweep_log.jsonl`](../ongoing_work/prismatic_sweep_log.jsonl)
(one record per polytope).

## Results

### Family A — polyhedral prisms

17 in scope (the cube prism = tesseract is covered in the main corpus).

| 3D base polyhedron | Distinct shapes |
|---|---:|
| cuboctahedron ([`cuboctahedron_prism`](../output/polyhedral_prisms/cuboctahedron_prism/RESULTS.md)) | 2 |
| dodecahedron ([`dodecahedron_prism`](../output/polyhedral_prisms/dodecahedron_prism/RESULTS.md)) | 5 |
| icosahedron ([`icosahedron_prism`](../output/polyhedral_prisms/icosahedron_prism/RESULTS.md)) | 5 |
| icosidodecahedron ([`icosidodecahedron_prism`](../output/polyhedral_prisms/icosidodecahedron_prism/RESULTS.md)) | 5 |
| octahedron ([`octahedron_prism`](../output/polyhedral_prisms/octahedron_prism/RESULTS.md)) | 2 |
| rhombicosidodecahedron ([`rhombicosidodecahedron_prism`](../output/polyhedral_prisms/rhombicosidodecahedron_prism/RESULTS.md)) | 5 |
| rhombicuboctahedron (rhombicuboctahedron_prism) | 0 |
| snub cube (snub_cube_prism) | 0 |
| snub dodecahedron (snub_dodecahedron_prism) | 0 |
| tetrahedron ([`tetrahedron_prism`](../output/polyhedral_prisms/tetrahedron_prism/RESULTS.md)) | 2 |
| truncated cube (truncated_cube_prism) | 0 |
| truncated cuboctahedron (truncated_cuboctahedron_prism) | 0 |
| truncated dodecahedron ([`truncated_dodecahedron_prism`](../output/polyhedral_prisms/truncated_dodecahedron_prism/RESULTS.md)) | 5 |
| truncated icosahedron ([`truncated_icosahedron_prism`](../output/polyhedral_prisms/truncated_icosahedron_prism/RESULTS.md)) | 5 |
| truncated icosidodecahedron ([`truncated_icosidodecahedron_prism`](../output/polyhedral_prisms/truncated_icosidodecahedron_prism/RESULTS.md)) | 5 |
| truncated octahedron ([`truncated_octahedron_prism`](../output/polyhedral_prisms/truncated_octahedron_prism/RESULTS.md)) | 2 |
| truncated tetrahedron ([`truncated_tetrahedron_prism`](../output/polyhedral_prisms/truncated_tetrahedron_prism/RESULTS.md)) | 2 |


### Family B — duoprisms `{p}×{q}`

170 in scope (3 ≤ p ≤ q ≤ 20, skipping (4, 4) = tesseract).

**6 duoprisms** yielded ≥ 1 zomeable projection.

| p | q | Distinct shapes |
|---:|---:|---:|
| 3 | 6 | [`duoprism_3_6`](../output/duoprisms/duoprism_3_6/RESULTS.md) → 1 |
| 4 | 6 | [`duoprism_4_6`](../output/duoprisms/duoprism_4_6/RESULTS.md) → 1 cell-first + inf family |
| 4 | 10 | [`duoprism_4_10`](../output/duoprisms/duoprism_4_10/RESULTS.md) → 1 cell-first + inf family |
| 5 | 10 | [`duoprism_5_10`](../output/duoprisms/duoprism_5_10/RESULTS.md) → 1 |
| 6 | 6 | [`duoprism_6_6`](../output/duoprisms/duoprism_6_6/RESULTS.md) → 2 |
| 10 | 10 | [`duoprism_10_10`](../output/duoprisms/duoprism_10_10/RESULTS.md) → 2 |

The remaining 164 duoprisms produced 0 zomeable projections.  Most fail because at least one of the {p}-gon or {q}-gon circles lies in ℤ[√3] (p ∈ {3, 6, 12, …}) or ℤ[√2] (p ∈ {8, …}), which don't embed in the icosahedral field ℤ[φ].  The icosahedral-compatible regular polygons in range are {4} (in ℤ), {5}, and {10} (both in ℤ[φ]).

#### Infinite families

For `{4}×{q}` with kernel `n=(a,b,0,0)`, the `{q}`-gon plane is preserved and
the square factor becomes four parallel polygon layers.  The square edges are
height differences `a+b` and `a-b`, not the individual projected square basis
vectors; nevertheless these are still `Q(phi)` multiples of a single Zome axis.

- `{4}×{6}`: use a blue hexagon plane with yellow height axis.  The arithmetic
  condition is `q^2 = 3*(a^2+b^2)` with `q in Q(phi)`.  Example emitted:
  `a=2-phi`, `b=-1+3phi`, `q=-3+6phi`.
- `{4}×{10}`: use a blue decagon plane with red height axis.  The arithmetic
  condition is the tesseract support-2 condition `c^2 = a^2+b^2` with
  `c in Q(phi)`.  Examples emitted: `(a,b,c)=(5,12,13)` and `(8,15,17)`.


### Family C — antiprismatic prisms

17 in scope (n ∈ [4, 20]; n=3 = octahedral prism, in Family A).

**1 antiprismatic prism** yielded ≥ 1 zomeable projection.

| n | Distinct shapes |
|---:|---:|
| 5 | [`5_antiprismatic_prism`](../output/antiprismatic_prisms/5_antiprismatic_prism/RESULTS.md) → 9 |

The remaining 16 antiprismatic prisms (n ≠ 5) produced 0 zomeable projections: only the pentagonal antiprism embeds in ℤ[φ]³ via the icosahedron's non-polar vertices.


## Reproduction

```bash
# Family A (17 polyhedral prisms)
python tools/run_prismatic_sweep.py --family A --rng 3
# Family B (170 duoprisms)
python tools/run_prismatic_sweep.py --family B --rng 3
# Family C (17 antiprismatic prisms)
python tools/run_prismatic_sweep.py --family C --rng 3

# Regenerate per-polytope RESULTS.md files from the sweep log
python tools/build_prismatic_results.py

# Regenerate this doc + the manifest from the sweep log
python tools/build_prismatic_doc.py

# Emit constructive infinite-family examples for {4}x{6} and {4}x{10}
python tools/emit_duoprism_inf_family.py
```
