import sys, os
sys.path.insert(0, 'lib')
sys.path.insert(0, 'tools')
import numpy as np
import wythoff as wy
import search_engine as se

cases = [
  ('H4 bitr 600c',     'H4', (0,1,1,0)),
  ('H4 ringing 0101',  'H4', (0,1,0,1)),
  ('H4 cantel 600c',   'H4', (1,0,1,0)),
  ('H4 cantitr 120c',  'H4', (0,1,1,1)),
  ('H4 cantitr 600c',  'H4', (1,1,1,0)),
  ('H4 runcitr 120c',  'H4', (1,0,1,1)),
  ('H4 runcitr 600c',  'H4', (1,1,0,1)),
  ('H4 omnitr 120c',   'H4', (1,1,1,1)),
]
print(f"{'case':22s} {'V':>6s} {'K_full':>7s} {'K_reps':>7s} {'K_red':>7s}")
print('-' * 60)
for label, g, b in cases:
  V, E = wy.build_polytope(g, b)
  Earr = np.array([V[bb] - V[aa] for (aa, bb) in E]).T
  rep, _ = se._edge_dir_classes(Earr)
  print(f"{label:22s} {len(V):6d} {len(E):7d} {len(rep):7d} {100 * len(rep) / len(E):6.2f}%")
