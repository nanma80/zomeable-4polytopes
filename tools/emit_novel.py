"""Emit .vZome files for shapes flagged [NOVEL] by analyze_sweep.

Reads ongoing_work/shapes_rng<N>.jsonl + the canonical-hashes cache
produced by tools/analyze_sweep.py, picks one (group, bitmask,
example_kernel) representative per novel fp_hash, and runs
lib.emit_generic.project_and_emit to produce a .vZome file.

Output: output/wythoff_sweep/<group>_<bitmask>_<short-hash>.vZome
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
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

import numpy as np

from wythoff import build_polytope
from emit_generic import project_and_emit


ONGOING = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "ongoing_work"))
OUT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "output", "wythoff_sweep"))


def load_canonical(rng):
    path = os.path.join(ONGOING, f"canonical_hashes_rng{rng}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} missing; run tools/analyze_sweep.py first to "
            f"populate the canonical-hash cache.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_records(rng, jsonl=None):
    path = jsonl or os.path.join(ONGOING, f"shapes_rng{rng}.jsonl")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            out.append(json.loads(line))
    return out


def collect_novel(records, canonical):
    """Return dict fp_hash -> {group, bitmask, name, shape_idx, kernel,
    n_balls}. Picks the smallest-V representative for each novel hash."""
    novel = {}
    for r in records:
        for i, sh in enumerate(r["shapes"]):
            h = sh["fp_hash"]
            if h in canonical:
                continue
            cand = {
                "group": r["group"],
                "bitmask": tuple(r["bitmask"]),
                "name": r["name"],
                "shape_idx": i,
                "n_balls": sh["n_balls"],
                "kernel": tuple(sh["example_kernel"]),
                "V": r["V"],
                "E": r["E"],
            }
            prev = novel.get(h)
            if prev is None or cand["V"] < prev["V"]:
                novel[h] = cand
    return novel


def emit_one(h, info, out_dir):
    g = info["group"]
    bm = info["bitmask"]
    name = info["name"]
    n = np.array(info["kernel"], dtype=float)
    fname = (f"{g}_{''.join(str(b) for b in bm)}_"
             f"{info['shape_idx']:02d}_{h[:10]}.vZome")
    path = os.path.join(out_dir, fname)
    V4, E4 = build_polytope(g, bm)
    counts = project_and_emit(
        f"{g} {bm} {name} (shape {info['shape_idx']}, hash {h[:10]})",
        V4, E4, n, path, verbose=False)
    return path, counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rng", type=int, default=2)
    ap.add_argument("--shapes-jsonl", default=None)
    ap.add_argument("--limit", type=int, default=None,
                    help="emit at most N novel shapes (smallest-V first)")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    canonical = load_canonical(args.rng)
    records = load_records(args.rng, args.shapes_jsonl)
    print(f"{len(canonical)} canonical hashes, {len(records)} polytope "
          f"records.")

    novel = collect_novel(records, canonical)
    print(f"{len(novel)} distinct novel fp_hashes")
    if args.limit:
        ranked = sorted(novel.items(),
                        key=lambda kv: (kv[1]["n_balls"], kv[1]["V"]))
        novel = dict(ranked[:args.limit])
        print(f"  (limited to first {len(novel)})")

    manifest = []
    n_ok = n_fail = 0
    for h, info in sorted(novel.items(),
                          key=lambda kv: (kv[1]["n_balls"],
                                          kv[1]["V"])):
        rec = {
            "fp_hash": h,
            "group": info["group"],
            "bitmask": list(info["bitmask"]),
            "source_polytope": info["name"],
            "shape_idx": info["shape_idx"],
            "n_balls": info["n_balls"],
            "kernel": list(info["kernel"]),
        }
        try:
            path, counts = emit_one(h, info, OUT_DIR)
            rec["status"] = "ok"
            rec["file"] = os.path.relpath(path,
                                          os.path.dirname(OUT_DIR))
            rec["strut_counts"] = {k: int(v) for k, v in counts.items()}
            n_ok += 1
            print(f"  OK    {h[:10]}  {info['group']} {info['bitmask']} "
                  f"{info['name']:25s} balls={info['n_balls']}")
        except Exception as e:
            rec["status"] = "fail"
            rec["error"] = str(e)
            n_fail += 1
            short = (str(e).splitlines() or [""])[0][:80]
            print(f"  FAIL  {h[:10]}  {info['group']} {info['bitmask']} "
                  f"{info['name']:25s}  {short}")
        manifest.append(rec)

    manifest_path = os.path.join(OUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"rng": args.rng, "n_ok": n_ok, "n_fail": n_fail,
                   "shapes": manifest}, f, indent=2, sort_keys=True)
    print(f"\n{n_ok} emitted, {n_fail} failed.  Manifest: "
          f"{os.path.relpath(manifest_path)}")


if __name__ == "__main__":
    main()
