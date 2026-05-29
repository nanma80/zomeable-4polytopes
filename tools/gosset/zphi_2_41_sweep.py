"""Raw-column Z[phi]^3 sweep for 2_41.

The 2_41 polytope has 2160 vertices and 69120 edges.  In the integral
coordinates used here, all vertices have norm^2 = 16 and all edges have
length^2 = 8.  Its edge directions form an E8 root system:

  type A:  +/-2 e_i +/-2 e_j
  type B:  (+/-1, ..., +/-1) with an odd number of minus signs

This is the opposite spinor parity from the 4_21 helper, so this script runs a
direct parity-correct sweep instead of reusing 4_21 rows blindly.
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


def build_2_41_vertices() -> np.ndarray:
    verts: set[tuple[int, ...]] = set()

    # All permutations of (+/-4, 0^7).
    for i in range(8):
        for s in (4, -4):
            v = [0] * 8
            v[i] = s
            verts.add(tuple(v))

    # All permutations of (+/-2, +/-2, +/-2, +/-2, 0^4).
    for inds in itertools.combinations(range(8), 4):
        for signs in itertools.product((2, -2), repeat=4):
            v = [0] * 8
            for i, s in zip(inds, signs):
                v[i] = s
            verts.add(tuple(v))

    # All permutations and even sign changes of (3, 1, 1, 1, 1, 1, 1, 1).
    for pos3 in range(8):
        for signs in itertools.product((1, -1), repeat=8):
            if sum(1 for s in signs if s < 0) % 2 == 0:
                v = [(3 if i == pos3 else 1) * s for i, s in enumerate(signs)]
                verts.add(tuple(v))

    V = np.asarray(sorted(verts), dtype=float)
    assert V.shape == (2160, 8)
    norms2 = np.sum(V * V, axis=1)
    assert np.allclose(norms2, 16.0)
    return V - V.mean(axis=0)


def build_2_41_edges(V: np.ndarray) -> np.ndarray:
    edges = []
    for i in range(len(V)):
        d2 = np.sum((V[i + 1:] - V[i]) ** 2, axis=1)
        for off in np.where(np.abs(d2 - 8.0) < 1e-9)[0]:
            edges.append((i, i + 1 + int(off)))
    assert len(edges) == 69120
    return np.asarray(edges, dtype=np.int32)


def odd_half_roots_ok(chosen: list[col.ZV]) -> bool:
    """Check the odd-parity spinor root sums. Multiplying by 2 preserves direction."""
    for signs in itertools.product((1, -1), repeat=8):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            continue
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
        "source_edges": 69120,
        "cov_eigs": [float(x) for x in ev],
        "rank_singular_values": [float(x) for x in sv],
    }


def progress_summary(R: int, t0: float, stats: Counter, hits: dict) -> dict:
    elapsed_s = time.time() - t0
    top_total = ((2 * R + 1) ** 2) ** 3
    top_seen = min(stats["depth0"], top_total)
    progress = top_seen / top_total if top_total else 0.0
    top_rate = top_seen / elapsed_s if elapsed_s > 0 else 0.0
    leaf_rate = stats["leaf"] / elapsed_s if elapsed_s > 0 else 0.0
    eta_s = (top_total - top_seen) / top_rate if top_seen >= 100 and top_rate > 0 else None
    return {
        "elapsed_s": elapsed_s,
        "top_level_seen": top_seen,
        "top_level_total": top_total,
        "progress_fraction": progress,
        "progress_percent": 100.0 * progress,
        "top_level_per_s": top_rate,
        "leaf_per_s": leaf_rate,
        "eta_s": eta_s,
        "eta_note": None if eta_s is not None else "waiting for at least 100 top-level branches",
        "hit_count": len(hits),
    }


def format_seconds(seconds: float | None) -> str:
    if seconds is None:
        return "unknown"
    seconds = max(0, int(seconds))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, sec = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h {minutes}m"
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {sec}s"
    return f"{sec}s"


def write_checkpoint(
    out_dir: Path,
    R: int,
    status: str,
    t0: float,
    stats: Counter,
    hits: dict,
    phase: str | None = None,
):
    out_dir.mkdir(parents=True, exist_ok=True)
    progress = progress_summary(R, t0, stats, hits)
    if phase is not None:
        progress["phase"] = phase
    payload = {
        "polytope": "2_41",
        "description": "2_41 / E8 uniform polytope with odd-spinor E8 edge roots",
        "R": R,
        "status": status,
        "phase": phase,
        "elapsed_s": time.time() - t0,
        "progress": progress,
        "stats": dict(stats),
        "hits": hits,
    }
    text = json.dumps(payload, indent=2)
    suffixes = ["progress.json"] if status == "running" else ["json", "progress.json"]
    for suffix in suffixes:
        out_file = out_dir / f"column_sweep_2_41_R{R}.{suffix}"
        tmp_file = out_file.with_suffix(out_file.suffix + ".tmp")
        tmp_file.write_text(text, encoding="utf-8")
        tmp_file.replace(out_file)
    return payload


def dfs_sweep(
    R: int,
    out_dir: Path,
    max_seconds: float | None = None,
    progress_seconds: float = 60.0,
    checkpoint_seconds: float = 300.0,
):
    V = build_2_41_vertices()
    print(f"2_41 column sweep R={R}")
    print(f"  vertices={len(V)} edges=69120 columns={((2 * R + 1) ** 2) ** 3:,}")
    cols = col.make_columns(R, include_zero=True)
    t0 = time.time()
    hits = {}
    cheap_seen = {}
    stats = Counter()
    write_checkpoint(out_dir, R, "running", t0, stats, hits, phase="building_adjacency")
    adj = col.build_adjacency(cols, R)
    deg = [m.bit_count() for m in adj]
    print(
        f"  adjacency built in {time.time()-t0:.1f}s; "
        f"degree min/median/mean/max={min(deg)}/{sorted(deg)[len(deg)//2]}/"
        f"{sum(deg)/len(deg):.2f}/{max(deg)}",
        flush=True,
    )
    write_checkpoint(out_dir, R, "running", t0, stats, hits, phase="dfs")

    n = len(cols)
    ge_masks = [col.mask_ge(n, i) for i in range(n)]
    all_mask = (1 << n) - 1
    grams = [col.outer_gram(c) for c in cols]
    last = time.time()
    last_checkpoint = time.time()

    def dfs(depth, start, mask, chosen_idx, g):
        nonlocal last, last_checkpoint
        if max_seconds is not None and time.time() - t0 > max_seconds:
            raise TimeoutError
        if depth == 8:
            stats["leaf"] += 1
            if col.gram_is_orthographic(g):
                stats["gram_hits"] += 1
                chosen = [cols[i] for i in chosen_idx]
                if not odd_half_roots_ok(chosen):
                    stats["half_fail"] += 1
                    return
                stats["half_hits"] += 1
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
            if now - last > progress_seconds:
                progress = progress_summary(R, t0, stats, hits)
                print(
                    f"  dfs elapsed={format_seconds(progress['elapsed_s'])} "
                    f"eta~{format_seconds(progress['eta_s'])} "
                    f"top={progress['top_level_seen']:,}/{progress['top_level_total']:,} "
                    f"({progress['progress_percent']:.3f}%) depth={depth} "
                    f"leaf={stats['leaf']:,} ({progress['leaf_per_s']:.0f}/s) "
                    f"gram={stats['gram_hits']:,} half={stats['half_hits']:,} hits={len(hits)}",
                    flush=True,
                )
                last = now
            if now - last_checkpoint > checkpoint_seconds:
                write_checkpoint(out_dir, R, "running", t0, stats, hits, phase="dfs")
                last_checkpoint = now
            dfs(depth + 1, j, mask & adj[j] & ge_masks[j], chosen_idx + [j], col.gram_add(g, grams[j]))

    try:
        dfs(0, 0, all_mask, [], col.ZERO_GRAM)
        status = "complete"
    except TimeoutError:
        status = "timeout"

    payload = write_checkpoint(out_dir, R, status, t0, stats, hits, phase=status)
    print(json.dumps({
        "status": status,
        "elapsed_s": payload["elapsed_s"],
        "progress": payload["progress"],
        "stats": payload["stats"],
        "hit_count": len(hits),
        "hit_sigs": sorted(hits),
    }, indent=2))
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, required=True)
    ap.add_argument("--out_dir", default="ongoing_work/gosset_2_41")
    ap.add_argument("--max_seconds", type=float, default=None)
    ap.add_argument("--progress_seconds", type=float, default=60.0)
    ap.add_argument("--checkpoint_seconds", type=float, default=300.0)
    args = ap.parse_args()
    dfs_sweep(
        args.R,
        ROOT / args.out_dir,
        args.max_seconds,
        args.progress_seconds,
        args.checkpoint_seconds,
    )


if __name__ == "__main__":
    main()
