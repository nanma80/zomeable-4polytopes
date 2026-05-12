"""Generate RESULTS.md for each prismatic polytope from sweep log.

Reads ongoing_work/prismatic_sweep_log.jsonl (the latest record per
polytope wins) and writes:
  * output/<slug>/RESULTS.md  -- for every polytope that emitted >= 1
                                  zomeable shape

Pattern follows the existing 47-corpus RESULTS.md files: header, summary
table, optional kernel/sig table, then the vzome-viewer embed block per
emitted file.
"""

import argparse
import json
import os
import sys
from collections import OrderedDict


HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
LOG_PATH = os.path.join(REPO_ROOT, "ongoing_work", "prismatic_sweep_log.jsonl")
OUTPUT_ROOT = os.path.join(REPO_ROOT, "output")

# Family -> category subfolder under output/.  Mirrors the layout used
# by tools/run_prismatic_sweep.py.
FAMILY_DIR = {
    "A": "polyhedral_prisms",
    "B": "duoprisms",
    "C": "antiprismatic_prisms",
}


def _category(family: str) -> str:
    return FAMILY_DIR.get(family, "")


def _rel_output_path(slug: str, family: str) -> str:
    cat = _category(family)
    return f"output/{cat}/{slug}" if cat else f"output/{slug}"


SCRIPT_LINE = ("<script type='module' "
               "src='https://www.vzome.com/modules/vzome-viewer.js'></script>")


def _viewer_figure(fname: str) -> str:
    return (
        '<figure style="width: 800px; margin: 5%">\n'
        f' <vzome-viewer style="width: 100%; height: 500px" src="{fname}" progress="true" >\n'
        ' </vzome-viewer>\n'
        ' <figcaption style="text-align: center; font-style: italic;">\n'
        f'    {fname}\n'
        ' </figcaption>\n'
        '</figure>\n'
    )


def _polytope_display_name(slug: str, family: str, metadata: dict) -> str:
    if family == "A":
        return f"{metadata['polyhedron'].replace('_', ' ')} prism"
    if family == "B":
        p, q = metadata["p"], metadata["q"]
        return f"{{{p}}}×{{{q}}} duoprism"
    if family == "C":
        return f"{metadata['n']}-gonal antiprismatic prism"
    return slug


def _family_text(family: str) -> str:
    return {
        "A": "polyhedral prism",
        "B": "duoprism",
        "C": "antiprismatic prism",
    }.get(family, family)


def _format_kernel(k):
    return "(" + ", ".join(f"{x:+.4f}" for x in k) + ")"


def _strut_sig(emit) -> str:
    sc = emit.get("strut_counts")
    if not sc:
        return ""
    items = sorted(sc.items())
    return "  ".join(f"{k}:{v}" for k, v in items)


def _latest_per_slug(log_path: str) -> OrderedDict:
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
            recs[slug] = r  # later wins
    return recs


def build_results_md(rec: dict) -> str | None:
    slug = rec["slug"]
    family = rec["family"]
    metadata = rec["metadata"]
    emits = [e for e in rec.get("emitted", []) if e.get("status") == "emitted"]
    if not emits:
        return None
    name = _polytope_display_name(slug, family, metadata)
    fam_text = _family_text(family)
    nV = rec.get("nV", "?")
    nE = rec.get("nE", "?")
    rng = rec.get("rng", 2)

    lines = []
    lines.append(f"# {name} → zomeable orthographic projections")
    lines.append("")
    lines.append(f"- Family **{family}** ({fam_text})")
    lines.append(f"- 4D vertices: **{nV}**, edges: **{nE}**")
    lines.append(f"- Folder: `{_rel_output_path(slug, family)}/`")
    lines.append("")
    lines.append(f"**{len(emits)} distinct zomeable shape"
                 f"{'' if len(emits) == 1 else 's'}** found "
                 f"(rng = {rng} agnostic kernel sweep).")
    lines.append("")
    lines.append("## Shapes")
    lines.append("")
    lines.append("| # | File | Label / direction | n_balls | Struts |")
    lines.append("|---|------|-------------------|--------:|--------|")
    for i, e in enumerate(emits, 1):
        sub = e.get("subtype") or ""
        lab = e.get("label", "")
        if sub:
            label = f"{lab} / {sub}"
        else:
            label = lab
        fname = f"`{e['basename']}.vZome`"
        nballs = e.get("n_balls", "?")
        sig = _strut_sig(e)
        lines.append(f"| {i} | {fname} | {label} | {nballs} | {sig} |")
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    lines.append(f"- Sweep driver: `tools/run_prismatic_sweep.py "
                 f"--family {family} --rng {rng}`")
    lines.append(f"- Construction: `lib/polytopes_prismatic.py` "
                 f"+ `lib/uniform_polyhedra.py`")
    lines.append("- See [`docs/PRISMATIC.md`](../../../docs/PRISMATIC.md) "
                 "for the full prismatic-family taxonomy and sweep summary.")
    lines.append("")
    lines.append("## 3D Viewers")
    lines.append("")
    lines.append("<!-- _3d-viewer-html-link_ -->")
    lines.append(f"➡️ **[Open this page on GitHub Pages]"
                 f"(https://nanma80.github.io/zomeable-4polytopes/"
                 f"{_rel_output_path(slug, family)}/RESULTS.html)** to "
                 f"interact with the 3D models below (the embeds only "
                 f"render when this file is served via GitHub Pages, not "
                 f"in github.com's markdown preview).")
    lines.append("")
    lines.append(SCRIPT_LINE)
    lines.append("")
    for e in emits:
        lines.append(_viewer_figure(f"{e['basename']}.vZome"))

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=LOG_PATH)
    ap.add_argument("--family", choices=["A", "B", "C"], default=None)
    args = ap.parse_args()

    if not os.path.exists(args.log):
        print(f"ERROR: log not found: {args.log}", file=sys.stderr)
        sys.exit(1)

    recs = _latest_per_slug(args.log)
    written = 0
    skipped_no_emit = 0
    for slug, rec in recs.items():
        if args.family and rec.get("family") != args.family:
            continue
        md = build_results_md(rec)
        if md is None:
            skipped_no_emit += 1
            continue
        cat = _category(rec.get("family", ""))
        if cat:
            out_dir = os.path.join(OUTPUT_ROOT, cat, slug)
        else:
            out_dir = os.path.join(OUTPUT_ROOT, slug)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "RESULTS.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        written += 1
    print(f"wrote {written} RESULTS.md files; {skipped_no_emit} skipped (0 emits)")


if __name__ == "__main__":
    main()
