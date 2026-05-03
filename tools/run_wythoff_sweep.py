"""Run the Wythoff sweep over all 47 convex uniform 4-polytopes.

Strategy (rep-theoretic shortcut):
  For each Coxeter group G in {A4, B4, F4, H4}, the zomeable kernel
  directions of any G-Wythoff polytope must lie among those of the
  regular G-polytope (the bitmask 1000 form), as shown empirically for
  the regular cases.  So we:

  1. Find the working kernels for each regular polytope at the chosen
     coefficient range.
  2. For every (group, bitmask), test only those kernels against the
     polytope's vertex/edge data.
  3. Group hits by shape fingerprint.
  4. Print the census.

Usage:
    python tools/run_wythoff_sweep.py [--rng N] [--group A4|B4|F4|H4]

Resuming:
  Step-1 kernels are cached at ongoing_work/kernels_<group>_rng<N>.npy
  (delete the .npy file to force recomputation, e.g. after lib changes).
  Step-2 entries are read from any ongoing_work/sweep_log_*.txt file
  in the repo and skipped on re-run.

  Output for this run is written to
  ongoing_work/sweep_log_rng<N>_<group>.txt (or _all.txt if no --group).
"""
import sys
import os
import re
import time
import glob
import json
import hashlib
import argparse

# Allow running as a module or directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

import numpy as np

from wythoff import build_polytope
from uniform_polytopes import all_uniform_polytopes, KNOWN_DUPLICATES
from search_engine import gen_dirs, search, group_by_shape


GROUPS = ("A4", "B4", "F4", "H4")
REGULAR_BITMASK = (1, 0, 0, 0)

# ongoing_work/ relative to repo root (parent of tools/)
ONGOING = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "ongoing_work"))


def kernel_cache_path(group, rng):
    return os.path.join(ONGOING, f"kernels_{group}_rng{rng}.npy")


def find_group_kernels(group, rng, cache=True):
    """Return a list of kernel ndarrays for the regular polytope of
    `group` at coefficient range `rng`.

    Reads from ongoing_work/kernels_<group>_rng<N>.npy if present;
    otherwise runs the search and writes the cache."""
    path = kernel_cache_path(group, rng)
    if cache and os.path.exists(path):
        arr = np.load(path)
        rel = os.path.relpath(path)
        print(f"  [{group}] loaded {len(arr)} cached kernels from {rel}")
        return [arr[i] for i in range(len(arr))]
    V, E = build_polytope(group, REGULAR_BITMASK)
    dirs = gen_dirs(rng=rng, integer_only=False, permute_dedup=False)
    print(f"  [{group}] regular: |V|={len(V)}, |E|={len(E)}, "
          f"trying {len(dirs)} dirs...")
    t0 = time.time()
    hits = search(group + "_regular", V, E, dirs, verbose=False)
    kernels = [np.array(n) for (n, sig, balls) in hits]
    print(f"  [{group}] {len(kernels)} hits in {time.time()-t0:.1f}s")
    if cache and kernels:
        os.makedirs(ONGOING, exist_ok=True)
        np.save(path, np.array(kernels))
        print(f"  [{group}] cached to {os.path.relpath(path)}")
    return kernels


def test_polytope_against_kernels(group, bitmask, name, kernels):
    """For each kernel in `kernels`, test whether projecting
    `(group, bitmask)` produces a zomeable image.  Returns
    (V, E, hits, shape_groups)."""
    V, E = build_polytope(group, bitmask)
    hits = search(name, V, E, kernels, verbose=False)
    groups = group_by_shape(hits, V, E)
    return V, E, hits, groups


# Threshold above which a shape's full pairwise-distance tuple is too
# bulky to dump (n_balls choose 2 floats per shape).  For shapes larger
# than this we still dump n_balls + a stable hash of the fingerprint, so
# the shape can be cross-referenced on inspection.
_MAX_DUMP_BALLS = 500


