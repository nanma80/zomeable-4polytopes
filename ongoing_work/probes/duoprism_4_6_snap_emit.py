"""Test inf-family hypothesis for duoprism_4_6 by SNAP-emit success at rng=2..5.

Only enumerates kernels of form (a, b, 0, 0) since all 3 known emit kernels
(at rng=3) have this form, and the geometry argument confirms: kernel in
{4}-plane preserves {6}-plane fully, and any other kernel direction mixes
the hex-edges with the square-edges in ways that break alignment.

For each kernel:
  - Run search_engine.search (directional zomeable test)
  - Dedup by direction + group by shape
  - Try project_and_emit (writes to a temp file, then deletes)
  - Count snap-emit successes

Output: number of distinct snap-emittable shapes per rng.
"""
import sys
import os
import tempfile
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "lib"))

import numpy as np
from itertools import product
from collections import Counter
import hashlib

from polytopes_prismatic import duoprism
from search_engine import projection_matrix, _try_align, search, group_by_shape, phi
from emit_generic import project_and_emit


def gen_2d_dirs(rng):
    """Kernels (a, b, 0, 0) with ZZ[phi]-coefficients |coeff|<=rng."""
    vals = sorted({round(a + b * phi, 9) for a in range(-rng, rng + 1)
                                          for b in range(-rng, rng + 1)})
    out = set()
    for n0, n1 in product(vals, repeat=2):
        if n0 == 0 and n1 == 0:
            continue
        if n0 != 0:
            sgn = 1 if n0 > 0 else -1
        else:
            sgn = 1 if n1 > 0 else -1
        out.add((sgn * n0, sgn * n1, 0.0, 0.0))
    return [np.array(v) for v in out]


def _dedup_by_direction(hits, cos_tol=1e-6):
    if not hits:
        return hits
    K = np.array([h[0] for h in hits], dtype=float)
    norms = np.linalg.norm(K, axis=1)
    Ku = K / np.maximum(norms, 1e-12)[:, None]
    seen = np.zeros(len(hits), dtype=bool)
    kept = []
    for i in range(len(hits)):
        if seen[i]:
            continue
        sim = np.where((Ku @ Ku[i]) > 1 - cos_tol)[0]
        seen[sim] = True
        canon = sim[int(np.argmin([norms[j] for j in sim]))]
        kept.append(hits[int(canon)])
    return kept


def main():
    V, edges = duoprism(4, 6)
    print(f"duoprism_4_6: V={len(V)}, E={len(edges)}")
    tmpdir = tempfile.mkdtemp(prefix="duo46_probe_")
    try:
        for rng in [2, 3, 4, 5]:
            dirs = gen_2d_dirs(rng)
            print(f"\n=== rng={rng}: {len(dirs)} kernels in (a, b, 0, 0) plane ===")
            hits = search("duoprism_4_6", V, edges, dirs, verbose=False)
            print(f"  search() returned {len(hits)} directional hits")
            hits = _dedup_by_direction(hits)
            print(f"  after dir-dedup: {len(hits)}")
            groups = group_by_shape(hits, V, edges)
            print(f"  unique shape groups: {len(groups)}")

            # canonical pick: smallest |n| per group
            canonicals = []
            for fp, occs in groups.items():
                idx = min(range(len(occs)), key=lambda i: np.linalg.norm(occs[i][0]))
                canonicals.append((fp, occs[idx][0], occs[idx][2]))

            # try snap-emit each
            n_emit = 0
            n_snap_fail = 0
            emit_kernels = []
            for fp, n_tuple, n_balls in canonicals:
                tmp_path = os.path.join(tmpdir, f"probe_{n_emit + n_snap_fail}.vZome")
                try:
                    project_and_emit("probe", V, edges, np.array(n_tuple),
                                     tmp_path, verbose=False)
                    n_emit += 1
                    emit_kernels.append(n_tuple)
                except Exception:
                    n_snap_fail += 1
            print(f"  snap-emit: {n_emit} success, {n_snap_fail} fail")
            print(f"  emittable kernels:")
            for k in sorted(emit_kernels, key=lambda x: np.linalg.norm(x)):
                a, b, _, _ = k
                print(f"    ({a:+.4f}, {b:+.4f}, 0, 0)   |k|={np.linalg.norm(k):.4f}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
