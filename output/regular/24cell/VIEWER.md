# 24-cell {3,4,3} — interactive 3D viewer

➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/regular/24cell/VIEWER.html)** to interact with the 3 models below.

For methodology, kernel directions, search subtleties, and reproduction commands, see [`ZOMEABLE_PROJECTIONS.md`](ZOMEABLE_PROJECTIONS.md) in the same folder.

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
 <vzome-viewer src="24cell_long_root_rhombic_dodecahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    24cell_long_root_rhombic_dodecahedron.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="24cell_short_root_cuboctahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    24cell_short_root_cuboctahedron.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="24cell_triality.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    24cell_triality.vZome
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="../24cell_hidden_cells/24cell_triality_front_visible.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    24cell_triality.vZome — hidden-cell-removal view
 </figcaption>
</figure>
