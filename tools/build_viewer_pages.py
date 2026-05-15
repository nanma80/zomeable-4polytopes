"""Generate the 3-level browsing UX.

Reads existing manifests + filesystem and emits:
  * output/<category>/<slug>/VIEWER.md      -- viewer-only per polytope
  * docs/CATEGORY_REGULAR.md
  * docs/CATEGORY_UNIFORM.md
  * docs/CATEGORY_DUOPRISMS.md
  * docs/CATEGORY_POLYHEDRAL_PRISMS.md
  * docs/CATEGORY_ANTIPRISMATIC_PRISMS.md

The top-level README.md is rewritten by a separate step (this script
prints recommended counts at the end so the human edit of README is
trivial).

Idempotent: rerunning with no corpus changes produces no diff.
"""

import json
import os
import re
import sys
from collections import OrderedDict, defaultdict


HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
OUTPUT_ROOT = os.path.join(REPO_ROOT, "output")
DOCS_ROOT = os.path.join(REPO_ROOT, "docs")

WYTHOFF_MANIFEST = os.path.join(OUTPUT_ROOT, "wythoff_sweep_manifest.json")
PRISMATIC_MANIFEST = os.path.join(OUTPUT_ROOT, "prismatic_manifest.json")

PAGES_BASE = "https://nanma80.github.io/zomeable-4polytopes"

VZOME_SCRIPT = ("<script type='module' "
                "src='https://www.vzome.com/modules/vzome-viewer.js'></script>")


def viewer_figure(fname: str) -> str:
    return (
        '<figure style="width: 800px; margin: 5%">\n'
        f' <vzome-viewer style="width: 100%; height: 500px" src="{fname}" progress="true" >\n'
        ' </vzome-viewer>\n'
        ' <figcaption style="text-align: center; font-style: italic;">\n'
        f'    {fname}\n'
        ' </figcaption>\n'
        '</figure>\n'
    )


# -----------------------------------------------------------------------
# Regular polytopes — hand-curated metadata
# -----------------------------------------------------------------------

REGULAR_POLYTOPES = OrderedDict([
    # slug, display_name, deep_dive_filename, brief_count, shape_names
    ("5cell",   ("5-cell {3,3,3}",     "RESULTS.md",
                "4",                "vertex-first + 3 oblique")),
    ("8cell",   ("8-cell {4,3,3} (tesseract)", "CLASSIFICATION.md",
                "3 + 1 inf family", "cell-first + vertex-first + phi-oblique + inf family")),
    ("16cell",  ("16-cell {3,3,4}",    "RESULTS.md",
                "6",                "vertex-first + cell-first + edge-first + 3 triality")),
    ("24cell",  ("24-cell {3,4,3}",    "ZOMEABLE_PROJECTIONS.md",
                "3",                "cell-first + vertex-first + triality")),
    ("120cell", ("120-cell {5,3,3}",   "RESULTS.md",
                "1",                "cell-first")),
    ("600cell", ("600-cell {3,3,5}",   "RESULTS.md",
                "1",                "vertex-first")),
])


# 8-cell viewer ordering: sporadics first, then inf-family in ascending
# norm (a²+b²).  Integers first, then ℤ[φ] members.
EIGHT_CELL_SPORADICS = [
    "8cell_cell_first_cube.vZome",
    "8cell_vertex_first_rhombic_dodec.vZome",
    "8cell_phi_oblique.vZome",
]
EIGHT_CELL_INF_FAMILY = [
    # ordered by a²+b² ascending; phi-branch members at the end
    "8cell_inf_family_a1_b2.vZome",       # a²+b² = 5
    "8cell_inf_family_a3_b4.vZome",       # 25
    "8cell_inf_family_a5_b12.vZome",      # 169
    "8cell_inf_family_a8_b15.vZome",      # 289
    "8cell_inf_family_a2_b11.vZome",      # 125
    "8cell_inf_family_a19_b22.vZome",     # 845
    "8cell_inf_family_a2_b29.vZome",      # 845
    "8cell_inf_family_phi_aSqrt5_b2.vZome",          # 9 (φ-branch)
    "8cell_inf_family_phi_a3plus2phi_b4phi-4.vZome", # 45 (φ-branch)
    "8cell_inf_family_phi_a4phi_b5-2phi.vZome",      # 45 (φ-branch)
]


