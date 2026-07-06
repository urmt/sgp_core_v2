"""
Phase 019A — T/N-Matched Null Pipeline

Tests whether MEC spectral separation survives when null ensembles are
matched to actual T, N, T/N ratios and covariance estimation method.

Addressing PRE editor concern: "sample covariance broadening under low T/N
could inflate PR artificially."

Usage:
    python experiments/phase_019/019A_tn_matched_nulls.py [--full]

Outputs:
    - experiments/phase_019/results/019A_results.json
    - experiments/phase_019/results/fig_tn_pr.pdf
    - experiments/phase_019/results/fig_tn_alpha.pdf
    - experiments/phase_019/results/fig_naive_vs_shrinkage.pdf
    - experiments/phase_019/results/fig_distance_shrinkage.pdf
"""

import numpy as np
from numpy import linalg as la
from scipy import linalg as scipy_linalg
from scipy.stats import gaussian_kde
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, json, argparse

# ── Paths ───────────────────────────────────────────────────────────────

DATA_DIR = 'experiments/dynamics/tier2_data'
RESULTS_DIR = 'experiments/phase_019/results'
os.makedirs(RESULTS_DIR, exist_ok=True)

# ── Metric definitions ──────────────────────────────────────────────────

def participation_ratio(eigenvalues):
    eigenvalues = np.real(eigenvalues)
    eigenvalues = eigenvalues[eigenvalues > 0]
    if len(eigenvalues) == 0:
        return 1.0
    s = np.sum(eigenvalues)
    if s < 1e-30:
        return 1.0
    return float(s**2 / np.sum(eigenvalues**2))

def spectral_decay_rate(eigenvalues):
    eigenvalues = np.real(eigenvalues)
    eigenvalues = np.sort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[eigenvalues > 0]
    half = len(eigenvalues) // 2
    if half < 4:
        return 0.0
    k = np.arange(1, half)
    log_vals = np.log(eigenvalues[1:half] + 1e-30)
    coeffs = np.polyfit(k, log_vals, 1)
    return float(np.clip(-coeffs[0], 0.001, 2.0))

# ── Covariance estimators ──────────────────────────────────────────────

def naive_covariance(X):
    """Sample covariance (no regularization)."""
    X = X - X.mean(axis=0)
    C = (X.T @ X) / max(X.shape[0] - 1, 1)
    return C

def ledoit_wolf_shrinkage(X):
    """Ledoit-Wolf shrinkage covariance estimator (simplified)."""
    from sklearn.covariance import LedoitWolf
    X = X - X.mean(axis=0)
    try:
        lw = LedoitWolf().fit(X)
        return lw.covariance_
    except:
        # Fallback to naive
        return (X.T @ X) / max(X.shape[0] - 1, 1)

def oas_shrinkage(X):
    """Oracle Approximating Shrinkage estimator (simplified)."""
    from sklearn.covariance import OAS
    X = X - X.mean(axis=0)
    try:
        oas = OAS().fit(X)
        return oas.covariance_
    except:
        return (X.T @ X) / max(X.shape[0] - 1, 1)

# ── Null generators ────────────────────────────────────────────────────

def generate_iid_gaussian(T, N, rng):
    """i.i.d. Gaussian — baseline MP null."""
    return rng.randn(T, N)

def generate_smoothed_gaussian(T, N, sigma_ms=40, bin_ms=20, rng=None):
    """Gaussian with smoothing matching MEC pipeline."""
    if rng is None:
        rng = np.random.RandomState(42)
    X = rng.randn(T, N)
    # Apply Gaussian smoothing
    sigma_bins = sigma_ms / bin_ms
    kernel_size = int(6 * sigma_bins + 1)
    t = np.arange(kernel_size) - kernel_size // 2
    kernel = np.exp(-0.5 * (t / sigma_bins)**2)
    kernel = kernel / kernel.sum()
    # Vectorized smoothing
    X = np.column_stack([np.convolve(X[:, i], kernel, mode='same') for i in range(min(N, 50))])
    if N > 50:
        X_rest = rng.randn(T, N - 50)
        X_rest = X_rest - X_rest.mean(axis=0)
        X_rest = X_rest / (X_rest.std(axis=0) + 1e-10)
        X = np.hstack([X, X_rest])
    return X

