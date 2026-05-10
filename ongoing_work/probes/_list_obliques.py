"""List all 'oblique'-classified entries in the wythoff_sweep manifest."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
m = json.loads((ROOT / 'output' / 'wythoff_sweep' / 'manifest.json').read_text())
shapes = [s for s in m['shapes'] if s.get('status') == 'ok']

by_poly = defaultdict(list)
for s in shapes:
    sp = s.get('source_polytope', '?')
    by_poly[sp].append({
        'label': s.get('label'),
        'kernel': s.get('kernel'),
        'file': s.get('file'),
    })

# Determine parent group from the 'group' field in manifest
poly_to_group = {}
for s in shapes:
    poly_to_group[s.get('source_polytope', '?')] = s.get('group', '?')

print('Oblique entries by parent group:')
print()
for grp in ['A4', 'B4', 'F4', 'H4']:
    print(f'=== {grp} ===')
    n = 0
    for p in sorted(poly_to_group):
        if poly_to_group[p] != grp:
            continue
        obs = [s for s in by_poly[p] if s['label'] == 'oblique']
        if not obs:
            continue
        n += len(obs)
        print(f'  {p}: {len(obs)} oblique')
        for o in obs:
            k = o['kernel']
            f = o['file']
            print(f'    kernel={k}')
            print(f'        file={f}')
    print(f'  total {grp} oblique: {n}')
    print()
