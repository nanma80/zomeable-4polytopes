# Strict zomeable n-cube projections

Scope: n-cubes for `n >= 3`, projected orthographically to 3D with every cube
edge parallel to a vZome default axis.  A projection is represented by generator
vectors `v_1, ..., v_n` in `Z[phi]^3`.

## Exact test

The projection is strict orthographic iff the generators form a tight frame:

```text
sum_i v_i v_i^T = c I_3,   c != 0.
```

This is the n-cube analogue of the isotropic covariance check used elsewhere in
the project.  It is exact over `Z[phi]`.

## New vs inherited

An `n`-cube projection is inherited from the `(n-1)`-cube exactly when one
generator is zero.  The current report marks a projection as `new` when all
generators are nonzero.

There is a second distinction:

- `primitive`: no zero generator and no parallel generator pair.
- `reducible/split`: no zero generator, but at least two generators are
  parallel.  The tesseract infinite family is the first split family.

For filtering out the less-interesting split and planar constructions, use the
stronger **essential/general-position** criterion:

```text
rank(v_i, v_j, v_k) = 3 for every distinct triple i,j,k.
```

Equivalently, every triplet of projected cube generators spans 3D
nontrivially.  For `n >= 3` this automatically implies every pair is
independent: if `v_i` and `v_j` were parallel, then every triple containing both
would have rank at most 2.

## Known `n=4` baseline

Under this convention, the ordinary cube model in the tesseract classification
is inherited from `n=3`.  The genuinely new strict `n=4` types are:

- the tesseract infinite split family,
- the phi-oblique sporadic,
- the rhombic dodecahedron sporadic.

See `output/regular/8cell/CLASSIFICATION.md`.

## `n=4` bounded generator-sweep sanity check

The exact generator sweep

```powershell
python tools\ncube\zphi_ncube_sweep.py --R 3
```

enumerates all unoriented zome-axis generators in `Z[phi]^3` with coefficient
radius `R=3`, groups generator pairs by their exact anisotropy, and combines
only complementary pair sums.  The leaf test is the exact tight-frame equation
above, not a floating point covariance proxy.

Output:

```text
ongoing_work\ncube\column_sweep_ncube4_R3.json
ongoing_work\ncube\column_sweep_ncube4_R3.progress.json
```

This run rediscovers the expected core `n=4` taxonomy:

- inherited cube,
- split infinite-family samples,
- phi-oblique sporadic,
- vertex-first rhombic-dodecahedron sporadic.

At this broad zome-axis generator level it also sees the known axis-aligned
cubic-only degenerates from the 8-cell notes: the face-first split and
edge-first hex prism.  They are recorded separately in the JSON labels and are
not counted as missing core strict-vZome types.

Applying the essential/general-position criterion to the same `R=3` sweep
leaves 1 `n=4` signature: the vertex-first rhombic-dodecahedron projection.
The phi-oblique representative has a non-spanning generator triple, and the
split-family samples fail because they contain parallel generators.

## Split infinite families

If `a^2 + b^2 = c^2` in `Z[phi]`, then the following axis-parallel generator
sets are exact tight frames:

```text
n=4:  (a x), (b x), (c y), (c z)
n=5:  (a x), (b x), (a y), (b y), (c z)
n=6:  (a x), (b x), (a y), (b y), (a z), (b z)
```

Varying the `Z[phi]` Pythagorean triple gives infinite families.  Sample triples
used in the generated report include `(1, 2, 2phi-1)`, `(3, 4, 5)`,
`(5, 12, 13)`, and `(2phi-1, 2, 3)`.

This confirms the expected new reducible infinite families for `n=5` and `n=6`.

## `n=5` bounded generator sweep

Run:

```powershell
python tools\ncube\zphi_ncube_sweep.py --n 5 --R 3
```

Output:

```text
ongoing_work\ncube\column_sweep_ncube5_R3.json
ongoing_work\ncube\column_sweep_ncube5_R3.progress.json
```

The `R=3` exact pair+triple sweep checked 65,907,695 unordered triples via
anisotropy grouping and completed in about 90 seconds.  It found 2,372 exact
frames, deduped to 56 projected point-cloud signatures.  Of these, 47 are new
relative to `n=4` because all five generators are nonzero:

- 7 samples of the expected `(2,2,1)` split infinite family,
- 32 other reducible/split signatures,
- 8 primitive candidate signatures with no zero or parallel generator pair.

