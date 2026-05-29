"""Exact bounded strict-zomeable n-cube generator sweeps.

For an n-cube projected to 3D, let g_i be the projected coordinate
generators.  Strict orthographicity is exactly the tight-frame condition

    sum_i g_i g_i^T = c I_3.

The n=4 sweep is a pair+pair match.  The n=5 sweep is a pair+triple
match.  The n=6 and n=7 sweeps are strict/general-position searches using
triple+triple and triple+quad matches respectively, still using exact Z[phi]
Gram arithmetic.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

col_spec = importlib.util.spec_from_file_location(
    "zphi_column_sweep", ROOT / "tools" / "gosset" / "zphi_column_sweep.py"
)
col = importlib.util.module_from_spec(col_spec)
assert col_spec.loader is not None
col_spec.loader.exec_module(col)

fam_spec = importlib.util.spec_from_file_location(
    "zphi_ncube_families", ROOT / "tools" / "ncube" / "zphi_ncube_families.py"
)
fam = importlib.util.module_from_spec(fam_spec)
assert fam_spec.loader is not None
fam_spec.loader.exec_module(fam)

ZERO: col.ZV = ((0, 0), (0, 0), (0, 0))
OUT = ROOT / "ongoing_work" / "ncube"


def canonical_unoriented(v: col.ZV) -> col.ZV:
    return min(v, col.vscale_int(-1, v))


def anisotropy_key(g: col.GRAM) -> tuple[col.Z, col.Z, col.Z, col.Z, col.Z]:
    """Return the five exact values that must cancel for a pair-pair frame."""
    xx = g[0:2]
    yy = g[2:4]
    zz = g[4:6]
    return (
        col.zsub(xx, yy),
        col.zsub(xx, zz),
        g[6:8],
        g[8:10],
        g[10:12],
    )


def neg_key(key: tuple[col.Z, ...]) -> tuple[col.Z, ...]:
    return tuple(col.zneg(x) for x in key)


def z_to_json(x: col.Z) -> list[int]:
    return [x[0], x[1]]


def zv_to_json(v: col.ZV) -> list[list[int]]:
    return [z_to_json(x) for x in v]


def gram_scale(g: col.GRAM) -> col.Z:
    return (g[0], g[1])


def zcross(u: col.ZV, v: col.ZV) -> col.ZV:
    return (
        col.zsub(col.zmul(u[1], v[2]), col.zmul(u[2], v[1])),
        col.zsub(col.zmul(u[2], v[0]), col.zmul(u[0], v[2])),
        col.zsub(col.zmul(u[0], v[1]), col.zmul(u[1], v[0])),
    )


def is_parallel(u: col.ZV, v: col.ZV) -> bool:
    return zcross(u, v) == ZERO


def zdot(u: col.ZV, v: col.ZV) -> col.Z:
    out = (0, 0)
    for a, b in zip(u, v):
        out = col.zadd(out, col.zmul(a, b))
    return out


def zdet(u: col.ZV, v: col.ZV, w: col.ZV) -> col.Z:
    return zdot(zcross(u, v), w)


def nonspanning_triples(gens: list[col.ZV]) -> list[list[int]]:
    failures = []
    for triple in itertools.combinations(range(len(gens)), 3):
        i, j, k = triple
        if zdet(gens[i], gens[j], gens[k]) == (0, 0):
            failures.append([i, j, k])
    return failures


def is_essential_general_position(gens: list[col.ZV]) -> bool:
    return not nonspanning_triples(gens)


def is_spanning_triple_indices(candidates: list[col.ZV], i: int, j: int, k: int) -> bool:
    return zdet(candidates[i], candidates[j], candidates[k]) != (0, 0)


def classify_generators(gens: list[col.ZV]) -> str:
    if any(g == ZERO for g in gens):
        return "inherited"
    for i, u in enumerate(gens):
        for v in gens[i + 1:]:
            if is_parallel(u, v):
                return "reducible/split"
    return "primitive"


def parallel_class_sizes(gens: list[col.ZV]) -> list[int]:
    classes: list[list[col.ZV]] = []
    for g in gens:
        if g == ZERO:
            continue
        for klass in classes:
            if is_parallel(g, klass[0]):
                klass.append(g)
                break
        else:
            classes.append([g])
    return sorted((len(klass) for klass in classes), reverse=True)


def cube_points(gens: list[col.ZV]) -> np.ndarray:
    pts = []
    for signs in itertools.product((-1, 1), repeat=len(gens)):
        acc = np.zeros(3, dtype=float)
        for sign, gen in zip(signs, gens):
            acc += sign * col.vfloat(gen)
        pts.append(acc)
    return np.asarray(pts, dtype=float)


def collapsed_edge_count(gens: list[col.ZV]) -> int:
    sign_to_raw: dict[tuple[int, ...], int] = {}
    raw = []
    for signs in itertools.product((-1, 1), repeat=len(gens)):
        acc = tuple(np.round(sum(sign * col.vfloat(gen)[axis] for sign, gen in zip(signs, gens)), 12)
                    for axis in range(3))
        sign_to_raw[signs] = len(raw)
        raw.append(acc)

    point_index: dict[tuple[float, float, float], int] = {}
    raw_to_unique = []
    for p in raw:
        if p not in point_index:
            point_index[p] = len(point_index)
        raw_to_unique.append(point_index[p])

    edges = set()
    for signs, raw_i in sign_to_raw.items():
        for axis in range(len(gens)):
            flipped = list(signs)
            flipped[axis] *= -1
            raw_j = sign_to_raw[tuple(flipped)]
            a = raw_to_unique[raw_i]
            b = raw_to_unique[raw_j]
            if a != b:
                edges.add((min(a, b), max(a, b)))
    return len(edges)


def taxonomy_label(n: int, unique_vertices: int, classification: str, pcs: list[int]) -> str:
    if n == 5:
        if unique_vertices == 1:
            return "all_collapsed_ignore"
        if classification == "inherited":
            return "inherited_from_n4"
        if classification == "reducible/split" and pcs == [2, 2, 1]:
            return "split_2_2_1_infinite_family_sample"
        if classification == "reducible/split":
            return "other_reducible_split"
        if classification == "primitive":
            return "primitive_candidate"
        return "unlabeled"

    if n >= 6:
        if classification == "primitive":
            return "essential_candidate"
        if classification == "inherited":
            return f"inherited_from_n{n - 1}"
        if classification == "reducible/split":
            return "reducible_split"
        return "unlabeled"

    if unique_vertices == 1:
        return "all_collapsed_ignore"
    if classification == "inherited" and unique_vertices == 8:
        return "inherited_cube"
    if classification == "primitive" and unique_vertices == 15:
        return "vertex_first_rhombic_dodecahedron"
    if classification == "primitive" and unique_vertices == 16:
        return "phi_oblique"
    if classification == "reducible/split" and unique_vertices == 16 and pcs == [2, 1, 1]:
        return "split_infinite_family_sample"
    if classification == "reducible/split" and unique_vertices == 12:
        return "degenerate_face_first_split"
    if classification == "primitive" and unique_vertices == 14:
        return "axis_aligned_edge_first_hex_prism"
    return "unlabeled"


def frame_record(
    n: int,
    sig: str,
    gens: list[col.ZV],
    gram: col.GRAM,
    example_count: int,
) -> dict:
    pts = cube_points(gens)
    unique_vertices = len({tuple(np.round(p, 10)) for p in pts})
    classification = classify_generators(gens)
    pcs = parallel_class_sizes(gens)
    failures = nonspanning_triples(gens)
    return {
        "shape_sig": sig,
        "taxonomy_label": taxonomy_label(n, unique_vertices, classification, pcs),
        "classification": classification,
        "essential_general_position": not failures,
        "nonspanning_triples": failures,
        "new_vs_previous_dimension": "inherited" if any(g == ZERO for g in gens) else "new",
        "unique_projected_vertices": unique_vertices,
        "collapsed_edge_count": collapsed_edge_count(gens),
        "parallel_class_sizes": pcs,
        "frame_scale": fam.zstr(gram_scale(gram)),
        "frame_scale_zphi": z_to_json(gram_scale(gram)),
        "generators": fam.generator_labels(gens),
        "generators_zphi": [zv_to_json(g) for g in gens],
        "example_count_for_signature": example_count,
    }


def progress_path(n: int, R: int) -> Path:
    return OUT / f"column_sweep_ncube{n}_R{R}.progress.json"


def result_path(n: int, R: int) -> Path:
    return OUT / f"column_sweep_ncube{n}_R{R}.json"


def write_progress(n: int, R: int, payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    progress_path(n, R).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def sweep_n4(R: int) -> dict:
    t0 = time.time()
    zero = [ZERO]
    candidates = zero + sorted({canonical_unoriented(v) for v in col.axis_set(R) if v != ZERO})
    grams = [col.outer_gram(v) for v in candidates]

    write_progress(4, R, {
        "phase": "pair_grouping",
        "n": 4,
        "R": R,
        "candidate_count": len(candidates),
        "elapsed_sec": round(time.time() - t0, 3),
    })

    pairs: list[tuple[int, int, col.GRAM]] = []
    groups: dict[tuple[col.Z, ...], list[int]] = defaultdict(list)
    for i in range(len(candidates)):
        for j in range(i, len(candidates)):
            g = col.gram_add(grams[i], grams[j])
            groups[anisotropy_key(g)].append(len(pairs))
            pairs.append((i, j, g))

    write_progress(4, R, {
        "phase": "pair_matching",
        "n": 4,
        "R": R,
        "candidate_count": len(candidates),
        "pair_count": len(pairs),
        "anisotropy_group_count": len(groups),
        "elapsed_sec": round(time.time() - t0, 3),
    })

    seen_indices: set[tuple[int, int, int, int]] = set()
    signature_examples: dict[str, tuple[list[col.ZV], col.GRAM, bool]] = {}
    signature_counts: Counter[str] = Counter()
    signature_essential_counts: Counter[str] = Counter()
    exact_frame_count = 0

    for key, pair_ids in groups.items():
        complement_ids = groups.get(neg_key(key), [])
        if not complement_ids:
            continue
        for pid in pair_ids:
            i, j, g1 = pairs[pid]
            for qid in complement_ids:
                if qid < pid:
                    continue
                k, l, g2 = pairs[qid]
                idx = tuple(sorted((i, j, k, l)))
                if idx in seen_indices:
                    continue
                seen_indices.add(idx)
                gram = col.gram_add(g1, g2)
                if not col.gram_is_orthographic(gram):
                    continue
                exact_frame_count += 1
                gens = [candidates[x] for x in idx]
                pts = cube_points(gens)
                sig = col.shape_sig(pts)
                essential = is_essential_general_position(gens)
                signature_counts[sig] += 1
                if essential:
                    signature_essential_counts[sig] += 1
                if sig not in signature_examples or (essential and not signature_examples[sig][2]):
                    signature_examples[sig] = (gens, gram, essential)

    records = [
        {
            **frame_record(4, sig, gens, gram, signature_counts[sig]),
            "essential_example_count_for_signature": signature_essential_counts[sig],
        }
        for sig, (gens, gram, _essential) in signature_examples.items()
    ]
    records.sort(key=lambda r: (
        r["taxonomy_label"] == "all_collapsed_ignore",
        r["new_vs_previous_dimension"],
        r["classification"],
        r["unique_projected_vertices"],
        r["shape_sig"],
    ))

    labels = {r["taxonomy_label"] for r in records}
    essential_labels = {r["taxonomy_label"] for r in records if r["essential_general_position"]}
    expected_core = {
        "vertex_first_rhombic_dodecahedron",
    }
    elapsed = time.time() - t0
    return {
        "sweep": "ncube4_exact_generator_pair_sweep",
        "n": 4,
        "R": R,
        "candidate_count": len(candidates),
        "pair_count": len(pairs),
        "anisotropy_group_count": len(groups),
        "candidate_pair_pair_count": len(seen_indices),
        "exact_frame_count": exact_frame_count,
        "distinct_shape_count": len(records),
        "essential_shape_count": sum(1 for r in records if r["essential_general_position"]),
        "elapsed_sec": round(elapsed, 3),
        "expected_core_taxonomy": sorted(expected_core),
        "expected_core_covered": sorted(expected_core & essential_labels),
        "expected_core_missing": sorted(expected_core - essential_labels),
        "records": records,
    }


def sweep_n5(R: int) -> dict:
    t0 = time.time()
    candidates = [ZERO] + sorted({canonical_unoriented(v) for v in col.axis_set(R) if v != ZERO})
    grams = [col.outer_gram(v) for v in candidates]

    write_progress(5, R, {
        "phase": "pair_grouping",
        "n": 5,
        "R": R,
        "candidate_count": len(candidates),
        "elapsed_sec": round(time.time() - t0, 3),
    })

    pairs: list[tuple[int, int, col.GRAM]] = []
    pair_groups: dict[tuple[col.Z, ...], list[int]] = defaultdict(list)
    needed_triple_keys: set[tuple[col.Z, ...]] = set()
    for i in range(len(candidates)):
        for j in range(i, len(candidates)):
            g = col.gram_add(grams[i], grams[j])
            key = anisotropy_key(g)
            pair_groups[key].append(len(pairs))
            needed_triple_keys.add(neg_key(key))
            pairs.append((i, j, g))

    write_progress(5, R, {
        "phase": "triple_grouping",
        "n": 5,
        "R": R,
        "candidate_count": len(candidates),
        "pair_count": len(pairs),
        "pair_anisotropy_group_count": len(pair_groups),
        "elapsed_sec": round(time.time() - t0, 3),
    })

    triples: list[tuple[int, int, int, col.GRAM]] = []
    triple_groups: dict[tuple[col.Z, ...], list[int]] = defaultdict(list)
    triple_count = 0
    last_progress = time.time()
    for i in range(len(candidates)):
        gi = grams[i]
        for j in range(i, len(candidates)):
            gij = col.gram_add(gi, grams[j])
            for k in range(j, len(candidates)):
                triple_count += 1
                g = col.gram_add(gij, grams[k])
                key = anisotropy_key(g)
                if key in needed_triple_keys:
                    triple_groups[key].append(len(triples))
                    triples.append((i, j, k, g))
        now = time.time()
        if now - last_progress > 10:
            last_progress = now
            write_progress(5, R, {
                "phase": "triple_grouping",
                "n": 5,
                "R": R,
                "candidate_count": len(candidates),
                "triple_i": i,
                "triple_i_total": len(candidates),
                "triple_count_so_far": triple_count,
                "matching_triples_so_far": len(triples),
                "elapsed_sec": round(now - t0, 3),
            })

    write_progress(5, R, {
        "phase": "pair_triple_matching",
        "n": 5,
        "R": R,
        "candidate_count": len(candidates),
        "pair_count": len(pairs),
        "triple_count": triple_count,
        "matching_triple_count": len(triples),
        "triple_anisotropy_group_count": len(triple_groups),
        "elapsed_sec": round(time.time() - t0, 3),
    })

    seen_indices: set[tuple[int, int, int, int, int]] = set()
    signature_examples: dict[str, tuple[list[col.ZV], col.GRAM, bool]] = {}
    signature_counts: Counter[str] = Counter()
    signature_essential_counts: Counter[str] = Counter()
    exact_frame_count = 0

    for key, pair_ids in pair_groups.items():
        complement_ids = triple_groups.get(neg_key(key), [])
        if not complement_ids:
            continue
        for pid in pair_ids:
            i, j, g1 = pairs[pid]
            for tid in complement_ids:
                k, l, m, g2 = triples[tid]
                idx = tuple(sorted((i, j, k, l, m)))
                if idx in seen_indices:
                    continue
                seen_indices.add(idx)
                gram = col.gram_add(g1, g2)
                if not col.gram_is_orthographic(gram):
                    continue
                exact_frame_count += 1
                gens = [candidates[x] for x in idx]
                pts = cube_points(gens)
                sig = col.shape_sig(pts)
                essential = is_essential_general_position(gens)
                signature_counts[sig] += 1
                if essential:
                    signature_essential_counts[sig] += 1
                if sig not in signature_examples or (essential and not signature_examples[sig][2]):
                    signature_examples[sig] = (gens, gram, essential)

    records = [
        {
            **frame_record(5, sig, gens, gram, signature_counts[sig]),
            "essential_example_count_for_signature": signature_essential_counts[sig],
        }
        for sig, (gens, gram, _essential) in signature_examples.items()
    ]
    records.sort(key=lambda r: (
        r["taxonomy_label"] == "all_collapsed_ignore",
        r["new_vs_previous_dimension"],
        r["classification"],
        r["unique_projected_vertices"],
        r["shape_sig"],
    ))

    essential_labels = {r["taxonomy_label"] for r in records if r["essential_general_position"]}
    expected_core: set[str] = set()
    elapsed = time.time() - t0
    return {
        "sweep": "ncube5_exact_generator_pair_triple_sweep",
        "n": 5,
        "R": R,
        "candidate_count": len(candidates),
        "pair_count": len(pairs),
        "triple_count": triple_count,
        "matching_triple_count": len(triples),
        "pair_anisotropy_group_count": len(pair_groups),
        "triple_anisotropy_group_count": len(triple_groups),
        "candidate_pair_triple_count": len(seen_indices),
        "exact_frame_count": exact_frame_count,
        "distinct_shape_count": len(records),
        "essential_shape_count": sum(1 for r in records if r["essential_general_position"]),
        "new_shape_count": sum(1 for r in records if r["new_vs_previous_dimension"] == "new"),
        "essential_new_shape_count": sum(
            1 for r in records
            if r["essential_general_position"] and r["new_vs_previous_dimension"] == "new"
        ),
        "elapsed_sec": round(elapsed, 3),
        "expected_core_taxonomy": sorted(expected_core),
        "expected_core_covered": sorted(expected_core & essential_labels),
        "expected_core_missing": sorted(expected_core - essential_labels),
        "records": records,
    }


def strict_candidates(R: int) -> tuple[list[col.ZV], list[col.GRAM]]:
    candidates = sorted({canonical_unoriented(v) for v in col.axis_set(R) if v != ZERO})
    grams = [col.outer_gram(v) for v in candidates]
    return candidates, grams


def record_strict_frame(
    n: int,
    gens: list[col.ZV],
    gram: col.GRAM,
    signature_examples: dict[str, tuple[list[col.ZV], col.GRAM]],
    signature_counts: Counter[str],
) -> None:
    if not is_essential_general_position(gens):
        return
    pts = cube_points(gens)
    sig = col.shape_sig(pts)
    signature_counts[sig] += 1
    signature_examples.setdefault(sig, (gens, gram))


def strict_records(
    n: int,
    signature_examples: dict[str, tuple[list[col.ZV], col.GRAM]],
    signature_counts: Counter[str],
) -> list[dict]:
    records = [
        {
            **frame_record(n, sig, gens, gram, signature_counts[sig]),
            "essential_example_count_for_signature": signature_counts[sig],
        }
        for sig, (gens, gram) in signature_examples.items()
    ]
    records.sort(key=lambda r: (
        r["unique_projected_vertices"],
        r["shape_sig"],
    ))
    return records


def sweep_n6_strict(R: int) -> dict:
    t0 = time.time()
    candidates, grams = strict_candidates(R)
    triple_total_estimate = len(candidates) * (len(candidates) - 1) * (len(candidates) - 2) // 6

    write_progress(6, R, {
        "phase": "strict_triple_grouping",
        "n": 6,
        "R": R,
        "candidate_count": len(candidates),
        "triple_total_estimate": triple_total_estimate,
        "elapsed_sec": round(time.time() - t0, 3),
    })

    triples: list[tuple[int, int, int, col.GRAM]] = []
    triple_groups: dict[tuple[col.Z, ...], list[int]] = defaultdict(list)
    triple_count = 0
    strict_triple_count = 0
    last_progress = time.time()
    for i in range(len(candidates)):
        gi = grams[i]
        for j in range(i + 1, len(candidates)):
            gij = col.gram_add(gi, grams[j])
            for k in range(j + 1, len(candidates)):
                triple_count += 1
                if not is_spanning_triple_indices(candidates, i, j, k):
                    continue
                strict_triple_count += 1
                g = col.gram_add(gij, grams[k])
                key = anisotropy_key(g)
                triple_groups[key].append(len(triples))
                triples.append((i, j, k, g))
        now = time.time()
        if now - last_progress > 10:
            last_progress = now
            write_progress(6, R, {
                "phase": "strict_triple_grouping",
                "n": 6,
                "R": R,
                "candidate_count": len(candidates),
                "triple_i": i,
                "triple_i_total": len(candidates),
                "triple_count_so_far": triple_count,
                "strict_triple_count_so_far": strict_triple_count,
                "elapsed_sec": round(now - t0, 3),
            })

    write_progress(6, R, {
        "phase": "strict_triple_matching",
        "n": 6,
        "R": R,
        "candidate_count": len(candidates),
        "triple_count": triple_count,
        "strict_triple_count": strict_triple_count,
        "triple_anisotropy_group_count": len(triple_groups),
        "elapsed_sec": round(time.time() - t0, 3),
    })

    seen_indices: set[tuple[int, ...]] = set()
    signature_examples: dict[str, tuple[list[col.ZV], col.GRAM]] = {}
    signature_counts: Counter[str] = Counter()
    exact_frame_count = 0
    candidate_triple_triple_count = 0

    for key, triple_ids in triple_groups.items():
        complement = neg_key(key)
        if complement not in triple_groups or complement < key:
            continue
        complement_ids = triple_groups[complement]
        for pid in triple_ids:
            i, j, k, g1 = triples[pid]
            ids1 = {i, j, k}
            for qid in complement_ids:
                if complement == key and qid < pid:
                    continue
                a, b, c, g2 = triples[qid]
                if ids1 & {a, b, c}:
                    continue
                idx = tuple(sorted((i, j, k, a, b, c)))
                if idx in seen_indices:
                    continue
                seen_indices.add(idx)
                candidate_triple_triple_count += 1
                gens = [candidates[x] for x in idx]
                if not is_essential_general_position(gens):
                    continue
                gram = col.gram_add(g1, g2)
                if not col.gram_is_orthographic(gram):
                    continue
                exact_frame_count += 1
                record_strict_frame(6, gens, gram, signature_examples, signature_counts)

    records = strict_records(6, signature_examples, signature_counts)
    elapsed = time.time() - t0
    return {
        "sweep": "ncube6_strict_generator_triple_triple_sweep",
        "n": 6,
        "R": R,
        "candidate_count": len(candidates),
        "triple_count": triple_count,
        "strict_triple_count": strict_triple_count,
        "triple_anisotropy_group_count": len(triple_groups),
        "candidate_triple_triple_count": candidate_triple_triple_count,
        "exact_frame_count": exact_frame_count,
        "distinct_shape_count": len(records),
        "essential_shape_count": len(records),
        "new_shape_count": len(records),
        "essential_new_shape_count": len(records),
        "elapsed_sec": round(elapsed, 3),
        "expected_core_taxonomy": [],
        "expected_core_covered": [],
        "expected_core_missing": [],
        "records": records,
    }


def sweep_n7_strict(R: int) -> dict:
    t0 = time.time()
    candidates, grams = strict_candidates(R)
    triple_total_estimate = len(candidates) * (len(candidates) - 1) * (len(candidates) - 2) // 6
    quad_total_estimate = (
        len(candidates) * (len(candidates) - 1) * (len(candidates) - 2) * (len(candidates) - 3) // 24
    )

    write_progress(7, R, {
        "phase": "strict_triple_grouping",
        "n": 7,
        "R": R,
        "candidate_count": len(candidates),
        "triple_total_estimate": triple_total_estimate,
        "quad_total_estimate": quad_total_estimate,
        "elapsed_sec": round(time.time() - t0, 3),
    })

    triples: list[tuple[int, int, int, col.GRAM]] = []
    triple_groups: dict[tuple[col.Z, ...], list[int]] = defaultdict(list)
    triple_count = 0
    strict_triple_count = 0
    for i in range(len(candidates)):
        gi = grams[i]
        for j in range(i + 1, len(candidates)):
            gij = col.gram_add(gi, grams[j])
            for k in range(j + 1, len(candidates)):
                triple_count += 1
                if not is_spanning_triple_indices(candidates, i, j, k):
                    continue
                strict_triple_count += 1
                g = col.gram_add(gij, grams[k])
                key = anisotropy_key(g)
                triple_groups[key].append(len(triples))
                triples.append((i, j, k, g))

    needed_quad_keys = {neg_key(key) for key in triple_groups}
    write_progress(7, R, {
        "phase": "strict_quad_streaming",
        "n": 7,
        "R": R,
        "candidate_count": len(candidates),
        "triple_count": triple_count,
        "strict_triple_count": strict_triple_count,
        "triple_anisotropy_group_count": len(triple_groups),
        "elapsed_sec": round(time.time() - t0, 3),
    })

    seen_indices: set[tuple[int, ...]] = set()
    signature_examples: dict[str, tuple[list[col.ZV], col.GRAM]] = {}
    signature_counts: Counter[str] = Counter()
    quad_count = 0
    strict_quad_count = 0
    matching_quad_count = 0
    candidate_triple_quad_count = 0
    exact_frame_count = 0
    last_progress = time.time()

    for i in range(len(candidates)):
        gi = grams[i]
        for j in range(i + 1, len(candidates)):
            gij = col.gram_add(gi, grams[j])
            for k in range(j + 1, len(candidates)):
                if not is_spanning_triple_indices(candidates, i, j, k):
                    quad_count += len(candidates) - (k + 1)
                    continue
                gijk = col.gram_add(gij, grams[k])
                for l in range(k + 1, len(candidates)):
                    quad_count += 1
                    if (
                        not is_spanning_triple_indices(candidates, i, j, l)
                        or not is_spanning_triple_indices(candidates, i, k, l)
                        or not is_spanning_triple_indices(candidates, j, k, l)
                    ):
                        continue
                    strict_quad_count += 1
                    gq = col.gram_add(gijk, grams[l])
                    key = anisotropy_key(gq)
                    if key not in needed_quad_keys:
                        continue
                    matching_quad_count += 1
                    for tid in triple_groups[neg_key(key)]:
                        a, b, c, gt = triples[tid]
                        if {i, j, k, l} & {a, b, c}:
                            continue
                        idx = tuple(sorted((i, j, k, l, a, b, c)))
                        if idx in seen_indices:
                            continue
                        seen_indices.add(idx)
                        candidate_triple_quad_count += 1
                        gens = [candidates[x] for x in idx]
                        if not is_essential_general_position(gens):
                            continue
                        gram = col.gram_add(gq, gt)
                        if not col.gram_is_orthographic(gram):
                            continue
                        exact_frame_count += 1
                        record_strict_frame(7, gens, gram, signature_examples, signature_counts)
        now = time.time()
        if now - last_progress > 10:
            last_progress = now
            write_progress(7, R, {
                "phase": "strict_quad_streaming",
                "n": 7,
                "R": R,
                "candidate_count": len(candidates),
                "quad_i": i,
                "quad_i_total": len(candidates),
                "quad_count_so_far": quad_count,
                "strict_quad_count_so_far": strict_quad_count,
                "matching_quad_count_so_far": matching_quad_count,
                "candidate_triple_quad_count_so_far": candidate_triple_quad_count,
                "exact_frame_count_so_far": exact_frame_count,
                "distinct_shape_count_so_far": len(signature_examples),
                "elapsed_sec": round(now - t0, 3),
            })

    records = strict_records(7, signature_examples, signature_counts)
    elapsed = time.time() - t0
    return {
        "sweep": "ncube7_strict_generator_triple_quad_sweep",
        "n": 7,
        "R": R,
        "candidate_count": len(candidates),
        "triple_count": triple_count,
        "strict_triple_count": strict_triple_count,
        "quad_count": quad_count,
        "strict_quad_count": strict_quad_count,
        "matching_quad_count": matching_quad_count,
        "triple_anisotropy_group_count": len(triple_groups),
        "candidate_triple_quad_count": candidate_triple_quad_count,
        "exact_frame_count": exact_frame_count,
        "distinct_shape_count": len(records),
        "essential_shape_count": len(records),
        "new_shape_count": len(records),
        "essential_new_shape_count": len(records),
        "elapsed_sec": round(elapsed, 3),
        "expected_core_taxonomy": [],
        "expected_core_covered": [],
        "expected_core_missing": [],
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, choices=(4, 5, 6, 7), default=4, help="cube dimension to sweep")
    parser.add_argument("--R", type=int, default=3, help="Z[phi] coefficient radius for generator candidates")
    args = parser.parse_args()

    if args.n == 4:
        result = sweep_n4(args.R)
    elif args.n == 5:
        result = sweep_n5(args.R)
    elif args.n == 6:
        result = sweep_n6_strict(args.R)
    else:
        result = sweep_n7_strict(args.R)
    OUT.mkdir(parents=True, exist_ok=True)
    result_path(args.n, args.R).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    write_progress(args.n, args.R, {
        "phase": "complete",
        "n": args.n,
        "R": args.R,
        "distinct_shape_count": result["distinct_shape_count"],
        "essential_shape_count": result["essential_shape_count"],
        "exact_frame_count": result["exact_frame_count"],
        "expected_core_missing": result["expected_core_missing"],
        "elapsed_sec": result["elapsed_sec"],
    })
    print(json.dumps({
        "R": result["R"],
        "distinct_shape_count": result["distinct_shape_count"],
        "essential_shape_count": result["essential_shape_count"],
        "exact_frame_count": result["exact_frame_count"],
        "expected_core_missing": result["expected_core_missing"],
        "output": str(result_path(args.n, args.R)),
    }, indent=2))


if __name__ == "__main__":
    main()
