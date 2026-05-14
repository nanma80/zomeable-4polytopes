"""Inspect icosidodecahedron_prism rng=3 vs rng=4 shapes."""
import json

m3 = json.load(open("ongoing_work/prismatic_manifest_rng3_snapshot.json"))
print("=== rng=3 baseline (from snapshot) ===")
rng3_shapes = []
for fam in m3["families"].values():
    for p in fam:
        if p["slug"] == "icosidodecahedron_prism":
            for s in p["shapes"]:
                rng3_shapes.append(s)
                print(f"  {s['basename']:35s} label={s['label']:12s} subtype={str(s.get('subtype')):20s} kernel={s.get('kernel')}")

print()
print("=== rng=4 sweep emitted (from log) ===")
rng4_emits = []
for line in open("ongoing_work/prismatic_sweep_log.jsonl"):
    r = json.loads(line)
    if r.get("rng") == 4 and r.get("slug") == "icosidodecahedron_prism":
        for e in r.get("emitted", []):
            if isinstance(e, dict) and e.get("status") == "emitted":
                rng4_emits.append(e)
                print(f"  {e['basename']:35s} label={e['label']:12s} subtype={str(e.get('subtype')):20s} kernel={e.get('kernel')}")
        break

print()
print(f"rng=3 had {len(rng3_shapes)} shapes; rng=4 emitted {len(rng4_emits)}")
print()

rng3_kernels = {tuple(s["kernel"]) for s in rng3_shapes}
rng4_kernels = {tuple(e["kernel"]) for e in rng4_emits}

print("=== Kernels present in rng=4 but NOT rng=3 (the new ones) ===")
new = rng4_kernels - rng3_kernels
for k in new:
    for e in rng4_emits:
        if tuple(e["kernel"]) == k:
            print(f"  {e['basename']:35s}  kernel={list(k)}  |k|^2={sum(c*c for c in k):.4f}")
            break

print()
print("=== Kernels present in rng=3 but NOT rng=4 (any losses) ===")
lost = rng3_kernels - rng4_kernels
for k in lost:
    for s in rng3_shapes:
        if tuple(s["kernel"]) == k:
            print(f"  {s['basename']:35s}  kernel={list(k)}")
            break
