"""Raw-column Z[phi]^3 sweep for 1_21, the 5-demicube.

1_21 is the 5-dimensional demicube: the 16 vertices of {+/-1/2}^5
with even parity.  Its edge directions are +/-e_i +/-e_j, so the same
column-compatibility condition used for the Gosset raw-column sweep applies:

    c_i + c_j and c_i - c_j must be zome-axis/zero.

There are no E8 half-root constraints for this standalone 5D polytope.
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


def build_1_21():
    verts = []
    for signs in itertools.product((1, -1), repeat=5):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            verts.append(np.array(signs, dtype=float) / 2.0)
    V = np.asarray(verts, dtype=float)
    E = []
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            if abs(np.sum((V[i] - V[j]) ** 2) - 2.0) < 1e-9:
                E.append((i, j))
    return V - V.mean(axis=0), np.asarray(E, dtype=np.int32)


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
        "edge_count": int(len(E)),
        "cov_eigs": [float(x) for x in ev],
    }


def dfs_sweep(R: int, out_dir: Path, max_seconds: float | None = None):
    V, E = build_1_21()
    cols = col.make_columns(R, include_zero=True)
    print(f"1_21 column sweep R={R}")
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
        "polytope": "1_21",
        "description": "5-demicube",
        "R": R,
        "status": status,
        "elapsed_s": time.time() - t0,
        "stats": stats,
        "hits": hits,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"column_sweep_1_21_R{R}.json"
    out_file.write_text(json.dumps(payload, indent=2))
    print(json.dumps({
        "status": status,
        "elapsed_s": payload["elapsed_s"],
        "stats": stats,
        "hit_count": len(hits),
    }, indent=2))
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, required=True)
    ap.add_argument("--out_dir", default="ongoing_work/gosset_1_21")
    ap.add_argument("--max_seconds", type=float, default=None)
    args = ap.parse_args()
    dfs_sweep(args.R, ROOT / args.out_dir, args.max_seconds)


if __name__ == "__main__":
    main()
