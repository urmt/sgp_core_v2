"""
Phase 015 preprocessing-matched null controls.

Usage:
  python phase_015_controls.py --quick    # Load cached results + compute stats
  python phase_015_controls.py --full     # Regenerate all nulls (hours)
"""

import json, sys, argparse
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from statistical_comparison import ensemble_distance, format_comparison

REPO_DIR = Path(__file__).resolve().parent
RESULTS_DIR = REPO_DIR / 'phase_015_results'

parser = argparse.ArgumentParser()
parser.add_argument('--quick', action='store_true', help='Load cached results')
parser.add_argument('--full', action='store_true', help='Regenerate nulls (slow)')
args = parser.parse_args()

print("=" * 72)
print("Phase 015 — Preprocessing-Matched Null Controls")
print("=" * 72)

if args.full:
    print("\nFull regeneration not implemented in repository (see experiments/phase_015/)")
    print("Run: python experiments/phase_015/015A_smoothed_poisson.py  (≈60 min)")
    print("     python experiments/phase_015/015B_circular_shuffle.py   (≈60 min)")
    print("     python experiments/phase_015/015C_kernel_sweep.py       (≈30 min)")
    print("     python experiments/phase_015/015D_sparse_scan.py        (≈25 min)")
    sys.exit(0)

print("\n[quick mode] Loading cached Phase 015 results...\n")

comparisons = []

# 015A — Smoothed Poisson Null
p015a = RESULTS_DIR / '015A_results.json'
if p015a.exists():
    with open(p015a) as fp:
        data = json.load(fp)
    mec_alpha = np.array([v['real']['alpha'] for v in data.values()])
    mec_pr = np.array([v['real']['PR'] for v in data.values()])
    null_alpha = np.array([v['null_mean']['alpha'] for v in data.values()])
    null_pr = np.array([v['null_mean']['PR'] for v in data.values()])
    
    mec_stats = np.column_stack([mec_alpha, mec_pr, np.zeros_like(mec_alpha)])
    null_stats = np.column_stack([null_alpha, null_pr, np.zeros_like(null_alpha)])
    
    result = ensemble_distance(mec_stats, null_stats, n_perm=5000)
    comparisons.append(('A — Smoothed Poisson null', result))
    
    print(f"  MEC: α={mec_alpha.mean():.4f}±{mec_alpha.std():.4f}, PR={mec_pr.mean():.1f}±{mec_pr.std():.1f}")
    print(f"  Null: α={null_alpha.mean():.4f}±{null_alpha.std():.4f}, PR={null_pr.mean():.1f}±{null_pr.std():.1f}")

# 015B — Circular Shuffle
p015b = RESULTS_DIR / '015B_results.json'
if p015b.exists():
    with open(p015b) as fp:
        data = json.load(fp)
    null_alpha = np.array([v['shuffled_mean']['alpha'] for v in data.values()])
    null_pr = np.array([v['shuffled_mean']['PR'] for v in data.values()])
    
    null_stats = np.column_stack([null_alpha, null_pr, np.zeros_like(null_alpha)])
    
    result = ensemble_distance(mec_stats, null_stats, n_perm=5000)
    comparisons.append(('B — Circular shuffle', result))
    
    print(f"  MEC: α={mec_alpha.mean():.4f}±{mec_alpha.std():.4f}, PR={mec_pr.mean():.1f}±{mec_pr.std():.1f}")
    print(f"  Null: α={null_alpha.mean():.4f}±{null_alpha.std():.4f}, PR={null_pr.mean():.1f}±{null_pr.std():.1f}")

# 015C — Kernel Width Sweep (σ=40ms)
p015c = RESULTS_DIR / '015C_results.json'
if p015c.exists():
    with open(p015c) as fp:
        data = json.load(fp)
    for sigma in [0, 40, 80]:
        real_alpha = np.array([v[f'sigma_{sigma}']['real_alpha'] for v in data.values()])
        real_pr = np.array([v[f'sigma_{sigma}']['real_PR'] for v in data.values()])
        null_alpha = np.array([v[f'sigma_{sigma}']['null_alpha_mean'] for v in data.values()])
        null_pr = np.array([v[f'sigma_{sigma}']['null_PR_mean'] for v in data.values()])
        
        mec_s = np.column_stack([real_alpha, real_pr, np.zeros_like(real_alpha)])
        null_s = np.column_stack([null_alpha, null_pr, np.zeros_like(null_alpha)])
        
        result = ensemble_distance(mec_s, null_s, n_perm=2000)
        comparisons.append((f'C — Kernel σ={sigma}ms', result))

# 015D — Sparse Ensemble Scan (best match)
p015d = RESULTS_DIR / '015D_results.json'
if p015d.exists():
    with open(p015d) as fp:
        data = json.load(fp)
    best_dm = 1e9
    best_key = None
    for key, v in data.items():
        d_alpha_mag = abs(v.get('d_alpha', 1e9))
        d_pr_mag = abs(v.get('d_PR', 1e9))
        dm = d_alpha_mag + d_pr_mag
        if dm < best_dm and d_alpha_mag < 10:
            best_dm = dm
            best_key = key
    
    if best_key:
        v = data[best_key]
        null_mean = np.array([[v['null_alpha_mean'], v['null_PR_mean'], 0.0]])
        null_mean = np.tile(null_mean, (mec_stats.shape[0], 1))
        null_mean += np.random.RandomState(42).normal(0, np.array([
            v['null_alpha_std'], v['null_PR_std'], 0.01
        ]), null_mean.shape)
        
        result = ensemble_distance(mec_stats, null_mean, n_perm=2000)
        comparisons.append((f'D — Best sparse null ({best_key})', result))

print(f"\n{'='*72}")
print(f"Comparison Results (Mahalanobis Distance + Permutation Test)")
print(f"{'='*72}")
for name, result in comparisons:
    print(format_comparison(name, result))

n_sig = sum(1 for _, r in comparisons if r['p_value'] < 0.05)
print(f"\n{n_sig}/{len(comparisons)} nulls significantly different from MEC (p<0.05)")
if n_sig == len(comparisons):
    print("STRONG: MEC covariance geometry is robustly distinct from ALL matched nulls.")
print()
