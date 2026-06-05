# 8-orthoplex (`5_11`) R=1/R=2 symmetry and color audit

Sweep/audit reference for the 8-orthoplex (`5_11`) gallery models.  The
official page is provisional because R=3 is still running.

Source sweeps:

- `column_sweep_8_orthoplex_R1.json`
- `column_sweep_8_orthoplex_R2.json`

Post-processing audits:

- `orthoplex_8_R1_symmetry_analysis.json`
- `orthoplex_8_R1_strut_audit.json`
- `orthoplex_8_R2_symmetry_color_audit.json`
- `orthoplex_8_R2_D5d_formal_symmetry.json`

The color column below comes from the exact emitter-style strut audit, not from
the sweep's quick direction-color field.

The two R=2 signatures previously labeled generically as order 20 have been
formally classified as `D5d`: full order 20, rotational subgroup `D5` of order
10, one 5-fold axis, five perpendicular 2-fold axes, inversion, five `sigma_d`
mirror planes, and no horizontal mirror plane.

R=1 found 11 signatures.  R=2 found all 11 R=1 signatures plus seven more,
for 18 total.  These R=2 models are promoted under
`output/gosset_projections/5_11/`.

This is unlike the lower published orthoplex checks: the 6-orthoplex (`3_11`)
and 7-orthoplex (`4_11`) both saturated at R=1/R=2.  The 8-orthoplex therefore
appears to be the first orthoplex dimension in this D-family check where R=2
adds new shapes.  The 10-demicube (`1_71`) is already R=2-confirmed: its direct
D10 demicube sweep found the same 13 even-coset signatures at R=1 and R=2
(`column_sweep_10_demicube_R1.json`, `column_sweep_10_demicube_R2.json`).  The
10-orthoplex (`7_11`) R=2 check also matched R=1 exactly, with no new
signatures.

| Signature | First seen | Balls | Point-cloud symmetry | Colors |
|---|---|---:|---|---|
| `N6_a66b9103c2fb` | R=1 | 6 | D4 | B/Y/G |
| `N7_6d29d5e3ef9d` | R=1 | 7 | D4 | B/Y/G |
| `N7_6e3cf5e6f391` | R=1 | 7 | B3 | B/G |
| `N8_66f7d78bc22d` | R=2 | 8 | D3d | B/Y/G |
| `N8_99aeec21b429` | R=1 | 8 | B3 | B/Y/G |
| `N8_df8d08011115` | R=2 | 8 | D2h | B/Y/G |
| `N9_7b11b4a0657a` | R=1 | 9 | B3 | B/Y/G |
| `N10_682888a1f835` | R=2 | 10 | D4 | B/Y/G |
| `N12_14f4718877cf` | R=1 | 12 | D2h | B/Y/R |
| `N12_a61cd70e5e9e` | R=1 | 12 | D2h | B/Y/R |
| `N13_38bd06cecae8` | R=1 | 13 | H3 | B/R |
| `N13_dbaa9fca32a0` | R=1 | 13 | Th | B/Y/G |
| `N14_2034f9d8a550` | R=2 | 14 | D3d | B/Y/R |
| `N14_3d0502dd7979` | R=2 | 14 | D5d | B/Y/R |
| `N14_5626cb2a4839` | R=2 | 14 | D3d | B/Y/R |
| `N14_834bdf65e92e` | R=2 | 14 | D5d | B/Y/R |
| `N14_a9cae79664e2` | R=1 | 14 | D3d | B/Y/G |
| `N16_097e9af3e675` | R=1 | 16 | D3d | B/Y/R |

## `N14_3d0502dd7979` D5d projection matrix

Inspection candidate:

`output/gosset_projections/5_11/5_11_D5d_14_balls_a.vZome`

The raw R=2 sweep columns `c1..c8` are:

```text
[ -2,       -2,       -2phi,    -2phi,     0,        0,        0,        0 ]
[ -1,        1,       -1,        1,       -1-2phi,  -1,       -1,       -1+2phi ]
[ -1-phi,    1+phi,    1-phi,   -1+phi,    1+phi,   -1+phi,   -1+phi,    1+phi ]
```

Equivalently:

```text
c1 = (-2,    -1,       -1-phi)
c2 = (-2,     1,        1+phi)
c3 = (-2phi, -1,        1-phi)
c4 = (-2phi,  1,       -1+phi)
c5 = (0,     -1-2phi,   1+phi)
c6 = (0,     -1,       -1+phi)
c7 = (0,     -1,       -1+phi)
c8 = (0,     -1+2phi,   1+phi)
```

The visible 5-fold rotational symmetry is clearer after flipping the signs of
`c2` and `c3`, which only swaps the two vertices in those orthoplex antipodal
pairs. With `d1=c1`, `d2=-c2`, `d3=-c3`, `d4=c4`, `d5=c5`, `d6=c6`, `d7=c7`,
and `d8=c8`, a 72-degree rotation cycles

```text
d1 -> d4 -> d8 -> d3 -> d2 -> d1
```

and fixes the 5-fold axis setwise. The axis columns satisfy

```text
d5 = phi^3 d6
d7 = d6
```

so `d5`, `d6=d7`, `-d6`, and `-d5` are collinear on the D5d axis. The D5d
symmetry is a symmetry of the full signed point set `{+/- c_i}`, not of the raw
positive column representatives alone.

## `N14_834bdf65e92e` D5d projection matrix

Inspection candidate:

`output/gosset_projections/5_11/5_11_D5d_14_balls_b.vZome`

The raw R=2 sweep columns `c1..c8` are:

```text
[ -2-phi,   -2+phi,   -phi,     -phi,     -phi,     -phi,      -phi,      -phi ]
[  0,        0,       -2,       -2phi,     0,        0,         2phi,      2 ]
[ -1+phi,    1-phi,    1+phi,    1-phi,   -1-phi,   -1-phi,     1-phi,    1+phi ]
```

Equivalently:

```text
c1 = (-2-phi,  0,     -1+phi)
c2 = (-2+phi,  0,      1-phi)
c3 = (-phi,   -2,      1+phi)
c4 = (-phi,   -2phi,   1-phi)
c5 = (-phi,    0,     -1-phi)
c6 = (-phi,    0,     -1-phi)
c7 = (-phi,    2phi,   1-phi)
c8 = (-phi,    2,      1+phi)
```

One 72-degree rotation cycles the off-axis signed representatives

```text
c1 -> c4 -> -c8 -> -c3 -> c7 -> c1
```

The 5-fold axis columns are `c2` and `c5=c6`, with

```text
c5 = c6 = phi^3 c2
```

Thus this second D5d model has the duplicated axial vector at the larger
`phi^3` scale. In the first D5d model above, the roles are swapped: the
duplicated axial vector is the smaller one (`c6=c7`) and the single axial vector
is the larger one (`c5 = phi^3 c6`).
