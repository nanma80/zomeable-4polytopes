# {4}×{10} duoprism → zomeable orthographic projections

- Family **B** (duoprism)
- 4D vertices: **40**, edges: **80**
- Folder: `output/duoprisms/duoprism_4_10/`

The zomeable set is best summarized as **1 cell-first projection + an inf
family**.  The finite rng = 4 agnostic kernel sweep found the cell-first model
plus five sample members of that family; two additional constructive
representatives are emitted here.

## Shapes

| # | File | Label / direction | n_balls | Struts |
|---|------|-------------------|--------:|--------|
| 1 | `cell_first_cube.vZome` | cell_first / cube | 24 | B:20  G:24 |
| 2 | `duoprism_4_10_inf_family_a2phi-3_b2-phi.vZome` | inf family representative | 40 | B:40  R:40 |
| 3 | `duoprism_4_10_inf_family_aphi_b4phi-1.vZome` | inf family representative | 40 | B:40  R:40 |
| 4 | `duoprism_4_10_inf_family_a4phi-3_b4+3phi.vZome` | inf family representative | 40 | B:40  R:40 |
| 5 | `duoprism_4_10_inf_family_a2phi-3_b1+phi.vZome` | inf family representative | 40 | B:40  R:40 |
| 6 | `duoprism_4_10_inf_family_aphi-1_b3+4phi.vZome` | inf family representative | 40 | B:40  R:40 |
| 7 | `duoprism_4_10_inf_family_a5_b12.vZome` | inf family representative | 40 | B:40  R:40 |
| 8 | `duoprism_4_10_inf_family_a8_b15.vZome` | inf family representative | 40 | B:40  R:40 |

## Inf family

For kernels `n=(a,b,0,0)`, the decagon plane is preserved and the square factor
projects to four parallel decagon layers.  The square edges again use the
height differences `a+b` and `a-b`, so they remain on the same Zome axis when
`a,b in Q(phi)`.

The preserved decagon can be placed in a blue-axis plane perpendicular to a red
axis.  Because the blue/red length ratio is `2/sqrt(5) in Q(phi)`, the
tesseract support-2 arithmetic condition transfers directly:

```text
c^2 = a^2+b^2,  c in Q(phi).
```

The emitted examples use ordinary Pythagorean triples:

```text
(a,b,c) = (5,12,13)
(a,b,c) = (8,15,17)
```

The full `Q(phi)` Pythagorean conic supplies infinitely many projective ratios,
so `{4}x{10}` has an infinite zomeable orthographic family.

## Provenance

- Sweep driver: `tools/run_prismatic_sweep.py --family B --rng 4`
- Infinite-family emitter: `python tools/emit_duoprism_inf_family.py`
- Construction: `lib/polytopes_prismatic.py` + `lib/uniform_polyhedra.py`
- See [`docs/PRISMATIC.md`](../../../docs/PRISMATIC.md) for the full prismatic-family taxonomy and sweep summary.

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/duoprisms/duoprism_4_10/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cell_first_cube.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cell_first_cube.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_10_inf_family_a2phi-3_b2-phi.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_10_inf_family_a2phi-3_b2-phi.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_10_inf_family_aphi_b4phi-1.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_10_inf_family_aphi_b4phi-1.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_10_inf_family_a4phi-3_b4+3phi.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_10_inf_family_a4phi-3_b4+3phi.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_10_inf_family_a2phi-3_b1+phi.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_10_inf_family_a2phi-3_b1+phi.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_10_inf_family_aphi-1_b3+4phi.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_10_inf_family_aphi-1_b3+4phi.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_10_inf_family_a5_b12.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_10_inf_family_a5_b12.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="duoprism_4_10_inf_family_a8_b15.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    duoprism_4_10_inf_family_a8_b15.vZome
 </figcaption>
</figure>
