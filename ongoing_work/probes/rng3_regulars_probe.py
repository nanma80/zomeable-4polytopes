"""rng=3 probe on regulars and small descendants.

Compare shape count at rng=3 (full direct search) vs the rng=2 baseline.
If rng=3 finds new shapes, those are candidates for new zomeable .vZome files.
"""
import sys, time, json
sys.path.insert(0, 'lib')
from wythoff import build_polytope
from search_engine import gen_dirs, search, group_by_shape

print('Generating rng=3 candidate kernel directions...', flush=True)
t0 = time.time()
dirs3 = list(gen_dirs(rng=3, integer_only=False, permute_dedup=False))
print(f'rng=3: {len(dirs3)} directions ({time.time()-t0:.1f}s)', flush=True)

# Master baseline counts
master = {
    '5-cell': 4, 'tesseract': 9, '16-cell': 6, '24-cell': 3,
    '120-cell': 1, '600-cell': 1,
}

# rng=2 full-search baselines (from earlier probe)
rng2_full = {
    ('A4', (1,0,0,0), '5-cell'):              4,
    ('A4', (0,1,0,0), 'rectified 5-cell'):    4,
    ('B4', (1,0,0,0), 'tesseract'):          32,
    ('B4', (0,0,0,1), '16-cell'):             6,
    ('F4', (1,0,0,0), '24-cell'):             3,  # F4 self-dual
    ('H4', (1,0,0,0), '120-cell'):            1,
    ('H4', (0,0,0,1), '600-cell'):            1,
}

cases = [
    ('A4', (1,0,0,0), '5-cell'),
    ('A4', (0,1,0,0), 'rectified 5-cell'),
    ('B4', (1,0,0,0), 'tesseract'),
    ('B4', (0,0,0,1), '16-cell'),
    ('F4', (1,0,0,0), '24-cell'),
    ('H4', (0,0,0,1), '600-cell'),
    ('H4', (1,0,0,0), '120-cell'),
]

results = []
print()
print(f"{'group':5s} {'bm':12s} {'name':20s} {'V':>4s} {'E':>5s} {'rng2_full':>10s} {'rng3':>6s} {'master':>7s} {'time(s)':>8s}")
print('=' * 90)
for g, bm, nm in cases:
    V, E = build_polytope(g, bm)
    t0 = time.time()
    hits = search(nm, V, E, dirs3, verbose=False)
    groups = group_by_shape(hits, V, E)
    elapsed = time.time() - t0
    rng3_count = len(groups)
    r2 = rng2_full.get((g, bm, nm), '?')
    m = master.get(nm, '?')
    delta = ''
    if isinstance(r2, int) and rng3_count > r2:
        delta = f'  +{rng3_count - r2} new!'
    print(f'{g:5s} {str(bm):12s} {nm:20s} {len(V):4d} {len(E):5d} {str(r2):>10s} {rng3_count:6d} {str(m):>7s} {elapsed:8.1f}{delta}', flush=True)
    results.append({
        'group': g, 'bitmask': list(bm), 'name': nm,
        'V': len(V), 'E': len(E),
        'rng2_full': r2 if isinstance(r2, int) else None,
        'rng3': rng3_count,
        'master': m if isinstance(m, int) else None,
        'time_seconds': elapsed,
        'shape_data': [{'fp_hash': fp, 'count': len(ks)} for fp, ks in groups.items()],
    })

with open('ongoing_work/rng3_probe.json', 'w') as f:
    json.dump(results, f, indent=2)
print()
print('Saved rng3_probe.json')
