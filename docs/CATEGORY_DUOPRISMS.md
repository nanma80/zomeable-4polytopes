# Duoprisms — zomeable orthographic projections

Cartesian products {p}×{q} of two regular polygons, 3 ≤ p ≤ q ≤ 20
(excluding (4, 4) = tesseract).  170 polytopes in scope; 6 yielded
≥1 zomeable projection.

`duoprism_4_10` was the only +3 gainer at rng=4 and was investigated
for inf-family behavior — saturated bounded at 5 shapes through rng=8.
Similarly `duoprism_4_6` is bounded at 3 shapes through rng=8.

| Polytope | Zomeable shapes | Viewer |
|----------|----------------:|--------|
| {3}×{6} duoprism | 1 | [3D viewer →](../output/duoprisms/duoprism_3_6/VIEWER.md) |
| {4}×{6} duoprism | 3 | [3D viewer →](../output/duoprisms/duoprism_4_6/VIEWER.md) |
| {4}×{10} duoprism | 5 | [3D viewer →](../output/duoprisms/duoprism_4_10/VIEWER.md) |
| {5}×{10} duoprism | 1 | [3D viewer →](../output/duoprisms/duoprism_5_10/VIEWER.md) |
| {6}×{6} duoprism | 2 | [3D viewer →](../output/duoprisms/duoprism_6_6/VIEWER.md) |
| {10}×{10} duoprism | 2 | [3D viewer →](../output/duoprisms/duoprism_10_10/VIEWER.md) |


## Zero-shape duoprisms (164)

The remaining 164 duoprisms produced 0 zomeable projections.  Most fail because at least one of the {p}-gon or {q}-gon circles lies in ℤ[√3] (p ∈ {3, 6, 12, …}) or ℤ[√2] (p ∈ {8, …}), which don't embed in the icosahedral field ℤ[φ].  The icosahedral-compatible regular polygons in range are {4} (in ℤ), {5}, and {10} (both in ℤ[φ]).


## More detail

- [`docs/PRISMATIC.md`](PRISMATIC.md) — full prismatic sweep methodology and results
- [`ongoing_work/duoprism_4_10_inf_family_resolved.md`](../ongoing_work/duoprism_4_10_inf_family_resolved.md) — duoprism_4_10 saturation evidence
- [`ongoing_work/duoprism_4_6_inf_family_resolved.md`](../ongoing_work/duoprism_4_6_inf_family_resolved.md) — duoprism_4_6 saturation evidence
- [`ongoing_work/duoprism_4q_census.md`](../ongoing_work/duoprism_4q_census.md) — q ∈ {5..12} census
