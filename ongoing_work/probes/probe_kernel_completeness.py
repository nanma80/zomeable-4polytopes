"""Kernel-completeness audit at rng=2.

For each Wythoff descendant, run a full rng=2 kernel search (no
regular-only seed restriction) and compare to the production pipeline's
shape count.  If a descendant has more shapes under full-search than
under the (1,0,0,0)-seeded pipeline, the production sweep is missing
those shapes.

This is the script that produced the 'B4 has gaps on every descendant,
A4/F4/H4 have no gap' result documented in WYTHOFF_SWEEP.md.
"""
import sys, time
sys.path.insert(0, 'lib')
from wythoff import build_polytope
from search_engine import gen_dirs, search, group_by_shape

print('Generating rng=2 candidate kernel directions...', flush=True)
dirs2 = list(gen_dirs(rng=2, integer_only=False, permute_dedup=False))
print(f'rng=2 candidate kernel directions: {len(dirs2)}', flush=True)

# (group, bitmask, descendant name, pipeline_count_from_manifest)
cases = [
    # B4 descendants:
    ('B4', (0, 0, 0, 1), '16-cell',                3),
    ('B4', (0, 1, 0, 0), 'rectified tesseract',    3),
    ('B4', (0, 0, 1, 0), '24-cell (B4)',           2),
    ('B4', (0, 0, 1, 1), 'truncated 16-cell',      3),
    ('B4', (0, 1, 0, 1), 'cantellated 16-cell',    2),
    ('B4', (0, 1, 1, 1), 'cantitruncated 16-cell', 2),
    # H4 600-cell as a sanity check
    ('H4', (0, 0, 0, 1), '600-cell',               1),
    # H4 next-largest cases (slow):
    # ('H4', (0, 0, 1, 0), 'rectified 600-cell',   1),
    # ('H4', (0, 1, 0, 0), 'rectified 120-cell',   1),
    # ('H4', (0, 0, 1, 1), 'truncated 600-cell',   1),
    # ('H4', (0, 1, 1, 0), 'cantellated 600-cell', 1),
]

print()
print(f"{'group':5s} {'bm':12s} {'name':28s} {'pipeline':>9s} {'full_rng2':>10s} {'gap':>5s}")
print('=' * 80)
for g, bm, nm, pipeline_cnt in cases:
    V, E = build_polytope(g, bm)
    hits = search(nm, V, E, dirs2, verbose=False)
    groups = group_by_shape(hits, V, E)
    full_cnt = len(groups)
    gap = full_cnt - pipeline_cnt
    flag = '  <-- MISSED' if gap > 0 else ''
    print(f'{g:5s} {str(bm):12s} {nm:28s} {pipeline_cnt:9d} {full_cnt:10d} {gap:5d}{flag}', flush=True)
