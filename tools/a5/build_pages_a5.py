"""Generate the A5-family gallery pages from output/a5_projections/manifest.json.

Mirrors the gosset_projections layout: one viewer page per polytope (each
embedding its family-shape variants via the vzome-viewer web component),
a VIEWER.md index, and a README.md file list + symmetry/buildability audit.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
GAL = ROOT / "output" / "a5_projections"
BASE_URL = "https://nanma80.github.io/zomeable-4polytopes/output/a5_projections"

from family import POLYS  # noqa: E402

DISPLAY = {p["slug"]: p["display"] for p in POLYS}
ORDER = [p["slug"] for p in POLYS]

VZOME_SCRIPT = "<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>"


def sym_label(order: int) -> str:
    names = {
        48: "octahedral symmetry (order 48)",
        24: "order-24 symmetry",
        12: "chiral-tetrahedral symmetry (order 12)",
        6: "order-6 symmetry",
    }
    return names.get(order, f"symmetry order {order}")


def shape_note(row: dict) -> str:
    notes = []
    if row["polytope"] == "5_simplex" and row["balls"] == 6:
        notes.append("projects onto a regular octahedron")
    if not row["fully_buildable"]:
        notes.append("direction-zomeable only")
    else:
        colors = "+".join(sorted(row["strut_colors"]))
        notes.append(f"buildable: {colors}")
    return "; ".join(notes)


def caption(row: dict) -> str:
    return (
        f"{DISPLAY[row['polytope']]} - {sym_label(row['symmetry_order'])}, "
        f"{row['balls']} balls ({shape_note(row)})"
    )


def figure(row: dict) -> str:
    return (
        '<figure style="width: 800px; margin: 5%">\n'
        f' <vzome-viewer style="width: 100%; height: 500px" src="{row["file"]}" progress="true" >\n'
        " </vzome-viewer>\n"
        ' <figcaption style="text-align: center; font-style: italic;">\n'
        f"    {caption(row)}\n"
        " </figcaption>\n"
        "</figure>"
    )


def color_priority(row: dict) -> int:
    """Consistent A5 family ordering by edge-color scheme:
    0 = green/blue (no yellow), 1 = yellow/green (no blue),
    2 = yellow/green/blue (all three)."""
    colors = row["direction_colors"]
    has_y = "Y" in colors
    has_b = "B" in colors
    if has_b and not has_y:
        return 0
    if has_y and not has_b:
        return 1
    return 2


def main():
    manifest = json.loads((GAL / "manifest.json").read_text())
    by_poly: dict[str, list[dict]] = {p: [] for p in ORDER}
    for row in manifest:
        by_poly[row["polytope"]].append(row)
    for rows in by_poly.values():
        rows.sort(key=lambda r: (color_priority(r), -r["symmetry_order"], r["balls"]))

    # per-polytope viewer pages
    for poly in ORDER:
        rows = by_poly[poly]
        disp = DISPLAY[poly]
        body = [
            f"# {disp} - interactive 3D viewer",
            "",
            f"**[Open this page on GitHub Pages]({BASE_URL}/{poly}.html)** to interact with these models.",
            "",
            "[Back to A5 projections index](VIEWER.md).",
            "",
            f"Strict orthographic zomeable projections of {disp} (A5 family). "
            "Each edge points along a default zometool axis (Blue/Yellow/Red/Green).",
            "",
            'In the captions, "balls" means distinct 3D ball positions in the vZome model after projection.',
            "",
            VZOME_SCRIPT,
            "",
        ]
        body += [figure(r) + "\n" for r in rows]
        (GAL / f"{poly}.md").write_text("\n".join(body), encoding="utf-8")

    # VIEWER.md index
    lines = [
        "# A5 simplex family projections - viewer index",
        "",
        f"**[Open this page on GitHub Pages]({BASE_URL}/VIEWER.html)** for the viewer index.",
        "",
        "Strict orthographic zomeable projections of the A5 (5-simplex) uniform "
        "family.  The polytope-independent raw-column `Z[phi]^3` sweep saturates at "
        "three distinct projection geometries, applied to all 19 Wythoff "
        "polytopes below.",
        "",
        '"Balls" counts distinct 3D ball positions in the projected vZome model; '
        "some vertices of the source polytope may coincide in 3D.",
        "",
        "| Source polytope | Models | Viewer |",
        "|---|---:|---|",
    ]
    for poly in ORDER:
        lines.append(f"| {DISPLAY[poly]} | {len(by_poly[poly])} | [3D viewer ->]({poly}.md) |")
    lines += [
        "",
        "See [`README.md`](README.md) for the file list and "
        "[`../../docs/A5_PROJECTIONS.md`](../../docs/A5_PROJECTIONS.md) for methodology.",
        "",
    ]
    (GAL / "VIEWER.md").write_text("\n".join(lines), encoding="utf-8")

    # README.md file list
    n_build = sum(1 for r in manifest if r["fully_buildable"])
    rl = [
        "# A5 simplex family projections",
        "",
        "Strict orthographic 3D projections of the A5 (5-simplex) uniform family: "
        "all 19 Wythoff ringed-node subsets modulo diagram reversal.",
        "",
        f"The {len(manifest)} `.vZome` files are organized in per-polytope subfolders.  "
        '"Balls" counts distinct 3D ball positions in the projected vZome model.',
        "",
        "Open the viewer index here:",
        "",
        "- [`VIEWER.md`](VIEWER.md)",
        "",
        "## Models",
        "",
        "| File | Source polytope | Vertices | Balls | Symmetry order | Scale | Colors | Buildable |",
        "|---:|---|---:|---:|---:|---|---|:---:|",
    ]
    for poly in ORDER:
        for r in by_poly[poly]:
            cmap = r["strut_colors"] if r["fully_buildable"] else r["direction_colors"]
            struts = ", ".join(f"{k}x{v}" for k, v in sorted(cmap.items()))
            rl.append(
                f"| `{r['file']}` | {DISPLAY[poly]} | "
                f"{r.get('source_vertices', '')} | {r['balls']} | "
                f"{r['symmetry_order']} | `{r['scale']}` | {struts} | "
                f"{'yes' if r['fully_buildable'] else 'direction-only'} |"
            )
    rl += [
        "",
        f"{n_build} of {len(manifest)} models are fully buildable with standard "
        "vZome struts (a phi-power strut length, or exactly double one, matched per "
        "color orbit); every model is direction-zomeable (all edges parallel to a "
        "zometool axis).  Models are centered on the ball centroid, scaled by a "
        "power of phi, and the auto-created origin ball is deleted.",
        "",
        "## Provenance",
        "",
        "Found by a polytope-independent raw-column `Z[phi]^3` sweep that enumerates "
        "every strict-orthographic projection whose columns and pairwise column "
        "differences are zometool axes.  R=2 and R=3 saturate at the same three "
        "projection geometries; R=1 finds one of them.  See "
        "[`../../docs/A5_PROJECTIONS.md`](../../docs/A5_PROJECTIONS.md).",
        "",
    ]
    (GAL / "README.md").write_text("\n".join(rl), encoding="utf-8")

    print(f"Wrote {len(ORDER)} viewer pages + VIEWER.md + README.md to {GAL}")


if __name__ == "__main__":
    main()