# -----------------------------------------------------------------------
# Wythoff descendant catalogue (39 polytopes across A4/B4/F4/H4)
# -----------------------------------------------------------------------
#
# Per WYTHOFF_SWEEP.md the 39 Wythoff descendants of the four rank-4
# Coxeter groups, with shape counts.  Slugs match the existing
# output/uniform/<slug>/ folders.  Zero-shape descendants have no folder
# (no .vZome to put there) — they appear in the category page but not
# as viewer links.
#
# Two B4 names ((0,1,0,1)=cantellated 16-cell ≡ rectified 24-cell,
# (0,1,1,1)=cantitruncated 16-cell ≡ truncated 24-cell) are counted
# under F4 by convention; they are not listed under B4 here.

WYTHOFF_CATALOGUE = OrderedDict([
    # ---- A4 (5-cell family) ----
    ("rectified_5cell",       ("rectified 5-cell",       "A4", 4)),
    ("truncated_5cell",       ("truncated 5-cell",       "A4", 4)),
    ("bitruncated_5cell",     ("bitruncated 5-cell",     "A4", 4)),
    ("cantellated_5cell",     ("cantellated 5-cell",     "A4", 4)),
    ("cantitruncated_5cell",  ("cantitruncated 5-cell",  "A4", 4)),
    ("runcinated_5cell",      ("runcinated 5-cell",      "A4", 4)),
    ("runcitruncated_5cell",  ("runcitruncated 5-cell",  "A4", 4)),
    ("omnitruncated_5cell",   ("omnitruncated 5-cell",   "A4", 4)),
    # ---- B4 (tesseract / 16-cell family) ----
    ("rectified_8cell",       ("rectified tesseract",    "B4", 6)),
    ("truncated_tesseract",   ("truncated tesseract",    "B4", 0)),
    ("cantellated_tesseract", ("cantellated tesseract",  "B4", 0)),
    ("bitruncated_8cell",     ("bitruncated tesseract",  "B4", 6)),
    ("cantitruncated_tesseract", ("cantitruncated tesseract", "B4", 0)),
    ("runcinated_tesseract",  ("runcinated tesseract",   "B4", 0)),
    ("runcitruncated_tesseract", ("runcitruncated tesseract", "B4", 0)),
    ("truncated_16cell",      ("truncated 16-cell",      "B4", 6)),
    ("runcitruncated_16cell", ("runcitruncated 16-cell", "B4", 0)),
    ("omnitruncated_tesseract", ("omnitruncated tesseract", "B4", 0)),
    # ---- F4 (24-cell family) ----
    ("rectified_24cell",      ("rectified 24-cell",      "F4", 3)),
    ("truncated_24cell",      ("truncated 24-cell",      "F4", 3)),
    ("cantellated_24cell",    ("cantellated 24-cell",    "F4", 0)),
    ("bitruncated_24cell",    ("bitruncated 24-cell",    "F4", 0)),
    ("cantitruncated_24cell", ("cantitruncated 24-cell", "F4", 0)),
    ("runcinated_24cell",     ("runcinated 24-cell",     "F4", 0)),
    ("runcitruncated_24cell", ("runcitruncated 24-cell", "F4", 0)),
    ("omnitruncated_24cell",  ("omnitruncated 24-cell",  "F4", 0)),
    # ---- H4 (120-cell / 600-cell family) — all 13 nonzero ----
    ("rectified_120cell",       ("rectified 120-cell",       "H4", 1)),
    ("rectified_600cell",       ("rectified 600-cell",       "H4", 1)),
    ("truncated_120cell",       ("truncated 120-cell",       "H4", 1)),
    ("truncated_600cell",       ("truncated 600-cell",       "H4", 1)),
    ("bitruncated_120cell",     ("bitruncated 120-cell",     "H4", 1)),
    ("cantellated_120cell",     ("cantellated 120-cell",     "H4", 1)),
    ("cantellated_600cell",     ("cantellated 600-cell",     "H4", 1)),
    ("cantitruncated_120cell",  ("cantitruncated 120-cell",  "H4", 1)),
    ("cantitruncated_600cell",  ("cantitruncated 600-cell",  "H4", 1)),
    ("runcinated_120cell",      ("runcinated 120-cell",      "H4", 1)),
    ("runcitruncated_120cell",  ("runcitruncated 120-cell",  "H4", 1)),
    ("runcitruncated_600cell",  ("runcitruncated 600-cell",  "H4", 1)),
    ("omnitruncated_120cell",   ("omnitruncated 120-cell",   "H4", 1)),
])


