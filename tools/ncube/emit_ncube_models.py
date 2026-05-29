"""Emit concrete strict zomeable n-cube projection models."""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

from emit_vzome import (  # noqa: E402
    GF,
    ZERO,
    classify_direction,
    emit_vzome_directional,
    vadd,
    vkey,
    vscale,
)

OUT = ROOT / "output" / "ncubes"
NCUBE_WORK = ROOT / "ongoing_work" / "ncube"
SCALE = GF(2, 2)

CURATED_N6_SIGNATURES = {
    "N58_cb02a32360a4",
    "N63_3b1c7b06d29d",
    "N64_0ae3735889e4",
    "N64_1ddb6225f607",
    "N64_1f11e03db897",
    "N64_2b777b0be9ad",
    "N64_3a4cad3346a7",
    "N64_3d3456a501a2",
    "N64_7a0c1b9ac842",
    "N64_7e40e8b0dc89",
}


def gf_inv(x: GF) -> GF:
    a, b = x.a, x.b
    denom = a * a + a * b - b * b
    if denom == 0:
        raise ZeroDivisionError(x)
    return GF(Fraction(a + b, denom), Fraction(-b, denom))


def z_to_gf(x: tuple[int, int]) -> GF:
    return GF(x[0], x[1])


def zjson_to_gfv(v):
    return tuple(z_to_gf(tuple(x)) for x in v)


def dedup_balls(balls):
    uniq = []
    idx = []
    by_key = {}
    for p in balls:
        k = vkey(p)
        if k not in by_key:
            by_key[k] = len(uniq)
            uniq.append(p)
        idx.append(by_key[k])
    return uniq, idx


def gf_cross(u, v):
    return (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )


def gf_dot(u, v):
    out = ZERO
    for a, b in zip(u, v):
        out = out + a * b
    return out


def gf_det(u, v, w):
    return gf_dot(gf_cross(u, v), w)


def essential_general_position(gens) -> bool:
    for i, j, k in itertools.combinations(range(len(gens)), 3):
        if gf_det(gens[i], gens[j], gens[k]) == ZERO:
            return False
    return True


def cleanup_old_models() -> None:
    for folder in OUT.glob("ncube_*"):
        if folder.is_dir():
            for path in folder.glob("*.vZome"):
                path.unlink()


def emit_ncube(gens, path: Path, norm: GF | None = None) -> tuple[int, int, dict]:
    if norm is not None:
        factor = SCALE * gf_inv(norm)
        gens = [vscale(g, factor) for g in gens]

    raw = []
    sign_to_raw_index = {}
    for signs in itertools.product((-1, 1), repeat=len(gens)):
        acc = (ZERO, ZERO, ZERO)
        for sign, gen in zip(signs, gens):
            acc = vadd(acc, vscale(gen, GF(sign)))
        sign_to_raw_index[signs] = len(raw)
        raw.append(acc)

    uniq, idx = dedup_balls(raw)
    edge_set = set()
    for signs, raw_i in sign_to_raw_index.items():
        for axis in range(len(gens)):
            flipped = list(signs)
            flipped[axis] *= -1
            raw_j = sign_to_raw_index[tuple(flipped)]
            a, b = idx[raw_i], idx[raw_j]
            if a != b:
                edge_set.add((min(a, b), max(a, b)))

    edges = sorted(edge_set)
    for i, j in edges:
        if classify_direction(uniq[i], uniq[j]) is None:
            raise RuntimeError(f"{path.name}: edge {i}-{j} is not parallel to a zome axis")
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = emit_vzome_directional(uniq, edges, path)
    return len(uniq), len(edges), counts


def latest_sweep_path(n: int) -> Path | None:
    paths = [
        p for p in NCUBE_WORK.glob(f"column_sweep_ncube{n}_R*.json")
        if not p.name.endswith(".progress.json")
    ]
    paths.sort(key=lambda p: int(p.stem.rsplit("_R", 1)[1]))
    return paths[-1] if paths else None


def load_essential_sweep_records(n: int) -> list[dict]:
    path = latest_sweep_path(n)
    if path is None:
        return []
    records = json.loads(path.read_text(encoding="utf-8"))["records"]
    records = [r for r in records if r["essential_general_position"]]
    if n == 6:
        records = [r for r in records if r["shape_sig"] in CURATED_N6_SIGNATURES]
    return records


def emit_sweep_record(n: int, record: dict) -> tuple[str, int, int, dict]:
    gens = [zjson_to_gfv(v) for v in record["generators_zphi"]]
    if not essential_general_position(gens):
        raise RuntimeError(f"{record['shape_sig']} failed the essential general-position check")
    label = record["taxonomy_label"].replace("/", "_")
    name = f"ncube_{n}_{label}_{record['shape_sig']}.vZome"
    balls, edges, counts = emit_ncube(gens, OUT / f"ncube_{n}" / name)
    return name, balls, edges, counts


