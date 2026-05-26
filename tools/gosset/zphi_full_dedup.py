"""Full Euclidean-similarity dedup for emitted/curated vZome point clouds.

Dedup criterion:
  - parse all ShowPoint coordinates,
  - center the point cloud,
  - normalize by shortest nonzero pairwise distance,
  - compare the complete sorted pairwise squared-distance multiset.

This is invariant under translation, rotation, reflection, uniform scale, and
point ordering.  If two shapes have different spectra, they cannot be the same
under any Euclidean rotation/reflection/scale.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PHI = (1 + 5 ** 0.5) / 2


def parse_num(tok: str) -> float:
    return float(Fraction(tok))


def parse_point(s: str) -> tuple[float, float, float]:
    toks = s.strip().split()
    if len(toks) != 6:
        raise ValueError(f"Expected 6 golden-coordinate tokens, got {len(toks)}: {s!r}")
    nums = [parse_num(t) for t in toks]
    return (
        nums[0] + nums[1] * PHI,
        nums[2] + nums[3] * PHI,
        nums[4] + nums[5] * PHI,
    )


def parse_vzome(path: Path) -> np.ndarray:
    text = path.read_text(encoding="utf-8")
    pts = []
    seen = set()
    for m in re.finditer(r"<ShowPoint\s+point\s*=\s*['\"]([^'\"]+)['\"]", text):
        p = parse_point(m.group(1))
        key = tuple(round(x, 12) for x in p)
        if key in seen:
            continue
        seen.add(key)
        pts.append(p)
    if not pts:
        raise ValueError(f"No ShowPoint records parsed from {path}")
    return np.asarray(pts, dtype=float)


def infer_poly(path: Path) -> str:
    m = re.match(r"([234]_21)_", path.name)
    if not m:
        return "unknown"
    return m.group(1)


def spectrum(V: np.ndarray, decimals: int = 8) -> tuple[int, tuple[float, ...]]:
    V = V - V.mean(axis=0)
    # Do NOT round coordinates before scale normalization.  Some equivalent
    # models differ by a phi scale; pre-normalization rounding can split them.
    # parse_vzome() already removes duplicate ShowPoint records.
    A = np.asarray(V, dtype=float)
    n = len(A)
    if n < 2:
        return n, tuple()
    D = A[:, None, :] - A[None, :, :]
    d2 = (D * D).sum(axis=-1)
    vals = d2[np.triu_indices(n, k=1)]
    nz = vals[vals > 1e-12]
    if len(nz) == 0:
        return n, tuple()
    vals = np.round(vals / float(nz.min()), decimals)
    vals.sort()
    return n, tuple(float(x) for x in vals)


def sig_from_spectrum(n: int, spec: tuple[float, ...]) -> str:
    payload = ",".join(f"{x:.8f}" for x in spec)
    return f"N{n}_" + hashlib.sha1(payload.encode()).hexdigest()[:16]


def summarize(paths: list[Path], source: str):
    out = []
    for p in paths:
        V = parse_vzome(p)
        n, spec = spectrum(V)
        sig = sig_from_spectrum(n, spec)
        out.append({
            "source": source,
            "poly": infer_poly(p),
            "file": str(p.relative_to(ROOT)),
            "name": p.name,
            "N": n,
            "sig": sig,
            "spectrum_len": len(spec),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emitted", default="output/column_sweep_R2")
    ap.add_argument("--curated", default="curated_ortho_shapes")
    ap.add_argument("--out", default="ongoing_work/zphi_column_full_dedup.json")
    args = ap.parse_args()

    emitted_paths = sorted((ROOT / args.emitted).glob("*.vZome"))
    curated_paths = sorted((ROOT / args.curated).glob("*.vZome"))
    records = summarize(emitted_paths, "emitted") + summarize(curated_paths, "curated")

    by_poly_sig = defaultdict(list)
    by_sig = defaultdict(list)
    for r in records:
        by_poly_sig[(r["poly"], r["sig"])].append(r)
        by_sig[r["sig"]].append(r)

    emitted = [r for r in records if r["source"] == "emitted"]
    curated = [r for r in records if r["source"] == "curated"]

    emitted_groups_by_poly = defaultdict(list)
    for (poly, sig), rs in sorted(by_poly_sig.items()):
        es = [r for r in rs if r["source"] == "emitted"]
        if es:
            cs = [r for r in rs if r["source"] == "curated"]
            emitted_groups_by_poly[poly].append({
                "sig": sig,
                "N": es[0]["N"],
                "emitted_files": [r["file"] for r in es],
                "curated_matches": [r["file"] for r in cs],
            })

    cross_poly_groups = []
    for sig, rs in sorted(by_sig.items()):
        polys = sorted(set(r["poly"] for r in rs))
        if len(polys) > 1:
            cross_poly_groups.append({
                "sig": sig,
                "N": rs[0]["N"],
                "polys": polys,
                "files": [r["file"] for r in rs],
            })

    coverage = {}
    for poly in sorted(set(r["poly"] for r in records)):
        e_sigs = {r["sig"] for r in emitted if r["poly"] == poly}
        c_sigs = {r["sig"] for r in curated if r["poly"] == poly}
        coverage[poly] = {
            "emitted_unique": len(e_sigs),
            "curated_unique": len(c_sigs),
            "covered_curated": len(e_sigs & c_sigs),
            "missing_curated": sorted(c_sigs - e_sigs),
            "new_emitted": sorted(e_sigs - c_sigs),
        }

    report = {
        "dedup_method": "center + shortest-distance scale + complete pairwise squared-distance multiset; invariant under rotation/reflection/translation/scale",
        "emitted_files": len(emitted),
        "curated_files": len(curated),
        "emitted_unique_by_poly": {p: len(gs) for p, gs in emitted_groups_by_poly.items()},
        "emitted_groups_by_poly": emitted_groups_by_poly,
        "cross_poly_groups": cross_poly_groups,
        "coverage": coverage,
        "records": records,
    }

    out_path = ROOT / args.out
    out_path.write_text(json.dumps(report, indent=2))

    print("Full Euclidean-similarity dedup")
    print(f"emitted files: {len(emitted)}")
    print(f"curated files: {len(curated)}")
    print()
    for poly in ("2_21", "3_21", "4_21"):
        cov = coverage.get(poly, {})
        print(
            f"{poly}: emitted unique={cov.get('emitted_unique', 0)}, "
            f"curated unique={cov.get('curated_unique', 0)}, "
            f"covered curated={cov.get('covered_curated', 0)}, "
            f"new emitted={len(cov.get('new_emitted', []))}"
        )
        for g in emitted_groups_by_poly.get(poly, []):
            label = "known" if g["curated_matches"] else "NEW"
            print(f"  {label:5s} {g['sig']} N={g['N']} emitted={len(g['emitted_files'])}")
            for f in g["emitted_files"]:
                print(f"        emitted {f}")
            for f in g["curated_matches"]:
                print(f"        curated {f}")
    print()
    print(f"cross-poly geometric overlaps: {len(cross_poly_groups)}")
    for g in cross_poly_groups:
        print(f"  {g['sig']} N={g['N']} polys={','.join(g['polys'])}")
    print()
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
