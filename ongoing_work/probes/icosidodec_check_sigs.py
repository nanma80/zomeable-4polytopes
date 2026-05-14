"""Check shape_signature on all 6 icosidodecahedron_prism rng=4 files."""
import os
import sys
from pathlib import Path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "lib"))

from dedup_corpus_by_shape import parse_vzome, shape_signature

FOLDER = os.path.join(ROOT, "output", "polyhedral_prisms", "icosidodecahedron_prism")

print(f"Files in {FOLDER}:")
results = []
for fn in sorted(os.listdir(FOLDER)):
    if not fn.endswith(".vZome"):
        continue
    path = Path(os.path.join(FOLDER, fn))
    try:
        P, E = parse_vzome(path)
        sig = shape_signature(P, E)
        results.append((fn, sig, P.shape[0]))
        print(f"  {fn:40s}  V={P.shape[0]:3d}  sig={sig[:16]}...")
    except Exception as e:
        print(f"  {fn:40s}  ERROR: {e}")

print()
print("=== Grouped by signature (any same group = duplicates) ===")
from collections import defaultdict
groups = defaultdict(list)
for fn, sig, nv in results:
    groups[sig].append((fn, nv))

for sig, items in groups.items():
    if len(items) > 1:
        print(f"  DUPLICATE GROUP (sig={sig[:16]}...):")
        for fn, nv in items:
            print(f"    {fn}  V={nv}")
    else:
        fn, nv = items[0]
        print(f"  unique: {fn}  V={nv}")

print()
print(f"Total files: {len(results)}, distinct shapes: {len(groups)}")
