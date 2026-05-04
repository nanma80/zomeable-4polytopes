"""Deduplicate the wythoff_sweep corpus by kernel *direction*.

Background
----------
``shape_fingerprint`` in ``lib/search_engine.py`` is intended to be a
rotation+scale invariant 3D-shape hash, but it is in practice sensitive
to the basis chosen by ``np.linalg.svd`` inside ``projection_matrix``.
When the kernel ``n`` has degenerate singular values for ``I - n n^T``
(always the case here: three eigenvalues are 1.0), small FP perturbations
in the input ``n`` shuffle the basis order, yielding slightly different
3D coordinates for the same projected shape.

In the manifest, kernel coordinates are stored as 4-decimal floats.  Two
exact ``Z[phi]^4`` kernels that are positive scalar multiples of each
other (e.g. ``k`` and ``phi^2 * k``) round to *slightly* different unit
vectors after this lossy storage, so their fingerprints collide ~ but
not exactly ~ producing distinct ``fp_hash`` values for what is in fact
a single 3D shape.

This tool collapses such duplicates to a single canonical entry per
direction.  Canonical representative: the kernel with the smallest L2
norm in the duplicate group (the simplest integer Z[phi] direction).

Action
------
* Scan ``output/wythoff_sweep/manifest.json``.
* Per source-polytope, group ok-status shapes by direction (cos>1-1e-6).
* Keep the canonical (smallest |k|) shape, mark the rest as duplicates.
* Delete the duplicate ``.vZome`` files on disk.
* Rewrite the manifest with a backup at ``manifest.json.predup.bak``.
* Append a ``deduplicated_by_direction`` flag and ``aliases`` list (the
  removed fp_hashes) to each surviving entry.
"""
from __future__ import annotations

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np
from numpy.linalg import norm


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--manifest",
                   default="output/wythoff_sweep/manifest.json",
                   help="Path to manifest.json")
    p.add_argument("--corpus-root",
                   default="output",
                   help="Root directory the manifest's 'file' entries are relative to")
    p.add_argument("--cos-tol",
                   type=float,
                   default=1e-6,
                   help="Cosine tolerance: kernels with cos > 1-cos_tol "
                        "are treated as the same direction.")
    p.add_argument("--dry-run",
                   action="store_true",
                   help="Report what would change without modifying disk.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    corpus_root = Path(args.corpus_root)

    with manifest_path.open("r", encoding="utf-8") as f:
        m = json.load(f)
    shapes = m.get("shapes", [])
    print(f"loaded manifest: {len(shapes)} shape entries")

    by_poly: dict[tuple, list[int]] = defaultdict(list)
    for i, s in enumerate(shapes):
        if s.get("status") != "ok":
            continue
        key = (s["group"], tuple(s["bitmask"]))
        by_poly[key].append(i)

    surviving_indices: list[int] = []
    removed: list[dict] = []
    aliases_for: dict[int, list[str]] = defaultdict(list)

    for key, idxs in sorted(by_poly.items()):
        if len(idxs) <= 1:
            surviving_indices.extend(idxs)
            continue
        K = np.asarray([shapes[i]["kernel"] for i in idxs], dtype=float)
        Ku = K / np.maximum(norm(K, axis=1, keepdims=True), 1e-12)
        seen = np.zeros(len(idxs), dtype=bool)
        for local_i in range(len(idxs)):
            if seen[local_i]:
                continue
            sim_local = np.where((Ku @ Ku[local_i]) > 1 - args.cos_tol)[0]
            seen[sim_local] = True
            group_global = [idxs[j] for j in sim_local]
            # canonical = smallest L2 norm (= simplest direction)
            norms = [norm(shapes[g]["kernel"]) for g in group_global]
            canon = group_global[int(np.argmin(norms))]
            surviving_indices.append(canon)
            for g in group_global:
                if g == canon:
                    continue
                aliases_for[canon].append(shapes[g]["fp_hash"])
                removed.append(shapes[g])

    # also keep all non-ok entries (failures) in the new manifest verbatim
    non_ok = [i for i, s in enumerate(shapes) if s.get("status") != "ok"]
    surviving_indices.sort()

    print(f"surviving ok shapes: {len(surviving_indices)} "
          f"(was {sum(1 for s in shapes if s.get('status') == 'ok')})")
    print(f"removed duplicates:  {len(removed)}")

    # ---- file deletions --------------------------------------------------
    deleted = 0
    missing = 0
    for s in removed:
        rel = s.get("file")
        if not rel:
            continue
        p = corpus_root / rel
        if p.exists():
            if args.dry_run:
                pass
            else:
                p.unlink()
            deleted += 1
        else:
            missing += 1
    print(f"deleted vZome files: {deleted} ({'dry-run' if args.dry_run else 'real'}); missing: {missing}")

    # ---- new manifest ----------------------------------------------------
    new_shapes: list[dict] = []
    for i in non_ok + surviving_indices:
        s = dict(shapes[i])
        if i in aliases_for:
            s["aliases"] = sorted(aliases_for[i])
            s["alias_count"] = len(aliases_for[i])
        new_shapes.append(s)
    # preserve original ordering: sort by (status, group, bitmask, fp_hash)
    new_shapes.sort(key=lambda s: (
        0 if s.get("status") == "ok" else 1,
        s.get("group", ""),
        tuple(s.get("bitmask", ())),
        s.get("fp_hash", ""),
    ))

    new_m = dict(m)
    new_m["shapes"] = new_shapes
    notes = list(new_m.get("notes", []) if isinstance(new_m.get("notes"), list) else [])
    notes.append("deduplicated by kernel direction "
                 f"(cos>1-{args.cos_tol}): "
                 f"{len(removed)} aliases collapsed into {len(aliases_for)} canonical entries")
    new_m["notes"] = notes

    if args.dry_run:
        print("DRY-RUN: would update", manifest_path)
    else:
        bak = manifest_path.with_suffix(manifest_path.suffix + ".predup.bak")
        if not bak.exists():
            shutil.copy2(manifest_path, bak)
            print("backup written:", bak)
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(new_m, f, indent=2)
        print("manifest updated:", manifest_path)


if __name__ == "__main__":
    main()
