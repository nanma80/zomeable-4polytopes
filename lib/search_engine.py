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


def _check_cos_pairs(U, tol=1e-5):
    """Vectorised: are all pairwise |cos| in `_ALLOWED_COS` (within `tol`)?

    U: 3 x K, each column unit-length.

    Returns True iff every (i, j) with i < j has |U[:, i] . U[:, j]|
    within `tol` of some entry of `_ALLOWED_COS`.  Chunked along the
    rows so that for large K (e.g. 28800 edges of the omnitruncated
    120-cell) the K x K Gram matrix is never fully materialised.

    The chunk size is small (16) so the `np.any(diff > tol)` early-exit
    fires after only ~chunk*K cosine checks for kernels that fail the
    necessary-condition test.  The cos-pair test is a pure
    necessary-condition check, so smaller chunks just reject failing
    kernels sooner without changing semantics.  Empirically chunk=16
    gives 4-23x speedup over chunk=512 on K=240..2304 polytopes (and
    more on K>=4000 H4 polytopes), with hits-set identical.
    See ongoing_work/probes/bench_search_chunk.py for the regression
    test that validates this.
    """
    K = U.shape[1]
    chunk = 16
    allowed = _ALLOWED_COS
    n_allowed = len(allowed)
    for i in range(0, K, chunk):
        Ub = U[:, i:i + chunk]
        Cb = np.abs(Ub.T @ U)  # b x K
        b = Ub.shape[1]
        # Restrict to strictly upper triangle in the global K x K sense.
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
        # Edge case: when cos_use == allowed[0] exactly,
        # idx_clip-1 == 0 still gives the right answer.
        if np.any(diff > tol):
            return False
    return True


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


def _edge_dir_classes(E, tol=1e-9):
    """Group 4D edge displacements (columns of a 4xK matrix `E`) by
    parallel direction modulo sign.

    Two edges that are scalar multiples of each other (including
    anti-parallel) are mapped to the same class.  This is a *lossless*
    reduction for the cos-pair check and the per-edge classify loop in
    `_try_align`:

      * `_check_cos_pairs` uses `|U_i . U_j|`, which is invariant under
        `U_j -> -U_j` and unchanged when `U_j = c * U_i` for any c != 0
        (always 1 within a class).  So intra-class pairs always pass and
        inter-class pairs depend only on the class direction.
      * `_classify_dir` operates on `v / ||v||` and returns an axis name
        regardless of magnitude, so all members of a class always
        receive the same class label (or both reject).

    Parameters
    ----------
    E : np.ndarray of shape (4, K)
        Edge displacements in 4D.
    tol : float
        Treat ||e|| < tol as a "zero" edge (no class assigned).

    Returns
    -------
    rep_idx : np.ndarray of int, shape (K_distinct,)
        Column indices (into E) of one representative per class.
    class_of : np.ndarray of int, shape (K,)
        For each column of E, the index into `rep_idx` of its class
        (or -1 if the edge is a zero-norm 4D edge, which shouldn't
        happen on the polytopes we sweep but is handled defensively).
    """
    K = E.shape[1]
    norms = np.linalg.norm(E, axis=0)
    seen = {}  # canonicalized direction tuple -> class index
    rep_idx_list = []
    class_of = np.full(K, -1, dtype=np.int64)
    for k in range(K):
        if norms[k] < tol:
            continue
        u = E[:, k] / norms[k]
        # Force sign-canonical: first |x|>tol component positive.
        for x in u:
            if abs(x) > tol:
                if x < 0:
                    u = -u
                break
        key = tuple(np.round(u, 9))
        c = seen.get(key)
        if c is None:
            c = len(rep_idx_list)
            seen[key] = c
            rep_idx_list.append(k)
        class_of[k] = c
    return np.asarray(rep_idx_list, dtype=np.int64), class_of


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