NON_WYTHOFFIAN = OrderedDict([
    ("snub_24cell",     ("snub 24-cell",     2)),
    ("grand_antiprism", ("grand antiprism",  2)),
])


# slug -> short inheritance descriptor for the level-2 uniform table.
# Format mirrors the old top-level README "Inherits from" column.
INHERITS_FROM = {
    "snub_24cell":              "600-cell (diminishing)",
    "grand_antiprism":          "600-cell (diminishing)",
    # A4
    "rectified_5cell":          "5-cell — vertex-first + 3 oblique",
    "truncated_5cell":          "5-cell — vertex-first + 3 oblique",
    "bitruncated_5cell":        "5-cell — vertex-first + 3 oblique",
    "cantellated_5cell":        "5-cell — vertex-first + 3 oblique",
    "cantitruncated_5cell":     "5-cell — vertex-first + 3 oblique",
    "runcinated_5cell":         "5-cell — vertex-first + 3 oblique",
    "runcitruncated_5cell":     "5-cell — vertex-first + 3 oblique",
    "omnitruncated_5cell":      "5-cell — vertex-first + 3 oblique",
    # B4 (kernels trace to the 16-cell)
    "rectified_8cell":          "16-cell — vertex/cell/edge-first + 3 triality",
    "bitruncated_8cell":        "16-cell — vertex/cell/edge-first + 3 triality",
    "truncated_16cell":         "16-cell — vertex/cell/edge-first + 3 triality",
    # F4
    "rectified_24cell":         "24-cell — cell-first + vertex-first + triality",
    "truncated_24cell":         "24-cell — cell-first + vertex-first + triality",
    # H4
    "rectified_120cell":        "120-cell",
    "truncated_120cell":        "120-cell",
    "cantellated_120cell":      "120-cell",
    "cantitruncated_120cell":   "120-cell",
    "runcitruncated_120cell":   "120-cell",
    "bitruncated_120cell":      "120-cell + 600-cell",
    "runcinated_120cell":       "120-cell + 600-cell",
    "omnitruncated_120cell":    "120-cell + 600-cell",
    "rectified_600cell":        "600-cell",
    "truncated_600cell":        "600-cell",
    "cantellated_600cell":      "600-cell",
    "cantitruncated_600cell":   "600-cell",
    "runcitruncated_600cell":   "600-cell",
}


CANONICAL_LABEL_ORDER = ["cell_first", "vertex_first", "face_first", "edge_first"]


def prismatic_shape_descr(shapes):
    """Aggregate prismatic shape labels into 'cell-first + 3 oblique' format."""
    counts = defaultdict(int)
    for sh in shapes:
        counts[sh.get("label") or "oblique"] += 1
    parts = []
    for key in CANONICAL_LABEL_ORDER:
        n = counts.get(key, 0)
        if n == 0:
            continue
        label = key.replace("_", "-")
        parts.append(label if n == 1 else f"{n} {label}")
    n_obl = counts.get("oblique", 0)
    if n_obl > 0:
        parts.append("oblique" if n_obl == 1 else f"{n_obl} oblique")
    return " + ".join(parts)


# -----------------------------------------------------------------------
# Manifest loaders
# -----------------------------------------------------------------------

def load_wythoff_files():
    """slug -> sorted [basename.vZome, ...]"""
    m = json.load(open(WYTHOFF_MANIFEST, encoding="utf-8"))
    by_slug = defaultdict(list)
    for sh in m["shapes"]:
        if sh.get("status") != "ok" or "file" not in sh:
            continue
        path = sh["file"]  # e.g. "uniform/rectified_5cell/foo.vZome"
        parts = path.split("/")
        if len(parts) < 3:
            continue
        slug = parts[1]
        fname = parts[-1]
        by_slug[slug].append(fname)
    return {k: sorted(set(v)) for k, v in by_slug.items()}


