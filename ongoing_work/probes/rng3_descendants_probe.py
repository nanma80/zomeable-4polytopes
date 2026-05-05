"""rng=3 probe on small/fast cases that the first probe didn't reach.

Focused on A4 descendants (small) and a few B4/F4 small descendants where
rng=3 might surface new shapes.  Skip 600-cell and 120-cell - the rng=2
search already returned 1, and high symmetry makes rng=3 unlikely to differ.
"""
import sys, time, json, os
sys.path.insert(0, 'lib')
from wythoff import build_polytope
from search_engine import gen_dirs, search, group_by_shape

print('Generating rng=3 candidate kernel directions...', flush=True)
t0 = time.time()
dirs3 = list(gen_dirs(rng=3, integer_only=False, permute_dedup=False))
print(f'rng=3: {len(dirs3)} directions ({time.time()-t0:.1f}s)', flush=True)

# rng=2 baselines from earlier full-search probe
rng2_full = {
    ('A4', (1,1,0,0)): None,   ('A4', (1,0,0,1)): None,
    ('A4', (1,1,1,0)): None,   ('A4', (1,1,0,1)): None,
    ('A4', (1,1,1,1)): None,
    ('B4', (0,1,0,0)): 7,
    ('B4', (0,0,1,1)): 7,
    ('B4', (0,1,0,1)): 5,
    ('B4', (0,1,1,1)): 6,
    ('B4', (0,0,1,0)): 3,
    ('F4', (0,1,0,0)): 5,
    ('F4', (0,1,1,0)): 1,
}

cases = [
    # Small A4 descendants - all should be quick
    ('A4', (1,1,0,0), 'truncated 5-cell'),
    ('A4', (1,0,0,1), 'runcinated 5-cell'),
    ('A4', (1,1,1,0), 'cantellated 5-cell'),
    ('A4', (1,1,0,1), 'runcitruncated 5-cell'),
    ('A4', (1,1,1,1), 'omnitruncated 5-cell'),
    # Small B4 descendants
    ('B4', (0,1,0,0), 'rectified tesseract'),
    ('B4', (0,0,1,0), '24-cell-as-B4'),
    ('B4', (0,1,0,1), 'cantellated 16-cell'),
    ('B4', (0,1,1,1), 'cantitruncated 16-cell'),
    ('B4', (0,0,1,1), 'truncated 16-cell'),
    # Small F4 descendants
    ('F4', (0,1,0,0), 'rectified 24-cell'),
    ('F4', (0,1,1,0), 'bitruncated 24-cell'),
]

results = []
print()
print(f"{'group':5s} {'bm':12s} {'name':24s} {'V':>4s} {'E':>5s} {'rng2_full':>10s} {'rng3':>6s} {'time(s)':>8s}")
print('=' * 86)
for g, bm, nm in cases:
    V, E = build_polytope(g, bm)
    t0 = time.time()
    hits = search(nm, V, E, dirs3, verbose=False)
    groups = group_by_shape(hits, V, E)
    elapsed = time.time() - t0
    rng3_count = len(groups)
    r2 = rng2_full.get((g, bm))
    delta = ''
    if isinstance(r2, int) and rng3_count > r2:
        delta = f'  +{rng3_count - r2} new!'
    elif isinstance(r2, int):
        delta = '  match'
    print(f'{g:5s} {str(bm):12s} {nm:24s} {len(V):4d} {len(E):5d} {str(r2):>10s} {rng3_count:6d} {elapsed:8.1f}{delta}', flush=True)
    results.append({
        'group': g, 'bitmask': list(bm), 'name': nm,
        'V': len(V), 'E': len(E),
        'rng2_full': r2,
        'rng3': rng3_count,
        'time_seconds': elapsed,
    })

with open('ongoing_work/rng3_descendants.json', 'w') as f:
    json.dump(results, f, indent=2)
print()
print('Saved ongoing_work/rng3_descendants.json')
