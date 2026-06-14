"""Multiscale entropy (MSE): sample entropy at multiple time scales.

At scale s, the coarse-grained time series is:
y_j^s = (1/s) * Σ_{i=(j-1)s+1}^{js} x_i

Sample entropy at each scale measures the conditional probability
that two sequences similar for m points remain similar at m+1.
"""

import numpy as np


def _sample_entropy(x: np.ndarray, m: int = 2, r: float = 0.2) -> float:
    """Sample entropy of a 1D time series at tolerance r * std(x).

    Lower SampEn = more regular/ predictable.
    Uses vectorized Chebyshev distance.
    """
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    std = x.std()
    if std < 1e-10:
        return 0.0
    r_abs = r * std

    def _count_matches(template_len: int) -> int:
        k = n - template_len
        shape = (k, template_len)
        strides = (x.strides[0], x.strides[0])
        templates = np.lib.stride_tricks.as_strided(x, shape=shape, strides=strides)
        diffs = np.max(np.abs(templates[:, None] - templates[None, :]), axis=2)
        matches = np.sum(diffs < r_abs) - k
        return max(matches // 2, 0)

    B = _count_matches(m)
    A = _count_matches(m + 1)
    if B == 0 or A == 0:
        return 0.0
    return float(-np.log(A / B))


def compute_mse(
    X: np.ndarray, scales: list[int] | None = None,
    m: int = 2, r: float = 0.2,
) -> dict:
    """Multiscale entropy across components.

    X shape: (n_components, n_timepoints).
    Returns {scale: mean_sample_entropy_across_components}.
    """
    X = np.asarray(X, dtype=np.float64)
    n_comp, T = X.shape
    if scales is None:
        scales = list(range(1, min(T // 10, 21)))

    result = {}
    for s in scales:
        n_coarse = T // s
        if n_coarse < m + 2:
            continue
        coarse = X[:, :n_coarse * s].reshape(n_comp, n_coarse, s).mean(axis=2)
        se_values = []
        for i in range(n_comp):
            se = _sample_entropy(coarse[i], m, r)
            if np.isfinite(se):
                se_values.append(se)
        result[s] = float(np.mean(se_values)) if se_values else 0.0

    return result