def load_prismatic_files():
    """slug -> {n_shapes, files, family, metadata}"""
    m = json.load(open(PRISMATIC_MANIFEST, encoding="utf-8"))
    out = {}
    for fam, rows in m["families"].items():
        for row in rows:
            slug = row["slug"]
            n = row.get("n_shapes", 0)
            files = [s["basename"] + ".vZome" for s in row.get("shapes", [])]
            out[slug] = {
                "n_shapes": n,
                "files": sorted(set(files)),
                "shapes": row.get("shapes", []),
                "family": fam,
                "metadata": row.get("metadata", {}),
                "nV": row.get("nV"),
                "nE": row.get("nE"),
            }
    return out


def glob_vzome(rel_dir):
    """Return sorted list of *.vZome basenames in output/<rel_dir>/."""
    full = os.path.join(OUTPUT_ROOT, rel_dir)
    if not os.path.isdir(full):
        return []
    return sorted(f for f in os.listdir(full) if f.endswith(".vZome"))


# -----------------------------------------------------------------------
# VIEWER.md emitter
# -----------------------------------------------------------------------

def emit_viewer(output_dir, display_name, files, deep_dive_filename,
                groups=None, n_total=None):
    """Write VIEWER.md in output/<output_dir>/.

    files: list of basenames OR (when `groups` is set) ignored
    groups: optional list of (section_heading_or_None, [files...])
    """
    full_dir = os.path.join(OUTPUT_ROOT, output_dir)
    os.makedirs(full_dir, exist_ok=True)

    rel = output_dir.replace(os.sep, "/")
    pages_url = f"{PAGES_BASE}/output/{rel}/VIEWER.html"

    if n_total is None:
        if groups is not None:
            n_total = sum(len(fs) for _, fs in groups)
        else:
            n_total = len(files)

    lines = []
    lines.append(f"# {display_name} — interactive 3D viewer")
    lines.append("")
    lines.append(
        f"➡️ **[Open this page on GitHub Pages]({pages_url})** to interact "
        f"with the {n_total} model{'s' if n_total != 1 else ''} below."
    )
    lines.append("")
    lines.append(
        f"For methodology, kernel directions, search subtleties, and "
        f"reproduction commands, see "
        f"[`{deep_dive_filename}`]({deep_dive_filename}) in the same folder."
    )
    lines.append("")
    lines.append(VZOME_SCRIPT)
    lines.append("")

    if groups is None:
        groups = [(None, files)]

    for heading, fs in groups:
        if heading:
            lines.append(f"## {heading}")
            lines.append("")
        for fname in fs:
            lines.append(viewer_figure(fname))

    content = "\n".join(lines).rstrip() + "\n"
    out_path = os.path.join(full_dir, "VIEWER.md")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    return out_path


# -----------------------------------------------------------------------
# Category-page emitter
# -----------------------------------------------------------------------

def emit_category_page(filename, title, intro_lines, rows, descr_header,
                       zero_section=None, footer_lines=None):
    """rows: list of (display_name, count, descr, viewer_relpath_or_None, extra_note)"""
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    for line in intro_lines:
        lines.append(line)
    if intro_lines:
        lines.append("")

    lines.append(f"| Polytope | Zomeable projections | {descr_header} | Viewer |")
    lines.append("|----------|---------------------:|----------------|--------|")
    for name, count, descr, viewer_rel, note in rows:
        nm = name
        if note:
            nm = f"{nm} {note}"
        if viewer_rel:
            viewer_url = f"{PAGES_BASE}/{viewer_rel[:-3]}.html"
            viewer_cell = f"[3D viewer\u00a0→]({viewer_url})"
        else:
            viewer_cell = "—"
        lines.append(f"| {nm} | {count} | {descr} | {viewer_cell} |")
    lines.append("")

    if zero_section:
        lines.append("")
        lines.append(zero_section.rstrip())
        lines.append("")

    if footer_lines:
        lines.append("")
        for line in footer_lines:
            lines.append(line)
        lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    out_path = os.path.join(DOCS_ROOT, filename)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    return out_path


