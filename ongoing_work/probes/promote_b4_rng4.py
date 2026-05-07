"""Promote 6 NEW B4 rng=4 shapes to output/wythoff_sweep/ with full audit.

Inputs: ongoing_work/{rectified_tesseract,truncated_16cell}_rng4.json
        ongoing_work/{rectified_tesseract,truncated_16cell}_rng4/*.vZome

Pipeline (all in one pass, full audit logging):
    1. For each .vZome flagged in_corpus=False, recompute Stage-B sig
       directly from the file (don't trust the JSON blindly).
    2. Within each polytope, drop files whose sig matches another file
       (the fp00 vs fp06 hash collisions, where the same shape comes
       out at different fp indices).
    3. Confirm no collision against the FULL existing corpus
       (output/wythoff_sweep/**/*.vZome plus master regulars).
    4. Confirm no cross-polytope duplicates among the 6 candidates.
    5. Use lib/polytope_features.classify_kernel to label each kernel.
       Build target filename: <label>[_<idx>]_<hash10>.vZome under
       output/wythoff_sweep/<slug>/.
    6. Copy the .vZome with the new name; preserve original kernel.
    6b. Normalise physical scale within each polytope: the upstream
        rng=4 emitter sometimes outputs a kernel-rotated shape at a
        scale that is phi^k times larger than its sibling shapes
        (where k>=1 is a small integer).  Within each polytope we
        apply tools/scale_vzome_by_inv_phi.transform_text to bring
        every file down to the smallest emitted min-edge.  This is
        an exact ZZ[phi]-integer rewrite (no floating-point error)
        and the Stage-B fingerprint hash is uniform-scale invariant,
        so signatures are preserved.  Result: all promoted shapes in
        a given polytope share a common min-edge length.
    7. Append new entries to output/wythoff_sweep/manifest.json with
       a per-entry 'rng': 4 field; bump top-level n_ok and update
       'rng' top-level field to 'mixed (2 baseline; 4 for B4 rng=4
       audit-flagged additions)' + a note.
    8. Print a full audit log.
"""
import json
import math
import os
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'lib'))
sys.path.insert(0, str(ROOT / 'tools'))

import numpy as np
from wythoff import build_polytope
from polytope_features import (
    classify_kernel, extract_features, label_basename,
)
from dedup_corpus_by_shape import parse_vzome, shape_signature
from scale_vzome_by_inv_phi import transform_text as _inv_phi_transform_text

PHI = (1.0 + 5.0 ** 0.5) / 2.0


SOURCES = [
    {
        'group': 'B4',
        'bitmask': (0, 1, 0, 0),
        'source_polytope': 'rectified tesseract',
        'slug': 'rectified_tesseract',
        'json': ROOT / 'ongoing_work' / 'rectified_tesseract_rng4.json',
        'src_dir': ROOT / 'ongoing_work' / 'rectified_tesseract_rng4',
    },
    {
        'group': 'B4',
        'bitmask': (0, 0, 1, 1),
        'source_polytope': 'truncated 16-cell',
        'slug': 'truncated_16-cell',
        'json': ROOT / 'ongoing_work' / 'truncated_16cell_rng4.json',
        'src_dir': ROOT / 'ongoing_work' / 'truncated_16cell_rng4',
    },
]

OUT_DIR = ROOT / 'output' / 'wythoff_sweep'
MANIFEST = OUT_DIR / 'manifest.json'

print('=' * 80)
print('Stage 1: Index existing corpus signatures (output + master regulars)')
print('=' * 80)
corpus_sigs = {}
n_files = 0
for vz in (ROOT / 'output' / 'wythoff_sweep').rglob('*.vZome'):
    try:
        P, E = parse_vzome(vz)
        sig = shape_signature(P, E)
        corpus_sigs.setdefault(sig, []).append(str(vz.relative_to(ROOT)))
        n_files += 1
    except Exception as exc:
        pass
