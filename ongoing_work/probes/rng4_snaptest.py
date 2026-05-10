"""rng=4 snap+dedup test on the smallest regulars.

Tests whether the rng=2 corpus is also stable under rng=4 for cases
where rng=4 search is feasible.  Tesseract is included for its known
infinite cuboid family (CLASSIFICATION.md predicts ~280 shapes at
rng=4).  The other regulars are expected to match master.
"""
import sys, os, time, json
sys.path.insert(0, 'lib')
sys.path.insert(0, 'tools')
from wythoff import build_polytope
from search_engine import gen_dirs, search, group_by_shape
from emit_generic import project_and_emit
from dedup_corpus_by_shape import parse_vzome, shape_signature

print('Generating rng=4 directions...', flush=True)
t0 = time.time()
dirs4 = list(gen_dirs(rng=4, integer_only=False, permute_dedup=False))
print(f'rng=4: {len(dirs4)} dirs ({time.time()-t0:.1f}s)', flush=True)

OUT = os.path.join('ongoing_work', 'rng4_snaptest')
os.makedirs(OUT, exist_ok=True)

cases = [
    # (group, bm, slug, master_files)
    ('A4', (1, 0, 0, 0), '5cell',     4),
    ('B4', (0, 0, 0, 1), '16cell',    6),
    ('F4', (1, 0, 0, 0), '24cell',    3),
    ('B4', (1, 0, 0, 0), 'tesseract', 9),
]

summary = []
for group, bm, slug, master in cases:
    print(f"\n=== {group} {bm} {slug} (master = {master}) ===", flush=True)
    V, E = build_polytope(group, bm)
    print(f"V={len(V)} E={len(E)}, searching at rng=4...", flush=True)
    t0 = time.time()
    hits = search(slug, V, E, dirs4, verbose=False)
    groups = group_by_shape(hits, V, E)
    elapsed = time.time() - t0
    print(f"rng=4 raw fp = {len(groups)}, took {elapsed:.1f}s", flush=True)

    snapped, failed = [], []
    out_files = []
    for fp_idx, (fp, examples) in enumerate(groups.items()):
        n0, sig0, balls0 = examples[0]
        n_list = list(map(float, n0))
        out_path = os.path.join(OUT, f'{slug}__{fp_idx:03d}.vZome')
        try:
            project_and_emit(slug, V, E, n_list, out_path, verbose=False)
            snapped.append({'idx': fp_idx, 'kernel': n_list,
                            'n_balls': int(fp[0])})
            out_files.append(out_path)
        except Exception as exc:
            failed.append({'idx': fp_idx, 'kernel': n_list,
                           'n_balls': int(fp[0]),
                           'reason': str(exc)[:120]})
    print(f"  snap: {len(snapped)}/{len(groups)} pass", flush=True)

    # Stage B dedup on the rng=4 snapped files
    sig_groups = {}
    for vz in out_files:
        try:
            P, E_loaded = parse_vzome(__import__('pathlib').Path(vz))
            sig = shape_signature(P, E_loaded)
            sig_groups.setdefault(sig, []).append(vz)
        except Exception as exc:
            print(f"  dedup parse fail {vz}: {exc}", flush=True)
    rng4_unique = len(sig_groups)
    print(f"  Stage B dedup: {rng4_unique} unique shapes", flush=True)

    summary.append({
        'group': group, 'bitmask': list(bm), 'name': slug,
        'V': len(V), 'E': len(E),
        'master_count': master,
        'rng4_raw_fp': len(groups),
        'rng4_snapped': len(snapped),
        'rng4_failed': len(failed),
        'rng4_unique_after_stage_b': rng4_unique,
        'time_seconds': elapsed,
    })

print()
print(f"{'name':12s} {'V':>4s} {'E':>5s} {'master':>7s} {'rng4_raw':>9s} {'rng4_snap':>10s} {'rng4_unique':>12s}")
print('=' * 80)
for s in summary:
    print(f"{s['name']:12s} {s['V']:4d} {s['E']:5d} {s['master_count']:7d} "
          f"{s['rng4_raw_fp']:9d} {s['rng4_snapped']:10d} "
          f"{s['rng4_unique_after_stage_b']:12d}")

with open(os.path.join('ongoing_work', 'rng4_snaptest_summary.json'), 'w') as f:
    json.dump(summary, f, indent=2)
print('\nSaved ongoing_work/rng4_snaptest_summary.json')
