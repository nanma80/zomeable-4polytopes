"""Raw-column Z[phi]^3 sweep for the 1_42 Gosset polytope.

The 1_42 polytope has 17280 vertices and 483840 edges.  In the integral
coordinates used here, all vertices have norm^2 = 32 and all edges have
length^2 = 8.  Its unoriented edge directions are:

  type A:  +/-2 e_i +/-2 e_j
  type B:  (+/-1, ..., +/-1), with both sign parities

This is stricter than the E8-root polytopes that use only one spinor parity.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
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


def build_1_42_vertices() -> np.ndarray:
    verts: set[tuple[int, ...]] = set()

    # All permutations and sign changes of (4, 2, 2, 2, 2, 0, 0, 0).
    for zero_inds in itertools.combinations(range(8), 3):
        nonzero = [i for i in range(8) if i not in zero_inds]
        for pos4 in nonzero:
            pos2 = [i for i in nonzero if i != pos4]
            for signs in itertools.product((1, -1), repeat=5):
                v = [0] * 8
                v[pos4] = 4 * signs[0]
                for i, s in zip(pos2, signs[1:]):
                    v[i] = 2 * s
                verts.add(tuple(v))

    # Half of the sign combinations for the remaining three coordinate orbits.
    for base in ([2] * 8, [5] + [1] * 7, [3, 3, 3] + [1] * 5):
        for perm in set(itertools.permutations(base)):
            for signs in itertools.product((1, -1), repeat=8):
                if sum(1 for s in signs if s < 0) % 2 == 0:
                    verts.add(tuple(a * s for a, s in zip(perm, signs)))

    V = np.asarray(sorted(verts), dtype=float)
    assert V.shape == (17280, 8)
    norms2 = np.sum(V * V, axis=1)
    assert np.allclose(norms2, 32.0)
    return V - V.mean(axis=0)


def all_spinor_roots_ok(chosen: list[col.ZV]) -> bool:
    """Check all (+/-1)^8 spinor-root sums.  Multiplying roots preserves direction."""
    for signs in itertools.product((1, -1), repeat=8):
        acc = ((0, 0), (0, 0), (0, 0))
        for s, c in zip(signs, chosen):
            acc = col.vadd(acc, c if s > 0 else col.vscale_int(-1, c))
        if not col.is_zome_axis(acc):
            return False
    return True


def matrix_from_columns(chosen: list[col.ZV], g: col.GRAM) -> np.ndarray:
    return col.matrix_from_columns(chosen, g)


def cheap_point_signature(V3: np.ndarray) -> tuple[int, str]:
    V = np.asarray(V3, dtype=float)
    V = V - V.mean(axis=0)
    pts = sorted({tuple(np.round(p, 10)) for p in V})
    arr = np.asarray(pts, dtype=float)
    r2 = np.round(np.sum(arr * arr, axis=1), 8)
    r2.sort()
    payload = ",".join(f"{x:.8f}" for x in r2)
    return len(arr), hashlib.sha1(payload.encode()).hexdigest()[:16]


def collect_shape(chosen, g, V, cheap_seen):
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

    cheap_sig = cheap_point_signature(V3)
    if cheap_sig in cheap_seen:
        return None
    sig = col.shape_sig(V3)
    cheap_seen[cheap_sig] = sig
    return {
        "sig": sig,
        "N": cheap_sig[0],
        "cheap_sig": list(cheap_sig),
        "columns": chosen,
        "source_edges": 483840,
        "cov_eigs": [float(x) for x in ev],
        "rank_singular_values": [float(x) for x in sv],
    }


def write_checkpoint(out_dir: Path, R: int, status: str, elapsed_s: float, stats, hits):
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "polytope": "1_42",
        "description": "1_42 / E8 uniform polytope with both spinor parities as edge roots",
        "R": R,
        "status": status,
        "elapsed_s": elapsed_s,
        "stats": dict(stats),
        "hits": hits,
    }
    suffix = "json" if status != "running" else "progress.json"
    out_file = out_dir / f"column_sweep_1_42_R{R}.{suffix}"
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def dfs_sweep(R: int, out_dir: Path, max_seconds: float | None = None):
    V = build_1_42_vertices()
    print(f"1_42 column sweep R={R}")
    print(f"  vertices={len(V)} edges=483840 columns={((2 * R + 1) ** 2) ** 3:,}")
    cols = col.make_columns(R, include_zero=True)
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
    cheap_seen = {}
    stats = Counter()
    last = time.time()

    def dfs(depth, start, mask, chosen_idx, g):
        nonlocal last
        if max_seconds is not None and time.time() - t0 > max_seconds:
            raise TimeoutError
        if depth == 8:
            stats["leaf"] += 1
            if col.gram_is_orthographic(g):
                stats["gram_hits"] += 1
                chosen = [cols[i] for i in chosen_idx]
                if not all_spinor_roots_ok(chosen):
                    stats["spinor_fail"] += 1
                    return
                stats["spinor_hits"] += 1
                info = collect_shape(chosen, g, V, cheap_seen)
                if info and info["sig"] not in hits:
                    hits[info["sig"]] = info
                    print(f"  HIT {info['sig']} N={info['N']}", flush=True)
            return
        if mask == 0:
            return
        for j in col.bit_iter(mask & ge_masks[start]):
            stats[f"depth{depth}"] += 1
            now = time.time()
            if now - last > 60:
                print(
                    f"  dfs elapsed={now-t0:.0f}s depth={depth} leaf={stats['leaf']:,} "
                    f"gram={stats['gram_hits']:,} spinor={stats['spinor_hits']:,} "
                    f"hits={len(hits)}",
                    flush=True,
                )
                write_checkpoint(out_dir, R, "running", now - t0, stats, hits)
                last = now
            dfs(depth + 1, j, mask & adj[j] & ge_masks[j], chosen_idx + [j], col.gram_add(g, grams[j]))

    try:
        dfs(0, 0, all_mask, [], col.ZERO_GRAM)
        status = "complete"
    except TimeoutError:
        status = "timeout"

    payload = write_checkpoint(out_dir, R, status, time.time() - t0, stats, hits)
    print(json.dumps({
        "status": status,
        "elapsed_s": payload["elapsed_s"],
        "stats": payload["stats"],
        "hit_count": len(hits),
        "hit_sigs": sorted(hits),
    }, indent=2))
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, required=True)
    ap.add_argument("--out_dir", default="ongoing_work/gosset_1_42")
    ap.add_argument("--max_seconds", type=float, default=None)
    args = ap.parse_args()
    dfs_sweep(args.R, ROOT / args.out_dir, args.max_seconds)


if __name__ == "__main__":
    main()
