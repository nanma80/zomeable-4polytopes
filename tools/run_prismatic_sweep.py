"""Run agnostic kernel sweep on every prismatic uniform 4-polytope in scope.

Sweep machinery:
  * Construct (V, edges) via lib/polytopes_prismatic.
  * Generate all ZZ[phi]^4 kernel directions with |a|, |b| <= rng
    (lib/search_engine.gen_dirs).
  * Test each kernel via lib/search_engine.search.
  * Group hits by shape fingerprint (lib/search_engine.group_by_shape).
  * For each unique shape, pick smallest-|n| canonical kernel and try
    to snap+emit via lib/emit_generic.project_and_emit.

This is the SAME machinery used for the 47-corpus Wythoff sweep, but
WITHOUT the kernel-inheritance shortcut.  Every polytope is swept from
scratch; nothing is assumed.

Usage:
    python tools/run_prismatic_sweep.py [--family A|B|C] [--rng N]
                                         [--slug SLUG] [--no-emit]
                                         [--no-skip] [--max-V N]

Output:
  * Log: ongoing_work/prismatic_sweep_log.jsonl (one record per polytope)
  * Emitted shapes: output/<family-category>/<slug>/<basename>.vZome
    where family-category is polyhedral_prisms / duoprisms / antiprismatic_prisms.
  * Kernel cache: NOT used here (kernels regenerate trivially per
    polytope; gen_dirs is cheap).

Resume behaviour:
  Polytopes already present in the existing log are skipped by default
  (--no-skip to force re-run).
"""

import argparse
import datetime
import json
import os
import sys
import time
import traceback
from collections import defaultdict
from pathlib import Path

# Allow running as a module
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO_ROOT, "lib"))

import numpy as np

from prismatic_polytopes import get_registry
from search_engine import gen_dirs, search, group_by_shape
from polytope_features import extract_features, classify_kernel, label_basename
from emit_generic import project_and_emit


LOG_PATH = os.path.join(REPO_ROOT, "ongoing_work", "prismatic_sweep_log.jsonl")
OUTPUT_ROOT = os.path.join(REPO_ROOT, "output")

# Family -> category subfolder under output/.  Antiprismatic prisms are
# the only Family C members; polyhedral prisms = Family A; duoprisms =
# Family B.  These align with the broader output/ taxonomy
# (output/regular, output/uniform, output/polyhedral_prisms,
# output/duoprisms, output/antiprismatic_prisms).
FAMILY_DIR = {
    "A": "polyhedral_prisms",
    "B": "duoprisms",
    "C": "antiprismatic_prisms",
}


# ---------------------------------------------------------------------- #
# Direction-dedup helpers
# ---------------------------------------------------------------------- #
def _dedup_by_direction(hits, cos_tol=1e-6):
    """Collapse hits whose kernels are positive scalar multiples of each
    other.  Keeps smallest-|kernel|; returns deduped list."""
    if not hits:
        return hits
    K = np.array([h[0] for h in hits], dtype=float)
    norms = np.linalg.norm(K, axis=1)
    Ku = K / np.maximum(norms, 1e-12)[:, None]
    seen = np.zeros(len(hits), dtype=bool)
    kept = []
    for i in range(len(hits)):
        if seen[i]:
            continue
        sim = np.where((Ku @ Ku[i]) > 1 - cos_tol)[0]
        seen[sim] = True
        canon = sim[int(np.argmin([norms[j] for j in sim]))]
        kept.append(hits[int(canon)])
    return kept


# ---------------------------------------------------------------------- #
# Log helpers
# ---------------------------------------------------------------------- #
def _load_done_slugs(path: str):
    """Return set of slugs already present in the JSONL log."""
    out = set()
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                if rec.get("slug"):
                    out.add(rec["slug"])
            except Exception:
                continue
    return out


