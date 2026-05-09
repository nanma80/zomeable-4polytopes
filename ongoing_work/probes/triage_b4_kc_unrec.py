"""Triage the 53 unrecognised B4 fp_hashes from the kernel-completeness
sweep against the master corpus shape signatures.

For each unrec'd fp_hash:
1. Emit the .vZome via tools.emit_one(example_kernel) into a temp dir.
2. Parse the .vZome and compute shape_signature.
3. Compare against:
   - master_corpus_signatures.json (output/8cell, 16cell, 24cell, etc.)
   - manifest shape_signatures (compute on-the-fly from manifest .vZome files)
4. Classify as: master-corpus-alias / manifest-alias / genuinely-new.

Output: ongoing_work/triage_b4_kc_unrec.json
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from tools.dedup_corpus_by_shape import parse_vzome, shape_signature  # type: ignore
from tools.emit_novel import emit_one  # type: ignore


def _sig_to_key(sig):
    """Hashable representation of a shape_signature tuple."""
    n_pts, n_edges, h, edge_ms = sig
    return (int(n_pts), int(n_edges), str(h),
            tuple((float(k), int(v)) for k, v in edge_ms))


def main():
    new_shapes_path = ROOT / "ongoing_work" / "shapes_rng2_B4_kc.jsonl"
    master_path = ROOT / "ongoing_work" / "master_corpus_signatures.json"
    manifest_path = ROOT / "output" / "wythoff_sweep" / "manifest.json"

    if not new_shapes_path.exists():
        print(f"missing {new_shapes_path}; abort")
        return
    if not master_path.exists():
        print(f"missing {master_path}; run build_master_corpus_signatures.py first")
        return

    master = json.load(master_path.open())
    master_sigs: dict[tuple, list[str]] = defaultdict(list)
    for entry in master:
        key = (entry["n_points"], entry["n_edges"], entry["hash"])
        master_sigs[key].append(entry["file"])
    print(f"master corpus: {len(master)} entries, {len(master_sigs)} unique sigs")

    manifest = json.load(manifest_path.open())
    manifest_sigs: dict[tuple, list[str]] = defaultdict(list)
    for s in manifest["shapes"]:
        f = s.get("file")
        if not f:
            continue
        path = ROOT / "output" / f.replace("\\", "/")
        if not path.exists():
            print(f"  manifest file missing: {path}")
            continue
        try:
            P, E = parse_vzome(path)
            sig = shape_signature(P, E)
            key = (int(sig[0]), int(sig[1]), str(sig[2]))
            manifest_sigs[key].append(f"{s['fp_hash']}:{f}")
        except Exception as e:
            print(f"  ERR sig manifest {f}: {e}")
    print(f"manifest: {sum(len(v) for v in manifest_sigs.values())} entries, "
          f"{len(manifest_sigs)} unique sigs")

    # Find canonical+alias fp_hashes already known.
    canonical_fp = set(s["fp_hash"] for s in manifest["shapes"])
    alias_fp = set()
    for s in manifest["shapes"]:
        for a in s.get("aliases", []):
            alias_fp.add(a)

    out_root = ROOT / "ongoing_work" / "triage_b4_kc_emitted"
    out_root.mkdir(parents=True, exist_ok=True)

    findings = []
    n_master_match = 0
    n_manifest_match = 0
    n_genuinely_new = 0
    n_emit_fail = 0

    with new_shapes_path.open() as f:
        for line in f:
            rec = json.loads(line)
            grp, bm, name = rec["group"], tuple(rec["bitmask"]), rec["name"]
            for sh in rec["shapes"]:
                fph = sh["fp_hash"]
                if fph in canonical_fp or fph in alias_fp:
                    continue
                # Try to emit + sig.
                info = {
                    "group": grp,
                    "bitmask": list(bm),
                    "name": name,
                    "shape_idx": -1,
                    "example_kernel": sh["example_kernel"],
                }
                try:
                    path, _counts = emit_one(fph, info, str(out_root),
                                              "kc_triage")
                    P, E = parse_vzome(Path(path))
                    sig = shape_signature(P, E)
                    sig_key = (int(sig[0]), int(sig[1]), str(sig[2]))
                except Exception as e:
                    print(f"  ERR {grp} {bm} {name} {fph[:10]}: {e}")
                    n_emit_fail += 1
                    findings.append({
                        "group": grp, "bitmask": list(bm), "name": name,
                        "fp_hash": fph, "status": "emit_fail",
                        "reason": str(e),
                    })
                    continue

                status = None
                matches = []
                if sig_key in master_sigs:
                    status = "master_corpus_alias"
                    matches = master_sigs[sig_key]
                    n_master_match += 1
                elif sig_key in manifest_sigs:
                    status = "manifest_alias"
                    matches = manifest_sigs[sig_key]
                    n_manifest_match += 1
                else:
                    status = "genuinely_new"
                    n_genuinely_new += 1

                findings.append({
                    "group": grp,
                    "bitmask": list(bm),
                    "name": name,
                    "fp_hash": fph,
                    "n_balls": sh["n_balls"],
                    "post_snap_sig": list(sig_key),
                    "status": status,
                    "matches": matches,
                    "emitted_path": str(Path(path).relative_to(ROOT))
                                    if status != "emit_fail" else None,
                })
                print(f"  {grp} {bm} {name} {fph[:10]}: {status}"
                      + (f"  -> {matches[0]}" if matches else ""))

    out_path = ROOT / "ongoing_work" / "triage_b4_kc_unrec.json"
    out_path.write_text(json.dumps({
        "summary": {
            "total_unrec": len(findings),
            "master_corpus_alias": n_master_match,
            "manifest_alias": n_manifest_match,
            "genuinely_new": n_genuinely_new,
            "emit_fail": n_emit_fail,
        },
        "findings": findings,
    }, indent=2))
    print(f"\nWrote {out_path}")
    print(f"summary: master={n_master_match} manifest={n_manifest_match} "
          f"new={n_genuinely_new} emit_fail={n_emit_fail}")


if __name__ == "__main__":
    main()
