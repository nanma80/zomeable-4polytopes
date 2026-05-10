"""Triage the blind-spot audit findings.

Reads `ongoing_work/blind_spot_audit_rng2.json` (produced by
`blind_spot_audit.py`).  For every (group, bitmask) with new_fp > 0,
for every new fp, snap-emit a candidate .vZome via project_and_emit
and classify the resulting Stage-B fingerprint:

   * already in `output/wythoff_sweep/<slug>/` for THIS polytope?
     -> already-known shape; the audit just demonstrates the
        manifest's fp_hash differs from the descendant-direct
        fp_hash (likely a kernel-orbit hash artifact, not a new
        shape).
   * present in any other corpus file (any wythoff_sweep entry,
     any master regular)?
     -> already-known shape, mis-attributed; flag for inspection.
   * not in corpus, but matches another candidate in the same
     audit run?  -> intra-audit duplicate (one shape surfaces from
     multiple polytopes); flag and pick a canonical owner.
   * not in corpus and unique among candidates?  -> GENUINELY NEW.
     Stage for promotion.

Output:
  ongoing_work/blind_spot_triage.json
    Per-fp record with snap status, Stage-B sig, classification,
    and (for "new" candidates) the staged .vZome path.
  ongoing_work/blind_spot_candidates/<group>_<bitmask>/<idx>.vZome
    Snapped .vZome files (only for fp not in corpus).
"""
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

import numpy as np  # noqa: E402

from wythoff import build_polytope                       # noqa: E402
from emit_generic import project_and_emit                # noqa: E402
from dedup_corpus_by_shape import parse_vzome, shape_signature  # noqa: E402
from uniform_polytopes import _NAMES                     # noqa: E402

AUDIT_PATH = ROOT / "ongoing_work" / "blind_spot_audit_rng2.json"
TRIAGE_PATH = ROOT / "ongoing_work" / "blind_spot_triage.json"
STAGING_DIR = ROOT / "ongoing_work" / "blind_spot_candidates"


def slugify(name: str) -> str:
    """Match output/wythoff_sweep/ subdir naming."""
    return name.replace(" ", "_")


def index_corpus():
    """Return dict[stage_b_sig] -> list of corpus file paths."""
    print("Indexing corpus (output/wythoff_sweep + master regulars)...",
          flush=True)
    sig_to_files = defaultdict(list)
    for vz in (ROOT / "output" / "wythoff_sweep").rglob("*.vZome"):
        try:
            P, E = parse_vzome(vz)
            sig = shape_signature(P, E)
            sig_to_files[sig].append(str(vz.relative_to(ROOT)))
        except Exception:
            pass
    for d in ["5cell", "8cell", "16cell", "24cell",
              "600cell", "120cell", "snub24cell", "grand_antiprism"]:
        p = ROOT / "output" / d
        if not p.exists():
            continue
        for vz in p.glob("*.vZome"):
            try:
                P, E = parse_vzome(vz)
                sig = shape_signature(P, E)
                sig_to_files[sig].append(str(vz.relative_to(ROOT)))
            except Exception:
                pass
    n_files = sum(len(v) for v in sig_to_files.values())
    print(f"  {len(sig_to_files)} unique sigs across {n_files} files",
          flush=True)
    return sig_to_files


