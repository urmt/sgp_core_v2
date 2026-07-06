import numpy as np
from glob import glob
from pathlib import Path
from numpy import linalg as la
import json, time, sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import canonical_alpha, participation_ratio, compute_metrics

DATA_DIR = Path('experiments/dynamics/tier2_data')
RESULTS_DIR = Path('experiments/phase_015/results')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
N_REALIZATIONS = 100
N_TARGET = 120  # fixed size for comparison

# Scan parameters
DENSITIES = [0.01, 0.02, 0.05, 0.10, 0.20]
TOPOLOGIES = {
    'er': lambda N, p, rng: _er_covariance(N, p, rng),
    'modular': lambda N, p, rng: _modular_covariance(N, p, rng),
    'banded': lambda N, p, rng: _banded_covariance(N, p, rng),
}

def _er_covariance(N, p, rng):
    A = rng.binomial(1, p, size=(N, N)).astype(np.float64)
    A = (A + A.T) / 2
    A[np.diag_indices(N)] = 0
    evals = la.eigh(A)[0]
    return A, evals

def _modular_covariance(N, p, rng):
    n_blocks = max(2, N // 20)
    block_size = N // n_blocks
    p_in = min(1.0, p * 5)
    A = np.zeros((N, N))
    for b in range(n_blocks):
        i0, i1 = b * block_size, min((b + 1) * block_size, N)
        for i in range(i0, i1):
            for j in range(i0, i1):
                if i != j and rng.random() < p_in:
                    A[i, j] = 1
    A = (A + A.T) / 2
    evals = la.eigh(A)[0]
    return A, evals

def _banded_covariance(N, p, rng):
    bandwidth = max(2, int(N * p * 2))
    A = np.zeros((N, N))
    for i in range(N):
        for d in range(1, min(bandwidth, N - i)):
            if rng.random() < 0.5:
                A[i, i + d] = 1
                A[i + d, i] = 1
    evals = la.eigh(A)[0]
    return A, evals

files = sorted(glob(str(DATA_DIR / '*MEC_FRtensor*.npy')))
print(f'Found {len(files)} recordings')

# Real MEC metrics at subsampled N~120
mec_alphas, mec_prs = [], []
for f in files:
    X = np.load(f).astype(np.float64)
    if X.ndim == 3:
        X = X.reshape(X.shape[0] * X.shape[1], X.shape[2])
    if X.shape[1] < N_TARGET:
        continue
    rng = np.random.RandomState(42)
    idx = rng.choice(X.shape[1], N_TARGET, replace=False)
    X_sub = X[:, idx]
    m = compute_metrics(X_sub)
    mec_alphas.append(m['alpha'])
    mec_prs.append(m['PR'])

mec_alpha_mean = np.mean(mec_alphas)
mec_alpha_std = np.std(mec_alphas)
mec_pr_mean = np.mean(mec_prs)
mec_pr_std = np.std(mec_prs)
print(f'MEC (N~{N_TARGET}): α={mec_alpha_mean:.4f}±{mec_alpha_std:.4f}, PR={mec_pr_mean:.1f}±{mec_pr_std:.1f}')

results = {}
for p in DENSITIES:
    for topo_name, topo_func in TOPOLOGIES.items():
        key = f'{topo_name}_p{p}'
        print(f'\n  {key}...')
        null_alphas, null_prs = [], []
        t0 = time.time()
        for r in range(N_REALIZATIONS):
            rng = np.random.RandomState(r * 1000 + int(p * 100))
            A, evals = topo_func(N_TARGET, p, rng)
            alpha = canonical_alpha(evals)
            pr = participation_ratio(evals)
            null_alphas.append(alpha)
            null_prs.append(pr)
        elapsed = time.time() - t0

        null_alphas = np.array(null_alphas)
        null_prs = np.array(null_prs)

        d_alpha = (mec_alpha_mean - null_alphas.mean()) / max(null_alphas.std(), 1e-10)
        d_pr = (mec_pr_mean - null_prs.mean()) / max(null_prs.std(), 1e-10)

        results[key] = {
            'p': p,
            'topology': topo_name,
            'null_alpha_mean': round(float(null_alphas.mean()), 4),
            'null_alpha_std': round(float(null_alphas.std()), 4),
            'null_PR_mean': round(float(null_prs.mean()), 1),
            'null_PR_std': round(float(null_prs.std()), 1),
            'd_alpha': round(float(d_alpha), 2),
            'd_PR': round(float(d_pr), 2),
        }
        print(f'    α={null_alphas.mean():.4f}±{null_alphas.std():.4f}, PR={null_prs.mean():.1f}±{null_prs.std():.1f}, d_α={d_alpha:.2f}σ, d_PR={d_pr:.2f}σ')

# Find best match
best = min(results.values(), key=lambda x: abs(x['d_alpha']) + abs(x['d_PR']))
print(f'\n{"="*60}')
print(f'Best matching null: {best}')
print(f'MEC reference: α={mec_alpha_mean:.4f}±{mec_alpha_std:.4f}, PR={mec_pr_mean:.1f}±{mec_pr_std:.1f}')

outpath = RESULTS_DIR / '015D_results.json'
with open(outpath, 'w') as fp:
    json.dump(results, fp, indent=2)
print(f'\nResults saved to {outpath}')
