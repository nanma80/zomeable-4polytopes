# dodecahedron prism → zomeable orthographic projections

- Family **A** (polyhedral prism)
- 4D vertices: **40**, edges: **80**
- Folder: `output/polyhedral_prisms/dodecahedron_prism/`

**5 distinct zomeable shapes** found (rng = 2 agnostic kernel sweep).

## Shapes

| # | File | Label / direction | n_balls | Struts |
|---|------|-------------------|--------:|--------|
| 1 | `cell_first_dodecahedron.vZome` | cell_first / dodecahedron | 20 | B:30 |
| 2 | `oblique_00.vZome` | oblique | 40 | B:12  R:24  Y:44 |
| 3 | `oblique_01.vZome` | oblique | 40 | B:20  R:40  Y:20 |
| 4 | `face_first_square.vZome` | face_first / square | 24 | B:18  R:16  Y:8 |
| 5 | `oblique_02.vZome` | oblique | 40 | B:20  R:40  Y:20 |

## Provenance

- Sweep driver: `tools/run_prismatic_sweep.py --family A --rng 2`
- Construction: `lib/polytopes_prismatic.py` + `lib/uniform_polyhedra.py`
- See [`docs/PRISMATIC.md`](../../../docs/PRISMATIC.md) for the full prismatic-family taxonomy and sweep summary.

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/polyhedral_prisms/dodecahedron_prism/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="cell_first_dodecahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    cell_first_dodecahedron.vZome
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
 <vzome-viewer style="width: 100%; height: 500px" src="oblique_01.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    oblique_01.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="face_first_square.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    face_first_square.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="oblique_02.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    oblique_02.vZome
 </figcaption>
</figure>

