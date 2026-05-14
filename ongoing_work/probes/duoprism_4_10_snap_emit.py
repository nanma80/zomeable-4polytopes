"""Test the inf-family hypothesis for duoprism_4_10 with FULL snap-to-balls.

Uses the production sweep_polytope() pipeline but supplies a minimal
custom dirs list restricted to the (a,b,0,0) plane (the {4}-polygon
plane). At rng=N this plane has at most (2*(2N+1))^2 ~ 1681 kernels
(post sign-canonicalisation), vs gen_dirs(rng=5) = 107M (OOM-prone).

Hypothesis: duoprism_4_10 IS an inf-family — emit-count grows
super-saturated as rng increases. Compare to duoprism_4_6 which
saturates at 3 emit at every rng >= 3.

Usage:
    python ongoing_work/probes/duoprism_4_10_snap_emit.py
"""
from __future__ import annotations

import os
import sys
import time
from itertools import product

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from polytopes_prismatic import duoprism  # noqa: E402
from search_engine import phi  # noqa: E402
from run_prismatic_sweep import sweep_polytope, get_registry  # noqa: E402


def gen_2d_dirs(rng: int) -> list[np.ndarray]:
    """Generate (a, b, 0, 0) kernels with ZZ[phi] coords bounded by rng."""
    vals = sorted({round(a + b * phi, 9)
                   for a in range(-rng, rng + 1)
                   for b in range(-rng, rng + 1)})
    out = set()
    for n0, n1 in product(vals, repeat=2):
        if n0 == 0 and n1 == 0:
            continue
        # sign canonicalisation: first nonzero positive
        sgn = 1 if n0 > 0 else (-1 if n0 < 0 else (1 if n1 > 0 else -1))
        t = (sgn * n0, sgn * n1, 0.0, 0.0)
        out.add(t)
    return [np.array(v) for v in out]


def main():
    # Locate duoprism_4_10 entry from registry
    entry = None
    for e in get_registry(None):
        if e["slug"] == "duoprism_4_10":
            entry = e
            break
    if entry is None:
        print("ERROR: duoprism_4_10 not in registry", file=sys.stderr)
        sys.exit(1)

    # Redirect output to a probe-specific temp dir so we don't pollute
    # the real corpus.
    import run_prismatic_sweep as rps
    tmpdir = os.path.join(ROOT, "ongoing_work", "probe_4_10_emits")
    os.makedirs(tmpdir, exist_ok=True)
    rps.OUTPUT_ROOT = tmpdir
    rps.FAMILY_DIR = {"A": "", "B": "", "C": ""}

    print(f"=== duoprism_4_10 (a,b,0,0)-plane snap probe ===")
    print(f"emits redirected to: {tmpdir}")
    print()
    print("rng | dirs | _try_align hits | unique shapes | emit | snap_fail | elapsed_s")
    print("----+------+-----------------+---------------+------+-----------+----------")

    for rng in [2, 3, 4, 5, 6, 7]:
        dirs = gen_2d_dirs(rng)
        t0 = time.time()
        rec, _ = sweep_polytope(entry, dirs, rng,
                                emit=True, verbose=False)
        elapsed = time.time() - t0
        hits = rec.get("raw_hits", 0)
        uq = rec.get("unique_shapes", 0)
        emits = rec.get("emitted", [])
        n_emit = sum(1 for e in emits if e.get("status") == "emitted")
        n_fail = sum(1 for e in emits if e.get("status") == "snap_failed")
        print(f" {rng:>2} | {len(dirs):>4} | {hits:>15} | {uq:>13} | {n_emit:>4} | {n_fail:>9} | {elapsed:>8.1f}")

    print()
    print("If duoprism_4_10 is inf-family: emit count grows steadily.")
    print("If bounded (like 4_6): emit count saturates at small constant.")


if __name__ == "__main__":
    main()
