# snub 24-cell — interactive 3D viewer

➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/uniform/snub_24cell/VIEWER.html)** to interact with the 2 models below.

For methodology, kernel directions, search subtleties, and reproduction commands, see [`RESULTS.md`](RESULTS.md) in the same folder.

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>


<style>
  .vzome-card {
    box-sizing: border-box;
    border: 1px solid #ddd;
    border-radius: 0.5rem;
    padding: 0.25rem;
    background: #fff;
    max-width: min(100%, 72dvh);
    margin: 2rem auto;
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

<figure class="vzome-card">
 <vzome-viewer src="snub_24cell_cell_first.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    snub_24cell_cell_first.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="snub_24cell_vertex_first.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    snub_24cell_vertex_first.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="../snub_24cell_hidden_cells/snub_24cell_vertex_first_front_visible.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    snub_24cell_vertex_first.vZome — hidden-cell-removal view
 </figcaption>
</figure>
