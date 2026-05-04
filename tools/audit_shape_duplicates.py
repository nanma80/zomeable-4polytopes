"""Audit the wythoff_sweep corpus for shapes that are *congruent*
(rotation + reflection + uniform-scale equivalent) despite having
distinct fp_hashes.

Two .vZome files are deemed the same shape when:

  (a) Their vertex sets have the same normalised pairwise-distance
      multiset (rotation+reflection+translation+scale invariant), AND
  (b) Their edge-length multisets match (after the same normalisation).

If both match, the shapes are congruent in the sense the user defined:
"if two models only differ by a 3D rotation [or reflection or uniform
scale] and each edge goes from the same exact orbit, it's the same
projection."

We do NOT consider edges in different orbits (colours) as the same
shape: a coincidence in vertex layout but a different edge selection
makes them genuinely distinct.

Per polytope (subfolder), we group all vZome files by an exact
fingerprint of (sorted normalised distance tuple, sorted edge-length
multiset).  Files in the same fingerprint group are duplicates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

PHI = (1 + 5 ** 0.5) / 2
JPP_RE = re.compile(r'<JoinPointPair start="([^"]+)" end="([^"]+)"\s*/>')
SHOW_RE = re.compile(r'<ShowPoint\s+point="([^"]+)"\s*/>')


def parse_int_coord(s: str) -> tuple[int, ...]:
    return tuple(int(x) for x in s.split())


def to_float3(t6: tuple[int, ...]) -> np.ndarray:
    a = np.array(t6, dtype=float)
    return np.array([a[0] + a[1] * PHI,
                     a[2] + a[3] * PHI,
                     a[4] + a[5] * PHI])


def parse_vzome(path: Path):
    text = path.read_text()
    points_int: list[tuple[int, ...]] = []
    seen: dict[tuple[int, ...], int] = {}
    for s in SHOW_RE.findall(text):
        t = parse_int_coord(s)
        if t not in seen:
            seen[t] = len(points_int)
            points_int.append(t)
    edges = []
    for s, e in JPP_RE.findall(text):
        ts = parse_int_coord(s)
        te = parse_int_coord(e)
        if ts not in seen:
            seen[ts] = len(points_int); points_int.append(ts)
        if te not in seen:
            seen[te] = len(points_int); points_int.append(te)
        edges.append((seen[ts], seen[te]))
    P = np.stack([to_float3(t) for t in points_int])
    return P, edges


def shape_fingerprint(P: np.ndarray, E, dist_decimals=5, edge_decimals=5):
    """Return a hashable, rotation+reflection+scale invariant
    fingerprint of (vertex set, edge selection)."""
    # pairwise sq distances of vertex set, normalised by smallest
    # non-zero pairwise distance, rounded to dist_decimals places.
    sq = (P * P).sum(axis=1)
    D2 = sq[:, None] + sq[None, :] - 2.0 * (P @ P.T)
    iu = np.triu_indices(len(P), k=1)
    d2 = np.sort(D2[iu])
    pos = d2[d2 > 1e-9]
    s_min = float(pos[0])
    d2n = np.round(d2 / s_min, dist_decimals)

    # Edge length multiset, normalised by smallest edge length.
    L = np.array([np.linalg.norm(P[i] - P[j]) for i, j in E])
    L_min = float(L.min())
    L_norm = np.round(L / L_min, edge_decimals)
    edge_ms = tuple(sorted(Counter(L_norm.tolist()).items()))

    # Hash the long distance tuple to keep memory bounded.
    h = hashlib.sha256(d2n.tobytes()).hexdigest()[:16]
    return (len(P), len(E), h, edge_ms)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--corpus-root', default='output/wythoff_sweep')
    ap.add_argument('--cross-polytope', action='store_true',
                    help='also report duplicates that span polytope subfolders')
    args = ap.parse_args()

    root = Path(args.corpus_root)
    files_by_subfolder: dict[str, list[Path]] = defaultdict(list)
    for p in root.glob('*/*.vZome'):
        files_by_subfolder[p.parent.name].append(p)

    total = sum(len(v) for v in files_by_subfolder.values())
    print(f'scanning {total} vZome files in {len(files_by_subfolder)} polytope folders\n')

    all_groups: dict[str, list[tuple[Path, tuple]]] = defaultdict(list)
    per_poly_dups = 0
    per_poly_dup_groups = 0

    for subfolder, files in sorted(files_by_subfolder.items()):
        groups: dict[tuple, list[Path]] = defaultdict(list)
        for f in sorted(files):
            P, E = parse_vzome(f)
            fp = shape_fingerprint(P, E)
            groups[fp].append(f)
            if args.cross_polytope:
                all_groups[fp].append((f, fp))

        dup_groups = [g for g in groups.values() if len(g) > 1]
        if not dup_groups:
            continue
        n_extra = sum(len(g) - 1 for g in dup_groups)
        per_poly_dups += n_extra
        per_poly_dup_groups += len(dup_groups)
        print(f'[{subfolder}] {len(files)} files -> '
              f'{len(groups)} distinct shapes '
              f'({n_extra} duplicates in {len(dup_groups)} groups)')
        for g in sorted(dup_groups, key=lambda g: g[0].name):
            print(f'  group of {len(g)}:')
            for p in g:
                print(f'    {p.name}')

    print(f'\n=== summary ===')
    print(f'within-polytope duplicate groups: {per_poly_dup_groups}')
    print(f'within-polytope extra files:      {per_poly_dups}')
    print(f'unique shapes (within-polytope):  {total - per_poly_dups}')

    if args.cross_polytope:
        cross_groups = [g for g in all_groups.values()
                        if len({p[0].parent.name for p in g}) > 1]
        if cross_groups:
            print(f'\n--- cross-polytope duplicates ---')
            for g in cross_groups:
                print(f'  shape shared by {len(g)} polytopes:')
                for p, _ in g:
                    print(f'    {p.parent.name}/{p.name}')
        else:
            print('\nno cross-polytope duplicates detected')


if __name__ == '__main__':
    main()