def _hash_fingerprint(fp):
    """Stable SHA-256 hex digest of a (n_balls, distance_tuple)
    fingerprint, robust across Python's randomized hash()."""
    n_balls, dists = fp
    payload = repr((int(n_balls), tuple(round(float(d), 6) for d in dists)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def dump_shape_record(path, group, bitmask, name, V, E, n_hits,
                      n_kernels_tested, shape_groups):
    """Append a single JSON record describing this polytope's shapes."""
    shapes = []
    for fp, examples in shape_groups.items():
        n_balls, dists = fp
        n0, sig0, balls0 = examples[0]
        rec = {
            "n_balls": int(n_balls),
            "fp_hash": _hash_fingerprint(fp),
            "n_kernels": len(examples),
            "example_kernel": [float(x) for x in n0],
            "example_sig": {k: int(v) for k, v in sig0.items()},
            "example_balls": int(balls0),
        }
        if n_balls <= _MAX_DUMP_BALLS:
            rec["distances"] = [float(d) for d in dists]
        shapes.append(rec)
    record = {
        "group": group,
        "bitmask": list(bitmask),
        "name": name,
        "V": int(len(V)),
        "E": int(len(E)),
        "n_kernels_tested": int(n_kernels_tested),
        "n_hits": int(n_hits),
        "shapes": shapes,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


# Match a successful step-2 result line, e.g.
#   "  A4 (1, 0, 0, 0)  5-cell        V=    5 E=   10  hits= 324  shapes=4  (3.6s)"
_DONE_RE = re.compile(
    r"^\s+(A4|B4|F4|H4)\s+\((\d),\s*(\d),\s*(\d),\s*(\d)\)\s+.*"
    r"shapes=\d+\s+\([\d.]+s\)\s*$"
)


def parse_done_set(log_paths):
    """Scan `log_paths` (list of file paths) and return a set of
    (group, bitmask) for step-2 entries that completed successfully."""
    done = set()
    for path in log_paths:
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                m = _DONE_RE.match(line.rstrip("\n"))
                if m:
                    g = m.group(1)
                    b = tuple(int(m.group(i)) for i in (2, 3, 4, 5))
                    done.add((g, b))
    return done


class _Tee:
    """Mirror writes to a file and the original stdout."""
    def __init__(self, path, original):
        self.f = open(path, "a", encoding="utf-8", buffering=1)
        self.orig = original

    def write(self, s):
        self.f.write(s)
        self.orig.write(s)

    def flush(self):
        self.f.flush()
        self.orig.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rng", type=int, default=3,
                    help="kernel-direction range for the regular-polytope search")
    ap.add_argument("--group", choices=GROUPS, default=None,
                    help="run only this Coxeter group (default: all four)")
    ap.add_argument("--no-cache", action="store_true",
                    help="don't read or write the step-1 kernel cache")
    ap.add_argument("--force", action="store_true",
                    help="ignore prior-log done_set and re-test every "
                         "selected polytope (useful for backfilling the "
                         "shapes JSONL after the sweep)")
    ap.add_argument("--sort-by-size", action="store_true",
                    help="iterate step 2 by polytope vertex count ascending "
                         "(useful for graceful degradation on H4 where the "
                         "omnitruncated 120-cell is much larger than the rest)")
    ap.add_argument("--no-dump-shapes", action="store_true",
                    help="don't append per-polytope shape records to the "
                         "ongoing_work/shapes_rng<N>.jsonl shape dump")
    ap.add_argument("--shapes-jsonl", default=None,
                    help="path for the JSONL shape dump "
                         "(default: ongoing_work/shapes_rng<N>.jsonl)")
    ap.add_argument("--log", default=None,
                    help="output log path (default: "
                         "ongoing_work/sweep_log_rng<N>_<group>.txt)")
    args = ap.parse_args()

    groups_to_run = [args.group] if args.group else list(GROUPS)
    suffix = args.group if args.group else "all"
    log_path = args.log or os.path.join(
        ONGOING, f"sweep_log_rng{args.rng}_{suffix}.txt")
    shapes_jsonl_path = (args.shapes_jsonl or
                         os.path.join(ONGOING, f"shapes_rng{args.rng}.jsonl"))
    os.makedirs(ONGOING, exist_ok=True)

    # Detect already-completed polytopes from any prior log in ongoing_work/
    prior_logs = sorted(glob.glob(os.path.join(ONGOING, "sweep_log_*.txt")))
    done_set = set() if args.force else parse_done_set(prior_logs)

    sys.stdout = _Tee(log_path, sys.__stdout__)
    print(f"# run_wythoff_sweep --rng {args.rng} "
          f"--group {args.group or 'all'}")
    print(f"# log: {os.path.relpath(log_path)}")
    if not args.no_dump_shapes:
        print(f"# shapes dump: {os.path.relpath(shapes_jsonl_path)}")
    if done_set:
        print(f"# {len(done_set)} polytopes already done in prior logs; "
              f"will skip those")
    print()

    # 1. Find kernels for each regular polytope (cached).
    print("=" * 70)
    print("Step 1: kernels of regular polytopes")
    print("=" * 70)
    group_kernels = {}
    for g in groups_to_run:
        group_kernels[g] = find_group_kernels(
            g, args.rng, cache=not args.no_cache)
    print()

    # 2. Test all Wythoff combos for the selected groups.
    print("=" * 70)
    print("Step 2: test each Wythoff combo against group kernels")
    print("=" * 70)

    # Collect work items, optionally sorted by polytope V count.
    work = [(g, b, n) for (g, b, n) in all_uniform_polytopes()
            if g in groups_to_run]
    if args.sort_by_size:
        sized = []
        for g, b, n in work:
            if (g, b) in KNOWN_DUPLICATES or (g, b) in done_set:
                # Place skips/dups at the front (cheap to handle).
                sized.append((-1, g, b, n))
                continue
            try:
                Vp, _ = build_polytope(g, b)
                sized.append((len(Vp), g, b, n))
            except Exception:
                sized.append((10**9, g, b, n))
        sized.sort(key=lambda t: t[0])
        work = [(g, b, n) for (_, g, b, n) in sized]
        print(f"# step-2 iteration order (sort-by-size):")
        for g, b, n in work:
            print(f"#   {g} {b}  {n}")
        print()

    results = []
    for group, b, name in work:
        if (group, b) in KNOWN_DUPLICATES:
            tgt = KNOWN_DUPLICATES[(group, b)]
            print(f"  {group} {b}  {name:30s}  [DUP of {tgt}]")
            results.append((group, b, name, "DUP", None, None, None))
            continue
        if (group, b) in done_set:
            print(f"  {group} {b}  {name:30s}  [SKIP: in prior log]")
            continue
        kernels = group_kernels[group]
        t0 = time.time()
        try:
            V, E, hits, shape_groups = test_polytope_against_kernels(
                group, b, name, kernels)
        except RuntimeError as e:
            print(f"  {group} {b}  {name:30s}  ERR: {e}")
            results.append((group, b, name, f"ERR: {e}", None, None, None))
            continue
        dt = time.time() - t0
        print(f"  {group} {b}  {name:30s}  V={len(V):5d} E={len(E):5d}  "
              f"hits={len(hits):4d}  shapes={len(shape_groups)}  ({dt:.1f}s)")
        if not args.no_dump_shapes:
            try:
                dump_shape_record(shapes_jsonl_path, group, b, name, V, E,
                                  len(hits), len(kernels), shape_groups)
            except Exception as e:
                print(f"  WARN: shape dump failed for {group} {b}: {e}")
        results.append((group, b, name, len(V), len(E), len(hits),
                        shape_groups))

    # 3. Census of *this run* (use parse_done_set across all logs for
    #    a global census).
    print()
    print("=" * 70)
    print("Step 3: census (this run only)")
    print("=" * 70)
    print(f"{'group':4s} {'bitmask':10s} {'name':30s} {'V':>5s} {'E':>5s} "
          f"{'hits':>5s} {'shapes':>7s}")
    total_shapes = 0
    for r in results:
        group, b, name = r[:3]
        if r[3] == "DUP":
            print(f"  {group} {str(b):10s} {name:30s}  [DUP]")
            continue
        if isinstance(r[3], str):
            print(f"  {group} {str(b):10s} {name:30s}  {r[3]}")
            continue
        _, _, _, V_n, E_n, hit_n, sg = r
        print(f"  {group} {str(b):10s} {name:30s} {V_n:5d} {E_n:5d} "
              f"{hit_n:5d} {len(sg):7d}")
        total_shapes += len(sg)
    print()
    print(f"Distinct shapes across this run: {total_shapes}")


if __name__ == "__main__":
    main()
