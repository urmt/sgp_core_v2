import numpy as np
from numpy import linalg as la

def canonical_alpha(eigvals):
    s = np.sort(eigvals)[::-1]
    half = len(s) // 2
    if half < 4:
        return 0.0
    valid = s[1:half] > 1e-10
    if valid.sum() < 3:
        return 0.0
    coeffs = np.polyfit(np.arange(1, half)[valid], np.log(np.maximum(s[1:half][valid], 1e-10)), 1)
    return float(max(-coeffs[0], 0.0))

def participation_ratio(eigvals):
    ev = np.abs(eigvals)
    s = np.sum(ev)
    if s < 1e-15:
        return float(len(ev))
    return float((np.sum(ev) ** 2) / np.sum(ev ** 2))

def compute_metrics(X):
    X = X - X.mean(axis=0)
    std = X.std(axis=0) + 1e-10
    X = X / std
    C = (X.T @ X) / max(X.shape[0] - 1, 1)
    evals = la.eigh(C)[0]
    evals = evals[evals > 1e-12]
    alpha = canonical_alpha(evals)
    pr = participation_ratio(evals)
    U, s, Vt = la.svd(X, full_matrices=False)
    cumvar = np.cumsum(s**2) / np.sum(s**2)
    n_95 = int(np.searchsorted(cumvar, 0.95) + 1)
    X_proj = U[:, :n_95] @ np.diag(s[:n_95]) @ Vt[:n_95, :]
    lc = float(np.log10(np.sum((X - X_proj)**2) / np.maximum(np.sum(X**2), 1e-15)))
    return {'alpha': alpha, 'PR': pr, 'LC': lc, 'N': X.shape[1]}

def gaussian_smoothing(spikes, sigma_ms=40, bin_ms=20):
    from scipy.ndimage import gaussian_filter1d
    sigma_bins = sigma_ms / bin_ms
    if sigma_bins < 0.5:
        return spikes
    return gaussian_filter1d(spikes.astype(np.float64), sigma=sigma_bins, axis=0)

def standard_pipeline(spike_counts, bin_ms=20, sigma_ms=40):
    smoothed = gaussian_smoothing(spike_counts, sigma_ms, bin_ms)
    return smoothed
