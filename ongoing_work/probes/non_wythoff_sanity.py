"""Sanity check: do the snub-24-cell and grand antiprism (non-Wythoffian
uniforms) project to master's hand-curated 4 zomeable shapes when fed
through the same search engine + snap pipeline used for the Wythoff
sweep?

Master shapes:
  output/snub24cell/snub24cell_cell_first.vZome
  output/snub24cell/snub24cell_vertex_first.vZome
  output/grand_antiprism/grand_antiprism_ring_first.vZome
  output/grand_antiprism/grand_antiprism_vertex_first.vZome

The point: snub-24-cell and grand antiprism are *not* Wythoffian, so
build_polytope (the Wythoff constructor) cannot generate them.  But
they share the rng=2 search + snap + dedup machinery with the Wythoff
sweep, so finding master's 4 shapes from a fresh rng=2 search is a
meaningful end-to-end sanity check.
"""
import sys, os, time, json
from pathlib import Path
sys.path.insert(0, 'lib')
sys.path.insert(0, 'tools')
from polytopes import snub_24cell, grand_antiprism
from search_engine import gen_dirs, search, group_by_shape
from emit_generic import project_and_emit
from dedup_corpus_by_shape import parse_vzome, shape_signature

print('Generating rng=2 directions...', flush=True)
dirs2 = list(gen_dirs(rng=2, integer_only=False, permute_dedup=False))
print(f'rng=2: {len(dirs2)} dirs', flush=True)

OUT = Path('ongoing_work/non_wythoff_sanity')
OUT.mkdir(exist_ok=True)

cases = [
    ('snub_24cell',     snub_24cell,
     ['output/snub24cell/snub24cell_cell_first.vZome',
      'output/snub24cell/snub24cell_vertex_first.vZome']),
    ('grand_antiprism', grand_antiprism,
     ['output/grand_antiprism/grand_antiprism_ring_first.vZome',
      'output/grand_antiprism/grand_antiprism_vertex_first.vZome']),
]

summary = []
for name, builder, master_files in cases:
    print(f"\n=== {name} ===", flush=True)
    t0 = time.time()
    V, E = builder()
    print(f"V={len(V)} E={len(E)} (built in {time.time()-t0:.1f}s)",
          flush=True)
    t0 = time.time()
    hits = search(name, V, E, dirs2, verbose=False)
    groups = group_by_shape(hits, V, E)
    elapsed = time.time() - t0
    print(f"rng=2 raw fp = {len(groups)} ({elapsed:.1f}s)", flush=True)

    # Snap each fingerprint
    snapped, failed = [], []
    for fp_idx, (fp, examples) in enumerate(groups.items()):
        n0, sig0, balls0 = examples[0]
        n_list = list(map(float, n0))
        out_path = str(OUT / f'{name}__{fp_idx:02d}.vZome')
        try:
            project_and_emit(name, V, E, n_list, out_path, verbose=False)
            snapped.append(out_path)
        except Exception as exc:
            failed.append((fp_idx, n_list, type(exc).__name__))
    print(f"  snap: {len(snapped)}/{len(groups)} pass", flush=True)

    # Stage B dedup on the rng=2 snapped files
    sig_groups = {}
    for vz in snapped:
        P, E_loaded = parse_vzome(Path(vz))
        sig = shape_signature(P, E_loaded)
        sig_groups.setdefault(sig, []).append(vz)
    print(f"  Stage B unique: {len(sig_groups)}", flush=True)

    # Compare against master
    master_sigs = {}
    for mf in master_files:
        if not Path(mf).exists():
            print(f"  MASTER MISSING: {mf}", flush=True)
            continue
        P, E_loaded = parse_vzome(Path(mf))
        sig = shape_signature(P, E_loaded)
        master_sigs[sig] = mf

    found = [s for s in sig_groups if s in master_sigs]
    not_in_master = [s for s in sig_groups if s not in master_sigs]
    missing = [mf for s, mf in master_sigs.items() if s not in sig_groups]
    print(f"  Master shapes: {len(master_sigs)}", flush=True)
    print(f"  Master shapes recovered: {len(found)}", flush=True)
    if missing:
        print(f"  MISSING from probe:", flush=True)
        for mf in missing:
            print(f"    {mf}", flush=True)
    if not_in_master:
        print(f"  EXTRA shapes (not in master):", flush=True)
        for s in not_in_master:
            print(f"    {s[:3]}: {sig_groups[s]}", flush=True)

    summary.append({
        'name': name,
        'V': len(V), 'E': len(E),
        'rng2_raw_fp': len(groups),
        'rng2_snapped': len(snapped),
        'rng2_unique_after_stage_b': len(sig_groups),
        'master_files': len(master_files),
        'master_shapes_recovered': len(found),
        'missing_from_probe': len(missing),
        'extra_not_in_master': len(not_in_master),
    })

print()
print(f"{'name':16s} {'V':>4s} {'E':>5s} {'master':>7s} {'rng2_raw':>9s} "
      f"{'rng2_snap':>10s} {'rng2_unique':>12s} {'recovered':>10s} "
      f"{'missing':>8s} {'extra':>6s}")
print('=' * 110)
for s in summary:
    print(f"{s['name']:16s} {s['V']:4d} {s['E']:5d} "
          f"{s['master_files']:7d} {s['rng2_raw_fp']:9d} "
          f"{s['rng2_snapped']:10d} {s['rng2_unique_after_stage_b']:12d} "
          f"{s['master_shapes_recovered']:10d} "
          f"{s['missing_from_probe']:8d} {s['extra_not_in_master']:6d}")

with open('ongoing_work/non_wythoff_sanity_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print()
print('Saved ongoing_work/non_wythoff_sanity_summary.json')
