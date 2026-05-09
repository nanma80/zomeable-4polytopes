"""Build a cache of post-snap shape_signatures for every .vZome in
the master corpus folders (output/<polytope>/*.vZome).

Output: ongoing_work/master_corpus_signatures.json

Each entry: {file: relative_path, polytope_dir, signature: [V_count, E_count, hash16, edge_multiset]}.

Used by triage probes that need to determine if a sweep-discovered
shape is congruent to an existing master-corpus entry (which is NOT
tracked in manifest.json).
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from tools.dedup_corpus_by_shape import parse_vzome, shape_signature  # type: ignore


MASTER_DIRS = [
    "5cell", "8cell", "16cell", "24cell", "120cell", "600cell",
    "snub24cell", "grand_antiprism",
]


def main():
    out = []
    for sub in MASTER_DIRS:
        d = ROOT / "output" / sub
        if not d.exists():
            print(f"  skip {sub} (missing)")
            continue
        files = sorted(d.glob("*.vZome"))
        print(f"{sub}: {len(files)} files")
        for f in files:
            try:
                P, E = parse_vzome(f)
            except Exception as e:
                print(f"  ERR parsing {f.name}: {e}")
                continue
            sig = shape_signature(P, E)
            sig_serializable = list(sig)
            sig_serializable[-1] = list(sig_serializable[-1])
            out.append({
                "file": str(f.relative_to(ROOT)).replace("\\", "/"),
                "polytope_dir": sub,
                "n_points": int(sig[0]),
                "n_edges": int(sig[1]),
                "hash": str(sig[2]),
                "edge_multiset": list(sig[3]),
                "signature": sig_serializable,
            })
            print(f"  {f.name}: V={sig[0]} E={sig[1]} h={sig[2]}")

    out_path = ROOT / "ongoing_work" / "master_corpus_signatures.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {len(out)} entries to {out_path}")


if __name__ == "__main__":
    main()
