"""Statistical complexity: C_σ = H(X_t) - I(X_t; X_{t-τ}).

The remaining entropy after accounting for predictive information.
High C_σ = system has structure that is neither fully random nor fully predictable.

For multivariate systems, we use the joint entropy and joint predictive information.
"""

import numpy as np
from .total_correlation import _gaussian_entropy, _normalize
from .predictive_information import compute_predictive_information


def compute_statistical_complexity(
    X: np.ndarray, tau: int = 1, k: int = 5
) -> float:
    """C_σ = H(X) - I_pred. In nats."""
    X = np.asarray(X, dtype=np.float64)
    Xn = _normalize(X)
    H = _gaussian_entropy(Xn)
    I_pred = compute_predictive_information(X, tau, k)
    return float(max(H - I_pred, 0.0))


def compute_statistical_complexity_ci(
    X: np.ndarray, tau: int = 1, k: int = 5,
    n_bootstrap: int = 200, seed: int = 42,
) -> tuple[float, float, float]:
    """Statistical complexity with bootstrap CI. Returns (mean, lower, upper)."""
    point = compute_statistical_complexity(X, tau, k)
    rng = np.random.default_rng(seed)
    _, T = X.shape
    vals = np.zeros(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integers(0, T, size=T)
        vals[i] = compute_statistical_complexity(X[:, idx], tau, k)
    alpha = 0.05
    lower = float(np.percentile(vals, 100 * alpha / 2))
    upper = float(np.percentile(vals, 100 * (1 - alpha / 2)))
    return (point, lower, upper)
