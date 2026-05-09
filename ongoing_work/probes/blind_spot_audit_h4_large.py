"""H4 large-descendant blind-spot audit (post search-engine-prefilter).

Runs the same descendant-direct rng=2 sweep architecture as
ongoing_work/probes/blind_spot_audit_h4.py, but covers the 8 remaining
H4 Wythoff descendants with V >= 3600 that were skipped before because
each cost >5 hours under chunk=512.

Now feasible thanks to lib/search_engine.py:_check_cos_pairs chunk=16
optimisation (commit 7ccc1a7) which gives ~6x speedup on K=3600 and
correspondingly more on larger K.

H4 polytopes audited:
    (0, 1, 1, 0)  bitruncated 600-cell                V=3600  E=7200
    (0, 1, 0, 1)  cantellated/rectified-cuboctah-ish  V=3600  E=10800
    (1, 0, 1, 0)  cantellated 600-cell                V=3600  E=10800
    (1, 1, 1, 0)  cantitruncated 600-cell             V=7224  E=14520
    (0, 1, 1, 1)  cantitruncated 120-cell             V=7224  E=14508
    (1, 1, 0, 1)  runcitruncated 600-cell             V=7212  E=18060
    (1, 0, 1, 1)  runcitruncated 120-cell             V=7200  E=18000
    (1, 1, 1, 1)  omnitruncated 120-cell              V=14544 E=29538

Persists to ongoing_work/blind_spot_audit_h4_large_rng2.json.
"""
import os, sys, json, time, hashlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

from wythoff import build_polytope                             # noqa: E402
from search_engine import gen_dirs, search, group_by_shape     # noqa: E402


def hash_fp(fp):
    n_balls, dists = fp
    payload = repr((int(n_balls),
                    tuple(round(float(d), 6) for d in dists)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# Order: smallest K first so we discover fast feedback before the big
# omnitruncated 120-cell at the end.
H4_LARGE_WORK = [
    ((0, 1, 1, 0), "bitruncated 600-cell"),       # K=7200
    ((0, 1, 0, 1), "ringing (0,1,0,1)"),          # K=10800
    ((1, 0, 1, 0), "cantellated 600-cell"),       # K=10800
    ((0, 1, 1, 1), "cantitruncated 120-cell"),    # K=14508
    ((1, 1, 1, 0), "cantitruncated 600-cell"),    # K=14520
    ((1, 0, 1, 1), "runcitruncated 120-cell"),    # K=18000
    ((1, 1, 0, 1), "runcitruncated 600-cell"),    # K=18060
    ((1, 1, 1, 1), "omnitruncated 120-cell"),     # K=29538
]


def main():
    os.chdir(ROOT)
    out_path = "ongoing_work/blind_spot_audit_h4_large_rng2.json"

    manifest = json.load(open("output/wythoff_sweep/manifest.json"))
    print(f"manifest: {len(manifest['shapes'])} shape entries", flush=True)
    known_hashes = defaultdict(set)
    known_aliases = defaultdict(set)
    for sh in manifest["shapes"]:
        if sh["group"] != "H4":
            continue
        key = (sh["group"], tuple(sh["bitmask"]))
        known_hashes[key].add(sh["fp_hash"])
        for a in sh.get("aliases", []):
            known_aliases[key].add(a)
    print(f"  -> {len(known_hashes)} H4 (group, bitmask) entries with known fp",
          flush=True)
    print(f"  -> {sum(len(v) for v in known_aliases.values())} known aliases tracked",
          flush=True)

    work = [("H4", b, name) for (b, name) in H4_LARGE_WORK]
    print(f"audit worklist: {len(work)} H4 large-V polytopes (V>=3600)",
          flush=True)
    for g, b, n in work:
        print(f"   {g} {b}  {n}", flush=True)
    print(flush=True)

    print("Generating rng=2 directions...", flush=True)
    t0 = time.time()
    dirs2 = gen_dirs(rng=2, integer_only=False, permute_dedup=False)
    print(f"  {len(dirs2)} dirs ({time.time() - t0:.1f}s)", flush=True)
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
        ts = time.strftime("%H:%M:%S")
        print(f"[{i_p}/{len(work)}] {ts} {group} {b} {name}  "
              f"V={n_v} E={n_e}  starting search...", flush=True)
        hits = search(name, V, E, dirs2, verbose=False)
        groups = group_by_shape(hits, V, E)
        n_fp = len(groups)
        fp_hashes_now = {}
        for fp, examples in groups.items():
            h = hash_fp(fp)
            fp_hashes_now[h] = (fp, examples)
        known = known_hashes.get((group, b), set())
        aliases = known_aliases.get((group, b), set())
        new_hashes = sorted(set(fp_hashes_now) - known - aliases)
        unseen_known = sorted(known - set(fp_hashes_now))
        elapsed = time.time() - t0
        marker = " <<< NEW" if new_hashes else ""
        ts2 = time.strftime("%H:%M:%S")
        print(f"[{i_p}/{len(work)}] {ts2} {group} {b} {name}  "
              f"V={n_v} E={n_e}  fp={n_fp}  manifest={len(known)}  "
              f"alias={len(aliases)}  new={len(new_hashes)}  "
              f"miss={len(unseen_known)}  ({elapsed:.1f}s){marker}",
              flush=True)
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
            "alias_known": len(aliases),
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
    print(f"Total elapsed: {time.time() - t_total:.1f}s", flush=True)
    print(f"Wrote {out_path}", flush=True)
    n_with_new = sum(1 for r in summary_rows if r.get("new_fp", 0) > 0)
    n_total_new = sum(r.get("new_fp", 0) for r in summary_rows)
    print(f"Summary: {n_with_new} polytopes have new fp; "
          f"{n_total_new} new fp_hashes total.", flush=True)


if __name__ == "__main__":
    main()
