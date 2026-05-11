"""Auto-fit the camera frustum in every output/**/*.vZome so models open at a
sensible zoom in both the vzome-viewer web embed and vZome desktop.

The two clients compute FOV differently:

  - vZome desktop:   FOV = 2 * atan( (width / 2) / distance )    (Camera.java:142)
    Uses both width and distance from the file directly.

  - vzome-viewer (web): the file's width is OVERRIDDEN by the viewer's
    hardcoded WIDTH_FACTOR = 0.45  (online/src/viewer/context/camera.jsx:11);
    width is effectively `distance * 0.45`.  So FOV = 2*atan(0.45/2) ~= 25.4
    degrees, fixed, and only the file's `distance` attribute affects how
    much of the scene is visible.

The web embed has the narrower FOV, so distance must be chosen to fit
the model there; the desktop FOV will then be wider (looser fit) which
is fine.

For radius r, we need:
    r  <=  (WIDTH_FACTOR / 2) * distance * FILL_FACTOR
    distance  >=  2 * r / (WIDTH_FACTOR * FILL_FACTOR)  ~= 5.23 * r at 85% fill

The file's `width` is set to `distance` (so vZome desktop opens at its
default ~53 degree FOV).

LookAtPoint is at the origin in every file in this repo, so radius is
measured as max(|P|) over <ShowPoint> elements.

The script is idempotent: re-running computes attributes from coordinates,
not from previous attribute values.
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

# Hardcoded in online/src/viewer/context/camera.jsx (WIDTH_FACTOR).
VIEWER_WIDTH_FACTOR = 0.45
# Fraction of half-frustum the model should occupy (15% margin).
FILL_FACTOR = 0.85
DEFAULT_DISTANCE = 50.0
DEFAULT_FAR = 200.0
DEFAULT_NEAR = 0.5


def compute_radius(path: Path) -> float | None:
    """Return max |P| over all ShowPoints, or None if the file has no balls."""
    P, _E = parse_vzome(path)
    if P.shape[0] == 0:
        return None
    return float(np.linalg.norm(P, axis=1).max())


def round_nice(x: float, step: float = 10.0) -> float:
    return math.ceil(x / step) * step


def new_attrs(radius: float) -> tuple[float, float, float, float]:
    # Distance needed so radius r fits within FILL_FACTOR of the viewer's
    # half-frustum (viewer width = distance * VIEWER_WIDTH_FACTOR).
    needed_distance = 2.0 * radius / (VIEWER_WIDTH_FACTOR * FILL_FACTOR)
    distance = max(DEFAULT_DISTANCE, round_nice(needed_distance, 10.0))
    # vZome desktop reads `width` directly and computes FOV from width/distance;
    # width == distance gives the default ~53-degree desktop FOV.
    width = distance
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
