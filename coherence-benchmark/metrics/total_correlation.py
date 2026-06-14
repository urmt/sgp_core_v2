"""Normalized total correlation estimator.

C = T(X_1; ... ; X_n) / H(X_1, ..., X_n)

where T = sum(H(X_i)) - H(X_1, ..., X_n) is the total correlation (multi-information).

Three estimators:
- 'gaussian' (default): Gaussian copula. Stable, unbiased for Gaussian data, lower bound otherwise.
- 'knn': Kozachenko-Leonenko. Fast but dimension-biased — only reliable for d <= 5.
- 'ksg': KSG adaptive estimator. Corrects the cross-dimensional bias.

All public functions accept X with shape (n_components, n_timepoints).
"""

import numpy as np
from scipy.special import digamma, gammaln
from sklearn.neighbors import NearestNeighbors


EPS = 1e-30


def _log_ball_volume(d: int) -> float:
    if d == 0:
        return 0.0
    return (d / 2) * np.log(np.pi) - gammaln(d / 2 + 1)


def _knn_entropy(X: np.ndarray, k: int = 3) -> float:
    """Kozachenko-Leonenko kNN entropy estimator.

    X shape: (n_samples, n_features). Returns H in nats.
    Biased for d > ~5 at typical sample sizes.
    """
    n, d = X.shape
    if n <= k + 1:
        raise ValueError(f"n_samples ({n}) must be > k+1 ({k+1})")
    if d == 0:
        return 0.0

    nbrs = NearestNeighbors(n_neighbors=k, metric="euclidean")
    nbrs.fit(X)
    distances, _ = nbrs.kneighbors(X)
    r_k = np.maximum(distances[:, -1], EPS)
    safe_log_eps = np.mean(np.log(r_k))
    log_vd = _log_ball_volume(d)
    entropy = digamma(n) - digamma(k) + d * safe_log_eps + log_vd
    return float(entropy)


def _gaussian_entropy(X: np.ndarray) -> float:
    """Entropy under Gaussian assumption.

    X shape: (n_components, n_timepoints). Returns H in nats.
    """
    d, _ = X.shape
    cov = np.cov(X, rowvar=True)
    sign, logdet = np.linalg.slogdet(cov)
    if sign <= 0:
        trace = np.trace(cov)
        return 0.5 * (d * np.log(2 * np.pi * np.e * trace / max(d, 1)))
    return 0.5 * (logdet + d * np.log(2 * np.pi * np.e))


def _total_correlation_gaussian(X: np.ndarray) -> float:
    """Total correlation via Gaussian copula: -0.5 * log(det(C)).

    X shape: (n_components, n_timepoints). Uses shrinkage regularization.
    """
    corr = np.corrcoef(X, rowvar=True)

    mask = np.isfinite(corr).all(axis=1)
    corr = corr[mask][:, mask]
    d = corr.shape[0]
    if d < 2:
        return 0.0

    alpha = 1e-6
    corr = (1 - alpha) * corr + alpha * np.eye(d)
    sign, logdet = np.linalg.slogdet(corr)
    if sign <= 0:
        return 0.0
    return float(-0.5 * logdet)


def _total_correlation_ksg(X: np.ndarray, k: int = 5) -> float:
    """KSG adaptive estimator for total correlation.

    Uses the k-th NN in the joint space to define adaptive bandwidth,
    then counts neighbors in each marginal within that bandwidth.
    This cancels the dimension-dependent bias.

    X shape: (n_samples, n_features) where samples = timepoints, features = components.
    """
    n, d = X.shape
    if n <= k + 1 or d < 2:
        return 0.0

    nbrs = NearestNeighbors(n_neighbors=k, metric="chebyshev")
    nbrs.fit(X)
    distances, _ = nbrs.kneighbors(X)
    epsilons = np.maximum(distances[:, -1], EPS)

    counts = np.zeros((n, d))
    for j in range(d):
        marginal = X[:, j:j+1]
        for i in range(n):
            diff = np.abs(marginal[:, 0] - marginal[i, 0])
            counts[i, j] = np.sum(diff < epsilons[i]) - 1

    psi_n = digamma(n)
    psi_k = digamma(k)
    term = np.mean([np.sum(digamma(c + 1)) for c in counts])

    total = (d - 1) * psi_n + psi_k - term
    return float(max(total, 0.0))


