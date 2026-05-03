"""Shape-fingerprint audit.

Re-runs every polytope at its established rng and checks whether the
distance-multiset fingerprint (used by group_by_shape) ever merges
shapes that have *different strut-color signatures*. If two hits share
the same distance fingerprint but differ in sig, group_by_shape may have
incorrectly merged genuinely distinct shapes.

For each polytope embedding:
 1. Run search.
 2. Group hits by the existing fingerprint.
 3. Within each group, collect the set of distinct strut-color sigs.
 4. Flag any group that contains >1 distinct sig.
 5. Also re-dedupe with augmented key (existing_fp, frozen_sig) and
    report whether the count of distinct shapes changes.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from polytopes import POLYTOPES
from search_engine import gen_dirs, search, shape_fingerprint
import numpy as np


def freeze_sig(sig):
    return tuple(sorted(sig.items()))


# (name, rng) - rng matches what's documented in each RESULTS.md
TARGETS = [
    ("5cell", 3),
    ("16cell", 3),
    ("8cell", 3),
    ("24cell", 3),
    ("120cell", 4),
    ("600cell", 4),
    ("snub24cell", 4),
    ("grand_antiprism", 4),
]

problems = []
print(f"{'polytope':30s} {'embed':20s} {'hits':>5s} {'old':>4s} {'new':>4s}  status")
print("-" * 80)

for name, rng in TARGETS:
    if name not in POLYTOPES:
        print(f"  SKIP: {name} not in POLYTOPES")
        continue
    embeddings = POLYTOPES[name]
    dirs = gen_dirs(rng=rng, integer_only=False)
    for label, fn in embeddings:
        V, E = fn()
        hits = search(label, V, E, dirs, verbose=False)
        # Group by old fp
        old_groups = {}
        for n, sig, balls in hits:
            fp = shape_fingerprint(V, E, np.array(n))
            old_groups.setdefault(fp, []).append((n, sig, balls))
        # Augmented fp
        new_groups = {}
        for n, sig, balls in hits:
            fp = shape_fingerprint(V, E, np.array(n))
            key = (fp, freeze_sig(sig))
            new_groups.setdefault(key, []).append((n, sig, balls))
        # Check for fp groups with multiple sigs
        bad = 0
        for fp, ex in old_groups.items():
            sigs = set(freeze_sig(e[1]) for e in ex)
            if len(sigs) > 1:
                bad += 1
                problems.append((name, label, fp, sigs))
        status = "OK" if bad == 0 and len(old_groups) == len(new_groups) else f"DIFF ({bad} mixed-sig groups)"
        print(f"{name:30s} {label:20s} {len(hits):5d} {len(old_groups):4d} {len(new_groups):4d}  {status}")

print()
if not problems:
    print("CONCLUSION: no fingerprint collisions detected. group_by_shape is consistent with strut-color signature.")
else:
    print(f"WARNING: {len(problems)} fingerprint groups had multiple strut-color sigs:")
    for name, label, fp, sigs in problems:
        print(f"  {name}/{label}: fp_n_balls={fp[0]}  sigs={sigs}")
