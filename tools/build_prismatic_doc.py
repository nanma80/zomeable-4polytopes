"""Generate docs/PRISMATIC.md and a manifest from the prismatic sweep log.

Outputs:
  * docs/PRISMATIC.md
  * output/prismatic_manifest.json

Reads ongoing_work/prismatic_sweep_log.jsonl (latest record per slug
wins).
"""

import argparse
import json
import os
from collections import OrderedDict


HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
LOG_PATH = os.path.join(REPO_ROOT, "ongoing_work", "prismatic_sweep_log.jsonl")
DOC_PATH = os.path.join(REPO_ROOT, "docs", "PRISMATIC.md")
MANIFEST_PATH = os.path.join(REPO_ROOT, "output", "prismatic_manifest.json")

# Family -> category subfolder under output/.  Mirrors the layout used
# by tools/run_prismatic_sweep.py.
FAMILY_DIR = {
    "A": "polyhedral_prisms",
    "B": "duoprisms",
    "C": "antiprismatic_prisms",
}


def _rel_link(slug: str, family: str) -> str:
    cat = FAMILY_DIR.get(family, "")
    return f"../output/{cat}/{slug}/RESULTS.md" if cat else f"../output/{slug}/RESULTS.md"


def _latest_per_slug(log_path):
    recs = OrderedDict()
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            slug = r.get("slug")
            if not slug:
                continue
            recs[slug] = r
    return recs


def _sort_a(rec):
    return rec["metadata"]["polyhedron"]


def _sort_b(rec):
    return (rec["metadata"]["p"], rec["metadata"]["q"])


def _sort_c(rec):
    return rec["metadata"]["n"]


def _table_a(recs):
    rows = sorted([r for r in recs if r["family"] == "A"], key=_sort_a)
    lines = []
    lines.append("### Family A — polyhedral prisms")
    lines.append("")
    lines.append("17 in scope (the cube prism = tesseract is covered in the main corpus).")
    lines.append("")
    lines.append("| 3D base polyhedron | Distinct shapes |")
    lines.append("|---|---:|")
    for r in rows:
        emits = [e for e in r.get("emitted", []) if e.get("status") == "emitted"]
        n = len(emits)
        link = (f"[`{r['slug']}`]({_rel_link(r['slug'], 'A')})"
                if n > 0 else r["slug"])
        polyhedron = r["metadata"]["polyhedron"].replace("_", " ")
        lines.append(f"| {polyhedron} ({link}) | {n} |")
    lines.append("")
    return "\n".join(lines)


def _table_b(recs):
    rows = sorted([r for r in recs if r["family"] == "B"], key=_sort_b)
    # Two views: the hits table (only nonzero), and a compact summary.
    hits = [r for r in rows
            if any(e.get("status") == "emitted" for e in r.get("emitted", []))]
    lines = []
    lines.append("### Family B — duoprisms `{p}×{q}`")
    lines.append("")
    lines.append(f"170 in scope (3 ≤ p ≤ q ≤ 20, skipping (4, 4) = tesseract).")
    lines.append("")
    if hits:
        lines.append(f"**{len(hits)} duoprisms** yielded ≥ 1 zomeable projection.")
        lines.append("")
        lines.append("| p | q | Distinct shapes |")
        lines.append("|---:|---:|---:|")
        for r in hits:
            p, q = r["metadata"]["p"], r["metadata"]["q"]
            emits = [e for e in r.get("emitted", []) if e.get("status") == "emitted"]
            link = f"[`{r['slug']}`]({_rel_link(r['slug'], 'B')})"
            lines.append(f"| {p} | {q} | {link} → {len(emits)} |")
    else:
        lines.append("No duoprisms yielded zomeable projections.")
    lines.append("")
    lines.append("The remaining "
                 f"{len(rows) - len(hits)} duoprisms produced 0 zomeable "
                 "projections.  Most fail because at least one of the "
                 "{p}-gon or {q}-gon circles lies in ℤ[√3] (p ∈ {3, 6, "
                 "12, …}) or ℤ[√2] (p ∈ {8, …}), which don't embed in "
                 "the icosahedral field ℤ[φ].  The icosahedral-compatible "
                 "regular polygons in range are {4} (in ℤ), {5}, and "
                 "{10} (both in ℤ[φ]).")
    lines.append("")
    return "\n".join(lines)


