"""Shared A5 (5-simplex) uniform-family data.

The 19 A5 uniform 5-polytopes are the nonempty Wythoff ringed-node subsets of
the A5 Coxeter diagram, modulo the diagram reversal i -> 6-i.  For a subset S
of nodes {1, ..., 5}, the seed vertex is the 6-tuple whose consecutive
differences are 1 exactly at the nodes in S.  The full vertex set is the S6
orbit of that seed tuple.

Edges of these orbit polytopes are obtained by swapping two coordinates whose
values differ by exactly one; these are the Wythoff edge orbits and all have A5
root directions.
"""
from __future__ import annotations

import itertools
import math
from functools import lru_cache

import numpy as np


def reverse_nodes(nodes: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(6 - i for i in nodes))


def canonical_nodes(nodes: tuple[int, ...]) -> tuple[int, ...]:
    nodes = tuple(sorted(nodes))
    return min(nodes, reverse_nodes(nodes))


def all_node_sets() -> list[tuple[int, ...]]:
    out = []
    for r in range(1, 6):
        for nodes in itertools.combinations(range(1, 6), r):
            if nodes == canonical_nodes(nodes):
                out.append(nodes)
    assert len(out) == 19
    return out


def slug_for_nodes(nodes: tuple[int, ...]) -> str:
    nodes = canonical_nodes(nodes)
    special = {
        (1,): "5_simplex",
        (2,): "rectified_5_simplex",
        (3,): "birectified_5_simplex",
    }
    return special.get(nodes, "a5_t" + "".join(str(i) for i in nodes))


def display_for_nodes(nodes: tuple[int, ...]) -> str:
    nodes = canonical_nodes(nodes)
    special = {
        (1,): "5-simplex (hexateron)",
        (2,): "Rectified 5-simplex",
        (3,): "Birectified 5-simplex",
    }
    if nodes in special:
        return special[nodes]
    return "A5 Wythoff t{" + ",".join(str(i) for i in nodes) + "}"


def base_values(nodes: tuple[int, ...]) -> tuple[int, ...]:
    nodes = canonical_nodes(nodes)
    diffs = [1 if i in nodes else 0 for i in range(1, 6)]
    return tuple(sum(diffs[i:]) for i in range(6))


def vertex_count(nodes: tuple[int, ...]) -> int:
    counts = {}
    for v in base_values(nodes):
        counts[v] = counts.get(v, 0) + 1
    n = math.factorial(6)
    for c in counts.values():
        n //= math.factorial(c)
    return n


POLYS = tuple(
    {
        "nodes": nodes,
        "slug": slug_for_nodes(nodes),
        "display": display_for_nodes(nodes),
        "base": base_values(nodes),
        "vertices": vertex_count(nodes),
    }
    for nodes in all_node_sets()
)
POLY_BY_SLUG = {p["slug"]: p for p in POLYS}


@lru_cache(maxsize=None)
def build_polytope(slug: str):
    """Return (vertices_as_integer_tuples, centered_float_matrix, edge_list)."""
    info = POLY_BY_SLUG[slug]
    verts = sorted(set(itertools.permutations(info["base"])))
    index = {v: i for i, v in enumerate(verts)}
    edges = set()
    for i, v in enumerate(verts):
        by_value: dict[int, list[int]] = {}
        for pos, val in enumerate(v):
            by_value.setdefault(val, []).append(pos)
        for val, positions in by_value.items():
            higher = by_value.get(val + 1)
            if not higher:
                continue
            for a in positions:
                for b in higher:
                    w = list(v)
                    w[a], w[b] = w[b], w[a]
                    j = index[tuple(w)]
                    edges.add((min(i, j), max(i, j)))
    V = np.asarray(verts, dtype=float)
    return verts, V - V.mean(axis=0), sorted(edges)


def poly_summary() -> list[dict]:
    return [
        {
            "slug": p["slug"],
            "display": p["display"],
            "nodes": p["nodes"],
            "base": p["base"],
            "vertices": p["vertices"],
            "edges": len(build_polytope(p["slug"])[2]),
        }
        for p in POLYS
    ]
