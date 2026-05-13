# icosidodecahedron prism → zomeable orthographic projections

- Family **A** (polyhedral prism)
- 4D vertices: **60**, edges: **150**
- Folder: `output/polyhedral_prisms/icosidodecahedron_prism/`

**5 distinct zomeable shapes** found (rng = 3 agnostic kernel sweep).

## Shapes

| # | File | Label / direction | n_balls | Struts |
|---|------|-------------------|--------:|--------|
| 1 | `edge_first.vZome` | edge_first | 34 | B:25  R:32  Y:16 |
| 2 | `oblique_00.vZome` | oblique | 60 | B:40  R:70  Y:40 |
| 3 | `oblique_02.vZome` | oblique | 60 | B:40  R:70  Y:40 |
| 4 | `oblique_01.vZome` | oblique | 60 | B:24  R:48  Y:78 |
| 5 | `cell_first_icosidodecahedron.vZome` | cell_first / icosidodecahedron | 30 | B:60 |

## Provenance

- Sweep driver: `tools/run_prismatic_sweep.py --family A --rng 3`
- Construction: `lib/polytopes_prismatic.py` + `lib/uniform_polyhedra.py`
- See [`docs/PRISMATIC.md`](../../../docs/PRISMATIC.md) for the full prismatic-family taxonomy and sweep summary.

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/polyhedral_prisms/icosidodecahedron_prism/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="edge_first.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    edge_first.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="oblique_00.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    oblique_00.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="oblique_02.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    oblique_02.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="oblique_01.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    oblique_01.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cell_first_icosidodecahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cell_first_icosidodecahedron.vZome
 </figcaption>
</figure>

