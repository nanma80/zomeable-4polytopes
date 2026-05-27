"""Raw-column Z[phi]^3 sweep for 2_11, the regular 5-orthoplex.

The 5-orthoplex has vertices +/-e_i in R^5. Its edge directions are the D5
roots +/-e_i +/- e_j, so the same column-compatibility condition used for
1_21 and t1 2_11 applies:

    c_i + c_j and c_i - c_j must be zome-axis/zero.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

spec = importlib.util.spec_from_file_location(
    "col", Path(__file__).resolve().parent / "zphi_column_sweep.py"
)
col = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(col)


def build_2_11():
    verts = []
    for i in range(5):
        for s in (1, -1):
            v = np.zeros(5)
            v[i] = s
            verts.append(v)
    V = np.asarray(verts, dtype=float)

    edges = []
    edge_dirs = set()
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            if abs(float(np.dot(V[i], V[j]))) < 1e-9:
                edges.append((i, j))
                d = V[j] - V[i]
                edge_dirs.add(min(tuple(d), tuple(-d)))

    d5_dirs = set()
    for i in range(5):
        for j in range(i + 1, 5):
            for si in (1, -1):
                for sj in (1, -1):
                    d = np.zeros(5)
                    d[i] = si
                    d[j] = sj
                    d5_dirs.add(min(tuple(d), tuple(-d)))

    assert len(V) == 10
    assert len(edges) == 40
    assert edge_dirs == d5_dirs
    return V - V.mean(axis=0), np.asarray(edges, dtype=np.int32)


def matrix_from_columns(chosen, g):
    P = np.array([[col.zfloat(chosen[j][r]) for j in range(5)] for r in range(3)], dtype=float)
    scale = np.sqrt(col.gram_scale_float(g))
    return P / scale


def collect_shape(chosen, g, V, E):
    P = matrix_from_columns(chosen, g)
    V3 = V @ P.T
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
        "columns": chosen,
        "source_edges": int(len(E)),
        "cov_eigs": [float(x) for x in ev],
        "rank_singular_values": [float(x) for x in sv],
    }


def dfs_sweep(R: int, out_dir: Path, max_seconds: float | None = None):
    V, E = build_2_11()
    cols = col.make_columns(R, include_zero=True)
    print(f"2_11 column sweep R={R}")
    print(f"  vertices={len(V)} edges={len(E)} columns={len(cols):,}")
    t0 = time.time()
    adj = col.build_adjacency(cols, R)
    deg = [m.bit_count() for m in adj]
    print(
        f"  adjacency built in {time.time()-t0:.1f}s; "
        f"degree min/median/mean/max={min(deg)}/{sorted(deg)[len(deg)//2]}/"
        f"{sum(deg)/len(deg):.2f}/{max(deg)}",
        flush=True,
    )

    n = len(cols)
    ge_masks = [col.mask_ge(n, i) for i in range(n)]
    all_mask = (1 << n) - 1
    grams = [col.outer_gram(c) for c in cols]
    hits = {}
    stats = {"leaf": 0, "gram_hits": 0}
    last = time.time()

    def dfs(depth, start, mask, chosen_idx, g):
        nonlocal last
        if max_seconds is not None and time.time() - t0 > max_seconds:
            raise TimeoutError
        if depth == 5:
            stats["leaf"] += 1
            if col.gram_is_orthographic(g):
                stats["gram_hits"] += 1
                chosen = [cols[i] for i in chosen_idx]
                info = collect_shape(chosen, g, V, E)
                if info and info["sig"] not in hits:
                    hits[info["sig"]] = info
                    print(f"  HIT {info['sig']} N={info['N']}", flush=True)
            return
        mm = mask & ge_masks[start]
        while mm:
            lsb = mm & -mm
            j = lsb.bit_length() - 1
            mm ^= lsb
            now = time.time()
            if now - last > 60:
                print(
                    f"  dfs elapsed={now-t0:.0f}s depth={depth} leaf={stats['leaf']:,} "
                    f"gram={stats['gram_hits']:,} hits={len(hits)}",
                    flush=True,
                )
                last = now
            dfs(depth + 1, j, mask & adj[j] & ge_masks[j], chosen_idx + [j], col.gram_add(g, grams[j]))

    try:
        dfs(0, 0, all_mask, [], col.ZERO_GRAM)
        status = "complete"
    except TimeoutError:
        status = "timeout"

    payload = {
        "polytope": "2_11",
        "description": "regular 5-orthoplex / pentacross",
        "R": R,
        "status": status,
        "elapsed_s": time.time() - t0,
        "stats": stats,
        "hits": hits,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"column_sweep_2_11_R{R}.json"
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": status,
        "elapsed_s": payload["elapsed_s"],
        "stats": stats,
        "hit_count": len(hits),
        "hit_sigs": sorted(hits),
    }, indent=2))
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, required=True)
    ap.add_argument("--out_dir", default="ongoing_work/gosset_2_11")
    ap.add_argument("--max_seconds", type=float, default=None)
    args = ap.parse_args()
    dfs_sweep(args.R, ROOT / args.out_dir, args.max_seconds)


if __name__ == "__main__":
    main()
