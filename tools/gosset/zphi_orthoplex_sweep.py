"""Bounded raw-column Z[phi]^3 sweep for n-orthoplexes.

The n-orthoplex has vertices +/-e_i.  Its edge directions are the D_n roots
+/-e_i +/- e_j, so a projection with columns c_i is zomeable exactly when
c_i + c_j and c_i - c_j are zome axes or zero for every pair i,j.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from collections import Counter
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

from search_engine import _classify_dir  # noqa: E402


def build_orthoplex(n: int):
    verts = []
    labels = []
    for i in range(n):
        for s in (1, -1):
            v = np.zeros(n)
            v[i] = s
            verts.append(v)
            labels.append((i, s))
    V = np.asarray(verts, dtype=float)

    edges = []
    edge_dirs = set()
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            if labels[i][0] == labels[j][0]:
                continue
            edges.append((i, j))
            d = V[j] - V[i]
            edge_dirs.add(min(tuple(d), tuple(-d)))

    dn_dirs = set()
    for i in range(n):
        for j in range(i + 1, n):
            for si in (1, -1):
                for sj in (1, -1):
                    d = np.zeros(n)
                    d[i] = si
                    d[j] = sj
                    dn_dirs.add(min(tuple(d), tuple(-d)))

    assert len(V) == 2 * n
    assert len(edges) == 2 * n * (n - 1)
    assert edge_dirs == dn_dirs
    return V - V.mean(axis=0), np.asarray(edges, dtype=np.int32)


def matrix_from_columns(chosen, g):
    n = len(chosen)
    P = np.array([[col.zfloat(chosen[j][r]) for j in range(n)] for r in range(3)], dtype=float)
    return P / np.sqrt(col.gram_scale_float(g))


def project_and_edges(chosen, g, V, E):
    P = matrix_from_columns(chosen, g)
    V3 = V @ P.T
    keys = {}
    pts = []
    v2p = []
    for p in V3:
        k = tuple(np.round(p, 10))
        if k not in keys:
            keys[k] = len(pts)
            pts.append(p)
        v2p.append(keys[k])
    edge_set = set()
    collapsed = 0
    for i, j in E:
        a, b = v2p[i], v2p[j]
        if a == b:
            collapsed += 1
        else:
            edge_set.add((min(a, b), max(a, b)))
    return V3, np.asarray(pts), sorted(edge_set), collapsed


def edge_color_counts(pts, edge_set):
    counts = Counter()
    for a, b in edge_set:
        d = pts[b] - pts[a]
        n = float(np.linalg.norm(d))
        c = "_" if n < 1e-12 else _classify_dir(d / n, tol=1e-5)
        if c is not None:
            counts[c] += 1
    return dict(sorted(counts.items()))


def collect_shape(chosen, g, V, E):
    P = matrix_from_columns(chosen, g)
    V3 = V @ P.T
    Vc = V3 - V3.mean(axis=0)
    cov = Vc.T @ Vc / max(1, len(V3) - 1)
    ev = np.linalg.eigvalsh(cov)
    if ev[-1] < 1e-12 or ev[0] / ev[-1] < 0.999999:
        return None
    sv = np.linalg.svd(Vc, compute_uv=False)
    if len(sv) < 3 or sv[2] < 1e-7:
        return None
    V3, pts, edge_set, collapsed = project_and_edges(chosen, g, V, E)
    return {
        "sig": col.shape_sig(V3, decimals=5),
        "N": int(len(pts)),
        "columns": chosen,
        "source_edges": int(len(E)),
        "visible_edges": int(len(edge_set)),
        "collapsed_edges": int(collapsed),
        "colors": edge_color_counts(pts, edge_set),
        "cov_eigs": [float(x) for x in ev],
        "singular_values": [float(x) for x in sv],
    }


def write_progress(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def dfs_sweep(n: int, label: str, R: int, out_dir: Path, max_seconds: float | None = None):
    V, E = build_orthoplex(n)
    cols = col.make_columns(R, include_zero=True)
    print(f"{label} / {n}-orthoplex column sweep R={R}")
    print(f"  vertices={len(V)} edges={len(E)} columns={len(cols):,}", flush=True)
    t0 = time.time()
    adj = col.build_adjacency(cols, R)
    deg = [m.bit_count() for m in adj]
    print(
        f"  adjacency built in {time.time()-t0:.1f}s; "
        f"degree min/median/mean/max={min(deg)}/{sorted(deg)[len(deg)//2]}/"
        f"{sum(deg)/len(deg):.2f}/{max(deg)}",
        flush=True,
    )

    ncols = len(cols)
    ge_masks = [col.mask_ge(ncols, i) for i in range(ncols)]
    all_mask = (1 << ncols) - 1
    grams = [col.outer_gram(c) for c in cols]
    hits = {}
    stats = {"leaf": 0, "gram_hits": 0, "rank_hits": 0}
    last = time.time()
    progress_path = out_dir / f"column_sweep_{label}_R{R}.progress.json"

    def progress(status="running", depth=None, top_index=None):
        write_progress(progress_path, {
            "polytope": label,
            "orthoplex_dimension": n,
            "R": R,
            "status": status,
            "elapsed_s": time.time() - t0,
            "depth": depth,
            "top_index": top_index,
            "stats": stats,
            "hit_count": len(hits),
        })

    def dfs(depth, start, mask, chosen_idx, g):
        nonlocal last
        if max_seconds is not None and time.time() - t0 > max_seconds:
            raise TimeoutError
        if depth == n:
            stats["leaf"] += 1
            if col.gram_is_orthographic(g):
                stats["gram_hits"] += 1
                chosen = [cols[i] for i in chosen_idx]
                info = collect_shape(chosen, g, V, E)
                if info:
                    stats["rank_hits"] += 1
                    if info["sig"] not in hits:
                        hits[info["sig"]] = info
                        print(
                            f"  HIT {len(hits)} {info['sig']} N={info['N']} "
                            f"edges={info['visible_edges']} colors={info['colors']}",
                            flush=True,
                        )
            return
        mm = mask & ge_masks[start]
        while mm:
            lsb = mm & -mm
            j = lsb.bit_length() - 1
            mm ^= lsb
            now = time.time()
            if now - last > 30:
                print(
                    f"  dfs elapsed={now-t0:.0f}s depth={depth} leaf={stats['leaf']:,} "
                    f"gram={stats['gram_hits']:,} rank={stats['rank_hits']:,} hits={len(hits)}",
                    flush=True,
                )
                progress(depth=depth, top_index=chosen_idx[0] if chosen_idx else j)
                last = now
            dfs(depth + 1, j, mask & adj[j] & ge_masks[j], chosen_idx + [j], col.gram_add(g, grams[j]))

    try:
        progress()
        dfs(0, 0, all_mask, [], col.ZERO_GRAM)
        status = "complete"
    except TimeoutError:
        status = "timeout"

    payload = {
        "polytope": label,
        "description": f"{n}-orthoplex; vertices +/-e_i; D{n} edge directions",
        "orthoplex_dimension": n,
        "R": R,
        "status": status,
        "elapsed_s": time.time() - t0,
        "stats": stats,
        "hits": hits,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"column_sweep_{label}_R{R}.json"
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    progress(status=status)
    print(json.dumps({
        "status": status,
        "elapsed_s": payload["elapsed_s"],
        "stats": stats,
        "hit_count": len(hits),
        "out_file": str(out_file),
    }, indent=2), flush=True)
    return payload


def default_label(n: int) -> str:
    known = {5: "2_11", 6: "3_11", 7: "4_11", 10: "7_11"}
    return known.get(n, f"{n}-orthoplex")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--R", type=int, required=True)
    ap.add_argument("--label", default=None)
    ap.add_argument("--out_dir", default="ongoing_work/gosset_orthoplex_dn")
    ap.add_argument("--max_seconds", type=float, default=None)
    args = ap.parse_args()
    dfs_sweep(args.n, args.label or default_label(args.n), args.R, ROOT / args.out_dir, args.max_seconds)


if __name__ == "__main__":
    main()
