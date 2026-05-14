"""Run shape_signature on any prismatic folder."""
import os, sys
from pathlib import Path
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "lib"))

from dedup_corpus_by_shape import parse_vzome, shape_signature

folder = sys.argv[1] if len(sys.argv) > 1 else "output/duoprisms/duoprism_4_10"
FOLDER = os.path.join(ROOT, folder)
print(f"Folder: {folder}")

results = []
for fn in sorted(os.listdir(FOLDER)):
    if not fn.endswith(".vZome"):
        continue
    path = Path(os.path.join(FOLDER, fn))
    try:
        P, E = parse_vzome(path)
        sig = shape_signature(P, E)
        results.append((fn, sig, P.shape[0], len(E)))
        print(f"  {fn:40s}  V={P.shape[0]:3d}  E={len(E):3d}  sig={sig[2][:16]}")
    except Exception as e:
        print(f"  {fn:40s}  ERROR: {e}")

groups = defaultdict(list)
for fn, sig, nv, ne in results:
    groups[sig].append((fn, nv, ne))

print()
print("=== Grouped by shape_signature ===")
for sig, items in groups.items():
    if len(items) > 1:
        print(f"  DUPLICATE GROUP (V={items[0][1]} E={items[0][2]} hash={sig[2][:16]}):")
        for fn, nv, ne in items:
            print(f"    {fn}")
    else:
        fn, nv, ne = items[0]
        print(f"  unique: {fn:40s} V={nv} E={ne}")

print()
print(f"Total files: {len(results)},  distinct shapes: {len(groups)}")