for d in ['5cell', '8cell', '16cell', '24cell', '600cell', '120cell',
          'snub24cell', 'grand_antiprism']:
    p = ROOT / 'output' / d
    if p.exists():
        for vz in p.glob('*.vZome'):
            try:
                P, E = parse_vzome(vz)
                sig = shape_signature(P, E)
                corpus_sigs.setdefault(sig, []).append(str(vz.relative_to(ROOT)))
                n_files += 1
            except Exception as exc:
                pass
print(f'indexed {n_files} files across {len(corpus_sigs)} unique sigs')

print()
print('=' * 80)
print('Stage 2: Verify Stage-B sigs of candidate files & dedup within polytope')
print('=' * 80)

candidates = []  # list of (poly_meta, src_path, sig, kernel)
for poly in SOURCES:
    print(f"\n  {poly['source_polytope']}:")
    data = json.loads(poly['json'].read_text())
    fresh_sigs_in_polytope = {}
    for rec in data['records']:
        if not rec.get('snap'):
            continue
        if rec.get('in_corpus'):
            continue
        path = ROOT / rec['out_path'].replace('\\', '/')
        if not path.exists():
            print(f'    MISSING {path}')
            continue
        P, E = parse_vzome(path)
        sig = shape_signature(P, E)
        # sanity: hash matches the JSON record
        recorded_hash = rec['sig_hash']
        if sig[2] != recorded_hash:
            print(f'    HASH MISMATCH for {path.name}: '
                  f'JSON={recorded_hash} vs recomputed={sig[2]}; SKIP')
            continue
        if sig in fresh_sigs_in_polytope:
            other = fresh_sigs_in_polytope[sig]
            print(f"    duplicate within polytope: fp{rec['fp_idx']:02d} "
                  f"({path.name}) ~= fp{other['fp_idx']:02d} "
                  f"({other['path'].name}) -- DROP fp{rec['fp_idx']:02d}")
            continue
        fresh_sigs_in_polytope[sig] = {
            'fp_idx': rec['fp_idx'], 'path': path}
        # global corpus check
        if sig in corpus_sigs:
            print(f"    fp{rec['fp_idx']:02d} hash={sig[2][:10]} "
                  f"unexpectedly matches existing corpus "
                  f"{corpus_sigs[sig][0]}; SKIP")
            continue
        candidates.append({
            'poly': poly,
            'fp_idx': rec['fp_idx'],
            'src_path': path,
            'sig': sig,
            'kernel': tuple(rec['kernel']),
        })
        print(f"    fp{rec['fp_idx']:02d} hash={sig[2][:10]} V={sig[0]} "
              f"E={sig[1]} edges={list(sig[3])}  KEEP")

print()
print('=' * 80)
print('Stage 3: Cross-polytope dedup (across the candidate set)')
print('=' * 80)
sig_seen = {}
for c in candidates:
    if c['sig'] in sig_seen:
        other = sig_seen[c['sig']]
        print(f"  collision: {c['poly']['source_polytope']} fp{c['fp_idx']:02d} "
              f"== {other['poly']['source_polytope']} fp{other['fp_idx']:02d} -- impossible (V differs)")
        sys.exit(1)
    sig_seen[c['sig']] = c
print(f'  no cross-polytope duplicates among {len(candidates)} candidates.')

print()
print('=' * 80)
print('Stage 4: Classify kernels and assign filenames')
print('=' * 80)
# Build features per (group, bitmask)
feat_cache = {}
classifications = []
for c in candidates:
    key = (c['poly']['group'], c['poly']['bitmask'])
    if key not in feat_cache:
        V, E = build_polytope(*key)
        feat_cache[key] = extract_features(np.asarray(V, dtype=float), E)
    feats = feat_cache[key]
    label, subtype = classify_kernel(np.asarray(c['kernel']), feats)
    classifications.append((label, subtype))
    print(f"  {c['poly']['source_polytope']:25s} fp{c['fp_idx']:02d} "
          f"kernel={list(c['kernel'])}  ->  ({label}, {subtype})")