# -----------------------------------------------------------------------
# Main builds
# -----------------------------------------------------------------------

def build_regulars(counts):
    written = []
    for slug, (display, dd, _brief, _descr) in REGULAR_POLYTOPES.items():
        rel_dir = os.path.join("regular", slug)
        if slug == "8cell":
            files = glob_vzome(rel_dir)
            file_set = set(files)
            sporadics = [f for f in EIGHT_CELL_SPORADICS if f in file_set]
            infs = [f for f in EIGHT_CELL_INF_FAMILY if f in file_set]
            covered = set(sporadics) | set(infs)
            leftover = sorted(f for f in files if f not in covered)
            if leftover:
                print(f"  WARN: 8cell leftover files not in ordering: {leftover}",
                      file=sys.stderr)
            groups = [
                (f"Sporadic shapes ({len(sporadics)})", sporadics),
                (f"Infinite family — split-cuboids ({len(infs)})", infs + leftover),
            ]
            n_total = len(sporadics) + len(infs) + len(leftover)
            path = emit_viewer(rel_dir, display, [], dd, groups=groups,
                               n_total=n_total)
            counts["regular_files"] += n_total
        else:
            files = glob_vzome(rel_dir)
            path = emit_viewer(rel_dir, display, files, dd)
            counts["regular_files"] += len(files)
        written.append(path)
        counts["regular_polytopes_with_shapes"] += 1
    counts["regular_polytopes_in_scope"] = len(REGULAR_POLYTOPES)
    return written


def build_uniforms(counts):
    written = []
    wy_files = load_wythoff_files()
    # Wythoff descendants
    for slug, (display, group, n) in WYTHOFF_CATALOGUE.items():
        if n == 0:
            continue
        rel_dir = os.path.join("uniform", slug)
        files = wy_files.get(slug) or glob_vzome(rel_dir)
        if not files:
            print(f"  WARN: {slug} has expected n={n} but no files found",
                  file=sys.stderr)
            continue
        path = emit_viewer(rel_dir, display, files, "RESULTS.md")
        written.append(path)
        counts["uniform_polytopes_with_shapes"] += 1
        counts["uniform_files"] += len(files)
    # Non-Wythoffian
    for slug, (display, n) in NON_WYTHOFFIAN.items():
        rel_dir = os.path.join("uniform", slug)
        files = glob_vzome(rel_dir)
        if not files:
            print(f"  WARN: {slug} folder empty", file=sys.stderr)
            continue
        path = emit_viewer(rel_dir, display, files, "RESULTS.md")
        written.append(path)
        counts["uniform_polytopes_with_shapes"] += 1
        counts["uniform_files"] += len(files)
    counts["uniform_polytopes_in_scope"] = (
        len(WYTHOFF_CATALOGUE) + len(NON_WYTHOFFIAN))
    return written


def build_prismatics(counts, prismatic_data):
    written = []
    # Display-name helpers
    def disp_A(slug, meta):
        ph = meta.get("polyhedron", slug)
        return f"{ph.replace('_', ' ')} prism"
    def disp_B(slug, meta):
        p, q = meta.get("p"), meta.get("q")
        return f"{{{p}}}×{{{q}}} duoprism"
    def disp_C(slug, meta):
        n = meta.get("n", slug)
        return f"{n}-antiprismatic prism"
    fam_display = {"A": disp_A, "B": disp_B, "C": disp_C}
    fam_cat_dir = {"A": "polyhedral_prisms", "B": "duoprisms", "C": "antiprismatic_prisms"}
    fam_key = {"A": "polyhedral", "B": "duoprism", "C": "antiprismatic"}

    for slug, row in prismatic_data.items():
        if row["n_shapes"] == 0:
            continue
        fam = row["family"]
        cat = fam_cat_dir[fam]
        display = fam_display[fam](slug, row["metadata"])
        rel_dir = os.path.join(cat, slug)
        files = row["files"]
        path = emit_viewer(rel_dir, display, files, "RESULTS.md")
        written.append(path)
        counts[f"{fam_key[fam]}_polytopes_with_shapes"] += 1
        counts[f"{fam_key[fam]}_files"] += len(files)
    counts["polyhedral_polytopes_in_scope"] = 17
    counts["duoprism_polytopes_in_scope"] = 170
    counts["antiprismatic_polytopes_in_scope"] = 17
    return written


