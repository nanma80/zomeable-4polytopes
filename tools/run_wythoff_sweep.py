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

from wythoff import build_polytope, simple_roots, wythoff_seed, orbit
from uniform_polytopes import all_uniform_polytopes, KNOWN_DUPLICATES
from polytopes import snub_24cell, grand_antiprism
from search_engine import gen_dirs, search, group_by_shape


def _vertex_count(group, bitmask):
    """Cheap vertex count: orbit only, skip the O(V^2) edge build.

    Used by --sort-by-size where we only need |V| to order the work
    queue.  For the omnitruncated 120-cell (V=14400) the full
    build_polytope() spends ~tens of minutes computing edges; this
    avoids that wasted work for polytopes that may not yet be
    processed."""
    if sum(bitmask) == 0:
        return 0
    roots = simple_roots(group)
    seed = wythoff_seed(roots, bitmask)
    return len(orbit(seed, roots))


GROUPS = ("A4", "B4", "F4", "H4")
REGULAR_BITMASK = (1, 0, 0, 0)

# Regular polytopes per group (single-ring Coxeter ringings that are
# regular polytopes, NOT the rectifications).  Both (1,0,0,0) and
# (0,0,0,1) ringings are regular for every Coxeter group; for the
# self-dual groups A4 and F4 they happen to be the same polytope but
# oriented differently in the wythoff frame, so the search may surface
# different kernel vectors.  For the dual-pair groups B4 and H4 they
# are different polytopes (tesseract vs 16-cell, 120-cell vs 600-cell).
#
# kernel-completeness-fix (2026-05-08): the production sweep used to
# search only (1,0,0,0); empirical blind-spot audits at rng=2 across
# all four groups (A4/B4/F4 in commit history M17/M18; H4 small-V in
# M19.audit and M19.audit-round-3; H4 large-V in this milestone)
# discovered no genuinely new shapes that the (1,0,0,0)-only inheritance
# missed.  But the production code's safety claim is "all single-ring
# regulars give every kernel any descendant could need", so this dict
# now lists all the regulars per group, the cache stores them
# separately, and find_group_kernels() unions them at runtime.
REGULAR_BITMASKS = {
    "A4": [(1, 0, 0, 0), (0, 0, 0, 1)],
    "B4": [(1, 0, 0, 0), (0, 0, 0, 1)],
    "F4": [(1, 0, 0, 0), (0, 0, 0, 1)],
    "H4": [(1, 0, 0, 0), (0, 0, 0, 1)],
}

# Non-Wythoff polytopes: tested against the kernels of an explicit
# canonical-frame regular polytope (NOT the wythoff (1,0,0,0) cache).
# The wythoff frame uses a Procrustes calibration anchored to the
# (1,0,0,0) regular (cell120 for H4, tesseract for B4, ...), so the
# (0,0,0,1) regular -- e.g., the wythoff-frame 600-cell -- comes out
# in a *different* frame from the canonical cell600() in lib/polytopes.py
# (radii 1.2361 vs 1.000, 0/120 vertex overlap).  snub_24cell() and
# grand_antiprism() are constructed in the canonical cell600 frame, so
# their zomeable kernels live in *that* frame, not in the wythoff
# (1,0,0,0)-calibrated H4 frame.
#
# Each entry: (parent_group_label, sentinel_bitmask, polytope_name,
#              vertex_loader, canonical_kernel_loader).
#
# `parent_group_label` is informational (used in shape records); the
# kernel set comes from the kernel_loader callable, not from
# group_kernels[parent_group].
#
# The sentinel bitmask (0,0,0,0) is impossible for a Wythoff polytope
# (Wythoff requires at least one ringed node), so it doubles as a
# "non-Wythoff" tag in shape records.
#
# Master kernels that this sweep is expected to rediscover (the .vZome
# files already in output/uniform/snub_24cell/ and output/uniform/grand_antiprism/):
#   snub 24-cell      cell-first   (1, 0, 0, 0)
#   snub 24-cell      vertex-first (phi^2, phi, 1, 0)
#   grand antiprism   vertex-first (1, 1, 1, 1)
#   grand antiprism   ring-first   (1, 0, 0, 0)


