"""Predictive information: I_pred(τ) = I(X_t; X_{t-τ}).

The mutual information between a system's present state and its past state.
High predictive information = system is predictable from its own history.
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.special import digamma


def _ksg_mi(x: np.ndarray, y: np.ndarray, k: int = 5) -> float:
    """KSG mutual information I(X;Y). x, y shape: (n_samples, d_x) and (n_samples, d_y)."""
    n = x.shape[0]
    xy = np.hstack([x, y])
    d_xy = xy.shape[1]
    nbrs = NearestNeighbors(n_neighbors=k, metric="chebyshev")
    nbrs.fit(xy)
    dist, _ = nbrs.kneighbors(xy)
    eps = np.maximum(dist[:, -1], 1e-30)

    counts_x = np.zeros(n)
    counts_y = np.zeros(n)
    for i in range(n):
        dx = np.max(np.abs(x - x[i:i+1]), axis=1)
        dy = np.max(np.abs(y - y[i:i+1]), axis=1)
        counts_x[i] = np.sum(dx < eps[i]) - 1
        counts_y[i] = np.sum(dy < eps[i]) - 1

    mi = digamma(k) + digamma(n) - np.mean(digamma(counts_x + 1) + digamma(counts_y + 1))
    return float(max(mi, 0.0))


def compute_predictive_information(
    X: np.ndarray, tau: int = 1, k: int = 5
) -> float:
    """Predictive information I(X_t; X_{t-τ}) for multivariate time series.

    X shape: (n_components, n_timepoints).
    """
    X = np.asarray(X, dtype=np.float64)
    X = X - X.mean(axis=1, keepdims=True)
    std = np.maximum(X.std(axis=1, keepdims=True), 1e-30)
    X = X / std

    X_t = X[:, tau:].T
    X_tau = X[:, :-tau].T
    return _ksg_mi(X_t, X_tau, k)


def compute_predictive_information_ci(
    X: np.ndarray, tau: int = 1, k: int = 5,
    n_bootstrap: int = 200, seed: int = 42,
) -> tuple[float, float, float]:
    """Predictive information with bootstrap CI. Returns (mean, lower, upper)."""
    point = compute_predictive_information(X, tau, k)
    rng = np.random.default_rng(seed)
    _, T = X.shape
    vals = np.zeros(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integers(0, T, size=T)
        vals[i] = compute_predictive_information(X[:, idx], tau, k)
    alpha = 0.05
    lower = float(np.percentile(vals, 100 * alpha / 2))
    upper = float(np.percentile(vals, 100 * (1 - alpha / 2)))
    return (point, lower, upper)
