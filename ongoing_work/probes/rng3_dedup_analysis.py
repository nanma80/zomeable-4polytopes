"""Compare rng=3 snap-test shapes against the rng=2 corpus.

For each polytope we tested at rng=3, group the rng=3 .vZome files by
3D-shape signature (rotation+reflection+uniform-scale invariant) and
compare the resulting set against the rng=2 corpus signatures in
output/wythoff_sweep/<polytope>/.  Reports:
  * rng=3 distinct shapes
  * rng=2 distinct shapes (corpus)
  * shapes new at rng=3 (not in rng=2 corpus)
"""
import sys, os, json
from pathlib import Path
sys.path.insert(0, 'tools')
from dedup_corpus_by_shape import parse_vzome, shape_signature

# rng=3 outputs we just produced
RNG3 = Path('ongoing_work/rng3_snaptest')

# rng=2 corpus folders (per-polytope)
CORPUS = Path('output/wythoff_sweep')

# slug -> rng=2 corpus folder name
slug_to_folder = {
    'cantitruncated_5cell':  'cantitruncated_5-cell',
    'runcitruncated_5cell':  'runcitruncated_5-cell',
    'omnitruncated_5cell':   'omnitruncated_5-cell',
    # cantellated 16-cell is aliased to rectified 24-cell folder
    'cantellated_16cell':    'rectified_24-cell',
}

def signatures_in(folder: Path):
    """Returns a dict of {sig_tuple: [vzome filenames]}."""
    out = {}
    if not folder.exists():
        return out
    for vz in sorted(folder.glob('*.vZome')):
        P, E = parse_vzome(vz)
        sig = shape_signature(P, E)
        out.setdefault(sig, []).append(vz.name)
    return out

# Group rng=3 .vZome files by slug
rng3_by_slug = {}
for vz in sorted(RNG3.glob('*.vZome')):
    slug = vz.name.split('__')[0]
    rng3_by_slug.setdefault(slug, []).append(vz)

print(f"{'polytope':25s} {'rng2_files':>10s} {'rng2_unique':>11s} "
      f"{'rng3_raw':>9s} {'rng3_unique':>11s} {'NEW':>5s}")
print('=' * 80)
results = []
for slug, files in sorted(rng3_by_slug.items()):
    folder = CORPUS / slug_to_folder[slug]
    rng2_sigs = signatures_in(folder)
    rng3_sigs = {}
    for vz in files:
        P, E = parse_vzome(vz)
        sig = shape_signature(P, E)
        rng3_sigs.setdefault(sig, []).append(vz.name)
    new_sigs = [s for s in rng3_sigs if s not in rng2_sigs]
    rng2_files_count = sum(len(v) for v in rng2_sigs.values())
    print(f"{slug:25s} {rng2_files_count:10d} {len(rng2_sigs):11d} "
          f"{len(files):9d} {len(rng3_sigs):11d} {len(new_sigs):5d}")
    results.append({
        'slug': slug, 'corpus_folder': str(folder),
        'rng2_corpus_files': rng2_files_count,
        'rng2_corpus_unique_shapes': len(rng2_sigs),
        'rng3_raw_files': len(files),
        'rng3_unique_shapes': len(rng3_sigs),
        'rng3_new_shapes': len(new_sigs),
        'new_signature_examples': [
            {'shape_hash': s[2], 'n_balls': s[0], 'n_edges': s[1],
             'rng3_files': rng3_sigs[s]}
            for s in new_sigs
        ],
    })

with open('ongoing_work/rng3_dedup_summary.json', 'w') as f:
    json.dump(results, f, indent=2)
print()
print('Saved ongoing_work/rng3_dedup_summary.json')
