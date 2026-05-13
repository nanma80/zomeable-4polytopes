"""Deduplicate the prismatic-sweep corpus by 3D-shape congruence.

Background
----------
``lib/search_engine.shape_fingerprint`` (used during the prismatic
sweep's ``group_by_shape`` pass) rounds normalised pairwise squared
distances to 3 decimal places before forming the sorted-tuple
fingerprint. For congruent shapes whose projections differ by a 3D
rotation, numerical noise from ``projection_matrix``'s SVD basis can
push a handful of pairwise distances across that rounding boundary,
yielding distinct sorted tuples — so the sweep emits the same shape
twice. Empirically the gap is ~0.001 (exactly the round-to-3 quantum).

This script applies the more robust ``shape_signature`` from
``tools/dedup_corpus_by_shape.py`` (round-to-5 decimals + SHA-256 of
the full sorted distance array + edge-length multiset) directly to
the emitted .vZome files in the prismatic corpus.

What it does
------------
For each polytope subfolder mentioned in
``output/prismatic_manifest.json``:

  1. Parse every emitted .vZome via ``parse_vzome``.
  2. Compute ``shape_signature``.
  3. Group by signature; for each duplicate group, keep the entry
     with the smallest |kernel| L2 norm (ties broken by lex-smallest
     ``basename``).
  4. Delete the non-canonical .vZome files (unless ``--dry-run``).
  5. Append a corrected log entry per affected slug to
     ``ongoing_work/prismatic_sweep_log.jsonl`` so that
     ``build_prismatic_results.py`` / ``build_prismatic_doc.py`` will
     regenerate clean docs (those builders read the *latest* log
     record per slug).

Run ``build_prismatic_results.py`` and ``build_prismatic_doc.py``
afterwards to regenerate RESULTS.md per slug, PRISMATIC.md and
the manifest.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO_ROOT, "lib"))

from dedup_corpus_by_shape import parse_vzome, shape_signature  # noqa: E402
from polytope_features import label_basename  # noqa: E402


LOG_PATH = os.path.join(REPO_ROOT, "ongoing_work", "prismatic_sweep_log.jsonl")
MANIFEST_PATH = os.path.join(REPO_ROOT, "output", "prismatic_manifest.json")


def _latest_per_slug(log_path: str) -> "OrderedDict[str, dict]":
    recs: "OrderedDict[str, dict]" = OrderedDict()
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            slug = r.get("slug")
            if not slug:
                continue
            recs[slug] = r
    return recs


def _canonical_index(group_emits, manifest_paths_to_kernel):
    """Pick canonical emit: smallest |kernel|, then lex-smallest basename."""
    def key(emit):
        # Prefer the kernel from the manifest entry if available, else from the emit.
        k = emit.get("kernel")
        if k is None:
            return (float("inf"), emit.get("basename", ""))
        return (float(np.linalg.norm(np.array(k, dtype=float))),
                emit.get("basename", ""))

    return min(range(len(group_emits)), key=lambda i: key(group_emits[i]))


def dedup_prismatic(manifest_path: str, log_path: str, *, dry_run: bool = False,
                    verbose: bool = True) -> dict:
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    recs = _latest_per_slug(log_path)

    affected_slugs: list[str] = []
    total_dups_removed = 0
    total_files_deleted = 0
    per_slug_report: list[tuple[str, int, int]] = []

    for fam_letter, polys in manifest.get("families", {}).items():
        for poly in polys:
            slug = poly["slug"]
            shapes = poly.get("shapes", [])
            if len(shapes) < 2:
                continue

            sigs: "defaultdict[tuple, list[int]]" = defaultdict(list)
            for i, shape in enumerate(shapes):
                rel = shape.get("path")
                if not rel:
                    continue
                p = Path(REPO_ROOT) / rel
                if not p.exists():
                    if verbose:
                        print(f"  WARN {slug}: missing file {rel}", flush=True)
                    continue
                P, E = parse_vzome(p)
                sig = shape_signature(P, E)
                sigs[sig].append(i)

            keep_idxs: list[int] = []
            drop_idxs: list[int] = []
            for sig, idxs in sigs.items():
                if len(idxs) == 1:
                    keep_idxs.append(idxs[0])
                    continue
                group = [shapes[i] for i in idxs]
                local_canon = _canonical_index(group, None)
                canon_i = idxs[local_canon]
                keep_idxs.append(canon_i)
                for j in idxs:
                    if j != canon_i:
                        drop_idxs.append(j)

            if not drop_idxs:
                continue

            affected_slugs.append(slug)
            total_dups_removed += len(drop_idxs)
            per_slug_report.append((slug, len(shapes), len(keep_idxs)))

            # Delete the duplicate .vZome files
            for j in drop_idxs:
                rel = shapes[j].get("path")
                if not rel:
                    continue
                p = Path(REPO_ROOT) / rel
                if p.exists():
                    if dry_run:
                        if verbose:
                            print(f"  [dry-run] would delete {rel}", flush=True)
                    else:
                        p.unlink()
                        total_files_deleted += 1
                        if verbose:
                            print(f"  deleted {rel}", flush=True)

            # Renumber surviving shapes within each (label, subtype) group
            # so basenames remain consecutive (00, 01, ...) and singletons
            # drop their numeric suffix.  This matches label_basename's
            # original convention from run_prismatic_sweep.
            kept_sorted = sorted(keep_idxs,
                                 key=lambda i: shapes[i]["basename"])
            by_lbl: "defaultdict[tuple, list[int]]" = defaultdict(list)
            for i in kept_sorted:
                key = (shapes[i].get("label"), shapes[i].get("subtype"))
                by_lbl[key].append(i)

            rename_map: dict[str, str] = {}
            for (lbl, sub), idxs in by_lbl.items():
                if len(idxs) == 1:
                    new_base = label_basename(lbl, sub, None)
                    old_base = shapes[idxs[0]]["basename"]
                    if new_base != old_base:
                        rename_map[old_base] = new_base
                else:
                    for new_idx, i in enumerate(idxs):
                        new_base = label_basename(lbl, sub, new_idx)
                        old_base = shapes[i]["basename"]
                        if new_base != old_base:
                            rename_map[old_base] = new_base

            # Apply renames to files + manifest entries
            if rename_map:
                # First pass: rename to temporary names to avoid collisions
                # (e.g. when oblique_02 -> oblique_01 while oblique_01 still
                # exists as the deleted dup we just removed -- usually fine
                # because deletes happened above, but safe to be careful).
                for i in kept_sorted:
                    old_base = shapes[i]["basename"]
                    if old_base not in rename_map:
                        continue
                    new_base = rename_map[old_base]
                    rel_old = shapes[i].get("path")
                    if not rel_old:
                        continue
                    p_old = Path(REPO_ROOT) / rel_old
                    rel_new = rel_old.replace(
                        f"/{old_base}.vZome", f"/{new_base}.vZome")
                    p_new = Path(REPO_ROOT) / rel_new
                    if dry_run:
                        if verbose:
                            print(f"  [dry-run] would rename "
                                  f"{old_base}.vZome -> {new_base}.vZome "
                                  f"({slug})", flush=True)
                    elif p_old.exists():
                        p_old.rename(p_new)
                        if verbose:
                            print(f"  renamed {old_base}.vZome -> "
                                  f"{new_base}.vZome  ({slug})",
                                  flush=True)
                    shapes[i]["basename"] = new_base
                    shapes[i]["path"] = rel_new

            kept_basenames = {shapes[i]["basename"] for i in keep_idxs}
            old_to_new_basename = dict(rename_map)

            # Build a corrected log entry by filtering the latest log
            # record's emitted[] down to the surviving basenames.
            old_rec = recs.get(slug)
            if old_rec is None:
                if verbose:
                    print(f"  WARN {slug}: no log record; skipping log append",
                          flush=True)
                continue
            new_rec = dict(old_rec)
            old_emits = old_rec.get("emitted", [])
            # Drop dup emits, then apply renames to surviving ones.
            removed_basenames = {shapes[j]["basename"] for j in drop_idxs}
            new_emits = []
            for e in old_emits:
                if e.get("status") != "emitted":
                    new_emits.append(e)
                    continue
                base = e.get("basename")
                if base in removed_basenames:
                    continue
                if base in old_to_new_basename:
                    e = dict(e)
                    new_base = old_to_new_basename[base]
                    e["basename"] = new_base
                    p = e.get("path")
                    if p:
                        e["path"] = p.replace(
                            f"/{base}.vZome", f"/{new_base}.vZome")
                new_emits.append(e)
            new_rec["emitted"] = new_emits
            new_rec["unique_shapes"] = sum(
                1 for e in new_emits if e.get("status") == "emitted"
            )
            new_rec["dedup_pass"] = {
                "tool": "dedup_prismatic_by_shape",
                "applied_at": datetime.datetime.now(
                    datetime.timezone.utc).isoformat(),
                "before_emits": sum(1 for e in old_emits
                                    if e.get("status") == "emitted"),
                "after_emits": new_rec["unique_shapes"],
                "removed_basenames": sorted(removed_basenames),
                "renamed": old_to_new_basename,
            }

            if not dry_run:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(new_rec) + "\n")

            # Update manifest in place (so callers who don't rebuild
            # via build_prismatic_doc still see consistent state).
            poly["shapes"] = [shapes[i] for i in sorted(keep_idxs)]
            poly["n_shapes"] = len(poly["shapes"])

    if not dry_run and affected_slugs:
        # Note the dedup in the manifest itself
        notes = manifest.get("notes")
        notes = list(notes) if isinstance(notes, list) else []
        notes.append(
            f"dedup_prismatic_by_shape: {total_dups_removed} duplicate(s) "
            f"removed across {len(affected_slugs)} polytope(s) "
            f"({datetime.datetime.now(datetime.timezone.utc).isoformat()})"
        )
        manifest["notes"] = notes
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    return {
        "affected_slugs": affected_slugs,
        "total_dups_removed": total_dups_removed,
        "total_files_deleted": total_files_deleted,
        "per_slug": per_slug_report,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=MANIFEST_PATH)
    ap.add_argument("--log", default=LOG_PATH)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    stats = dedup_prismatic(args.manifest, args.log,
                            dry_run=args.dry_run,
                            verbose=not args.quiet)

    print()
    print("=== prismatic shape-congruence dedup ===")
    print(f"affected polytopes : {len(stats['affected_slugs'])}")
    print(f"duplicates removed : {stats['total_dups_removed']}")
    print(f"files deleted      : {stats['total_files_deleted']}"
          f" ({'dry-run' if args.dry_run else 'real'})")
    if stats["per_slug"]:
        print()
        print("Per-slug changes (before -> after):")
        for slug, before, after in stats["per_slug"]:
            print(f"  {slug:55s}  {before} -> {after}")
    if not args.dry_run and stats["affected_slugs"]:
        print()
        print("Now re-run:")
        print("  python tools/build_prismatic_doc.py")
        print("  python tools/relabel_corpus.py --kind prismatic")
        print("  python tools/build_prismatic_doc.py")
        print("  python tools/build_prismatic_results.py")
        print("  python tools/autofit_vzome_camera.py")


if __name__ == "__main__":
    main()
