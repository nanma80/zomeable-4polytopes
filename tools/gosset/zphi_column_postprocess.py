"""Post-process zphi_column_sweep hits.

Loads column_sweep_R*.json, reconstructs each representative projection,
computes a full scale-invariant distance-multiset signature, and compares
against curated_ortho_shapes/*.vZome.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

spec = importlib.util.spec_from_file_location("col", TOOLS / "zphi_column_sweep.py")
col = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(col)

PHI = (1 + 5 ** 0.5) / 2


def full_dist_sig(V3, decimals: int = 5) -> str:
    V = np.asarray(V3, dtype=float)
    V = V - V.mean(axis=0)
    # Collapse coincident projected vertices at high precision, but do not use
    # the display/signature precision before scale normalization.
    pts = sorted({tuple(np.round(p, 12)) for p in V})
    arr = np.asarray(pts, dtype=float)
    n = len(arr)
    if n < 2:
        return f"N{n}_empty"
    d = arr[:, None, :] - arr[None, :, :]
    d2 = (d * d).sum(axis=-1)
    vals = d2[np.triu_indices(n, k=1)]
    nz = vals[vals > 1e-10]
    if len(nz) == 0:
        return f"N{n}_degenerate"
    vals = np.round(vals / float(nz.min()), decimals)
    vals.sort()
    payload = ",".join(f"{x:.{decimals}f}" for x in vals)
    return f"N{n}_" + hashlib.sha1(payload.encode()).hexdigest()[:16]


def parse_num(tok: str) -> float:
    return float(Fraction(tok))


def parse_point(s: str) -> tuple[float, float, float]:
    toks = s.strip().split()
    if len(toks) != 6:
        raise ValueError(f"expected 6 golden coords, got {len(toks)}: {s}")
    nums = [parse_num(t) for t in toks]
    return (
        nums[0] + nums[1] * PHI,
        nums[2] + nums[3] * PHI,
        nums[4] + nums[5] * PHI,
    )


def parse_vzome_points(path: Path) -> np.ndarray:
    txt = path.read_text(encoding="utf-8")
    pts = []
    seen = set()
    for m in re.finditer(r"<ShowPoint\s+point\s*=\s*['\"]([^'\"]+)['\"]", txt):
        p = parse_point(m.group(1))
        key = tuple(round(x, 12) for x in p)
        if key not in seen:
            seen.add(key)
            pts.append(p)
    return np.array(pts, dtype=float)


def columns_to_P(columns) -> np.ndarray:
    chosen = [
        tuple(tuple(int(x) for x in z) for z in c)
        for c in columns
    ]
    g = col.ZERO_GRAM
    for c in chosen:
        g = col.gram_add(g, col.outer_gram(c))
    return col.matrix_from_columns(chosen, g)


def hit_V3(poly: str, info: dict) -> np.ndarray:
    P = columns_to_P(info["columns"])
    embs = col.embeddings()[poly]
    emb_id = info["embedding"]
    for V, E, eid in embs:
        if eid == emb_id:
            return V @ P.T
    raise KeyError((poly, emb_id))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="ongoing_work/zphi_column_sweep/column_sweep_R2.json")
    ap.add_argument("--curated", default="curated_ortho_shapes")
    ap.add_argument("--out", default="ongoing_work/zphi_column_sweep_postprocess.json")
    args = ap.parse_args()

    d = json.loads((ROOT / args.json).read_text())

    curated = {"2_21": {}, "3_21": {}, "4_21": {}}
    for f in sorted((ROOT / args.curated).glob("*.vZome")):
        poly = next((p for p in curated if f.name.startswith(p + "_")), None)
        if poly is None:
            continue
        pts = parse_vzome_points(f)
        sig = full_dist_sig(pts)
        curated[poly].setdefault(sig, []).append(f.name)

    found = {"2_21": {}, "3_21": {}, "4_21": {}}
    for poly, hits in d["hits"].items():
        for raw_sig, info in hits.items():
            V3 = hit_V3(poly, info)
            sig = full_dist_sig(V3)
            found[poly].setdefault(sig, []).append({
                "raw_sig": raw_sig,
                "N": info["N"],
                "embedding": info["embedding"],
            })

    report = {
        "source": args.json,
        "sweep_status": d.get("status"),
        "sweep_elapsed_s": d.get("elapsed_s"),
        "stats": d.get("stats"),
        "curated": curated,
        "found": found,
        "coverage": {},
    }

    for poly in ("2_21", "3_21", "4_21"):
        covered = sorted(set(curated[poly]) & set(found[poly]))
        missing = sorted(set(curated[poly]) - set(found[poly]))
        extra = sorted(set(found[poly]) - set(curated[poly]))
        report["coverage"][poly] = {
            "covered": covered,
            "missing": missing,
            "extra": extra,
            "covered_files": {s: curated[poly][s] for s in covered},
            "extra_hits": {s: found[poly][s] for s in extra},
        }

    (ROOT / args.out).write_text(json.dumps(report, indent=2))

    print(f"Sweep status: {d.get('status')} elapsed_s={d.get('elapsed_s'):.1f}")
    print(f"Stats: {d.get('stats')}")
    for poly in ("2_21", "3_21", "4_21"):
        cov = report["coverage"][poly]
        print()
        print(f"{poly}: curated={len(curated[poly])} found={len(found[poly])} "
              f"covered={len(cov['covered'])} missing={len(cov['missing'])} extra={len(cov['extra'])}")
        for s in cov["covered"]:
            print(f"  HIT   {s}: {curated[poly][s]}")
        for s in cov["missing"]:
            print(f"  MISS  {s}: {curated[poly][s]}")
        for s in cov["extra"]:
            labels = [f"{h['raw_sig']}@{h['embedding']}" for h in found[poly][s]]
            print(f"  EXTRA {s}: {labels}")
    print(f"\nWrote {ROOT / args.out}")


if __name__ == "__main__":
    main()
