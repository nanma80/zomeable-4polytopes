"""Build the curated final Catalan favorite output set."""

from __future__ import annotations

import json
from pathlib import Path

from approx_platonic_zomes import gf_point_json
from postprocess_favorites import (
    center_and_scale,
    emit_vzome_view,
    final_scale_power,
    model_from_manifest,
    points_from_model,
    strut_scales,
)


OUT_DIR = Path("outputs/final/output_catalan_favorites_scaled_centered_20260602")

CATALAN_PICKS = [
    ("pentakis_dodecahedron", "e2b29cc4e0f23804"),
    ("rhombic_dodecahedron", "07f884ed3d7028dd"),
    ("rhombic_triacontahedron", "c7963170a0443a97"),
    ("triakis_icosahedron", "b6bd7be67e62bfc5"),
    ("triakis_tetrahedron", "da82fe133483e246"),
]


def catalan_manifest(target: str) -> Path:
    root = Path("outputs/catalan/output_catalan_batch_20260601")
    return root / target / target / "manifest.json"


def checked_favorite(target: str, expected_hash: str) -> dict:
    manifest = catalan_manifest(target)
    model = model_from_manifest(manifest, 1)
    if model.get("hash") != expected_hash:
        raise ValueError(
            f"{target} rank 1 hash is {model.get('hash')}; expected {expected_hash}"
        )
    return model


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.vZome"):
        old.unlink()

    manifest = {
        "purpose": "Curated favorite Catalan approximations, scaled to strut scales 2..3 and centroid-centered.",
        "scale_rule": "Selected one global phi power per model so every emitted graph strut has scale 2 or 3 when possible.",
        "centering_rule": "After scaling, translated by the exact golden-field centroid; no rotation and no additional scale.",
        "models": [],
    }

    for target, expected_hash in CATALAN_PICKS:
        source_manifest = catalan_manifest(target)
        model = checked_favorite(target, expected_hash)
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
                "source_rank": 1,
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

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"out": str(OUT_DIR), "models": len(manifest["models"])}, indent=2))


if __name__ == "__main__":
    main()
