"""Step-1-bypass blind-spot audit at rng=2.

For every (group, bitmask) in A4 + B4 + F4 (skipping regulars and
already-audited polytopes), run `search` directly on the descendant
without first filtering through the parent-regular snap test.  Compare
each surfaced fingerprint to what's already present in
`output/wythoff_sweep/manifest.json`; anything new is a "blind-spot
finding" that the original parent-filtered Step 2 missed.

Skips H4 by default (V > 600 makes rng=2 descendant-direct expensive
on the bigger H4 polytopes; do a separate focused pass).

Output:
  ongoing_work/blind_spot_audit_rng2.json
"""
import os, sys, json, time, hashlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

from wythoff import build_polytope                         # noqa: E402
from search_engine import gen_dirs, search, group_by_shape  # noqa: E402
from uniform_polytopes import all_uniform_polytopes, KNOWN_DUPLICATES  # noqa: E402


def hash_fp(fp):
    """Match _hash_fingerprint() in tools/run_wythoff_sweep.py."""
    n_balls, dists = fp
    if (isinstance(dists, tuple) and len(dists) == 2
            and dists[0] == "multiset"):
        items = dists[1]
        payload = repr(("multiset", int(n_balls),
                        tuple((round(float(v), 6), int(c))
                              for v, c in items)))
    else:
        payload = repr((int(n_balls),
                        tuple(round(float(d), 6) for d in dists)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# Polytopes we have already empirically audited via descendant-direct
# search at rng=4 (or via a dedicated focused probe).  Skip these to
# avoid duplicate work; their findings are already in the manifest.
ALREADY_AUDITED = {
    ("B4", (0, 1, 0, 0)),  # rectified tesseract  (rect_tess_rng4_focused.py)
    ("B4", (0, 0, 1, 1)),  # truncated 16-cell    (trunc16_rng4_focused.py)
    ("B4", (0, 1, 0, 1)),  # cantellated 16-cell  (cantel16_rng4_focused.py)
    ("B4", (0, 1, 1, 1)),  # cantitruncated 16-cell (cantitr16_rng4_focused.py)
}

REGULAR_BITMASKS = {(1, 0, 0, 0), (0, 0, 0, 1)}


def main():
    os.chdir(ROOT)
    out_path = "ongoing_work/blind_spot_audit_rng2.json"

    # 1. Index the existing wythoff_sweep manifest by (group, bitmask) -> {fp_hash}
    manifest = json.load(open("output/wythoff_sweep/manifest.json"))
    print(f"manifest: {len(manifest['shapes'])} shape entries", flush=True)
    known_hashes = defaultdict(set)
    known_polys_seen = set()
    for sh in manifest["shapes"]:
        key = (sh["group"], tuple(sh["bitmask"]))
        known_hashes[key].add(sh["fp_hash"])
        known_polys_seen.add(key)
    print(f"  -> {len(known_polys_seen)} (group, bitmask) entries with known fp", flush=True)

    # 2. Build worklist
    work = []
    for group, b, name in all_uniform_polytopes():
        if group == "H4":
            continue
        if b in REGULAR_BITMASKS:
            continue
        if (group, b) in KNOWN_DUPLICATES:
            continue
        if (group, b) in ALREADY_AUDITED:
            continue
        work.append((group, b, name))
    print(f"audit worklist: {len(work)} polytopes (A4+B4+F4, "
          f"non-regular, non-already-audited)", flush=True)
    for g, b, n in work:
        print(f"   {g} {b}  {n}", flush=True)
    print(flush=True)

    # 3. Build dirs once (rng=2 = 195312 directions)
    print("Generating rng=2 directions...", flush=True)
    t0 = time.time()
    dirs2 = gen_dirs(rng=2, integer_only=False, permute_dedup=False)
    print(f"  {len(dirs2)} dirs ({time.time()-t0:.1f}s)", flush=True)
    print(flush=True)

    # 4. Iterate
    findings = []
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
        hits = search(name, V, E, dirs2, verbose=False)
        groups = group_by_shape(hits, V, E)
        n_fp = len(groups)
        # Hash + diff
        fp_hashes_now = {}
        for fp, examples in groups.items():
            h = hash_fp(fp)
            fp_hashes_now[h] = (fp, examples)
        known = known_hashes.get((group, b), set())
        new_hashes = sorted(set(fp_hashes_now) - known)
        unseen_known = sorted(known - set(fp_hashes_now))  # sanity-check: all known should resurface
        elapsed = time.time() - t0
        marker = " <<< NEW" if new_hashes else ""
        print(f"[{i_p}/{len(work)}] {group} {b} {name}  "
              f"V={n_v} E={n_e}  fp={n_fp}  manifest={len(known)}  "
              f"new={len(new_hashes)}  miss={len(unseen_known)}  "
              f"({elapsed:.1f}s){marker}", flush=True)
        # Capture full data for new fp
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
        # Persist after each polytope (safety)
        with open(out_path, "w") as f:
            json.dump({
                "rng": 2,
                "groups_audited": ["A4", "B4", "F4"],
                "skipped_already_audited": [
                    [g, list(b)] for (g, b) in sorted(ALREADY_AUDITED)],
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
