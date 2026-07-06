import numpy as np
from glob import glob
from pathlib import Path
import json, time, sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import compute_metrics, standard_pipeline

DATA_DIR = Path('experiments/dynamics/tier2_data')
RESULTS_DIR = Path('experiments/phase_015/results')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
N_REALIZATIONS = 100
BIN_MS = 20
SIGMA_MS = 40

files = sorted(glob(str(DATA_DIR / '*MEC_FRtensor*.npy')))
print(f'Found {len(files)} recordings')

results = {}

for fi, f in enumerate(files):
    name = Path(f).stem
    print(f'\n[{fi+1}/{len(files)}] {name}')
    X = np.load(f).astype(np.float64)
    if X.ndim == 3:
        X = X.reshape(X.shape[0] * X.shape[1], X.shape[2])
    T, N = X.shape
    print(f'  T={T}, N={N}, mean_rate={X.mean():.4f}')

    # Real metrics
    real_metrics = compute_metrics(X)

    # Per-neuron mean firing rates
    rates = X.mean(axis=0)
    rates = np.clip(rates, 1e-6, None)

    # Poisson nulls
    null_alphas, null_prs, null_lcs = [], [], []
    t0 = time.time()
    for r in range(N_REALIZATIONS):
        poisson = np.random.poisson(rates[np.newaxis, :] * 1.0, size=(T, N))
        poisson_smoothed = standard_pipeline(poisson, BIN_MS, SIGMA_MS)
        m = compute_metrics(poisson_smoothed)
        null_alphas.append(m['alpha'])
        null_prs.append(m['PR'])
        null_lcs.append(m['LC'])
    elapsed = time.time() - t0

    # Stats
    null_alphas = np.array(null_alphas)
    null_prs = np.array(null_prs)
    null_lcs = np.array(null_lcs)

    d_alpha = (real_metrics['alpha'] - null_alphas.mean()) / max(null_alphas.std(), 1e-10)
    d_pr = (real_metrics['PR'] - null_prs.mean()) / max(null_prs.std(), 1e-10)

    results[name] = {
        'real': real_metrics,
        'null_mean': {
            'alpha': float(null_alphas.mean()),
            'PR': float(null_prs.mean()),
            'LC': float(null_lcs.mean()),
        },
        'null_std': {
            'alpha': float(null_alphas.std()),
            'PR': float(null_prs.std()),
            'LC': float(null_lcs.std()),
        },
        'd_alpha': float(d_alpha),
        'd_PR': float(d_pr),
        'T': int(T),
        'N': int(N),
        'elapsed_s': round(elapsed, 1),
    }

    print(f'  Real: α={real_metrics["alpha"]:.4f}, PR={real_metrics["PR"]:.1f}')
    print(f'  Null: α={null_alphas.mean():.4f}±{null_alphas.std():.4f}, PR={null_prs.mean():.1f}±{null_prs.std():.1f}')
    print(f'  d_α={d_alpha:.2f}σ, d_PR={d_pr:.2f}σ')

# Summary
d_alphas = [r['d_alpha'] for r in results.values()]
d_prs = [r['d_PR'] for r in results.values()]
print(f'\n{"="*60}')
print(f'Summary across {len(results)} recordings:')
print(f'd_α:  mean={np.mean(d_alphas):.2f}σ, min={np.min(d_alphas):.2f}σ, max={np.max(d_alphas):.2f}σ')
print(f'd_PR: mean={np.mean(d_prs):.2f}σ, min={np.min(d_prs):.2f}σ, max={np.max(d_prs):.2f}σ')
n_surviving_a = sum(1 for d in d_alphas if abs(d) > 2)
n_surviving_pr = sum(1 for d in d_prs if abs(d) > 2)
print(f'Survival (|d|>2σ): α={n_surviving_a}/{len(results)}, PR={n_surviving_pr}/{len(results)}')

outpath = RESULTS_DIR / '015A_results.json'
with open(outpath, 'w') as fp:
    json.dump(results, fp, indent=2)
print(f'\nResults saved to {outpath}')
