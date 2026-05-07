"""M17d: project EVERY B4 Wythoff descendant along the 3 antiprism master
kernels and check whether the resulting projection is zomeable and whether
the resulting shape is already in the corpus.

Currently 3 B4 polytopes have the antiprism trio of obliques in the corpus:
  - rectified tesseract (V=32, M14 rng=4)
  - truncated 16-cell  (V=48, M14 rng=4)
  - bitruncated tesseract (V=96, M17 rng=2 d-d)

Question: do the OTHER 9 B4 Wythoff descendants also have the antiprism
trio?  If we project each along the 3 antiprism master kernels, do we get
3 zomeable shapes per polytope that are not already in the corpus?

Using the same probe pattern as test_antiprism_hypothesis.py.
"""
import sys
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
SQRT5 = 5.0 ** 0.5

ANTIPRISM = {
    "B6R12Y6": [2 * PHI ** 3,    2.0,         -2 * PHI ** 3, 2 * PHI ** 3],
    "R12B6Y6": [1 / PHI ** 2,    3 * PHI - 4, -1 / PHI ** 2, 1 / PHI ** 2],
    "Y6R12B6": [1 + 2 * PHI ** 3, SQRT5,       SQRT5,        -SQRT5],
}

# 12 non-regular B4 Wythoff polytopes
B4_POLY = [
    ("rectified tesseract",                (0, 1, 0, 0)),  # has trio (M14)
    ("truncated 16-cell",                  (0, 0, 1, 1)),  # has trio (M14)
    ("bitruncated tesseract",              (0, 1, 1, 0)),  # has trio (M17)
    ("truncated tesseract",                (1, 1, 0, 0)),
    ("cantellated tesseract",              (1, 0, 1, 0)),
    ("runcinated tesseract",               (1, 0, 0, 1)),
    ("cantellated 16-cell / rect 24-cell", (0, 1, 0, 1)),
    ("cantitruncated tesseract",           (1, 1, 1, 0)),
    ("cantitr 16-cell / trunc 24-cell",    (0, 1, 1, 1)),
    ("runcitruncated tesseract",           (1, 1, 0, 1)),
    ("runcitruncated 16-cell",             (1, 0, 1, 1)),
    ("omnitruncated tesseract",            (1, 1, 1, 1)),
]

# Index every existing corpus shape by sig hash (the str-truncated [:10] hash
# at index [2] of the 4-tuple sig, same as test_antiprism_hypothesis.py).
print("Indexing corpus...")
corpus = {}  # sig_hash -> "category/file.vZome"
for d in ["5cell", "16cell", "24cell", "120cell", "600cell"]:
    p = ROOT / "output" / d
    if not p.exists():
        continue
    for vz in p.glob("*.vZome"):
        try:
            P, E = parse_vzome(vz)
            sig = shape_signature(P, E)
            corpus[sig[2]] = f"{d}/{vz.name}"
        except Exception:
            pass

ws_root = ROOT / "output" / "wythoff_sweep"
for vz in ws_root.rglob("*.vZome"):
    try:
        P, E = parse_vzome(vz)
        sig = shape_signature(P, E)
        rel = vz.relative_to(ws_root)
        corpus[sig[2]] = f"wythoff_sweep/{rel.as_posix()}"
    except Exception:
        pass
print(f"  {len(corpus)} unique sig hashes across full corpus\n")

scratch = ROOT / "ongoing_work" / "scratch_m17d"
scratch.mkdir(exist_ok=True)

print(f"{'polytope':40s} {'V':>5s}  {'kernel':10s}  {'align':6s}  {'snap':5s}  shape")
print("=" * 130)

novel_candidates = []
fail_summary = {}  # poly -> [list of failed kernels]
for poly_name, bm in B4_POLY:
    try:
        V4, E_idx = build_polytope("B4", bm)
    except Exception as e:
        print(f"{poly_name:40s}  build FAILED: {e}")
        continue
    V_arr = np.asarray(V4, dtype=float)
    edges_diff_T = np.array([V_arr[b] - V_arr[a] for a, b in E_idx]).T  # (4, E)

    for kname, kvec in ANTIPRISM.items():
        n_arr = np.asarray(kvec, dtype=float)
        Q3x4 = projection_matrix(n_arr)
        edges_dirs = Q3x4 @ edges_diff_T
        align = _try_align(edges_dirs)
        if align is None:
            print(f"{poly_name:40s} {len(V_arr):>5d}  {kname:10s}  FAIL    -      -")
            fail_summary.setdefault(poly_name, []).append(kname)
            continue
        out_vz = scratch / f"{poly_name.replace(' ','_').replace('/','-')}_{kname}.vZome"
        try:
            project_and_emit(f"{poly_name}_{kname}",
                             V_arr, E_idx, n_arr,
                             str(out_vz), verbose=False)
        except Exception as e:
            print(f"{poly_name:40s} {len(V_arr):>5d}  {kname:10s}  OK      FAIL   ({type(e).__name__}: {str(e)[:50]})")
            fail_summary.setdefault(poly_name, []).append(f"{kname}(snap)")
            continue
        try:
            P3, E3 = parse_vzome(out_vz)
            sig = shape_signature(P3, E3)
            sigh = sig[2]
        except Exception as e:
            print(f"{poly_name:40s} {len(V_arr):>5d}  {kname:10s}  OK      OK     parse-err {e}")
            continue
        match = corpus.get(sigh)
        if match:
            tag = f"in corpus: {match}"
        else:
            tag = f"** NEW SHAPE ** sig={sigh[:12]}"
            novel_candidates.append((poly_name, bm, kname, len(P3), len(E3), sigh))
        print(f"{poly_name:40s} {len(V_arr):>5d}  {kname:10s}  OK      OK     V={len(P3):3d} E={len(E3):3d}  {tag}")
    print()

print("=" * 130)
print(f"NOVEL SHAPE CANDIDATES (snap OK, not yet in corpus): {len(novel_candidates)}")
for c in novel_candidates:
    print(f"  {c[0]:40s} bm={c[1]} kernel={c[2]} V={c[3]} E={c[4]} sig={c[5][:12]}")

print()
print(f"SNAP-FAIL SUMMARY (kernel direction not zomeable for descendant):")
for poly, fails in fail_summary.items():
    print(f"  {poly:40s} fails on: {fails}")
