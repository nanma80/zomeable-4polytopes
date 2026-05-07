"""Promote 3 NEW shapes from blind-spot audit (Milestone 17).

Inputs:
    ongoing_work/blind_spot_triage.json
    ongoing_work/blind_spot_candidates/<slug>/fp_<hash>.vZome  (staged)

Pipeline (model: ongoing_work/probes/promote_b4_rng4.py):
    1. Index existing corpus signatures (output/wythoff_sweep + master regulars)
    2. Re-verify each candidate_new_canonical record's Stage-B sig from the
       staged .vZome; confirm not already in corpus.
    3. Cross-polytope dedup among candidates.
    4. classify_kernel + assign filenames.
    5. Copy files to output/wythoff_sweep/<slug>/
    5b. Normalise scale within each polytope (* phi^-k)
    6. Append manifest entries with rng=2 + Milestone 17 note.
"""
import json
import math
import os
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

import numpy as np
from wythoff import build_polytope
from polytope_features import (
    classify_kernel, extract_features, label_basename,
)
from dedup_corpus_by_shape import parse_vzome, shape_signature
from scale_vzome_by_inv_phi import transform_text as _inv_phi_transform_text

PHI = (1.0 + 5.0 ** 0.5) / 2.0

TRIAGE_JSON = ROOT / "ongoing_work" / "blind_spot_triage.json"
OUT_DIR = ROOT / "output" / "wythoff_sweep"
MANIFEST = OUT_DIR / "manifest.json"

print("=" * 80)
print("Stage 1: Index existing corpus signatures (output + master regulars)")
print("=" * 80)
corpus_sigs = {}
n_files = 0
for vz in (ROOT / "output" / "wythoff_sweep").rglob("*.vZome"):
    try:
        P, E = parse_vzome(vz)
        sig = shape_signature(P, E)
        corpus_sigs.setdefault(sig, []).append(str(vz.relative_to(ROOT)))
        n_files += 1
    except Exception:
        pass
for d in ["5cell", "8cell", "16cell", "24cell", "600cell", "120cell",
          "snub24cell", "grand_antiprism"]:
    p = ROOT / "output" / d
    if p.exists():
        for vz in p.glob("*.vZome"):
            try:
                P, E = parse_vzome(vz)
                sig = shape_signature(P, E)
                corpus_sigs.setdefault(sig, []).append(str(vz.relative_to(ROOT)))
                n_files += 1
            except Exception:
                pass
print(f"indexed {n_files} files across {len(corpus_sigs)} unique sigs")

print()
print("=" * 80)
print("Stage 2: Verify candidate_new_canonical Stage-B sigs from staged files")
print("=" * 80)
triage = json.loads(TRIAGE_JSON.read_text())
candidates = []
for rec in triage["results"]:
    if rec.get("status") != "candidate_new_canonical":
        continue
    src = ROOT / rec["staged_path"].replace("\\", "/")
    if not src.exists():
        print(f"  MISSING staged file: {src}; SKIP")
        continue
    P, E = parse_vzome(src)
    sig = shape_signature(P, E)
    # Note: triage script had a serialisation bug that stored sig_hash=None
    # in the JSON, but the in-memory sig was used correctly for corpus
    # lookup and intra-audit dedup, so the candidate set is reliable.
    # We re-derive sig from the staged file here (the source of truth).
    rec_sig_hash = rec.get("sig_hash")
    if rec_sig_hash and sig[2] != rec_sig_hash:
        print(f"  SIG MISMATCH for {src.name}: triage={rec_sig_hash} vs "
              f"recomputed={sig[2]}; SKIP")
        continue
    if sig in corpus_sigs:
        print(f"  fp={rec['fp_hash'][:10]} unexpectedly matches corpus "
              f"{corpus_sigs[sig][0]}; SKIP")
        continue
    slug = "_".join(rec["name"].split())
    candidates.append({
        "group": rec["group"],
        "bitmask": tuple(rec["bitmask"]),
        "source_polytope": rec["name"],
        "slug": slug,
        "src_path": src,
        "sig": sig,
        "kernel": tuple(rec["kernel"]),
        "fp_hash": rec["fp_hash"],
    })
    print(f"  {rec['name']:30s} fp={rec['fp_hash'][:10]} V={sig[0]} E={sig[1]} "
          f"kernel={list(rec['kernel'])}  KEEP")

print()
print("=" * 80)
print("Stage 3: Cross-polytope dedup among candidates")
print("=" * 80)
sig_seen = {}
for c in candidates:
    if c["sig"] in sig_seen:
        other = sig_seen[c["sig"]]
        print(f"  collision: {c['source_polytope']} vs {other['source_polytope']}")
        sys.exit(1)
    sig_seen[c["sig"]] = c
