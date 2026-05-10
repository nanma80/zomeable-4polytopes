"""Catalog and triage the 65 omnitruncated 120-cell rng=2 fingerprints."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
data = json.loads((ROOT / 'ongoing_work' / 'shapes_rng2_H4_1111.jsonl').read_text())
shapes = data['shapes']
print(f'group={data["group"]} bitmask={data["bitmask"]} name={data["name"]}')
print(f'V={data["V"]}  E={data["E"]}')
print(f'n_kernels_tested={data["n_kernels_tested"]}  n_hits={data["n_hits"]}  '
      f'n_distinct_shapes={len(shapes)}')
print()

# Categorise by n_balls
nb = Counter(s['n_balls'] for s in shapes)
print('n_balls distribution:')
for k, v in sorted(nb.items()):
    print(f'  V_proj={k:>5}: {v} shape(s)')
print()

# Per-shape strut sig
print('Each fingerprint (B/Y/R counts and "_" = collapsed-edge count):')
print(f'{"#":>3} {"V_proj":>6} {"n_ker":>6}  {"B":>6} {"Y":>6} {"R":>6} {"_":>6}  fp_hash')
clean_count = 0
for i, s in enumerate(shapes):
    sig = s['example_sig']
    collapsed = sig.get('_', 0)
    marker = '  <-- 0 collapsed' if collapsed == 0 else ''
    if collapsed == 0:
        clean_count += 1
    print(f'{i:>3} {s["n_balls"]:>6} {s["n_kernels"]:>6}  '
          f'{sig.get("B",0):>6} {sig.get("Y",0):>6} {sig.get("R",0):>6} '
          f'{collapsed:>6}{marker}')
print()
print(f'Shapes with 0 collapsed edges (clean snap candidates): {clean_count}/{len(shapes)}')
