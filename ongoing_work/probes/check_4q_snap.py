"""Show snap-success/fail per 4_q polytope from sweep log."""
import json
from collections import Counter
counts = {}
with open('ongoing_work/prismatic_sweep_log.jsonl') as f:
    for line in f:
        r = json.loads(line)
        s = r.get('slug', '')
        if s.startswith('duoprism_4_') and r.get('phase') in (None, 'sweep'):
            statuses = Counter(e.get('status') for e in r.get('emitted', []) if isinstance(e, dict))
            counts[s] = (r.get('unique_shapes'), dict(statuses))
for s in sorted(counts):
    u, st = counts[s]
    n_emit = st.get('emitted', 0)
    n_fail = st.get('snap_failed', 0)
    print(f"{s:25s} unique={u:4d} emit={n_emit:3d} snap_fail={n_fail:4d}")
