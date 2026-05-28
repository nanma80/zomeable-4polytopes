"""Raw-column Z[phi]^3 sweep for the A5 (5-simplex) uniform-polytope family.

The A5 family polytopes live in the 5D hyperplane H = {x in R^6 : sum x_i = c},
perpendicular to 1 = (1,1,1,1,1,1).  The three rectification shapes are:

    5-simplex (t0):      6 verts = permutations of (1,0,0,0,0,0)
    rectified (t1):     15 verts = permutations of (1,1,0,0,0,0)
    birectified (t2):   20 verts = permutations of (1,1,1,0,0,0)

For every A5 uniform polytope the edge directions are exactly the A5 roots
{e_i - e_j}.  A projection P = [c_0 ... c_5] (each c_i in Z[phi]^3) is therefore
zomeable iff every c_i - c_j is parallel to a zome axis (or zero).

Translation gauge: adding a constant vector to every column only translates the
projected image (all vertices share the same coordinate sum), so we fix c_0 = 0.
Then each c_i (= c_i - c_0, an edge image) must be a zome axis, and all pairwise
c_i - c_j must be zome axes.  We therefore choose 5 zome-axis columns c_1..c_5
(plus zero, which permits collapsed edges) whose pairwise differences are all
zome axes.

Strict-orthographic (isotropic-image) condition is polytope-independent: because
W(A5) = S6 acts irreducibly on H, every A5 polytope's centered vertex covariance
is proportional to the projector Pi_H = I_6 - (1/6) J.  Hence

    Cov(image) ~ P Pi_H P^T = sum_i c_i c_i^T - (1/6) s s^T,   s = sum_i c_i,

and the exact integer test (with c_0 = 0, so s = c_1 + ... + c_5) is

    6 * sum_i c_i c_i^T - s s^T = lambda * I_3,   lambda != 0.

A single sweep therefore finds every valid P; the per-polytope emission/dedup is
done separately by zphi_a5_emit.py.  Hits are deduplicated by the triple of
per-polytope shape signatures (rotation- and mirror-invariant).

The anchored-radius cutoff (c_0 = 0, |coeffs of c_i| <= R) is a deliberate,
non-exhaustive bound, matching the other raw-column sweeps in this repo.
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

spec = importlib.util.spec_from_file_location(
    "col", ROOT / "tools" / "gosset" / "zphi_column_sweep.py"
)
col = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(col)

ZERO: col.ZV = ((0, 0), (0, 0), (0, 0))


def build_polytopes():
    """Return {name: (V_centered, edges)} for the three A5 rectifications."""
    polys = {}
    for name, k in (("5_simplex", 1), ("rectified_5_simplex", 2), ("birectified_5_simplex", 3)):
        verts = []
        for combo in itertools.combinations(range(6), k):
            v = np.zeros(6)
            for idx in combo:
                v[idx] = 1.0
            verts.append(v)
        V = np.asarray(verts, dtype=float)
        edges = []
        # Two k-subsets are adjacent iff they share k-1 indices (Hamming-2 on the
        # 0/1 vector); the edge direction is then an A5 root e_a - e_b.
        for i in range(len(V)):
            for j in range(i + 1, len(V)):
                if int(np.sum(np.abs(V[i] - V[j]))) == 2:
                    edges.append((i, j))
        polys[name] = (V - V.mean(axis=0), np.asarray(edges, dtype=np.int32))
    assert len(polys["5_simplex"][0]) == 6
    assert len(polys["rectified_5_simplex"][0]) == 15
    assert len(polys["birectified_5_simplex"][0]) == 20
    return polys


def gram_scale_int(g: col.GRAM, s: int) -> col.GRAM:
    return tuple(s * x for x in g)


def gram_sub(g: col.GRAM, h: col.GRAM) -> col.GRAM:
    return tuple(a - b for a, b in zip(g, h))


def is_isotropic_centered(g_sum: col.GRAM, s_vec: col.ZV) -> bool:
    """Exact test 6 * sum c_i c_i^T - s s^T = lambda I_3 with lambda != 0."""
    m = gram_sub(gram_scale_int(g_sum, 6), col.outer_gram(s_vec))
    return col.gram_is_orthographic(m)


def build_candidates(R: int):
    """Zome-axis Z[phi]^3 vectors within coeff radius R (includes zero)."""
    return sorted(col.axis_set(R))


def build_diff_adjacency(cands, R: int):
    """adj[i] bitmask of j such that cands[i] - cands[j] is a zome axis/zero."""
    idx = {c: i for i, c in enumerate(cands)}
    axes2 = col.axis_set(2 * R)
    n = len(cands)
    adj = [0] * n
    t0 = time.time()
    for i, c in enumerate(cands):
        m = 0
        for s in axes2:
            # want cands[j] with c - cands[j] = s in axes2  ->  cands[j] = c - s
            cand_j = col.vsub(c, s)
            j = idx.get(cand_j)
            if j is not None:
                m |= 1 << j
        adj[i] = m
        if i and i % 2000 == 0:
            print(f"  adjacency {i:,}/{n:,} elapsed={time.time()-t0:.1f}s", flush=True)
    return adj


def matrix_from_columns6(columns6):
    return np.array(
        [[col.zfloat(columns6[j][r]) for j in range(6)] for r in range(3)],
        dtype=float,
    )


def shape_sig_triple(columns6, polys):
    P = matrix_from_columns6(columns6)
    sigs = {}
    for name, (V, _E) in polys.items():
        V3 = V @ P.T
        sigs[name] = {"sig": col.shape_sig(V3), "N": len({tuple(np.round(p, 4)) for p in V3})}
    return sigs


def dfs_sweep(R: int, out_dir: Path, max_seconds: float | None = None,
              checkpoint_every: float = 120.0):
    polys = build_polytopes()
    cands = build_candidates(R)
    print(f"A5 family column sweep R={R}")
    print(f"  zome-axis candidates (incl. zero): {len(cands):,}")
    t0 = time.time()
    adj = build_diff_adjacency(cands, R)
    deg = [m.bit_count() for m in adj]
    print(
        f"  adjacency built in {time.time()-t0:.1f}s; "
        f"degree min/median/mean/max={min(deg)}/{sorted(deg)[len(deg)//2]}/"
        f"{sum(deg)/len(deg):.2f}/{max(deg)}",
        flush=True,
    )

    n = len(cands)
    ge_masks = [col.mask_ge(n, i) for i in range(n)]
    all_mask = (1 << n) - 1
    grams = [col.outer_gram(c) for c in cands]
    hits = {}
    stats = {"leaf": 0, "ortho_hits": 0}
    last = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    progress_file = out_dir / f"progress_a5_R{R}.json"

    def write_progress(status: str):
        progress_file.write_text(json.dumps({
            "polytope_family": "A5",
            "R": R,
            "status": status,
            "elapsed_s": time.time() - t0,
            "stats": dict(stats),
            "hit_count": len(hits),
        }, indent=2), encoding="utf-8")

    def dfs(depth, start, mask, chosen_idx, g_sum, s_vec):
        nonlocal last
        if max_seconds is not None and time.time() - t0 > max_seconds:
            raise TimeoutError
        if depth == 5:
            stats["leaf"] += 1
            if is_isotropic_centered(g_sum, s_vec):
                stats["ortho_hits"] += 1
                columns6 = [ZERO] + [cands[i] for i in chosen_idx]
                sigs = shape_sig_triple(columns6, polys)
                key = "|".join(sigs[n2]["sig"] for n2 in
                               ("5_simplex", "rectified_5_simplex", "birectified_5_simplex"))
                if key not in hits:
                    hits[key] = {
                        "columns": columns6,
                        "shapes": sigs,
                    }
                    print(f"  HIT {key}  "
                          f"N=({sigs['5_simplex']['N']},{sigs['rectified_5_simplex']['N']},"
                          f"{sigs['birectified_5_simplex']['N']})", flush=True)
            return
        mm = mask & ge_masks[start]
        while mm:
            lsb = mm & -mm
            j = lsb.bit_length() - 1
            mm ^= lsb
            now = time.time()
            if now - last > checkpoint_every:
                print(
                    f"  dfs elapsed={now-t0:.0f}s depth={depth} leaf={stats['leaf']:,} "
                    f"ortho={stats['ortho_hits']:,} hits={len(hits)}",
                    flush=True,
                )
                write_progress("running")
                last = now
            dfs(depth + 1, j, mask & adj[j] & ge_masks[j], chosen_idx + [j],
                col.gram_add(g_sum, grams[j]), col.vadd(s_vec, cands[j]))

    try:
        dfs(0, 0, all_mask, [], col.ZERO_GRAM, ZERO)
        status = "complete"
    except TimeoutError:
        status = "timeout"

    payload = {
        "polytope_family": "A5",
        "description": "A5 / 5-simplex family: t0 (6), t1 rectified (15), t2 birectified (20)",
        "R": R,
        "status": status,
        "elapsed_s": time.time() - t0,
        "candidates": len(cands),
        "stats": stats,
        "hits": hits,
    }
    out_file = out_dir / f"column_sweep_a5_R{R}.json"
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_progress(status)
    print(json.dumps({
        "status": status,
        "elapsed_s": payload["elapsed_s"],
        "stats": stats,
        "hit_count": len(hits),
        "hit_keys": sorted(hits),
    }, indent=2))
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, required=True)
    ap.add_argument("--out_dir", default="ongoing_work/a5")
    ap.add_argument("--max_seconds", type=float, default=None)
    args = ap.parse_args()
    dfs_sweep(args.R, ROOT / args.out_dir, args.max_seconds)


if __name__ == "__main__":
    main()
