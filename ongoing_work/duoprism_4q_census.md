# duoprism_4_q snap+signature census

Per-q distinct shape signatures on the (a,b,0,0) and (a,b,c,d)
kernel planes at multiple rngs.  Probe: `ongoing_work/probes/duoprism_4q_snap_sig.py`.

Signature = robust 5-decimal SHA-256 (same as `tools/dedup_corpus_by_shape.py`).

## (a,b,0,0) plane — square plane only

| q | rng=2 sigs | rng=3 sigs | rng=4 sigs | rng=4 snap | rng=4 align |
|---|-----------:|-----------:|-----------:|-----------:|------------:|
| 5 | 0 | 0 | 0 | 0 | 3280 |
| 6 | 1 | 3 | 3 | 104 | 3280 |
| 7 | 0 | 0 | 0 | 0 | 0 |
| 8 | 0 | 0 | 0 | 0 | 3280 |
| 9 | 0 | 0 | 0 | 0 | 0 |
| 10 | 2 | 2 | 5 | 160 | 3280 |
| 11 | 0 | 0 | 0 | 0 | 0 |
| 12 | 0 | 0 | 0 | 0 | 0 |

## (a,b,c,d) plane — full 4D directions

| q | rng=2 sigs | rng=3 sigs | rng=2 snap | rng=3 snap | rng=3 align |
|---|-----------:|-----------:|-----------:|-----------:|------------:|
| 5 | 0 | 0 | 0 | 0 | 2400 |
| 6 | 1 | 3 | 24 | 64 | 2512 |
| 7 | 0 | 0 | 0 | 0 | 1200 |
| 8 | 0 | 0 | 0 | 0 | 2400 |
| 9 | 0 | 0 | 0 | 0 | 1200 |
| 10 | 2 | 2 | 40 | 84 | 2400 |
| 11 | 0 | 0 | 0 | 0 | 1200 |
| 12 | 0 | 0 | 0 | 0 | 1200 |

## Reading the table

- **sigs** = number of distinct shape signatures emitted.
- **snap** = number of (kernel direction, scale) pairs that
  successfully snapped to the zome lattice.
- **align** = number of directions that passed the
  `_try_align` axis classification (but may not have snapped).

A q-value with snap=0 at a high rng confirms that no kernel
direction in that range can produce a zomeable projection.

## Headline findings

The eight q values cleanly partition into three classes:

| class | q values | (a,b,0,0) align | (a,b,c,d) align | snap | n_shapes |
| ----- | -------- | ----------- | ----------- | ---: | -------: |
| **zomeable**    | 6, 10            | yes | yes | yes | bounded (3, 5) |
| **align-only**  | 5, 8             | yes | yes | no  | 0 |
| **non-aligned (square-plane)** | 7, 9, 11, 12 | no | yes | no | 0 |

Interpretation:

- **q = 6, 10**: the q-gon's symmetry (hexagon, decagon) is fully zome-
  compatible with the square's 4-fold symmetry on the (a,b,0,0) plane.
  Shape counts saturate at small values (3 for q=6, 5 for q=10) and
  remain there as rng grows — see `duoprism_4_10_inf_family_resolved.md`
  and `duoprism_4_6_inf_family_resolved.md`.

- **q = 5, 8**: the projection's *edges* align to zome axes (pentagon
  has R5 axes, octagon has 4-fold axes) but no consistent scale/quantum
  exists that simultaneously snaps all 4q vertices to zome balls.  This
  is a global lattice-incommensurability, not a directional failure.

- **q = 7, 9, 11, 12**: on the pure (a,b,0,0) plane these have zero
  aligned directions — the heptagon/nonagon/hendecagon/dodecagon edge
  set has no `_try_align` solution when projected via a square-plane
  kernel.  They do gain alignment on (a,b,c,d) (the q-gon plane
  contributes some directions) but still snap zero times.

## Why q=12 fails despite being "zome-compatible"

The dodecagon does have axes appearing in zome, but inside the 4D
duoprism the edge set's projected directions don't match the 4-fold
square pattern under any 4D rotation accessible to `_try_align`.
Conclusion: q=12 is **not** zomeable as a duoprism_4_q.

## Cross-reference with prismatic_manifest

| q  | manifest n_shapes (rng=4) | census ab00 rng=4 | census abcd rng=3 |
| -: | -----------------------: | ----------------: | ----------------: |
|  5 |                       0  |                 0 |                 0 |
|  6 |                       3  |                 3 |                 3 |
|  7 |                       0  |                 0 |                 0 |
|  8 |                       0  |                 0 |                 0 |
|  9 |                       0  |                 0 |                 0 |
| 10 |                       5  |                 5 |                 2 |
| 11 |                       0  |                 0 |                 0 |
| 12 |                       0  |                 0 |                 0 |

All entries agree — except (q=10, abcd rng=3) which undercounts
because the abcd-plane scan at rng=3 can't reach the wider 1D range
that the ab00-plane scan at rng=4 explores in the square plane.

## Output JSON files (one per q × plane × rng)

```
ongoing_work/probe_4q_sigs_q{5..12}_ab00_rng{2,3,4}.json
ongoing_work/probe_4q_sigs_q{5..12}_abcd_rng{2,3}.json
```

Each contains the full sig list, `n_aligned`, `n_snapped`, `n_errors`,
and `elapsed_s`.

## Reproducing

```powershell
python ongoing_work/probes/duoprism_4q_snap_sig.py --q 10 --plane ab00 --rngs 4,5,6
python ongoing_work/probes/duoprism_4q_census_driver.py
```

