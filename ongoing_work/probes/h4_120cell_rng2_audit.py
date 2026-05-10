"""rng=2 audit + snap+dedup probe on H4 (1,0,0,0) 120-cell.

This polytope was missing from the kernel-completeness audit case
list and from the rng=4 regulars probe.  The rng=2 sweep emitted
output/120cell/120cell_H4_to_H3.vZome (1 shape).  This probe runs
the full unrestricted rng=2 search, snaps each fp to ZZ[phi]^3, and
checks that every snapped shape matches the existing corpus.

V = 600, E = 1200.  Expected wall time at rng=2: ~30-60 min.
rng=4 on this polytope is infeasible (V*E too large).
"""
import sys, time, json
from pathlib import Path
sys.path.insert(0, 'lib')
sys.path.insert(0, 'tools')
from wythoff import build_polytope
from search_engine import gen_dirs, search, group_by_shape
from emit_generic import project_and_emit
from dedup_corpus_by_shape import parse_vzome, shape_signature

OUT = Path('ongoing_work/h4_120cell_rng2_audit')
OUT.mkdir(exist_ok=True)

print('Generating rng=2 directions...', flush=True)
t0 = time.time()
dirs2 = list(gen_dirs(rng=2, integer_only=False, permute_dedup=False))
print(f'rng=2: {len(dirs2)} dirs ({time.time()-t0:.1f}s)', flush=True)

V, E = build_polytope('H4', (1, 0, 0, 0))
print(f'120-cell V={len(V)} E={len(E)}', flush=True)

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

t0 = time.time()
hits = search('120-cell', V, E, dirs2, verbose=False)
groups = group_by_shape(hits, V, E)
search_time = time.time() - t0
print(f'rng=2 raw fp = {len(groups)} ({search_time:.1f}s)', flush=True)

records = []
for fp_idx, (fp, examples) in enumerate(groups.items()):
    n0 = examples[0][0]
    n_list = list(map(float, n0))
    out_path = str(OUT / f'fp{fp_idx:02d}.vZome')
    try:
        project_and_emit('120-cell', V, E, n_list, out_path, verbose=False)
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
        print(f'  fp{fp_idx:02d} V={sig[0]} E={sig[1]} '
              f'hash={sig[2][:8]} [{tag}]', flush=True)
    except Exception as exc:
        records.append({
            'fp_idx': fp_idx, 'kernel': n_list, 'snap': False,
            'snap_error': str(exc),
        })
        print(f'  fp{fp_idx:02d} SNAP FAIL ({type(exc).__name__})',
              flush=True)

sig_groups = {}
for r in records:
    if r['snap']:
        key = (r['sig_V'], r['sig_E'], r['sig_hash'])
        sig_groups.setdefault(key, []).append(r)

new = [k for k, v in sig_groups.items() if not v[0]['in_corpus']]
print(f'\nStage-B unique: {len(sig_groups)}; not in corpus: {len(new)}',
      flush=True)

with open('ongoing_work/h4_120cell_rng2_audit.json', 'w') as f:
    json.dump({
        'polytope': '120-cell',
        'group': 'H4', 'bm': [1, 0, 0, 0], 'V': len(V), 'E': len(E),
        'rng': 2,
        'rng2_raw_fp': len(groups),
        'rng2_snapped': sum(1 for r in records if r['snap']),
        'rng2_snap_failed': sum(1 for r in records if not r['snap']),
        'stage_b_unique': len(sig_groups),
        'in_corpus': sum(1 for v in sig_groups.values()
                         if v[0]['in_corpus']),
        'new_not_in_corpus': len(new),
        'records': records,
    }, f, indent=2, default=str)
print('\nSaved ongoing_work/h4_120cell_rng2_audit.json')
