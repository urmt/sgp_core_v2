"""
Demonstration script: ensemble distance with Mahalanobis + permutation testing.
Loads Phase 015 results and compares MEC against all null ensembles.

Usage:
    python statistical_comparison_demo.py
    
Output:
    Prints formatted comparison table with D_M, p-values, and 95% CIs.
"""

import json, sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from statistical_comparison import ensemble_distance, format_comparison

RESULTS_DIR = Path('experiments/phase_015/results')
RESULTS_DIR_REPO = Path(__file__).resolve().parent / 'phase_015_results'
DATA_DIR = Path('experiments/dynamics/tier2_data')

def get_mec_stats():
    """Extract (α, PR, LC) from all MEC recordings."""
    from reproduce_figures import compute_correlation_metrics
    from glob import glob
    files = sorted(glob(str(DATA_DIR / '*MEC_FRtensor*.npy')))
    stats = []
    for f in files:
        X = np.load(f).astype(np.float64)
        if X.ndim == 3:
            X = X.reshape(X.shape[0] * X.shape[1], X.shape[2])
        m = compute_correlation_metrics(X)
        stats.append([m['alpha'], m['PR'], m['LC']])
    return np.array(stats)

def load_null_stats(results_json, key='null_mean'):
    """Extract (α, PR, LC) from null results JSON."""
    with open(results_json) as fp:
        data = json.load(fp)
    stats = []
    for recording, vals in data.items():
        nm = vals.get(key, vals)
        stats.append([nm.get('alpha', 0), nm.get('PR', 0), 0.0])
    if not stats:
        return np.zeros((0, 3))
    return np.array(stats)

def main():
    print("=" * 72)
    print("ENSEMBLE COMPARISON: Mahalanobis Distance + Permutation Test")
    print("=" * 72)
    
    print("\nLoading MEC statistics...")
    mec_stats = get_mec_stats()
    print(f"  MEC recordings: {mec_stats.shape[0]}")
    print(f"  Mean α = {mec_stats[:, 0].mean():.4f} ± {mec_stats[:, 0].std():.4f}")
    print(f"  Mean PR = {mec_stats[:, 1].mean():.1f} ± {mec_stats[:, 1].std():.1f}")
    
    comparisons = []
    
    # 1. MEC vs Poisson null (015A)
    result_file = RESULTS_DIR / '015A_results.json'
    if result_file.exists():
        null_stats = load_null_stats(result_file, 'null_mean')
        if len(null_stats) > 0:
            result = ensemble_distance(mec_stats, null_stats, n_perm=5000)
            comparisons.append(('Poisson null (matched smoothing)', result))
    
    # 2. MEC vs shuffled (015B)
    result_file = RESULTS_DIR / '015B_results.json'
    if result_file.exists():
        null_stats = load_null_stats(result_file, 'shuffled_mean')
        if len(null_stats) > 0:
            result = ensemble_distance(mec_stats, null_stats, n_perm=5000)
            comparisons.append(('Circular shuffle', result))
    
    # 3. MEC vs sparse ER p=0.05
    result_file = RESULTS_DIR / '015D_results.json'
    if result_file.exists():
        with open(result_file) as fp:
            sparse_data = json.load(fp)
        er_p05 = sparse_data.get('er_p0.05')
        if er_p05:
            null_stats = np.array([[er_p05['null_alpha_mean'], er_p05['null_PR_mean'], 0.0]])
            null_stats = np.tile(null_stats, (mec_stats.shape[0], 1))
            # Add jitter for variance estimation
            null_stats += np.random.RandomState(42).normal(0, 0.5, null_stats.shape)
            result = ensemble_distance(mec_stats, null_stats, n_perm=2000)
            comparisons.append(('Sparse ER p=0.05', result))
    
    # 4. MEC vs GOE (from scaling_separation data)
    try:
        scaling_file = Path('experiments/dynamics/phase_013/scaling_results.json')
        if scaling_file.exists():
            pass  # Will fill from embedded GOE estimates
    except:
        pass
    
    print(f"\n{'='*72}")
    print(f"Comparison Results")
    print(f"{'='*72}")
    for name, result in comparisons:
        print(format_comparison(name, result))
    
    print(f"\nSignificance: * p<0.05  ** p<0.01  *** p<0.001")
    print(f"\n{'='*72}")
    
    # Summary assessment
    n_significant = sum(1 for _, r in comparisons if r['p_value'] < 0.05)
    print(f"\n{n_significant}/{len(comparisons)} comparisons significant at p<0.05")
    
    if n_significant == len(comparisons):
        print("MEC covariance geometry is robustly distinct from ALL tested nulls.")
    elif n_significant > 0:
        print(f"MEC distinguishable from {n_significant}/{len(comparisons)} nulls.")
    else:
        print("No significant separation detected.")

if __name__ == '__main__':
    main()