def _total_correlation_knn(X: np.ndarray, k: int = 3) -> float:
    """Total correlation via kNN entropy estimation.

    X shape: (n_samples, n_features). NOTE: biased for d > 5.
    """
    _, d = X.shape
    joint_h = _knn_entropy(X, k)
    marginal_hs = np.array([_knn_entropy(X[:, i:i+1], k) for i in range(d)])
    total = float(np.sum(marginal_hs) - joint_h)
    return max(total, 0.0)


def _normalize(X: np.ndarray) -> np.ndarray:
    """Z-score each component. X shape: (n_components, n_timepoints)."""
    X = np.asarray(X, dtype=np.float64)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    X = np.clip(X, -1e6, 1e6)
    X = X - X.mean(axis=1, keepdims=True)
    std = X.std(axis=1, keepdims=True)
    std = np.maximum(std, EPS)
    return X / std


def compute_C(X: np.ndarray, estimator: str = "gaussian", k: int = 3) -> float:
    """Compute normalized total correlation C in [0, 1].

    Uses robust normalization: C = T / (T + sum(H_i)) where T is total
    correlation and sum(H_i) is sum of marginal entropies. This formulation
    handles negative joint entropies (possible with differential entropy on
    highly correlated data) and guarantees C in [0, 1].

    X shape: (n_components, n_timepoints).

    Estimators:
    - 'gaussian' (default): stable, unbiased for Gaussian, lower bound otherwise
    - 'knn': Kozachenko-Leonenko, biased for d > 5
    - 'ksg': KSG adaptive, corrects cross-dimensional bias
    """
    X = _normalize(X)

    if estimator == "knn":
        X_knn = X.T
        total = _total_correlation_knn(X_knn, k)
        sum_marginal_h = float(np.sum([_knn_entropy(X_knn[:, i:i+1], k) for i in range(X_knn.shape[1])]))
    elif estimator == "ksg":
        X_ksg = X.T
        total = _total_correlation_ksg(X_ksg, k)
        sum_marginal_h = float(np.sum([_knn_entropy(X_ksg[:, i:i+1], k) for i in range(X_ksg.shape[1])]))
    elif estimator == "gaussian":
        total = _total_correlation_gaussian(X)
        sum_marginal_h = 0.5 * X.shape[0] * np.log(2 * np.pi * np.e)
    else:
        raise ValueError(f"Unknown estimator: {estimator}")

    if sum_marginal_h <= 0 or np.isinf(sum_marginal_h) or np.isnan(sum_marginal_h):
        return 0.0

    C_val = total / (total + sum_marginal_h)
    return float(np.clip(C_val, 0.0, 1.0))


def _bootstrap_sample(X: np.ndarray, seed: int) -> np.ndarray:
    """One bootstrap sample of timepoints. X shape: (n_components, n_timepoints)."""
    rng = np.random.default_rng(seed)
    _, T = X.shape
    idx = rng.integers(0, T, size=T)
    return X[:, idx]


def compute_C_ci(
    X: np.ndarray,
    estimator: str = "gaussian",
    k: int = 3,
    n_bootstrap: int = 200,
    ci_level: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """C with bootstrap confidence interval. Returns (mean, lower, upper)."""
    point_estimate = compute_C(X, estimator=estimator, k=k)

    boot_values = np.zeros(n_bootstrap)
    for i in range(n_bootstrap):
        X_boot = _bootstrap_sample(X, seed + i)
        boot_values[i] = compute_C(X_boot, estimator=estimator, k=k)

    alpha = 1.0 - ci_level
    lower = float(np.percentile(boot_values, 100 * alpha / 2))
    upper = float(np.percentile(boot_values, 100 * (1 - alpha / 2)))

    return (point_estimate, lower, upper)
