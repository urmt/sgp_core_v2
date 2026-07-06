"""
Statistical comparison tools for ensemble distance estimation.
Replaces ad-hoc Euclidean σ-normalized distance with covariance-aware metrics.

Functions:
  mahalanobis_distance(μ1, μ2, cov)  — Mahalanobis distance between two distributions
  permutation_test(X, Y, metric_fn)  — label-shuffle significance test
  bootstrap_ci(data, statistic_fn)   — bias-corrected accelerated bootstrap CI
  ensemble_distance(mec_stats, null_stats)  — full pipeline: D_M + p-value + CI
"""

import numpy as np
from numpy import linalg as la

def mahalanobis_distance(μ1, μ2, cov):
    """Mahalanobis distance D_M = sqrt((μ1-μ2)^T Σ^{-1} (μ1-μ2))."""
    d = np.array(μ1) - np.array(μ2)
    try:
        inv = la.inv(cov)
    except la.LinAlgError:
        inv = la.pinv(cov)
    return float(np.sqrt(d @ inv @ d))

def permutation_test(X, Y, metric_fn, n_perm=10000, seed=42):
    """
    Permutation test for separation between two multivariate samples.
    
    Args:
        X: (n1, d) array of MEC statistics
        Y: (n2, d) array of null statistics
        metric_fn: callable (X, Y) -> scalar distance
        n_perm: number of label shuffles
        seed: RNG seed
    
    Returns:
        observed: distance on true labels
        p_value: fraction of permuted distances ≥ observed
        perm_dist: array of n_perm distances under shuffle
    """
    rng = np.random.RandomState(seed)
    combined = np.vstack([X, Y])
    n1 = X.shape[0]
    n_tot = combined.shape[0]
    
    observed = metric_fn(X, Y)
    permuted = np.zeros(n_perm)
    
    for i in range(n_perm):
        idx = rng.permutation(n_tot)
        X_perm = combined[idx[:n1]]
        Y_perm = combined[idx[n1:]]
        permuted[i] = metric_fn(X_perm, Y_perm)
    
    p_value = float(np.mean(permuted >= observed))
    return observed, p_value, permuted

def bootstrap_ci(data, statistic_fn, n_resample=10000, ci=0.95, seed=42):
    """
    Bias-corrected accelerated bootstrap confidence interval.
    
    Args:
        data: (n_samples, d) array
        statistic_fn: callable (sample) -> scalar or array
        n_resample: bootstrap iterations
        ci: confidence level (e.g., 0.95)
        seed: RNG seed
    
    Returns:
        point: statistic on original data
        lower: lower CI bound
        upper: upper CI bound
    """
    rng = np.random.RandomState(seed)
    n = data.shape[0]
    point = statistic_fn(data)
    
    boot_stats = np.zeros(n_resample)
    for i in range(n_resample):
        idx = rng.randint(0, n, size=n)
        boot_stats[i] = statistic_fn(data[idx])
    
    alpha = (1 - ci) / 2
    lower = float(np.percentile(boot_stats, alpha * 100))
    upper = float(np.percentile(boot_stats, (1 - alpha) * 100))
    
    return point, lower, upper, boot_stats

def _pooled_cov(X, Y):
    """Pooled covariance matrix of two samples."""
    n1, n2 = X.shape[0], Y.shape[0]
    cov1 = np.cov(X, rowvar=False)
    cov2 = np.cov(Y, rowvar=False)
    return ((n1 - 1) * cov1 + (n2 - 1) * cov2) / max(n1 + n2 - 2, 1)

def _mahl_metric(X, Y):
    """Metric function for permutation test: Mahalanobis distance."""
    μ1 = X.mean(axis=0)
    μ2 = Y.mean(axis=0)
    cov = _pooled_cov(X, Y)
    return mahalanobis_distance(μ1, μ2, cov)

def ensemble_distance(mec_stats, null_stats, n_perm=10000):
    """
    Full ensemble comparison pipeline.
    
    Args:
        mec_stats: (n_mec, d) array of MEC statistics
        null_stats: (n_null, d) array of null statistics
        n_perm: permutation iterations
    
    Returns:
        dict with keys:
            D_M: Mahalanobis distance
            p_value: permutation test significance
            D_M_95CI_lower: bootstrap lower CI for D_M
            D_M_95CI_upper: bootstrap upper CI for D_M
            n_mec: number of MEC samples
            n_null: number of null samples
    """
    d_obs, p_val, _ = permutation_test(
        mec_stats, null_stats, _mahl_metric, n_perm=n_perm
    )
    
    null_mean = null_stats.mean(axis=0)
    null_cov = np.cov(null_stats, rowvar=False)
    
    def _dm_bootstrap(mec_sample):
        μ1 = mec_sample.mean(axis=0)
        cov = _pooled_cov(mec_sample, null_stats)
        return mahalanobis_distance(μ1, null_mean, cov)
    
    _, d_lower, d_upper, _ = bootstrap_ci(
        mec_stats, _dm_bootstrap, n_resample=5000
    )
    
    return {
        'D_M': round(d_obs, 3),
        'p_value': p_val,
        'D_M_95CI_lower': round(d_lower, 3),
        'D_M_95CI_upper': round(d_upper, 3),
        'n_mec': mec_stats.shape[0],
        'n_null': null_stats.shape[0],
    }

def format_comparison(name, result):
    """Format a comparison result as a printable string."""
    stars = ''
    if result['p_value'] < 0.001:
        stars = '***'
    elif result['p_value'] < 0.01:
        stars = '**'
    elif result['p_value'] < 0.05:
        stars = '*'
    
    return (f"  {name:<30s}  D_M={result['D_M']:.2f}  "
            f"95%CI=[{result['D_M_95CI_lower']:.2f}, {result['D_M_95CI_upper']:.2f}]  "
            f"p={result['p_value']:.4f}{stars}  "
            f"(MEC n={result['n_mec']}, null n={result['n_null']})")

if __name__ == '__main__':
    print("Statistical comparison module loaded.")
    print("Functions: mahalanobis_distance, permutation_test, bootstrap_ci, ensemble_distance")
