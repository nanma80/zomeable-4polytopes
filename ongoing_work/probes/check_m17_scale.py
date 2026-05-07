"""Diagnostic: scale of the 3 M17 bitruncated_tesseract V=96 obliques
relative to the inheritance master directions in rectified_tesseract /
truncated_16-cell, and to one another.

User observation (2026-05-07): face_first_hexagon (renamed to oblique_02 in M17b) should be /phi^2,
oblique_01 should be /phi, oblique_00 unchanged.
"""
import sys
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

from dedup_corpus_by_shape import parse_vzome

PHI = (1 + 5 ** 0.5) / 2

def stats(path):
    P, E = parse_vzome(path)
    L = np.array([np.linalg.norm(P[i] - P[j]) for i, j in E])
    R = np.linalg.norm(P, axis=1)
    return {
        "V": len(P),
        "E": len(E),
        "min_edge": float(L.min()),
        "max_edge": float(L.max()),
        "max_radius": float(R.max()),
    }

# 3 antiprism inheritance trios + the 3 M17 entries
groups = {
    "B6R12Y6": [
        ("output/wythoff_sweep/rectified_tesseract/oblique_00_e2b79a96f7.vZome",  "rect_tess oblique_00"),
        ("output/wythoff_sweep/truncated_16-cell/oblique_00_9d18eb2806.vZome",     "trunc_16  oblique_00"),
        ("output/wythoff_sweep/bitruncated_tesseract/oblique_00_26f0b7c6e6.vZome", "bitr_tess oblique_00"),
    ],
    "R12B6Y6": [
        ("output/wythoff_sweep/rectified_tesseract/oblique_01_b35b865a54.vZome",          "rect_tess oblique_01"),
        ("output/wythoff_sweep/truncated_16-cell/oblique_01_ccdfd208c9.vZome",            "trunc_16  oblique_01"),
        ("output/wythoff_sweep/bitruncated_tesseract/oblique_01_df821cc628.vZome","bitr_tess oblique_01"),
    ],
    "Y6R12B6": [
        ("output/wythoff_sweep/rectified_tesseract/oblique_02_2be6954c03.vZome",  "rect_tess oblique_02"),
        ("output/wythoff_sweep/truncated_16-cell/oblique_02_2c50f047a8.vZome",     "trunc_16  oblique_02"),
        ("output/wythoff_sweep/bitruncated_tesseract/oblique_02_80a961d9da.vZome", "bitr_tess oblique_02"),
    ],
}

for grp, items in groups.items():
    print(f"\n=== {grp} antiprism inheritance trio ===")
    print(f"  {'file':32s}  {'V':>3s}  {'min_edge':>10s}  {'max_radius':>10s}  {'/phi^k vs first':>15s}")
    base_min = None
    for path, label in items:
        s = stats(ROOT / path)
        if base_min is None:
            base_min = s["min_edge"]
            ratio = "1.00"
        else:
            r = s["min_edge"] / base_min
            # find nearest phi power
            import math
            k = math.log(r, PHI) if r > 0 else 0
            ratio = f"{r:.4f} ~ phi^{k:.2f}"
        print(f"  {label:32s}  {s['V']:3d}  {s['min_edge']:10.5f}  {s['max_radius']:10.5f}  {ratio}")
