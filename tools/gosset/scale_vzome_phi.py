"""Scale vZome golden-field coordinates by a power of phi.

The vZome files emitted by the sweeps use golden-field coordinates as six
tokens per 3D point:

    x_a x_b y_a y_b z_a z_b

where each coordinate is a + b*phi.  Multiplication by phi^n is exact in
Z[phi], and this script preserves integer/fraction tokens.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from fractions import Fraction
from pathlib import Path


def phi_power_pair(n: int) -> tuple[Fraction, Fraction]:
    """Return (a,b) for phi^n = a + b*phi, n >= 0."""
    if n < 0:
        raise ValueError("only nonnegative powers are supported")
    a, b = Fraction(1), Fraction(0)
    for _ in range(n):
        # (a + b*phi) * phi = b + (a+b)*phi
        a, b = b, a + b
    return a, b


def mul_zphi(x: tuple[Fraction, Fraction], y: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    a, b = x
    c, d = y
    return a * c + b * d, a * d + b * c + b * d


def parse_tok(tok: str) -> Fraction:
    return Fraction(tok)


def fmt_frac(x: Fraction) -> str:
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def scale_coord_attr(value: str, scale: tuple[Fraction, Fraction]) -> str:
    toks = value.strip().split()
    if len(toks) != 6:
        raise ValueError(f"expected 6 tokens in golden point, got {len(toks)}: {value!r}")
    out: list[str] = []
    for i in range(0, 6, 2):
        z = (parse_tok(toks[i]), parse_tok(toks[i + 1]))
        a, b = mul_zphi(z, scale)
        out.extend([fmt_frac(a), fmt_frac(b)])
    return " ".join(out)


ATTR_RE = re.compile(r'\b(point|start|end)="([^"]*)"')


def scale_text(text: str, scale: tuple[Fraction, Fraction]) -> str:
    def repl(m: re.Match[str]) -> str:
        return f'{m.group(1)}="{scale_coord_attr(m.group(2), scale)}"'

    return ATTR_RE.sub(repl, text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    ap.add_argument("--phi_power", type=int, default=8)
    args = ap.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)

    scale = phi_power_pair(args.phi_power)
    manifest = {
        "source": str(src),
        "scale": {
            "phi_power": args.phi_power,
            "zphi_pair": [fmt_frac(scale[0]), fmt_frac(scale[1])],
            "description": f"multiply every golden-field coordinate by phi^{args.phi_power}",
        },
        "files": [],
    }

    for in_file in sorted(src.glob("*.vZome")):
        out_file = dst / in_file.name
        out_file.write_text(scale_text(in_file.read_text(encoding="utf-8"), scale), encoding="utf-8")
        manifest["files"].append({"source": str(in_file), "scaled": str(out_file)})

    # Preserve the original manifest alongside a scale manifest.
    if (src / "manifest.json").exists():
        shutil.copy2(src / "manifest.json", dst / "source_manifest.json")
    (dst / "scale_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Scaled {len(manifest['files'])} files by phi^{args.phi_power} = {fmt_frac(scale[0])} + {fmt_frac(scale[1])}*phi")
    print(f"Wrote {dst}")


if __name__ == "__main__":
    main()