def _find_canonical_cell600_kernels(rng, cache=True):
    """Kernels of canonical cell600() (lib/polytopes.py), at coefficient
    range `rng`, in the *canonical* 600-cell frame (radius 1).

    Used for non-Wythoff polytopes whose vertex coordinates are also in
    the canonical cell600 frame (snub_24cell, grand_antiprism).  Cached
    to ongoing_work/kernels_H4_canon600_rng<N>.npy so the 40+ minute
    search is paid once."""
    from polytopes import cell600
    path = os.path.join(ONGOING, f"kernels_H4_canon600_rng{rng}.npy")
    if cache and os.path.exists(path):
        arr = np.load(path)
        rel = os.path.relpath(path)
        print(f"  [cell600 canon] loaded {len(arr)} cached kernels "
              f"from {rel}")
        kernels = [arr[i] for i in range(len(arr))]
    else:
        V, E = cell600()
        dirs = gen_dirs(rng=rng, integer_only=False, permute_dedup=False)
        print(f"  [cell600 canon] |V|={len(V)}, |E|={len(E)}, "
              f"trying {len(dirs)} dirs...")
        t0 = time.time()
        hits = search("cell600_canon", V, E, dirs, verbose=False)
        kernels = [np.array(n) for (n, sig, balls) in hits]
        print(f"  [cell600 canon] {len(kernels)} hits in "
              f"{time.time()-t0:.1f}s")
        if cache and kernels:
            os.makedirs(ONGOING, exist_ok=True)
            np.save(path, np.array(kernels))
            print(f"  [cell600 canon] cached to {os.path.relpath(path)}")
    return _dedup_kernels_by_direction(kernels)


NON_WYTHOFF = (
    ("H4", (0, 0, 0, 0), "snub 24-cell",
     snub_24cell, _find_canonical_cell600_kernels),
    ("H4", (0, 0, 0, 0), "grand antiprism",
     grand_antiprism, _find_canonical_cell600_kernels),
)

# ongoing_work/ relative to repo root (parent of tools/)
ONGOING = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "ongoing_work"))


def kernel_cache_path(group, rng, bitmask=None):
    """Cache path for the kernels of a given regular bitmask of `group`.

    `bitmask=None` (or the legacy default (1,0,0,0)) returns the
    historical filename ``kernels_<group>_rng<N>.npy`` so existing
    caches keep working.  Other regulars use
    ``kernels_<group>_<bm>_rng<N>.npy`` (e.g.
    ``kernels_H4_0001_rng2.npy``).
    """
    if bitmask is None or tuple(bitmask) == REGULAR_BITMASK:
        return os.path.join(ONGOING, f"kernels_{group}_rng{rng}.npy")
    bm_str = "".join(str(b) for b in bitmask)
    return os.path.join(ONGOING, f"kernels_{group}_{bm_str}_rng{rng}.npy")


def _dedup_kernels_by_direction(kernels, cos_tol=1e-6):
    """Collapse a list of kernel arrays to one canonical kernel per
    positive direction.

    ``shape_fingerprint`` returns slightly different hashes for kernels
    that are positive scalar multiples of each other (degenerate SVD
    basis in projection_matrix is sensitive to FP noise in the
    normalised input).  Rather than ask the fingerprint to be more
    robust, we dedupe at source: scaled-equivalent kernels project to
    identical 3D shapes by definition, so testing only the smallest
    representative per direction class is sufficient.

    Returns the deduplicated list.  Order is preserved relative to the
    first appearance of each direction class.
    """
    if len(kernels) <= 1:
        return list(kernels)
    K = np.asarray(kernels, dtype=float)
    norms = np.linalg.norm(K, axis=1)
    Ku = K / np.maximum(norms, 1e-12)[:, None]
    seen = np.zeros(len(K), dtype=bool)
    keep_idx = []
    for i in range(len(K)):
        if seen[i]:
            continue
        sim = np.where((Ku @ Ku[i]) > 1 - cos_tol)[0]
        seen[sim] = True
        # smallest |kernel| representative
        canon = sim[int(np.argmin(norms[sim]))]
        keep_idx.append(int(canon))
    keep_idx.sort()
    return [kernels[i] for i in keep_idx]