def _table_c(recs):
    rows = sorted([r for r in recs if r["family"] == "C"], key=_sort_c)
    hits = [r for r in rows
            if any(e.get("status") == "emitted" for e in r.get("emitted", []))]
    lines = []
    lines.append("### Family C — antiprismatic prisms")
    lines.append("")
    lines.append("17 in scope (n ∈ [4, 20]; n=3 = octahedral prism, in Family A).")
    lines.append("")
    if hits:
        noun = "antiprismatic prism" if len(hits) == 1 else "antiprismatic prisms"
        lines.append(f"**{len(hits)} {noun}** yielded ≥ 1 zomeable projection.")
        lines.append("")
        lines.append("| n | Distinct shapes |")
        lines.append("|---:|---:|")
        for r in hits:
            emits = [e for e in r.get("emitted", []) if e.get("status") == "emitted"]
            link = f"[`{r['slug']}`]({_rel_link(r['slug'], 'C')})"
            lines.append(f"| {r['metadata']['n']} | {link} → {len(emits)} |")
    else:
        lines.append("No antiprismatic prisms yielded zomeable projections.")
    lines.append("")
    remaining = len(rows) - len(hits)
    if remaining:
        noun = "antiprismatic prism" if remaining == 1 else "antiprismatic prisms"
        lines.append(f"The remaining {remaining} {noun} (n ≠ 5) produced 0 "
                     "zomeable projections: only the pentagonal antiprism "
                     "embeds in ℤ[φ]³ via the icosahedron's non-polar "
                     "vertices.")
    lines.append("")
    return "\n".join(lines)


def _totals(recs):
    total_emits = sum(
        len([e for e in r.get("emitted", []) if e.get("status") == "emitted"])
        for r in recs
    )
    hit_polytopes = sum(
        1 for r in recs
        if any(e.get("status") == "emitted" for e in r.get("emitted", []))
    )
    by_family = {}
    for r in recs:
        f = r["family"]
        by_family.setdefault(f, {"swept": 0, "hits": 0, "shapes": 0})
        by_family[f]["swept"] += 1
        emits = [e for e in r.get("emitted", []) if e.get("status") == "emitted"]
        if emits:
            by_family[f]["hits"] += 1
            by_family[f]["shapes"] += len(emits)
    return total_emits, hit_polytopes, by_family


