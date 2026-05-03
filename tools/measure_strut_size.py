"""Measure smallest non-zero edge length and smallest pairwise vertex
distance in vZome files (zome units)."""
import re
import sys
import glob

PHI = (1 + 5 ** 0.5) / 2


def parse_pt(s):
    nums = [int(x) for x in s.split()]
    return tuple(nums[i] + nums[i + 1] * PHI for i in (0, 2, 4))


def smallest_distances(path):
    txt = open(path).read()
    pts = re.findall(r'<ShowPoint point="([^"]+)"/>', txt)
    edges = re.findall(r'<JoinPointPair start="([^"]+)" end="([^"]+)"/>', txt)
    pts3 = [parse_pt(p) for p in pts]
    smin_edge = float("inf")
    for s, e in edges:
        a = parse_pt(s)
        b = parse_pt(e)
        d = sum((a[i] - b[i]) ** 2 for i in (0, 1, 2)) ** 0.5
        if 1e-6 < d < smin_edge:
            smin_edge = d
    smin_pair = float("inf")
    n = len(pts3)
    for i in range(n):
        for j in range(i + 1, n):
            a = pts3[i]
            b = pts3[j]
            d = sum((a[k] - b[k]) ** 2 for k in (0, 1, 2)) ** 0.5
            if 1e-6 < d < smin_pair:
                smin_pair = d
    return smin_edge, smin_pair, len(pts3), len(edges)


if __name__ == "__main__":
    pattern = sys.argv[1] if len(sys.argv) > 1 else "output/wythoff_sweep/**/*.vZome"
    print(f"  edge_min  pair_min  balls  edges  path")
    for path in sorted(glob.glob(pattern, recursive=True)):
        smin_e, smin_p, nb, ne = smallest_distances(path)
        print(f"  {smin_e:8.3f}  {smin_p:8.3f}  {nb:5d}  {ne:5d}  {path}")