def find_group_kernels_for_bitmask(group, bitmask, rng, cache=True):
    """Return a list of kernel ndarrays for the regular polytope of
    `group` at single-ring `bitmask` and coefficient range `rng`.

    Reads from the kernel cache file if present; otherwise runs the
    search and writes the cache.  The result is deduplicated by
    direction (positive scalar multiples collapsed), even when loaded
    from a cache that pre-dates the dedup pass."""
    path = kernel_cache_path(group, rng, bitmask)
    bm_label = "".join(str(b) for b in bitmask)
    if cache and os.path.exists(path):
        arr = np.load(path)
        rel = os.path.relpath(path)
        print(f"  [{group} {bm_label}] loaded {len(arr)} cached kernels "
              f"from {rel}")
        kernels = [arr[i] for i in range(len(arr))]
    else:
        V, E = build_polytope(group, bitmask)
        dirs = gen_dirs(rng=rng, integer_only=False, permute_dedup=False)
        print(f"  [{group} {bm_label}] regular: |V|={len(V)}, |E|={len(E)}, "
              f"trying {len(dirs)} dirs...")
        t0 = time.time()
        hits = search(group + "_" + bm_label, V, E, dirs, verbose=False)
        kernels = [np.array(n) for (n, sig, balls) in hits]
        print(f"  [{group} {bm_label}] {len(kernels)} hits in "
              f"{time.time()-t0:.1f}s")
        if cache and kernels:
            os.makedirs(ONGOING, exist_ok=True)
            np.save(path, np.array(kernels))
            print(f"  [{group} {bm_label}] cached to "
                  f"{os.path.relpath(path)}")
    n_before = len(kernels)
    kernels = _dedup_kernels_by_direction(kernels)
    if len(kernels) < n_before:
        print(f"  [{group} {bm_label}] direction-dedup: "
              f"{n_before} -> {len(kernels)} kernels")
    return kernels


