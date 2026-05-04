"""Deduplicate the wythoff_sweep corpus by *3D-shape congruence*.

Background
----------
``shape_fingerprint`` in ``lib/search_engine.py`` was supposed to produce
a single hash per congruence class of 3D projected shapes, but in practice
it produces *many* distinct hashes for shapes that are H4-orbit-related
(rigid-motion equivalent).  Two failure modes:

  * Kernels that are positive scalar multiples of each other route through
    different SVD bases inside ``projection_matrix`` because the eigenvalue
    structure of ``I - n n^T`` is degenerate (three eigenvalues = 1).
    ``dedup_corpus_by_direction.py`` already handles this case by direction.

  * Kernels that are H4-orbit-equivalent but *not* scalar multiples
    (e.g. three cell-centroid directions of the bitruncated 120-cell
    sitting at pairwise cos = +/- 1/2) project to congruent point sets
    in 3D, but with different orientation.  The pairwise distance multiset
    is identical to high precision, but the lossy 3-decimal binning in
    ``shape_fingerprint`` drifts at boundary-distances and yields
    different fp_hashes.  ``dedup_corpus_by_direction.py`` cannot catch
    this case.

This tool collapses both cases by computing a robust congruence
fingerprint directly from the emitted .vZome geometry:

  (a) Sorted multiset of pairwise vertex-vertex squared-distances,
      normalised by the smallest non-zero squared distance, rounded to
      ``--dist-decimals``.  This is invariant under rotation, reflection
      and uniform scale.
  (b) Sorted multiset of edge lengths, normalised by the smallest edge,
      rounded to ``--edge-decimals``.  This catches the (rare) case
      where two shapes share a vertex configuration but have a different
      edge selection.

If two manifest entries (within the same source polytope) match on both
(a) and (b), they describe congruent shapes and we keep one
representative.

Canonical representative: the one whose 4D kernel has the smallest L2
norm (= simplest Z[phi] direction).  Ties broken by lex-smallest
``fp_hash``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

PHI = (1 + 5 ** 0.5) / 2

JPP_RE = re.compile(r'<JoinPointPair start="([^"]+)" end="([^"]+)"\s*/>')
SHOW_RE = re.compile(r'<ShowPoint\s+point="([^"]+)"\s*/>')


def _parse_int_coord(s: str) -> tuple[int, ...]:
    return tuple(int(x) for x in s.split())


def _to_float3(t6: tuple[int, ...]) -> np.ndarray:
    a = np.array(t6, dtype=float)
    return np.array([a[0] + a[1] * PHI,
                     a[2] + a[3] * PHI,
                     a[4] + a[5] * PHI])


def parse_vzome(path: Path) -> tuple[np.ndarray, list[tuple[int, int]]]:
    text = path.read_text()
    seen: dict[tuple[int, ...], int] = {}
    points_int: list[tuple[int, ...]] = []
    for s in SHOW_RE.findall(text):
        t = _parse_int_coord(s)
        if t not in seen:
            seen[t] = len(points_int)
            points_int.append(t)
    edges: list[tuple[int, int]] = []
    for s, e in JPP_RE.findall(text):
        ts = _parse_int_coord(s)
        te = _parse_int_coord(e)
        if ts not in seen:
            seen[ts] = len(points_int); points_int.append(ts)
        if te not in seen:
            seen[te] = len(points_int); points_int.append(te)
        edges.append((seen[ts], seen[te]))
    P = np.stack([_to_float3(t) for t in points_int])
    return P, edges


def shape_signature(P: np.ndarray, E, *,
                    dist_decimals: int = 5,
                    edge_decimals: int = 5,
                    ) -> tuple:
    """Rotation+reflection+uniform-scale invariant fingerprint."""
    sq = (P * P).sum(axis=1)
    D2 = sq[:, None] + sq[None, :] - 2.0 * (P @ P.T)
    iu = np.triu_indices(len(P), k=1)
    d2 = np.sort(D2[iu])
    pos = d2[d2 > 1e-9]
    if pos.size == 0:
        return (len(P), len(E), "degenerate")
    s_min = float(pos[0])
    d2n = np.round(d2 / s_min, dist_decimals)

    L = np.array([float(np.linalg.norm(P[i] - P[j])) for i, j in E])
    L_min = float(L.min()) if L.size else 1.0
    L_norm = np.round(L / L_min, edge_decimals)
    edge_ms = tuple(sorted(Counter(L_norm.tolist()).items()))

    h = hashlib.sha256(d2n.tobytes()).hexdigest()[:16]
    return (len(P), len(E), h, edge_ms)


def _resolve(rel: str, corpus_root: Path) -> Path:
    return corpus_root / rel.replace("\\", "/")


def dedup_manifest_by_shape(
    manifest: dict,
    corpus_root: Path,
    *,
    dist_decimals: int = 5,
    edge_decimals: int = 5,
    dry_run: bool = False,
    log: callable = print,
) -> dict:
    """Mutate ``manifest`` in place: collapse congruent shapes per
    (group, bitmask) by reading their .vZome files and grouping by
    geometric signature.

    For each duplicate group: keep the entry with the smallest |kernel|
    (ties broken by fp_hash), remove the others from ``manifest['shapes']``,
    delete their .vZome files (unless ``dry_run``), and append their
    fp_hashes to the canonical entry's ``aliases`` list.

    Returns a stats dict with keys ``before``, ``after``, ``removed``,
    ``deleted``, ``missing``, ``alias_groups``.
    """
    shapes = manifest["shapes"]
    by_poly: dict[tuple, list[int]] = defaultdict(list)
    for i, s in enumerate(shapes):
        if s.get("status") != "ok":
            continue
        by_poly[(s["group"], tuple(s["bitmask"]))].append(i)

    n_before = sum(1 for s in shapes if s.get("status") == "ok")
    surviving: list[int] = []
    aliases_for: dict[int, list[str]] = defaultdict(list)
    removed: list[dict] = []

    for key, idxs in sorted(by_poly.items()):
        if len(idxs) <= 1:
            surviving.extend(idxs)
            continue
        sigs: dict[tuple, list[int]] = defaultdict(list)
        for i in idxs:
            path = _resolve(shapes[i]["file"], corpus_root)
            if not path.exists():
                log(f"  WARNING: missing {path}")
                surviving.append(i)
                continue
            P, E = parse_vzome(path)
            sig = shape_signature(P, E,
                                  dist_decimals=dist_decimals,
                                  edge_decimals=edge_decimals)
            sigs[sig].append(i)
        for sig, grp in sigs.items():
            if len(grp) == 1:
                surviving.append(grp[0])
                continue
            ranked = sorted(grp, key=lambda j: (
                float(np.linalg.norm(shapes[j]["kernel"])),
                shapes[j]["fp_hash"],
            ))
            canon = ranked[0]
            surviving.append(canon)
            for j in ranked[1:]:
                aliases_for[canon].append(shapes[j]["fp_hash"])
                removed.append(shapes[j])
        if any(len(v) > 1 for v in sigs.values()):
            log(f"  [{key[0]} {key[1]}] {len(idxs)} -> "
                f"{sum(1 for s in sigs.values())} distinct "
                f"({sum(len(v) - 1 for v in sigs.values())} duplicates)")

    deleted = 0
    missing = 0
    for s in removed:
        rel = s.get("file")
        if not rel:
            continue
        path = _resolve(rel, corpus_root)
        if path.exists():
            if not dry_run:
                path.unlink()
            deleted += 1
        else:
            missing += 1

    non_ok = [i for i, s in enumerate(shapes) if s.get("status") != "ok"]
    new_shapes: list[dict] = []
    for i in non_ok + sorted(surviving):
        s = dict(shapes[i])
        if i in aliases_for:
            merged = sorted(set(s.get("aliases", [])) | set(aliases_for[i]))
            s["aliases"] = merged
            s["alias_count"] = len(merged)
        new_shapes.append(s)
    new_shapes.sort(key=lambda s: (
        0 if s.get("status") == "ok" else 1,
        s.get("group", ""),
        tuple(s.get("bitmask", ())),
        s.get("fp_hash", ""),
    ))
    manifest["shapes"] = new_shapes

    notes = manifest.get("notes")
    notes = list(notes) if isinstance(notes, list) else []
    notes.append(
        f"deduplicated by 3D shape congruence "
        f"(dist_decimals={dist_decimals}, edge_decimals={edge_decimals}): "
        f"{len(removed)} aliases collapsed into {len(aliases_for)} "
        f"canonical entries"
    )
    manifest["notes"] = notes

    return {
        "before": n_before,
        "after": len(surviving),
        "removed": len(removed),
        "deleted": deleted,
        "missing": missing,
        "alias_groups": len(aliases_for),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--manifest",
                   default="output/wythoff_sweep/manifest.json")
    p.add_argument("--corpus-root",
                   default="output",
                   help="root directory the manifest's 'file' entries are relative to")
    p.add_argument("--dist-decimals", type=int, default=5)
    p.add_argument("--edge-decimals", type=int, default=5)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    manifest_path = Path(args.manifest)
    corpus_root = Path(args.corpus_root)
    with manifest_path.open("r", encoding="utf-8") as f:
        m = json.load(f)
    print(f"loaded manifest: {len(m['shapes'])} entries "
          f"({sum(1 for s in m['shapes'] if s.get('status') == 'ok')} ok)")

    stats = dedup_manifest_by_shape(
        m, corpus_root,
        dist_decimals=args.dist_decimals,
        edge_decimals=args.edge_decimals,
        dry_run=args.dry_run,
    )
    print(f"surviving ok: {stats['after']} (was {stats['before']})")
    print(f"removed:      {stats['removed']}")
    print(f"deleted vZome files: {stats['deleted']} "
          f"({'dry-run' if args.dry_run else 'real'}); "
          f"missing: {stats['missing']}")

    if args.dry_run:
        print("DRY-RUN: would update", manifest_path)
        return
    bak = manifest_path.with_suffix(manifest_path.suffix + ".preshapededup.bak")
    if not bak.exists():
        shutil.copy2(manifest_path, bak)
        print("backup:", bak)
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("manifest updated:", manifest_path)


if __name__ == "__main__":
    main()
