"""Drive duoprism_4_q snap+sig probes across all q values of interest.

For each q in QS:
  1. ab00 plane at rng=4 (cheap, ~2 min)  -- verify saturation
  2. abcd plane at rng=3 (medium, ~10 min) -- verify no off-square shapes

Writes a consolidated census table to ongoing_work/duoprism_4q_census.md.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

QS = [5, 6, 7, 8, 9, 10, 11, 12]
PROBE = os.path.join(ROOT, "ongoing_work", "probes", "duoprism_4q_snap_sig.py")


def run_one(q, plane, rngs):
    cmd = [sys.executable, "-u", PROBE,
           "--q", str(q), "--plane", plane,
           "--rngs", ",".join(str(r) for r in rngs)]
    log_path = os.path.join(ROOT, "ongoing_work",
                            f"probe_4q_q{q}_{plane}.log")
    print(f"[{time.strftime('%H:%M:%S')}] >>> q={q} plane={plane} rngs={rngs}",
          flush=True)
    t0 = time.time()
    with open(log_path, "w", encoding="utf-8") as fh:
        proc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT,
                              cwd=ROOT)
    elapsed = time.time() - t0
    print(f"  done in {elapsed:.0f}s rc={proc.returncode} log={log_path}",
          flush=True)
    return elapsed, proc.returncode


def load_sigs(q, plane, rng):
    path = os.path.join(ROOT, "ongoing_work",
                        f"probe_4q_sigs_q{q}_{plane}_rng{rng}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def main():
    print("=== duoprism_4_q comprehensive census ===", flush=True)
    print(f"qs = {QS}", flush=True)
    print(flush=True)

    t_total = time.time()
    # ab00 cheap probes first - rng 2,3,4
    for q in QS:
        run_one(q, "ab00", [2, 3, 4])
    # then abcd at rng 2,3 (medium)
    for q in QS:
        run_one(q, "abcd", [2, 3])
    print(f"TOTAL: {time.time() - t_total:.0f}s", flush=True)

    # Build census table.
    rows = []
    for q in QS:
        row = {"q": q}
        for plane in ("ab00", "abcd"):
            for rng in (2, 3, 4):
                d = load_sigs(q, plane, rng)
                if d:
                    row[f"{plane}_rng{rng}"] = d["n_sigs"]
                    row[f"{plane}_rng{rng}_snap"] = d["n_snapped"]
                    row[f"{plane}_rng{rng}_align"] = d["n_aligned"]
                else:
                    row[f"{plane}_rng{rng}"] = None
        rows.append(row)

    # Write census markdown.
    md_path = os.path.join(ROOT, "ongoing_work", "duoprism_4q_census.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("# duoprism_4_q snap+signature census\n\n")
        fh.write("Per-q distinct shape signatures on the (a,b,0,0) and (a,b,c,d)\n")
        fh.write("kernel planes at multiple rngs.  Probe: "
                 "`ongoing_work/probes/duoprism_4q_snap_sig.py`.\n\n")
        fh.write("Signature = robust 5-decimal SHA-256 (same as "
                 "`tools/dedup_corpus_by_shape.py`).\n\n")
        fh.write("## (a,b,0,0) plane — square plane only\n\n")
        fh.write("| q | rng=2 sigs | rng=3 sigs | rng=4 sigs | rng=4 snap | rng=4 align |\n")
        fh.write("|---|-----------:|-----------:|-----------:|-----------:|------------:|\n")
        for r in rows:
            q = r["q"]
            fh.write(f"| {q} | {r.get('ab00_rng2','—')} | "
                     f"{r.get('ab00_rng3','—')} | {r.get('ab00_rng4','—')} | "
                     f"{r.get('ab00_rng4_snap','—')} | "
                     f"{r.get('ab00_rng4_align','—')} |\n")
        fh.write("\n## (a,b,c,d) plane — full 4D directions\n\n")
        fh.write("| q | rng=2 sigs | rng=3 sigs | rng=2 snap | rng=3 snap | rng=3 align |\n")
        fh.write("|---|-----------:|-----------:|-----------:|-----------:|------------:|\n")
        for r in rows:
            q = r["q"]
            fh.write(f"| {q} | {r.get('abcd_rng2','—')} | "
                     f"{r.get('abcd_rng3','—')} | "
                     f"{r.get('abcd_rng2_snap','—')} | "
                     f"{r.get('abcd_rng3_snap','—')} | "
                     f"{r.get('abcd_rng3_align','—')} |\n")
        fh.write("\n")
        fh.write("## Reading the table\n\n")
        fh.write("- **sigs** = number of distinct shape signatures emitted.\n")
        fh.write("- **snap** = number of (kernel direction, scale) pairs that\n")
        fh.write("  successfully snapped to the zome lattice.\n")
        fh.write("- **align** = number of directions that passed the\n")
        fh.write("  `_try_align` axis classification (but may not have snapped).\n\n")
        fh.write("A q-value with snap=0 at a high rng confirms that no kernel\n")
        fh.write("direction in that range can produce a zomeable projection.\n")
    print(f"Wrote {md_path}", flush=True)


if __name__ == "__main__":
    main()
