---
layout: default
title: Zomeable 4-polytopes
description: Enumerated orthographic projections of 4-polytopes that can be built in zometool and modeled in vZome.
---

# Zomeable 4-polytopes

A catalogue of 4-dimensional polytopes that can be projected to 3D in ways that are **physically buildable with [zometool](https://www.zometool.com/)** struts (Blue / Yellow / Red / Green) and **modelled exactly in [vZome](https://vzome.com/)**.

For each polytope, we enumerate orthographic projections whose every edge lands on a default zometool axis. Hits are grouped up to rotation and uniform scale, then emitted as `.vZome` files that you can spin, zoom, and inspect right in the browser.

---

## Browse the corpus

Pick a category and click **View →** to jump into its interactive page.

| Category | Polytopes | Zomeable polytopes | Zomeable projections | |
| -------- | --------: | -----------------: | -------------------: | --- |
| **Regular** | 6 | 6 | 18 + 1 inf family ¹ | [**View regulars →**](https://nanma80.github.io/zomeable-4polytopes/docs/CATEGORY_REGULAR.html) |
| **Uniform** *(non-prismatic)* | 41 | 28 | 73 | [**View uniforms →**](https://nanma80.github.io/zomeable-4polytopes/docs/CATEGORY_UNIFORM.html) |
| **Duoprisms** *({p}×{q})* | ∞ | 6 | 8 + 2 inf families | [**View duoprisms →**](https://nanma80.github.io/zomeable-4polytopes/docs/CATEGORY_DUOPRISMS.html) |
| **Polyhedral prisms** *(P × [0,1])* | 17 | 12 | 45 | [**View polyhedral prisms →**](https://nanma80.github.io/zomeable-4polytopes/docs/CATEGORY_POLYHEDRAL_PRISMS.html) |
| **Antiprismatic prisms** *(A_n × [0,1])* | ∞ | 1 | 9 | [**View antiprismatic prisms →**](https://nanma80.github.io/zomeable-4polytopes/docs/CATEGORY_ANTIPRISMATIC_PRISMS.html) |
| **Total** | **∞** | **53** | **153 + 3 inf families** | |

Related non-4D collection:

| Category | Source polytopes | Models | |
| -------- | ---------------: | -----: | --- |
| **Gosset orthographic projections** | 17 | 85 | [**View projections →**](https://nanma80.github.io/zomeable-4polytopes/docs/CATEGORY_GOSSET_PROJECTIONS.html) |
| **A5 simplex family projections** *(all 19 A5 Wythoff polytopes)* | 19 | 57 | [**View projections →**](https://nanma80.github.io/zomeable-4polytopes/docs/CATEGORY_A5_PROJECTIONS.html) |
| **Approximate 3D polyhedron zomes** *(not projections; curated RGBY approximations)* | 16 | 16 | [**View approximate zomes →**](https://nanma80.github.io/zomeable-4polytopes/docs/APPROXIMATE_ZOMES.html) |

Every category page lists the polytopes in scope and gives one-click access to a **vZome 3D viewer** embedded inline.

¹ Infinite families currently occur for the tesseract (8-cell) and the duoprisms `{4}×{6}` and `{4}×{10}`; other corpus entries saturate at small finite counts. See the [8-cell master theorem](https://nanma80.github.io/zomeable-4polytopes/output/regular/8cell/CLASSIFICATION.html) and [duoprism category page](https://nanma80.github.io/zomeable-4polytopes/docs/CATEGORY_DUOPRISMS.html) for details.

Visualization option: some viewer pages include a second model immediately below
the original labelled **hidden-cell-removal view**.  This is a descriptive term
used here by analogy with hidden-line/hidden-surface removal: cells facing away
from the positive side of the 4D projection kernel are omitted, while equatorial
cells are retained, so the model is easier to inspect.  These variants are not
new projections and are not included in the counts above.  See the
[hidden-cell-removal index](https://nanma80.github.io/zomeable-4polytopes/output/HIDDEN_CELL_REMOVAL.html).

---

## How a kernel becomes a model

For each polytope `P` ⊂ ℝ⁴ and each candidate kernel direction `n ∈ ℤ[φ]⁴`, we form the orthogonal projection `Q = I − n nᵀ / |n|²` and project every vertex of `P` to ℝ³. The projection is **zomeable** when every projected edge points along one of the 31 zometool axes (B / Y / R / G families). We enumerate all kernel directions in a bounded coefficient box, dedupe up to rotation + uniform scale, and emit a `.vZome` file per distinct shape.

The catalogue's counts are **empirical**: we report a number once enlarging the coefficient box stops finding new shapes. They are not formally proven complete; see [`docs/METHODOLOGY.md`](https://nanma80.github.io/zomeable-4polytopes/docs/METHODOLOGY.html) for the discussion.

---

## Highlights

- **Tesseract.** Three sporadic shapes (cell-first cube, vertex-first rhombic dodecahedron, the *phi-oblique* sporadic) plus an infinite family of zomeable cuboids, one per ℤ[φ]-Pythagorean triple. [See all 13 emitted models →](https://nanma80.github.io/zomeable-4polytopes/output/regular/8cell/VIEWER.html)
- **120-cell, 600-cell.** Each admits a single canonical zomeable projection (cell-first and vertex-first, respectively).
- **Snub 24-cell, grand antiprism.** Both 600-cell diminishings yield two zomeable projections each — the snub's vertex-first and the grand antiprism's vertex-first appear here as new shapes.
- **Prismatic surprises.** Six duoprisms `{p}×{q}` produce zomeable rank-3 projections, including infinite families for `{4}×{6}` and `{4}×{10}`.

---

## Development

The full source, methodology, generation scripts, and per-polytope deep-dive write-ups live in the [GitHub repository](https://github.com/nanma80/zomeable-4polytopes). Python 3.10+ and NumPy; MIT-licensed.

Built on the [zometool](https://www.zometool.com/) construction system and [vZome](https://vzome.com/) (Scott Vorthmann).
