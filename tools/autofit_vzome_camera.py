"""Auto-fit the camera frustum in every output/**/*.vZome so models open at a
sensible zoom in the vzome-viewer embed (and in vZome desktop).

vZome's camera FOV is derived from the ViewModel attributes:

    FOV = 2 * atan( (width / 2) / distance )       (Camera.java:142)

The frustum width at the look-at plane is exactly `width`.  So for the model
to fit, we need `width >= 2 * radius`, where `radius` is the bounding-sphere
radius around the origin (LookAtPoint is at the origin in all our files).

Default is `distance=50, width=50` -> FOV ~= 53.13 degrees, fits radius ~= 25.
Models with radius > 25 (e.g. 120-cell projections) get clipped/zoomed in.
We rescale `width` and `distance` together to preserve the 53-degree FOV
while making the frustum just large enough to contain the model with a
small margin.

The script is idempotent: re-running on the same file produces the same
attributes (computed from ball coordinates, not from previous attribute
values).
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np

from tools.dedup_corpus_by_shape import parse_vzome  # type: ignore

OUTPUT = ROOT / "output"

VIEW_MODEL_RE = re.compile(
    r'(<ViewModel\s+)'              # 1: opening
    r'distance="[^"]*"\s+'
    r'far="[^"]*"\s+'
    r'near="[^"]*"\s+'
    r'(parallel="[^"]*"\s+'         # 2: parallel attr (preserved)
    r'stereoAngle="[^"]*"\s+)'
    r'width="[^"]*"'
    r'(\s*>)'                       # 3: closing
)

# Margin between model and frustum edge: model occupies 80% of the view.
FILL_FACTOR = 0.80
DEFAULT_WIDTH = 50.0
DEFAULT_FAR = 200.0
DEFAULT_NEAR = 0.5


def compute_radius(path: Path) -> float | None:
    """Return max distance from origin of any ShowPoint in the file, or None
    if there are no balls (no <ShowPoint> elements)."""
    P, _E = parse_vzome(path)
    if P.shape[0] == 0:
        return None
    return float(np.linalg.norm(P, axis=1).max())


def round_nice(x: float, step: float = 5.0) -> float:
    """Round up to the next multiple of `step` for tidy attribute values."""
    return math.ceil(x / step) * step


def new_attrs(radius: float) -> tuple[float, float, float, float]:
    needed_width = 2.0 * radius / FILL_FACTOR
    width = max(DEFAULT_WIDTH, round_nice(needed_width, 5.0))
    distance = width
    far = max(DEFAULT_FAR, round_nice(distance + 2.0 * radius, 10.0))
    near = DEFAULT_NEAR
    return distance, far, near, width


def process(path: Path) -> str:
    radius = compute_radius(path)
    if radius is None:
        return "no-balls"
    distance, far, near, width = new_attrs(radius)
    text = path.read_text(encoding="utf-8")
    m = VIEW_MODEL_RE.search(text)
    if not m:
        return "no-viewmodel"
    new_view_model = (
        f'{m.group(1)}'
        f'distance="{distance:.1f}" far="{far:.1f}" near="{near:.1f}" '
        f'{m.group(2)}'
        f'width="{width:.1f}"'
        f'{m.group(3)}'
    )
    new_text = text[: m.start()] + new_view_model + text[m.end() :]
    if new_text == text:
        return f"unchanged (r={radius:.2f}, w={width:.0f}, d={distance:.0f})"
    path.write_text(new_text, encoding="utf-8")
    return f"updated  (r={radius:.2f}, w={width:.0f}, d={distance:.0f}, far={far:.0f})"


def main() -> None:
    files = sorted(OUTPUT.rglob("*.vZome"))
    width_max = 32
    name_max = max(len(f.relative_to(ROOT).as_posix()) for f in files)
    name_max = min(name_max, 60)
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        status = process(path)
        print(f"{rel:<{name_max}}  {status}")


if __name__ == "__main__":
    main()
