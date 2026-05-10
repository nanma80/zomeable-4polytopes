"""Triage all fp_hashes from a new sweep against manifest, aliases,
and master corpus (output/<polytope>/ shape_signatures).

Reports:
- Per-bitmask: count of fp_hashes that are: in manifest / in aliases /
  in master corpus / in NONE (genuinely new).
"""
import json
import sys
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

NEW_SHAPES_PATH = sys.argv[1] if len(sys.argv) > 1 else \
    "ongoing_work/shapes_rng2_B4_kc.jsonl"


def main():
    os.chdir(ROOT)
    m = json.load(open("output/wythoff_sweep/manifest.json"))

    canonical_fp = set()
    alias_fp = set()
    by_polytope_canonical = defaultdict(set)
    by_polytope_alias = defaultdict(set)
    for s in m["shapes"]:
        key = (s["group"], tuple(s["bitmask"]))
        canonical_fp.add(s["fp_hash"])
        by_polytope_canonical[key].add(s["fp_hash"])
        for a in s.get("aliases", []):
            alias_fp.add(a)
            by_polytope_alias[key].add(a)

    print(f"manifest: {len(canonical_fp)} canonical fp_hashes, "
          f"{len(alias_fp)} aliases")

    # Per-polytope new sweep counts and fp_hash triage.
    print(f"\nNew sweep file: {NEW_SHAPES_PATH}")
    print(f"\n{'group':>4s} {'bitmask':14s}  {'new_fp':>6s}  "
          f"{'in_manifest':>11s} {'in_alias':>8s} {'in_other_pol':>12s} "
          f"{'unrec':>6s}")

    n_unrec_total = 0
    unrec_by_polytope = defaultdict(list)
    with open(NEW_SHAPES_PATH) as f:
        for line in f:
            rec = json.loads(line)
            key = (rec["group"], tuple(rec["bitmask"]))
            shapes = rec["shapes"]
            in_mf = sum(1 for sh in shapes if sh["fp_hash"]
                        in by_polytope_canonical[key])
            in_al = sum(1 for sh in shapes if sh["fp_hash"]
                        in by_polytope_alias[key])
            in_other = sum(1 for sh in shapes
                           if sh["fp_hash"] not in by_polytope_canonical[key]
                           and sh["fp_hash"] not in by_polytope_alias[key]
                           and (sh["fp_hash"] in canonical_fp
                                or sh["fp_hash"] in alias_fp))
            unrec = sum(1 for sh in shapes
                        if sh["fp_hash"] not in canonical_fp
                        and sh["fp_hash"] not in alias_fp)
            n_unrec_total += unrec
            for sh in shapes:
                if sh["fp_hash"] not in canonical_fp \
                        and sh["fp_hash"] not in alias_fp:
                    unrec_by_polytope[key].append(sh["fp_hash"])
            print(f"  {rec['group']:>4s} {str(key[1]):14s}  "
                  f"{len(shapes):>6d}  {in_mf:>11d} {in_al:>8d} "
                  f"{in_other:>12d} {unrec:>6d}")

    print(f"\nTotal unrecognised fp_hashes (NOT in manifest or aliases): "
          f"{n_unrec_total}")
    if unrec_by_polytope:
        print(f"\nUnrecognised fp_hashes by polytope:")
        for key, fps in unrec_by_polytope.items():
            print(f"  {key}:")
            for fp in fps:
                print(f"    {fp}")
        print()
        print("These need triage via emit_one + shape_signature to "
              "determine if genuinely new vs alias of master corpus.")
    else:
        print("\nNo unrecognised fp_hashes. New sweep is fully covered "
              "by manifest+aliases.")


if __name__ == "__main__":
    main()
