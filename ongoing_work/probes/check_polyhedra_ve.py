"""Sanity check V/E counts for the 18 convex uniform polyhedra."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from uniform_polyhedra import UNIFORM_POLYHEDRA, get_polyhedron, expected_VE, all_polyhedra

print(f"{'name':<32s}  V        E         zphi  notes")
print("-" * 80)
fail = 0
for name in all_polyhedra():
    try:
        V, edges = get_polyhedron(name)
        nv_exp, ne_exp, zphi = expected_VE(name)
        ok_v = (len(V) == nv_exp)
        ok_e = (len(edges) == ne_exp)
        flag = "OK" if (ok_v and ok_e) else "FAIL"
        if not (ok_v and ok_e):
            fail += 1
        print(f"{name:<32s}  {len(V):3d}({nv_exp:3d})  {len(edges):3d}({ne_exp:3d})  {str(zphi):5s}  [{flag}]")
    except Exception as e:
        print(f"{name:<32s}  ERR: {e}")
        fail += 1

print()
print(f"Total failures: {fail}")
sys.exit(0 if fail == 0 else 1)
