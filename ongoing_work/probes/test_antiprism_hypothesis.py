"""Test the hypothesis that all 3 M17 bitruncated tesseract shapes are
related to the 16-cell antiprism.

For each antiprism master kernel and each M17 kernel, project both
the 16-cell AND the bitruncated tesseract, and compare Stage-B sigs.
Also report kernel parallelism / phi-scaling relationships in
*nonlinear-coordinate* sense (per-axis sign+permutation by B4 Weyl
group, plus an overall phi-power scalar).
"""
import sys, json, itertools
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

# Documented 16-cell antiprism master kernels (from doc table).
# These are the actual kernels stored in 16cell_antiprism_*.vZome
# (per docs/WYTHOFF_SWEEP.md inheritance table around line 1093).
ANTIPRISM = {
    # exact phi-integer expressions verified against ongoing_work/b4_small_rng4_verify.json
    "B6R12Y6_master_A": [2 * PHI ** 3, 2.0,    -2 * PHI ** 3, 2 * PHI ** 3],   # [8.472136, 2, -8.472136, 8.472136]
    "R12B6Y6_master_B": [1 / PHI ** 2, 3 * PHI - 4, -1 / PHI ** 2, 1 / PHI ** 2],  # [0.381966, 0.854102, -0.381966, 0.381966]
    "Y6R12B6_master_C": [1 + 2 * PHI ** 3, SQRT5, SQRT5, -SQRT5],              # [9.472136, sqrt5, sqrt5, -sqrt5]
}

M17 = {
    "M17_oblique_00":         [1 / PHI ** 2, 1 / PHI ** 2, -1 / PHI ** 2, -PHI],
    "M17_oblique_01":         [1 / PHI ** 2, -PHI, PHI, PHI],
    "M17_face_first_hexagon": [PHI ** 3, -PHI, PHI, PHI],
}

# Index existing master regulars by Stage-B sig
master_sigs = {}
for d in ["5cell", "16cell", "24cell", "120cell", "600cell"]:
    p = ROOT / "output" / d
    if not p.exists():
        continue
    for vz in sorted(p.glob("*.vZome")):
        try:
            P, E = parse_vzome(vz)
            sig = shape_signature(P, E)
            master_sigs[sig[2]] = f"{d}/{vz.name}"
        except Exception:
            pass

# Index existing wythoff_sweep entries by sig
wythoff_sigs = {}
for vz in (ROOT / "output" / "wythoff_sweep").rglob("*.vZome"):
    try:
        P, E = parse_vzome(vz)
        sig = shape_signature(P, E)
        wythoff_sigs[sig[2]] = vz.relative_to(ROOT / "output" / "wythoff_sweep").as_posix()
    except Exception:
        pass

print(f"Indexed {len(master_sigs)} master sigs and {len(wythoff_sigs)} wythoff_sweep sigs\n")

PARENTS = [
    ("16-cell",            ("B4", (0, 0, 0, 1))),
    ("24-cell-as-B4",      ("B4", (0, 0, 1, 0))),
    ("bitr_tesseract",     ("B4", (0, 1, 1, 0))),
]
parent_VE = {name: build_polytope(*key) for name, key in PARENTS}

scratch = ROOT / "ongoing_work" / "scratch_antiprism_test"
scratch.mkdir(exist_ok=True)

def lookup(sig_hash):
    if sig_hash in master_sigs:
        return f"MASTER {master_sigs[sig_hash]}"
    if sig_hash in wythoff_sigs:
        return f"WYTHOFF {wythoff_sigs[sig_hash]}"
    return f"NEW (sig={sig_hash[:10]})"

print(f"{'kernel':25s}  {'parent':18s}  {'V':>3s}  {'align':6s}  {'snap':5s}  result")
print("=" * 110)
for kname, kvec in {**ANTIPRISM, **M17}.items():
    n = np.asarray(kvec, dtype=float)
    Q = projection_matrix(n)
    for pname, (V, E) in parent_VE.items():
        Vn = np.asarray(V, dtype=float)
        edges_dirs = (Q @ np.array([Vn[b] - Vn[a] for a, b in E]).T)
        res = _try_align(edges_dirs)
        if res is None:
            print(f"{kname:25s}  {pname:18s}  {len(V):3d}  FAIL    -      -")
            continue
        out = scratch / f"{pname}_{kname}.vZome"
        try:
            project_and_emit(f"{pname}_{kname}", V, E, kvec, str(out),
                             verbose=False)
        except Exception as exc:
            print(f"{kname:25s}  {pname:18s}  {len(V):3d}  OK      FAIL   ({type(exc).__name__})")
            continue
        P, E_out = parse_vzome(out)
        sig = shape_signature(P, E_out)
        print(f"{kname:25s}  {pname:18s}  {len(V):3d}  OK      OK     "
              f"V={len(P):3d} E={len(E_out):3d}  -> {lookup(sig[2])}")
    print()

# Test parallelism: is any M17 kernel a phi-power scaling of any antiprism kernel
# (after B4 Weyl group action)?
print("\nKernel-orbit equivalence check (sign-flips + permutations + phi^k scalar):")
print("=" * 90)
def orbit_match(n1, n2, tol=1e-6):
    """Is n1 == phi^k * sigma(n2) for some k in {-4..4} and sigma in B4 Weyl?"""
    n1 = np.asarray(n1, dtype=float)
    n2 = np.asarray(n2, dtype=float)
    for k in range(-4, 5):
        scale = PHI ** k
        for perm in itertools.permutations(range(4)):
            for signs in itertools.product([1, -1], repeat=4):
                permuted = scale * np.array([signs[i] * n2[perm[i]] for i in range(4)])
                if np.allclose(n1, permuted, atol=tol):
                    return (k, perm, signs)
    return None

for mname, mvec in M17.items():
    for aname, avec in ANTIPRISM.items():
        m = orbit_match(mvec, avec)
        if m is not None:
            k, perm, signs = m
            print(f"  {mname}  ==  phi^{k} * sigma({aname})   [perm={perm}, signs={signs}]")
        else:
            # Also try if they make the same projection by just being parallel up to phi^k
            n1 = np.asarray(mvec, dtype=float)
            n2 = np.asarray(avec, dtype=float)
            for k in range(-4, 5):
                if np.allclose(n1, (PHI ** k) * n2, atol=1e-6) or np.allclose(n1, -(PHI ** k) * n2, atol=1e-6):
                    print(f"  {mname}  ==  +/-phi^{k} * {aname}   (parallel!)")
                    break