# -----------------------------------------------------------------------
# Category pages
# -----------------------------------------------------------------------

def page_regular():
    rows = []
    for slug, (display, dd, brief, descr) in REGULAR_POLYTOPES.items():
        viewer_rel = f"output/regular/{slug}/VIEWER.md"
        rows.append((display, brief, descr, viewer_rel, None))
    return emit_category_page(
        "CATEGORY_REGULAR.md",
        "Regular 4-polytopes — zomeable orthographic projections",
        [
            "The six convex regular 4-polytopes.  The tesseract (8-cell)",
            "is the only one whose set of zomeable projections is infinite;",
            "the others all saturate at a small finite count.",
        ],
        rows,
        descr_header="By type",
        footer_lines=[
            "## More detail",
            "",
            "- [`docs/SUMMARY.md`](SUMMARY.md) — full result narrative",
            "- [`docs/METHODOLOGY.md`](METHODOLOGY.md) — saturation discussion",
            "- [`output/regular/8cell/CLASSIFICATION.md`](../output/regular/8cell/CLASSIFICATION.md) — tesseract inf-family master theorem",
        ],
    )


def page_uniform():
    rows = []
    rows.append(("**Non-Wythoffian** *(diminishings of the 600-cell)*", "", "", None, None))
    for slug, (display, n) in NON_WYTHOFFIAN.items():
        rel = f"output/uniform/{slug}/VIEWER.md"
        rows.append((display, str(n), INHERITS_FROM.get(slug, ""), rel, None))
    for grp_label, grp_id in [
        ("**A₄ descendants** *(5-cell family)*", "A4"),
        ("**B₄ descendants** *(tesseract / 16-cell family)*", "B4"),
        ("**F₄ descendants** *(24-cell family)*", "F4"),
        ("**H₄ descendants** *(120-cell / 600-cell family)*", "H4"),
    ]:
        group_hits = [
            (slug, display, n)
            for slug, (display, group, n) in WYTHOFF_CATALOGUE.items()
            if group == grp_id and n > 0
        ]
        if not group_hits:
            continue
        rows.append((grp_label, "", "", None, None))
        for slug, display, n in group_hits:
            rel = f"output/uniform/{slug}/VIEWER.md"
            rows.append((display, str(n), INHERITS_FROM.get(slug, ""), rel, None))
    return emit_category_page(
        "CATEGORY_UNIFORM.md",
        "Uniform 4-polytopes — zomeable orthographic projections",
        [
            "41 convex uniform 4-polytopes: 39 Wythoff descendants of the four",
            "rank-4 Coxeter groups (A₄, B₄, F₄, H₄) plus 2 non-Wythoffian forms",
            "(snub 24-cell, grand antiprism, both diminishings of the 600-cell).",
            "",
            "Wythoff descendants inherit their zomeable projections from their",
            "parent regular by inheritance ([`docs/INHERITANCE_FREE_SWEEP.md`](INHERITANCE_FREE_SWEEP.md)).",
            "The 13 zero-shape descendants live in ℤ[√2]³ (B₄/F₄'s natural field),",
            "which is outside the icosahedral scope of this project.",
        ],
        rows,
        descr_header="Inherits from",
        footer_lines=[
            "## More detail",
            "",
            "- [`docs/WYTHOFF_SWEEP.md`](WYTHOFF_SWEEP.md) — full methodology and per-polytope shape descriptions",
            "- [`docs/INHERITANCE_FREE_SWEEP.md`](INHERITANCE_FREE_SWEEP.md) — corpus-completeness audit",
            "- [`docs/UNIFORM_PLAN.md`](UNIFORM_PLAN.md) — extension plan to all 47 convex uniforms",
        ],
    )


