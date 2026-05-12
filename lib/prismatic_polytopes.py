"""Registry of the 204 prismatic uniform 4-polytopes in scope.

Family A: 17 polyhedral prisms (skip cube_prism = tesseract)
Family B: 170 duoprisms {p}x{q} (3 <= p <= q <= 20, skip (4,4) = tesseract)
Family C: 17 antiprismatic prisms (n in [3, 20], skip n=3 = octahedral prism)

Each registry entry is a dict with:
  slug:        output folder name under output/
  family:      'A' | 'B' | 'C'
  builder:     callable returning (V, edges)
  metadata:    dict with polytope-specific identifiers (name / p / q / n)
"""

from __future__ import annotations

from typing import Callable, Iterable

from polytopes_prismatic import (
    polyhedral_prism, duoprism, antiprismatic_prism,
    polyhedral_prism_slug, duoprism_slug, antiprismatic_prism_slug,
)
from uniform_polyhedra import all_polyhedra


def _family_a():
    out = []
    for name in all_polyhedra():
        if name == "cube":
            continue  # cube prism = tesseract, already in main corpus
        slug = polyhedral_prism_slug(name)
        out.append({
            "slug": slug,
            "family": "A",
            "builder": (lambda nm=name: polyhedral_prism(nm)),
            "metadata": {"polyhedron": name},
        })
    return out


def _family_b():
    out = []
    for p in range(3, 21):
        for q in range(p, 21):
            if (p, q) == (4, 4):
                continue
            slug = duoprism_slug(p, q)
            out.append({
                "slug": slug,
                "family": "B",
                "builder": (lambda pp=p, qq=q: duoprism(pp, qq)),
                "metadata": {"p": p, "q": q},
            })
    return out


def _family_c():
    out = []
    for n in range(3, 21):
        if n == 3:
            continue  # antiprism with n=3 = octahedron, already in Family A
        slug = antiprismatic_prism_slug(n)
        out.append({
            "slug": slug,
            "family": "C",
            "builder": (lambda nn=n: antiprismatic_prism(nn)),
            "metadata": {"n": n},
        })
    return out


_REGISTRY_A = _family_a()
_REGISTRY_B = _family_b()
_REGISTRY_C = _family_c()
REGISTRY = _REGISTRY_A + _REGISTRY_B + _REGISTRY_C


def get_registry(family: str | None = None) -> Iterable[dict]:
    if family is None:
        return list(REGISTRY)
    fam = family.upper()
    return [e for e in REGISTRY if e["family"] == fam]


def get_by_slug(slug: str) -> dict | None:
    for e in REGISTRY:
        if e["slug"] == slug:
            return e
    return None