def generate_poisson_spikes(T, N, mean_rate=5.0, bin_ms=20, rng=None):
    """Poisson spike trains with matched firing rates."""
    if rng is None:
        rng = np.random.RandomState(42)
    dt = bin_ms / 1000.0
    rates = rng.exponential(mean_rate, size=N)
    spikes = rng.poisson(rates * dt, size=(T, N)).astype(float)
    return spikes

def generate_shuffled_mec(X_mec, rng):
    """Circular shuffle of MEC data — preserves marginals, destroys correlations."""
    X = X_mec.copy()
    T, N = X.shape
    for i in range(N):
        shift = rng.randint(0, T)
        X[:, i] = np.roll(X[:, i], shift)
    return X

# ── Spectral analysis ─────────────────────────────────────────────────

def analyze_spectrum(C):
    """Compute eigenvalues, PR, alpha from covariance matrix."""
    eigvals = la.eigvalsh(C)
    eigvals = np.sort(eigvals)[::-1]
    pr = participation_ratio(eigvals)
    alpha = spectral_decay_rate(eigvals)
    return eigvals, pr, alpha

def analyze_eigenvectors(C, n_keep=50):
    """Compute IPR and level spacing of top eigenvectors."""
    eigvals, eigvecs = la.eigh(C)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]
    
    n_keep = min(n_keep, len(eigvals))
    top_vecs = eigvecs[:, :n_keep]
    
    # IPR
    ipr = np.sum(top_vecs**4, axis=0)
    
    # Level spacing
    spacing = np.diff(eigvals[:n_keep+1])
    spacing = spacing[spacing > 1e-10]
    
    return {
        'ipr_mean': float(np.mean(ipr)),
        'ipr_std': float(np.std(ipr)),
        'spacing_mean': float(np.mean(spacing)) if len(spacing) > 0 else 0,
        'eigvals': eigvals[:n_keep],
        'eigvecs': top_vecs,
    }

# ── Mahalanobis distance (from Phase 016) ─────────────────────────────

def ensemble_distance_mahalanobis(mec_stats, null_stats):
    """Mahalanobis distance between MEC and null ensemble."""
    mec = np.array(mec_stats)
    null = np.array(null_stats)
    
    if mec.ndim == 1:
        mec = mec.reshape(1, -1)
    if null.ndim == 1:
        null = null.reshape(1, -1)
    
    # Pooled covariance
    n1, n2 = mec.shape[0], null.shape[0]
    if n1 < 2 or n2 < 2:
        # Fall back to Euclidean distance
        mu1 = mec.mean(axis=0)
        mu2 = null.mean(axis=0)
        return float(np.linalg.norm(mu1 - mu2))
    
    cov1 = np.cov(mec.T) if n1 > 1 else np.eye(mec.shape[1]) * 1e-10
    cov2 = np.cov(null.T) if n2 > 1 else np.eye(null.shape[1]) * 1e-10
    cov_pooled = ((n1 - 1) * cov1 + (n2 - 1) * cov2) / (n1 + n2 - 2)
    
    # Add regularization
    cov_pooled += 1e-4 * np.eye(cov_pooled.shape[0])
    
    mu1 = mec.mean(axis=0)
    mu2 = null.mean(axis=0)
    
    d = mu1 - mu2
    try:
        inv = la.inv(cov_pooled)
    except la.LinAlgError:
        inv = la.pinv(cov_pooled)
    
    return float(np.sqrt(d @ inv @ d))

