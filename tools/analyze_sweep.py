"""Cross-reference shape fingerprints from the Wythoff sweep against
the 8 canonical convex uniform 4-polytopes already enumerated in
output/<polytope>/.

Reads ongoing_work/shapes_rng<N>.jsonl, computes canonical fingerprints
from lib/polytopes.py at the same rng, and labels each sweep shape:

  [KNOWN <polytope>/<label> #<idx>] - matches a canonical projection
  [NOVEL]                            - no canonical match

Canonical fingerprints are cached at
ongoing_work/canonical_hashes_rng<N>.json so subsequent runs skip the
search step.

Usage:
    python tools/analyze_sweep.py [--rng 2]
"""
import os
import sys
import json
import argparse
import hashlib
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

import numpy as np

from polytopes import POLYTOPES
from search_engine import gen_dirs, search, group_by_shape


ONGOING = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "ongoing_work"))


def hash_fingerprint(fp):
    """Match the hashing scheme used by run_wythoff_sweep.dump_shape_record."""
    n_balls, dists = fp
    payload = repr((int(n_balls),
                    tuple(round(float(d), 6) for d in dists)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def compute_canonical_hashes(rng, verbose=True):
    """Run the search on each polytope in lib/polytopes.POLYTOPES at the
    given rng, return a dict fp_hash -> {poly, label, shape_idx, n_balls,
    sig, n_kernels}."""
    out = {}
    for name, embeddings in POLYTOPES.items():
        for label, fn in embeddings:
            V, E = fn()
            # The sweep used permute_dedup=False; for canonical search
            # permute_dedup=True is fine since most canonical embeddings
            # are S_4-symmetric and the deduped set finds the same shapes.
            dirs = gen_dirs(rng=rng, integer_only=False, permute_dedup=True)
            if verbose:
                print(f"  canonical {name}/{label}: V={len(V)} E={len(E)} "
                      f"dirs={len(dirs)}")
            hits = search(name, V, E, dirs, verbose=False)
            sg = group_by_shape(hits, V, E)
            for idx, (fp, examples) in enumerate(sg.items()):
                h = hash_fingerprint(fp)
                if h in out:
                    continue
                n0, sig0, balls0 = examples[0]
                out[h] = {
                    "poly": name,
                    "label": label,
                    "shape_idx": idx,
                    "n_balls": int(fp[0]),
                    "sig": dict(sig0),
                    "n_kernels": len(examples),
                    "example_kernel": [float(x) for x in n0],
                }
            if verbose:
                print(f"    -> {len(sg)} distinct shapes, "
                      f"{len(out)} cumulative hashes")
    return out


def load_canonical(rng, verbose=True):
    """Load canonical hashes from cache, or compute and cache them."""
    path = os.path.join(ONGOING, f"canonical_hashes_rng{rng}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    if verbose:
        print(f"Computing canonical fingerprints at rng={rng} "
              f"(one-time, ~minutes; will cache to {os.path.relpath(path)})")
    out = compute_canonical_hashes(rng, verbose=verbose)
    os.makedirs(ONGOING, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rng", type=int, default=2,
                    help="kernel range that the sweep used")
    ap.add_argument("--shapes-jsonl", default=None,
                    help="(default: ongoing_work/shapes_rng<N>.jsonl)")
    ap.add_argument("--rebuild-canonical", action="store_true",
                    help="recompute canonical fingerprints "
                         "(deletes cache first)")
    args = ap.parse_args()

    jsonl = args.shapes_jsonl or os.path.join(
        ONGOING, f"shapes_rng{args.rng}.jsonl")

    if args.rebuild_canonical:
        cache = os.path.join(ONGOING, f"canonical_hashes_rng{args.rng}.json")
        if os.path.exists(cache):
            os.remove(cache)

    canonical = load_canonical(args.rng)
    print(f"\n{len(canonical)} distinct canonical fp_hashes loaded.\n")

    # Bucket canonical hashes by source polytope for compact reporting.
    canonical_by_poly = defaultdict(list)
    for h, info in canonical.items():
        canonical_by_poly[info["poly"]].append((h, info))
    print("Canonical breakdown:")
    for poly in sorted(canonical_by_poly.keys()):
        ents = canonical_by_poly[poly]
        # Distinct fp_hashes per polytope (might be > number of distinct
        # shapes if multiple embeddings produce different fingerprints
        # for the same 3D shape).
        print(f"  {poly:18s}  {len(ents)} fp_hash(es)")
    print()

    # Read sweep dump.
    if not os.path.exists(jsonl):
        print(f"ERROR: {jsonl} does not exist. Run the sweep first.")
        return
    with open(jsonl, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
    print(f"{len(records)} polytope records in "
          f"{os.path.relpath(jsonl)}\n")

    novel = defaultdict(list)
    seen_breakdown = defaultdict(int)
    per_group_count = defaultdict(lambda: {"shapes": 0, "novel": 0})

    print("=" * 76)
    print("Per-polytope shape labelling")
    print("=" * 76)
    for r in records:
        g = r["group"]
        bm = tuple(r["bitmask"])
        name = r["name"]
        print(f"{g} {bm}  {name}")
        for i, sh in enumerate(r["shapes"]):
            h = sh["fp_hash"]
            n_balls = sh["n_balls"]
            sig = sh["example_sig"]
            nk = sh["n_kernels"]
            per_group_count[g]["shapes"] += 1
            if h in canonical:
                info = canonical[h]
                tag = (f"[KNOWN {info['poly']}/{info['label']} "
                       f"#{info['shape_idx']}]")
                seen_breakdown[info["poly"]] += 1
            else:
                tag = "[NOVEL]"
                per_group_count[g]["novel"] += 1
                novel[h].append({
                    "group": g, "bitmask": bm, "name": name,
                    "shape_idx": i, "n_balls": n_balls, "sig": sig,
                    "n_kernels": nk,
                    "example_kernel": sh["example_kernel"],
                })
            print(f"    shape {i}: balls={n_balls:4d}  sig={sig}  "
                  f"kernels={nk:4d}  {tag}")
        print()

    print("=" * 76)
    print("Summary")
    print("=" * 76)
    print(f"{'group':6s} {'shapes':>7s} {'novel':>7s}")
    total_shapes = total_novel = 0
    for g in sorted(per_group_count):
        c = per_group_count[g]
        print(f"  {g:4s}  {c['shapes']:7d} {c['novel']:7d}")
        total_shapes += c["shapes"]
        total_novel += c["novel"]
    print(f"  {'TOT':4s}  {total_shapes:7d} {total_novel:7d}")
    print()
    print(f"Distinct novel fp_hashes: {len(novel)}")
    print(f"Known-shape matches by canonical polytope:")
    for poly in sorted(seen_breakdown):
        print(f"  {poly:18s}  {seen_breakdown[poly]} sweep-shape match(es)")
    print()

    if novel:
        print("=" * 76)
        print(f"Novel shapes ({len(novel)} distinct fp_hashes)")
        print("=" * 76)
        for h, occs in sorted(novel.items(),
                              key=lambda kv: (-len(kv[1]), kv[0])):
            sample = occs[0]
            print(f"  {h}  balls={sample['n_balls']:4d}  "
                  f"sig={sample['sig']}  ({len(occs)} occurrence(s))")
            for occ in occs[:5]:
                print(f"    {occ['group']} {occ['bitmask']} "
                      f"{occ['name']:30s} shape #{occ['shape_idx']}  "
                      f"kernels={occ['n_kernels']:4d}  "
                      f"n={occ['example_kernel']}")
            if len(occs) > 5:
                print(f"    ... and {len(occs)-5} more")


if __name__ == "__main__":
    main()