def search(rep_name, V, edges, dirs, tol=1e-5, verbose=True,
           progress_every=None, progress_tag=None):
    """Run the search.  Returns a list of (n_tuple, signature_dict, n_balls).

    Optimisation: edges that are parallel in 4D (scalar multiples of each
    other) are grouped via `_edge_dir_classes`.  The cos-pair check and
    classify loop inside `_try_align` only need one representative per
    class — see `_edge_dir_classes` docstring for the lossless-reduction
    proof.  The full-K classification for the `sig` Counter is recovered
    by indexing reps[class_of[k]].  For highly symmetric polytopes
    (omnitruncated 120-cell, etc.) this reduces K by 50-200x and the
    cos-pair work by 2500-40000x.

    Progress logging (cheap, no per-direction cost):
      verbose=True               -> per-hit print
      verbose='progress'         -> default progress lines every ~8% of dirs
      progress_every=N           -> custom interval (overrides 8% default)
      progress_tag='1/8 cantitr' -> prefix shown in progress lines
    """
    n_dirs = len(dirs)
    show_hits = verbose is True
    show_progress = verbose == 'progress' or progress_every is not None
    if progress_every is None:
        progress_every = max(1, int(n_dirs * 0.08))
    tag = f"  [{progress_tag}]" if progress_tag else "  "
    if verbose is True:
        print(f"\n=== {rep_name}: {n_dirs} candidate directions ===")
    found = []
    t0 = time.time()
    K_full = len(edges)
    E = np.array([V[b] - V[a] for (a, b) in edges]).T
    rep_idx, class_of = _edge_dir_classes(E)
    K_reps = len(rep_idx)
    E_reps = E[:, rep_idx] if K_reps > 0 else E
    if (show_hits or show_progress) and K_reps < K_full:
        print(f"{tag} parallel-edge reduction: K {K_full} -> {K_reps} "
              f"({100.0*K_reps/max(K_full,1):.2f}%)  ndirs={n_dirs}",
              flush=True)
    for i, n in enumerate(dirs):
        if show_progress and i > 0 and i % progress_every == 0:
            elapsed = time.time() - t0
            pct = 100.0 * i / n_dirs
            eta = elapsed * (n_dirs - i) / max(i, 1)
            ts = time.strftime('%H:%M:%S')
            print(f"{tag} {ts}  {pct:5.1f}%  {i}/{n_dirs}  "
                  f"elapsed={elapsed:.1f}s  ETA={eta:.1f}s  "
                  f"hits={len(found)}", flush=True)
        if np.linalg.norm(n) < 1e-9:
            continue
        Q = projection_matrix(n)
        P_reps = Q @ E_reps
        res = _try_align(P_reps, tol=tol)
        if res is None:
            continue
        R, classes_reps = res  # classes_reps has length K_reps
        # Expand to full K for the signature Counter.
        if K_reps == K_full:
            classes_full = classes_reps
        else:
            classes_full = [classes_reps[c] if c >= 0 else '_'
                            for c in class_of]
        sig = dict(Counter(classes_full))
        Vp = (Q @ V.T).T
        balls = set(tuple(np.round(p, 4)) for p in Vp)
        found.append((tuple(np.round(n, 6)), sig, len(balls)))
        if show_hits:
            print(f"  HIT n={tuple(np.round(n, 4))}  balls={len(balls)}  sig={sig}")
    if show_progress:
        elapsed = time.time() - t0
        ts = time.strftime('%H:%M:%S')
        print(f"{tag} {ts}  100.0%  {n_dirs}/{n_dirs}  "
              f"elapsed={elapsed:.1f}s  ETA=0.0s  hits={len(found)}",
              flush=True)
    if show_hits:
        print(f"  ({len(found)} hits, {time.time() - t0:.1f}s)")
    return found