print(f"  no cross-polytope duplicates among {len(candidates)} candidates.")

print()
print("=" * 80)
print("Stage 4: Classify kernels and assign filenames")
print("=" * 80)
feat_cache = {}
classifications = []
for c in candidates:
    key = (c["group"], c["bitmask"])
    if key not in feat_cache:
        V, E = build_polytope(*key)
        feat_cache[key] = extract_features(np.asarray(V, dtype=float), E)
    feats = feat_cache[key]
    label, subtype = classify_kernel(np.asarray(c["kernel"]), feats)
    classifications.append((label, subtype))
    print(f"  {c['source_polytope']:30s} kernel={list(c['kernel'])}  ->  "
          f"({label}, {subtype})")

# Disambiguate within (slug, label, subtype): assign indices. Read existing
# manifest to skip already-used indices.
manifest = json.loads(MANIFEST.read_text())
existing_basenames = {}
for s in manifest["shapes"]:
    if s.get("status") != "ok":
        continue
    src = s.get("source_polytope")
    if src is None:
        continue
    slug = "_".join(src.split())
    key = (slug, s.get("label"), s.get("label_subtype"))
    fname = Path(s.get("file", "")).name
    parts = fname.replace(".vZome", "").split("_")
    idx = None
    if len(parts) >= 2:
        cand = parts[-2]
        if cand.isdigit() and len(cand) == 2:
            idx = int(cand)
    existing_basenames.setdefault(key, set())
    if idx is not None:
        existing_basenames[key].add(idx)

group_buckets = {}
for i, (c, (label, subtype)) in enumerate(zip(candidates, classifications)):
    key = (c["slug"], label, subtype)
    group_buckets.setdefault(key, []).append(i)

filenames = [None] * len(candidates)
for key, idxs in group_buckets.items():
    used = existing_basenames.get(key, set()).copy()
    for i in idxs:
        c = candidates[i]
        label, subtype = classifications[i]
        n = 0
        if len(idxs) > 1 or label == "oblique" or used:
            while n in used:
                n += 1
            used.add(n)
            basename = label_basename(label, subtype, index=n)
        else:
            basename = label_basename(label, subtype, index=None)
        h10 = c["sig"][2][:10]
        filenames[i] = f"{basename}_{h10}.vZome"
        print(f"  {c['source_polytope']:30s} -> {filenames[i]}")

print()
print("=" * 80)
print("Stage 5: Copy files into output/wythoff_sweep/<slug>/")
print("=" * 80)
dst_paths = []
for c, fname in zip(candidates, filenames):
    dst = OUT_DIR / c["slug"] / fname
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        print(f"  refuse to overwrite existing {dst}")
        sys.exit(1)
    shutil.copy2(c["src_path"], dst)
    dst_paths.append(dst)
    print(f"  copied {c['src_path'].name}")
    print(f"      -> {dst.relative_to(ROOT)}")


def _min_edge_length(path):
    P, E = parse_vzome(path)
    L = np.array([np.linalg.norm(P[i] - P[j]) for i, j in E])
    return float(L.min())


def _label_of_existing(path, manifest):
    """Look up (label, V) for an existing file in the manifest; return
    (label, V) or (None, None) if not found."""
    rel_target = path.relative_to(ROOT).as_posix().replace("/", os.sep)
    for s in manifest.get("shapes", []):
        if s.get("file") == rel_target:
            P, E = parse_vzome(path)
            return s.get("label"), len(P)
    return None, None


print()
print("=" * 80)
print("Stage 5b: Normalise physical scale within each polytope (* phi^-k)")
print("Pools files by (V, label) so that distinct projection classes")
print("(e.g. cell_first vs oblique) don't pollute one another's scale "
      "reference.  See M17b: the original logic pooled the entire slug "
      "folder, allowing face_first_square (V=52, min_edge=9.07) to set "
      "the target for V=96 oblique entries that should match the antiprism "
      "canonical scale 12.31.")
print("=" * 80)
slug_to_paths = defaultdict(list)
for c, dst in zip(candidates, dst_paths):
    slug_to_paths[c["slug"]].append(dst)