def main():
    os.chdir(ROOT)
    audit = json.load(open(AUDIT_PATH))
    print(f"Loaded {AUDIT_PATH.name}: {len(audit['results'])} polytopes",
          flush=True)

    corpus_sigs = index_corpus()

    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    triage = {
        "rng": audit.get("rng", 2),
        "polytopes_processed": 0,
        "fp_processed": 0,
        "fp_snap_ok": 0,
        "fp_snap_fail": 0,
        "in_corpus": 0,
        "in_corpus_same_polytope": 0,
        "in_corpus_other_polytope": 0,
        "intra_audit_duplicate": 0,
        "genuinely_new": 0,
        "results": [],
    }

    # First pass: snap every new fp; record sig for intra-audit dedup
    candidate_records = []
    for r in audit["results"]:
        if not r.get("new_records"):
            continue
        triage["polytopes_processed"] += 1
        group = r["group"]
        bitmask = tuple(r["bitmask"])
        name = r["name"]
        slug = slugify(name)
        sub_dir = STAGING_DIR / f"{group}_{''.join(map(str,bitmask))}_{slug}"
        sub_dir.mkdir(parents=True, exist_ok=True)
        try:
            V, E = build_polytope(group, bitmask)
        except Exception as exc:
            print(f"!! {group} {bitmask} {name}: build FAIL: {exc}", flush=True)
            continue
        for nr in r["new_records"]:
            triage["fp_processed"] += 1
            fp_hash = nr["fp_hash"]
            kernel = np.array(nr["example_kernel"])
            out_path = sub_dir / f"fp_{fp_hash}.vZome"
            t0 = time.time()
            try:
                project_and_emit(name, V, E, kernel, str(out_path))
                snap_ok = True
            except Exception as exc:
                snap_ok = False
                snap_err = repr(exc)
            elapsed = time.time() - t0
            rec = {
                "group": group,
                "bitmask": list(bitmask),
                "name": name,
                "fp_hash": fp_hash,
                "kernel": [float(x) for x in kernel],
                "n_balls": nr["n_balls"],
                "n_kernels_in_orbit": nr.get("n_kernels_in_orbit"),
                "snap_ok": snap_ok,
                "snap_wall_s": round(elapsed, 1),
            }
            if not snap_ok:
                triage["fp_snap_fail"] += 1
                rec["snap_error"] = snap_err
                rec["status"] = "snap_fail"
                print(f"  {group} {bitmask} {name} fp={fp_hash}: "
                      f"SNAP FAIL  ({elapsed:.1f}s)  {snap_err[:80]}",
                      flush=True)
            else:
                triage["fp_snap_ok"] += 1
                # Stage-B sig from the just-emitted file
                P, E_loaded = parse_vzome(out_path)
                sig = shape_signature(P, E_loaded)
                rec["staged_path"] = str(out_path.relative_to(ROOT))
                rec["sig_V"] = len(P)
                rec["sig_E"] = len(E_loaded)
                rec["sig_hash"] = sig if isinstance(sig, str) else None
                # Lookup
                matches = corpus_sigs.get(sig, [])
                rec["corpus_matches"] = matches
                if matches:
                    triage["in_corpus"] += 1
                    same_poly = [m for m in matches
                                 if f"/{slug}/" in m.replace("\\", "/")]
                    if same_poly:
                        triage["in_corpus_same_polytope"] += 1
                        rec["status"] = "in_corpus_same_polytope"
                    else:
                        triage["in_corpus_other_polytope"] += 1
                        rec["status"] = "in_corpus_other_polytope"
                else:
                    rec["status"] = "candidate_new"
                # Track for intra-audit dedup
                candidate_records.append((rec, sig))
                print(f"  {group} {bitmask} {name} fp={fp_hash}  "
                      f"V={len(P)} E={len(E_loaded)}  status={rec['status']}  "
                      f"matches={len(matches)}  ({elapsed:.1f}s)", flush=True)
            triage["results"].append(rec)
            # Persist after each fp (safety)
            with open(TRIAGE_PATH, "w") as f:
                json.dump(triage, f, indent=2, default=str)

    # Second pass: intra-audit dedup among "candidate_new"
    sig_to_recs = defaultdict(list)
    for rec, sig in candidate_records:
        if rec["status"] == "candidate_new":
            sig_to_recs[sig].append(rec)
    for sig, recs in sig_to_recs.items():
        if len(recs) > 1:
            # Multiple polytopes produce the same Stage-B shape from
            # blind-spot kernels.  Keep first as canonical, mark rest
            # as intra-audit-duplicate.
            recs[0]["status"] = "candidate_new_canonical"
            for dup in recs[1:]:
                dup["status"] = "intra_audit_duplicate"
                dup["duplicate_of_fp_hash"] = recs[0]["fp_hash"]
                dup["duplicate_of_polytope"] = (
                    f"{recs[0]['group']} {tuple(recs[0]['bitmask'])} "
                    f"{recs[0]['name']}")
                triage["intra_audit_duplicate"] += 1
                triage["genuinely_new"] -= 0  # never incremented yet
        else:
            recs[0]["status"] = "candidate_new_canonical"
    n_new = sum(1 for rec, _ in candidate_records
                if rec["status"] == "candidate_new_canonical")
    triage["genuinely_new"] = n_new

    with open(TRIAGE_PATH, "w") as f:
        json.dump(triage, f, indent=2, default=str)

    print()
    print(f"=== TRIAGE SUMMARY ===")
    print(f"polytopes processed:        {triage['polytopes_processed']}")
    print(f"fp processed:               {triage['fp_processed']}")
    print(f"  snap OK:                  {triage['fp_snap_ok']}")
    print(f"  snap FAIL:                {triage['fp_snap_fail']}")
    print(f"  in corpus (same poly):    {triage['in_corpus_same_polytope']}")
    print(f"  in corpus (other poly):   {triage['in_corpus_other_polytope']}")
    print(f"  intra-audit duplicates:   {triage['intra_audit_duplicate']}")
    print(f"  GENUINELY NEW (canonical):{triage['genuinely_new']}")
    print(f"Wrote {TRIAGE_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
