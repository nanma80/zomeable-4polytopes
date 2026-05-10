"""H4 small-descendant blind-spot audit (Milestone 17b).

Same descendant-direct rng=2 sweep architecture as
ongoing_work/probes/blind_spot_audit.py, but covers the 5 smallest
H4 Wythoff descendants:

    H4 (0, 0, 1, 0)  rectified 600-cell    V=720,  E=3600
    H4 (0, 1, 0, 0)  rectified 120-cell    V=1200, E=3600
    H4 (0, 0, 1, 1)  truncated 600-cell    V=1440, E=4320
    H4 (1, 1, 0, 0)  truncated 120-cell    V=2400, E=...
    H4 (1, 0, 0, 1)  runcinated 120-cell   V=2400, E=...

(omits the V>=3600 H4 polytopes: bitruncated/cantellated 120-cell,
cantellated 600-cell, etc., which would each cost >5h.)

Persists to ongoing_work/blind_spot_audit_h4_rng2.json.
"""
import os, sys, json, time, hashlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

from wythoff import build_polytope                         # noqa: E402
from search_engine import gen_dirs, search, group_by_shape  # noqa: E402


def hash_fp(fp):
    n_balls, dists = fp
    payload = repr((int(n_balls),
                    tuple(round(float(d), 6) for d in dists)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# Run smallest-V H4 descendants first.  Beyond V=2400 the per-polytope
# audit cost climbs above ~3h, so we cap the first wave here.
H4_WORK = [
    ((0, 0, 1, 0), "rectified 600-cell"),
    ((0, 1, 0, 0), "rectified 120-cell"),
    ((0, 0, 1, 1), "truncated 600-cell"),
    ((1, 1, 0, 0), "truncated 120-cell"),
    ((1, 0, 0, 1), "runcinated 120-cell"),
]


def main():
    os.chdir(ROOT)
    out_path = "ongoing_work/blind_spot_audit_h4_rng2.json"

    manifest = json.load(open("output/wythoff_sweep/manifest.json"))
    print(f"manifest: {len(manifest['shapes'])} shape entries", flush=True)
    known_hashes = defaultdict(set)
    for sh in manifest["shapes"]:
        if sh["group"] != "H4":
            continue
        key = (sh["group"], tuple(sh["bitmask"]))
        known_hashes[key].add(sh["fp_hash"])
    print(f"  -> {len(known_hashes)} H4 (group, bitmask) entries with known fp",
          flush=True)

    work = [("H4", b, name) for (b, name) in H4_WORK]
    print(f"audit worklist: {len(work)} H4 polytopes (V<=2400)",
          flush=True)
    for g, b, n in work:
        print(f"   {g} {b}  {n}", flush=True)
    print(flush=True)

    print("Generating rng=2 directions...", flush=True)
    t0 = time.time()
    dirs2 = gen_dirs(rng=2, integer_only=False, permute_dedup=False)
    print(f"  {len(dirs2)} dirs ({time.time()-t0:.1f}s)", flush=True)
    print(flush=True)

    summary_rows = []
    t_total = time.time()
    for i_p, (group, b, name) in enumerate(work, 1):
        t0 = time.time()
        try:
            V, E = build_polytope(group, b)
        except Exception as exc:
            print(f"[{i_p}/{len(work)}] {group} {b} {name}: build FAIL: {exc}",
                  flush=True)
            summary_rows.append({"group": group, "bitmask": list(b),
                                 "name": name, "build_error": repr(exc)})
            continue
        n_v, n_e = len(V), len(E)
        print(f"[{i_p}/{len(work)}] {group} {b} {name}  "
              f"V={n_v} E={n_e}  starting search...", flush=True)
        hits = search(name, V, E, dirs2, verbose=False)
        groups = group_by_shape(hits, V, E)
        n_fp = len(groups)
        fp_hashes_now = {}
        for fp, examples in groups.items():
            h = hash_fp(fp)
            fp_hashes_now[h] = (fp, examples)
        known = known_hashes.get((group, b), set())
        new_hashes = sorted(set(fp_hashes_now) - known)
        unseen_known = sorted(known - set(fp_hashes_now))
        elapsed = time.time() - t0
        marker = " <<< NEW" if new_hashes else ""
        print(f"[{i_p}/{len(work)}] {group} {b} {name}  "
              f"V={n_v} E={n_e}  fp={n_fp}  manifest={len(known)}  "
              f"new={len(new_hashes)}  miss={len(unseen_known)}  "
              f"({elapsed:.1f}s){marker}", flush=True)
        new_records = []
        for h in new_hashes:
            fp, examples = fp_hashes_now[h]
            n_balls, dists = fp
            n0, sig0, balls0 = examples[0]
            new_records.append({
                "fp_hash": h,
                "n_balls": int(n_balls),
                "n_kernels_in_orbit": len(examples),
                "example_kernel": [float(x) for x in n0],
                "strut_sig": {k: int(v) for k, v in sig0.items()},
                "first_5_kernels": [[float(x) for x in ex[0]]
                                    for ex in examples[:5]],
            })
        summary_rows.append({
            "group": group,
            "bitmask": list(b),
            "name": name,
            "V": n_v, "E": n_e,
            "fp_total": n_fp,
            "manifest_known": len(known),
            "new_fp": len(new_hashes),
            "manifest_unseen": len(unseen_known),
            "elapsed_sec": round(elapsed, 1),
            "new_records": new_records,
            "manifest_hashes_not_resurfaced": list(unseen_known),
        })
        with open(out_path, "w") as f:
            json.dump({
                "rng": 2,
                "groups_audited": ["H4"],
                "results": summary_rows,
                "elapsed_total_sec": round(time.time() - t_total, 1),
            }, f, indent=2)

    print(flush=True)
    print(f"Total elapsed: {time.time()-t_total:.1f}s", flush=True)
    print(f"Wrote {out_path}", flush=True)
    n_with_new = sum(1 for r in summary_rows if r.get("new_fp", 0) > 0)
    n_total_new = sum(r.get("new_fp", 0) for r in summary_rows)
    print(f"Summary: {n_with_new} polytopes have new fp; "
          f"{n_total_new} new fp_hashes total.", flush=True)


if __name__ == "__main__":
    main()
