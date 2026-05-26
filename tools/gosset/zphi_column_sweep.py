"""Range-bounded raw-column Z[phi] sweep for Gosset projections.

This is the column-space complement to zphi_ksparse_brute.py.

Instead of choosing an RREF chart M = [I | A], enumerate the eight raw
columns c_i of a 3 x 8 projection matrix P directly:

    c_i in (Z[phi]^3),  |a|, |b| <= R.

For 4_21, every edge direction is an E_8 root.  Therefore P is zomeable
whenever every projected E_8 root is parallel to a zome axis (or collapses).
The E_8 roots are:

  type A:  +/- e_i +/- e_j              -> c_i +/- c_j
  type B:  (1/2)(+/- e_0 ... +/- e_7)   -> half-sums of the c_i

We first build a sparse compatibility graph on candidate columns using the
type-A constraints.  Then we enumerate compatible 8-column multisets, filter
by exact orthographicity P P^T = c I, and finally test all type-B roots plus
collect 4_21 / all 3_21 vertex-figure / all 2_21 vertex-figure shapes.

This parameterization naturally contains the canonical H_3 projection at R=2:
2*sqrt(2*(2+phi))*P has Z[phi] coefficients bounded by 2.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

PHI = (1 + 5 ** 0.5) / 2

Z = tuple[int, int]          # a + b*phi
ZV = tuple[Z, Z, Z]          # 3-vector over Z[phi]
GRAM = tuple[int, ...]       # 12 ints: six Z[phi] entries


def zadd(x: Z, y: Z) -> Z:
    return (x[0] + y[0], x[1] + y[1])


def zsub(x: Z, y: Z) -> Z:
    return (x[0] - y[0], x[1] - y[1])


def zmul(x: Z, y: Z) -> Z:
    a, b = x
    c, d = y
    return (a * c + b * d, a * d + b * c + b * d)


def zneg(x: Z) -> Z:
    return (-x[0], -x[1])


def zfloat(x: Z) -> float:
    return x[0] + x[1] * PHI


def vadd(u: ZV, v: ZV) -> ZV:
    return (zadd(u[0], v[0]), zadd(u[1], v[1]), zadd(u[2], v[2]))


def vsub(u: ZV, v: ZV) -> ZV:
    return (zsub(u[0], v[0]), zsub(u[1], v[1]), zsub(u[2], v[2]))


def vscale_int(s: int, v: ZV) -> ZV:
    return ((s * v[0][0], s * v[0][1]),
            (s * v[1][0], s * v[1][1]),
            (s * v[2][0], s * v[2][1]))


def vfloat(v: ZV) -> np.ndarray:
    return np.array([zfloat(v[0]), zfloat(v[1]), zfloat(v[2])], dtype=float)


_AXES_NUM = None


def axes_num() -> np.ndarray:
    """Default zome axes in the canonical-P chirality."""
    global _AXES_NUM
    if _AXES_NUM is None:
        from lib import zometool_axes as za

        axes = za.AX_VECS.astype(float)[:, [2, 1, 0]]
        _AXES_NUM = axes / np.linalg.norm(axes, axis=1, keepdims=True)
    return _AXES_NUM


def is_zome_axis(v: ZV, tol: float = 1e-5) -> bool:
    """True iff bounded exact vector is zero or numerically parallel to a zome axis."""
    vf = vfloat(v)
    n = float(np.linalg.norm(vf))
    if n < 1e-12:
        return True
    return float(np.max(np.abs(axes_num() @ (vf / n)))) > 1 - tol


def outer_gram(v: ZV) -> GRAM:
    xx = zmul(v[0], v[0])
    yy = zmul(v[1], v[1])
    zz = zmul(v[2], v[2])
    xy = zmul(v[0], v[1])
    xz = zmul(v[0], v[2])
    yz = zmul(v[1], v[2])
    return (xx[0], xx[1], yy[0], yy[1], zz[0], zz[1],
            xy[0], xy[1], xz[0], xz[1], yz[0], yz[1])


ZERO_GRAM: GRAM = (0,) * 12


def gram_add(g: GRAM, h: GRAM) -> GRAM:
    return tuple(a + b for a, b in zip(g, h))


def gram_is_orthographic(g: GRAM) -> bool:
    xx = g[0:2]
    yy = g[2:4]
    zz = g[4:6]
    xy = g[6:8]
    xz = g[8:10]
    yz = g[10:12]
    return xx == yy == zz and xy == (0, 0) and xz == (0, 0) and yz == (0, 0) and xx != (0, 0)


def gram_scale_float(g: GRAM) -> float:
    return zfloat((g[0], g[1]))


def bit_iter(mask: int):
    while mask:
        lsb = mask & -mask
        yield lsb.bit_length() - 1
        mask ^= lsb


def mask_ge(n: int, i: int) -> int:
    if i <= 0:
        return (1 << n) - 1
    return ((1 << n) - 1) ^ ((1 << i) - 1)


def make_columns(R: int, include_zero: bool = True) -> list[ZV]:
    vals = [(a, b) for a in range(-R, R + 1) for b in range(-R, R + 1)]
    cols: list[ZV] = []
    for x in vals:
        for y in vals:
            for z in vals:
                v = (x, y, z)
                if include_zero or v != ((0, 0), (0, 0), (0, 0)):
                    cols.append(v)
    return cols


def axis_set(max_coeff: int) -> set[ZV]:
    """All bounded Z[phi]^3 vectors parallel to default zome axes.

    Uses numeric classification but only to populate a finite exact set.
    The x<->z swap matches emit_vzome chirality used by canonical H_3.
    """
    vals = [(a, b) for a in range(-max_coeff, max_coeff + 1)
            for b in range(-max_coeff, max_coeff + 1)]
    out: set[ZV] = set()
    for x in vals:
        for y in vals:
            for z in vals:
                v = (x, y, z)
                if is_zome_axis(v):
                    out.add(v)
    return out


def build_adjacency(cols: list[ZV], R: int) -> list[int]:
    """Compatibility graph for c_i +/- c_j zome-axis constraints."""
    col_index = {c: i for i, c in enumerate(cols)}
    axes2 = axis_set(2 * R)
    n = len(cols)
    adj = [0] * n
    t0 = time.time()
    for i, c in enumerate(cols):
        m = 0
        for s in axes2:
            # s = c + d -> d = s - c
            d = vsub(s, c)
            j = col_index.get(d)
            if j is not None and vsub(c, d) in axes2:
                m |= 1 << j
        adj[i] = m
        if i and i % 5000 == 0:
            print(f"  adjacency {i:,}/{n:,} elapsed={time.time() - t0:.1f}s", flush=True)
    return adj


def even_half_roots_ok(chosen: list[ZV]) -> bool:
    """Check all 128 half-root sums.  Multiplying by 2 preserves direction."""
    for signs in itertools.product((1, -1), repeat=8):
        if sum(1 for s in signs if s < 0) % 2:
            continue
        acc = ((0, 0), (0, 0), (0, 0))
        for s, c in zip(signs, chosen):
            acc = vadd(acc, c if s > 0 else vscale_int(-1, c))
        if not is_zome_axis(acc):
            return False
    return True


def matrix_from_columns(chosen: list[ZV], g: GRAM) -> np.ndarray:
    P = np.array([[zfloat(chosen[j][r]) for j in range(8)] for r in range(3)], dtype=float)
    scale = math.sqrt(gram_scale_float(g))
    return P / scale


def shape_sig(V3: np.ndarray, decimals: int = 4) -> str:
    """Scale-invariant, rotation-invariant point-cloud signature."""
    V = np.asarray(V3, dtype=float)
    V = V - V.mean(axis=0)
    # Collapse coincident projected vertices at high precision, but do not use
    # the display/signature precision before scale normalization.
    pts = sorted({tuple(np.round(p, 12)) for p in V})
    arr = np.asarray(pts, dtype=float)
    n = len(arr)
    if n < 2:
        return f"N{n}_empty"
    d = arr[:, None, :] - arr[None, :, :]
    d2 = (d * d).sum(axis=-1)
    vals = d2[np.triu_indices(n, k=1)]
    nz = vals[vals > 1e-10]
    if len(nz) == 0:
        return f"N{n}_deg"
    vals = np.round(vals / float(nz.min()), decimals)
    vals.sort()
    payload = ",".join(f"{x:.{decimals}f}" for x in vals[:512])
    return f"N{n}_" + hashlib.sha1(payload.encode()).hexdigest()[:12]


def local_edges(V: np.ndarray, tol: float = 1e-8) -> np.ndarray:
    edges = []
    n = len(V)
    for i in range(n):
        diff = V - V[i]
        d2 = (diff * diff).sum(axis=1)
        for j in range(i + 1, n):
            if abs(d2[j] - 2.0) < tol:
                edges.append((i, j))
    return np.array(edges, dtype=np.int32)


_EMB_CACHE = {}


def embeddings():
    """All 4_21, 3_21 vertex-figure, and 2_21 vertex-figure embeddings in R^8."""
    if _EMB_CACHE:
        return _EMB_CACHE
    import gosset_polytopes as gp

    V4 = np.asarray(gp.V_421, dtype=float)
    E4 = np.asarray(gp.E_421, dtype=np.int32)
    _EMB_CACHE["4_21"] = [(V4 - V4.mean(axis=0), E4, "4_21_full")]

    emb3 = []
    emb2 = []
    for i, v0 in enumerate(V4):
        d2 = ((V4 - v0) ** 2).sum(axis=1)
        idx3 = np.where(np.abs(d2 - 2.0) < 1e-9)[0]
        W = V4[idx3] - v0
        E3 = local_edges(W)
        emb3.append((W - W.mean(axis=0), E3, f"vf_{i}"))

        for j_local, w0 in enumerate(W):
            d2w = ((W - w0) ** 2).sum(axis=1)
            idx2 = np.where(np.abs(d2w - 2.0) < 1e-9)[0]
            X = W[idx2] - w0
            E2 = local_edges(X)
            emb2.append((X - X.mean(axis=0), E2, f"vf_{i}_{j_local}"))
    _EMB_CACHE["3_21"] = emb3
    _EMB_CACHE["2_21"] = emb2
    return _EMB_CACHE


def collect_shapes(P: np.ndarray, max_2_21_embeddings: int | None = None) -> dict:
    """Collect strict-isotropic zomeable shapes from all embeddings.

    Since P has already passed full 4_21 zomeability, subpolytope edges are
    zomeable automatically.  We still enforce strict image isotropy and rank 3.
    """
    out = {"4_21": {}, "3_21": {}, "2_21": {}}
    embs = embeddings()
    for poly in ("4_21", "3_21", "2_21"):
        items = embs[poly]
        if poly == "2_21" and max_2_21_embeddings is not None:
            items = items[:max_2_21_embeddings]
        for V, E, emb_id in items:
            V3 = V @ P.T
            Vc = V3 - V3.mean(axis=0)
            cov = Vc.T @ Vc / max(1, len(V3) - 1)
            ev = np.linalg.eigvalsh(cov)
            if ev[-1] < 1e-12 or ev[0] / ev[-1] < 0.99:
                continue
            sv = np.linalg.svd(Vc, compute_uv=False)
            if len(sv) < 3 or sv[2] < 1e-7:
                continue
            sig = shape_sig(V3)
            if sig not in out[poly]:
                out[poly][sig] = {
                    "N": len({tuple(np.round(p, 4)) for p in V3}),
                    "embedding": emb_id,
                    "edges": int(len(E)),
                }
    return out


def dfs_cliques(cols, grams, adj, out_dir: Path, R: int,
                max_candidates: int | None, max_seconds: float | None,
                checkpoint_every: int = 10000):
    n = len(cols)
    all_mask = (1 << n) - 1
    ge_masks = [mask_ge(n, i) for i in range(n)]
    stats = Counter()
    hits = {"4_21": {}, "3_21": {}, "2_21": {}}
    t0 = time.time()
    last = t0

    def record_candidate(chosen_idx: list[int], g: GRAM):
        stats["gram_hits"] += 1
        chosen = [cols[i] for i in chosen_idx]
        if not even_half_roots_ok(chosen):
            stats["half_fail"] += 1
            return
        stats["half_hits"] += 1
        P = matrix_from_columns(chosen, g)
        shapes = collect_shapes(P)
        for poly, sigs in shapes.items():
            for sig, info in sigs.items():
                if sig not in hits[poly]:
                    info = dict(info)
                    info["columns"] = chosen
                    hits[poly][sig] = info
                    print(f"  HIT {poly} {sig} N={info['N']} emb={info['embedding']}", flush=True)

    def dfs(depth: int, start: int, mask: int, chosen: list[int], g: GRAM):
        nonlocal last
        if max_seconds is not None and time.time() - t0 > max_seconds:
            raise TimeoutError
        if depth == 8:
            stats["leaf"] += 1
            if gram_is_orthographic(g):
                record_candidate(chosen, g)
                if max_candidates is not None and stats["gram_hits"] >= max_candidates:
                    raise StopIteration
            return
        # Need enough distinct-or-repeat options left; bit count is only a loose guard.
        if mask == 0:
            return
        for j in bit_iter(mask & ge_masks[start]):
            stats[f"depth{depth}"] += 1
            now = time.time()
            if now - last > 60:
                print(
                    f"  dfs elapsed={now-t0:.0f}s depth={depth} leaf={stats['leaf']:,} "
                    f"gram={stats['gram_hits']:,} half={stats['half_hits']:,} "
                    f"hits=({len(hits['2_21'])},{len(hits['3_21'])},{len(hits['4_21'])})",
                    flush=True,
                )
                last = now
            new_mask = mask & adj[j] & ge_masks[j]
            dfs(depth + 1, j, new_mask, chosen + [j], gram_add(g, grams[j]))

    try:
        dfs(0, 0, all_mask, [], ZERO_GRAM)
        status = "complete"
    except StopIteration:
        status = "max_candidates"
    except TimeoutError:
        status = "timeout"

    payload = {
        "R": R,
        "status": status,
        "elapsed_s": time.time() - t0,
        "stats": dict(stats),
        "hits": hits,
    }
    out_file = out_dir / f"column_sweep_R{R}.json"
    out_file.write_text(json.dumps(payload, indent=2))
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--R", type=int, required=True)
    p.add_argument("--out_dir", default="ongoing_work/zphi_column_sweep")
    p.add_argument("--max_candidates", type=int, default=None)
    p.add_argument("--max_seconds", type=float, default=None)
    p.add_argument("--skip_dfs", action="store_true")
    args = p.parse_args()

    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Column sweep R={args.R}")
    cols = make_columns(args.R, include_zero=True)
    print(f"  columns: {len(cols):,}")
    t = time.time()
    adj = build_adjacency(cols, args.R)
    deg = [m.bit_count() for m in adj]
    print(
        f"  adjacency built in {time.time()-t:.1f}s; "
        f"degree min/median/mean/max = {min(deg)}/{sorted(deg)[len(deg)//2]}/"
        f"{sum(deg)/len(deg):.2f}/{max(deg)}",
        flush=True,
    )
    if args.skip_dfs:
        return
    grams = [outer_gram(c) for c in cols]
    payload = dfs_cliques(
        cols, grams, adj, out_dir, args.R,
        max_candidates=args.max_candidates,
        max_seconds=args.max_seconds,
    )
    print(json.dumps({
        "status": payload["status"],
        "elapsed_s": payload["elapsed_s"],
        "stats": payload["stats"],
        "hit_counts": {p: len(payload["hits"][p]) for p in payload["hits"]},
    }, indent=2))


if __name__ == "__main__":
    main()
