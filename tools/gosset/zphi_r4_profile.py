"""Memory-safe rough R=4 column-sweep profile.

This does NOT build the full adjacency bitset list used by zphi_column_sweep.
For R=4 that representation is expected to require too much memory.  Instead
we generate compatible neighbors on demand from the finite zome-axis difference
set and run a Knuth-style random-path estimator over the same nondecreasing
8-column DFS tree.

The goal is only a rough ETA/order-of-magnitude estimate for deciding whether a
full R=4 sweep is worth engineering, not a proof-grade count.
"""
from __future__ import annotations

import argparse
import functools
import importlib.util
import json
import math
import random
import statistics
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("col", Path(__file__).resolve().parent / "zphi_column_sweep.py")
col = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(col)


def mean_stderr(vals):
    if not vals:
        return 0.0, 0.0
    mean = sum(vals) / len(vals)
    if len(vals) == 1:
        return mean, 0.0
    return mean, statistics.pstdev(vals) / math.sqrt(len(vals))


def quantile(vals, q):
    if not vals:
        return 0
    xs = sorted(vals)
    i = min(len(xs) - 1, max(0, int(round(q * (len(xs) - 1)))))
    return xs[i]


class Enc:
    def __init__(self, R: int):
        self.R = R
        self.q = 2 * R + 1
        self.m = self.q * self.q
        self.N = self.m ** 3
        self.DR = 2 * R
        self.dq = 4 * R + 1
        self.dm = self.dq * self.dq

    def pair_id(self, a: int, b: int) -> int:
        return (a + self.R) * self.q + (b + self.R)

    def col_id_from_coeffs(self, c: tuple[int, int, int, int, int, int]) -> int:
        x = self.pair_id(c[0], c[1])
        y = self.pair_id(c[2], c[3])
        z = self.pair_id(c[4], c[5])
        return (x * self.m + y) * self.m + z

    def col_coeffs(self, idx: int) -> tuple[int, int, int, int, int, int]:
        z = idx % self.m
        idx //= self.m
        y = idx % self.m
        x = idx // self.m
        xa, xb = divmod(x, self.q)
        ya, yb = divmod(y, self.q)
        za, zb = divmod(z, self.q)
        return (
            xa - self.R, xb - self.R,
            ya - self.R, yb - self.R,
            za - self.R, zb - self.R,
        )

    def d_pair_id(self, a: int, b: int) -> int:
        return (a + self.DR) * self.dq + (b + self.DR)

    def d_id_from_coeffs(self, c: tuple[int, int, int, int, int, int]) -> int:
        x = self.d_pair_id(c[0], c[1])
        y = self.d_pair_id(c[2], c[3])
        z = self.d_pair_id(c[4], c[5])
        return (x * self.dm + y) * self.dm + z

    def in_col_range(self, c) -> bool:
        R = self.R
        return all(-R <= x <= R for x in c)

    def in_d_range(self, c) -> bool:
        R = self.DR
        return all(-R <= x <= R for x in c)


