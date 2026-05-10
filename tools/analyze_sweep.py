"""Cross-reference shape fingerprints from the Wythoff sweep against
the 6 regular convex 4-polytopes (5-cell, 8-cell, 16-cell, 24-cell,
600-cell, 120-cell), each of which appears as a (1,0,0,0)- or
(0,0,0,1)-bitmask record in the sweep itself.

Why we use the sweep's own regular records as reference rather than
re-running lib/polytopes.py: the Wythoff sweep applies a Cholesky-
to-Procrustes alignment so its build_polytope output is congruent to
lib/polytopes embeddings, but the alignment rotation in general is not
an axis-permutation in the canonical basis.  Since gen_dirs() samples
directions in the canonical lattice basis, the rotated Wythoff
embedding samples a *different* subset of zomeable kernels than
lib/polytopes does, even though both polytopes are the same regular
4-polytope abstractly.  Their full shape inventories therefore do not
fully overlap at finite rng -- so using the sweep regulars (which are
already aligned with everything else in the sweep) gives a clean
KNOWN/NOVEL bucketing that's internally consistent.

Reads ongoing_work/shapes_rng<N>.jsonl and labels each sweep shape:

  [KNOWN <polytope> #<idx>]  - matches a regular-polytope projection
  [NOVEL]                     - no regular-polytope match

Usage:
    python tools/analyze_sweep.py [--rng 2]
"""
import os
import sys
import json
import argparse
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))


ONGOING = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "ongoing_work"))


# (group, bitmask)  ->  human-readable regular-polytope name.
# These six records in the sweep collectively cover every standard
# regular convex 4-polytope.  F4 (1,0,0,0) is skipped here because it
# is a DUP of B4 (0,0,1,0).
REGULAR_REFERENCES = {
    ("A4", (1, 0, 0, 0)): "5-cell",
    ("B4", (1, 0, 0, 0)): "8-cell",
    ("B4", (0, 0, 1, 0)): "24-cell",
    ("B4", (0, 0, 0, 1)): "16-cell",
    ("H4", (1, 0, 0, 0)): "120-cell",
    ("H4", (0, 0, 0, 1)): "600-cell",
}


def load_reference_hashes(records, verbose=True):
    """Build {fp_hash: {poly, group, bitmask, shape_idx, n_balls, sig,
    n_kernels}} from the regular-polytope records in `records`."""
    ref = {}
    for r in records:
        key = (r["group"], tuple(r["bitmask"]))
        if key not in REGULAR_REFERENCES:
            continue
        poly = REGULAR_REFERENCES[key]
        if verbose:
            print(f"  reference {key[0]} {key[1]}  {poly:8s}  "
                  f"V={r.get('V')} E={r.get('E')}  "
                  f"shapes={len(r['shapes'])}")
        for i, sh in enumerate(r["shapes"]):
            h = sh["fp_hash"]
            if h in ref:
                # First-encountered regular wins; later regulars that
                # share a shape (e.g. degenerate projections) just
                # become aliases.
                continue
            ref[h] = {
                "poly": poly,
                "group": key[0],
                "bitmask": key[1],
                "shape_idx": i,
                "n_balls": sh["n_balls"],
                "sig": sh["example_sig"],
                "n_kernels": sh["n_kernels"],
            }
    return ref


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rng", type=int, default=2,
                    help="kernel range that the sweep used")
    ap.add_argument("--shapes-jsonl", default=None,
                    help="(default: ongoing_work/shapes_rng<N>.jsonl)")
    ap.add_argument("--out-novel", default=None,
                    help="optional path to write novel-shape table as JSON")
    args = ap.parse_args()

    jsonl = args.shapes_jsonl or os.path.join(
        ONGOING, f"shapes_rng{args.rng}.jsonl")
    if not os.path.exists(jsonl):
        print(f"ERROR: {jsonl} does not exist. Run the sweep first.")
        return

    with open(jsonl, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
    print(f"{len(records)} polytope records in "
          f"{os.path.relpath(jsonl)}\n")

    print("Building reference set from sweep regular records:")
    canonical = load_reference_hashes(records)
    print(f"\n{len(canonical)} distinct fp_hashes from regular polytopes.\n")

    # Bucket reference hashes by source polytope for compact reporting.
    canonical_by_poly = defaultdict(list)
    for h, info in canonical.items():
        canonical_by_poly[info["poly"]].append((h, info))
    print("Reference breakdown:")
    for poly in sorted(canonical_by_poly.keys()):
        ents = canonical_by_poly[poly]
        print(f"  {poly:10s}  {len(ents)} fp_hash(es)")
    print()

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
        # Skip the regular records themselves in the per-shape readout
        # (they're the reference; everything in them is trivially "known").
        is_regular = (g, bm) in REGULAR_REFERENCES
        marker = "  [REGULAR REF]" if is_regular else ""
        print(f"{g} {bm}  {name}{marker}")
        for i, sh in enumerate(r["shapes"]):
            h = sh["fp_hash"]
            n_balls = sh["n_balls"]
            sig = sh["example_sig"]
            nk = sh["n_kernels"]
            if not is_regular:
                per_group_count[g]["shapes"] += 1
            if h in canonical:
                info = canonical[h]
                tag = (f"[KNOWN {info['poly']} #{info['shape_idx']}]")
                if not is_regular:
                    seen_breakdown[info["poly"]] += 1
            else:
                tag = "[NOVEL]"
                if not is_regular:
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
    print("Summary (excluding regular reference records)")
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
    print(f"Known-shape matches by reference polytope:")
    for poly in sorted(seen_breakdown):
        print(f"  {poly:10s}  {seen_breakdown[poly]} sweep-shape match(es)")
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

    if args.out_novel:
        novel_dump = {
            h: {
                "n_balls": occs[0]["n_balls"],
                "sig": occs[0]["sig"],
                "occurrences": occs,
            } for h, occs in novel.items()
        }
        with open(args.out_novel, "w", encoding="utf-8") as f:
            json.dump(novel_dump, f, indent=2, sort_keys=True)
        print(f"\nNovel inventory written to {args.out_novel}")


if __name__ == "__main__":
    main()
