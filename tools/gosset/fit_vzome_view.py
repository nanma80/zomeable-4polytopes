"""Fit the vZome ViewModel to the model bounds.

Copies .vZome files from --src to --dst, replacing the <Viewing> block with
a per-file view centered on the point-cloud bounding box and zoomed so the
model fits comfortably in the initial view.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from fractions import Fraction
from pathlib import Path


PHI = (1 + 5 ** 0.5) / 2


def parse_num(tok: str) -> float:
    return float(Fraction(tok))


def parse_point(s: str) -> tuple[float, float, float]:
    toks = s.split()
    nums = [parse_num(t) for t in toks]
    return (
        nums[0] + nums[1] * PHI,
        nums[2] + nums[3] * PHI,
        nums[4] + nums[5] * PHI,
    )


def bounds(points):
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    center = [(mins[i] + maxs[i]) / 2 for i in range(3)]
    radius = max(math.sqrt(sum((p[i] - center[i]) ** 2 for i in range(3))) for p in points)
    spans = [maxs[i] - mins[i] for i in range(3)]
    return mins, maxs, center, radius, spans


VIEW_RE = re.compile(r"\s*<Viewing>.*?</Viewing>\n", re.DOTALL)


def view_block(center, radius, margin: float) -> str:
    width = max(1.0, 2 * radius * margin)
    distance = max(width, 4 * radius)
    near = max(0.1, distance - 2.5 * radius)
    far = max(distance + 4 * radius, 4 * width)
    return (
        "  <Viewing>\n"
        f'    <ViewModel distance="{distance:.6f}" far="{far:.6f}" near="{near:.6f}" '
        f'parallel="false" stereoAngle="0.0" width="{width:.6f}">\n'
        f'      <LookAtPoint x="{center[0]:.6f}" y="{center[1]:.6f}" z="{center[2]:.6f}"/>\n'
        '      <UpDirection x="0.0" y="1.0" z="0.0"/>\n'
        '      <LookDirection x="0.0" y="0.0" z="-1.0"/>\n'
        "    </ViewModel>\n"
        "  </Viewing>\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    ap.add_argument("--margin", type=float, default=1.25)
    args = ap.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)

    manifest = {
        "source": str(src),
        "view_fit": {
            "margin": args.margin,
            "width_formula": "2 * bounding_sphere_radius * margin",
            "distance_formula": "max(width, 4 * radius)",
            "look_direction": [0, 0, -1],
            "up_direction": [0, 1, 0],
        },
        "files": [],
    }

    for in_file in sorted(src.glob("*.vZome")):
        text = in_file.read_text(encoding="utf-8")
        pts = [parse_point(m.group(1)) for m in re.finditer(r'<ShowPoint\s+point="([^"]+)"', text)]
        if not pts:
            raise ValueError(f"No ShowPoint records in {in_file}")
        mins, maxs, center, radius, spans = bounds(pts)
        block = view_block(center, radius, args.margin)
        if VIEW_RE.search(text):
            text = VIEW_RE.sub("\n" + block, text, count=1)
        else:
            text = text.replace("  <SymmetrySystem", block + "  <SymmetrySystem", 1)
        out_file = dst / in_file.name
        out_file.write_text(text, encoding="utf-8")
        manifest["files"].append({
            "source": str(in_file),
            "output": str(out_file),
            "N": len(pts),
            "center": center,
            "spans": spans,
            "radius": radius,
            "width": max(1.0, 2 * radius * args.margin),
            "distance": max(max(1.0, 2 * radius * args.margin), 4 * radius),
        })

    for name in ("scale_manifest.json", "source_manifest.json", "manifest.json"):
        if (src / name).exists():
            shutil.copy2(src / name, dst / name)
    (dst / "view_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Fitted view for {len(manifest['files'])} files")
    print(f"Wrote {dst}")


if __name__ == "__main__":
    main()
