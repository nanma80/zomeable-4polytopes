"""Emit vZome models for the 2 zomeable projections of snub 24-cell."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from polytopes import snub_24cell, phi
from emit_generic import project_and_emit
from emit_vzome import GF
V, E = snub_24cell()
print(f'snub 24-cell: {len(V)} verts, {len(E)} edges\n')

cases = [
    {
        'name': 'snub_24cell_cell_first',
        'n': np.array([1.0, 0.0, 0.0, 0.0]),
        'description': 'icosahedral-cell-first: (1,0,0,0) is the center of one of '
                       'the 24 icosahedral cells (= vertex of the removed inscribed '
                       '24-cell). 60 balls.',
    },
    {
        'name': 'snub_24cell_vertex_first',
        'n': np.array([phi**2, phi, 1.0, 0.0]),
        'description': 'vertex-first: (phi^2, phi, 1, 0) normalised = '
                       '(phi/2, 1/2, 1/(2phi), 0) IS a snub 24-cell vertex. 69 balls.',
    },
]

for case in cases:
    print(f"--- {case['name']}: {case['description']} ---")
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output',
                            'snub_24cell', case['name'] + '.vZome')
    project_and_emit(case['name'], V, E, case['n'], out_path,
                     extra_scale=GF(3, 5))
    print()
