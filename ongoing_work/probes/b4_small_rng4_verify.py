"""rng=4 verification probe for B4 16-cell and B4 24-cell.

Both small polytopes (V=8, V=24).  Audit reported nonzero gaps:
  B4 (0,0,0,1) 16-cell:    pipeline=3, full_rng2=6, gap=3
  B4 (0,0,1,0) 24-cell-B4: pipeline=2, full_rng2=3, gap=1
However, the audit only counted output/wythoff_sweep/* files, not the
master regular folders (output/16cell/, output/24cell/).  This probe
verifies that all rng=4 snap+dedup unique shapes for these two
polytopes are covered by master + sweep folders combined.
"""
import sys, time, json
from pathlib import Path
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

print('Indexing existing corpus + master regulars...', flush=True)
corpus_sigs = {}
for vz in Path('output/wythoff_sweep').rglob('*.vZome'):
    try:
        P, E_loaded = parse_vzome(vz)
        sig = shape_signature(P, E_loaded)
        corpus_sigs.setdefault(sig, []).append(str(vz))
    except Exception:
        pass
for d in ['5cell', '8cell', '16cell', '24cell', '600cell', '120cell',
          'snub24cell', 'grand_antiprism']:
    p = Path('output') / d
    if p.exists():
        for vz in p.glob('*.vZome'):
            try:
                P, E_loaded = parse_vzome(vz)
                sig = shape_signature(P, E_loaded)
                corpus_sigs.setdefault(sig, []).append(str(vz))
            except Exception:
                pass
print(f'  {len(corpus_sigs)} unique sigs across '
      f'{sum(len(v) for v in corpus_sigs.values())} files', flush=True)

cases = [
    ('16-cell',           'B4', (0, 0, 0, 1), 3),
    ('24-cell',           'B4', (0, 0, 1, 0), 1),
]

OUT = Path('ongoing_work/b4_small_rng4_verify')
OUT.mkdir(exist_ok=True)
summary = []

for name, group, bm, audit_gap in cases:
    print(f'\n=== {name} {group} {bm} (audit gap={audit_gap}) ===', flush=True)
    V, E = build_polytope(group, bm)
    print(f'  V={len(V)} E={len(E)}', flush=True)
    t0 = time.time()
    hits = search(name, V, E, dirs4, verbose=False)
    groups = group_by_shape(hits, V, E)
    print(f'  rng=4 raw fp = {len(groups)} ({time.time()-t0:.1f}s)',
          flush=True)
    sub = OUT / name.replace(' ', '_')
    sub.mkdir(exist_ok=True)
    records = []
    for fp_idx, (fp, examples) in enumerate(groups.items()):
        n0 = examples[0][0]
        n_list = list(map(float, n0))
        out_path = str(sub / f'fp{fp_idx:02d}.vZome')
        try:
            project_and_emit(name, V, E, n_list, out_path, verbose=False)
            P, E_loaded = parse_vzome(Path(out_path))
            sig = shape_signature(P, E_loaded)
            in_corpus = sig in corpus_sigs
            records.append({
                'fp_idx': fp_idx, 'kernel': n_list, 'snap': True,
                'sig_V': sig[0], 'sig_E': sig[1], 'sig_hash': sig[2],
                'in_corpus': in_corpus,
                'matched': corpus_sigs.get(sig) if in_corpus else None,
            })
            tag = 'IN CORPUS' if in_corpus else 'NEW'
            print(f'    fp{fp_idx:02d} V={sig[0]} E={sig[1]} '
                  f'hash={sig[2][:8]} [{tag}]', flush=True)
        except Exception as exc:
            records.append({
                'fp_idx': fp_idx, 'kernel': n_list, 'snap': False,
                'snap_error': str(exc),
            })
            print(f'    fp{fp_idx:02d} SNAP FAIL '
                  f'({type(exc).__name__})', flush=True)
    sig_groups = {}
    for r in records:
        if r['snap']:
            key = (r['sig_V'], r['sig_E'], r['sig_hash'])
            sig_groups.setdefault(key, []).append(r)
    new = [k for k, v in sig_groups.items() if not v[0]['in_corpus']]
    print(f'  Stage-B unique: {len(sig_groups)}; not in corpus: '
          f'{len(new)}', flush=True)
    summary.append({
        'name': name, 'group': group, 'bm': list(bm),
        'audit_gap': audit_gap,
        'rng4_raw_fp': len(groups),
        'rng4_snapped': sum(1 for r in records if r['snap']),
        'stage_b_unique': len(sig_groups),
        'in_corpus': sum(1 for v in sig_groups.values()
                         if v[0]['in_corpus']),
        'new_not_in_corpus': len(new),
        'records': records,
    })

with open('ongoing_work/b4_small_rng4_verify.json', 'w') as f:
    json.dump(summary, f, indent=2, default=str)
print('\nSaved ongoing_work/b4_small_rng4_verify.json')
