"""Triage the 40 fp_hashes in novel_rng2.json that have no manifest
entry and no alias.  For each, emit-one + shape_signature, and
compare against existing manifest entries on the same (group, bitmask)
to classify as ALIAS / GENUINELY_NEW / SNAP_FAILED / EMIT_FAILED.

Smallest polytopes first (tractable), heaviest last (omnitr-120-cell
V=14400, 25 candidates).
"""
import json
import sys
import tempfile
import time
import traceback
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

from emit_novel import emit_one  # noqa: E402
from dedup_corpus_by_shape import shape_signature, parse_vzome  # noqa: E402
from wythoff import build_polytope  # noqa: E402


def _resolve_corpus_path(rel: str) -> Path:
    return ROOT / "output" / rel.replace("\\", "/")


def _load_manifest_index() -> dict:
    """{(group, bitmask): {shape_signature_tuple: fp_hash}}"""
    mp = ROOT / "output" / "wythoff_sweep" / "manifest.json"
    m = json.loads(mp.read_text())
    idx = defaultdict(dict)
    for s in m["shapes"]:
        if s.get("status") != "ok":
            continue
        rel = s.get("file")
        if not rel:
            continue
        path = _resolve_corpus_path(rel)
        if not path.exists():
            continue
        try:
            P, E = parse_vzome(path)
            sig = shape_signature(P, E)
        except Exception:
            continue
        idx[(s["group"], tuple(s["bitmask"]))][sig] = s["fp_hash"]
    return idx


def _find_uncovered(novel: dict, manifest: dict) -> list:
    canonical_fps = set()
    alias_fps = set()
    for s in manifest["shapes"]:
        canonical_fps.add(s["fp_hash"])
        for a in s.get("aliases", []):
            alias_fps.add(a)
    uncovered = []
    for fp in novel.keys():
        if fp in canonical_fps or fp in alias_fps:
            continue
        rep = novel[fp]["occurrences"][0]
        uncovered.append((fp, rep, novel[fp]))
    return uncovered


def _v_size(group, bitmask):
    V, _E = build_polytope(group, bitmask)
    return len(V)


def main():
    novel = json.loads((ROOT / "ongoing_work" / "novel_rng2.json").read_text())
    manifest = json.loads(
        (ROOT / "output" / "wythoff_sweep" / "manifest.json").read_text())
    print(f"Loading manifest shape index...")
    midx = _load_manifest_index()
    print(f"  manifest indexed: {sum(len(v) for v in midx.values())} "
          f"shapes across {len(midx)} (group,bitmask) keys\n")

    uncovered = _find_uncovered(novel, manifest)
    print(f"uncovered fp_hashes: {len(uncovered)}\n")

    # Sort by polytope V (smallest first)
    keyed = []
    v_cache = {}
    for fp, rep, _entry in uncovered:
        key = (rep["group"], tuple(rep["bitmask"]))
        if key not in v_cache:
            v_cache[key] = _v_size(*key)
        keyed.append((v_cache[key], fp, rep))
    keyed.sort(key=lambda x: (x[0], x[1]))

    by_poly = defaultdict(list)
    for v, fp, rep in keyed:
        by_poly[(v, rep["group"], tuple(rep["bitmask"]), rep["name"])].append(
            (fp, rep))

    n_alias = n_new = n_snap = n_fail = 0
    new_records = []  # for committing/promoting

    for (v, group, bitmask, name), entries in sorted(by_poly.items()):
        print(f"=== V={v}  {group} {list(bitmask)}  {name}: "
              f"{len(entries)} fp(s) ===")
        existing = midx.get((group, bitmask), {})
        print(f"  existing manifest shapes for this polytope: {len(existing)}")
        t_poly = time.time()
        for fp, rep in entries:
            t0 = time.time()
            info = {
                "n_balls": rep["n_balls"],
                "sig": rep["sig"],
                "group": rep["group"],
                "bitmask": list(rep["bitmask"]),
                "name": rep["name"],
                "shape_idx": rep["shape_idx"],
                "example_kernel": rep["example_kernel"],
            }
            with tempfile.TemporaryDirectory() as td:
                try:
                    path, counts = emit_one(fp, info, td, f"triage_{fp[:10]}")
                except Exception as exc:
                    short = (str(exc).splitlines() or [""])[0][:140]
                    if "snap" in short.lower():
                        verdict = "SNAP_FAILED"
                        n_snap += 1
                    else:
                        verdict = "EMIT_FAILED"
                        n_fail += 1
                    print(f"  {fp[:16]}  balls={rep['n_balls']:5d}  "
                          f"{verdict}  ({time.time()-t0:.1f}s)  err={short}")
                    continue
                try:
                    P, E = parse_vzome(Path(path))
                    sig = shape_signature(P, E)
                except Exception as exc:
                    print(f"  {fp[:16]}  PARSE_FAILED  err={exc}")
                    continue
                if sig in existing:
                    n_alias += 1
                    canon = existing[sig]
                    print(f"  {fp[:16]}  balls={rep['n_balls']:5d}  "
                          f"ALIAS_OF {canon[:16]}  "
                          f"({time.time()-t0:.1f}s)")
                else:
                    n_new += 1
                    print(f"  *** {fp[:16]}  balls={rep['n_balls']:5d}  "
                          f"GENUINELY_NEW  hash={sig[2]}  "
                          f"counts={dict(counts)}  "
                          f"kernel={rep['example_kernel']}  "
                          f"({time.time()-t0:.1f}s)")
                    new_records.append({
                        "fp_hash": fp,
                        "group": rep["group"],
                        "bitmask": list(rep["bitmask"]),
                        "source_polytope": rep["name"],
                        "shape_signature_hash": sig[2],
                        "n_balls": rep["n_balls"],
                        "n_edges": sig[1],
                        "kernel": rep["example_kernel"],
                        "counts": dict(counts),
                    })
        print(f"  -- polytope total: {time.time()-t_poly:.1f}s\n")

    print("=" * 60)
    print("Triage summary:")
    print(f"  alias of existing:       {n_alias}")
    print(f"  genuinely NEW:           {n_new}")
    print(f"  snap-failed during emit: {n_snap}")
    print(f"  other emit failures:     {n_fail}")

    if new_records:
        out = ROOT / "ongoing_work" / "novel_gap_genuinely_new.json"
        out.write_text(json.dumps(new_records, indent=2))
        print(f"\nWrote genuinely-new records to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
