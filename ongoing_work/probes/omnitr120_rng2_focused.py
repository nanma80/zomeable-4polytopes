"""Salvage the 65 H4 omnitruncated 120-cell rng=2 fingerprints.

The full sweep (tools/run_wythoff_sweep.py --group H4 --bitmask 1111) reached
Step 3 on 5/3, finding 65 distinct fingerprints from 432 H4 kernels for
the omnitruncated 120-cell (V=14544 E=29538), but never completed Step 4
(snap + emit).  The fingerprint file ongoing_work/shapes_rng2_H4_1111.jsonl
contains one example_kernel per shape group.

This focused probe re-uses those example_kernels directly -- no Step 1/2
re-run -- and calls emit_generic.project_and_emit per fingerprint with
per-fingerprint try/except so a single snap failure doesn't kill the
batch.  Output:

  ongoing_work/h4_omnitr120_rng2.json
  ongoing_work/h4_omnitr120_rng2/omnitr120_fp{NN}_*.vZome

Each shape's example_sig already shows ~480-505 collapsed/off-palette
edges (out of 29538), so most are expected to snap-fail.  Survivors are
candidate NEW shapes -- audit against the existing corpus follows.
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'lib'))
sys.path.insert(0, str(ROOT / 'tools'))

from wythoff import build_polytope
from emit_generic import project_and_emit
from dedup_corpus_by_shape import parse_vzome, shape_signature


JSONL = ROOT / 'ongoing_work' / 'shapes_rng2_H4_1111.jsonl'
OUT_DIR = ROOT / 'ongoing_work' / 'h4_omnitr120_rng2'
OUT_DIR.mkdir(exist_ok=True)
OUT_JSON = ROOT / 'ongoing_work' / 'h4_omnitr120_rng2.json'

print('=' * 70, flush=True)
print('Loading 65 fingerprints from shapes_rng2_H4_1111.jsonl', flush=True)
print('=' * 70, flush=True)
data = json.loads(JSONL.read_text())
shapes = data['shapes']
print(f'  group={data["group"]} bitmask={data["bitmask"]} '
      f'name={data["name"]}', flush=True)
print(f'  V={data["V"]} E={data["E"]}  n_distinct_shapes={len(shapes)}',
      flush=True)

print()
print('Building polytope V/E...', flush=True)
V, E = build_polytope('H4', tuple(data['bitmask']))
print(f'  V={len(V)}  E={len(E)}', flush=True)
assert len(V) == data['V'] and len(E) == data['E']

print()
print('Indexing existing corpus + master regulars...', flush=True)
corpus_sigs = {}
for vz in (ROOT / 'output' / 'wythoff_sweep').rglob('*.vZome'):
    try:
        P, El = parse_vzome(vz)
        sig = shape_signature(P, El)
        corpus_sigs.setdefault(sig, []).append(str(vz.relative_to(ROOT)))
    except Exception:
        pass
for d in ['5cell', '8cell', '16cell', '24cell', '600cell', '120cell',
          'snub24cell', 'grand_antiprism']:
    p = ROOT / 'output' / d
    if p.exists():
        for vz in p.glob('*.vZome'):
            try:
                P, El = parse_vzome(vz)
                sig = shape_signature(P, El)
                corpus_sigs.setdefault(sig, []).append(str(vz.relative_to(ROOT)))
            except Exception:
                pass
print(f'  {len(corpus_sigs)} unique sigs across '
      f'{sum(len(v) for v in corpus_sigs.values())} files', flush=True)

print()
print('=' * 70, flush=True)
print('Snap + emit each of the 65 example_kernels (per-fp try/except)',
      flush=True)
print('=' * 70, flush=True)

records = []
n_snap_ok = 0
n_snap_fail = 0
t_total = time.time()
for fp_idx, s in enumerate(shapes):
    kernel = list(map(float, s['example_kernel']))
    fname = f'omnitr120_fp{fp_idx:02d}.vZome'
    out_path = str(OUT_DIR / fname)
    rec = {
        'fp_idx': fp_idx,
        'fp_hash_pre_snap': s['fp_hash'],
        'kernel': kernel,
        'n_kernels_in_group': s['n_kernels'],
        'pre_snap_n_balls': s['n_balls'],
        'pre_snap_sig': s['example_sig'],
        'out_path': str(Path('ongoing_work') / 'h4_omnitr120_rng2' / fname),
    }
    t0 = time.time()
    try:
        project_and_emit('omnitruncated 120-cell', V, E, kernel,
                         out_path, verbose=False)
        P, El = parse_vzome(Path(out_path))
        sig = shape_signature(P, El)
        in_corpus = sig in corpus_sigs
        rec.update({
            'snap': True,
            'sig_V': sig[0],
            'sig_E': sig[1],
            'sig_hash': sig[2],
            'sig_edges': list(sig[3]),
            'in_corpus': in_corpus,
            'matched_corpus_files': corpus_sigs.get(sig, []),
            'wall_s': time.time() - t0,
        })
        n_snap_ok += 1
        status = 'IN CORPUS' if in_corpus else 'NEW'
        print(f'  fp{fp_idx:02d}/{len(shapes)-1}  V={sig[0]:>5} E={sig[1]:>5} '
              f'edges={list(sig[3])} [{status}] '
              f'({rec["wall_s"]:.1f}s)', flush=True)
    except Exception as exc:
        rec.update({
            'snap': False,
            'snap_error_type': type(exc).__name__,
            'snap_error': str(exc)[:300],
            'wall_s': time.time() - t0,
        })
        n_snap_fail += 1
        print(f'  fp{fp_idx:02d}/{len(shapes)-1}  SNAP FAIL '
              f'({type(exc).__name__}: {str(exc)[:80]}) '
              f'({rec["wall_s"]:.1f}s)', flush=True)
    records.append(rec)

    # Persist progress every 5 fps so a crash or kill doesn't lose work.
    if (fp_idx + 1) % 5 == 0 or fp_idx == len(shapes) - 1:
        OUT_JSON.write_text(json.dumps({
            'group': 'H4',
            'bitmask': data['bitmask'],
            'name': data['name'],
            'V': data['V'],
            'E': data['E'],
            'n_total': len(shapes),
            'n_processed': fp_idx + 1,
            'n_snap_ok': n_snap_ok,
            'n_snap_fail': n_snap_fail,
            'records': records,
        }, indent=2, default=str))

print()
print('=' * 70, flush=True)
print(f'Per-fingerprint snap done in {time.time() - t_total:.1f}s',
      flush=True)
print(f'  snap OK: {n_snap_ok}/{len(shapes)}', flush=True)
print(f'  snap FAIL: {n_snap_fail}/{len(shapes)}', flush=True)
print('=' * 70, flush=True)

# Stage-B dedup across snap-OK records
sig_groups = {}
for r in records:
    if r.get('snap'):
        key = (r['sig_V'], r['sig_E'], r['sig_hash'],
               tuple(tuple(x) for x in r['sig_edges']))
        sig_groups.setdefault(key, []).append(r)
print(f'\nStage-B unique among snap-OK: {len(sig_groups)}')
new_groups = {k: v for k, v in sig_groups.items() if not v[0]['in_corpus']}
print(f'  in existing corpus: {len(sig_groups) - len(new_groups)}')
print(f'  NOT in corpus (NEW candidates): {len(new_groups)}')
for k, v in new_groups.items():
    fp_indices = [r['fp_idx'] for r in v]
    print(f'    NEW: V={k[0]} E={k[1]} hash={k[2][:10]} '
          f'edges={list(k[3])}  '
          f'fp_idx={fp_indices}')

# Final flush of JSON
OUT_JSON.write_text(json.dumps({
    'group': 'H4',
    'bitmask': data['bitmask'],
    'name': data['name'],
    'V': data['V'],
    'E': data['E'],
    'n_total': len(shapes),
    'n_processed': len(records),
    'n_snap_ok': n_snap_ok,
    'n_snap_fail': n_snap_fail,
    'stage_b_unique': len(sig_groups),
    'in_corpus': len(sig_groups) - len(new_groups),
    'new_not_in_corpus': len(new_groups),
    'records': records,
}, indent=2, default=str))

print(f'\nWrote {OUT_JSON.relative_to(ROOT)}')
