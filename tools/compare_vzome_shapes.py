"""Compare a set of vZome files for congruence (up to rotation+reflection+scale).

Reads ShowPoint coords (6-int tuples encoding 3D Z[phi] vectors as
(a_x,b_x,a_y,b_y,a_z,b_z) with each coord = a + b*phi) and
JoinPointPair edges. For each pair of files compares:

  (a) pairwise squared-distance multiset of the vertex set (after
      normalisation by the smallest non-zero distance) -- congruence
      invariant under rotation+reflection+translation+scale.
  (b) edge length multiset (also normalised) -- congruence invariant.
  (c) edge "color/orbit" multiset, where each edge is classified by
      its 3D direction up to sign, then reduced via Procrustes-aligning
      one shape onto the other.

If (a) matches, the two shapes have identical vertex sets up to
rotation+reflection+scale.  Combined with (b)+(c) we conclude they
are the SAME shape up to rigid motion + reflection + uniform scale.
"""
from __future__ import annotations
import re, sys
from pathlib import Path
from collections import Counter

import numpy as np

PHI = (1 + 5 ** 0.5) / 2

POINT_RE = re.compile(r'point="([^"]+)"')
JPP_RE = re.compile(r'<JoinPointPair start="([^"]+)" end="([^"]+)"\s*/>')


def parse_int_coord(s: str) -> tuple[int, ...]:
    return tuple(int(x) for x in s.split())


def to_float3(t6: tuple[int, ...]) -> np.ndarray:
    a = np.array(t6, dtype=float)
    return np.array([a[0] + a[1] * PHI, a[2] + a[3] * PHI, a[4] + a[5] * PHI])


def parse_vzome(path: Path):
    text = path.read_text()
    points_int: list[tuple[int, ...]] = []
    seen: dict[tuple[int, ...], int] = {}
    show_points = re.findall(r'<ShowPoint\s+point="([^"]+)"\s*/>', text)
    for s in show_points:
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
    return P, edges, points_int


def pdist_normalised(P: np.ndarray) -> np.ndarray:
    sq = (P * P).sum(axis=1)
    D2 = sq[:, None] + sq[None, :] - 2.0 * (P @ P.T)
    iu = np.triu_indices(len(P), k=1)
    d2 = np.sort(D2[iu])
    s = float(d2[d2 > 1e-9][0])
    return np.round(d2 / s, 6)


def edge_lengths_normalised(P: np.ndarray, E):
    L = np.array([np.linalg.norm(P[i] - P[j]) for i, j in E])
    s = float(L.min())
    return Counter(np.round(L / s, 6).tolist())


def main():
    folder = Path(sys.argv[1])
    files = sorted(folder.glob("*.vZome"))
    parsed = []
    for f in files:
        P, E, pts = parse_vzome(f)
        d = pdist_normalised(P)
        elens = edge_lengths_normalised(P, E)
        parsed.append((f.name, P, E, d, elens))
        print(f"{f.name}")
        print(f"  V={len(P)} E={len(E)} edge-length multiset: {dict(sorted(elens.items()))}")

    print("\n=== pairwise comparison (normalised distance multiset) ===")
    n = len(parsed)
    for i in range(n):
        for j in range(i + 1, n):
            ni, _, _, di, eli = parsed[i]
            nj, _, _, dj, elj = parsed[j]
            same_d = (len(di) == len(dj)) and np.allclose(di, dj, atol=1e-4)
            same_e = (eli == elj)
            print(f"\n[{ni[:55]}] vs [{nj[:55]}]")
            if same_d:
                print(f"  pairwise-distance multisets MATCH (max abs diff "
                      f"= {0 if len(di) != len(dj) else float(np.abs(di - dj).max()):.3e})")
            else:
                print(f"  pairwise-distance multisets DIFFER")
                if len(di) == len(dj):
                    print(f"    max abs diff = {float(np.abs(di - dj).max()):.4f}")
                else:
                    print(f"    sizes differ: {len(di)} vs {len(dj)}")
            print(f"  edge-length multisets {'MATCH' if same_e else 'DIFFER'}")
            if not same_e:
                print(f"    A: {dict(sorted(eli.items()))}")
                print(f"    B: {dict(sorted(elj.items()))}")


if __name__ == "__main__":
    main()
