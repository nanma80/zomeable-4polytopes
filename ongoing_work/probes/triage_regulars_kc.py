"""Triage regular-polytope sweep fp_hashes from any group against
master corpus + manifest, post-snap.  Generalisation of
triage_b4_kc_unrec.py.

Usage:
    python ongoing_work/probes/triage_regulars_kc.py [--group A4|B4|F4|H4]

If --group not given, triages all 4.

Reads sweep fp_hashes from any shapes_rng2*.jsonl file in ongoing_work/.
Aggregates per (group, regular_bitmask), emits each unique fp_hash via
emit_one, post-snaps, and compares against master_corpus_signatures.json
+ manifest fingerprints.

Output: ongoing_work/triage_regulars_kc_unrec.json with summary +
per-finding details.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from tools.dedup_corpus_by_shape import parse_vzome, shape_signature  # type: ignore
from tools.emit_novel import emit_one  # type: ignore


REGULARS = {
    ("A4", (1, 0, 0, 0)): "5cell",
    ("A4", (0, 0, 0, 1)): "5cell",
    ("B4", (1, 0, 0, 0)): "8cell",
    ("B4", (0, 0, 0, 1)): "16cell",
    ("F4", (1, 0, 0, 0)): "24cell",
    ("F4", (0, 0, 0, 1)): "24cell",
    ("H4", (1, 0, 0, 0)): "120cell",
    ("H4", (0, 0, 0, 1)): "600cell",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", default=None,
                    help="Limit to A4/B4/F4/H4 (default: all)")
    args = ap.parse_args()

    master_path = ROOT / "ongoing_work" / "master_corpus_signatures.json"
    if not master_path.exists():
        print(f"missing {master_path}; run build_master_corpus_signatures.py first")
        return

    master = json.load(master_path.open())
    master_sigs: dict[tuple, list[str]] = defaultdict(list)
    for entry in master:
        key = (entry["n_points"], entry["n_edges"], entry["hash"])
        master_sigs[key].append(entry["file"])

    manifest_path = ROOT / "output" / "wythoff_sweep" / "manifest.json"
    manifest = json.load(manifest_path.open())
    manifest_sigs: dict[tuple, list[str]] = defaultdict(list)
    for s in manifest["shapes"]:
        f = s.get("file")
        if not f:
            continue
        path = ROOT / "output" / f.replace("\\", "/")
        if not path.exists():
            continue
        try:
            P, E = parse_vzome(path)
            sig = shape_signature(P, E)
            key = (int(sig[0]), int(sig[1]), str(sig[2]))
            manifest_sigs[key].append(f"{s['fp_hash']}:{f}")
        except Exception:
            pass
    print(f"master corpus: {len(master)} entries, {len(master_sigs)} unique sigs")
    print(f"manifest: {sum(len(v) for v in manifest_sigs.values())} entries, "
          f"{len(manifest_sigs)} unique sigs")

    # Collect all sweep fp_hashes for each (group, regular_bitmask).
    by_reg: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for f in (ROOT / "ongoing_work").glob("shapes_rng2*.jsonl"):
        with f.open() as fh:
            for line in fh:
                rec = json.loads(line)
                key = (rec["group"], tuple(rec["bitmask"]))
                if key not in REGULARS:
                    continue
                if args.group and rec["group"] != args.group:
                    continue
                for sh in rec["shapes"]:
                    fph = sh["fp_hash"]
                    if fph not in by_reg[key]:
                        by_reg[key][fph] = {
                            "n_balls": sh["n_balls"],
                            "example_kernel": sh["example_kernel"],
                            "name": rec["name"],
                            "src_file": str(f.relative_to(ROOT)).replace("\\", "/"),
                        }

    print()
    out_root = ROOT / "ongoing_work" / "triage_regulars_kc_emitted"
    out_root.mkdir(parents=True, exist_ok=True)

    findings = []
    by_status = defaultdict(int)
    for key, fps in sorted(by_reg.items()):
        grp, bm = key
        master_dir = REGULARS[key]
        print(f"\n=== {grp} {bm} (master={master_dir}): {len(fps)} fp_hashes ===")
        for fph, meta in sorted(fps.items()):
            info = {
                "group": grp,
                "bitmask": list(bm),
                "name": meta["name"],
                "shape_idx": -1,
                "example_kernel": meta["example_kernel"],
            }
            try:
                path, _ = emit_one(fph, info, str(out_root), "kc_triage")
                P, E = parse_vzome(Path(path))
                sig = shape_signature(P, E)
                sig_key = (int(sig[0]), int(sig[1]), str(sig[2]))
            except Exception as e:
                print(f"  {fph[:10]}: emit_fail ({str(e)[:60]})")
                by_status["emit_fail"] += 1
                findings.append({
                    "group": grp, "bitmask": list(bm),
                    "fp_hash": fph, "status": "emit_fail",
                    "reason": str(e),
                })
                continue
            status = "genuinely_new"
            matches = []
            if sig_key in master_sigs:
                status = "master_corpus_alias"
                matches = master_sigs[sig_key]
            elif sig_key in manifest_sigs:
                status = "manifest_alias"
                matches = manifest_sigs[sig_key]
            by_status[status] += 1
            print(f"  {fph[:10]}: {status}"
                  + (f"  -> {matches[0]}" if matches else ""))
            findings.append({
                "group": grp,
                "bitmask": list(bm),
                "name": meta["name"],
                "fp_hash": fph,
                "n_balls": meta["n_balls"],
                "post_snap_sig": list(sig_key),
                "status": status,
                "matches": matches,
                "emitted_path": str(Path(path).relative_to(ROOT)).replace("\\", "/"),
                "example_kernel": meta["example_kernel"],
            })

    print(f"\n=== summary ===")
    for k, v in sorted(by_status.items()):
        print(f"  {k}: {v}")

    out_path = ROOT / "ongoing_work" / "triage_regulars_kc_unrec.json"
    out_path.write_text(json.dumps({
        "summary": dict(by_status),
        "findings": findings,
    }, indent=2))
    print(f"\nWrote {out_path}")

    # Highlight genuinely_new
    new = [f for f in findings if f["status"] == "genuinely_new"]
    if new:
        print(f"\n*** {len(new)} GENUINELY NEW shape(s) found across regulars: ***")
        for f in new:
            print(f"  {f['group']} {f['bitmask']}  fp={f['fp_hash'][:10]}  "
                  f"sig={f['post_snap_sig'][2]}  V={f['post_snap_sig'][0]}  "
                  f"E={f['post_snap_sig'][1]}  staged={f['emitted_path']}")


if __name__ == "__main__":
    main()
