"""Build the curated final Platonic/Archimedean favorite output set."""

from __future__ import annotations

import json
import math
import re
from fractions import Fraction
from pathlib import Path

from approx_platonic_zomes import (
    GF,
    PHI,
    classify_strut,
    gf_dist2_float,
    gf_point_json,
    phi_pow,
    vadd,
    vscale,
)
from emit_vzome import HEADER, pt_str


OUT_DIR = Path("outputs/final/output_favorites_scaled_centered_20260601")

PLATONIC_PICKS = [
    ("tetrahedron", Path("outputs/platonic/output_final/tetrahedron/manifest.json"), 1),
    ("cube", Path("outputs/platonic/output_cube_B1_4seeds_ratio15_angle25_24h_20260530/cube/manifest.json"), 1),
    ("octahedron", Path("outputs/platonic/output_scratch_long_B1_4seeds_ratio16_20260529/octahedron/manifest.json"), 1),
    ("icosahedron", Path("outputs/platonic/output_icosa_B1_4seeds_ratio15_angle25_24h_20260530/icosahedron/manifest.json"), 1),
    ("dodecahedron", Path("outputs/platonic/output_dodeca_B1_4seeds_ratio12_angle15_faceclose_24h_20260531/dodecahedron/manifest.json"), 2),
]

ARCHIMEDEAN_TARGETS = [
    "truncated_tetrahedron",
    "cuboctahedron",
    "truncated_cube",
    "truncated_octahedron",
    "rhombicuboctahedron",
    "icosidodecahedron",
    "truncated_cuboctahedron",
    "truncated_dodecahedron",
    "rhombicosidodecahedron",
    "truncated_icosidodecahedron",
]


def model_from_manifest(path: Path, rank: int) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    models = data["models"]
    if len(models) < rank:
        raise ValueError(f"{path} has only {len(models)} models; cannot select rank {rank}")
    return models[rank - 1]


def gf_from_json(coord: list[str]) -> GF:
    return GF(Fraction(coord[0]), Fraction(coord[1]))


def points_from_model(model: dict):
    return [tuple(gf_from_json(coord) for coord in vertex) for vertex in model["vertices_golden"]]


def strut_scales(counts: dict[str, int]) -> list[int]:
    scales = []
    for label in counts:
        match = re.fullmatch(r"[BRGY](-?\d+)", label)
        if not match:
            raise ValueError(f"Cannot parse strut label {label!r}")
        scales.append(int(match.group(1)))
    return scales


def final_scale_power(model: dict) -> int:
    scales = strut_scales(model["struts"]["counts"])
    lo, hi = min(scales), max(scales)
    if hi - lo > 1:
        raise ValueError(f"{model['target']} has strut scales {lo}..{hi}; cannot fit all into 2..3")
    return 2 - lo


def centroid(points):
    n = len(points)
    return tuple(
        sum((point[axis] for point in points), GF(0)) * Fraction(1, n)
        for axis in range(3)
    )


def center_and_scale(points, scale_power: int):
    scale = phi_pow(scale_power)
    scaled = [vscale(point, scale) for point in points]
    c = centroid(scaled)
    return [tuple(point[axis] - c[axis] for axis in range(3)) for point in scaled], c


def radius(points) -> float:
    return max(math.sqrt(gf_dist2_float(point)) for point in points)


