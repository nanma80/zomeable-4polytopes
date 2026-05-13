# {10}×{10} duoprism → zomeable orthographic projections

- Family **B** (duoprism)
- 4D vertices: **100**, edges: **200**
- Folder: `output/duoprisms/duoprism_10_10/`

**2 distinct zomeable shapes** found (rng = 3 agnostic kernel sweep).

## Shapes

| # | File | Label / direction | n_balls | Struts |
|---|------|-------------------|--------:|--------|
| 1 | `oblique_04.vZome` | oblique | 96 | B:38  R:80  Y:80 |
| 2 | `face_first_decagon_04.vZome` | face_first / decagon | 50 | B:50  R:40 |

## Provenance

- Sweep driver: `tools/run_prismatic_sweep.py --family B --rng 3`
- Construction: `lib/polytopes_prismatic.py` + `lib/uniform_polyhedra.py`
- See [`docs/PRISMATIC.md`](../../../docs/PRISMATIC.md) for the full prismatic-family taxonomy and sweep summary.

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/duoprisms/duoprism_10_10/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="oblique_04.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    oblique_04.vZome
 </figcaption>
</figure>

<figure style="width: 800px; margin: 5%">
 <vzome-viewer style="width: 100%; height: 500px" src="face_first_decagon_04.vZome" progress="true" >
 </vzome-viewer>
 <figcaption style="text-align: center; font-style: italic;">
    face_first_decagon_04.vZome
 </figcaption>
</figure>

