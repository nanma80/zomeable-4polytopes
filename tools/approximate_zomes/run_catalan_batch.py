"""Batch runner for approximate Catalan zome searches."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


CATALAN_TARGETS = [
    "triakis_tetrahedron",
    "rhombic_dodecahedron",
    "triakis_octahedron",
    "tetrakis_hexahedron",
    "deltoidal_icositetrahedron",
    "disdyakis_dodecahedron",
    "pentagonal_icositetrahedron",
    "rhombic_triacontahedron",
    "triakis_icosahedron",
    "pentakis_dodecahedron",
    "deltoidal_hexecontahedron",
    "disdyakis_triacontahedron",
    "pentagonal_hexecontahedron",
]


def branch_cap_for(target: str) -> int:
    if target in {"disdyakis_triacontahedron", "pentagonal_hexecontahedron"}:
        return 64
    if target in {
        "disdyakis_dodecahedron",
        "pentagonal_icositetrahedron",
        "triakis_icosahedron",
        "pentakis_dodecahedron",
        "deltoidal_hexecontahedron",
    }:
        return 128
    return 320


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_target(out_dir: Path, target: str) -> dict:
    target_dir = out_dir / target
    progress = read_json(target_dir / "progress.json") or {}
    manifest = read_json(target_dir / "manifest.json") or {}
    models = manifest.get("models", [])
    best = models[0] if models else None
    return {
        "target": target,
        "phase": progress.get("phase"),
        "elapsed_sec": progress.get("elapsed_sec"),
        "nodes": progress.get("nodes"),
        "completed": progress.get("completed"),
        "kept": progress.get("kept"),
        "emitted": progress.get("emitted", len(models)),
        "best_objective": best.get("objective") if best else None,
        "best_file": best.get("file") if best else None,
        "best_struts": best.get("struts", {}).get("counts", {}) if best else {},
    }


def write_batch_manifest(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", nargs="+", default=CATALAN_TARGETS)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seconds-per-target", type=float, default=4 * 3600)
    parser.add_argument("--keep", type=int, default=120)
    parser.add_argument("--min-scale", type=int, default=-3)
    parser.add_argument("--max-scale", type=int, default=2)
    parser.add_argument("--coord-bound", type=float, default=44.0)
    parser.add_argument("--candidate-error-limit", type=float, default=1.35)
    parser.add_argument("--seed-scale", type=int, default=1)
    parser.add_argument("--seed-edge-ratio-limit", type=float, default=1.2)
    parser.add_argument("--edge-length-ratio-limit", type=float, default=1.2)
    parser.add_argument("--edge-angle-tolerance-deg", type=float, default=15.0)
    parser.add_argument("--progress-interval-sec", type=float, default=300.0)
    parser.add_argument("--emit-scale-power", type=int, default=2)
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_root = args.out or script_dir / "outputs" / "catalan" / f"output_catalan_batch_{stamp}"
    out_root.mkdir(parents=True, exist_ok=True)
    log_dir = out_root / "_logs"
    log_dir.mkdir(exist_ok=True)

    batch = {
        "purpose": "Automated Catalan approximate zome searches.",
        "note": "Uses Archimedean criteria with ideal-edge-aware scoring and max-edge-struts fixed at 1.",
        "started": datetime.now().isoformat(timespec="seconds"),
        "params": vars(args) | {"out": str(out_root), "max_edge_struts": 1},
        "targets": [],
    }
    manifest_path = out_root / "batch_manifest.json"
    write_batch_manifest(manifest_path, batch)

    for target in args.targets:
        branch_cap = branch_cap_for(target)
        target_out = out_root / target
        command = [
            sys.executable,
            "approx_platonic_zomes.py",
            "--search",
            "--targets",
            target,
            "--no-exact-fallback",
            "--allow-rough-scratch",
            "--seconds-per-target",
            str(args.seconds_per_target),
            "--keep",
            str(args.keep),
            "--min-scale",
            str(args.min_scale),
            "--max-scale",
            str(args.max_scale),
            "--coord-bound",
            str(args.coord_bound),
            "--branch-cap",
            str(branch_cap),
            "--max-initial-edges",
            "800",
            "--candidate-error-limit",
            str(args.candidate_error_limit),
            "--seed-scale",
            str(args.seed_scale),
            "--one-seed-per-color",
            "--seed-edge-ratio-limit",
            str(args.seed_edge_ratio_limit),
            "--edge-length-ratio-limit",
            str(args.edge_length_ratio_limit),
            "--edge-angle-tolerance-deg",
            str(args.edge_angle_tolerance_deg),
            "--progress-interval-sec",
            str(args.progress_interval_sec),
            "--emit-scale-power",
            str(args.emit_scale_power),
            "--out",
            str(target_out),
        ]
        entry = {
            "target": target,
            "status": "running",
            "started": datetime.now().isoformat(timespec="seconds"),
            "out": str(target_out),
            "branch_cap": branch_cap,
            "command": command,
        }
        batch["targets"].append(entry)
        write_batch_manifest(manifest_path, batch)

        started = time.time()
        with (log_dir / f"{target}.log").open("w", encoding="utf-8") as stdout, (
            log_dir / f"{target}.err.log"
        ).open("w", encoding="utf-8") as stderr:
            completed = subprocess.run(command, cwd=script_dir, stdout=stdout, stderr=stderr, check=False)

        entry.update(
            {
                "status": "done" if completed.returncode == 0 else "failed",
                "returncode": completed.returncode,
                "elapsed_wall_sec": time.time() - started,
                "finished": datetime.now().isoformat(timespec="seconds"),
                "summary": summarize_target(target_out, target),
            }
        )
        write_batch_manifest(manifest_path, batch)

    batch["finished"] = datetime.now().isoformat(timespec="seconds")
    write_batch_manifest(manifest_path, batch)


if __name__ == "__main__":
    main()
