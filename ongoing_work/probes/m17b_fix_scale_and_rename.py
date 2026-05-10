"""M17b fix: rescale + rename the 3 M17 bitruncated_tesseract V=96 obliques
to match the antiprism inheritance trio canonical scale (min_edge=12.31073,
matching rectified_tesseract / truncated_16-cell oblique entries and the
16-cell antiprism master files).

User observation (2026-05-07): all 3 M17 V=96 files emit at scales that
are clean phi-power multiples of the canonical 12.31:
    - oblique_00_80a961d9da:        12.31  (already correct, phi^0)
    - oblique_01_26f0b7c6e6:        19.92  = 12.31 * phi    -> /phi
    - face_first_hexagon_df821cc628: 32.23 = 12.31 * phi^2  -> /phi^2

Stage 5b in promote_blind_spot_m17.py missed this because it pooled
against ALL existing files in the slug folder, including
face_first_square (min_edge=9.07) and cell_first_truncated_octahedron
(min_edge=10.47), neither of which is an antiprism-class projection
and so neither shares the canonical 12.31 scale.

Additional fix: face_first_hexagon is misnamed -- it is actually
oblique (not face-first; the two hexagons near the projection center
are not centered).  Rename to oblique_02_df821cc628.vZome to match
the rect_tess/trunc_16 naming convention (which uses oblique_00,
oblique_01, oblique_02 for the 3 antiprism inheritance kernels).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

import numpy as np
from dedup_corpus_by_shape import parse_vzome, shape_signature
from scale_vzome_by_inv_phi import transform_text as inv_phi

OUT = ROOT / "output" / "wythoff_sweep" / "bitruncated_tesseract"
MANIFEST = ROOT / "output" / "wythoff_sweep" / "manifest.json"
PHI = (1 + 5 ** 0.5) / 2

# (current_filename, divisions_by_phi, new_filename_or_None)
ACTIONS = [
    ("oblique_00_80a961d9da.vZome",         0, None),
    ("oblique_01_26f0b7c6e6.vZome",         1, None),
    ("face_first_hexagon_df821cc628.vZome", 2, "oblique_02_df821cc628.vZome"),
]

print("=" * 80)
print("Stage 1: Verify current scales and recompute Stage-B sigs")
print("=" * 80)
for fname, k, newname in ACTIONS:
    p = OUT / fname
    P, E = parse_vzome(p)
    L = np.array([np.linalg.norm(P[i] - P[j]) for i, j in E])
    sig = shape_signature(P, E)
    print(f"  {fname:55s}  V={len(P)} min_edge={L.min():.5f}  sig={sig[2][:10]}  /phi^{k}")

print()
print("=" * 80)
print("Stage 2: Apply scale (in place) and verify min_edge approaches 12.31")
print("=" * 80)
TARGET = 12.31073
sig_map = {}  # original sig hash -> (new_path, new_sig hash)
for fname, k, newname in ACTIONS:
    p = OUT / fname
    P_old, E_old = parse_vzome(p)
    sig_old = shape_signature(P_old, E_old)
    if k > 0:
        text = p.read_text(encoding="utf-8")
        for _ in range(k):
            text = inv_phi(text)
        p.write_text(text, encoding="utf-8")
    P_new, E_new = parse_vzome(p)
    L_new = np.array([np.linalg.norm(P_new[i] - P_new[j]) for i, j in E_new])
    sig_new = shape_signature(P_new, E_new)
    if sig_new[2] != sig_old[2]:
        print(f"  FATAL: sig changed during rescale: {sig_old[2]} -> {sig_new[2]}")
        sys.exit(1)
    if abs(L_new.min() - TARGET) > 0.001:
        print(f"  WARNING: min_edge {L_new.min():.5f} not at canonical {TARGET:.5f}")
    print(f"  {fname:55s}  /phi^{k} -> min_edge={L_new.min():.5f}  sig unchanged ({sig_new[2][:10]})")
    sig_map[sig_old[2]] = (fname, newname or fname, sig_new[2])

print()
print("=" * 80)
print("Stage 3: Rename face_first_hexagon -> oblique_02")
print("=" * 80)
for fname, k, newname in ACTIONS:
    if newname is None or newname == fname:
        continue
    src = OUT / fname
    dst = OUT / newname
    if dst.exists():
        print(f"  refuse to overwrite existing {dst.name}")
        sys.exit(1)
    src.rename(dst)
    print(f"  renamed {fname} -> {newname}")

print()
print("=" * 80)
print("Stage 4: Update manifest.json (file path + label/subtype for renamed entry)")
print("=" * 80)
manifest = json.loads(MANIFEST.read_text())
n_updates = 0
for s in manifest["shapes"]:
    fp = s.get("fp_hash")
    if fp not in sig_map:
        continue
    old_fname, new_fname, sig_hash = sig_map[fp]
    file_path = s.get("file", "")
    if old_fname not in file_path:
        continue
    new_path = file_path.replace(old_fname, new_fname)
    s["file"] = new_path
    if old_fname != new_fname:
        # Reclassify as oblique (was face_first / hexagon)
        s["label"] = "oblique"
        s["label_subtype"] = "00"  # subtype index 02 is captured in filename
        s["note"] = (s.get("note", "") + "  Renamed in M17b: was misclassified as "
                     "face_first_hexagon; correctly an oblique projection (the "
                     "two hexagons near the projection center are off-center, "
                     "and the kernel is the bitr_tesseract image of the 16-cell "
                     "antiprism R12B6Y6 master direction).").strip()
    s.setdefault("note", "")
    if "M17b" not in s["note"]:
        s["note"] = (s["note"] + "  Rescaled in M17b by /phi^"
                     + str(next(k for fn, k, nn in ACTIONS if fn == old_fname))
                     + " to match antiprism canonical scale 12.31073.").strip()
    n_updates += 1
    print(f"  manifest entry fp={fp[:10]}: file = {new_path}")
print(f"  updated {n_updates} manifest entries")

manifest.setdefault("notes", []).append(
    "Milestone 17b: rescaled the 3 M17 bitruncated_tesseract V=96 oblique "
    "files to canonical antiprism scale (min_edge=12.31073) by /phi^k for "
    "k=0,1,2 respectively, and renamed face_first_hexagon_df821cc628 to "
    "oblique_02_df821cc628 (it is a bitr_tesseract image of the 16-cell "
    "antiprism R12B6Y6 master kernel, not a face-first hexagonal projection)."
)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True))
print(f"\n  manifest written; {len(manifest['shapes'])} shape entries")

print()
print("=" * 80)
print("Stage 5: Verify all 3 antiprism trios share min_edge = 12.31073")
print("=" * 80)
trios = [
    ("rectified_tesseract/oblique_00_e2b79a96f7.vZome",
     "truncated_16-cell/oblique_00_9d18eb2806.vZome",
     "bitruncated_tesseract/oblique_01_26f0b7c6e6.vZome"),
    ("rectified_tesseract/oblique_01_b35b865a54.vZome",
     "truncated_16-cell/oblique_01_ccdfd208c9.vZome",
     "bitruncated_tesseract/oblique_02_df821cc628.vZome"),
    ("rectified_tesseract/oblique_02_2be6954c03.vZome",
     "truncated_16-cell/oblique_02_2c50f047a8.vZome",
     "bitruncated_tesseract/oblique_00_80a961d9da.vZome"),
]
for trio in trios:
    print(f"  trio:")
    for f in trio:
        path = ROOT / "output" / "wythoff_sweep" / f
        P, E = parse_vzome(path)
        L = np.array([np.linalg.norm(P[i] - P[j]) for i, j in E])
        print(f"    {f:60s}  V={len(P):3d}  min_edge={L.min():.5f}")
