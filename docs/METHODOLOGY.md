# Methodology limitations and open questions

This file collects open questions about the search methodology that
should be revisited if any result becomes interesting enough to need
formal proof.

## Two-criteria distinction (zometool-aligned vs vZome-embeddable)

The 8-cell case revealed that the search engine's notion of
"zomeable" is **strictly weaker** than vZome-embeddability:

- **Search criterion**: each unit edge direction matches one of 31
  default zome axes after rotation.
- **vZome criterion**: additionally, the polytope's vertex coordinates
  can be expressed in ℤ[φ]³ (up to a single global scale).

The vZome criterion is equivalent to: every length ratio `|c_i|/|c_j|`
between projected edges lies in ℚ(φ). For most polytopes this is
automatic. For the 8-cell, two of the 8 search hits at rng=1 fail it
(magnitudes involve `√2/√3` or `√(2+φ)`).

When emitting `.vZome` files we always run `classify_direction` on
every strut as a final check: a `None` return means the model is not
vZome-embeddable and we skip emission.

## Saturation as evidence of completeness

**Method used:** for each polytope, run the kernel-direction search at
range rng = max |a|, |b| over n components in ℤ[φ] = {a + bφ}, with
rng = 2, 3, 4.  If the count of distinct 3D shapes is the same at every
range, we declare the search "saturated" and report that count.

**Why this is *probably* correct (informal argument):**

For each valid projection, the kernel direction n lies on a specific
1D ray in ℝ⁴ (modulo the icosahedral group acting on the 3D image).
ℤ[φ]⁴ ∩ ray is a 1D lattice; all lattice points give the *same* 3D shape
(just rescaled).  As rng grows we accumulate more lattice points on the
same finite collection of rays — hits grow linearly, shape count stays
constant.

**What could break this argument:** a "missed" valid ray whose smallest
ℤ[φ]⁴ lattice point lies at rng > 4.  This requires the ray's direction
to have large numerator/denominator coefficients in (a + bφ) form, which
would be unusual for a geometrically natural projection — but is
mathematically possible.

**Status: empirical, not formally proven.**

## Open questions and future work (parked 2026-05-02)

These are documented for picking up later; none are blocking.

1. **Run rng=5 (or rng=6) saturation for the finite-classification cases.**
   Currently saturated at rng ≤ 4 for 5/16/24/120/600-cell. rng=5 takes
   ~1 min; rng=6 ~4 min. If counts hold, evidence is near-formal.
   (`python lib/run_search.py <name> 5`.)

2. **Augment shape fingerprint with strut-color signature multiset.**
   `group_by_shape()` currently uses sorted pairwise squared 3D
   distances. Two shapes with the same distance multiset but different
   strut colorings would be wrongly merged. Spot checks on current
   results suggest no collisions (the strut signatures already differ),
   but a formal audit would close the gap.

3. **Algebraic enumeration as a kernel-rng-free alternative.**
   For each polytope, enumerate all valid color-assignments to edges
   (finite combinatorial set), solve for n ∈ ℝ⁴ in each case, classify
   resulting shapes. Removes the rng cutoff entirely. Combinatorially
   heavy but conceptually cleaner.

4. **Document the 2 non-vZome-embeddable support-3 8-cell shapes.**
   The 8-cell search at rng=1 finds two zometool-strut shapes with sigs
   B:24+Y:8 and B:8+Y:8+R:16, requiring length ratios √2/√3 and
   √(2+φ) respectively. They could be built physically with default
   zome parts at incommensurate scaling but cannot be emitted to vZome.
   Worth a brief writeup with explicit ball coordinates in a
   (ℚ(φ), √2, √3)-extended field.

5. **vZome-embedding verification on the 12 non-hand-built `.vZome`s.**
   The polytope4d-emitted files (5cell, 16cell, 120cell, 600cell — 12
   files total) rely on vZome's quaternion-based projection. Each
   should be opened in vZome and verified to render with default-color
   struts. Status of which have been confirmed by user vs. only
   `classify_direction`-checked at emit time should be tracked
   per-file. Spot-checked 5-cell files all confirmed as true
   orthographic via M·Mᵀ test (2026-05-02).