# Disambiguate within (polytope, label, subtype): assign indices
group_buckets = {}
for i, (c, (label, subtype)) in enumerate(zip(candidates, classifications)):
    key = (c['poly']['slug'], label, subtype)
    group_buckets.setdefault(key, []).append(i)

# Existing manifest provides existing label_basenames per polytope
manifest = json.loads(MANIFEST.read_text())
existing_basenames = {}  # (slug, label, subtype) -> set of indices used
for s in manifest['shapes']:
    if s.get('status') != 'ok':
        continue
    src = s.get('source_polytope')
    if src is None:
        continue
    slug = '_'.join(src.split())
    key = (slug, s.get('label'), s.get('label_subtype'))
    file_path = s.get('file', '')
    fname = Path(file_path).name
    # if fname has an _NN_ index, capture it
    parts = fname.replace('.vZome', '').split('_')
    # find index right before the trailing 10-char hash
    idx = None
    if len(parts) >= 2:
        candidate = parts[-2]
        if candidate.isdigit() and len(candidate) == 2:
            idx = int(candidate)
    existing_basenames.setdefault(key, set())
    if idx is not None:
        existing_basenames[key].add(idx)

# Assign filenames
filenames = [None] * len(candidates)
for key, idxs in group_buckets.items():
    used = existing_basenames.get(key, set())
    for i in idxs:
        c = candidates[i]
        label, subtype = classifications[i]
        # Choose first unused two-digit index
        n = 0
        if len(idxs) > 1 or label == 'oblique' or used:
            while n in used:
                n += 1
            used.add(n)
            basename = label_basename(label, subtype, index=n)
        else:
            basename = label_basename(label, subtype, index=None)
        h10 = c['sig'][2][:10]
        filenames[i] = f'{basename}_{h10}.vZome'
        print(f"  {c['poly']['source_polytope']:25s} fp{c['fp_idx']:02d} "
              f"-> {filenames[i]}")

print()
print('=' * 80)
print('Stage 5: Copy files into output/wythoff_sweep/<slug>/')
print('=' * 80)
dst_paths = []  # parallel to candidates / classifications / filenames
for c, (label, subtype), fname in zip(candidates, classifications, filenames):
    dst = OUT_DIR / c['poly']['slug'] / fname
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        print(f'  refuse to overwrite existing {dst}')
        sys.exit(1)
    shutil.copy2(c['src_path'], dst)
    dst_paths.append(dst)
    print(f"  copied {c['src_path'].name}")
    print(f"      -> {dst.relative_to(ROOT)}")


def _min_edge_length(path):
    P, E = parse_vzome(path)
    L = np.array([np.linalg.norm(P[i] - P[j]) for i, j in E])
    return float(L.min())


print()
print('=' * 80)
print('Stage 5b: Normalise physical scale within each polytope (* phi^-k)')
print('=' * 80)
# Group dst paths by polytope slug so we can find the canonical (smallest)
# min-edge length and rescale outliers down to it via integer powers of 1/phi.
slug_to_paths = defaultdict(list)
for c, dst in zip(candidates, dst_paths):
    slug_to_paths[c['poly']['slug']].append(dst)

