"""Focused rng=3 snap test on cantitruncated 5-cell only.

cantitruncated 5-cell at rng=2 raw fp = 7 (manifest = 4 files).  At
rng=3 we found 10 raw fingerprints in the descendants probe.  This
script re-runs the rng=3 search and tries to snap each of the 10 to
Z[phi]^3.  Outputs counts of snap successes vs failures.

Run time: ~12 min (rng=3 search on V=60 E=120) + few seconds per snap.
"""
import sys, os, time, json
sys.path.insert(0, 'lib')
from wythoff import build_polytope
from search_engine import gen_dirs, search, group_by_shape
from emit_generic import project_and_emit

print('Generating rng=3 directions...', flush=True)
t0 = time.time()
dirs3 = list(gen_dirs(rng=3, integer_only=False, permute_dedup=False))
print(f'rng=3: {len(dirs3)} dirs ({time.time()-t0:.1f}s)', flush=True)

OUT = os.path.join('ongoing_work', 'rng3_snaptest')
os.makedirs(OUT, exist_ok=True)

cases = [
    ('A4', (1, 1, 1, 0), 'cantitruncated_5cell',  4, 7),
    ('A4', (1, 1, 0, 1), 'runcitruncated_5cell',  4, 6),
    ('A4', (1, 1, 1, 1), 'omnitruncated_5cell',   4, 10),
    ('B4', (0, 1, 0, 1), 'cantellated_16cell',    3, 5),
]

summary = []
for group, bm, slug, files_rng2, raw_rng2 in cases:
    print(f"\n=== {group} {bm} {slug} ===", flush=True)
    V, E = build_polytope(group, bm)
    print(f"V={len(V)} E={len(E)}, searching at rng=3...", flush=True)
    t0 = time.time()
    hits = search(slug, V, E, dirs3, verbose=False)
    groups = group_by_shape(hits, V, E)
    elapsed = time.time() - t0
    print(f"rng=3 raw fp = {len(groups)}, took {elapsed:.1f}s", flush=True)

    snapped, failed = [], []
    for fp_idx, (fp, examples) in enumerate(groups.items()):
        n0, sig0, balls0 = examples[0]
        n_list = list(map(float, n0))
        out_path = os.path.join(OUT, f'{slug}__{fp_idx:02d}.vZome')
        try:
            project_and_emit(slug, V, E, n_list, out_path, verbose=False)
            snapped.append({'idx': fp_idx, 'kernel': n_list,
                            'n_balls': int(fp[0])})
            print(f"  fp{fp_idx:02d} balls={fp[0]:>4d}  -> SNAP OK", flush=True)
        except Exception as exc:
            failed.append({'idx': fp_idx, 'kernel': n_list,
                           'n_balls': int(fp[0]), 'reason': str(exc)[:120]})
            print(f"  fp{fp_idx:02d} balls={fp[0]:>4d}  -> FAIL "
                  f"({type(exc).__name__})", flush=True)
    summary.append({
        'group': group, 'bitmask': list(bm), 'name': slug,
        'V': len(V), 'E': len(E),
        'rng2_raw': raw_rng2,
        'rng2_files_in_corpus': files_rng2,
        'rng3_raw_fp': len(groups),
        'rng3_snapped': len(snapped),
        'rng3_failed': len(failed),
        'snapped': snapped,
        'failed': failed,
    })

print()
print(f"{'name':25s} {'V':>4s} {'E':>5s} {'rng2_corpus':>11s} {'rng3_raw':>8s} {'rng3_snap':>9s} {'rng3_fail':>9s}")
print('=' * 80)
for s in summary:
    print(f"{s['name']:25s} {s['V']:4d} {s['E']:5d} "
          f"{s['rng2_files_in_corpus']:11d} {s['rng3_raw_fp']:8d} "
          f"{s['rng3_snapped']:9d} {s['rng3_failed']:9d}")

with open(os.path.join('ongoing_work', 'rng3_snaptest_summary.json'), 'w') as f:
    json.dump(summary, f, indent=2)
print()
print('Saved ongoing_work/rng3_snaptest_summary.json')
