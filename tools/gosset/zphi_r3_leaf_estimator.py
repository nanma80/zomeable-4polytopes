"""Parallel estimator for total R=3 column-sweep DFS leaves.

The R=3 column sweep's DFS tree is very heavy-tailed.  This estimator runs
beside the main sweep and writes periodic snapshots:

  ongoing_work/zphi_column_sweep_R3_leaf_estimate.json

Estimator design:
  1. Build the same R=3 compatibility graph.
  2. Partition root branches by first-column degree.
  3. Exact-count cheap roots (bounded recursive visits).
  4. Use randomized Knuth path sampling inside each degree stratum.

This is intended as an ETA/order-of-magnitude estimator, not a replacement for
the full sweep.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location("col", Path(__file__).resolve().parent / "zphi_column_sweep.py")
col = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(col)


def bit_iter(mask: int):
    while mask:
        lsb = mask & -mask
        yield lsb.bit_length() - 1
        mask ^= lsb


def quantile(vals, q):
    if not vals:
        return 0
    xs = sorted(vals)
    i = min(len(xs) - 1, max(0, int(round(q * (len(xs) - 1)))))
    return xs[i]


def mean_stderr(vals):
    if not vals:
        return 0.0, 0.0
    m = sum(vals) / len(vals)
    if len(vals) == 1:
        return m, 0.0
    sd = statistics.pstdev(vals)
    return m, sd / math.sqrt(len(vals))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260525)
    ap.add_argument("--seconds", type=float, default=12 * 3600)
    ap.add_argument("--exact_visit_limit", type=int, default=250_000)
    ap.add_argument("--out", default="ongoing_work/zphi_column_sweep_R3_leaf_estimate.json")
    ap.add_argument("--log", default="ongoing_work/zphi_column_sweep_R3_leaf_estimate.log")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    out_path = ROOT / args.out
    log_path = ROOT / args.log
    t0 = time.time()

    def log(msg):
        line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        print(line, flush=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    log(f"building R={args.R} graph")
    cols = col.make_columns(args.R, include_zero=True)
    adj = col.build_adjacency(cols, args.R)
    n = len(cols)
    ge = [col.mask_ge(n, i) for i in range(n)]
    all_mask = (1 << n) - 1
    deg = [m.bit_count() for m in adj]
    log(f"graph built: N={n:,} degree min/median/mean/max={min(deg)}/{sorted(deg)[n//2]}/{sum(deg)/n:.3f}/{max(deg)}")

    # Degree strata.  Keep high-degree branches separate because they dominate
    # the heavy tail.
    strata = {
        "d0": [],
        "d1_4": [],
        "d5_16": [],
        "d17_64": [],
        "d65_256": [],
        "d257_plus": [],
    }
    for i, d in enumerate(deg):
        if d == 0:
            strata["d0"].append(i)
        elif d <= 4:
            strata["d1_4"].append(i)
        elif d <= 16:
            strata["d5_16"].append(i)
        elif d <= 64:
            strata["d17_64"].append(i)
        elif d <= 256:
            strata["d65_256"].append(i)
        else:
            strata["d257_plus"].append(i)
    log("strata sizes: " + json.dumps({k: len(v) for k, v in strata.items()}))

    exact_counts: dict[int, int] = {}
    exact_visits: dict[int, int] = {}
    heavy_roots: set[int] = set()

    def exact_subtree(root: int, visit_limit: int):
        visits = 0
        start_mask = all_mask & adj[root] & ge[root]

        def rec(depth: int, start: int, mask: int) -> int:
            nonlocal visits
            visits += 1
            if visits > visit_limit:
                raise TimeoutError
            if depth == 8:
                return 1
            total = 0
            mm = mask & ge[start]
            while mm:
                lsb = mm & -mm
                j = lsb.bit_length() - 1
                mm ^= lsb
                total += rec(depth + 1, j, mask & adj[j] & ge[j])
            return total

        return rec(1, root, start_mask), visits

    def sample_root(root: int) -> int:
        """Knuth path estimator for one fixed first root."""
        weight = 1
        start = root
        mask = all_mask & adj[root] & ge[root]
        for depth in range(1, 8):
            choices = list(bit_iter(mask & ge[start]))
            b = len(choices)
            if b == 0:
                return 0
            weight *= b
            j = choices[rng.randrange(b)]
            mask = mask & adj[j] & ge[j]
            start = j
        return weight

    # Phase 1: exact-count cheap roots in a deterministic sweep.  This gives
    # a solid lower bound and removes many zeros/small branches from sampling.
    log("phase 1 exact cheap roots")
    roots = list(range(n))
    # Prioritize low degree, but include high-degree roots early to identify
    # heavy branches that hit the exact limit.
    roots.sort(key=lambda i: (deg[i], i))
    last_write = time.time()
    for idx, root in enumerate(roots):
        if time.time() - t0 > min(args.seconds * 0.25, 3600):
            break
        if root in exact_counts or root in heavy_roots:
            continue
        try:
            c, v = exact_subtree(root, args.exact_visit_limit)
            exact_counts[root] = c
            exact_visits[root] = v
        except TimeoutError:
            heavy_roots.add(root)
        if time.time() - last_write > 60:
            write_snapshot(out_path, args, t0, n, deg, strata, exact_counts, exact_visits, heavy_roots, {})
            log(f"exact progress roots={idx+1:,}/{n:,} exact={len(exact_counts):,} heavy={len(heavy_roots):,} exact_sum={sum(exact_counts.values()):,}")
            last_write = time.time()

    # Phase 2: stratified sampling of roots not exact-counted.  We sample the
    # *root subtree count* by picking a random root in the stratum, then one
    # random path inside that root.  Stratum estimate = count(stratum)*mean.
    log("phase 2 stratified sampling")
    samples: dict[str, list[int]] = defaultdict(list)
    # Seed with sampled exact counts too, but only for roots not exact-counted
    # we use Monte-Carlo.  Exact roots are added separately in snapshot.
    while time.time() - t0 < args.seconds:
        for sname, sroots in strata.items():
            remaining = [r for r in sroots if r not in exact_counts]
            if not remaining:
                continue
            # Allocate more samples to heavy strata.
            reps = 1
            if sname in ("d65_256", "d257_plus"):
                reps = 8
            elif sname == "d17_64":
                reps = 4
            for _ in range(reps):
                r = remaining[rng.randrange(len(remaining))]
                samples[sname].append(sample_root(r))
        if time.time() - last_write > 60:
            write_snapshot(out_path, args, t0, n, deg, strata, exact_counts, exact_visits, heavy_roots, samples)
            est = estimate_total(n, strata, exact_counts, samples)
            log(f"sample progress elapsed={time.time()-t0:.0f}s exact={len(exact_counts):,} samples={sum(len(v) for v in samples.values()):,} estimate_mean={est['mean']:.3e} stderr={est['stderr']:.3e} lower_exact={sum(exact_counts.values()):,}")
            last_write = time.time()

    write_snapshot(out_path, args, t0, n, deg, strata, exact_counts, exact_visits, heavy_roots, samples)
    log("done")


def estimate_total(n, strata, exact_counts, samples):
    exact_sum = sum(exact_counts.values())
    exact_by_stratum = defaultdict(int)
    exact_roots_by_stratum = defaultdict(int)
    for sname, roots in strata.items():
        rset = set(roots)
        for r, c in exact_counts.items():
            if r in rset:
                exact_by_stratum[sname] += c
                exact_roots_by_stratum[sname] += 1

    mean = exact_sum
    var = 0.0
    stratum_report = {}
    for sname, roots in strata.items():
        remaining = len(roots) - exact_roots_by_stratum[sname]
        vals = samples.get(sname, [])
        m, se = mean_stderr(vals)
        contrib = remaining * m
        contrib_se = remaining * se
        mean += contrib
        var += contrib_se * contrib_se
        stratum_report[sname] = {
            "roots": len(roots),
            "exact_roots": exact_roots_by_stratum[sname],
            "remaining_roots": remaining,
            "exact_sum": exact_by_stratum[sname],
            "samples": len(vals),
            "sample_mean": m,
            "sample_stderr": se,
            "estimated_remaining": contrib,
            "estimated_remaining_stderr": contrib_se,
            "sample_q50": quantile(vals, 0.5) if vals else 0,
            "sample_q90": quantile(vals, 0.9) if vals else 0,
            "sample_q99": quantile(vals, 0.99) if vals else 0,
            "sample_max": max(vals) if vals else 0,
        }
    return {
        "mean": mean,
        "stderr": math.sqrt(var),
        "exact_lower_bound": exact_sum,
        "strata": stratum_report,
    }


def write_snapshot(out_path, args, t0, n, deg, strata, exact_counts, exact_visits, heavy_roots, samples):
    est = estimate_total(n, strata, exact_counts, samples)
    payload = {
        "R": args.R,
        "status": "running" if time.time() - t0 < args.seconds else "complete",
        "elapsed_s": time.time() - t0,
        "n_columns": n,
        "degree": {
            "min": min(deg),
            "median": sorted(deg)[n // 2],
            "mean": sum(deg) / n,
            "max": max(deg),
        },
        "exact_roots": len(exact_counts),
        "heavy_roots_hit_limit": len(heavy_roots),
        "exact_visit_limit": args.exact_visit_limit,
        "exact_leaf_sum": sum(exact_counts.values()),
        "samples_total": sum(len(v) for v in samples.values()),
        "estimate": est,
    }
    out_path.write_text(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