def permutation_test_distance(mec_stats, null_stats, n_perm=5000, seed=42):
    """Permutation test for Mahalanobis distance."""
    rng = np.random.RandomState(seed)
    mec = np.array(mec_stats)
    null = np.array(null_stats)
    combined = np.vstack([mec, null])
    n1 = mec.shape[0]
    
    observed = ensemble_distance_mahalanobis(mec, null)
    
    permuted = np.zeros(n_perm)
    for i in range(n_perm):
        idx = rng.permutation(combined.shape[0])
        permuted[i] = ensemble_distance_mahalanobis(combined[idx[:n1]], combined[idx[n1:]])
    
    p_value = float(np.mean(permuted >= observed))
    return observed, p_value

# ── Data loading ────────────────────────────────────────────────────────

def load_mec_recordings():
    """Load all MEC recordings and extract T, N, T/N."""
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*_FRtensor.npy')))
    recordings = []
    for f in files:
        X = np.load(f)
        if X.ndim == 3:
            X = X.reshape(X.shape[0] * X.shape[1], X.shape[2])
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if X.shape[0] < 10 or X.shape[1] < 5:
            continue
        
        T, N = X.shape
        name = os.path.basename(f).replace('_MEC_FRtensor.npy', '')
        
        recordings.append({
            'name': name,
            'X': X,
            'T': T,
            'N': N,
            'TN_ratio': T / N,
        })
    return recordings

# ── Main pipeline ───────────────────────────────────────────────────────

def run_full_pipeline():
    """Run T/N-matched null comparison for all MEC recordings."""
    print("Phase 019A — T/N-Matched Null Pipeline")
    print("=" * 60)
    
    recordings = load_mec_recordings()
    print(f"Loaded {len(recordings)} MEC recordings")
    
    results = []
    
    for rec in recordings:
        name = rec['name']
        X_mec = rec['X']
        T, N = rec['T'], rec['N']
        TN = rec['TN_ratio']
        
        print(f"\n--- {name}: T={T}, N={N}, T/N={TN:.1f} ---")
        
        # Preprocess MEC data
        X_mec = X_mec - X_mec.mean(axis=0)
        X_mec = X_mec / (X_mec.std(axis=0) + 1e-10)
        
        # Compute MEC covariance (naive and shrinkage)
        C_naive = naive_covariance(X_mec)
        C_shrink = ledoit_wolf_shrinkage(X_mec)
        C_oas = oas_shrinkage(X_mec)
        
        eigvals_naive, pr_naive, alpha_naive = analyze_spectrum(C_naive)
        eigvals_shrink, pr_shrink, alpha_shrink = analyze_spectrum(C_shrink)
        
        print(f"  Naive:    PR={pr_naive:.1f}, alpha={alpha_naive:.4f}")
        print(f"  Shrink:   PR={pr_shrink:.1f}, alpha={alpha_shrink:.4f}")
        
        # Generate matched nulls
        rng = np.random.RandomState(42)
        null_names = ['iid_gaussian', 'smoothed_gaussian', 'poisson', 'shuffled_mec']
        
        null_stats_naive = []
        null_stats_shrink = []
        
        n_null_samples = 10  # Multiple samples per null type
        
        for null_name in null_names:
            for _ in range(n_null_samples):
                if null_name == 'iid_gaussian':
                    X_null = generate_iid_gaussian(T, N, rng)
                elif null_name == 'smoothed_gaussian':
                    X_null = generate_smoothed_gaussian(T, N, sigma_ms=40, bin_ms=20, rng=rng)
                elif null_name == 'poisson':
                    X_null = generate_poisson_spikes(T, N, mean_rate=5.0, bin_ms=20, rng=rng)
                elif null_name == 'shuffled_mec':
                    X_null = generate_shuffled_mec(X_mec, rng)
            
            C_null_naive = naive_covariance(X_null)
            C_null_shrink = ledoit_wolf_shrinkage(X_null)
            
            _, pr_n, alpha_n = analyze_spectrum(C_null_naive)
            _, pr_s, alpha_s = analyze_spectrum(C_null_shrink)
            
            null_stats_naive.append([alpha_n, pr_n])
            null_stats_shrink.append([alpha_s, pr_s])
        
        null_stats_naive = np.array(null_stats_naive)
        null_stats_shrink = np.array(null_stats_shrink)
        
        # Compute distances
        mec_vec_naive = np.array([alpha_naive, pr_naive])
        mec_vec_shrink = np.array([alpha_shrink, pr_shrink])
        
        # Distance to pooled null (naive)
        pooled_null_naive = null_stats_naive.mean(axis=0)
        dist_naive = ensemble_distance_mahalanobis(mec_vec_naive.reshape(1, -1), pooled_null_naive.reshape(1, -1))
        
        # Distance to pooled null (shrinkage)
        pooled_null_shrink = null_stats_shrink.mean(axis=0)
        dist_shrink = ensemble_distance_mahalanobis(mec_vec_shrink.reshape(1, -1), pooled_null_shrink.reshape(1, -1))
        
        print(f"  Distance naive:    {dist_naive:.2f}")
        print(f"  Distance shrink:   {dist_shrink:.2f}")
        
        results.append({
            'name': name,
            'T': int(T),
            'N': int(N),
            'TN_ratio': float(TN),
            'naive': {'pr': float(pr_naive), 'alpha': float(alpha_naive)},
            'shrinkage': {'pr': float(pr_shrink), 'alpha': float(alpha_shrink)},
            'null_naive': null_stats_naive.tolist(),
            'null_shrinkage': null_stats_shrink.tolist(),
            'dist_naive': float(dist_naive),
            'dist_shrinkage': float(dist_shrink),
        })
    
    return results