for slug, paths in slug_to_paths.items():
    folder = OUT_DIR / slug
    existing_existing_paths = [p for p in folder.glob("*.vZome") if p not in paths]

    # Build (V, label) buckets across new + existing.
    pool = defaultdict(list)
    for p in paths:
        # New entry: look up (label, V) from the in-memory candidates.
        for c, d, fname, (lab, _sub) in zip(
                candidates, dst_paths, filenames, classifications):
            if d == p:
                P, _ = parse_vzome(p)
                pool[(len(P), lab)].append(p)
                break
    for p in existing_existing_paths:
        lab, V = _label_of_existing(p, manifest)
        if lab is None:
            continue
        pool[(V, lab)].append(p)

    for (V, label), pool_paths in pool.items():
        edges = {p: _min_edge_length(p) for p in pool_paths}
        target = min(edges.values())
        new_in_pool = [p for p in pool_paths if p in paths]
        if not new_in_pool:
            continue
        print(f"  {slug} pool (V={V}, label={label!r}): target min_edge={target:.5f} "
              f"({len(pool_paths) - len(new_in_pool)} existing + {len(new_in_pool)} new)")
        for p in new_in_pool:
            m = edges[p]
            ratio = m / target
            if ratio < 1.001:
                print(f"    {p.name}: already at target ({m:.5f})")
                continue
            k = int(round(math.log(ratio, PHI)))
            if k <= 0 or abs(ratio - PHI ** k) > 0.01 * (PHI ** k):
                print(f"    {p.name}: WARNING ratio={ratio:.4f} not a clean "
                      f"power of phi -- LEAVING AS-IS")
                continue
            text = p.read_text(encoding="utf-8")
            for _ in range(k):
                text = _inv_phi_transform_text(text)
            p.write_text(text, encoding="utf-8")
            new_min = _min_edge_length(p)
            print(f"    {p.name}: was {m:.5f}, /phi^{k} -> {new_min:.5f}")
            P_new, E_new = parse_vzome(p)
            sig_new = shape_signature(P_new, E_new)
            for c, d in zip(candidates, dst_paths):
                if d == p and sig_new[2] != c["sig"][2]:
                    print(f"      FATAL: hash changed during rescale "
                          f"({c['sig'][2]} -> {sig_new[2]})")
                    sys.exit(1)

print()
print("=" * 80)
print("Stage 6: Append entries to manifest.json (rng=2 + Milestone 17 note)")
print("=" * 80)


def _strut_counts_from_vzome(path):
    P, E = parse_vzome(path)
    L = np.array([np.linalg.norm(P[i] - P[j]) for i, j in E])
    Lmin = L.min()
    ratios = np.round(L / Lmin, 4)
    palette = {1.0: "B", 1.4734: "G", 1.618: "Y", 1.7013: "R"}
    counts = Counter()
    for r in ratios:
        for k, c in palette.items():
            if abs(float(r) - k) < 5e-3:
                counts[c] += 1
                break
    return dict(counts)


new_entries = []
for c, (label, subtype), fname, dst in zip(
        candidates, classifications, filenames, dst_paths):
    rel = Path("wythoff_sweep") / c["slug"] / fname
    rec = {
        "fp_hash": c["sig"][2],
        "group": c["group"],
        "bitmask": list(c["bitmask"]),
        "source_polytope": c["source_polytope"],
        "shape_idx": None,
        "n_balls": c["sig"][0],
        "kernel": list(c["kernel"]),
        "label": label,
        "label_subtype": subtype,
        "rng": 2,
        "status": "ok",
        "file": str(rel).replace("/", os.sep),
        "strut_counts": _strut_counts_from_vzome(dst),
        "note": "Milestone 17 blind-spot audit (rng=2 descendant-direct).  "
                "Found by ongoing_work/probes/blind_spot_audit.py.",
    }
    new_entries.append(rec)
    print(f"  {c['source_polytope']:30s} {fname}  "
          f"label={label}/{subtype}  struts={rec['strut_counts']}")

manifest["shapes"].extend(new_entries)
manifest["n_ok"] = manifest.get("n_ok", 0) + len(new_entries)
manifest.setdefault("notes", []).append(
    f"Milestone 17 blind-spot audit (rng=2 descendant-direct): added "
    f"{len(new_entries)} new shape(s) from "
    + ", ".join(sorted({c['source_polytope'] for c in candidates}))
    + ".  Found by ongoing_work/probes/blind_spot_audit.py running search() "
    "directly against descendant edge sets, bypassing the parent-regular "
    "Step-1 filter in tools/run_wythoff_sweep.py.  Each entry carries rng=2."
)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True))
print(f"\n  manifest now has {len(manifest['shapes'])} shape entries "
      f"(n_ok={manifest['n_ok']}, n_fail={manifest.get('n_fail', 0)})")

print()
print("=" * 80)
print(f"PROMOTED {len(new_entries)} NEW SHAPES (Milestone 17 blind-spot audit).")
print("=" * 80)