def shape_fingerprint(V, edges, n, tol=1e-3, large_n_balls=5000):
    """Rotation+scale-invariant fingerprint of the projected shape.
    Sorted tuple of normalized pairwise squared distances.

    Uses tol=1e-3 for ball deduplication, which is robust to the
    O(1e-5)..O(1e-4) numerical noise that comes from SVD basis ambiguity
    in projection_matrix() (degenerate singular values produce different
    orthonormal bases for n^perp depending on |n|; scaled-equivalent
    directions then yield rotation-equivalent but coordinate-different
    Vp arrays whose pointwise dedup at very-tight tolerance is
    inconsistent).

    Vectorised: uses scipy.spatial.cKDTree for O(N log N) greedy first-
    encounter ball dedup (semantics-equivalent to the previous O(N^2)
    Python double-loop), and the numpy Gram-matrix trick for O(M^2)
    pairwise distances on the M deduped balls (chunked when M is big
    enough that the M x M matrix wouldn't fit comfortably in memory).

    For n_balls > large_n_balls the M^2 sorted distance tuple is too
    bulky to materialise (M=14400 -> ~3 GB per call, accumulates across
    ~30 unique shapes for the H4 omnitruncated 120-cell into >40 GB
    even with proper Python-side dereferencing because of numpy arena
    behaviour).  In that regime we instead build a multiset hash:
    iterate chunks, accumulate (rounded normalised distance -> count)
    into a Counter, and return ``(n_balls, ('multiset', sorted_items))``.
    The multiset is order-independent (so the fingerprint stays a
    function of the shape, not the ball ordering) and at most
    ~few-thousand entries (one per distinct rounded distance value),
    which keeps the per-call peak memory at O(chunk + |distinct|).
    """
    from scipy.spatial import cKDTree
    Q = projection_matrix(n)
    Vp = (Q @ V.T).T
    # Greedy first-encounter dedup via KDTree.  Preserves the original
    # behaviour where each cluster's representative is the first point
    # of V to land in that cluster.
    tree = cKDTree(Vp)
    seen = np.zeros(len(Vp), dtype=bool)
    balls_idx = []
    for i in range(len(Vp)):
        if seen[i]:
            continue
        balls_idx.append(i)
        nbrs = tree.query_ball_point(Vp[i], tol)
        seen[nbrs] = True
    balls = Vp[balls_idx]
    n_balls = len(balls)
    if n_balls < 2:
        return (n_balls, ())

    sq = (balls * balls).sum(axis=1)

    # Memory-bounded path for very large polytopes.
    if n_balls > large_n_balls:
        chunk = 2048
        # Pass 1: find smallest non-zero squared distance for normalisation.
        s_min = float("inf")
        for i in range(0, n_balls, chunk):
            Bi = balls[i:i + chunk]
            sqi = sq[i:i + chunk]
            for j in range(i, n_balls, chunk):
                Bj = balls[j:j + chunk]
                sqj = sq[j:j + chunk]
                D2 = sqi[:, None] + sqj[None, :] - 2.0 * (Bi @ Bj.T)
                if i == j:
                    iu = np.triu_indices(D2.shape[0], k=1)
                    flat = D2[iu]
                else:
                    flat = D2.ravel()
                pos = flat[flat > tol]
                if pos.size:
                    cmin = float(pos.min())
                    if cmin < s_min:
                        s_min = cmin
        if s_min == float("inf"):
            return (n_balls, ())
        # Pass 2: build a bincount of the quantised normalised distances
        # (round((d / s_min), 3) * 1000 -> non-negative int).  Using
        # numpy's bincount keeps the per-chunk update O(chunk_size) and
        # vectorised; the accumulator grows lazily as larger normalised
        # distances are seen.
        inv_scaled = 1000.0 / s_min
        bins = np.zeros(0, dtype=np.int64)
        for i in range(0, n_balls, chunk):
            Bi = balls[i:i + chunk]
            sqi = sq[i:i + chunk]
            for j in range(i, n_balls, chunk):
                Bj = balls[j:j + chunk]
                sqj = sq[j:j + chunk]
                D2 = sqi[:, None] + sqj[None, :] - 2.0 * (Bi @ Bj.T)
                if i == j:
                    iu = np.triu_indices(D2.shape[0], k=1)
                    flat = D2[iu]
                else:
                    flat = D2.ravel()
                # Floating-point arithmetic can make the smallest distance
                # come out a hair below s_min on a different chunk; clamp
                # to >= 0 before integer rounding to avoid bogus negative
                # bin indices.
                q = np.maximum(np.round(flat * inv_scaled), 0.0).astype(np.int64)
                bc = np.bincount(q)
                if bc.size > bins.size:
                    new_bins = np.zeros(bc.size, dtype=np.int64)
                    new_bins[:bins.size] = bins
                    bins = new_bins
                bins[:bc.size] += bc
        nz = np.flatnonzero(bins)
        items = tuple((round(int(k) / 1000.0, 3), int(bins[k]))
                      for k in nz.tolist())
        return (n_balls, ("multiset", items))

    # Small / medium n_balls: original sorted-tuple path.
    if n_balls <= 8000:
        D2 = sq[:, None] + sq[None, :] - 2.0 * (balls @ balls.T)
        iu = np.triu_indices(n_balls, k=1)
        d2 = np.sort(D2[iu])
    else:
        chunk = 2048
        out = []
        for i in range(0, n_balls, chunk):
            Bi = balls[i:i + chunk]
            sqi = sq[i:i + chunk]
            for j in range(i, n_balls, chunk):
                Bj = balls[j:j + chunk]
                sqj = sq[j:j + chunk]
                D2 = sqi[:, None] + sqj[None, :] - 2.0 * (Bi @ Bj.T)
                if i == j:
                    iu = np.triu_indices(D2.shape[0], k=1)
                    out.append(D2[iu])
                else:
                    out.append(D2.ravel())
        d2 = np.sort(np.concatenate(out))

    s = float(d2[0])
    if s < tol:
        return (n_balls, tuple(round(float(x), 3) for x in d2))
    return (n_balls, tuple(round(float(x / s), 3) for x in d2))


def group_by_shape(hits, V, edges, tol=1e-3):
    """Cluster a list of search-hit results by 3D shape fingerprint."""
    groups = {}
    for n, sig, balls in hits:
        fp = shape_fingerprint(V, edges, np.array(n), tol=tol)
        groups.setdefault(fp, []).append((n, sig, balls))
    return groups