def build_axis_d_ids(R: int, enc: Enc):
    t0 = time.time()
    axes = col.axis_set(2 * R)
    ids = set()
    coeffs = []
    for v in axes:
        c = (v[0][0], v[0][1], v[1][0], v[1][1], v[2][0], v[2][1])
        ids.add(enc.d_id_from_coeffs(c))
        coeffs.append(c)
    return coeffs, ids, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, default=4)
    ap.add_argument("--seconds", type=float, default=12 * 3600)
    ap.add_argument("--seed", type=int, default=20260525)
    ap.add_argument("--out", default="ongoing_work/zphi_column_sweep_R4_profile.json")
    ap.add_argument("--log", default="ongoing_work/zphi_column_sweep_R4_profile.log")
    ap.add_argument("--sample_batch", type=int, default=2000)
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

    enc = Enc(args.R)
    log(f"R={args.R}; columns N={enc.N:,}; building axis difference set")
    d_coeffs, d_ids, axis_s = build_axis_d_ids(args.R, enc)
    log(f"axis D size={len(d_coeffs):,}; build_s={axis_s:.1f}")

    @functools.lru_cache(maxsize=200_000)
    def neighbors(idx: int) -> tuple[int, ...]:
        c = enc.col_coeffs(idx)
        out = []
        for s in d_coeffs:
            d = (
                s[0] - c[0], s[1] - c[1],
                s[2] - c[2], s[3] - c[3],
                s[4] - c[4], s[5] - c[5],
            )
            if not enc.in_col_range(d):
                continue
            # Need c - d = 2c - s also to be axis/zero.
            e = (
                2 * c[0] - s[0], 2 * c[1] - s[1],
                2 * c[2] - s[2], 2 * c[3] - s[3],
                2 * c[4] - s[4], 2 * c[5] - s[5],
            )
            if enc.d_id_from_coeffs(e) not in d_ids:
                continue
            out.append(enc.col_id_from_coeffs(d))
        out.sort()
        return tuple(out)

    def sample_path() -> int:
        """Knuth estimator for nondecreasing compatible 8-tuples."""
        root = rng.randrange(enc.N)
        weight = enc.N
        current = tuple(j for j in neighbors(root) if j >= root)
        for _depth in range(1, 8):
            b = len(current)
            if b == 0:
                return 0
            weight *= b
            j = current[rng.randrange(b)]
            nj = neighbors(j)
            # Intersect current with neighbors(j), enforcing nondecreasing.
            # Both sorted; do a linear merge.
            nxt = []
            a = bidx = 0
            while a < len(current) and bidx < len(nj):
                x = current[a]
                y = nj[bidx]
                if x < j:
                    a += 1
                elif y < j:
                    bidx += 1
                elif x == y:
                    nxt.append(x)
                    a += 1
                    bidx += 1
                elif x < y:
                    a += 1
                else:
                    bidx += 1
            current = tuple(nxt)
        return weight

    # A quick degree sample to sanity-check graph sparsity.
    deg_samples = []
    for _ in range(2000):
        deg_samples.append(len(neighbors(rng.randrange(enc.N))))
    log(
        "degree sample n=2000 "
        f"min/median/mean/q99/max={min(deg_samples)}/"
        f"{quantile(deg_samples,0.5)}/{sum(deg_samples)/len(deg_samples):.3f}/"
        f"{quantile(deg_samples,0.99)}/{max(deg_samples)}"
    )

    samples = []
    last = time.time()
    while time.time() - t0 < args.seconds:
        for _ in range(args.sample_batch):
            samples.append(sample_path())
        if time.time() - last > 60:
            write_snapshot(out_path, args, t0, enc, len(d_coeffs), deg_samples, samples, neighbors)
            mean, se = mean_stderr(samples)
            log(
                f"samples={len(samples):,} nonzero={sum(1 for v in samples if v):,} "
                f"mean={mean:.3e} stderr={se:.3e} q99={quantile(samples,0.99):.3e} "
                f"max={max(samples):.3e} cache={neighbors.cache_info()}"
            )
            last = time.time()

    write_snapshot(out_path, args, t0, enc, len(d_coeffs), deg_samples, samples, neighbors, complete=True)
    log("done")


def write_snapshot(out_path, args, t0, enc, axis_d_size, deg_samples, samples, neighbors, complete=False):
    mean, se = mean_stderr(samples)
    payload = {
        "R": args.R,
        "status": "complete" if complete else "running",
        "elapsed_s": time.time() - t0,
        "n_columns": enc.N,
        "axis_d_size": axis_d_size,
        "degree_sample": {
            "n": len(deg_samples),
            "min": min(deg_samples) if deg_samples else 0,
            "median": quantile(deg_samples, 0.5),
            "mean": sum(deg_samples) / len(deg_samples) if deg_samples else 0,
            "q90": quantile(deg_samples, 0.9),
            "q99": quantile(deg_samples, 0.99),
            "max": max(deg_samples) if deg_samples else 0,
        },
        "path_samples": {
            "n": len(samples),
            "nonzero": sum(1 for v in samples if v),
            "mean_leaf_estimate": mean,
            "stderr": se,
            "q50": quantile(samples, 0.5),
            "q90": quantile(samples, 0.9),
            "q99": quantile(samples, 0.99),
            "max": max(samples) if samples else 0,
        },
        "cache_info": str(neighbors.cache_info()),
        "warning": "Heavy-tailed Knuth estimator; use as rough order-of-magnitude only.",
    }
    out_path.write_text(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