def emit_vzome_view(verts, edges, path: Path) -> dict[str, int]:
    audit = []
    for i, j in edges:
        c = classify_strut(verts[i], verts[j])
        if c is None:
            raise ValueError(f"Non-standard strut {i}->{j}: {pt_str(verts[i])} -> {pt_str(verts[j])}")
        audit.append(c)

    r = radius(verts)
    width = max(8.0, 3.8 * r)
    distance = max(18.0, 2.6 * width)
    far = max(200.0, 8.0 * distance)
    near = max(0.05, distance / 400.0)

    cmds = [f'    <ShowPoint point="{pt_str(v)}"/>' for v in verts]
    cmds += [
        f'    <JoinPointPair start="{pt_str(verts[i])}" end="{pt_str(verts[j])}"/>'
        for i, j in edges
    ]
    origin_str = "0 0 0 0 0 0"
    if not any(pt_str(v) == origin_str for v in verts):
        cmds.append(f'    <SelectManifestation point="{origin_str}"/>')
        cmds.append("    <Delete/>")

    footer = f'''  <notes/>
  <sceneModel ambientLight="41,41,41" background="175,200,220">
    <directionalLight color="235,235,228" x="1.0" y="-1.0" z="-1.0"/>
    <directionalLight color="228,228,235" x="-1.0" y="0.0" z="0.0"/>
    <directionalLight color="30,30,30" x="0.0" y="0.0" z="-1.0"/>
  </sceneModel>
  <Viewing>
    <ViewModel distance="{distance:.6g}" far="{far:.6g}" near="{near:.6g}" parallel="false" stereoAngle="0.0" width="{width:.6g}">
      <LookAtPoint x="0.0" y="0.0" z="0.0"/>
      <UpDirection x="0.0" y="1.0" z="0.0"/>
      <LookDirection x="-0.45" y="-0.35" z="-1.0"/>
    </ViewModel>
  </Viewing>
  <SymmetrySystem name="icosahedral" renderingStyle="solid connectors">
    <Direction color="0,142,194"  name="blue"   orbit="[[0,0,1],[0,0,1]]"/>
    <Direction color="0,153,63"   name="green"  orbit="[[2,-1,1],[5,-3,1]]"/>
    <Direction color="217,18,24"  name="red"    orbit="[[-1,1,1],[0,0,1]]"/>
    <Direction color="255,179,26" name="yellow" orbit="[[0,0,1],[2,-1,1]]"/>
  </SymmetrySystem>
  <OtherSymmetries/>
  <Tools/>
</vzome:vZome>
'''

    xml = HEADER
    xml += f'  <EditHistory editNumber="{len(cmds)}" lastStickyEdit="-1">\n'
    xml += "\n".join(cmds) + "\n"
    xml += "  </EditHistory>\n" + footer
    path.write_text(xml, encoding="utf-8")

    counts: dict[str, int] = {}
    for color, scale in audit:
        label = f"{color}{scale}"
        counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items()))


def archimedean_picks():
    root = Path("outputs/archimedean/output_archimedean_batch_20260531")
    for target in ARCHIMEDEAN_TARGETS:
        manifest = root / target / target / "manifest.json"
        if not manifest.exists():
            continue
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data["models"]:
            yield target, manifest, 1


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.vZome"):
        old.unlink()

    picks = PLATONIC_PICKS + list(archimedean_picks())
    manifest = {
        "purpose": "Curated favorite Platonic and solved Archimedean approximations, scaled to strut scales 2..3 and centroid-centered.",
        "scale_rule": "Selected one global phi power per model so every emitted graph strut has scale 2 or 3.",
        "centering_rule": "After scaling, translated by the exact golden-field centroid; no rotation and no additional scale.",
        "models": [],
    }

    for target, source_manifest, rank in picks:
        model = model_from_manifest(source_manifest, rank)
        scale_power = final_scale_power(model)
        raw_points = points_from_model(model)
        final_points, removed_centroid = center_and_scale(raw_points, scale_power)
        filename = f"{target}_favorite.vZome"
        final_counts = emit_vzome_view(final_points, model["edges"], OUT_DIR / filename)
        scales = strut_scales(final_counts)
        if min(scales) < 2 or max(scales) > 3:
            raise ValueError(f"{target} emitted counts outside scale 2..3: {final_counts}")
        manifest["models"].append(
            {
                "target": target,
                "file": filename,
                "source_manifest": str(source_manifest),
                "source_file": model.get("file"),
                "source_rank": rank,
                "source_hash": model.get("hash"),
                "objective": model.get("objective"),
                "applied_phi_scale_power": scale_power,
                "removed_centroid_after_scaling": gf_point_json(removed_centroid),
                "final_struts": final_counts,
                "balls": len(final_points),
                "edges": len(model["edges"]),
                "score": model.get("score"),
            }
        )

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(OUT_DIR), "models": len(manifest["models"])}, indent=2))


if __name__ == "__main__":
    main()
