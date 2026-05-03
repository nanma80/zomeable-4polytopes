"""Generic exhaustive-direction search for default-color orthographic projections.

For a given 4-polytope embedding (vertices V, edges E), enumerate kernel
directions n in Z[phi]^4 with bounded |a|+|b|<=rng, project to 3D, and
test whether all projected edges can be simultaneously aligned with the
zometool default-color icosahedral axes (B/Y/R/G).

Adapted from 24-cell/search/exhaustive_search.py.
"""
import numpy as np
from itertools import product
from collections import Counter
import time

phi = (1 + 5 ** 0.5) / 2


# ---------------------------------------------------------------------- #
# Icosahedral default-axis machinery
# ---------------------------------------------------------------------- #
def _rot(ax, ang):
    a = np.asarray(ax, dtype=float)
    a = a / np.linalg.norm(a)
    c, s = np.cos(ang), np.sin(ang)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return c * np.eye(3) + s * K + (1 - c) * np.outer(a, a)


def _icos_group():
    f = {tuple(np.round(np.eye(3), 9).flatten()): np.eye(3)}
    fr = [np.eye(3)]
    gens = [_rot([1, 0, 0], np.pi),
            _rot([1, 1, 1], 2 * np.pi / 3),
            _rot([0, 1, phi], 2 * np.pi / 5)]
    for _ in range(300):
        new = []
        for m in fr:
            for g in gens:
                p = g @ m
                k = tuple(np.round(p, 9).flatten())
                if k not in f:
                    f[k] = p
                    new.append(p)
        if not new:
            break
        fr = new
    return list(f.values())


_A5 = _icos_group()
_PROTO = {
    'B': np.array([1.0, 0, 0]),
    'Y': np.array([1, 1, 1]) / np.sqrt(3),
    'R': np.array([0, 1, phi]) / np.sqrt(phi ** 2 + 1),
    'G': np.array([1, 1, 0]) / np.sqrt(2),
}


def _collect_axes():
    out = []
    for name, p in _PROTO.items():
        seen = {}
        for r in _A5:
            v = r @ p
            v = v / np.linalg.norm(v)
            for x in v:
                if abs(x) > 1e-7:
                    if x < 0:
                        v = -v
                    break
            seen[tuple(np.round(v, 7))] = (v, name)
        for v, n in seen.values():
            out.append((v, n))
    return out


_AXES = _collect_axes()
AX_VECS = np.array([a[0] for a in _AXES])
AX_NAMES = [a[1] for a in _AXES]
_G = np.abs(AX_VECS @ AX_VECS.T)
_ALLOWED_COS = np.array(sorted(set(np.round(_G.flatten(), 6))))


def _is_allowed_cos(c, tol=1e-5):
    return bool(np.any(np.abs(_ALLOWED_COS - c) < tol))


def _classify_dir(u, tol=1e-5):
    cs = np.abs(AX_VECS @ u)
    idx = int(np.argmax(cs))
    if abs(cs[idx] - 1) < tol:
        return AX_NAMES[idx]
    return None


def _try_align(P3, tol=1e-5):
    """Given a 3xK array of edge displacements in 3D, attempt to find an
    O(3) rotation R such that every nonzero R @ P3[:,k] lies on a default
    axis.  Return (R, classes) or None."""
    K = P3.shape[1]
    norms = np.linalg.norm(P3, axis=0)
    nz = np.where(norms > tol)[0]
    if len(nz) < 2:
        return None
    U = P3[:, nz] / norms[nz]
    Ur = U.T
    for i in range(len(nz)):
        for j in range(i + 1, len(nz)):
            c = abs(Ur[i] @ Ur[j])
            if not _is_allowed_cos(c, tol):
                return None
    pa = U[:, 0]
    b = None
    for k in range(1, U.shape[1]):
        if np.linalg.norm(np.cross(pa, U[:, k])) > tol:
            b = k
            break
    if b is None:
        return None
    pb = U[:, b]
    cab = pa @ pb
    for ia, (axa, _) in enumerate(_AXES):
        for sa in (1, -1):
            ta = sa * axa
            for ib, (axb, _) in enumerate(_AXES):
                for sb in (1, -1):
                    tb = sb * axb
                    if abs(ta @ tb - cab) > tol:
                        continue
                    e1s = pa
                    v2s = pb - cab * pa
                    n2s = np.linalg.norm(v2s)
                    if n2s < tol:
                        continue
                    e2s = v2s / n2s
                    e3s = np.cross(e1s, e2s)
                    e1t = ta
                    v2t = tb - cab * ta
                    n2t = np.linalg.norm(v2t)
                    if n2t < tol:
                        continue
                    e2t = v2t / n2t
                    e3t = np.cross(e1t, e2t)
                    R = (np.column_stack([e1t, e2t, e3t])
                         @ np.column_stack([e1s, e2s, e3s]).T)
                    classes = []
                    ok = True
                    for c_ in range(K):
                        v = R @ P3[:, c_]
                        L = np.linalg.norm(v)
                        if L < tol:
                            classes.append('_')
                            continue
                        cn = _classify_dir(v / L, tol)
                        if cn is None:
                            ok = False
                            break
                        classes.append(cn)
                    if ok:
                        return R, classes
    return None


