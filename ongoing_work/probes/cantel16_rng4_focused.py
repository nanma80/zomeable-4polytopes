"""rng=4 focused probe on B4 cantellated 16-cell.

Same protocol as trunc16_rng4_focused.py but for B4 (0,1,0,1)
cantellated 16-cell, V=96 E=288.  Kernel-completeness audit reported
gap=3 for this polytope.  Two earlier gap-bearing B4 cases each
gained 3 new zomeable shapes at rng=4 (rectified tesseract gap=4,
truncated 16-cell gap=4); this probe extends the pattern to gap=3.
"""
import sys, os, time, json
from pathlib import Path
sys.path.insert(0, 'lib')
sys.path.insert(0, 'tools')
from wythoff import build_polytope
from search_engine import gen_dirs, search, group_by_shape
from emit_generic import project_and_emit
from dedup_corpus_by_shape import parse_vzome, shape_signature

OUT = Path('ongoing_work/cantellated_16cell_rng4')
OUT.mkdir(exist_ok=True)

print('Generating rng=4 directions...', flush=True)
t0 = time.time()
dirs4 = list(gen_dirs(rng=4, integer_only=False, permute_dedup=False))
print(f'rng=4: {len(dirs4)} dirs ({time.time()-t0:.1f}s)', flush=True)

V, E = build_polytope('B4', (0, 1, 0, 1))
print(f'cantellated 16-cell V={len(V)} E={len(E)}', flush=True)

print('Indexing existing corpus + master regulars...', flush=True)
corpus_sigs = {}
for vz in Path('output/wythoff_sweep').rglob('*.vZome'):
    try:
        P, E_loaded = parse_vzome(vz)
        sig = shape_signature(P, E_loaded)
        corpus_sigs.setdefault(sig, []).append(str(vz))
    except Exception as exc:
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
            except Exception as exc:
                pass
print(f'  {len(corpus_sigs)} unique sigs across '
      f'{sum(len(v) for v in corpus_sigs.values())} files', flush=True)

t0 = time.time()
hits = search('cantellated 16-cell', V, E, dirs4, verbose=False)
groups = group_by_shape(hits, V, E)
search_time = time.time() - t0
print(f'rng=4 raw fp = {len(groups)} ({search_time:.1f}s)', flush=True)

with open('ongoing_work/cantellated_16cell_rng4_kernels.json', 'w') as f:
    json.dump(
        [{'fp_idx': i,
          'fp_hash': str(fp),
          'num_kernel_directions': len(examples),
          'first_kernel': list(map(float, examples[0][0])),
          'first_5_kernels': [list(map(float, ex[0]))
                              for ex in examples[:5]]}
         for i, (fp, examples) in enumerate(groups.items())],
        f, indent=2)

records = []
for fp_idx, (fp, examples) in enumerate(groups.items()):
    n0, sig0, balls0 = examples[0]
    n_list = list(map(float, n0))
    out_path = str(OUT / f'cantel_16c_fp{fp_idx:02d}_kernel_{n_list}.vZome')
    out_path = out_path.replace(' ', '').replace('[', '').replace(']', '')
    out_path = out_path.replace(',', '_')
    try:
        project_and_emit('cantellated 16-cell', V, E, n_list, out_path,
                         verbose=False)
        P, E_loaded = parse_vzome(Path(out_path))
        sig = shape_signature(P, E_loaded)
        in_corpus = sig in corpus_sigs
        records.append({
            'fp_idx': fp_idx,
            'kernel': n_list,
            'fp_hash': fp,
            'snap': True,
            'sig_V': sig[0],
            'sig_E': sig[1],
            'sig_hash': sig[2],
            'sig_edges': list(sig[3]),
            'in_corpus': in_corpus,
            'matched_corpus_files': (corpus_sigs.get(sig) if in_corpus
                                     else None),
            'out_path': out_path,
        })
        status = 'IN CORPUS' if in_corpus else 'NEW'
        print(f'  fp{fp_idx:02d} kernel={n_list} -> '
              f'V={sig[0]} E={sig[1]} hash={sig[2][:8]} '
              f'edges={list(sig[3])} [{status}]', flush=True)
    except Exception as exc:
        records.append({
            'fp_idx': fp_idx,
            'kernel': n_list,
            'fp_hash': fp,
            'snap': False,
            'snap_error': str(exc),
        })
        print(f'  fp{fp_idx:02d} kernel={n_list} -> SNAP FAIL '
              f'({type(exc).__name__})', flush=True)

sig_groups = {}
for r in records:
    if r['snap']:
        key = (r['sig_V'], r['sig_E'], r['sig_hash'],
               tuple(tuple(x) for x in r['sig_edges']))
        sig_groups.setdefault(key, []).append(r)

print(f'\nStage-B unique: {len(sig_groups)}', flush=True)
new_groups = {k: v for k, v in sig_groups.items()
              if not v[0]['in_corpus']}
print(f'Not in corpus: {len(new_groups)}', flush=True)

with open('ongoing_work/cantellated_16cell_rng4.json', 'w') as f:
    json.dump({
        'rng4_raw_fp': len(groups),
        'rng4_snapped': sum(1 for r in records if r['snap']),
        'rng4_snap_failed': sum(1 for r in records if not r['snap']),
        'stage_b_unique': len(sig_groups),
        'in_corpus': sum(1 for v in sig_groups.values() if v[0]['in_corpus']),
        'new_not_in_corpus': len(new_groups),
        'records': records,
    }, f, indent=2, default=str)
print('\nSaved ongoing_work/cantellated_16cell_rng4.json')
