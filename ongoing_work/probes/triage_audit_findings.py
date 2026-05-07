"""Triage audit findings: snap-emit each "new" fp_hash and compare its
post-snap shape_signature against the manifest's existing entries on
the same (group, bitmask).

Usage:
    python ongoing_work/probes/triage_audit_findings.py \
        ongoing_work/blind_spot_audit_h4_rng2.json

For each "new_records" entry, the triage:
  1. Builds the emit_novel "info" dict.
  2. Calls emit_one with a temp output dir.
  3. Computes shape_signature on the resulting .vZome.
  4. Loads existing manifest .vZome files for the same (group, bitmask)
     and compares signatures.
  5. Reports: ALIAS (matches existing) / GENUINELY_NEW / SNAP_FAILED.

Exit code 0 if all triages succeeded, 1 if any genuinely-new shape was
found (worth committing), 2 if any snap-failed.
"""
import json
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

from emit_novel import emit_one  # noqa: E402
from dedup_corpus_by_shape import shape_signature, parse_vzome  # noqa: E402


def _resolve_corpus_path(rel: str) -> Path:
    return ROOT / "output" / rel.replace("\\", "/")


def _load_manifest_index() -> dict:
    """Return {(group, bitmask): {fp_hash: shape_signature}} for status=ok
    entries in the wythoff_sweep manifest."""
    mp = ROOT / "output" / "wythoff_sweep" / "manifest.json"
    m = json.loads(mp.read_text())
    idx = {}
    for s in m["shapes"]:
        if s.get("status") != "ok":
            continue
        key = (s["group"], tuple(s["bitmask"]))
        rel = s.get("file")
        if not rel:
            continue
        path = _resolve_corpus_path(rel)
        if not path.exists():
            print(f"  WARN: manifest file missing: {rel}")
            continue
        try:
            P, E = parse_vzome(path)
            sig = shape_signature(P, E)
        except Exception as exc:
            print(f"  WARN: parse failed for {rel}: {exc}")
            continue
        idx.setdefault(key, {})[s["fp_hash"]] = sig
    return idx


def triage(audit_path: Path) -> int:
    audit = json.loads(audit_path.read_text())
    manifest_idx = _load_manifest_index()
    print(f"manifest indexed: "
          f"{sum(len(v) for v in manifest_idx.values())} shapes "
          f"across {len(manifest_idx)} (group,bitmask) keys\n")

    found_new = 0
    found_snap_fail = 0
    found_alias = 0

    for poly in audit.get("results", []):
        new_records = poly.get("new_records", [])
        if not new_records:
            continue
        key = (poly["group"], tuple(poly["bitmask"]))
        print(f"=== {key[0]} {list(key[1])} {poly['name']}: "
              f"{len(new_records)} new fp_hash(es) to triage ===")
        existing_sigs = {sig: fp for fp, sig
                         in manifest_idx.get(key, {}).items()}

        for rec in new_records:
            fp = rec["fp_hash"]
            info = {
                "n_balls": rec["n_balls"],
                "sig": rec["strut_sig"],
                "group": poly["group"],
                "bitmask": list(poly["bitmask"]),
                "name": poly["name"],
                "shape_idx": 0,
                "example_kernel": rec["example_kernel"],
            }
            with tempfile.TemporaryDirectory() as td:
                try:
                    path, counts = emit_one(fp, info, td, f"triage_{fp[:10]}")
                except Exception as exc:
                    short = (str(exc).splitlines() or [""])[0][:120]
                    if "snap" in short.lower():
                        verdict = "SNAP_FAILED"
                        found_snap_fail += 1
                    else:
                        verdict = "EMIT_FAILED"
                        traceback.print_exc()
                    print(f"  {fp[:16]} balls={rec['n_balls']:5d} "
                          f"{verdict}  err={short}")
                    continue
                try:
                    P, E = parse_vzome(Path(path))
                    sig = shape_signature(P, E)
                except Exception as exc:
                    print(f"  {fp[:16]} balls={rec['n_balls']:5d} "
                          f"PARSE_FAILED  err={exc}")
                    continue
                if sig in existing_sigs:
                    found_alias += 1
                    print(f"  {fp[:16]} balls={rec['n_balls']:5d} "
                          f"ALIAS_OF {existing_sigs[sig][:16]}  "
                          f"counts={dict(counts)}")
                else:
                    found_new += 1
                    print(f"  *** {fp[:16]} balls={rec['n_balls']:5d} "
                          f"GENUINELY_NEW  hash={sig[2]}  "
                          f"counts={dict(counts)} "
                          f"example_kernel={rec['example_kernel']}")
        print()

    print(f"=== Triage summary ===")
    print(f"  alias of existing:       {found_alias}")
    print(f"  genuinely new:           {found_new}")
    print(f"  snap-failed during emit: {found_snap_fail}")

    if found_new > 0:
        return 1
    if found_snap_fail > 0:
        return 2
    return 0


if __name__ == "__main__":
    audit_path = Path(sys.argv[1] if len(sys.argv) > 1
                      else "ongoing_work/blind_spot_audit_h4_rng2.json")
    sys.exit(triage(audit_path.resolve()))
