# Uniform 4-polytopes: zomeable projection prospects

**Status:** planning. Drafted 2026-05-02.

This document inventories the ~47 convex uniform 4-polytopes and identifies which
are worth searching for new zomeable orthographic projections to 3D.

## TL;DR

Most uniform 4-polytopes are *Wythoffian* (built by ringing a Coxeter
diagram). For these, **edge directions are constrained to the union of root
orbits of the parent Coxeter group**, which means their zomeable projections
are necessarily subsets of the projections we already enumerated for the
regular 4-polytopes. No new shapes arise.

The genuinely new opportunities are the **two non-Wythoffian uniform
4-polytopes** and the prismatic/duoprism families.

**Recommended priority order:**

1. **Snub 24-cell** (D₄-symmetric, 5 edge orbits). High value, moderate cost.
2. **Grand antiprism** (non-Wythoff, partial H₄). High value, moderate cost.
3. **Pentagonal duoprism {5}×{5}** and a couple of small duoprisms. Moderate
   value (educational; trivially zomeable in some cases), low cost.
4. *(Skip)* All Wythoff uniforms — automated batch run only as sanity check.

## 1. The root-orbit argument (why Wythoff uniforms yield nothing new)

In the Wythoff construction with ringed nodes S ⊆ {0,1,...,n}, edges of the
resulting polytope come in |S| orbits under the symmetry group W. The k-th
orbit consists of W-translates of a simple-root direction associated with
ring node k.

If all simple roots of W lie in a single W-orbit (i.e. W is *simply laced*
or has connected Coxeter diagram with all single bonds, OR the diagram is
non-crystallographic but uniform-orbit like H₄), then **every uniform
polytope in family W has edges in the same direction-orbit as the regular
{p,q,r} of that family.** Identical zomeable kernel set.

If W has two root orbits (B₄, F₄), then a uniform polytope's edges live in
the union of those two orbits. A kernel n is zomeable for the polytope iff
n is zomeable for *both* orbits simultaneously — i.e., the intersection of
the zomeable kernels for the two regular polytopes that exhibit those
orbits. Strictly fewer, never more.

| Coxeter family | # root orbits | Regular polytopes exhibiting each orbit |
|----------------|---------------|------------------------------------------|
| A₄ (5-cell)    | 1             | 5-cell                                   |
| B₄ (8/16-cell) | 2             | 16-cell (long), 8-cell (short)           |
| F₄ (24-cell)   | 2             | 24-cell long-root, short-root 24-cell    |
| H₄ (120/600-cell) | 1          | 120-cell, 600-cell (same orbit)          |

**Corollary.** For each Wythoff uniform 4-polytope, the set of zomeable
kernels is contained in the kernels we already enumerated for the regular
polytopes of its family. We expect *no new 3D shapes* from Wythoff uniforms,
only restrictions or duplicates.

This is testable: an automated batch run on all Wythoff uniforms should
yield only shapes already in our database. (Useful as a sanity check on
the search engine and the database, but not as a new-shape generator.)

### 1.1 Empirical confirmation: bitruncated 5-cell (2026-05-02)

Built the bitruncated 5-cell (30 vertices, 60 edges in 2 Wythoff orbits)
in the same R⁴ embedding as the regular 5-cell (sym coordinates =
permutations of (0,0,1,2,2), mapped via T(w) = Σ wᵢ vᵢ). Ran search at
rng=3:

| | 5-cell | bitruncated 5-cell |
|---|--------|---------------------|
| hits          | 40 | 40 |
| distinct shapes (rng=3) | 3 | 3 |
| kernel set diff | — | **0 new, 0 missing** |

Every one of the 40 zomeable kernel directions is **identical** between
the two polytopes. The 3D *shapes* change (4-ball → 18-ball, 5-ball →
30-ball ×2) because the bitruncated projection has more vertices, but
the projection *direction* is in 1-to-1 correspondence. This empirically
confirms the representation-theory argument: A₄ Wythoff uniforms share
the 5-cell's zomeable kernel set exactly. (Script:
`reality_check_bitrunc5.py`.)

## 2. Inventory of Wythoff uniform 4-polytopes (47 total)

Listed by family with edge-orbit count. *EO* = "edge orbits" = number of
ringed nodes. All edges of these polytopes are in the corresponding
direction orbits of the parent group.

### A₄ family (9 polytopes)
All have edges in the single A₄ root orbit (20 vectors e_i − e_j).
Zomeable kernels = same as 5-cell (4 distinct shapes).

| Symbol | Name | EO |
|--------|------|----|
| {3,3,3}    | 5-cell                  | 1 |
| r{3,3,3}   | rectified 5-cell        | 1 |
| t{3,3,3}   | truncated 5-cell        | 2 |
| rr{3,3,3}  | cantellated 5-cell      | 2 |
| 2t{3,3,3}  | bitruncated 5-cell      | 2 |
| t₀,₃       | runcinated 5-cell       | 2 |
| tr{3,3,3}  | cantitruncated 5-cell   | 3 |
| t₀,₁,₃     | runcitruncated 5-cell   | 3 |
| t₀,₁,₂,₃   | omnitruncated 5-cell    | 4 |

