"""Final inheritance check for the 3 M17 bitruncated tesseract kernels.

For each kernel:
  - Does the tesseract zomeably project? (already shown: NO for all 3)
  - Does the 16-cell zomeably project, and to what shape?
    (already shown: YES for ob_00 -> Y6R12B6, YES for ob_01 -> B6R12Y6,
     NO for face_first_hex)
  - Does the 24-cell (in B4 basis = rect 16-cell) zomeably project?
"""
import sys, json
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

from wythoff import build_polytope
from search_engine import _try_align
from emit_generic import projection_matrix, project_and_emit
from dedup_corpus_by_shape import parse_vzome, shape_signature

PHI = (1.0 + 5.0 ** 0.5) / 2.0

KERNELS = [
    ("oblique_00",        [1/PHI**2, 1/PHI**2, -1/PHI**2, -PHI]),
    ("oblique_01",        [1/PHI**2, -PHI, PHI, PHI]),
    ("face_first_hexagon",[PHI**3, -PHI, PHI, PHI]),
]

# Index existing master regulars by Stage-B sig
master_sigs = {}
for d in ["5cell", "8cell", "16cell", "24cell", "600cell", "120cell"]:
    p = ROOT / "output" / d
    if not p.exists():
        continue
    for vz in sorted(p.glob("*.vZome")):
        try:
            P, E = parse_vzome(vz)
            sig = shape_signature(P, E)
            master_sigs[sig] = f"{d}/{vz.name}"
        except Exception:
            pass

# Test under each B4 parent
PARENTS = [
    ("tesseract",     ("B4", (1, 0, 0, 0))),
    ("16-cell",       ("B4", (0, 0, 0, 1))),
    ("24-cell-as-B4", ("B4", (0, 0, 1, 0))),
]
parent_VE = {}
for name, key in PARENTS:
    V, E = build_polytope(*key)
    parent_VE[name] = (np.asarray(V, dtype=float), E, key[1])

scratch = ROOT / "ongoing_work" / "scratch_m17_inheritance"
scratch.mkdir(exist_ok=True)

print(f"{'M17 kernel':25s}  {'parent':16s}  V    align    snap   master/sig")
print("=" * 95)
for kname, kvec in KERNELS:
    n = np.asarray(kvec, dtype=float)
    Q = projection_matrix(n)
    for pname, (V, E, _bm) in parent_VE.items():
        edges_dirs = (Q @ np.array([V[b] - V[a] for a, b in E]).T)
        res = _try_align(edges_dirs)
        if res is None:
            print(f"{kname:25s}  {pname:16s}  V={len(V):3d}  align=FAIL")
            continue
        # Snap + emit + sig
        out = scratch / f"{pname}_{kname}.vZome"
        try:
            project_and_emit(f"{pname}_{kname}", V, E, kvec, str(out),
                             verbose=False)
        except Exception as exc:
            print(f"{kname:25s}  {pname:16s}  V={len(V):3d}  align=OK   "
                  f"snap=FAIL  ({type(exc).__name__})")
            continue
        P, E_out = parse_vzome(out)
        sig = shape_signature(P, E_out)
        marker = master_sigs.get(sig, f"NEW (V={len(P)} E={len(E_out)})")
        print(f"{kname:25s}  {pname:16s}  V={len(V):3d}  align=OK   snap=OK  "
              f"-> {marker}")
    print()
