# runcitruncated 120-cell → zomeable orthographic projections

- Coxeter group: **H4**, Wythoff bitmask: **(1,1,0,1)**
- Vertices: **7212**, edges: **18060**
- Folder: `output/uniform/runcitruncated_120cell/`

**1 distinct zomeable shape** found (rng = 2 production sweep + rng = 4 inheritance-free audit):

| File | Label / direction | n_balls | fp_hash |
|------|-------------------|--------:|---------|
| `runcitruncated_120cell_cell_first_truncated_dodecahedron.vZome` | cell_first / truncated_dodecahedron | 3660 | `77bc10c853` |

Each `.vZome` document embeds the 4D polytope via a `<Polytope4d>` element under a specific kernel direction.  See [`docs/WYTHOFF_SWEEP.md`](../../docs/WYTHOFF_SWEEP.md) for the master taxonomy, the search methodology, and the per-shape strut counts (B/Y/R/G zometool axes).

## Provenance

- Production sweep: `tools/run_wythoff_sweep.py` (rng = 2).
- Inheritance-free audit: `tools/inheritance_free_sweep.py` (rng ∈ {2, 3, 4}); see [`docs/INHERITANCE_FREE_SWEEP.md`](../../docs/INHERITANCE_FREE_SWEEP.md).
- Manifest entry: `output/wythoff_sweep_manifest.json` (search `"source_polytope": "runcitruncated 120-cell"`).

## 3D Viewers

<!-- _3d-viewer-html-link_ -->
➡️ **[Open this page on GitHub Pages](https://nanma80.github.io/zomeable-4polytopes/output/uniform/runcitruncated_120cell/RESULTS.html)** to interact with the 3D models below (the embeds only render when this file is served via GitHub Pages, not in github.com's markdown preview).



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
 <vzome-viewer src="runcitruncated_120cell_cell_first_truncated_dodecahedron.vZome" progress="true" >
 </vzome-viewer>
 <figcaption>
    runcitruncated_120cell_cell_first_truncated_dodecahedron.vZome
 </figcaption>
</figure>

