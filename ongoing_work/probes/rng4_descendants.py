"""rng=4 snap+dedup probe on small A4 / B4 descendants.

Goal: extend the rng=4 corpus-stability test from regulars (5-cell,
16-cell, 24-cell, tesseract — already shown stable in
rng4_snaptest_summary.json) to small Wythoff descendants.  If every
rng=4 raw fingerprint either snap-fails or Stage-B-collapses onto
the existing rng=2 corpus, that strongly extends the
'corpus is stable under higher rng' claim past regulars.

Cases (by ascending V*E so quick ones go first):
  A4 (1,1,0,0) truncated 5-cell      V=20  E=40
  A4 (1,0,0,1) runcinated 5-cell     V=20  E=60
  B4 (0,0,1,0) 24-cell-as-B4         V=24  E=96
  B4 (0,1,0,0) rectified tesseract   V=32  E=96
  B4 (0,0,1,1) truncated 16-cell     V=48  E=120
  A4 (1,1,1,0) cantitruncated 5-cell V=60  E=120
  A4 (1,1,0,1) runcitruncated 5-cell V=60  E=150

For each: run rng=4 search, group by Stage-A fingerprint, attempt
snap on each unique fp, then Stage-B dedup the snapped output and
compare against the existing rng=2 corpus on disk.
"""
import sys, os, time, json
from pathlib import Path
sys.path.insert(0, 'lib')
sys.path.insert(0, 'tools')
from wythoff import build_polytope
from search_engine import gen_dirs, search, group_by_shape
from emit_generic import project_and_emit
from dedup_corpus_by_shape import parse_vzome, shape_signature

OUT = Path('ongoing_work/rng4_descendants_tmp')
OUT.mkdir(exist_ok=True)

# Build the rng=2 corpus signature index from disk
print('Building rng=2 corpus Stage-B signature index...', flush=True)
t0 = time.time()
corpus_sigs = {}
for vz in Path('output/wythoff_sweep').rglob('*.vZome'):
    P, E_loaded = parse_vzome(vz)
    sig = shape_signature(P, E_loaded)
    corpus_sigs.setdefault(sig, []).append(str(vz))
print(f'  {len(corpus_sigs)} unique sigs across '
      f'{sum(len(v) for v in corpus_sigs.values())} files '
      f'({time.time()-t0:.1f}s)', flush=True)

print('\nGenerating rng=4 candidate kernel directions...', flush=True)
t0 = time.time()
dirs4 = list(gen_dirs(rng=4, integer_only=False, permute_dedup=False))
print(f'rng=4: {len(dirs4)} dirs ({time.time()-t0:.1f}s)', flush=True)

cases = [
    ('A4', (1,1,0,0), 'truncated 5-cell',       'truncated_5-cell'),
    ('A4', (1,0,0,1), 'runcinated 5-cell',      'runcinated_5-cell'),
    ('B4', (0,0,1,0), '24-cell-as-B4',          '24-cell'),
    ('B4', (0,1,0,0), 'rectified tesseract',    'rectified_tesseract'),
    ('B4', (0,0,1,1), 'truncated 16-cell',      'truncated_16-cell'),
    ('A4', (1,1,1,0), 'cantitruncated 5-cell',  'cantitruncated_5-cell'),
    ('A4', (1,1,0,1), 'runcitruncated 5-cell',  'runcitruncated_5-cell'),
]

summary = []
for group, bm, name, slug in cases:
    print(f"\n=== {group} {bm} {name} ===", flush=True)
    V, E = build_polytope(group, bm)
    print(f"V={len(V)} E={len(E)}", flush=True)
    t0 = time.time()
    hits = search(name, V, E, dirs4, verbose=False)
    groups = group_by_shape(hits, V, E)
    search_time = time.time() - t0
    print(f"rng=4 raw fp = {len(groups)} ({search_time:.1f}s)", flush=True)

    snapped = []
    snap_failed = 0
    for fp_idx, (fp, examples) in enumerate(groups.items()):
        n0, sig0, balls0 = examples[0]
        n_list = list(map(float, n0))
        out_path = str(OUT / f'{slug}__{fp_idx:03d}.vZome')
        try:
            project_and_emit(name, V, E, n_list, out_path, verbose=False)
            snapped.append(out_path)
        except Exception:
            snap_failed += 1
    print(f"  snap: {len(snapped)}/{len(groups)} pass "
          f"({snap_failed} fail)", flush=True)

    # Stage B dedup
    sig_groups = {}
    for vz in snapped:
        P, E_loaded = parse_vzome(Path(vz))
        sig = shape_signature(P, E_loaded)
        sig_groups.setdefault(sig, []).append(vz)
    print(f"  Stage B unique: {len(sig_groups)}", flush=True)

    # Compare against existing corpus
    in_corpus = sum(1 for s in sig_groups if s in corpus_sigs)
    new_shapes = [s for s in sig_groups if s not in corpus_sigs]
    print(f"  in corpus: {in_corpus}/{len(sig_groups)}", flush=True)
    if new_shapes:
        print(f"  *** NEW SHAPES NOT IN CORPUS: {len(new_shapes)} ***",
              flush=True)
        for s in new_shapes:
            print(f"    sig {s[:80]}: {sig_groups[s]}", flush=True)

    # Cleanup tmp .vZome files
    for vz in snapped:
        try: os.remove(vz)
        except OSError: pass

    summary.append({
        'group': group, 'bitmask': list(bm), 'name': name,
        'V': len(V), 'E': len(E),
        'rng4_raw_fp': len(groups),
        'rng4_snapped': len(snapped),
        'rng4_snap_failed': snap_failed,
        'rng4_unique_after_stage_b': len(sig_groups),
        'in_existing_corpus': in_corpus,
        'new_shapes': len(new_shapes),
        'search_seconds': search_time,
    })
    # incremental save (in case probe is interrupted)
    with open('ongoing_work/rng4_descendants_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

print()
print(f"{'name':24s} {'V':>4s} {'E':>5s} {'raw':>5s} {'snap':>5s} "
      f"{'fail':>5s} {'uniq':>5s} {'corp':>5s} {'NEW':>5s}")
print('=' * 86)
for s in summary:
    print(f"{s['name']:24s} {s['V']:4d} {s['E']:5d} "
          f"{s['rng4_raw_fp']:5d} {s['rng4_snapped']:5d} "
          f"{s['rng4_snap_failed']:5d} "
          f"{s['rng4_unique_after_stage_b']:5d} "
          f"{s['in_existing_corpus']:5d} {s['new_shapes']:5d}")

# Final cleanup
try:
    OUT.rmdir()
except OSError:
    pass
print()
print('Saved ongoing_work/rng4_descendants_summary.json')
