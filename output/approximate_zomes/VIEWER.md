# Approximate Zome Polyhedra

**[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/approximate_zomes/VIEWER.html)** to interact with the 16 curated models below.

These are approximate RGBY zome models of 3D Platonic, Archimedean, and Catalan solid graphs. They are not part of the strict 4-polytope orthographic projection classification.

For context and generation notes, see [`docs/APPROXIMATE_ZOMES.md`](../../docs/APPROXIMATE_ZOMES.md).

<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>

<style>
.model-section {
  border: 1px solid #d0d7de;
  border-radius: 10px;
  margin: 1rem 0;
  overflow: hidden;
  scroll-margin-top: 0.5rem;
}
.section-toggle {
  align-items: center;
  background: #f6f8fa;
  border: 0;
  border-bottom: 1px solid #d0d7de;
  color: inherit;
  cursor: pointer;
  display: flex;
  font: inherit;
  gap: 0.6rem;
  padding: 0.85rem 1rem;
  text-align: left;
  width: 100%;
}
.section-toggle[aria-expanded="false"] {
  border-bottom: 0;
}
.section-toggle small {
  color: #57606a;
  display: block;
  font-size: 0.9rem;
  margin-top: 0.15rem;
}
.section-toggle[aria-expanded="true"] .chevron {
  transform: rotate(90deg);
}
.chevron {
  display: inline-block;
  transition: transform 0.15s ease;
}
.section-panel:empty {
  display: none;
}
.approx-model {
  margin: 1rem auto;
  max-width: 800px;
  padding: 0 1rem 1rem;
}
.approx-model vzome-viewer {
  display: block;
  height: min(500px, 70vh);
  width: 100%;
}
.approx-model figcaption {
  font-style: italic;
  text-align: center;
}
</style>

<section class="model-section" data-family="platonic">
  <button type="button" class="section-toggle" aria-expanded="false" aria-controls="platonic-panel">
    <span class="chevron" aria-hidden="true">▶</span>
    <span><strong>Platonic solids</strong> <small>(5 models: Tetrahedron, Cube, Octahedron, and 2 more)</small></span>
  </button>
  <div id="platonic-panel" class="section-panel" role="region" aria-label="Platonic solids"></div>
  <template id="platonic-template">
<figure class="approx-model">
 <vzome-viewer src="tetrahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Tetrahedron — B2 x 3, R2 x 3</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="cube_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Cube — B3 x 4, G2 x 8</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="octahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Octahedron — B2 x 6, R2 x 6</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="icosahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Icosahedron — B3 x 6, G2 x 24</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="dodecahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Dodecahedron — B3 x 6, G2 x 24</figcaption>
</figure>
  </template>
</section>

<section class="model-section" data-family="archimedean">
  <button type="button" class="section-toggle" aria-expanded="false" aria-controls="archimedean-panel">
    <span class="chevron" aria-hidden="true">▶</span>
    <span><strong>Archimedean solids</strong> <small>(6 models: Truncated tetrahedron, Cuboctahedron, Truncated octahedron, and 3 more)</small></span>
  </button>
  <div id="archimedean-panel" class="section-panel" role="region" aria-label="Archimedean solids"></div>
  <template id="archimedean-template">
<figure class="approx-model">
 <vzome-viewer src="truncated_tetrahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Truncated tetrahedron — B2 x 9, R2 x 9</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="cuboctahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Cuboctahedron — B2 x 12, R2 x 12</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="truncated_octahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Truncated octahedron — B2 x 18, R2 x 18</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="rhombicuboctahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Rhombicuboctahedron — B3 x 24, G2 x 24</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="icosidodecahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Icosidodecahedron — B3 x 12, G2 x 48</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="rhombicosidodecahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Rhombicosidodecahedron — B3 x 24, G2 x 96</figcaption>
</figure>
  </template>
</section>

<section class="model-section" data-family="catalan">
  <button type="button" class="section-toggle" aria-expanded="false" aria-controls="catalan-panel">
    <span class="chevron" aria-hidden="true">▶</span>
    <span><strong>Catalan solids</strong> <small>(5 models: Triakis tetrahedron, Rhombic dodecahedron, Rhombic triacontahedron, and 2 more)</small></span>
  </button>
  <div id="catalan-panel" class="section-panel" role="region" aria-label="Catalan solids"></div>
  <template id="catalan-template">
<figure class="approx-model">
 <vzome-viewer src="triakis_tetrahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Triakis tetrahedron — B2 x 3, B3 x 3, R2 x 3, Y2 x 6, Y3 x 3</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="rhombic_dodecahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Rhombic dodecahedron — G2 x 18, Y3 x 6</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="rhombic_triacontahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Rhombic triacontahedron — G2 x 60</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="triakis_icosahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Triakis icosahedron — B3 x 30, R2 x 60</figcaption>
</figure>
<figure class="approx-model">
 <vzome-viewer src="pentakis_dodecahedron_favorite.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>Pentakis dodecahedron — B3 x 30, G2 x 60</figcaption>
</figure>
  </template>
</section>


<script>
const sections = Array.from(document.querySelectorAll(".model-section"));

function expandSection(family, shouldScroll = true) {
  let activeSection = null;
  sections.forEach((section) => {
    const isActive = section.dataset.family === family;
    const button = section.querySelector(".section-toggle");
    const panel = section.querySelector(".section-panel");
    button.setAttribute("aria-expanded", String(isActive));
    if (isActive) {
      activeSection = section;
      const template = section.querySelector("template");
      if (!panel.childElementCount) {
        panel.appendChild(template.content.cloneNode(true));
      }
    } else {
      panel.replaceChildren();
    }
  });
  if (shouldScroll && activeSection) {
    activeSection.scrollIntoView({ block: "start", behavior: "smooth" });
  }
}

sections.forEach((section) => {
  section.querySelector(".section-toggle").addEventListener("click", () => {
    expandSection(section.dataset.family);
  });
});

expandSection("platonic", false);
</script>

## References and acknowledgements

Some of these approximation ideas are related to earlier Zometool constructions shared in the following sources:

- Reza Sarhangi, "An Art and Technology Approach to Actively Engage Students in
  the Mathematics of the Regular Polyhedra," *Mathematics Education Trends and
  Research*, 2014, doi:10.5899/2014/metr-00060. In particular, Sarhangi shows
  Zome approximations for the tetrahedron and octahedron.
- Tick Wang, [Facebook reel](https://www.facebook.com/reel/3394895470670317),
  showing related Zome polyhedron approximation constructions.

The models here are a curated computational gallery in the same spirit: standard RGBY zome strut graphs chosen to approximate ideal Platonic, Archimedean, and Catalan targets visually and metrically.
