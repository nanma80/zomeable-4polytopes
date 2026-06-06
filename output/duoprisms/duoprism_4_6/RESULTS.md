# {4}×{6} duoprism → zomeable orthographic projections

- Family **B** (duoprism)
- 4D vertices: **24**, edges: **48**
- Folder: `output/duoprisms/duoprism_4_6/`

The zomeable set is best summarized as **1 cell-first projection + an inf
family with B/Y and G/Y subfamilies**.  The finite rng = 5 agnostic kernel
sweep found the cell-first model plus three B/Y sample members; one additional
B/Y representative and two G/Y representatives are emitted here.

## Shapes

| # | File | Label / direction | n_balls | Struts |
|---|------|-------------------|--------:|--------|
| 1 | `cell_first_cube.vZome` | cell_first / cube | 16 | B:12  G:16 |
| 2 | `duoprism_4_6_inf_family_a5-3phi_b2-phi.vZome` | inf family representative | 24 | B:24  Y:24 |
| 3 | `duoprism_4_6_inf_family_a5-3phi_b4phi-5.vZome` | inf family representative | 24 | B:24  Y:24 |
| 4 | `duoprism_4_6_inf_family_aphi_b5-2phi.vZome` | inf family representative | 24 | B:24  Y:24 |
| 5 | `duoprism_4_6_inf_family_a2-phi_b3phi-1.vZome` | inf family representative | 24 | B:24  Y:24 |
| 6 | `duoprism_4_6_inf_family_GY_a2phi-1_b1.vZome` | G/Y inf family representative | 24 | G:24  Y:24 |
| 7 | `duoprism_4_6_inf_family_GY_a2+3phi_b4+phi.vZome` | G/Y inf family representative | 24 | G:24  Y:24 |

## Inf family

For kernels `n=(a,b,0,0)`, the hexagon plane is preserved and the square factor
projects to four parallel hexagon layers.  The actual square edges use the
height differences `a+b` and `a-b`, so they remain on the same Zome axis when
`a,b in Q(phi)`.

There are two zome hexagon frames with a perpendicular yellow height axis.
For the B/Y subfamily, the preserved hexagon is placed on two blue axes at
60 degrees.  The blue/yellow length ratio changes the snap condition from the
tesseract support-2 condition to

```text
q^2 = 3*(a^2+b^2),  q in Q(phi).
```

Example emitted above:

```text
a = 2 - phi,  b = -1 + 3 phi,
q = -3 + 6 phi = 3*sqrt(5),
q^2 = 3*(a^2+b^2) = 45.
```

For the G/Y subfamily, the preserved hexagon is placed on green axes and the
condition becomes

```text
2*q^2 = 3*(a^2+b^2),  q in Q(phi).
```

Examples emitted above:

```text
a = -1 + 2 phi,  b = 1,      q = 3
a = 2 + 3 phi,   b = 4+phi,  q = 6 + 3 phi
```

Both conics have `Q(phi)` points, so both have infinitely many `Q(phi)` points.
The finite rng sweep/probe therefore only found low-height representatives of a
larger infinite family.

## Provenance

- Sweep driver: `tools/run_prismatic_sweep.py --family B --rng 5`
- Infinite-family emitter: `python tools/emit_duoprism_inf_family.py`
- Construction: `lib/polytopes_prismatic.py` + `lib/uniform_polyhedra.py`
- See [`docs/PRISMATIC.md`](../../../docs/PRISMATIC.md) for the full prismatic-family taxonomy and sweep summary.

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/duoprisms/duoprism_4_6/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cell_first_cube.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cell_first_cube.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_6_inf_family_a5-3phi_b2-phi.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_6_inf_family_a5-3phi_b2-phi.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_6_inf_family_a5-3phi_b4phi-5.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_6_inf_family_a5-3phi_b4phi-5.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_6_inf_family_aphi_b5-2phi.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_6_inf_family_aphi_b5-2phi.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_6_inf_family_a2-phi_b3phi-1.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_6_inf_family_a2-phi_b3phi-1.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_6_inf_family_GY_a2phi-1_b1.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_6_inf_family_GY_a2phi-1_b1.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_6_inf_family_GY_a2+3phi_b4+phi.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_6_inf_family_GY_a2+3phi_b4+phi.vZome
 </figcaption>
</figure>
