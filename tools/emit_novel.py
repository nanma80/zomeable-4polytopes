"""Emit .vZome files for shapes flagged [NOVEL] by analyze_sweep.

Reads ongoing_work/novel_rng<N>.json (produced by
`tools/analyze_sweep.py --out-novel`), picks one (group, bitmask,
example_kernel) representative per novel fp_hash, and runs
lib.emit_generic.project_and_emit to produce a .vZome file.

Output: output/wythoff_sweep/<common-name-slug>/<group>_<bitmask>_<idx>_<hash>.vZome
together with a JSON manifest at output/wythoff_sweep/manifest.json
mapping novel fp_hash -> source polytope, kernel, and emission status.

Usage:
    python tools/emit_novel.py [--rng 2] [--limit N]

Some shapes will fail to emit because their projected coordinates
cannot be snapped to ZZ[phi]^3 (the zometool-realisable subset of the
abstractly zomeable shapes is strictly smaller; this is a known
phenomenon -- e.g. only 3 of the 5 rng=1 8-cell shapes snap).  Those
are recorded as `status: 'snap_failed'` in the manifest.
"""
import os
import sys
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

import numpy as np

from wythoff import build_polytope
from emit_generic import project_and_emit


ONGOING = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "ongoing_work"))
OUT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "output", "wythoff_sweep"))


def load_novel(rng, path=None):
    """Load the novel-shape inventory written by analyze_sweep --out-novel."""
    p = path or os.path.join(ONGOING, f"novel_rng{rng}.json")
    if not os.path.exists(p):
        raise FileNotFoundError(
            f"{p} missing; run "
            f"`python tools/analyze_sweep.py --rng {rng} "
            f"--out-novel ongoing_work/novel_rng{rng}.json` first.")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_representative(occurrences):
    """Smallest n_balls (= simplest projection) wins; ties broken by
    polytope name for stability."""
    return min(occurrences,
               key=lambda o: (o["n_balls"], o["group"], o["bitmask"],
                              o["shape_idx"]))


def _slug(name):
    """Light slug for a polytope common name; preserves dashes/digits and
    replaces whitespace with underscore.  E.g. 'omnitruncated 120-cell' ->
    'omnitruncated_120-cell'."""
    return "_".join(name.split())


def emit_one(h, info, out_root):
    g = info["group"]
    bm = tuple(info["bitmask"])
    name = info["name"]
    n = np.array(info["example_kernel"], dtype=float)
    subdir = os.path.join(out_root, _slug(name))
    os.makedirs(subdir, exist_ok=True)
    fname = (f"{g}_{''.join(str(b) for b in bm)}_"
             f"{info['shape_idx']:02d}_{h[:10]}.vZome")
    path = os.path.join(subdir, fname)
    V4, E4 = build_polytope(g, bm)
    counts = project_and_emit(
        f"{g} {bm} {name} (shape {info['shape_idx']}, hash {h[:10]})",
        V4, E4, n, path, verbose=False)
    return path, counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rng", type=int, default=2)
    ap.add_argument("--novel-json", default=None,
                    help="(default: ongoing_work/novel_rng<N>.json)")
    ap.add_argument("--limit", type=int, default=None,
                    help="emit at most N novel shapes (smallest-V first)")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    novel_in = load_novel(args.rng, args.novel_json)
    print(f"{len(novel_in)} novel fp_hashes loaded.")

    # Pick smallest-balls representative for each novel hash.
    representatives = {}
    for h, entry in novel_in.items():
        rep = pick_representative(entry["occurrences"])
        representatives[h] = {
            "n_balls": entry["n_balls"],
            "sig": entry["sig"],
            **rep,
        }

    items = sorted(representatives.items(),
                   key=lambda kv: (kv[1]["n_balls"], kv[0]))
    if args.limit:
        items = items[:args.limit]
        print(f"  (limited to first {len(items)})")

    manifest = []
    n_ok = n_fail = 0
    for h, info in items:
        rec = {
            "fp_hash": h,
            "group": info["group"],
            "bitmask": list(info["bitmask"]),
            "source_polytope": info["name"],
            "shape_idx": info["shape_idx"],
            "n_balls": info["n_balls"],
            "kernel": list(info["example_kernel"]),
        }
        try:
            path, counts = emit_one(h, info, OUT_DIR)
            rec["status"] = "ok"
            rec["file"] = os.path.relpath(path,
                                          os.path.dirname(OUT_DIR))
            rec["strut_counts"] = {k: int(v) for k, v in counts.items()}
            n_ok += 1
            print(f"  OK    {h[:10]}  {info['group']} "
                  f"{info['bitmask']} {info['name']:25s} "
                  f"balls={info['n_balls']}")
        except Exception as e:
            short = (str(e).splitlines() or [""])[0][:120]
            if "snap" in short.lower():
                rec["status"] = "snap_failed"
            elif "alignable" in short.lower():
                rec["status"] = "align_failed"
            elif "edge classification" in short.lower():
                rec["status"] = "classify_failed"
            else:
                rec["status"] = "fail"
            rec["error"] = short
            n_fail += 1
            print(f"  FAIL  {h[:10]}  {info['group']} "
                  f"{info['bitmask']} {info['name']:25s}  "
                  f"[{rec['status']}] {short}")
        manifest.append(rec)

    manifest_path = os.path.join(OUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"rng": args.rng, "n_ok": n_ok, "n_fail": n_fail,
                   "shapes": manifest}, f, indent=2, sort_keys=True)
    print(f"\n{n_ok} emitted, {n_fail} failed.  Manifest: "
          f"{os.path.relpath(manifest_path)}")


if __name__ == "__main__":
    main()
