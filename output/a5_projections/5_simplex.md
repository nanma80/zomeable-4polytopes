# 5-simplex - interactive 3D viewer

**[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/a5_projections/5_simplex.html)** to interact with these models.

[Back to A5 projections index](VIEWER.md).

Strict orthographic zomeable projections of 5-simplex (A5 family). Each edge points along a default zometool axis (Blue/Yellow/Red/Green).

In the captions, "balls" means distinct 3D ball positions in the vZome model after projection.

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
 <vzome-viewer src="5_simplex/5_simplex_sym48_6balls_2be46b.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    5-simplex - octahedral symmetry (order 48), 6 balls (projects onto a regular octahedron; buildable: B(x2)+G)
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="5_simplex/5_simplex_sym24_5balls_30531f.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    5-simplex - order-24 symmetry, 5 balls (buildable: G+Y)
 </figcaption>
</figure>

<figure class="vzome-card">
 <vzome-viewer src="5_simplex/5_simplex_sym6_5balls_667fed.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    5-simplex - order-6 symmetry, 5 balls (direction-zomeable only)
 </figcaption>
</figure>