This is a bounded search result, not a saturation proof: the result grew from
17 new signatures at `R=2` to 47 at `R=3`.

Family analysis of the 47 new `R=3` signatures:

- All 39 reducible signatures are samples of infinite split/refinement
  constructions, not sporadics.
- Parallel-class pattern `(2,2,1)` (7 signatures) coarsens to the `n=3` cube:
  split two cube generators by independent Pythagorean equations.
- Parallel-class pattern `(3,1,1)` (14 signatures) coarsens to the `n=3` cube:
  split one cube generator by a three-square equation
  `a^2 + b^2 + c^2 = d^2`.
- Parallel-class pattern `(2,1,1,1)` (18 signatures) coarsens to an `n=4`
  frame: 8 phi-oblique, 7 edge-first hex-prism, 2 vertex-first
  rhombic-dodecahedron, and 1 weighted/split-family base not matching the
  bounded `n=4` labels.  Scaling the base frame and replacing one generator
  `h` by `a h, b h` with `a^2 + b^2 = c^2` gives infinite families.

The 8 primitive candidates are also structured.  Every one has one generator
orthogonal to the other four, so it is a normal zome axis plus a planar
four-generator tight frame in the perpendicular plane.  At least one explicit
primitive infinite family is:

```text
(A,0,0), (0,B,0), (0,C,C), (0,C,-C), (0,0,B)
with A^2 = B^2 + 2 C^2.
```

The equation has a standard infinite parametrization over `Z[phi]`, for example

```text
A = u^2 + 2 v^2
B = u^2 - 2 v^2
C = 2 u v
```

for `u,v in Z[phi]`.  Generic nonzero choices give five non-parallel zome
generators, hence primitive strict `n=5` projections.

Applying the essential/general-position criterion to the `R=3` n=5 sweep leaves
0 signatures.  The reducible signatures fail because they contain parallel
generators; the primitive planar family fails because at least three generators
lie in the same 2D subspace.  Expanding to `R=4` increases the raw n=5 catalog
to 104 signatures but still leaves 0 essential/general-position signatures.

Under this stricter output convention, `output\ncubes` emits only qualifying
models: the `n=3` cube, the essential `n=4` vertex-first model, and the
sweep-backed essential n=6 candidates described below.

## `n=6` essential bounded generator sweep

Run:

```powershell
python tools\ncube\zphi_ncube_sweep.py --n 6 --R 2
```

Output:

```text
ongoing_work\ncube\column_sweep_ncube6_R2.json
ongoing_work\ncube\column_sweep_ncube6_R2.progress.json
```

The `R=2` strict triple+triple sweep found 46 distinct
essential/general-position signatures.  Rechecking the records gives 46 unique
shape signatures and 0 generator sextuples with a non-spanning triplet.  The
previously known six-blue-axis sporadic is included as signature
`N63_3b1c7b06d29d`, so the sweep adds 45 more essential n=6 signatures at this
bound.

The first generated strict catalog emitted all 46 n=6 `.vZome` models from
these records under `output\ncubes\ncube_6`.  Spot-checking showed that even
this stricter general-position criterion is still too permissive for a useful
model catalog: many outputs are single-color, many look arbitrary, and the
search did not appear close to saturation.

The retained catalog is therefore a visual curation, not the full sweep output.
Only 10 n=6 models are kept in `output\ncubes\ncube_6`, including the old
all-blue six-axis model `N63_3b1c7b06d29d` and several mixed-color examples.
The 46-record sweep JSON is retained as evidence of the broader bounded result.

An n=7 `R=2` strict triple+quad sweep was also started.  It was stopped before
completion after it had already found multiple strict candidates, because the
direction was judged unlikely to produce a small, aesthetically meaningful
classification.

## Beyond `n=6`

The same tight-frame construction generalizes by splitting each coordinate axis
into any positive lengths whose squared sums agree.  The helper script searches
for small positive integer witnesses and finds non-inherited split examples up
to the current bound (`n <= 10`, `c <= 80`).  These are constructive samples, not
a classification and not a primitive-family result.

If the intended classification should exclude reducible split refinements, then
the open problem is the primitive search after the known new `n=4` sporadics.

## Generated artifact

Run:

```powershell
python tools\ncube\zphi_ncube_families.py --max_n 10 --max_c 80
```

Output:

```text
ongoing_work\ncube\ncube_split_family_report.json
```