# ---------------------------------------------------------------------- #
# Search core
# ---------------------------------------------------------------------- #
def projection_matrix(n):
    n = n / np.linalg.norm(n)
    M = np.eye(4) - np.outer(n, n)
    U, s, Vh = np.linalg.svd(M)
    return U[:, :3].T  # 3 x 4


def gen_dirs(rng=3, integer_only=False, permute_dedup=True):
    """All ZZ[phi]^4 4-tuples with components a+b*phi, |a|<=rng, |b|<=rng
    (or just integer if integer_only).

    With permute_dedup=True (default): also dedup by component permutation
    via sort-by-decreasing-magnitude.  This is correct for polytopes whose
    vertex set is invariant under coordinate permutation (24-cell, 8-cell,
    16-cell, 600-cell, 120-cell, etc.).  Use False for embeddings without
    full S_4 axis-permutation symmetry (e.g. our 5-cell embedding which
    singles out the 4th axis).
    """
    vals = set()
    for a in range(-rng, rng + 1):
        if integer_only:
            vals.add(float(a))
        else:
            for b in range(-rng, rng + 1):
                vals.add(round(a + b * phi, 9))
    vals = sorted(vals)
    out = set()
    for tup in product(vals, repeat=4):
        if all(t == 0 for t in tup):
            continue
        if permute_dedup:
            s = tuple(sorted((abs(t) for t in tup), reverse=True))
        else:
            s = tuple(abs(t) if i != 0 else t for i, t in enumerate(tup))
            # only sign-flip dedup: flip global sign so first nonzero is +
            for t in tup:
                if t != 0:
                    if t < 0:
                        s = tuple(-x for x in tup)
                    else:
                        s = tuple(tup)
                    break
        out.add(s)
    return [np.array(v) for v in out]


def search(rep_name, V, edges, dirs, tol=1e-5, verbose=True):
    """Run the search.  Returns a list of (n_tuple, signature_dict, n_balls)."""
    if verbose:
        print(f"\n=== {rep_name}: {len(dirs)} candidate directions ===")
    found = []
    t0 = time.time()
    E = np.array([V[b] - V[a] for (a, b) in edges]).T
    for n in dirs:
        if np.linalg.norm(n) < 1e-9:
            continue
        Q = projection_matrix(n)
        P = Q @ E
        res = _try_align(P, tol=tol)
        if res is None:
            continue
        R, classes = res
        sig = dict(Counter(classes))
        Vp = (Q @ V.T).T
        balls = set(tuple(np.round(p, 4)) for p in Vp)
        found.append((tuple(np.round(n, 6)), sig, len(balls)))
        if verbose:
            print(f"  HIT n={tuple(np.round(n, 4))}  balls={len(balls)}  sig={sig}")
    if verbose:
        print(f"  ({len(found)} hits, {time.time() - t0:.1f}s)")
    return found


def shape_fingerprint(V, edges, n, tol=1e-3):
    """Rotation+scale-invariant fingerprint of the projected shape.
    Sorted tuple of normalized pairwise squared distances.

    Uses tol=1e-3 for ball deduplication, which is robust to the
    O(1e-5)..O(1e-4) numerical noise that comes from SVD basis ambiguity
    in projection_matrix() (degenerate singular values produce different
    orthonormal bases for n^perp depending on |n|; scaled-equivalent
    directions then yield rotation-equivalent but coordinate-different
    Vp arrays whose pointwise dedup at very-tight tolerance is
    inconsistent)."""
    Q = projection_matrix(n)
    Vp = (Q @ V.T).T
    # dedup balls with generous tol
    balls = []
    for p in Vp:
        for q in balls:
            if np.linalg.norm(p - q) < tol:
                break
        else:
            balls.append(p)
    balls = np.array(balls)
    n_balls = len(balls)
    if n_balls < 2:
        return (n_balls, ())
    d2 = []
    for i in range(n_balls):
        for j in range(i + 1, n_balls):
            d2.append(float(np.linalg.norm(balls[i] - balls[j]) ** 2))
    d2 = sorted(d2)
    s = d2[0]
    if s < tol:
        return (n_balls, tuple(round(x, 3) for x in d2))
    return (n_balls, tuple(round(x / s, 3) for x in d2))


def group_by_shape(hits, V, edges, tol=1e-3):
    """Cluster a list of search-hit results by 3D shape fingerprint."""
    groups = {}
    for n, sig, balls in hits:
        fp = shape_fingerprint(V, edges, np.array(n), tol=tol)
        groups.setdefault(fp, []).append((n, sig, balls))
    return groups
