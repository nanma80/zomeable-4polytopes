# 5-cell {3,3,3} — interactive 3D viewer

➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/regular/5cell/VIEWER.html)** to interact with the 4 models below.

For methodology, kernel directions, search subtleties, and reproduction commands, see [`RESULTS.md`](RESULTS.md) in the same folder.

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<style>
  .vzome-gallery {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
    margin: 2rem 0;
  }
  .vzome-card {
    box-sizing: border-box;
    border: 1px solid #ddd;
    border-radius: 0.5rem;
    padding: 0.25rem;
    background: #fff;
    max-width: min(100%, 72dvh);
    margin: 0 auto;
    width: 100%;
  }
  .vzome-card vzome-viewer {
    display: block;
    width: 100%;
    aspect-ratio: 1 / 1;
    height: auto;
  }
  .vzome-card figcaption {
    margin: 0.75rem 0 0.5rem;
    color: #555;
    text-align: center;
    font-style: italic;
  }
</style>

<div class="vzome-gallery">

<figure class="vzome-card">
 <vzome-viewer src="5cell_4ball_Y6B3.vZome" progress="true">
 </vzome-viewer>
 <figcaption>
    5cell_4ball_Y6B3.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="5cell_5ball_R6Y1B3.vZome" progress="true">
 </vzome-viewer>
 <figcaption>
    5cell_5ball_R6Y1B3.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="../5cell_hidden_cells/5cell_5ball_R6Y1B3_front_visible.vZome" progress="true">
 </vzome-viewer>
 <figcaption>
    5cell_5ball_R6Y1B3.vZome — hidden-cell-removal view
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="5cell_5ball_Y4B2R4.vZome" progress="true">
 </vzome-viewer>
 <figcaption>
    5cell_5ball_Y4B2R4.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="5cell_vertex_first_tet_plus_center.vZome" progress="true">
 </vzome-viewer>
 <figcaption>
    5cell_vertex_first_tet_plus_center.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="../5cell_hidden_cells/5cell_vertex_first_tet_plus_center_front_visible.vZome" progress="true">
 </vzome-viewer>
 <figcaption>
    5cell_vertex_first_tet_plus_center.vZome — hidden-cell-removal view
 </figcaption>
</figure>

</div>
