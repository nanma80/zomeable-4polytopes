"""31 default-color zometool axes (B/Y/R/G) + alignment test.

Lifted verbatim from zomeable-4polytopes/lib/search_engine.py — the
image-side machinery is dimension-agnostic, so it works for 6D→3D
projections too.

Public API:
    AX_VECS, AX_NAMES        — the 31 axes (rows of AX_VECS) and labels
    try_align(P3, tol)       — given 3xK array of displacement vectors,
                               find an O(3) rotation R such that R @ P3[:,k]
                               is parallel to a default axis for every k.
                               Returns (R, classes) or None.
    classify_dir(u, tol)     — for a unit-length 3-vector, return the
                               axis name it's parallel to, or None.
"""
import numpy as np

phi = (1 + 5 ** 0.5) / 2


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


def classify_dir(u, tol=1e-5):
    """For unit-length 3-vector u, return name of axis it's parallel to, or None."""
    cs = np.abs(AX_VECS @ u)
    idx = int(np.argmax(cs))
    if abs(cs[idx] - 1) < tol:
        return AX_NAMES[idx]
    return None


def _check_cos_pairs(U, tol=1e-5):
    """Necessary condition: all pairwise |cos| land on the allowed-cosine list."""
    K = U.shape[1]
    chunk = 16
    allowed = _ALLOWED_COS
    n_allowed = len(allowed)
    for i in range(0, K, chunk):
        Ub = U[:, i:i + chunk]
        Cb = np.abs(Ub.T @ U)
        b = Ub.shape[1]
        j_idx = np.arange(K)
        i_idx = np.arange(i, i + b)[:, None]
        keep = j_idx[None, :] > i_idx
        cos_use = Cb[keep]
        if cos_use.size == 0:
            continue
        idx = np.searchsorted(allowed, cos_use)
        idx_clip = np.clip(idx, 1, n_allowed - 1)
        diff = np.minimum(np.abs(allowed[idx_clip - 1] - cos_use),
                          np.abs(allowed[idx_clip] - cos_use))
        if np.any(diff > tol):
            return False
    return True


def try_align(P3, tol=1e-5):
    """Given a 3xK array of (3D) edge displacements, find an O(3) rotation R
    such that every nonzero R @ P3[:,k] is parallel to a default zome axis.
    Returns (R, [class names]) or None."""
    K = P3.shape[1]
    norms = np.linalg.norm(P3, axis=0)
    nz = np.where(norms > tol)[0]
    if len(nz) < 2:
        return None
    U = P3[:, nz] / norms[nz]
    if not _check_cos_pairs(U, tol=tol):
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
                        cn = classify_dir(v / L, tol)
                        if cn is None:
                            ok = False
                            break
                        classes.append(cn)
                    if ok:
                        return R, classes
    return None


if __name__ == "__main__":
    print(f"Loaded {len(AX_VECS)} default-color zome axes")
    from collections import Counter
    print(f"  by colour: {dict(Counter(AX_NAMES))}")
    print(f"  allowed |cos| values: {len(_ALLOWED_COS)}")