### B₄ family (15 polytopes)
Edges in long-root orbit (24 vectors), short-root orbit (8 vectors), or both.
Zomeable kernels = subset of 16-cell ∪ 8-cell projections.

Notable mixed-orbit cases: truncated 8-cell (rings 2,3 → mixes orbits),
runcinated tesseract, omnitruncated tesseract.

### F₄ family (9 polytopes, including 24-cell families)
Edges in F₄ long-root orbit, short-root orbit, or both. Zomeable kernels =
subset of long-root-24-cell ∪ short-root-24-cell.

### H₄ family (15 polytopes)
All edges in single H₄ root orbit (120 vectors). Zomeable kernels = same
as 120/600-cell, i.e. **the unique H₄→H₃ Coxeter projection only**.

This is a strong rep-theory statement: there is essentially one
linear H₄-equivariant map H₄ → H₃ up to symmetry, so every uniform H₄
polytope has at most one zomeable projection up to symmetry — the same one.

## 3. The genuinely new candidates (non-Wythoff)

### 3.1 Snub 24-cell {3,4,3}/2 — TOP PRIORITY

- **Symmetry:** D₄ (index 6 inside F₄) → snub-24-cell symmetry group of
  order 1152.
- **Vertices:** 96.
- **Edges:** 432, in **5 distinct edge orbits** (per Coxeter / Wikipedia).
- **Non-Wythoff:** built by alternation of truncated 24-cell.
- **Why interesting:** edges include directions that are NOT in F₄ root
  orbits — mixtures induced by alternation. A genuinely new edge-direction
  landscape, not a subset of any regular polytope's.
- **Cost estimate:** 432 edges × ~30K dirs at rng=3 ≈ feasible.
- **Embedding:** known explicit coordinates in ℤ[φ]⁴ (Coxeter-Du Val).

### 3.2 Grand antiprism — SECOND PRIORITY

- **Symmetry:** non-Wythoff, order 400 (≈ I₂(10) × I₂(10) extended).
- **Vertices:** 100.
- **Edges:** 500, in **3 edge orbits**.
- **Structure:** decomposes into 2 rings of 10 pentagonal antiprisms each
  (filling tubes around 2 great circles) + 300 tetrahedra filling the gap.
- **Why interesting:** has built-in pentagonal symmetry, so projections
  preserving one of the two pentagonal axes might give clean H₃-aligned
  zonotopes that aren't pure H₄-projection.
- **Coordinates:** explicit ℤ[φ]⁴ coordinates known.

### 3.3 Duoprism / antiprism-prism families (infinite, picky selection)

- **{p}×{q} duoprism**: vertices = product of regular p-gon and q-gon.
  Trivially has B/Y/R alignment for some specific (p,q). E.g.
  - {5}×{5}: pentagonal duoprism. Edges all in 2D pentagon directions
    × axial. Always zomeable in vZome via blue-yellow-red 5-fold subzome.
  - {10}×{10}: decagonal duoprism. Same story.
  - {3}×{p} = triangular-p-gonal duoprism: less interesting.
- **Antiprism prisms** (n-antiprism × edge): only n=3,4,5,10 candidates
  for vZome alignment.

These are mainly educational / pretty rather than novel-shape-finding.

## 4. Proposed work plan

### Phase A — automated sanity check (low effort)
Run existing search_engine over all 9 A₄ uniforms, verify zomeable kernels
are subsets of the 5-cell kernels. Quick regression test. Could similarly
hit a representative subset of B₄/F₄/H₄ uniforms.

Optional: write the batch driver and run overnight.

### Phase B — snub 24-cell
1. Add snub_24cell to `polytopes.py` (vertices + edges).
2. Run search_engine at rng=3,4. Identify zomeable kernels.
3. For each kernel, classify projected 3D shape and emit `.vZome`.
4. Document in `snub24cell/RESULTS.md`.

### Phase C — grand antiprism
Same workflow; smaller in vertex count but irregular structure means
edge enumeration is the careful step.

### Phase D — duoprisms (optional decorative)
Pick {5}×{5}, {10}×{10}, {3}×{8}, emit one each as illustration.

## 5. Open uncertainties (good to confirm before starting)

- **(?)** Does the user want to include the snub 24-cell's 5 different edge
  *lengths* as a strict zomeability constraint (each must hit the right
  zomeable strut size after projection)? Or only that every direction lies
  on a zome axis? Our 6-regular-polytope work used the looser (direction-
  only) criterion.
- **(?)** Are non-convex uniform 4-polytopes (Schläfli–Hess polychora — 10
  star polytopes) in scope? Their edges interpenetrate, but as zonotope
  generators they're well-defined. If yes, that adds 10 candidates worth
  investigating (especially the H₄ ones since they have new symmetry
  combinations).
- **(?)** Should we restrict to convex hull, or accept self-intersecting
  uniform compounds?

## 6. Summary recommendation

- **Skip the 47 Wythoff uniforms** — by representation theory we expect
  zero new shapes. (Maybe one automated regression run for sanity.)
- **Pursue snub 24-cell** as the single highest-value target.
- **Pursue grand antiprism** as the second.
- **Optionally illustrate** with 1–2 duoprisms.