def build_doc(recs):
    swept_count = len(recs)
    total_emits, hit_polytopes, by_family = _totals(recs)
    L = []
    L.append("# Prismatic uniform 4-polytopes — zomeable orthographic projections")
    L.append("")
    L.append("## Scope")
    L.append("")
    L.append("The non-prismatic convex uniform 4-polytopes (47 of them) are")
    L.append("covered in [`../README.md`](../README.md). The remaining convex")
    L.append("uniform 4-polytopes — the **prismatic** ones — fall into three")
    L.append("families, two of which are infinite. This document sweeps a")
    L.append("bounded sample of each family and catalogues every zomeable")
    L.append("orthographic projection found.")
    L.append("")
    L.append("Sweep parameters: `rng = 3`, `permute_dedup = False`,")
    L.append("agnostic search (no kernel-inheritance shortcut, no")
    L.append("obstruction-based filtering).  Each polytope is constructed")
    L.append("from scratch and tested identically.")
    L.append("")
    L.append("Polytopes covered: **{} (in scope)**".format(swept_count))
    L.append("")
    L.append("| Family | Description | In scope | Hit ≥ 1 | Total shapes |")
    L.append("|---|---|---:|---:|---:|")
    fam_labels = {
        "A": "Polyhedral prisms `P × [0,1]`",
        "B": "Duoprisms `{p}×{q}`",
        "C": "Antiprismatic prisms `A_n × [0,1]`",
    }
    for f in ["A", "B", "C"]:
        d = by_family.get(f, {"swept": 0, "hits": 0, "shapes": 0})
        L.append(f"| **{f}** | {fam_labels[f]} | {d['swept']} | {d['hits']} | {d['shapes']} |")
    L.append(f"| **Total** | | **{swept_count}** | **{hit_polytopes}** | **{total_emits}** |")
    L.append("")
    L.append("## Definitions")
    L.append("")
    L.append("A **zomeable projection** is a rank-3 orthogonal linear map")
    L.append("π : ℝ⁴ → ℝ³ whose image of the polytope's vertex set lies in")
    L.append("ℤ[φ]³, such that all edge directions can be aligned (by a")
    L.append("global rotation) with canonical Zometool RGBY axes.  Vertex")
    L.append("multiplicity in the image is allowed (a kernel-aligned")
    L.append("projection may collapse several 4D vertices to one 3D")
    L.append("point).")
    L.append("")
    L.append("Strict rank-3: the image must span a 3D subspace.  A 4D → 2D")
    L.append("projection (image planar, sitting in ℝ³ as `z = 0`) is not a")
    L.append("zomeable projection under this definition.  The sweep")
    L.append("enforces this through `_try_align` (a rotation must exist")
    L.append("that maps the projected edge directions onto Zome axes —")
    L.append("planar images cannot satisfy this for non-collinear edge")
    L.append("sets).")
    L.append("")
    L.append("## Methodology")
    L.append("")
    L.append("Identical machinery to the 47-corpus sweep:")
    L.append("")
    L.append("1. Construct each polytope's vertex set V ⊂ ℝ⁴ and edge list.")
    L.append("2. Enumerate kernel directions n ∈ ℤ[φ]⁴ with |a|, |b| ≤ 3")
    L.append("   (`gen_dirs(rng=3, permute_dedup=False)` — `False` because")
    L.append("   prismatic polytopes lack full S₄ axis-permutation")
    L.append("   symmetry).")
    L.append("3. For each n: project, attempt RGBY-alignment of edge")
    L.append("   directions, group hits by 3D shape signature.")
    L.append("4. For each unique shape: snap projected vertex coords to")
    L.append("   ℤ[φ]³ (multi-scale search) and emit a `.vZome` file.")
    L.append("")
    L.append("Driver: [`tools/run_prismatic_sweep.py`](../tools/run_prismatic_sweep.py).")
    L.append("Log: [`ongoing_work/prismatic_sweep_log.jsonl`](../ongoing_work/prismatic_sweep_log.jsonl)")
    L.append("(one record per polytope).")
    L.append("")
    L.append("## Results")
    L.append("")
    L.append(_table_a(recs))
    L.append("")
    L.append(_table_b(recs))
    L.append("")
    L.append(_table_c(recs))
    L.append("")
    L.append("## Reproduction")
    L.append("")
    L.append("```bash")
    L.append("# Family A (17 polyhedral prisms)")
    L.append("python tools/run_prismatic_sweep.py --family A --rng 3")
    L.append("# Family B (170 duoprisms)")
    L.append("python tools/run_prismatic_sweep.py --family B --rng 3")
    L.append("# Family C (17 antiprismatic prisms)")
    L.append("python tools/run_prismatic_sweep.py --family C --rng 3")
    L.append("")
    L.append("# Regenerate per-polytope RESULTS.md files from the sweep log")
    L.append("python tools/build_prismatic_results.py")
    L.append("")
    L.append("# Regenerate this doc + the manifest from the sweep log")
    L.append("python tools/build_prismatic_doc.py")
    L.append("```")
    L.append("")
    return "\n".join(L)


def build_manifest(recs):
    """A compact JSON manifest of all emitted shapes."""
    rng_values = [r.get("rng") for r in recs.values() if isinstance(r.get("rng"), int)]
    max_rng = max(rng_values) if rng_values else 3
    manifest = {
        "version": 1,
        "rng": max_rng,
        "permute_dedup": False,
        "families": {},
    }
    for slug, r in recs.items():
        f = r["family"]
        manifest["families"].setdefault(f, [])
        emits = [e for e in r.get("emitted", []) if e.get("status") == "emitted"]
        manifest["families"][f].append({
            "slug": slug,
            "metadata": r["metadata"],
            "nV": r.get("nV"),
            "nE": r.get("nE"),
            "n_shapes": len(emits),
            "shapes": [{
                "basename": e["basename"],
                "label": e["label"],
                "subtype": e.get("subtype"),
                "n_balls": e["n_balls"],
                "kernel": e["kernel"],
                "strut_counts": e.get("strut_counts"),
                "path": e.get("path"),
            } for e in emits],
        })
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=LOG_PATH)
    ap.add_argument("--doc-out", default=DOC_PATH)
    ap.add_argument("--manifest-out", default=MANIFEST_PATH)
    args = ap.parse_args()

    raw = _latest_per_slug(args.log)
    # Preserve insertion order but ensure we sort families A, B, C
    recs = list(raw.values())

    md = build_doc(recs)
    os.makedirs(os.path.dirname(args.doc_out), exist_ok=True)
    with open(args.doc_out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"wrote {args.doc_out}")

    manifest = build_manifest(raw)
    os.makedirs(os.path.dirname(args.manifest_out), exist_ok=True)
    with open(args.manifest_out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"wrote {args.manifest_out}")


if __name__ == "__main__":
    main()
