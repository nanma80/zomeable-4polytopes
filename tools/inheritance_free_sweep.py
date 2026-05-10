"""Unified inheritance-free direct-search sweep over Wythoff polytopes.

Single canonical algorithm for every (group, bitmask, rng) cell:

    1.  Build polytope V, E via wythoff.build_polytope (regular if a single
        node ringed, descendant otherwise — same code path).
    2.  Enumerate Z[phi]^4 candidate kernel directions at the requested
        rng with `gen_dirs(integer_only=False, permute_dedup=False)`.  No
        kernel-inheritance assumption: every polytope is searched
        independently from scratch.
    3.  Run search() with parallel-edge-class reduction and progress
        logging.
    4.  Group hits by Stage-A signature (group_by_shape), snap each
        unique fp to Z[phi]^3 via project_and_emit, then Stage-B dedup
        by shape_signature.
    5.  Compare Stage-B sigs against the on-disk corpus
        (output/wythoff_sweep + output/<polytope>) to flag NEW shapes.

Results are appended to a single JSON keyed by (group, bitmask, rng).
Re-running the script skips cells already present, so the same command
can be invoked many times to fill out the matrix incrementally.

Usage:
    python tools/inheritance_free_sweep.py --group H4 --rng 2
    python tools/inheritance_free_sweep.py --group F4 --rng 3 --bitmask 0100
    python tools/inheritance_free_sweep.py --group H4 --rng 4 --only-bitmasks 1000,0001
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from itertools import product
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'lib'))
sys.path.insert(0, str(REPO / 'tools'))

from wythoff import build_polytope                                  # noqa: E402
from search_engine import gen_dirs, search, group_by_shape          # noqa: E402
from emit_generic import project_and_emit                           # noqa: E402
from dedup_corpus_by_shape import parse_vzome, shape_signature      # noqa: E402

DEFAULT_OUT = REPO / 'ongoing_work' / 'inheritance_free_sweep.json'
TMP_DIR = REPO / 'ongoing_work' / 'inheritance_free_sweep_tmp'

GROUPS = {'A4', 'B4', 'F4', 'H4'}

# Polytope display names (fall back to "<group> <bitmask>" when missing).
NAMES = {
    ('A4', (1,0,0,0)): '5-cell',
    ('A4', (1,1,0,0)): 'truncated 5-cell',
    ('A4', (0,1,0,0)): 'rectified 5-cell',
    ('A4', (1,0,1,0)): 'cantellated 5-cell',
    ('A4', (1,1,1,0)): 'cantitruncated 5-cell',
    ('A4', (1,0,0,1)): 'runcinated 5-cell',
    ('A4', (1,1,0,1)): 'runcitruncated 5-cell',
    ('A4', (0,1,1,0)): 'bitruncated 5-cell',
    ('A4', (1,1,1,1)): 'omnitruncated 5-cell',
    ('B4', (1,0,0,0)): 'tesseract',
    ('B4', (0,0,0,1)): '16-cell',
    ('B4', (0,0,1,0)): '24-cell-as-B4',
    ('B4', (0,1,0,0)): 'rectified tesseract',
    ('B4', (1,1,0,0)): 'truncated tesseract',
    ('B4', (1,0,1,0)): 'cantellated tesseract',
    ('B4', (1,1,1,0)): 'cantitruncated tesseract',
    ('B4', (1,0,0,1)): 'runcinated tesseract',
    ('B4', (1,1,0,1)): 'runcitruncated tesseract',
    ('B4', (1,0,1,1)): 'runcitruncated 16-cell',
    ('B4', (0,1,1,0)): 'bitruncated tesseract',
    ('B4', (0,1,0,1)): 'cantellated 16-cell',
    ('B4', (0,1,1,1)): 'cantitruncated 16-cell',
    ('B4', (0,0,1,1)): 'truncated 16-cell',
    ('B4', (1,1,1,1)): 'omnitruncated tesseract',
    ('F4', (1,0,0,0)): '24-cell',
    ('F4', (0,0,0,1)): '24-cell (dual ring)',
    ('F4', (1,1,0,0)): 'truncated 24-cell',
    ('F4', (0,1,0,0)): 'rectified 24-cell',
    ('F4', (1,0,1,0)): 'cantellated 24-cell',
    ('F4', (1,1,1,0)): 'cantitruncated 24-cell',
    ('F4', (1,0,0,1)): 'runcinated 24-cell',
    ('F4', (1,1,0,1)): 'runcitruncated 24-cell',
    ('F4', (1,0,1,1)): 'runcitruncated 24-cell (dual)',
    ('F4', (0,1,1,0)): 'bitruncated 24-cell',
    ('F4', (0,1,0,1)): 'cantellated 24-cell (dual)',
    ('F4', (0,1,1,1)): 'cantitruncated 24-cell (dual)',
    ('F4', (0,0,1,1)): 'truncated 24-cell (dual)',
    ('F4', (1,1,1,1)): 'omnitruncated 24-cell',
    ('H4', (1,0,0,0)): '120-cell',
    ('H4', (0,0,0,1)): '600-cell',
    ('H4', (1,1,0,0)): 'truncated 120-cell',
    ('H4', (0,1,0,0)): 'rectified 120-cell',
    ('H4', (1,0,1,0)): 'cantellated 120-cell',
    ('H4', (1,1,1,0)): 'cantitruncated 120-cell',
    ('H4', (1,0,0,1)): 'runcinated 120-cell',
    ('H4', (1,1,0,1)): 'runcitruncated 120-cell',
    ('H4', (1,0,1,1)): 'runcitruncated 600-cell',
    ('H4', (0,1,1,0)): 'bitruncated 120-cell',
    ('H4', (0,1,0,1)): 'cantellated 600-cell',
    ('H4', (0,1,1,1)): 'cantitruncated 600-cell',
    ('H4', (0,0,1,1)): 'truncated 600-cell',
    ('H4', (1,1,1,1)): 'omnitruncated 120-cell',
}


def all_bitmasks():
    """Every nonzero 4-bit mask."""
    return [bm for bm in product([0, 1], repeat=4) if any(bm)]


def parse_bm(s: str) -> tuple:
    s = s.strip().replace(',', '')
    if len(s) != 4 or any(c not in '01' for c in s):
        raise argparse.ArgumentTypeError(
            f'bitmask must be 4 chars of 0/1, got {s!r}')
    return tuple(int(c) for c in s)


def load_existing(path: Path) -> dict:
    """Return dict keyed by (group, bm-tuple, rng) -> result-dict."""
    if not path.exists():
        return {}
    with open(path) as f:
        data = json.load(f)
    out = {}
    for rec in data.get('results', []):
        out[(rec['group'], tuple(rec['bitmask']), rec['rng'])] = rec
    return out


def save_results(path: Path, by_key: dict, started_at: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        '_schema': 'inheritance_free_sweep.v1',
        'started_at': started_at,
        'updated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
        '_note': 'One row per (group, bitmask, rng).  Stage-B unique sigs '
                 'compared against the on-disk corpus.  Algorithm: direct '
                 'search() with parallel-edge reduction; no inheritance '
                 'assumption.',
        'results': sorted(
            by_key.values(),
            key=lambda r: (r['group'], r['bitmask'], r['rng'])),
    }
    tmp = path.with_suffix(path.suffix + '.tmp')
    with open(tmp, 'w') as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, path)


def build_corpus_index() -> dict:
    """Stage-B sig -> [vzome paths] across the on-disk corpus."""
    sigs: dict = {}
    roots = [REPO / 'output']
    for root in roots:
        if not root.exists():
            continue
        for vz in root.rglob('*.vZome'):
            try:
                P, E = parse_vzome(vz)
                sig = shape_signature(P, E)
            except Exception:
                continue
            sigs.setdefault(sig, []).append(str(vz.relative_to(REPO)))
    return sigs


def sweep_cell(group, bm, rng, dirs, corpus_sigs, tag):
    """Run the inheritance-free pipeline for a single (group, bm, rng) cell."""
    name = NAMES.get((group, bm), f'{group} {"".join(map(str, bm))}')
    t0 = time.time()
    V, E = build_polytope(group, bm)
    print(f'\n=== {tag}  {group} {bm}  {name}  V={len(V)}  E={len(E)} ===',
          flush=True)
    t_search0 = time.time()
    hits = search(name, V, E, dirs, verbose='progress', progress_tag=tag)
    t_search = time.time() - t_search0

    t_fp0 = time.time()
    groups = group_by_shape(hits, V, E)
    t_fp = time.time() - t_fp0
    print(f'  {tag} Stage-A fp groups = {len(groups)}  '
          f'(search {t_search:.1f}s, fingerprint {t_fp:.1f}s)', flush=True)

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    snapped = []
    snap_failed = 0
    snap_errors = []
    for fp_idx, (fp_hash, examples) in enumerate(groups.items()):
        n0, _sig0, _balls0 = examples[0]
        n_list = list(map(float, n0))
        out_path = TMP_DIR / f'{group}_{"".join(map(str, bm))}_rng{rng}__{fp_idx:03d}.vZome'
        try:
            project_and_emit(name, V, E, n_list, str(out_path),
                             verbose=False)
            snapped.append((fp_hash, out_path))
        except Exception as exc:
            snap_failed += 1
            snap_errors.append({'fp_idx': fp_idx,
                                'fp_hash': fp_hash[:16],
                                'err': repr(exc)[:200]})

    sig_groups: dict = {}
    for fp_hash, vz in snapped:
        try:
            P, E_loaded = parse_vzome(vz)
            sig = shape_signature(P, E_loaded)
        except Exception as exc:
            snap_errors.append({'phase': 'stage_b',
                                'vz': str(vz),
                                'err': repr(exc)[:200]})
            continue
        sig_groups.setdefault(sig, []).append(fp_hash)

    in_corpus = sum(1 for s in sig_groups if s in corpus_sigs)
    new_sigs = [s for s in sig_groups if s not in corpus_sigs]

    for _fp, vz in snapped:
        try:
            os.remove(vz)
        except OSError:
            pass
    try:
        TMP_DIR.rmdir()
    except OSError:
        pass

    elapsed = time.time() - t0
    rec = {
        'group': group,
        'bitmask': list(bm),
        'name': name,
        'rng': rng,
        'V': len(V),
        'E': len(E),
        'n_dirs': len(dirs),
        'n_hits': len(hits),
        'stage_a_fp': len(groups),
        'snapped_ok': len(snapped),
        'snap_failed': snap_failed,
        'stage_b_unique': len(sig_groups),
        'in_corpus': in_corpus,
        'new_shapes': len(new_sigs),
        'new_sig_examples': [
            {'sig_prefix': s[:120], 'fp_hashes': sig_groups[s][:5]}
            for s in new_sigs[:10]],
        'snap_errors': snap_errors[:5],
        'search_seconds': round(t_search, 2),
        'fingerprint_seconds': round(t_fp, 2),
        'total_seconds': round(elapsed, 2),
        'finished_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
    }
    star = '  *** NEW SHAPES ***' if new_sigs else ''
    print(f'  {tag} Stage-B unique={len(sig_groups)}  in_corpus={in_corpus}  '
          f'new={len(new_sigs)}{star}  total={elapsed:.1f}s', flush=True)
    return rec


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--group', required=True, choices=sorted(GROUPS))
    p.add_argument('--rng', type=int, required=True, choices=[2, 3, 4])
    p.add_argument('--bitmask', type=parse_bm, default=None,
                   help='Single bitmask (e.g. 0100); omit to sweep all 15')
    p.add_argument('--only-bitmasks', default=None,
                   help='Comma-separated subset, e.g. "1000,0001"')
    p.add_argument('--out', default=str(DEFAULT_OUT))
    p.add_argument('--force', action='store_true',
                   help='Re-run cells already present in the JSON')
    p.add_argument('--max-V', type=int, default=None,
                   help='Skip polytopes with V > this (runtime guard)')
    args = p.parse_args()

    out_path = Path(args.out)
    started_at = time.strftime('%Y-%m-%dT%H:%M:%S')

    if args.bitmask is not None:
        worklist = [args.bitmask]
    elif args.only_bitmasks:
        worklist = [parse_bm(x) for x in args.only_bitmasks.split(',') if x.strip()]
    else:
        worklist = all_bitmasks()

    by_key = load_existing(out_path)
    print(f'[{started_at}] inheritance_free_sweep group={args.group} '
          f'rng={args.rng}  worklist={len(worklist)} polytopes  '
          f'existing={len(by_key)} cells in {out_path}', flush=True)

    print('Building on-disk corpus signature index...', flush=True)
    t0 = time.time()
    corpus_sigs = build_corpus_index()
    print(f'  {len(corpus_sigs)} unique sigs  '
          f'({sum(len(v) for v in corpus_sigs.values())} files, '
          f'{time.time() - t0:.1f}s)', flush=True)

    print(f'Generating rng={args.rng} dirs (permute_dedup=False)...',
          flush=True)
    t0 = time.time()
    dirs = list(gen_dirs(rng=args.rng, integer_only=False,
                         permute_dedup=False))
    print(f'  {len(dirs)} dirs ({time.time() - t0:.1f}s)', flush=True)

    n = len(worklist)
    for i, bm in enumerate(worklist, 1):
        key = (args.group, bm, args.rng)
        if key in by_key and not args.force:
            print(f'[{i}/{n}] SKIP {args.group} {bm} rng={args.rng} '
                  f'(already in {out_path.name})', flush=True)
            continue
        try:
            V_pre, _ = build_polytope(args.group, bm)
        except Exception as exc:
            print(f'[{i}/{n}] FAIL build_polytope {args.group} {bm}: {exc}',
                  flush=True)
            continue
        if args.max_V is not None and len(V_pre) > args.max_V:
            print(f'[{i}/{n}] SKIP {args.group} {bm} V={len(V_pre)} '
                  f'> max-V={args.max_V}', flush=True)
            continue
        tag = f'{i}/{n}'
        rec = sweep_cell(args.group, bm, args.rng, dirs, corpus_sigs, tag)
        by_key[key] = rec
        save_results(out_path, by_key, started_at)

    print(f'\n[{time.strftime("%Y-%m-%dT%H:%M:%S")}] DONE  '
          f'wrote {out_path}', flush=True)


if __name__ == '__main__':
    main()
