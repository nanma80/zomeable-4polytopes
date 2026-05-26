"""Raw-column Z[phi]^3 sweep for 2_31, the E7 root polytope.

2_31 is a 7-dimensional E7 uniform/root polytope with 126 vertices and
2016 edges.  We realize its vertices as the E8 roots orthogonal to one E8
root u=(1,1,0,0,0,0,0,0).

Every projection of this E7 subspace has a unique representative whose rows
annihilate u, so the first two columns obey

    c_1 = -c_0.

The remaining six columns have +/- pair constraints.  We enumerate those six
columns as a multiset, use an exact Gram-signature lookup to find compatible
c_0 values, then check the 32 half-root constraints.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

spec = importlib.util.spec_from_file_location("col", Path(__file__).resolve().parent / "zphi_column_sweep.py")
col = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(col)


def build_e8_roots():
    roots = []
    for i in range(8):
        for j in range(i + 1, 8):
            for si in (1, -1):
                for sj in (1, -1):
                    v = np.zeros(8)
                    v[i] = si
                    v[j] = sj
                    roots.append(v)
    for signs in itertools.product((1, -1), repeat=8):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            roots.append(np.array(signs, dtype=float) / 2)
    return np.asarray(roots)


def build_e7_roots():
    E8 = build_e8_roots()
    u = np.array([1, 1, 0, 0, 0, 0, 0, 0], dtype=float)
    mask = np.abs(E8 @ u) < 1e-9
    R = E8[mask]
    assert R.shape == (126, 8)
    assert np.linalg.matrix_rank(R) == 7
    return R


def edge_count(V):
    return sum(
        1 for i in range(len(V)) for j in range(i + 1, len(V))
        if abs(float(np.dot(V[i], V[j])) - 1.0) < 1e-9
    )


def constraints_from_roots(R):
    pair_constraints = {}
    half_signs = []
    c0_axis = False
    for r in R:
        nz = np.where(np.abs(r) > 1e-9)[0]
        if len(nz) == 2:
            i, j = map(int, nz)
            si, sj = int(round(r[i])), int(round(r[j]))
            if si < 0:
                si, sj = -si, -sj
            if (i, j) == (0, 1):
                c0_axis = True
            else:
                pair_constraints.setdefault((i, j), set()).add((si, sj))
        elif len(nz) == 8:
            signs = tuple(int(round(2 * x)) for x in r)
            if signs[0] < 0:
                signs = tuple(-x for x in signs)
            if signs not in half_signs:
                half_signs.append(signs)
        else:
            raise ValueError(r)
    assert c0_axis
    return pair_constraints, half_signs


def half_ok(chosen, half_signs):
    for signs in half_signs:
        acc = ((0, 0), (0, 0), (0, 0))
        for s, c in zip(signs, chosen):
            acc = col.vadd(acc, c if s > 0 else col.vscale_int(-1, c))
        if not col.is_zome_axis(acc):
            return False
    return True


def gram_signature_for_c0(c):
    """Signature of 2*outer(c) relevant to making H + 2*outer(c) orthographic."""
    g = col.outer_gram(c)
    xx = g[0:2]
    yy = g[2:4]
    zz = g[4:6]
    xy = g[6:8]
    xz = g[8:10]
    yz = g[10:12]

    def z2(p):
        return (2 * p[0], 2 * p[1])

    return (
        *z2(xy), *z2(xz), *z2(yz),
        2 * (xx[0] - yy[0]), 2 * (xx[1] - yy[1]),
        2 * (xx[0] - zz[0]), 2 * (xx[1] - zz[1]),
    )


def needed_c0_signature(H):
    xx = H[0:2]
    yy = H[2:4]
    zz = H[4:6]
    xy = H[6:8]
    xz = H[8:10]
    yz = H[10:12]
    return (
        -xy[0], -xy[1], -xz[0], -xz[1], -yz[0], -yz[1],
        -(xx[0] - yy[0]), -(xx[1] - yy[1]),
        -(xx[0] - zz[0]), -(xx[1] - zz[1]),
    )


def scaled_gram(k, g):
    return tuple(k * x for x in g)


def matrix_from_columns(chosen, g):
    P = np.array([[col.zfloat(chosen[j][r]) for j in range(8)] for r in range(3)], dtype=float)
    scale = np.sqrt(col.gram_scale_float(g))
    return P / scale


def strict_iso_shape(R, chosen, g):
    P = matrix_from_columns(chosen, g)
    V3 = R @ P.T
    Vc = V3 - V3.mean(axis=0)
    cov = Vc.T @ Vc / max(1, len(V3) - 1)
    ev = np.linalg.eigvalsh(cov)
    if ev[-1] < 1e-12 or ev[0] / ev[-1] < 0.99:
        return None
    sv = np.linalg.svd(Vc, compute_uv=False)
    if len(sv) < 3 or sv[2] < 1e-7:
        return None
    return {
        "sig": col.shape_sig(V3),
        "N": len({tuple(np.round(p, 4)) for p in V3}),
        "cov_eigs": [float(x) for x in ev],
    }


def sweep(Rmax: int, out_dir: Path, max_seconds: float | None = None):
    roots = build_e7_roots()
    pairs, half_signs = constraints_from_roots(roots)
    print(f"2_31/E7 root sweep R={Rmax}")
    print(f"  vertices={len(roots)} edges={edge_count(roots)} pair_constraints={sum(len(v) for v in pairs.values())} half_constraints={len(half_signs)}")
    cols = col.make_columns(Rmax, include_zero=True)
    print(f"  columns={len(cols):,}")
    t_build = time.time()
    adj = col.build_adjacency(cols, Rmax)
    deg = [m.bit_count() for m in adj]
    print(
        f"  adjacency built in {time.time()-t_build:.1f}s; "
        f"degree min/median/mean/max={min(deg)}/{sorted(deg)[len(deg)//2]}/"
        f"{sum(deg)/len(deg):.2f}/{max(deg)}",
        flush=True,
    )

    grams = [col.outer_gram(c) for c in cols]
    c0_by_sig = {}
    for c in cols:
        # E7 has the root e0-e1, so c0 must itself point along a zome axis
        # (zero is allowed, corresponding to collapse).
        if col.is_zome_axis(c):
            c0_by_sig.setdefault(gram_signature_for_c0(c), []).append(c)
    n = len(cols)
    ge_masks = [col.mask_ge(n, i) for i in range(n)]
    all_mask = (1 << n) - 1
    stats = {f"depth{k}": 0 for k in range(8)}
    stats.update({"leaf": 0, "gram_hits": 0, "half_hits": 0, "half_fail": 0, "c0_candidates": 0})
    hits = {}
    t0 = time.time()
    last = t0

    def dfs(depth, start, mask, chosen_tail, H):
        nonlocal last
        if max_seconds is not None and time.time() - t0 > max_seconds:
            raise TimeoutError
        if depth == 6:
            stats["leaf"] += 1
            sig = needed_c0_signature(H)
            c0s = c0_by_sig.get(sig, [])
            if not c0s:
                return
            stats["c0_candidates"] += len(c0s)
            for c0 in c0s:
                c0g = scaled_gram(2, col.outer_gram(c0))
                g = col.gram_add(H, c0g)
                if not col.gram_is_orthographic(g):
                    continue
                stats["gram_hits"] += 1
                neg_c0 = col.vscale_int(-1, c0)
                chosen = [c0, neg_c0] + chosen_tail
                if not half_ok(chosen, half_signs):
                    stats["half_fail"] += 1
                    continue
                stats["half_hits"] += 1
                info = strict_iso_shape(roots, chosen, g)
                if info and info["sig"] not in hits:
                    info["columns"] = chosen
                    hits[info["sig"]] = info
                    print(f"  HIT {info['sig']} N={info['N']}", flush=True)
            return
        mm = mask & ge_masks[start]
        while mm:
            lsb = mm & -mm
            idx = lsb.bit_length() - 1
            mm ^= lsb
            c = cols[idx]
            stats[f"depth{depth}"] += 1
            now = time.time()
            if now - last > 60:
                print(
                    f"  dfs elapsed={now-t0:.0f}s depth={depth} leaf={stats['leaf']:,} "
                    f"c0={stats['c0_candidates']:,} gram={stats['gram_hits']:,} "
                    f"half={stats['half_hits']:,} hits={len(hits)}",
                    flush=True,
                )
                last = now
            dfs(depth + 1, idx, mask & adj[idx] & ge_masks[idx], chosen_tail + [c], col.gram_add(H, grams[idx]))

    try:
        dfs(0, 0, all_mask, [], col.ZERO_GRAM)
        status = "complete"
    except TimeoutError:
        status = "timeout"

    payload = {
        "polytope": "2_31",
        "description": "E7 root polytope",
        "R": Rmax,
        "status": status,
        "elapsed_s": time.time() - t0,
        "stats": stats,
        "hits": hits,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"column_sweep_2_31_R{Rmax}.json"
    out_file.write_text(json.dumps(payload, indent=2))
    print(json.dumps({
        "status": status,
        "elapsed_s": payload["elapsed_s"],
        "stats": stats,
        "hit_count": len(hits),
    }, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, required=True)
    ap.add_argument("--out_dir", default="ongoing_work/gosset_2_31")
    ap.add_argument("--max_seconds", type=float, default=None)
    args = ap.parse_args()
    sweep(args.R, ROOT / args.out_dir, args.max_seconds)


if __name__ == "__main__":
    main()
