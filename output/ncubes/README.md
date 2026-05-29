# Strict zomeable n-cube projection models

These folders contain concrete `.vZome` models for strict zomeable
orthographic projections of n-cubes that also satisfy the essential
general-position filter: every projected generator triplet spans 3D.

| n | emitted models | notes |
|---:|:---|:---|
| 3 | `ncube_3_cube.vZome` | baseline cube |
| 4 | `ncube_4_vertex_first_rhombic_dodecahedron_N15_64bc42a7c2b8.vZome` | all latest-bound essential sweep representatives |
| 5 | none | no latest-bound essential representatives found |
| 6 | `ncube_6_essential_candidate_N58_cb02a32360a4.vZome`<br>`ncube_6_essential_candidate_N63_3b1c7b06d29d.vZome`<br>`ncube_6_essential_candidate_N64_0ae3735889e4.vZome`<br>`ncube_6_essential_candidate_N64_1ddb6225f607.vZome`<br>`ncube_6_essential_candidate_N64_1f11e03db897.vZome`<br>`ncube_6_essential_candidate_N64_2b777b0be9ad.vZome`<br>`ncube_6_essential_candidate_N64_3a4cad3346a7.vZome`<br>`ncube_6_essential_candidate_N64_3d3456a501a2.vZome`<br>`ncube_6_essential_candidate_N64_7a0c1b9ac842.vZome`<br>`ncube_6_essential_candidate_N64_7e40e8b0dc89.vZome` | curated subset of latest-bound essential sweep representatives |
| 7 | none | R=2 sweep stopped before completion; no catalog models retained |

The essential filter is the exact condition

```text
rank(v_i, v_j, v_k) = 3 for every distinct triple i,j,k.
```

The sweep-backed entries come from exact bounded generator sweeps. This
is not a completeness proof beyond the recorded bounds.

For n=6, the R=2 sweep found 46 strict signatures, but this directory
keeps only the 10 models retained after visual spot-checking. The larger
strict sweep direction was abandoned because it produced too many
seemingly arbitrary models even under the general-position filter.

Regenerate with:

```powershell
python tools\ncube\emit_ncube_models.py
```
