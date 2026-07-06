import numpy as np
from glob import glob
from pathlib import Path
import json, time, sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import compute_metrics, standard_pipeline

DATA_DIR = Path('experiments/dynamics/tier2_data')
RESULTS_DIR = Path('experiments/phase_015/results')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
SIGMAS_MS = [0, 40, 80]
N_REALIZATIONS = 20
BIN_MS = 20

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
    rates = np.clip(X.mean(axis=0), 1e-6, None)

    entry = {}
    for sigma in SIGMAS_MS:
        # Real at this sigma
        X_smooth = standard_pipeline(X, BIN_MS, sigma)
        real = compute_metrics(X_smooth)

        # Poisson null at this sigma
        null_alphas, null_prs = [], []
        for _ in range(N_REALIZATIONS):
            poisson = np.random.poisson(rates[np.newaxis, :], size=(T, N))
            poisson_s = standard_pipeline(poisson, BIN_MS, sigma)
            m = compute_metrics(poisson_s)
            null_alphas.append(m['alpha'])
            null_prs.append(m['PR'])

        null_alphas = np.array(null_alphas)
        null_prs = np.array(null_prs)

        d_alpha = (real['alpha'] - null_alphas.mean()) / max(null_alphas.std(), 1e-10)

        entry[f'sigma_{sigma}'] = {
            'real_alpha': round(real['alpha'], 4),
            'real_PR': round(real['PR'], 1),
            'null_alpha_mean': round(float(null_alphas.mean()), 4),
            'null_alpha_std': round(float(null_alphas.std()), 4),
            'null_PR_mean': round(float(null_prs.mean()), 1),
            'null_PR_std': round(float(null_prs.std()), 1),
            'd_alpha': round(float(d_alpha), 2),
        }
        print(f'  σ={sigma:2d}ms: real α={real["alpha"]:.4f} PR={real["PR"]:.1f} | null α={null_alphas.mean():.4f} PR={null_prs.mean():.1f} | d_α={d_alpha:.1f}σ')

    results[name] = entry

outpath = RESULTS_DIR / '015C_results.json'
with open(outpath, 'w') as fp:
    json.dump(results, fp, indent=2)
print(f'\nResults saved to {outpath}')