def run_permutation_tests(results, n_perm=2000):
    """Run permutation tests on key recordings."""
    print("\n\nPermutation tests (n_perm=2000)...")
    
    recordings = load_mec_recordings()
    
    for i, rec in enumerate(recordings):
        name = rec['name']
        print(f"\n  {name}...")
        
        X_mec = rec['X']
        X_mec = X_mec - X_mec.mean(axis=0)
        X_mec = X_mec / (X_mec.std(axis=0) + 1e-10)
        
        C_shrink = ledoit_wolf_shrinkage(X_mec)
        eigvals, pr, alpha = analyze_spectrum(C_shrink)
        mec_vec = np.array([alpha, pr])
        
        # Shuffled MEC null
        rng = np.random.RandomState(42)
        null_vecs = []
        for _ in range(30):
            X_null = generate_shuffled_mec(X_mec, rng)
            X_null = X_null - X_null.mean(axis=0)
            X_null = X_null / (X_null.std(axis=0) + 1e-10)
            C_null = ledoit_wolf_shrinkage(X_null)
            _, pr_n, alpha_n = analyze_spectrum(C_null)
            null_vecs.append([alpha_n, pr_n])
        
        null_vecs = np.array(null_vecs)
        obs, p_val = permutation_test_distance(mec_vec.reshape(1, -1), null_vecs, n_perm=n_perm)
        
        results[i]['perm_test_shuffled'] = {
            'observed_distance': float(obs),
            'p_value': float(p_val),
        }
        print(f"    Distance={obs:.2f}, p={p_val:.4f}")
    
    return results

