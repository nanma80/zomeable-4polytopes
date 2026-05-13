"""Re-classify and rename .vZome files using updated ``classify_kernel``.

Background
----------
``lib.polytope_features.classify_kernel`` previously defaulted to
``tol=5e-3`` (cos > 0.995, ~5.7 deg) when matching a kernel direction
to a feature direction (vertex / cell-centroid / face-centroid /
edge-midpoint).  For kernels in ZZ[phi]^4 and feature directions in
QQ[phi]^4 (means of integer ZZ[phi] vertex coords), genuine
parallelism gives ``cos = 1 +/- ~1e-14``: the original tolerance was
~12 orders of magnitude looser than needed and ended up labeling
kernels that were merely *close* to a feature direction.  In the
visual projection, the feature centroid then lands *near* but not
*at* the projected origin -- e.g. ``icosidodecahedron_prism`` with
kernel ``(0, 1, 1/phi, 1/phi^2)`` is 2.7 deg off the nearest
pentagon-centroid direction so was labeled ``face_first_pentagon``
even though no pentagon actually projects to the centre.

After tightening the tolerance to ``1e-6`` in ``polytope_features``,
this tool walks an existing manifest (prismatic or wythoff_sweep),
re-runs ``classify_kernel`` on every shape's kernel, and:

  1. computes a new ``(label, subtype)`` per shape
  2. renumbers basenames within each (label, subtype) group of a
     polytope so they follow the ``label_basename`` convention
     (singleton -> no suffix; multi -> ``_00, _01, ...``)
  3. renames the ``.vZome`` files on disk
  4. updates the manifest entries' ``label`` / ``subtype`` /
     ``label_subtype`` / ``basename`` / ``path`` / ``file`` fields
  5. (prismatic only) appends a corrected log record to
     ``ongoing_work/prismatic_sweep_log.jsonl`` so subsequent
     ``build_prismatic_doc.py`` runs regenerate consistent docs.

Idempotent: shapes already on their target basename are left alone.
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
REPO_ROOT = Path(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO_ROOT, "lib"))

from polytope_features import (  # noqa: E402
    PolytopeFeatures, classify_kernel, extract_features, label_basename,
)


# ---------------------------------------------------------------------------
# Polytope dispatch
# ---------------------------------------------------------------------------

def _build_prismatic(slug: str):
    from polytopes_prismatic import (
        polyhedral_prism, duoprism, antiprismatic_prism,
    )
    if slug.startswith("duoprism_"):
        _, p, q = slug.split("_")
        return duoprism(int(p), int(q))
    if slug.endswith("_antiprismatic_prism"):
        n = int(slug.split("_")[0])
        return antiprismatic_prism(n)
    if slug.endswith("_prism"):
        name = slug[: -len("_prism")]
        return polyhedral_prism(name)
    raise ValueError(f"unrecognised prismatic slug: {slug}")


def _build_wythoff(group: str, bitmask):
    from wythoff import build_polytope
    return build_polytope(group, tuple(bitmask))


# ---------------------------------------------------------------------------
# Feature cache
# ---------------------------------------------------------------------------

class FeatureCache:
    def __init__(self, kind: str):
        self.kind = kind
        self._c: dict[tuple, PolytopeFeatures] = {}

    def get(self, key, builder):
        if key in self._c:
            return self._c[key]
        V, E = builder()
        feats = extract_features(np.asarray(V, dtype=float), E)
        self._c[key] = feats
        return feats


# ---------------------------------------------------------------------------
# Prismatic relabel
# ---------------------------------------------------------------------------

def _kernel_norm(shape: dict) -> float:
    k = shape.get("kernel")
    if k is None:
        return float("inf")
    return float(np.linalg.norm(np.array(k, dtype=float)))


def _assign_stable_basenames(
        idxs: list[int],
        new_class: list[tuple[str, str | None]],
        old_basenames: list[str],
        kernel_norms: list[float],
        label_basename_fn,
        slug_prefix: str = "",
) -> list[str]:
    """Assign new basenames using a stable-anchor algorithm.

    For each new (label, subtype) group within ``idxs``:

      * If size == 1: basename is ``label[_<subtype>]`` (no index).
      * If size >= 2: members whose OLD basename already conforms to the
        convention (``label[_<subtype>]_NN`` with NN < group_size and
        unique across the group) keep their index.  Remaining members
        are assigned the smallest unused indices in order of
        (kernel_norm, old_basename).

    This minimises disturbance: shapes that were already correctly
    indexed within their group stay put, only newly-relabeled or
    misnumbered members move.

    ``slug_prefix`` is prepended to the basename for wythoff
    manifests (e.g. ``"cantellated_5cell_"``).  Empty for prismatic.
    """
    from collections import defaultdict

    # Group indices (positions in idxs, not raw shape ids)
    groups: defaultdict[tuple, list[int]] = defaultdict(list)
    for pos, _ in enumerate(idxs):
        groups[new_class[pos]].append(pos)

    new_basenames: list[str] = [""] * len(idxs)
    for (lbl, sub), members in groups.items():
        target_tail = label_basename_fn(lbl, sub, None)  # no suffix
        N = len(members)
        if N == 1:
            new_basenames[members[0]] = slug_prefix + target_tail
            continue

        # N >= 2: parse old basenames for valid indexed conformance.
        # Strip optional slug prefix to get the tail.
        used: dict[int, int] = {}  # pos -> index
        # Build prefix string to detect
        # The indexed convention: f"{target_tail}_{NN}" where NN is 2-digit
        for pos in members:
            base = old_basenames[pos]
            if slug_prefix and base.startswith(slug_prefix):
                tail = base[len(slug_prefix):]
            else:
                tail = base
            if not tail.startswith(target_tail + "_"):
                continue
            suffix = tail[len(target_tail) + 1:]
            if not (suffix.isdigit() and len(suffix) >= 2):
                continue
            n = int(suffix)
            if 0 <= n < N and n not in used.values():
                used[pos] = n

        # Assign remaining positions to lowest unused indices.
        unassigned = [p for p in members if p not in used]
        unassigned.sort(key=lambda p: (kernel_norms[p], old_basenames[p]))
        available = [n for n in range(N) if n not in set(used.values())]
        for p, n in zip(unassigned, available):
            used[p] = n

        for pos, n in used.items():
            tail = label_basename_fn(lbl, sub, n)
            new_basenames[pos] = slug_prefix + tail

    return new_basenames


def relabel_prismatic(manifest_path: Path, log_path: Path, *,
                      dry_run: bool, verbose: bool) -> dict:
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    cache = FeatureCache("prismatic")
    # Slugs where ANY (label, subtype) was refreshed. We must update the log
    # for these regardless of whether basenames changed, otherwise the next
    # `build_prismatic_doc` run will re-introduce stale label/subtype.
    relabel_slugs: list[str] = []
    affected_slugs: list[str] = []  # subset with file renames
    total_files_renamed = 0
    rename_log: list[tuple[str, str, str]] = []  # (slug, old, new)
    per_slug_rename_maps: dict[str, dict] = {}

    for fam, polys in manifest.get("families", {}).items():
        for poly in polys:
            slug = poly["slug"]
            shapes = poly.get("shapes", [])
            if not shapes:
                continue

            feats = cache.get((slug,), lambda s=slug: _build_prismatic(s))

            # Pass 1: re-classify every shape
            new_class: list[tuple[str, str | None]] = []
            old_basenames: list[str] = []
            kernel_norms: list[float] = []
            changed_any = False
            for s in shapes:
                k = np.array(s["kernel"], dtype=float)
                lbl, sub = classify_kernel(k, feats)
                new_class.append((lbl, sub))
                old_basenames.append(s.get("basename", ""))
                kernel_norms.append(_kernel_norm(s))
                if (lbl, sub) != (s.get("label"), s.get("subtype")):
                    changed_any = True

            if not changed_any:
                continue

            relabel_slugs.append(slug)

            # Pass 2: stable-anchor basename assignment
            idxs = list(range(len(shapes)))
            new_basenames = _assign_stable_basenames(
                idxs, new_class, old_basenames, kernel_norms,
                label_basename, slug_prefix="",
            )

            # Apply: rename files + update manifest entries
            rename_map: dict[str, str] = {}
            two_phase: list[tuple[Path, Path]] = []
            for i, s in enumerate(shapes):
                old_base = s.get("basename")
                new_base = new_basenames[i]
                # Always refresh label/subtype from the new classification,
                # regardless of whether the basename changed. The basename
                # may stay stable (e.g. (oblique, None) -> (oblique, None))
                # while subtype changes due to feature improvements; we
                # must keep label/subtype synced with the kernel.
                s["label"] = new_class[i][0]
                s["subtype"] = new_class[i][1]
                if old_base == new_base:
                    continue
                rename_map[old_base] = new_base
                rel_old = s.get("path")
                if rel_old:
                    rel_new = rel_old.replace(
                        f"/{old_base}.vZome", f"/{new_base}.vZome")
                    two_phase.append((Path(REPO_ROOT) / rel_old,
                                      Path(REPO_ROOT) / rel_new))
                    s["path"] = rel_new
                s["basename"] = new_base
                rename_log.append((slug, old_base, new_base))
                total_files_renamed += 1

            if rename_map:
                affected_slugs.append(slug)
                per_slug_rename_maps[slug] = rename_map
            else:
                per_slug_rename_maps[slug] = {}

            # Renames: do via two-phase swap through temp names to handle
            # cycles (e.g. when an oblique_00 needs to swap places with
            # an oblique_01 inside the same polytope).
            if not dry_run and two_phase:
                temps: list[tuple[Path, Path]] = []
                for p_old, p_new in two_phase:
                    if not p_old.exists():
                        if verbose:
                            print(f"  WARN {slug}: missing source {p_old}",
                                  flush=True)
                        continue
                    p_tmp = p_old.with_suffix(".vZome.tmp_relabel")
                    p_old.rename(p_tmp)
                    temps.append((p_tmp, p_new))
                for p_tmp, p_new in temps:
                    p_tmp.rename(p_new)
            if verbose and rename_map:
                print(f"[{slug}]", flush=True)
                for old, new in rename_map.items():
                    print(f"   {old}.vZome -> {new}.vZome", flush=True)
            elif verbose and not rename_map:
                print(f"[{slug}] (label/subtype refreshed, no file rename)",
                      flush=True)

    # Update manifest on disk
    if not dry_run and relabel_slugs:
        notes = manifest.get("notes")
        notes = list(notes) if isinstance(notes, list) else []
        notes.append(
            "relabel_corpus: classify_kernel tightened from tol=5e-3 to "
            "tol=1e-6; "
            f"{total_files_renamed} basename(s) corrected across "
            f"{len(affected_slugs)} polytope(s); "
            f"label/subtype refreshed across {len(relabel_slugs)} polytope(s) "
            f"({datetime.datetime.now(datetime.timezone.utc).isoformat()})"
        )
        manifest["notes"] = notes
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    # Append corrected log records (prismatic only).  ALL slugs whose
    # classification refreshed must get a corrected log record, not just
    # those with file renames -- otherwise the next build_prismatic_doc
    # run would re-introduce stale label/subtype.
    if not dry_run and relabel_slugs and log_path.exists():
        recs = _latest_per_slug_jsonl(log_path)
        # Build a slug -> {basename -> (label, subtype)} lookup with the
        # freshly-classified values from the in-memory manifest.
        slug_to_fresh: dict[str, dict[str, tuple[str, str | None]]] = {}
        for fam, polys in manifest.get("families", {}).items():
            for poly in polys:
                slug = poly["slug"]
                fresh: dict[str, tuple[str, str | None]] = {}
                for s in poly.get("shapes", []):
                    fresh[s["basename"]] = (s.get("label"), s.get("subtype"))
                slug_to_fresh[slug] = fresh
        with log_path.open("a", encoding="utf-8") as f:
            for slug in relabel_slugs:
                old_rec = recs.get(slug)
                if old_rec is None:
                    continue
                new_rec = dict(old_rec)
                old_emits = old_rec.get("emitted", [])
                new_emits = []
                rename_map = per_slug_rename_maps.get(slug, {})
                fresh_lookup = slug_to_fresh.get(slug, {})
                for e in old_emits:
                    if e.get("status") != "emitted":
                        new_emits.append(e)
                        continue
                    base = e.get("basename")
                    e = dict(e)
                    if base in rename_map:
                        new_base = rename_map[base]
                        e["basename"] = new_base
                        p = e.get("path")
                        if p:
                            e["path"] = p.replace(
                                f"/{base}.vZome", f"/{new_base}.vZome")
                    # Always rewrite label/subtype from the freshly-classified
                    # values. The principle is: ground truth = kernel; label
                    # is derived fresh from it via classify_kernel.
                    fresh_lbl = fresh_lookup.get(e["basename"])
                    if fresh_lbl is not None:
                        e["label"] = fresh_lbl[0]
                        e["subtype"] = fresh_lbl[1]
                    new_emits.append(e)
                new_rec["emitted"] = new_emits
                new_rec["relabel_pass"] = {
                    "tool": "relabel_corpus (prismatic)",
                    "applied_at": datetime.datetime.now(
                        datetime.timezone.utc).isoformat(),
                    "renamed": rename_map,
                }
                f.write(json.dumps(new_rec) + "\n")

    return {
        "affected_slugs": affected_slugs,
        "relabel_slugs": relabel_slugs,
        "total_files_renamed": total_files_renamed,
        "rename_log": rename_log,
    }

    return {
        "affected_slugs": affected_slugs,
        "total_files_renamed": total_files_renamed,
        "rename_log": rename_log,
    }


def _latest_per_slug_jsonl(log_path: Path) -> "OrderedDict[str, dict]":
    recs: "OrderedDict[str, dict]" = OrderedDict()
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            slug = r.get("slug")
            if slug:
                recs[slug] = r
    return recs


# ---------------------------------------------------------------------------
# Wythoff relabel
# ---------------------------------------------------------------------------

def _wythoff_slug_basename(file_rel: str) -> tuple[str, str]:
    """Given e.g. 'cantellated_5cell/cantellated_5cell_face_first_square.vZome',
    return ('cantellated_5cell', 'cantellated_5cell_face_first_square')."""
    parts = file_rel.replace("\\", "/").split("/")
    slug = parts[0]
    leaf = parts[-1]
    if leaf.endswith(".vZome"):
        leaf = leaf[: -len(".vZome")]
    return slug, leaf


def _resolve_wythoff_path(file_rel: str) -> tuple[Path | None, str]:
    """Find the actual on-disk path for a wythoff_sweep manifest file.

    The manifest stores paths relative to ``output/`` but the corpus
    was later reorganised into category subfolders (``uniform/``,
    ``regular/``) without updating the manifest.  Try each candidate
    root and return ``(absolute_path, new_relative_path)`` where
    new_relative_path includes the discovered prefix.  Returns
    ``(None, file_rel)`` if no candidate exists.
    """
    norm = file_rel.replace("\\", "/")
    for prefix in ("", "uniform/", "regular/"):
        candidate = REPO_ROOT / "output" / (prefix + norm)
        if candidate.exists():
            return candidate, prefix + norm
    return None, norm


def relabel_wythoff(manifest_path: Path, *, dry_run: bool, verbose: bool
                    ) -> dict:
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    shapes = manifest.get("shapes", [])
    cache = FeatureCache("wythoff")

    # Group shapes by (group, bitmask) i.e. polytope identity
    poly_groups: defaultdict[tuple, list[int]] = defaultdict(list)
    for i, s in enumerate(shapes):
        if s.get("group") is None or s.get("bitmask") is None:
            continue
        if s.get("status") and s["status"] != "ok":
            # snap_failed / other non-emitted entries have no .vZome file.
            continue
        if "file" not in s:
            continue
        key = (s["group"], tuple(s["bitmask"]))
        poly_groups[key].append(i)

    affected_slugs: list[str] = []
    rename_log: list[tuple[str, str, str]] = []
    total_files_renamed = 0
    per_slug_rename_maps: dict[str, dict] = {}

    for key, idxs in poly_groups.items():
        group, bitmask = key
        feats = cache.get(key, lambda k=key: _build_wythoff(k[0], k[1]))

        # Re-classify
        new_class = []
        old_basenames = []
        old_files = []
        resolved_dir_prefixes = []  # "uniform/" / "regular/" / "" per shape
        slug_for_subfolder = None
        changed_any = False
        for i in idxs:
            s = shapes[i]
            k = np.array(s["kernel"], dtype=float)
            lbl, sub = classify_kernel(k, feats)
            new_class.append((lbl, sub))
            sl, old_base = _wythoff_slug_basename(s["file"])
            if slug_for_subfolder is None:
                slug_for_subfolder = sl
            old_basenames.append(old_base)
            old_files.append(s["file"])
            # Resolve actual on-disk location
            _, resolved_rel = _resolve_wythoff_path(s["file"])
            # Capture only the prefix portion (e.g. "uniform/").
            norm = s["file"].replace("\\", "/")
            prefix = resolved_rel[: len(resolved_rel) - len(norm)] \
                if resolved_rel.endswith(norm) else ""
            resolved_dir_prefixes.append(prefix)
            if (lbl, sub) != (s.get("label"), s.get("label_subtype")):
                changed_any = True

        # Always normalise the manifest "file" paths to include the
        # resolved prefix, even if classification didn't change.
        # (Idempotent: a re-run becomes a no-op once prefixes are set.)
        paths_already_synced = all(
            shapes[ii].get("file", "").startswith(resolved_dir_prefixes[jj])
            and resolved_dir_prefixes[jj] != ""
            for jj, ii in enumerate(idxs)
        ) if any(p for p in resolved_dir_prefixes) else True

        if not changed_any and paths_already_synced:
            continue

        # Pass 2: stable-anchor basename assignment
        kernel_norms = [_kernel_norm(shapes[i]) for i in idxs]
        slug_prefix = f"{slug_for_subfolder}_"
        # Use position-indexed working arrays for the helper.
        new_basenames = _assign_stable_basenames(
            list(range(len(idxs))), new_class, old_basenames,
            kernel_norms, label_basename, slug_prefix=slug_prefix,
        )

        rename_map: dict[str, str] = {}
        two_phase: list[tuple[Path, Path]] = []
        for jj, ii in enumerate(idxs):
            s = shapes[ii]
            old_base = old_basenames[jj]
            new_base = new_basenames[jj]
            old_file = old_files[jj]
            prefix = resolved_dir_prefixes[jj]
            # Compute the new manifest file path (with prefix) and
            # the on-disk paths to rename.
            old_file_with_prefix = prefix + old_file if not old_file.startswith(prefix) else old_file
            new_file_with_prefix = old_file_with_prefix.replace(
                f"/{old_base}.vZome", f"/{new_base}.vZome")
            label_changed = (s.get("label"), s.get("label_subtype")) != new_class[jj]
            path_synced = s.get("file", "") == new_file_with_prefix
            if old_base == new_base and not label_changed and path_synced:
                continue
            if old_base != new_base:
                rename_map[old_base] = new_base
                two_phase.append((REPO_ROOT / "output" / old_file_with_prefix,
                                  REPO_ROOT / "output" / new_file_with_prefix))
                rename_log.append((slug_for_subfolder, old_base, new_base))
                total_files_renamed += 1
            s["file"] = new_file_with_prefix
            s["label"] = new_class[jj][0]
            s["label_subtype"] = new_class[jj][1]

        if rename_map:
            affected_slugs.append(slug_for_subfolder)
            per_slug_rename_maps[slug_for_subfolder] = rename_map

        if not dry_run and two_phase:
            temps: list[tuple[Path, Path]] = []
            for p_old, p_new in two_phase:
                if not p_old.exists():
                    if verbose:
                        print(f"  WARN {slug_for_subfolder}: missing "
                              f"source {p_old}", flush=True)
                    continue
                p_tmp = p_old.with_suffix(".vZome.tmp_relabel")
                p_old.rename(p_tmp)
                temps.append((p_tmp, p_new))
            for p_tmp, p_new in temps:
                p_tmp.rename(p_new)
        if verbose and rename_map:
            print(f"[{slug_for_subfolder}]", flush=True)
            for old, new in rename_map.items():
                print(f"   {old}.vZome -> {new}.vZome", flush=True)

    if not dry_run and affected_slugs:
        notes = manifest.get("notes")
        notes = list(notes) if isinstance(notes, list) else []
        notes.append(
            "relabel_corpus: classify_kernel tightened from tol=5e-3 to "
            "tol=1e-6; "
            f"{total_files_renamed} basename(s) corrected across "
            f"{len(affected_slugs)} polytope(s) "
            f"({datetime.datetime.now(datetime.timezone.utc).isoformat()})"
        )
        manifest["notes"] = notes
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    return {
        "affected_slugs": affected_slugs,
        "total_files_renamed": total_files_renamed,
        "rename_log": rename_log,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kind", choices=["prismatic", "wythoff"], required=True)
    ap.add_argument("--manifest", default=None,
                    help="path to manifest; defaults based on --kind")
    ap.add_argument("--log",
                    default=str(REPO_ROOT / "ongoing_work"
                                / "prismatic_sweep_log.jsonl"),
                    help="prismatic sweep log path (only used when "
                         "--kind=prismatic)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.manifest:
        manifest_path = Path(args.manifest)
    elif args.kind == "prismatic":
        manifest_path = REPO_ROOT / "output" / "prismatic_manifest.json"
    else:
        manifest_path = REPO_ROOT / "output" / "wythoff_sweep_manifest.json"

    if args.kind == "prismatic":
        stats = relabel_prismatic(manifest_path, Path(args.log),
                                  dry_run=args.dry_run,
                                  verbose=not args.quiet)
    else:
        stats = relabel_wythoff(manifest_path,
                                dry_run=args.dry_run,
                                verbose=not args.quiet)

    print()
    print(f"=== relabel_corpus ({args.kind}) ===")
    print(f"affected polytopes : {len(stats['affected_slugs'])}")
    print(f"files renamed      : {stats['total_files_renamed']}"
          f" ({'dry-run' if args.dry_run else 'real'})")
    if stats["rename_log"]:
        print()
        print("Rename log (slug | old | new):")
        for slug, old, new in stats["rename_log"]:
            print(f"  {slug:55s}  {old:35s}  ->  {new}")
    if args.dry_run and stats["rename_log"]:
        print("\n(dry-run; re-run without --dry-run to apply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