def _prismatic_rows(prismatic_data, family_key, display_fn, sort_key):
    """Return (rows, zero_summary).  sort_key takes (slug, row) -> sortable."""
    matched = [(slug, row) for slug, row in prismatic_data.items()
               if row["family"] == family_key]
    matched.sort(key=lambda sr: sort_key(sr[0], sr[1]))
    rows = []
    zero_items = []
    for slug, row in matched:
        display = display_fn(slug, row["metadata"])
        if row["n_shapes"] > 0:
            cat = {"A": "polyhedral_prisms", "B": "duoprisms",
                   "C": "antiprismatic_prisms"}[family_key]
            rel = f"output/{cat}/{slug}/VIEWER.md"
            descr = prismatic_shape_descr(row["shapes"])
            rows.append((display, str(row["n_shapes"]), descr, rel, None))
        else:
            zero_items.append(display)
    return rows, zero_items


def page_duoprisms(prismatic_data):
    def disp(slug, meta):
        return f"{{{meta['p']}}}×{{{meta['q']}}} duoprism"
    rows, zero = _prismatic_rows(
        prismatic_data, "B", disp,
        sort_key=lambda slug, row: (row["metadata"]["p"], row["metadata"]["q"]))
    zero_sec = (
        f"## Zero-shape duoprisms ({len(zero)})\n\n"
        "The remaining 164 duoprisms produced 0 zomeable projections.  Most "
        "fail because at least one of the {p}-gon or {q}-gon circles lies "
        "in ℤ[√3] (p ∈ {3, 6, 12, …}) or ℤ[√2] (p ∈ {8, …}), which don't "
        "embed in the icosahedral field ℤ[φ].  The icosahedral-compatible "
        "regular polygons in range are {4} (in ℤ), {5}, and {10} (both in "
        "ℤ[φ]).\n"
    )
    return emit_category_page(
        "CATEGORY_DUOPRISMS.md",
        "Duoprisms — zomeable orthographic projections",
        [
            "Cartesian products {p}×{q} of two regular polygons, 3 ≤ p ≤ q ≤ 20",
            "(excluding (4, 4) = tesseract).  170 polytopes in scope; 6 yielded",
            "≥1 zomeable projection.",
            "",
            "`duoprism_4_10` was the only +3 gainer at rng=4 and was investigated",
            "for inf-family behavior — saturated bounded at 5 shapes through rng=8.",
            "Similarly `duoprism_4_6` is bounded at 3 shapes through rng=8.",
        ],
        rows,
        descr_header="By type",
        zero_section=zero_sec,
        footer_lines=[
            "## More detail",
            "",
            "- [`docs/PRISMATIC.md`](PRISMATIC.md) — full prismatic sweep methodology and results",
            "- [`ongoing_work/duoprism_4_10_inf_family_resolved.md`](../ongoing_work/duoprism_4_10_inf_family_resolved.md) — duoprism_4_10 saturation evidence",
            "- [`ongoing_work/duoprism_4_6_inf_family_resolved.md`](../ongoing_work/duoprism_4_6_inf_family_resolved.md) — duoprism_4_6 saturation evidence",
            "- [`ongoing_work/duoprism_4q_census.md`](../ongoing_work/duoprism_4q_census.md) — q ∈ {5..12} census",
        ],
    )


def page_polyhedral_prisms(prismatic_data):
    def disp(slug, meta):
        return f"{meta.get('polyhedron', slug).replace('_', ' ')} prism"
    rows, zero = _prismatic_rows(
        prismatic_data, "A", disp,
        sort_key=lambda slug, row: row["metadata"].get("polyhedron", slug))
    zero_sec = (
        f"## Zero-shape polyhedral prisms ({len(zero)})\n\n"
        + ", ".join(f"`{z}`" for z in zero) +
        "\n\nThese 3D base polyhedra do not admit a zomeable orthographic "
        "projection of their cylinder.\n"
    ) if zero else ""
    return emit_category_page(
        "CATEGORY_POLYHEDRAL_PRISMS.md",
        "Polyhedral prisms — zomeable orthographic projections",
        [
            "P × [0,1] for each 3D uniform polyhedron P.  17 in scope (the",
            "cube prism = tesseract is covered under regulars).  12 yielded",
            "≥1 zomeable projection.",
        ],
        rows,
        descr_header="By type",
        zero_section=zero_sec,
        footer_lines=[
            "## More detail",
            "",
            "- [`docs/PRISMATIC.md`](PRISMATIC.md) — full prismatic sweep methodology and results",
        ],
    )


