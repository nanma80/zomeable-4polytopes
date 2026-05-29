"""Construct and audit strict zomeable orthographic n-cube generator families.

An n-cube projection to 3D is encoded by its projected coordinate generators
v_1, ..., v_n in Z[phi]^3.  Strict orthographicity is the exact tight-frame
condition

    sum_i v_i v_i^T = c I_3.

This script focuses on inheritance-free split families: all generators are
nonzero, but some parallel generators refine one cube direction.  The known
4-cube infinite family is the first case of this construction.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

spec = importlib.util.spec_from_file_location(
    "col", ROOT / "tools" / "gosset" / "zphi_column_sweep.py"
)
col = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(col)

ZERO: col.ZV = ((0, 0), (0, 0), (0, 0))


def zstr(x: col.Z) -> str:
    a, b = x
    if b == 0:
        return str(a)
    if a == 0:
        return "phi" if b == 1 else f"{b}phi"
    sign = "+" if b > 0 else ""
    coeff = "phi" if abs(b) == 1 else f"{abs(b)}phi"
    if b < 0:
        return f"{a}-{coeff}"
    return f"{a}{sign}{coeff}"


def zsquare(x: col.Z) -> col.Z:
    return col.zmul(x, x)


def zsum_squares(xs: list[col.Z]) -> col.Z:
    out = (0, 0)
    for x in xs:
        out = col.zadd(out, zsquare(x))
    return out


def axis_vec(axis: int, length: col.Z) -> col.ZV:
    vals = [(0, 0), (0, 0), (0, 0)]
    vals[axis] = length
    return tuple(vals)  # type: ignore[return-value]


def gram_sum(gens: list[col.ZV]) -> col.GRAM:
    g = col.ZERO_GRAM
    for v in gens:
        g = col.gram_add(g, col.outer_gram(v))
    return g


def zcross(u: col.ZV, v: col.ZV) -> col.ZV:
    return (
        col.zsub(col.zmul(u[1], v[2]), col.zmul(u[2], v[1])),
        col.zsub(col.zmul(u[2], v[0]), col.zmul(u[0], v[2])),
        col.zsub(col.zmul(u[0], v[1]), col.zmul(u[1], v[0])),
    )


def is_zero(v: col.ZV) -> bool:
    return v == ZERO


def is_parallel(u: col.ZV, v: col.ZV) -> bool:
    return is_zero(zcross(u, v))


def classify_generators(gens: list[col.ZV]) -> str:
    if any(is_zero(v) for v in gens):
        return "inherited"
    for i, u in enumerate(gens):
        for v in gens[i + 1:]:
            if is_parallel(u, v):
                return "reducible/split"
    return "primitive"


def generator_labels(gens: list[col.ZV]) -> list[str]:
    labels = []
    for v in gens:
        parts = []
        for axis, name in enumerate("xyz"):
            if v[axis] != (0, 0):
                parts.append(f"{zstr(v[axis])}{name}")
        labels.append("+".join(parts) if parts else "0")
    return labels


def cube_points(gens: list[col.ZV]) -> np.ndarray:
    rows = []
    for signs in itertools.product((-1, 1), repeat=len(gens)):
        acc = np.zeros(3, dtype=float)
        for s, v in zip(signs, gens):
            acc += s * col.vfloat(v)
        rows.append(acc)
    return np.asarray(rows, dtype=float)


def parallel_class_sizes(gens: list[col.ZV]) -> list[int]:
    classes: list[list[col.ZV]] = []
    for v in gens:
        if is_zero(v):
            continue
        for klass in classes:
            if is_parallel(v, klass[0]):
                klass.append(v)
                break
        else:
            classes.append([v])
    return sorted((len(klass) for klass in classes), reverse=True)


def frame_record(name: str, gens: list[col.ZV], note: str) -> dict:
    g = gram_sum(gens)
    pts = cube_points(gens)
    unique_pts = {tuple(np.round(p, 10)) for p in pts}
    return {
        "name": name,
        "dimension": len(gens),
        "classification": classify_generators(gens),
        "new_vs_previous_dimension": "new" if all(not is_zero(v) for v in gens) else "inherited",
        "note": note,
        "tight_frame": col.gram_is_orthographic(g),
        "frame_scale": zstr((g[0], g[1])),
        "generators": generator_labels(gens),
        "parallel_class_sizes": parallel_class_sizes(gens),
        "unique_projected_vertices": len(unique_pts),
        "shape_sig": col.shape_sig(pts),
    }


PYTHAGOREAN_SAMPLES: list[tuple[str, col.Z, col.Z, col.Z]] = [
    ("sqrt5_branch_1_2", (1, 0), (2, 0), (-1, 2)),  # c = 2phi - 1 = sqrt(5)
    ("integer_3_4_5", (3, 0), (4, 0), (5, 0)),
    ("integer_5_12_13", (5, 0), (12, 0), (13, 0)),
    ("zphi_sqrt5_2_3", (-1, 2), (2, 0), (3, 0)),
]


def split_family_generators(n: int, a: col.Z, b: col.Z, c: col.Z) -> list[col.ZV]:
    if zsum_squares([a, b]) != zsquare(c):
        raise ValueError(f"{zstr(a)}^2 + {zstr(b)}^2 != {zstr(c)}^2")
    if n == 4:
        groups = [[a, b], [c], [c]]
    elif n == 5:
        groups = [[a, b], [a, b], [c]]
    elif n == 6:
        groups = [[a, b], [a, b], [a, b]]
    else:
        raise ValueError("Pythagorean split template is implemented for n=4,5,6")
    return [axis_vec(axis, length) for axis, group in enumerate(groups) for length in group]


def split_family_pattern(n: int) -> tuple[int, int, int]:
    if n == 4:
        return (2, 1, 1)
    if n == 5:
        return (2, 2, 1)
    if n == 6:
        return (2, 2, 2)
    raise ValueError("Pythagorean split template is implemented for n=4,5,6")


def pythagorean_split_records() -> list[dict]:
    records: list[dict] = []
    for n in (4, 5, 6):
        for slug, a, b, c in PYTHAGOREAN_SAMPLES:
            gens = split_family_generators(n, a, b, c)
            records.append(frame_record(
                f"C{n}_{slug}",
                gens,
                (
                    "Axis-parallel split family sample. Varying the Z[phi] "
                    "Pythagorean triple (a,b,c) gives an infinite reducible "
                    f"family with parallel-class pattern {split_family_pattern(n)}."
                ),
            ))
    return records


def positive_square_decompositions(k: int, c: int) -> list[tuple[int, ...]]:
    """Return nondecreasing positive integer k-tuples with sum squares c^2."""
    out: list[tuple[int, ...]] = []

    def rec(start: int, remaining: int, slots: int, acc: list[int]) -> None:
        if remaining < slots * start * start:
            return
        if slots == 0:
            if remaining == 0:
                out.append(tuple(acc))
            return
        max_x = int(math.isqrt(remaining - (slots - 1) * start * start))
        for x in range(start, max_x + 1):
            rest = remaining - x * x
            if rest < (slots - 1) * x * x:
                break
            rec(x, rest, slots - 1, acc + [x])

    rec(1, c * c, k, [])
    return out


def partition3(n: int) -> list[tuple[int, int, int]]:
    parts = []
    for a in range(1, n - 1):
        for b in range(a, n - a):
            c = n - a - b
            if b <= c:
                parts.append((a, b, c))
    return parts


def integer_split_witnesses(max_n: int, max_c: int) -> list[dict]:
    """Find one axis-split tight-frame witness for each n using integer lengths."""
    decomp_cache: dict[tuple[int, int], list[tuple[int, ...]]] = {}

    def decomps(k: int, c: int) -> list[tuple[int, ...]]:
        key = (k, c)
        if key not in decomp_cache:
            decomp_cache[key] = positive_square_decompositions(k, c)
        return decomp_cache[key]

    records = []
    for n in range(3, max_n + 1):
        if n == 3:
            gens = [axis_vec(0, (1, 0)), axis_vec(1, (1, 0)), axis_vec(2, (1, 0))]
            records.append(frame_record("C3_ordinary_cube", gens, "The strict 3-cube baseline."))
            continue
        found = None
        for c in range(1, max_c + 1):
            for sizes in partition3(n):
                ds = [decomps(k, c) for k in sizes]
                if all(ds):
                    found = (c, sizes, [d[0] for d in ds])
                    break
            if found:
                break
        if not found:
            records.append({
                "name": f"C{n}_no_integer_split_witness",
                "dimension": n,
                "status": "not_found",
                "max_c": max_c,
                "note": "No axis-parallel positive integer split witness found within this bound.",
            })
            continue
        c, sizes, decomps3 = found
        gens = [
            axis_vec(axis, (length, 0))
            for axis, group in enumerate(decomps3)
            for length in group
        ]
        records.append(frame_record(
            f"C{n}_integer_split_{'_'.join(map(str, sizes))}_c{c}",
            gens,
            (
                f"Integer axis-split witness with class sizes {sizes}; each "
                f"class has squared-length sum {c}^2. This is a constructive "
                "sample, not a completeness claim."
            ),
        ))
    return records


def build_report(max_n: int, max_c: int) -> dict:
    return {
        "description": (
            "Strict zomeable orthographic n-cube generator-family report. "
            "Records marked new have no zero generator, so they are not inherited "
            "from the previous cube by appending a zero generator."
        ),
        "conventions": {
            "strict_orthographic_test": "sum_i v_i v_i^T = c I_3 over Z[phi]",
            "inherited": "at least one generator is zero",
            "reducible_split": "no zero generator, but at least two generators are parallel",
            "primitive": "no zero generator and no parallel generator pair",
        },
        "known_new_n4_context": {
            "inherited_from_C3": "ordinary cube / 8cell_cell_first_cube.vZome",
            "new_vzome_strict_types": [
                "8-cell infinite split family",
                "phi-oblique sporadic",
                "rhombic dodecahedron sporadic",
            ],
            "source": "output/regular/8cell/CLASSIFICATION.md",
        },
        "pythagorean_split_infinite_family_samples_n4_to_n6": pythagorean_split_records(),
        "bounded_integer_split_witnesses": integer_split_witnesses(max_n, max_c),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max_n", type=int, default=10)
    ap.add_argument("--max_c", type=int, default=50)
    ap.add_argument("--out", default="ongoing_work/ncube/ncube_split_family_report.json")
    args = ap.parse_args()

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(args.max_n, args.max_c)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "out": str(out.relative_to(ROOT)),
        "pythagorean_records": len(report["pythagorean_split_infinite_family_samples_n4_to_n6"]),
        "integer_witnesses": len(report["bounded_integer_split_witnesses"]),
    }, indent=2))


if __name__ == "__main__":
    main()