def find_group_kernels(group, rng, cache=True):
    """Return the deduplicated union of kernels across all regular
    polytopes of `group` at coefficient range `rng`.

    For each regular bitmask in REGULAR_BITMASKS[group], runs the
    per-bitmask search (cached separately), then unions and dedupes by
    direction so the caller sees a single combined kernel list.

    The (1,0,0,0) entry uses the historical cache path
    ``kernels_<group>_rng<N>.npy`` so existing caches keep working.
    Additional regular bitmasks (currently (0,0,0,1) for all four
    groups) are cached separately.

    Empirical note (2026-05-08): for rng=2 the (0,0,0,1) cache is
    expected to add zero new kernel directions to the deduplicated
    union; the blind-spot audits across all four groups found no
    genuinely new shapes that the (1,0,0,0)-only inheritance missed.
    Including (0,0,0,1) here ensures the production code's safety
    claim is implemented, not just empirically supported.
    """
    bitmasks = REGULAR_BITMASKS.get(group, [REGULAR_BITMASK])
    all_kernels = []
    per_bm_counts = []
    for bm in bitmasks:
        ks = find_group_kernels_for_bitmask(group, bm, rng, cache=cache)
        all_kernels.extend(ks)
        per_bm_counts.append((bm, len(ks)))
    n_pre_union = len(all_kernels)
    merged = _dedup_kernels_by_direction(all_kernels)
    if len(bitmasks) > 1:
        parts = ", ".join(f"{''.join(str(b) for b in bm)}={n}"
                          for bm, n in per_bm_counts)
        print(f"  [{group}] union of {len(bitmasks)} regulars "
              f"({parts}) -> {n_pre_union} kernels, "
              f"{len(merged)} after direction-dedup")
    return merged


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
    """Stable SHA-256 hex digest of a fingerprint, robust across
    Python's randomized hash().

    The fingerprint can have two shapes (see lib/search_engine
    .shape_fingerprint):
      - ``(n_balls, sorted_distance_tuple)`` for the small/medium
        polytopes (the original format).
      - ``(n_balls, ('multiset', sorted_(value, count)_items))`` for
        the very-large polytopes (V > ~5000) where the full sorted
        distance tuple is too bulky to materialise.
    Both formats are dispatched here so a single fp_hash field in the
    JSONL records covers either case; collisions across formats are not
    expected because the multiset path only ever fires for n_balls
    above a threshold that no small-polytope record will reach.
    """
    n_balls, dists = fp
    if (isinstance(dists, tuple) and len(dists) == 2
            and dists[0] == "multiset"):
        items = dists[1]
        payload = repr(("multiset", int(n_balls),
                        tuple((round(float(v), 6), int(c))
                              for v, c in items)))
    else:
        payload = repr((int(n_balls),
                        tuple(round(float(d), 6) for d in dists)))
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
        is_multiset = (isinstance(dists, tuple) and len(dists) == 2
                       and dists[0] == "multiset")
        if n_balls <= _MAX_DUMP_BALLS and not is_multiset:
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
    ap.add_argument("--bitmask", default=None,
                    help="restrict to a single Wythoff bitmask, e.g. "
                         "--bitmask 1111 (used to launch per-polytope "
                         "parallel jobs for the H4 endgame)")
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
    if args.bitmask is not None:
        bm_filter = tuple(int(c) for c in args.bitmask)
        work = [(g, b, n) for (g, b, n) in work if b == bm_filter]
        if not work:
            print(f"# no work item matches --bitmask {args.bitmask} "
                  f"in selected groups")
            return
    if args.sort_by_size:
        sized = []
        for g, b, n in work:
            if (g, b) in KNOWN_DUPLICATES or (g, b) in done_set:
                # Place skips/dups at the front (cheap to handle).
                sized.append((-1, g, b, n))
                continue
            try:
                Vn = _vertex_count(g, b)
                sized.append((Vn, g, b, n))
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

    # 2b. Non-Wythoff polytopes (snub 24-cell, grand antiprism), tested
    #     against an explicit canonical-frame kernel set rather than the
    #     parent group's wythoff (1,0,0,0) cache.  These are not in
    #     all_uniform_polytopes() so we iterate them explicitly.  The
    #     --bitmask filter excludes them (real Wythoff bitmask required).
    if args.bitmask is None:
        for parent_group, b, name, loader, kernel_loader in NON_WYTHOFF:
            try:
                kernels = kernel_loader(args.rng)
            except Exception as e:
                print(f"  {parent_group} {b}  {name:30s}  "
                      f"kernel-loader ERR: {e}  [non-Wythoff, skip]")
                continue
            t0 = time.time()
            try:
                V, E = loader()
                hits = search(name, V, E, kernels, verbose=False)
                shape_groups = group_by_shape(hits, V, E)
            except RuntimeError as e:
                print(f"  {parent_group} {b}  {name:30s}  ERR: {e}  "
                      f"[non-Wythoff]")
                results.append((parent_group, b, name, f"ERR: {e}",
                                None, None, None))
                continue
            dt = time.time() - t0
            print(f"  {parent_group} {b}  {name:30s}  "
                  f"V={len(V):5d} E={len(E):5d}  "
                  f"hits={len(hits):4d}  shapes={len(shape_groups)}  "
                  f"({dt:.1f}s)  [non-Wythoff]")
            if not args.no_dump_shapes:
                try:
                    dump_shape_record(shapes_jsonl_path, parent_group,
                                      b, name, V, E, len(hits),
                                      len(kernels), shape_groups)
                except Exception as e:
                    print(f"  WARN: shape dump failed for "
                          f"{parent_group} {b}: {e}")
            results.append((parent_group, b, name, len(V), len(E),
                            len(hits), shape_groups))

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