def page_antiprismatic_prisms(prismatic_data):
    def disp(slug, meta):
        return f"A_{meta['n']} × [0,1] (n={meta['n']})"
    rows, zero = _prismatic_rows(
        prismatic_data, "C", disp,
        sort_key=lambda slug, row: row["metadata"]["n"])
    zero_sec = (
        f"## Zero-shape antiprismatic prisms ({len(zero)})\n\n"
        "n ∈ {4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20} — "
        "16 cases.  Only the pentagonal antiprism (n=5) embeds in ℤ[φ]³ "
        "via the icosahedron's non-polar vertices.\n"
    )
    return emit_category_page(
        "CATEGORY_ANTIPRISMATIC_PRISMS.md",
        "Antiprismatic prisms — zomeable orthographic projections",
        [
            "A_n × [0,1] for each n-gonal antiprism A_n.  17 in scope",
            "(n ∈ [4, 20]; n=3 is the octahedral prism, covered under",
            "polyhedral prisms).  Only n=5 yielded zomeable projections.",
        ],
        rows,
        descr_header="By type",
        zero_section=zero_sec,
        footer_lines=[
            "## More detail",
            "",
            "- [`docs/PRISMATIC.md`](PRISMATIC.md) — full prismatic sweep methodology and results",
        ],
    )


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    counts = defaultdict(int)
    print("Loading manifests...")
    prismatic = load_prismatic_files()

    print("Building VIEWER.md pages...")
    written = []
    written += build_regulars(counts)
    written += build_uniforms(counts)
    written += build_prismatics(counts, prismatic)
    print(f"  wrote {len(written)} VIEWER.md files")

    print("Building category pages...")
    cat_pages = [
        page_regular(),
        page_uniform(),
        page_duoprisms(prismatic),
        page_polyhedral_prisms(prismatic),
        page_antiprismatic_prisms(prismatic),
    ]
    for p in cat_pages:
        print(f"  wrote {os.path.relpath(p, REPO_ROOT)}")

    print()
    print("=== Summary counts (for the top-level README table) ===")
    summary_rows = [
        ("Regular", counts["regular_polytopes_in_scope"],
         counts["regular_polytopes_with_shapes"], counts["regular_files"]),
        ("Uniform", counts["uniform_polytopes_in_scope"],
         counts["uniform_polytopes_with_shapes"], counts["uniform_files"]),
        ("Duoprisms", counts["duoprism_polytopes_in_scope"],
         counts["duoprism_polytopes_with_shapes"], counts["duoprism_files"]),
        ("Polyhedral prisms", counts["polyhedral_polytopes_in_scope"],
         counts["polyhedral_polytopes_with_shapes"], counts["polyhedral_files"]),
        ("Antiprismatic prisms", counts["antiprismatic_polytopes_in_scope"],
         counts["antiprismatic_polytopes_with_shapes"], counts["antiprismatic_files"]),
    ]
    total_scope = sum(r[1] for r in summary_rows)
    total_hits  = sum(r[2] for r in summary_rows)
    total_files = sum(r[3] for r in summary_rows)
    print(f"{'category':25} {'scope':>8} {'with_shapes':>12} {'shapes':>8}")
    for cat, scope, hits, files in summary_rows:
        print(f"{cat:25} {scope:>8} {hits:>12} {files:>8}")
    print(f"{'TOTAL':25} {total_scope:>8} {total_hits:>12} {total_files:>8}")
    print()
    print(f"Note: Regular total of {counts['regular_files']} shapes counts 8-cell sporadics (3) +")
    print("emitted inf-family members; the full tesseract inf-family is")
    print("parametrized by ZZ[phi]-Pythagorean triples and is infinite.")


if __name__ == "__main__":
    main()
