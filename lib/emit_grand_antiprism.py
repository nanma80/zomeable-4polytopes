"""Emit vZome models for the 2 zomeable projections of the grand antiprism."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from polytopes import grand_antiprism, phi
from emit_generic import project_and_emit
from emit_vzome import GF

V, E = grand_antiprism()
print(f'grand antiprism: {len(V)} verts, {len(E)} edges\n')

cases = [
    {
        'name': 'grand_antiprism_vertex_first',
        'n': np.array([1.0, 1.0, 1.0, 1.0]),
        'description': 'vertex-first: (1,1,1,1)/2 is a GA vertex (a tesseract '
                       'vertex of the 600-cell that survives diminishing). '
                       '69 balls; sig Y:168 B:104 R:216, 12 collapsed edges.',
    },
    {
        'name': 'grand_antiprism_ring_first',
        'n': np.array([1.0, 0.0, 0.0, 0.0]),
        'description': 'pentagonal-antiprism-ring-first: (1,0,0,0) is one of '
                       'the 20 REMOVED Hopf-decagon vertices, so its direction '
                       'is the axis of one antiprismatic ring of GA. '
                       '68 balls; sig R:188 Y:164 B:142, 6 collapsed edges.',
    },
]

for case in cases:
    print(f"--- {case['name']}: {case['description']} ---")
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output',
                            'grand_antiprism', case['name'] + '.vZome')
    project_and_emit(case['name'], V, E, case['n'], out_path,
                     extra_scale=GF(3, 5))
    print()
