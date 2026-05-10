"""Rename Wythoff-sweep .vZome files using kernel-direction classification.

Reads ``output/wythoff_sweep/manifest.json`` produced by
``tools/emit_novel.py``.  For each shape with status='ok':

  1. Build the source polytope's 4D vertex/edge data (cached per
     polytope for the run).
  2. Extract feature directions (vertex / edge midpoint / 2-face
     centroid / 3-cell centroid + types).
  3. Classify the shape's kernel direction against those features as
     one of:
         vertex_first
         cell_first[_<celltype>]    (e.g. cell_first_truncated_octahedron)
         face_first[_<polygon>]      (e.g. face_first_hexagon)
         edge_first
         oblique
  4. Rename the file to ``<label>[_<idx>]_<short_hash>.vZome`` within
     its existing per-polytope subfolder.  ``_<idx>`` is appended only
     when multiple shapes within the same polytope classify identically.
  5. Update the manifest entry's ``file`` path and add a ``label``
     field.

Run idempotently: a shape already on its target name is left alone.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

import numpy as np

from wythoff import build_polytope
from polytope_features import (
    PolytopeFeatures, classify_kernel, extract_features, label_basename,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "output" / "wythoff_sweep"
MANIFEST_PATH = OUT_DIR / "manifest.json"


def _features_for(group: str, bitmask: tuple[int, ...]
                  ) -> PolytopeFeatures:
    V, E = build_polytope(group, bitmask)
    return extract_features(np.asarray(V, dtype=float), E)


def _resolve_existing_path(rel: str) -> Path:
    """The manifest stores paths relative to ``output/`` with native
    separators; normalise to a Path under REPO_ROOT."""
    norm = rel.replace("\\", "/")
    return REPO_ROOT / "output" / norm


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", default=str(MANIFEST_PATH))
    p.add_argument("--dry-run", action="store_true",
                   help="report rename plan without renaming or "
                        "updating the manifest")
    args = p.parse_args(argv)

    manifest_path = Path(args.manifest)
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    shapes = [s for s in manifest["shapes"] if s.get("status") == "ok"]
    print(f"loaded {len(shapes)} ok-status shapes")

    # ------- Pass 1: classify each shape -------
    feat_cache: dict[tuple, PolytopeFeatures] = {}
    classifications: list[tuple[str, str | None]] = []
    grouped: dict[tuple, list[int]] = defaultdict(list)  # (group, bm, label, sub) -> indices into shapes

    for idx, shape in enumerate(shapes):
        key = (shape["group"], tuple(shape["bitmask"]))
        if key not in feat_cache:
            print(f"  building features for {key[0]} {key[1]} "
                  f"({shape['source_polytope']})...")
            feat_cache[key] = _features_for(*key)
        feats = feat_cache[key]
        kernel = np.asarray(shape["kernel"], dtype=float)
        label, subtype = classify_kernel(kernel, feats)
        classifications.append((label, subtype))
        grouped[(*key, label, subtype)].append(idx)

    # ------- Pass 2: assign basenames, suffixing _<idx> if needed -------
    new_basenames: list[str] = [""] * len(shapes)
    for key, idxs in grouped.items():
        if len(idxs) == 1:
            i = idxs[0]
            label, subtype = classifications[i]
            new_basenames[i] = label_basename(label, subtype, index=None)
        else:
            for n, i in enumerate(idxs):
                label, subtype = classifications[i]
                new_basenames[i] = label_basename(label, subtype,
                                                  index=n)

    # ------- Pass 3: rename + update manifest entries -------
    # Use a two-phase rename: first move every file that needs to change to
    # a unique scratch name, then move from scratch -> final target.  This
    # is robust to within-polytope index renumbering (e.g. after a dedup
    # pass collapsed some shapes, surviving _<idx> values shift down and
    # the desired target may currently hold a different file that itself
    # is being renamed).
    counts = defaultdict(int)
    plan: list[tuple[Path, Path, dict, str, str | None]] = []
    for shape, basename, (label, subtype) in zip(
            shapes, new_basenames, classifications):
        rel = shape["file"]
        old_path = _resolve_existing_path(rel)
        if not old_path.exists():
            print(f"  WARNING: {old_path} not found; skipping")
            continue
        short = shape["fp_hash"][:10]
        new_fname = f"{basename}_{short}.vZome"
        new_path = old_path.parent / new_fname

        shape["label"] = label
        shape["label_subtype"] = subtype
        if new_path == old_path:
            counts["unchanged"] += 1
            # record file path is unchanged
            continue
        plan.append((old_path, new_path, shape, label, subtype))

    # Phase A: move sources to unique scratch names so their old slots are
    # freed before any final move runs.  Scratch names use a temporary
    # suffix that cannot collide with our final names (which all end in
    # ``_<10-hex-hash>.vZome``).
    scratch_pairs: list[tuple[Path, Path, dict]] = []
    for old_path, new_path, shape, label, subtype in plan:
        scratch = old_path.with_name(f"__renaming__.{old_path.name}")
        if not args.dry_run:
            os.rename(old_path, scratch)
        scratch_pairs.append((scratch, new_path, shape))

    # Phase B: move scratch -> final.  A collision now would mean two
    # surviving shapes legitimately share a target name, which should
    # never happen with a correct (label, subtype, index) assignment.
    for scratch, new_path, shape in scratch_pairs:
        if new_path.exists() and not args.dry_run:
            print(f"  WARNING: target {new_path} already exists; "
                  f"leaving scratch {scratch.name} in place")
            counts["collision"] += 1
            continue
        if not args.dry_run:
            os.rename(scratch, new_path)
        rel_to_output = new_path.relative_to(REPO_ROOT / "output")
        shape["file"] = str(rel_to_output)
        counts["renamed"] += 1

    if not args.dry_run:
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)

    print(f"\n  renamed:    {counts['renamed']}")
    print(f"  unchanged:  {counts['unchanged']}")
    print(f"  collision:  {counts['collision']}")
    print(f"  dry_run:    {args.dry_run}")
    print(f"  manifest:   {manifest_path}")

    # Print label distribution.
    label_counts = defaultdict(int)
    for label, subtype in classifications:
        key = label if subtype is None else f"{label}_{subtype}"
        label_counts[key] += 1
    print("\n  label distribution:")
    for k in sorted(label_counts):
        print(f"    {label_counts[k]:4d}  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
