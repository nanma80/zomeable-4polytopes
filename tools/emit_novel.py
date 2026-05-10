"""Emit .vZome files for shapes flagged [NOVEL] by analyze_sweep.

Reads ongoing_work/novel_rng<N>.json (produced by
`tools/analyze_sweep.py --out-novel`), picks one (group, bitmask,
example_kernel) representative per novel fp_hash, and runs
lib.emit_generic.project_and_emit to produce a .vZome file.

Output: output/wythoff_sweep/<common-name-slug>/<label>[_<idx>]_<hash>.vZome
where <label> is the kernel-direction classification produced by
``lib.polytope_features.classify_kernel``:

    vertex_first
    cell_first[_<celltype>]    (e.g. cell_first_truncated_octahedron)
    face_first[_<polygon>]      (e.g. face_first_hexagon)
    edge_first
    oblique

``_<idx>`` is appended only when multiple shapes within the same
polytope classify identically.

The driver also collapses representatives that are positive scalar
multiples of one another to a single canonical entry: such kernels
project to identical 3D shapes but ``shape_fingerprint`` produces
slightly different hashes for them due to SVD basis ambiguity in
``projection_matrix`` -- that ambiguity over-reports distinct novel
shapes.  Within each polytope we keep the smallest-|kernel| direction
as the canonical representative.

A JSON manifest at output/wythoff_sweep/manifest.json records each
emitted shape's source polytope, kernel, label, alias hashes, and
emission status.

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
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np

from wythoff import build_polytope
from emit_generic import project_and_emit
from polytope_features import (
    classify_kernel, extract_features, label_basename,
)
from dedup_corpus_by_shape import dedup_manifest_by_shape


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


def _dedup_by_direction(reps, cos_tol=1e-6):
    """Collapse representatives whose kernels are positive scalar multiples
    of each other.  Keeps the smallest-|kernel| representative per
    direction-class; returns a (kept_reps_dict, aliases) pair where
    ``aliases[h]`` is a sorted list of fp_hashes that were absorbed
    into the canonical entry ``h``.

    Grouping is *per polytope* (group, bitmask) -- different polytopes
    legitimately share kernel directions.
    """
    by_poly = defaultdict(list)
    for h, info in reps.items():
        key = (info["group"], tuple(info["bitmask"]))
        by_poly[key].append(h)

    aliases = defaultdict(list)
    kept = {}
    for key, hashes in by_poly.items():
        if len(hashes) == 1:
            kept[hashes[0]] = reps[hashes[0]]
            continue
        K = np.asarray([reps[h]["example_kernel"] for h in hashes],
                       dtype=float)
        norms = np.linalg.norm(K, axis=1)
        Ku = K / np.maximum(norms, 1e-12)[:, None]
        seen = np.zeros(len(hashes), dtype=bool)
        for i in range(len(hashes)):
            if seen[i]:
                continue
            sim = np.where((Ku @ Ku[i]) > 1 - cos_tol)[0]
            seen[sim] = True
            grp = [hashes[j] for j in sim]
            canon = grp[int(np.argmin([norms[j] for j in sim]))]
            kept[canon] = reps[canon]
            for h in grp:
                if h != canon:
                    aliases[canon].append(h)
    for h in aliases:
        aliases[h].sort()
    return kept, dict(aliases)


def _build_basenames(items, feat_cache):
    """Classify each item's kernel and assign ``label[_<idx>]`` basenames.

    Returns parallel lists ``basenames``, ``labels``, ``subtypes`` keyed
    on the order of ``items``.  ``feat_cache`` is filled in-place.
    """
    keys = [(info["group"], tuple(info["bitmask"]))
            for _, info in items]
    classifications = [None] * len(items)
    grouped = defaultdict(list)

    for idx, ((h, info), key) in enumerate(zip(items, keys)):
        if key not in feat_cache:
            print(f"    building features for {key[0]} {key[1]} "
                  f"({info['name']})...")
            V, E = build_polytope(*key)
            feat_cache[key] = extract_features(np.asarray(V, dtype=float), E)
        feats = feat_cache[key]
        kernel = np.asarray(info["example_kernel"], dtype=float)
        label, subtype = classify_kernel(kernel, feats)
        classifications[idx] = (label, subtype)
        grouped[(*key, label, subtype)].append(idx)

    basenames = [""] * len(items)
    for gkey, idxs in grouped.items():
        if len(idxs) == 1:
            i = idxs[0]
            label, subtype = classifications[i]
            basenames[i] = label_basename(label, subtype, index=None)
        else:
            for n, i in enumerate(idxs):
                label, subtype = classifications[i]
                basenames[i] = label_basename(label, subtype, index=n)
    labels = [c[0] for c in classifications]
    subtypes = [c[1] for c in classifications]
    return basenames, labels, subtypes


def emit_one(h, info, out_root, basename):
    g = info["group"]
    bm = tuple(info["bitmask"])
    name = info["name"]
    n = np.array(info["example_kernel"], dtype=float)
    subdir = os.path.join(out_root, _slug(name))
    os.makedirs(subdir, exist_ok=True)
    fname = f"{basename}_{h[:10]}.vZome"
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
    ap.add_argument("--no-dedup-direction", action="store_true",
                    help="skip per-polytope direction-deduplication "
                         "(for debugging the spurious-fp_hash bug).")
    ap.add_argument("--no-dedup-shape", action="store_true",
                    help="skip post-emission 3D shape-congruence dedup.")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    novel_in = load_novel(args.rng, args.novel_json)
    print(f"{len(novel_in)} novel fp_hashes loaded.")

    representatives = {}
    for h, entry in novel_in.items():
        rep = pick_representative(entry["occurrences"])
        representatives[h] = {
            "n_balls": entry["n_balls"],
            "sig": entry["sig"],
            **rep,
        }

    if args.no_dedup_direction:
        aliases_for: dict[str, list[str]] = {}
    else:
        before = len(representatives)
        representatives, aliases_for = _dedup_by_direction(representatives)
        after = len(representatives)
        n_aliases = sum(len(v) for v in aliases_for.values())
        print(f"direction-dedup: {before} -> {after} canonical entries "
              f"({n_aliases} aliases collapsed)")

    items = sorted(representatives.items(),
                   key=lambda kv: (kv[1]["n_balls"], kv[0]))
    if args.limit:
        items = items[:args.limit]
        print(f"  (limited to first {len(items)})")

    print("classifying kernels and building filenames...")
    feat_cache = {}
    basenames, labels, subtypes = _build_basenames(items, feat_cache)

    manifest = []
    n_ok = n_fail = 0
    for (h, info), basename, label, subtype in zip(
            items, basenames, labels, subtypes):
        rec = {
            "fp_hash": h,
            "group": info["group"],
            "bitmask": list(info["bitmask"]),
            "source_polytope": info["name"],
            "shape_idx": info["shape_idx"],
            "n_balls": info["n_balls"],
            "kernel": list(info["example_kernel"]),
            "label": label,
            "label_subtype": subtype,
        }
        if h in aliases_for:
            rec["aliases"] = aliases_for[h]
            rec["alias_count"] = len(aliases_for[h])
        try:
            path, counts = emit_one(h, info, OUT_DIR, basename)
            rec["status"] = "ok"
            rec["file"] = os.path.relpath(path,
                                          os.path.dirname(OUT_DIR))
            rec["strut_counts"] = {k: int(v) for k, v in counts.items()}
            n_ok += 1
            print(f"  OK    {h[:10]}  {info['group']} "
                  f"{info['bitmask']} {info['name']:25s} "
                  f"balls={info['n_balls']}  -> {basename}")
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
    full_manifest = {"rng": args.rng, "n_ok": n_ok, "n_fail": n_fail,
                     "shapes": manifest}
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(full_manifest, f, indent=2, sort_keys=True)
    print(f"\n{n_ok} emitted, {n_fail} failed.  Manifest: "
          f"{os.path.relpath(manifest_path)}")

    if not args.no_dedup_shape and n_ok > 1:
        print("\nrunning 3D shape-congruence dedup pass...")
        corpus_root = Path(OUT_DIR).parent  # output/
        stats = dedup_manifest_by_shape(full_manifest, corpus_root)
        print(f"  shape-dedup: {stats['before']} -> {stats['after']} "
              f"({stats['removed']} duplicates removed; "
              f"{stats['deleted']} files deleted)")
        full_manifest["n_ok"] = sum(
            1 for s in full_manifest["shapes"] if s.get("status") == "ok")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(full_manifest, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
