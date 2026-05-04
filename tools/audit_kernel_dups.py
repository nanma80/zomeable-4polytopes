"""Audit: which polytopes have manifest entries that are scalar-multiples of each other?

This identifies the spurious duplicates produced by shape_fingerprint's SVD-basis
ambiguity bug.  Two kernels that are positive scalar multiples of each other
(parallel, same sign) produce identical 3D projections by definition, but the
fingerprint function returns slightly different hashes due to numerical noise.
"""
import json, numpy as np
from collections import defaultdict
from numpy.linalg import norm

with open('output/wythoff_sweep/manifest.json') as f:
    m = json.load(f)

poly_groups = defaultdict(list)
for s in m['shapes']:
    if s['status'] == 'ok':
        poly_groups[(s['group'], tuple(s['bitmask']))].append(s)

print(f'{"polytope":<35} {"#shapes":>7} {"#dirs":>6} {"#dups":>5}')
print('-' * 60)
total_count = 0
total_dirs = 0
for (g, bm), shapes in sorted(poly_groups.items()):
    name = shapes[0]['source_polytope']
    if len(shapes) <= 1:
        total_count += len(shapes)
        total_dirs += len(shapes)
        continue
    K = np.asarray([s['kernel'] for s in shapes], dtype=float)
    Ku = K / norm(K, axis=1, keepdims=True)
    seen = np.zeros(len(K), dtype=bool)
    dirs = 0
    for i in range(len(K)):
        if seen[i]:
            continue
        sim = np.where((Ku @ Ku[i]) > 1 - 1e-6)[0]
        seen[sim] = True
        dirs += 1
    total_count += len(shapes)
    total_dirs += dirs
    flag = '  *' if dirs < len(shapes) else ''
    print(f'{name:<35} {len(shapes):>7} {dirs:>6} {len(shapes)-dirs:>5}{flag}')

print('-' * 60)
print(f'{"TOTAL":<35} {total_count:>7} {total_dirs:>6} {total_count-total_dirs:>5}')