def emit_c6_icosahedral_axes() -> tuple[str, int, int, dict] | None:
    phi = GF(0, 1)
    gens = [
        (GF(-2, -2), GF(0), GF(0)),
        (GF(0), GF(0), GF(-2, -2)),
        (GF(-1, -1), GF(-1, -2), -phi),
        (GF(0), GF(-2, -2), GF(0)),
        (-phi, GF(1, 1), GF(-1, -2)),
        (GF(-1, -2), phi, GF(1, 1)),
    ]
    if not essential_general_position(gens):
        return None
    name = "ncube_6_six_blue_axes_sporadic.vZome"
    balls, edges, counts = emit_ncube(gens, OUT / "ncube_6" / name)
    counts = {**counts, "family": "primitive sporadic"}
    return name, balls, edges, counts


def write_readme(summary: dict[int, list[tuple[str, int, int, dict]]]) -> None:
    lines = [
        "# Strict zomeable n-cube projection models",
        "",
        "These folders contain concrete `.vZome` models for strict zomeable",
        "orthographic projections of n-cubes that also satisfy the essential",
        "general-position filter: every projected generator triplet spans 3D.",
        "",
        "| n | emitted models | notes |",
        "|---:|:---|:---|",
    ]
    notes = {
        3: "baseline cube",
        4: "all latest-bound essential sweep representatives",
        5: "no latest-bound essential representatives found",
        6: "curated subset of latest-bound essential sweep representatives",
        7: "R=2 sweep stopped before completion; no catalog models retained",
    }
    for n in sorted(summary):
        names = "<br>".join(f"`{name}`" for name, _, _, _ in summary[n]) or "none"
        lines.append(f"| {n} | {names} | {notes[n]} |")
    lines.extend([
        "",
        "The essential filter is the exact condition",
        "",
        "```text",
        "rank(v_i, v_j, v_k) = 3 for every distinct triple i,j,k.",
        "```",
        "",
        "The sweep-backed entries come from exact bounded generator sweeps. This",
        "is not a completeness proof beyond the recorded bounds.",
        "",
        "For n=6, the R=2 sweep found 46 strict signatures, but this directory",
        "keeps only the 10 models retained after visual spot-checking. The larger",
        "strict sweep direction was abandoned because it produced too many",
        "seemingly arbitrary models even under the general-position filter.",
        "",
        "Regenerate with:",
        "",
        "```powershell",
        "python tools\\ncube\\emit_ncube_models.py",
        "```",
        "",
    ])
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")

    for n, rows in summary.items():
        (OUT / f"ncube_{n}").mkdir(parents=True, exist_ok=True)
        per = [
            f"# n-cube models: n={n}",
            "",
            "| file | balls | struts | direction counts |",
            "|:---|---:|---:|:---|",
        ]
        for name, balls, edges, counts in rows:
            b = "" if balls < 0 else str(balls)
            e = "" if edges < 0 else str(edges)
            if counts.get("source"):
                c = f"copied from `{counts['source']}`"
            else:
                c = "`" + repr(counts) + "`"
            per.append(f"| `{name}` | {b} | {e} | {c} |")
        if not rows:
            per.append("| none |  |  |  |")
        per.append("")
        (OUT / f"ncube_{n}" / "README.md").write_text("\n".join(per), encoding="utf-8")


def main() -> None:
    summary: dict[int, list[tuple[str, int, int, dict]]] = {3: [], 4: [], 5: [], 6: [], 7: []}
    cleanup_old_models()

    cube = [
        (GF(1), GF(0), GF(0)),
        (GF(0), GF(1), GF(0)),
        (GF(0), GF(0), GF(1)),
    ]
    summary[3].append(("ncube_3_cube.vZome", *emit_ncube(cube, OUT / "ncube_3" / "ncube_3_cube.vZome", norm=GF(1))))

    for n in (4, 5, 6, 7):
        for record in load_essential_sweep_records(n):
            summary[n].append(emit_sweep_record(n, record))

    if not summary[6]:
        c6 = emit_c6_icosahedral_axes()
        if c6 is not None:
            summary[6].append(c6)

    write_readme(summary)
    for n in sorted(summary):
        print(f"n={n}")
        for name, balls, edges, counts in summary[n]:
            detail = "copied" if balls < 0 else f"{balls} balls, {edges} struts, {counts}"
            print(f"  {name}: {detail}")


if __name__ == "__main__":
    main()