def generate_figures(results):
    """Generate 4 diagnostic figures."""
    names = [r['name'] for r in results]
    tn_ratios = [r['TN_ratio'] for r in results]
    pr_naive = [r['naive']['pr'] for r in results]
    pr_shrink = [r['shrinkage']['pr'] for r in results]
    alpha_naive = [r['naive']['alpha'] for r in results]
    alpha_shrink = [r['shrinkage']['alpha'] for r in results]
    
    # Figure 1: PR vs T/N
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    
    ax = axes[0]
    ax.scatter(tn_ratios, pr_naive, c='steelblue', s=60, label='Naive', zorder=5)
    ax.scatter(tn_ratios, pr_shrink, c='coral', s=60, marker='s', label='Ledoit-Wolf', zorder=5)
    ax.set_xlabel('T/N ratio')
    ax.set_ylabel('Participation Ratio')
    ax.set_xscale('log')
    ax.legend()
    ax.set_title('PR vs T/N: Naive vs Shrinkage')
    ax.axhline(y=37, color='gray', linestyle='--', alpha=0.5, label='MEC mean')
    
    ax = axes[1]
    ax.scatter(tn_ratios, alpha_naive, c='steelblue', s=60, label='Naive')
    ax.scatter(tn_ratios, alpha_shrink, c='coral', s=60, marker='s', label='Ledoit-Wolf')
    ax.set_xlabel('T/N ratio')
    ax.set_ylabel('Spectral Decay Rate α')
    ax.set_xscale('log')
    ax.legend()
    ax.set_title('α vs T/N: Naive vs Shrinkage')
    ax.axhline(y=0.039, color='gray', linestyle='--', alpha=0.5, label='MEC mean')
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'fig_tn_pr.pdf'), dpi=150, bbox_inches='tight')
    plt.close()
    
    # Figure 2: Naive vs Shrinkage comparison
    fig, ax = plt.subplots(figsize=(6, 6))
    
    ax.scatter(pr_naive, pr_shrink, c='steelblue', s=60, zorder=5)
    lim = max(max(pr_naive), max(pr_shrink)) * 1.1
    ax.plot([0, lim], [0, lim], 'k--', alpha=0.3, label='y=x')
    ax.set_xlabel('PR (Naive)')
    ax.set_ylabel('PR (Ledoit-Wolf)')
    ax.set_title('Naive vs Shrinkage PR')
    ax.legend()
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'fig_naive_vs_shrinkage.pdf'), dpi=150, bbox_inches='tight')
    plt.close()
    
    # Figure 3: Distance comparison
    fig, ax = plt.subplots(figsize=(8, 5))
    
    x = np.arange(len(names))
    width = 0.35
    
    dist_naive = [r['dist_naive'] for r in results]
    dist_shrink = [r['dist_shrinkage'] for r in results]
    
    bars1 = ax.bar(x - width/2, dist_naive, width, label='Naive', color='steelblue', alpha=0.8)
    bars2 = ax.bar(x + width/2, dist_shrink, width, label='Ledoit-Wolf', color='coral', alpha=0.8)
    
    ax.set_xlabel('Recording')
    ax.set_ylabel('Mahalanobis Distance to Null')
    ax.set_title('Distance to Null: Naive vs Shrinkage')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right')
    ax.legend()
    ax.axhline(y=3, color='red', linestyle='--', alpha=0.5, label='p<0.001 threshold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'fig_distance_shrinkage.pdf'), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Figures saved to {RESULTS_DIR}")

# ── Main ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true', help='Run full permutation tests')
    args = parser.parse_args()
    
    results = run_full_pipeline()
    
    if args.full:
        results = run_permutation_tests(results)
    
    # Save results
    with open(os.path.join(RESULTS_DIR, '019A_results.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    generate_figures(results)
    
    # Summary
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    pr_naive = [r['naive']['pr'] for r in results]
    pr_shrink = [r['shrinkage']['pr'] for r in results]
    alpha_naive = [r['naive']['alpha'] for r in results]
    alpha_shrink = [r['shrinkage']['alpha'] for r in results]
    
    print(f"Naive:    PR = {np.mean(pr_naive):.1f} ± {np.std(pr_naive):.1f}, α = {np.mean(alpha_naive):.4f} ± {np.std(alpha_naive):.4f}")
    print(f"Shrink:   PR = {np.mean(pr_shrink):.1f} ± {np.std(pr_shrink):.1f}, α = {np.mean(alpha_shrink):.4f} ± {np.std(alpha_shrink):.4f}")
    
    d_pr = np.mean(pr_naive) - np.mean(pr_shrink)
    print(f"\nPR reduction under shrinkage: {d_pr:.1f} ({d_pr/np.mean(pr_naive)*100:.1f}%)")
    
    dist_naive = [r['dist_naive'] for r in results]
    dist_shrink = [r['dist_shrinkage'] for r in results]
    print(f"\nDistance naive:    {np.mean(dist_naive):.2f} ± {np.std(dist_naive):.2f}")
    print(f"Distance shrink:   {np.mean(dist_shrink):.2f} ± {np.std(dist_shrink):.2f}")
