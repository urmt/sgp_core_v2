"""Transfer entropy: directional information flow between components.

TE(Y → X) = I(X_t; Y_{t-τ} | X_{t-τ})

High TE = Y's past helps predict X's future beyond X's own past.
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.special import digamma


def _ksg_mi_raw(x: np.ndarray, y: np.ndarray, k: int = 5) -> float:
    """KSG mutual information I(X;Y). Vectorized. x,y shape: (n, d_x), (n, d_y)."""
    n = x.shape[0]
    xy = np.hstack([x, y])
    nbrs = NearestNeighbors(n_neighbors=k, metric="chebyshev")
    nbrs.fit(xy)
    dist, _ = nbrs.kneighbors(xy)
    eps = np.maximum(dist[:, -1], 1e-30)

    if x.shape[1] == 1:
        diff_x = np.abs(x[:, 0:1] - x[:, 0:1].T)
    else:
        diff_x = np.max(np.abs(x[:, None] - x[None, :]), axis=2)
    if y.shape[1] == 1:
        diff_y = np.abs(y[:, 0:1] - y[:, 0:1].T)
    else:
        diff_y = np.max(np.abs(y[:, None] - y[None, :]), axis=2)

    counts_x = np.sum(diff_x < eps[:, None], axis=1) - 1
    counts_y = np.sum(diff_y < eps[:, None], axis=1) - 1

    mi = digamma(k) + digamma(n) - np.mean(digamma(counts_x + 1) + digamma(counts_y + 1))
    return float(max(mi, 0.0))


def _transfer_entropy(
    src_past: np.ndarray, tgt_present: np.ndarray, tgt_past: np.ndarray, k: int = 5
) -> float:
    """TE = I(target_t; source_{t-τ}, target_{t-τ}) - I(target_t; target_{t-τ})"""
    x = tgt_present.reshape(-1, 1)
    y = src_past.reshape(-1, 1)
    z = tgt_past.reshape(-1, 1)

    mi_xyz = _ksg_mi_raw(x, np.hstack([y, z]), k)
    mi_xz = _ksg_mi_raw(x, z, k)
    return float(max(mi_xyz - mi_xz, 0.0))


def compute_transfer_entropy_matrix(
    X: np.ndarray, tau: int = 1, k: int = 5
) -> np.ndarray:
    """Pairwise transfer entropy matrix TE_{i→j}.

    X shape: (n_components, n_timepoints).
    Returns (n_components, n_components) matrix.
    """
    X = np.asarray(X, dtype=np.float64)
    X = X - X.mean(axis=1, keepdims=True)
    std = np.maximum(X.std(axis=1, keepdims=True), 1e-30)
    X = X / std

    n_comp, T = X.shape
    te = np.zeros((n_comp, n_comp))

    X_t = X[:, tau:]
    X_tau = X[:, :-tau]

    for src in range(n_comp):
        for tgt in range(n_comp):
            if src == tgt:
                continue
            te[src, tgt] = _transfer_entropy(X_tau[src], X_t[tgt], X_tau[tgt], k)

    return te


def compute_transfer_entropy_summary(X: np.ndarray, tau: int = 1, k: int = 5) -> dict:
    """Summary statistics of the transfer entropy matrix."""
    te = compute_transfer_entropy_matrix(X, tau, k)
    return {
        "matrix": te.tolist(),
        "mean": float(np.mean(te)),
        "max": float(np.max(te)),
        "num_directed_edges": int(np.sum(te > 0.01)),
        "avg_in_degree": float(np.mean(np.sum(te > 0.01, axis=0))),
        "avg_out_degree": float(np.mean(np.sum(te > 0.01, axis=1))),
    }
