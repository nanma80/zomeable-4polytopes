"""Dry-run validation of Stage 5b in promote_b4_rng4.py.

Replicates the Stage 2 filter (snap=True, in_corpus=False, dedup-within
polytope) on the ongoing_work source files, then applies the Stage 5b
rescale logic and prints final min-edge per emitted file.  Does NOT
touch output/wythoff_sweep/.
"""
import json
import math
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'lib'))
sys.path.insert(0, str(ROOT / 'tools'))

import numpy as np
from dedup_corpus_by_shape import parse_vzome, shape_signature
from scale_vzome_by_inv_phi import transform_text as inv_phi

PHI = (1.0 + 5.0 ** 0.5) / 2.0


def min_edge(p):
    P, E = parse_vzome(p)
    L = np.array([np.linalg.norm(P[i] - P[j]) for i, j in E])
    return float(L.min())


SOURCES = [
    ('rectified_tesseract', ROOT / 'ongoing_work' / 'rectified_tesseract_rng4.json'),
    ('truncated_16-cell',   ROOT / 'ongoing_work' / 'truncated_16cell_rng4.json'),
]

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    targets = []
    for slug, jp in SOURCES:
        out = td / slug
        out.mkdir()
        data = json.loads(jp.read_text())
        seen = {}
        for rec in data['records']:
            if not rec.get('snap') or rec.get('in_corpus'):
                continue
            p = ROOT / rec['out_path'].replace('\\', '/')
            if not p.exists():
                continue
            sig = shape_signature(*parse_vzome(p))
            if sig[2] != rec['sig_hash']:
                continue
            if sig in seen:
                continue
            seen[sig] = rec['fp_idx']
            fp_name = f"fp{rec['fp_idx']:02d}.vZome"
            d = out / fp_name
            shutil.copy2(p, d)
            targets.append((d, slug))

    by = defaultdict(list)
    for d, s in targets:
        by[s].append(d)

    print('PROMOTED candidates BEFORE Stage 5b:')
    pre_sigs = {}
    for s, ps in by.items():
        for p in ps:
            sig = shape_signature(*parse_vzome(p))
            pre_sigs[p] = sig[2]
            print(f'  {s}/{p.name}: min_edge={min_edge(p):8.4f}  hash={sig[2][:10]}')

    print()
    print('Applying Stage 5b...')
    for s, ps in by.items():
        edges = {p: min_edge(p) for p in ps}
        tgt = min(edges.values())
        print(f'  {s}: target = {tgt:.4f}')
        for p, m in edges.items():
            ratio = m / tgt
            if ratio < 1.001:
                print(f'    {p.name}: at target ({m:.4f})')
                continue
            k = int(round(math.log(ratio, PHI)))
            if k <= 0 or abs(ratio - PHI ** k) > 0.01 * PHI ** k:
                print(f'    {p.name}: ratio={ratio:.4f} not clean phi^k -- skip')
                continue
            t = p.read_text(encoding='utf-8')
            for _ in range(k):
                t = inv_phi(t)
            p.write_text(t, encoding='utf-8')
            print(f'    {p.name}: was {m:.4f}, /phi^{k} -> {min_edge(p):.4f}')

    print()
    print('AFTER Stage 5b:')
    all_hashes_preserved = True
    for s, ps in by.items():
        for p in ps:
            sig = shape_signature(*parse_vzome(p))
            ok = sig[2] == pre_sigs[p]
            if not ok:
                all_hashes_preserved = False
            print(f'  {s}/{p.name}: min_edge={min_edge(p):8.4f}  hash={sig[2][:10]} ({"OK" if ok else "HASH CHANGED"})')

    print()
    print(f'all hashes preserved: {all_hashes_preserved}')
    print('all min_edges within slug equal: ' + str(all(
        len(set(round(min_edge(p), 4) for p in ps)) == 1 for ps in by.values()
    )))
