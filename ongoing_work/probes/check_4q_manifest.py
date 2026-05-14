"""Quick: list duoprism_4_q (and tesseract) shape counts."""
import json
m = json.load(open('output/prismatic_manifest.json'))
for entry in m['polytopes']:
    s = entry['slug']
    if s.startswith('duoprism_4_'):
        print(f"{s:30s} nV={entry['nV']:4d} n_shapes={entry['n_shapes']}")
