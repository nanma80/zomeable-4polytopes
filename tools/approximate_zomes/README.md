# Approximate zome scripts

These scripts generated the approximate Platonic, Archimedean, and Catalan zome
gallery in `output/approximate_zomes/`.

- `approx_platonic_zomes.py` builds and scores approximate RGBY strut graph
  embeddings for Platonic, nonprismatic Archimedean, and Catalan targets.
- `run_archimedean_batch.py` runs the non-snub Archimedean search batch with
  progress JSON/logging.
- `run_catalan_batch.py` runs the strict one-strut Catalan search batch with
  progress JSON/logging.
- `postprocess_favorites.py` records the curation step used to select, scale,
  center, and emit the Platonic and Archimedean favorite models.
- `postprocess_catalan_favorites.py` records the same curation step for the
  Catalan favorites. The postprocessors expect the original scratch output
  folders from the search session; the committed final results are already in
  `output/approximate_zomes/`.

This collection is intentionally not part of the strict orthographic projection
classification used by the main catalogue.