for slug, paths in slug_to_paths.items():
    edges = {p: _min_edge_length(p) for p in paths}
    target = min(edges.values())
    print(f'  {slug}: canonical target min_edge = {target:.5f}')
    for p, m in edges.items():
        ratio = m / target
        if ratio < 1.001:
            print(f'    {p.name}: already at target ({m:.5f})')
            continue
        k = int(round(math.log(ratio, PHI)))
        if k <= 0 or abs(ratio - PHI ** k) > 0.01 * (PHI ** k):
            print(f'    {p.name}: WARNING ratio={ratio:.4f} not a clean '
                  f'power of phi -- LEAVING AS-IS')
            continue
        text = p.read_text(encoding='utf-8')
        for _ in range(k):
            text = _inv_phi_transform_text(text)
        p.write_text(text, encoding='utf-8')
        new_min = _min_edge_length(p)
        print(f'    {p.name}: was {m:.5f}, /phi^{k} -> {new_min:.5f}')
        # Stage-B sig is scale-invariant; verify hash unchanged.
        P_new, E_new = parse_vzome(p)
        sig_new = shape_signature(P_new, E_new)
        # find the original sig for this dst
        for c, d in zip(candidates, dst_paths):
            if d == p:
                if sig_new[2] != c['sig'][2]:
                    print(f'      FATAL: hash changed during rescale '
                          f'({c["sig"][2]} -> {sig_new[2]})')
                    sys.exit(1)
                break

print()
print('=' * 80)
print('Stage 6: Append entries to manifest.json (rng=4 marker per entry)')
print('=' * 80)

def _strut_counts_from_vzome(path):
    """Count the 4 zometool strut colours from emitted .vZome by edge length."""
    P, E = parse_vzome(path)
    L = np.array([np.linalg.norm(P[i]-P[j]) for i, j in E])
    Lmin = L.min()
    ratios = np.round(L/Lmin, 4)
    # Standard zometool ratio palette: 1.0=B(blue), 1.61803=Y(yellow),
    # 1.7013=R(red), 1.4734=G(green) -- mapping verified from existing
    # manifest entries.
    palette = {1.0: 'B', 1.4734: 'G', 1.618: 'Y', 1.7013: 'R'}
    counts = Counter()
    for r in ratios:
        for k, c in palette.items():
            if abs(float(r) - k) < 5e-3:
                counts[c] += 1
                break
    return dict(counts)

new_entries = []
for c, (label, subtype), fname in zip(candidates, classifications, filenames):
    rel = Path('wythoff_sweep') / c['poly']['slug'] / fname
    rec = {
        'fp_hash': c['sig'][2],  # 16 char
        'group': c['poly']['group'],
        'bitmask': list(c['poly']['bitmask']),
        'source_polytope': c['poly']['source_polytope'],
        'shape_idx': None,
        'n_balls': c['sig'][0],
        'kernel': list(c['kernel']),
        'label': label,
        'label_subtype': subtype,
        'rng': 4,
        'status': 'ok',
        'file': str(rel).replace('/', os.sep),
        'strut_counts': _strut_counts_from_vzome(c['src_path']),
        'note': 'B4 rng=4 audit-flagged finding (Milestone 6 / 7).  '
                'Found by ongoing_work/probes/{rect_tess,trunc16}_rng4_focused.py.',
    }
    new_entries.append(rec)
    print(f"  {c['poly']['source_polytope']:25s} {fname}  "
          f"label={label}/{subtype}  struts={rec['strut_counts']}")

manifest['shapes'].extend(new_entries)
manifest['n_ok'] = manifest.get('n_ok', 0) + len(new_entries)
manifest['rng'] = 'mixed (2 baseline; 4 for B4 rng=4 audit-flagged additions)'
manifest.setdefault('notes', []).append(
    f'B4 rng=4 audit (Milestones 6/7): added {len(new_entries)} new shapes '
    f'(3 from rectified tesseract, 3 from truncated 16-cell) found at rng=4 '
    f'that the rng=2 sweep cannot reach.  Each new entry carries rng=4.'
)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True))
print(f"\n  manifest now has {len(manifest['shapes'])} shape entries "
      f"(n_ok={manifest['n_ok']}, n_fail={manifest.get('n_fail', 0)})")

print()
print('=' * 80)
print(f'PROMOTED {len(new_entries)} NEW B4 rng=4 SHAPES.')
print('=' * 80)
