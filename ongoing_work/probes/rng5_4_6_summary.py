"""Quick summary of duoprism_4_6 rng=5 result."""
import json

for line in open("ongoing_work/prismatic_sweep_log.jsonl"):
    r = json.loads(line)
    if r.get("rng") == 5 and r.get("slug") == "duoprism_4_6":
        emits = [e for e in r.get("emitted", []) if isinstance(e, dict)]
        n_emit = sum(1 for e in emits if e.get("status") == "emitted")
        n_fail = sum(1 for e in emits if e.get("status") == "snap_failed")
        print(f"duoprism_4_6 at rng=5:")
        print(f"  raw_hits        = {r['raw_hits']}")
        print(f"  after_dir_dedup = {r.get('after_dir_dedup','?')}")
        print(f"  unique_shapes   = {r['unique_shapes']}")
        print(f"  emitted         = {n_emit}")
        print(f"  snap_failed     = {n_fail}")
        print(f"  elapsed         = {r.get('elapsed_s','?')} s")
        print()
        if n_emit:
            print("Emitted kernels (sorted by L2 norm):")
            okk = [e for e in emits if e.get("status") == "emitted"]
            for e in sorted(okk, key=lambda x: sum(c*c for c in x.get("kernel", []))):
                k = e.get("kernel")
                bn = e.get("basename")
                lab = e.get("label")
                sub = e.get("subtype")
                norm2 = sum(c*c for c in k)
                print(f"  {bn:25s} label={lab:12s} subtype={str(sub):8s} kernel={k}  |k|^2={norm2:.4f}")
        break