## Strengthening options

If we ever need to upgrade saturation to proof:

1. **Push rng higher.**  rng=5 (≈250K dirs, ~1 min) and rng=6 (≈700K
   dirs, ~4 min) are cheap.  rng=8 gets expensive (~10⁷ dirs).
2. **Algebraic enumeration.**  For each polytope, enumerate all valid
   color-assignments to the edges, solve for n ∈ ℝ⁴ in each case, then
   classify the resulting shapes.  Finite, exhaustive, no rng cutoff —
   but combinatorially heavy.
3. **Random irrational sampling.**  Sample n from a continuous
   distribution outside ℤ[φ]⁴ and run try_align.  If no new shapes
   appear over millions of samples, the discrete set really is what
   ℤ[φ]⁴ captures.

## Verification: all emitted models are true orthographic projections

Each `.vZome` file we emitted can be verified to be a uniform-scale
orthographic projection by the **M·Mᵀ test**:

1. Parse the ball coordinates from `<ShowPoint>` elements (ZZ[φ]³).
2. Find the vertex assignment (V_i ↔ ball_j, possibly merging V_i pairs
   for collapsed cases) that minimizes least-squares fit residual of a
   3×4 linear map M with M·V₄ᵀ ≈ pts3ᵀ.
3. Compute M·Mᵀ. For a true orthographic projection (with rotation +
   uniform scale), this must equal s²·I₃ (eigenvalues all equal).

Audit results (2026-05-02):

- **5-cell** (4 files): all M·Mᵀ = s²·I to machine precision ✓
- **16-cell** (6 files, including the suspicious edge-first model):
  all M·Mᵀ = s²·I to machine precision ✓

Remaining files (24-cell hand-built, 120/600-cell polytope4d-based)
have not been audited yet via this test but should be cheap to add.

## Per-polytope confidence

| Polytope | Result            | Saturation evidence | Confidence |
|----------|-------------------|---------------------|------------|
| 5-cell   | 4 shapes          | rng 2/3 both 4      | high       |
| 8-cell   | 1 inf family + 2 sporadic | rng 1/2/3 → 8/32/129 with per-support breakdown {1,28,2,1} → {1,125,2,1}: only support-2 grows | high (theoretical + search) |
| 16-cell  | 6 shapes          | rng 2/3/4 all 6     | high       |
| 24-cell  | 3 shapes          | rng 2/3 both 3      | high       |
| 120-cell | 1 shape           | rng 2/3 both 1      | high       |
| 600-cell | 1 shape           | rng 2/3/4 all 1     | high       |

## 8-cell special case (resolved)

The 8-cell is the only polytope where **edge directions align with the
4D coordinate basis** (e_1, e_2, e_3, e_4). Consequence: the projection
formula `c_i = e_i − n_i n` makes `c_i = e_i⁺` (a unit vector in n^⊥)
whenever `n_i = 0`. So any 4D kernel with **support 2** — i.e.
`n = (a, b, 0, 0)` modulo permutation — automatically produces a
zometool-aligned projection (3 of the 4 image vectors are unit B-axes,
the 4th lies along the in-plane direction of (a, b)).

This gives the **infinite family of split cuboids** parametrized by
the integer ratio `(a:b)`, with vZome-embeddability further restricted
to `a² + b² ∈ ℤ[φ]²` — i.e. either Pythagorean triples (giving
integer c) or `a² + b² = 5m²` (giving `c = m(2φ−1) = m√5`). See
`8cell/CLASSIFICATION.md`.

The other 4-polytopes don't have edges aligned with any 4D coordinate
basis, so no analog of this argument applies — their shape sets are
finite.

## 5-cell special case (resolved)

The 5-cell's natural ring is **ℤ[√5]**, but √5 = 2φ - 1 ∈ ℤ[φ], so it
embeds in ℤ[φ]⁴ with an explicit aligned embedding (see
`5cell/RESULTS.md`).  The default `gen_dirs(permute_dedup=True)` was
incorrect for the 5-cell because the embedding singles out the 4th
axis; using `permute_dedup=False` correctly enumerates all directions
and finds **4 distinct shapes** including the natural vertex-first
"tetrahedron + center" projection.
