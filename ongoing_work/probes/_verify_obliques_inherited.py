"""Verify: are the descendant 'oblique' kernels just the parent regular's
obscure projections inherited?

Approach: for each unique oblique kernel n appearing in the wythoff_sweep
manifest, project the *parent regular polytope* along n (using the same
emit_generic.project_and_emit pipeline as the sweep), compute the Stage-B
fingerprint of the result, and compare to the Stage-B fingerprints of the
hand-curated master files in output/{5cell, 8cell, 16cell, 24cell}/.

Stage-B is rotation + uniform-scale invariant, so basis differences
between emit_vzome.py (master files) and emit_generic.py (sweep) do
not interfere.

If the parent-projection-via-descendant-oblique-kernel's Stage-B matches
a master file's Stage-B, the user's hypothesis is confirmed for that
kernel: the descendant's oblique projection IS the descendant viewed
through the parent's master oblique projection direction.
"""
import json
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'lib'))
sys.path.insert(0, str(ROOT / 'tools'))

from wythoff import build_polytope
from emit_generic import project_and_emit
from dedup_corpus_by_shape import parse_vzome, shape_signature


# ---- Step 1: collect unique oblique kernels per group from manifest ----
m = json.loads((ROOT / 'output' / 'wythoff_sweep' / 'manifest.json').read_text())
shapes = [s for s in m['shapes'] if s.get('status') == 'ok' and s.get('label') == 'oblique']

# group -> {kernel_tuple: [example file]}
unique_by_group = defaultdict(dict)
for s in shapes:
    g = s.get('group')
    k = tuple(s.get('kernel'))
    unique_by_group[g].setdefault(k, []).append(s.get('file'))

print('=' * 78)
print('Unique oblique kernels per group (from wythoff_sweep manifest):')
print('=' * 78)
for g in ['A4', 'B4', 'F4', 'H4']:
    if g not in unique_by_group:
        print(f'  {g}: 0')
        continue
    print(f'  {g}: {len(unique_by_group[g])} distinct kernel directions')
    for k, files in unique_by_group[g].items():
        print(f'    kernel={list(k)}  -> {len(files)} descendant file(s)')

# ---- Step 2: index master parent files by Stage-B ----
print()
print('=' * 78)
print('Master parent files (output/{5cell,8cell,16cell,24cell}/*.vZome) sigs:')
print('=' * 78)
master_sigs = {}  # sig -> file path
for sub in ['5cell', '8cell', '16cell', '24cell']:
    for vz in (ROOT / 'output' / sub).glob('*.vZome'):
        try:
            P, E = parse_vzome(vz)
            sig = shape_signature(P, E)
            master_sigs[sig] = str(vz.relative_to(ROOT))
            print(f'  {vz.relative_to(ROOT)}: V={sig[0]} E={sig[1]} '
                  f'hash={sig[2][:10]} edges={list(sig[3])}')
        except Exception as exc:
            print(f'  SKIP {vz.relative_to(ROOT)}: {exc}')

# ---- Step 3: project each parent regular along each descendant oblique kernel ----
PARENTS = {
    'A4': [('A4', (1, 0, 0, 0), '5-cell')],
    'B4': [('B4', (1, 0, 0, 0), 'tesseract'),
           ('B4', (0, 0, 0, 1), '16-cell')],
    'F4': [('F4', (1, 0, 0, 0), '24-cell')],
    'H4': [('H4', (1, 0, 0, 0), '120-cell'),
           ('H4', (0, 0, 0, 1), '600-cell')],
}

print()
print('=' * 78)
print('Project each parent regular along each descendant oblique kernel:')
print('=' * 78)
results = []  # (group, parent_name, kernel, sig, match_master_or_None)
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    for g, kernels in unique_by_group.items():
        for k, files in kernels.items():
            for grp, bm, name in PARENTS.get(g, []):
                V, E = build_polytope(grp, bm)
                kn = list(k)
                out = td / f'{name.replace(" ","")}_kernel.vZome'
                try:
                    project_and_emit(name, V, E, kn, str(out), verbose=False)
                    P, El = parse_vzome(out)
                    sig = shape_signature(P, El)
                except Exception as exc:
                    print(f'  {g} {name:>10} kernel={kn} -> SNAP FAIL '
                          f'({type(exc).__name__})')
                    results.append((g, name, k, None, None, str(exc)[:80]))
                    continue
                match = master_sigs.get(sig)
                marker = '<-- MATCHES MASTER!' if match else ''
                print(f'  {g} {name:>10} kernel={kn}')
                print(f'      -> sig V={sig[0]} E={sig[1]} hash={sig[2][:10]} '
                      f'edges={list(sig[3])}  {marker}')
                if match:
                    print(f'         master file: {match}')
                results.append((g, name, k, sig, match, None))

# ---- Step 4: summary ----
print()
print('=' * 78)
print('SUMMARY: descendant oblique kernels matched to master parent files')
print('=' * 78)
for g in ['A4', 'B4', 'F4', 'H4']:
    rs = [r for r in results if r[0] == g]
    if not rs:
        continue
    print(f'\n{g}:')
    # group by kernel
    by_k = defaultdict(list)
    for r in rs:
        by_k[r[2]].append(r)
    for k, group_rs in by_k.items():
        print(f'  kernel={list(k)}')
        matches = [r for r in group_rs if r[4] is not None]
        if matches:
            for r in matches:
                print(f'    via parent {r[1]:>10}: matches {r[4]}')
        else:
            for r in group_rs:
                if r[3] is None:
                    print(f'    via parent {r[1]:>10}: SNAP FAIL ({r[5]})')
                else:
                    print(f'    via parent {r[1]:>10}: NO MATCH (hash={r[3][2][:10]} '
                          f'V={r[3][0]} E={r[3][1]})')