def _append_log(path: str, rec: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------------- #
# Per-polytope sweep
# ---------------------------------------------------------------------- #
def sweep_polytope(entry: dict, dirs, rng: int, emit: bool, verbose: bool):
    slug = entry["slug"]
    family = entry["family"]
    metadata = entry["metadata"]
    t0 = time.time()
    rec = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "slug": slug,
        "family": family,
        "metadata": metadata,
        "rng": rng,
        "status": "started",
    }
    try:
        V, edges = entry["builder"]()
    except Exception as e:
        rec["status"] = "build_failed"
        rec["error"] = repr(e)
        rec["elapsed_s"] = time.time() - t0
        return rec, []
    rec["nV"] = int(len(V))
    rec["nE"] = int(len(edges))
    if verbose:
        print(f"  [{slug}] V={len(V)} E={len(edges)}", flush=True)

    # Run sweep
    try:
        hits = search(slug, V, edges, dirs, verbose=False)
    except Exception as e:
        rec["status"] = "sweep_failed"
        rec["error"] = repr(e)
        rec["traceback"] = traceback.format_exc()
        rec["elapsed_s"] = time.time() - t0
        return rec, []

    rec["raw_hits"] = len(hits)
    if not hits:
        rec["status"] = "zero_hits"
        rec["unique_shapes"] = 0
        rec["emitted"] = []
        rec["elapsed_s"] = time.time() - t0
        if verbose:
            print(f"  [{slug}] 0 hits in {rec['elapsed_s']:.1f}s", flush=True)
        return rec, []

    # 1) Cheap direction-dedup first: collapse positive scalar multiples.
    #    This skips O(V^2) shape-fingerprint work on redundant kernels.
    hits = _dedup_by_direction(hits)
    rec["after_dir_dedup"] = len(hits)

    # 2) Shape-fingerprint group (this projects + computes pairwise dists).
    groups = group_by_shape(hits, V, edges)
    # Pick smallest-|n| canonical per shape group
    reps = []  # list of (fp_key, n_tuple, sig, n_balls)
    for fp, occs in groups.items():
        occ = min(occs, key=lambda x: (float(np.linalg.norm(np.array(x[0]))),
                                       tuple(np.abs(np.array(x[0])))))
        reps.append((fp, occ[0], occ[1], occ[2]))
    rec["unique_shapes"] = len(reps)

    # Classify each kernel
    try:
        features = extract_features(V, edges, skip_cells_above=600)
    except Exception as e:
        features = None
        rec["features_error"] = repr(e)

    # Group reps by (label, subtype) to assign indices
    classified = []
    for fp, n, sig, n_balls in reps:
        if features is not None:
            label, subtype = classify_kernel(np.array(n), features)
        else:
            label, subtype = ("oblique", None)
        classified.append({"fp": fp, "n": list(n), "sig": sig,
                           "n_balls": n_balls, "label": label,
                           "subtype": subtype})

    by_lbl = defaultdict(list)
    for i, c in enumerate(classified):
        by_lbl[(c["label"], c["subtype"])].append(i)
    for (label, subtype), idxs in by_lbl.items():
        if len(idxs) == 1:
            classified[idxs[0]]["basename"] = label_basename(label, subtype, None)
        else:
            for k, idx in enumerate(idxs):
                classified[idx]["basename"] = label_basename(label, subtype, k)

    # Emit each canonical
    emitted = []
    if emit:
        category = FAMILY_DIR.get(family, "")
        if category:
            out_dir = os.path.join(OUTPUT_ROOT, category, slug)
        else:
            out_dir = os.path.join(OUTPUT_ROOT, slug)
        os.makedirs(out_dir, exist_ok=True)
        for c in classified:
            out_path = os.path.join(out_dir, f"{c['basename']}.vZome")
            try:
                counts = project_and_emit(
                    f"{slug} {c['basename']}", V, edges,
                    np.array(c["n"]), out_path, verbose=False)
                emitted.append({
                    "basename": c["basename"],
                    "path": os.path.relpath(out_path, REPO_ROOT).replace("\\", "/"),
                    "label": c["label"],
                    "subtype": c["subtype"],
                    "n_balls": c["n_balls"],
                    "kernel": c["n"],
                    "strut_counts": dict(counts) if hasattr(counts, "items") else counts,
                    "status": "emitted",
                })
            except Exception as e:
                emitted.append({
                    "basename": c["basename"],
                    "label": c["label"],
                    "subtype": c["subtype"],
                    "n_balls": c["n_balls"],
                    "kernel": c["n"],
                    "status": "snap_failed",
                    "error": repr(e),
                })
    rec["emitted"] = emitted
    rec["status"] = "ok"
    rec["elapsed_s"] = time.time() - t0
    if verbose:
        n_ok = sum(1 for e in emitted if e["status"] == "emitted")
        n_fail = sum(1 for e in emitted if e["status"] == "snap_failed")
        print(f"  [{slug}] {len(reps)} unique shapes -> {n_ok} emitted, "
              f"{n_fail} snap-fail  ({rec['elapsed_s']:.1f}s)", flush=True)
    return rec, emitted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", choices=["A", "B", "C", "all"], default="all")
    ap.add_argument("--rng", type=int, default=2)
    ap.add_argument("--slug", default=None,
                    help="Limit to a single polytope by slug.")
    ap.add_argument("--no-emit", action="store_true",
                    help="Skip emit step (sweep + log only).")
    ap.add_argument("--no-skip", action="store_true",
                    help="Re-run polytopes already in the log.")
    ap.add_argument("--max-V", type=int, default=None,
                    help="Skip polytopes with more than N vertices.")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    family = None if args.family == "all" else args.family
    entries = list(get_registry(family))
    if args.slug:
        entries = [e for e in entries if e["slug"] == args.slug]
    if args.max_V:
        # Quick V-count using metadata; for polyhedral prisms we approximate.
        def estV(e):
            m = e["metadata"]
            if e["family"] == "A":
                from uniform_polyhedra import expected_VE
                return 2 * expected_VE(m["polyhedron"])[0]
            if e["family"] == "B":
                return m["p"] * m["q"]
            if e["family"] == "C":
                return 4 * m["n"]
            return 0
        entries = [e for e in entries if estV(e) <= args.max_V]

    # Skip already-done
    if not args.no_skip:
        done = _load_done_slugs(LOG_PATH)
        before = len(entries)
        entries = [e for e in entries if e["slug"] not in done]
        skipped = before - len(entries)
        if skipped and not args.quiet:
            print(f"skipping {skipped} polytopes already in log", flush=True)

    if not entries:
        print("nothing to do.")
        return

    # Order: small V first (rough estimate)
    def sort_key(e):
        m = e["metadata"]
        if e["family"] == "A":
            from uniform_polyhedra import expected_VE
            return 2 * expected_VE(m["polyhedron"])[0]
        if e["family"] == "B":
            return m["p"] * m["q"]
        if e["family"] == "C":
            return 4 * m["n"]
        return 0
    entries.sort(key=sort_key)

    if not args.quiet:
        print(f"=== prismatic sweep rng={args.rng}  ({len(entries)} polytopes) ===",
              flush=True)

    # Compute kernel directions once (depends only on rng).
    # NOTE: permute_dedup=False because prismatic polytopes do NOT have full
    # S4 axis-permutation symmetry: polyhedral + antiprism prisms single out
    # axis 4 (the prism axis); duoprisms split into two 2D groups.
    print(f"  generating kernels at rng={args.rng} (permute_dedup=False)...",
          flush=True)
    t0 = time.time()
    dirs = gen_dirs(args.rng, permute_dedup=False)
    print(f"  {len(dirs)} kernel directions ({time.time()-t0:.2f}s)", flush=True)

    sweep_t0 = time.time()
    for i, entry in enumerate(entries, 1):
        if not args.quiet:
            elapsed = time.time() - sweep_t0
            pct = 100.0 * (i - 1) / len(entries)
            eta = elapsed * (len(entries) - i + 1) / max(i - 1, 1)
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] [{i}/{len(entries)} {pct:5.1f}% elapsed={elapsed:.0f}s "
                  f"ETA={eta:.0f}s] {entry['slug']}", flush=True)
        rec, _ = sweep_polytope(entry, dirs, args.rng,
                                emit=not args.no_emit, verbose=not args.quiet)
        _append_log(LOG_PATH, rec)

    if not args.quiet:
        print(f"=== done ({time.time()-sweep_t0:.1f}s) ===", flush=True)


if __name__ == "__main__":
    main()
