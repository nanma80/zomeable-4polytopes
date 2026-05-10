"""In-place uniform phi^k rescale of every <ShowPoint> in a .vZome corpus.

vZome stores each ZZ[phi] coordinate as a pair of integers (a, b) meaning
``a + b * phi``.  Multiplying by phi^k stays inside ZZ[phi] because phi is
a unit (phi*(phi-1) = 1).  This script edits ShowPoint elements in place.

The relevant integer transforms (derived from phi^2 = phi + 1):

  * (a, b) * phi      = (b, a + b)
  * (a, b) * phi^-1   = (a + b, -a)              # b - 1/phi*a but
                                                  # via 1/phi = phi - 1
  * (a, b) * phi^2    = (b, a + 2b)              # = ((a+b) + b*phi) * phi
                                                  #     hmm wait derive
  * (a, b) * phi^-2   = (2a - b, b - a)

We use these as:

    phi^-2:  (a, b) -> (2a - b, b - a)

Usage:
    python tools/rescale_corpus.py --power -2 [--glob "output/wythoff_sweep/**/*.vZome"]

Default: --power -2, default glob is the Wythoff sweep corpus.
"""

from __future__ import annotations

import argparse
import glob as glob_mod
import re
import sys
from pathlib import Path


# ZZ[phi] elementary multiplications.  Each maps (a, b) representing
# ``a + b*phi`` to ``(a', b')`` representing the product.
def mul_phi(a: int, b: int) -> tuple[int, int]:
    """(a + b*phi) * phi = a*phi + b*phi^2 = a*phi + b*(phi+1) = b + (a+b)*phi."""
    return (b, a + b)


def mul_phi_inv(a: int, b: int) -> tuple[int, int]:
    """1/phi = phi - 1, so (a + b*phi) * (phi - 1) = (a + b*phi)*phi - (a + b*phi)
    = (b + (a+b)*phi) - (a + b*phi) = (b - a) + a*phi.  But that is (a + b*phi)/phi
    so the integer answer is ((b - a), a).  Wait check sign: 1/phi ≈ 0.618.
    (1, 0)/phi = 0.618 = -1 + phi, i.e. (-1, 1).  Try (b - a, a): (0 - 1, 1) = (-1, 1). ✓
    (0, 1)/phi = 1, i.e. (1, 0).  Try (b - a, a): (1 - 0, 0) = (1, 0). ✓
    """
    return (b - a, a)


def mul_phi_pow(a: int, b: int, k: int) -> tuple[int, int]:
    """Multiply (a + b*phi) by phi^k, returning the resulting (a', b')."""
    if k == 0:
        return (a, b)
    if k > 0:
        for _ in range(k):
            a, b = mul_phi(a, b)
    else:
        for _ in range(-k):
            a, b = mul_phi_inv(a, b)
    return (a, b)


SHOW_POINT_RE = re.compile(
    r'(\b(?:point|start|end)=")([^"]*)(")', re.IGNORECASE)


def _rescale_point_attr(point_str: str, k: int) -> str:
    parts = point_str.strip().split()
    if len(parts) != 6:
        # Not a 6-int coord (some attributes share the name in vZome XML
        # but carry other things, e.g. start/end on non-coord elements).
        # Leave untouched.
        return point_str
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return point_str
    out = []
    for i in range(0, 6, 2):
        a, b = nums[i], nums[i + 1]
        a2, b2 = mul_phi_pow(a, b, k)
        out.append(str(a2))
        out.append(str(b2))
    return " ".join(out)


def rescale_file(path: Path, k: int, dry_run: bool = False) -> int:
    """Rescale every coord-bearing attribute (point/start/end) in `path`
    by phi^k.  Returns count of attributes rewritten."""
    text = path.read_text(encoding="utf-8")
    n = 0

    def repl(m: re.Match) -> str:
        nonlocal n
        new_val = _rescale_point_attr(m.group(2), k)
        if new_val != m.group(2):
            n += 1
        return f"{m.group(1)}{new_val}{m.group(3)}"

    new_text = SHOW_POINT_RE.sub(repl, text)
    if not dry_run and new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return n


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--power", "-k", type=int, default=-2,
                   help="integer k; multiply every ShowPoint by phi^k. "
                        "Default -2 (i.e. divide by phi^2).")
    p.add_argument(
        "--glob", default="output/wythoff_sweep/**/*.vZome",
        help="glob pattern of .vZome files to rescale (recursive).")
    p.add_argument("--dry-run", action="store_true",
                   help="report changes without writing.")
    args = p.parse_args(argv)

    paths = sorted(Path(g) for g in glob_mod.glob(args.glob, recursive=True))
    if not paths:
        print(f"no files match {args.glob!r}", file=sys.stderr)
        return 2

    total_pts = 0
    print(f"rescaling {len(paths)} files by phi^{args.power}"
          + (" (dry run)" if args.dry_run else ""))
    for p in paths:
        n = rescale_file(p, args.power, dry_run=args.dry_run)
        total_pts += n
    print(f"done: {total_pts} ShowPoints across {len(paths)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
