"""Scale a Wythoff-sweep .vZome file uniformly by 1/phi.

Each ZZ[phi] integer pair (a, b) represents a + b*phi.  Dividing by phi:

    (a + b*phi) / phi  =  a/phi + b  =  a*(phi - 1) + b  =  (b - a) + a*phi

so (a, b) -> (b - a, a).  Each <ShowPoint point="ax bx ay by az bz"/> and
<JoinPointPair start=... end=.../> coordinate pair is rewritten in place.
The file is otherwise byte-identical (preamble, EditHistory, etc).
"""
import re
import sys
from pathlib import Path

PAIRS_RE = re.compile(r'\b(-?\d+)\s+(-?\d+)\b')
COORD_ATTRS = ('point', 'start', 'end')


def _scale_pair(m):
    a = int(m.group(1))
    b = int(m.group(2))
    return f'{b - a} {a}'


def scale_coord_string(coord: str) -> str:
    """Coord string is 6 ints: (ax bx ay by az bz).  Rewrite each pair."""
    nums = coord.split()
    if len(nums) != 6:
        raise ValueError(f'unexpected coord arity: {coord!r}')
    out = []
    for i in range(0, 6, 2):
        a = int(nums[i])
        b = int(nums[i+1])
        out.append(str(b - a))
        out.append(str(a))
    return ' '.join(out)


ATTR_RE = re.compile(
    r'(' + '|'.join(COORD_ATTRS) + r')="([^"]+)"'
)


def transform_text(text: str) -> str:
    def repl(m):
        attr = m.group(1)
        coord = m.group(2)
        new_coord = scale_coord_string(coord)
        return f'{attr}="{new_coord}"'
    return ATTR_RE.sub(repl, text)


def main():
    if len(sys.argv) != 2:
        print('usage: python scale_vzome_by_inv_phi.py <path.vZome>',
              file=sys.stderr)
        sys.exit(2)
    p = Path(sys.argv[1])
    text = p.read_text(encoding='utf-8')
    new_text = transform_text(text)
    p.write_text(new_text, encoding='utf-8')
    print(f'rewritten {p}')


if __name__ == '__main__':
    main()
