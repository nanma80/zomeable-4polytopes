# Approximate zome scripts

These scripts generated the approximate Platonic and Archimedean zome gallery in
`output/approximate_zomes/`.

- `approx_platonic_zomes.py` builds and scores approximate RGBY strut graph
  embeddings for Platonic and nonprismatic Archimedean targets.
- `run_archimedean_batch.py` runs the non-snub Archimedean search batch with
  progress JSON/logging.
- `postprocess_favorites.py` records the curation step used to select, scale,
  center, and emit the favorite models. It expects the original scratch output
  folders from the search session; the committed final results are already in
  `output/approximate_zomes/`.

This collection is intentionally not part of the strict orthographic projection
classification used by the main catalogue.
