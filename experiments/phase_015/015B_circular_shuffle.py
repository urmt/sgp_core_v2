import numpy as np
from glob import glob
from pathlib import Path
import json, time, sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import compute_metrics

DATA_DIR = Path('experiments/dynamics/tier2_data')
RESULTS_DIR = Path('experiments/phase_015/results')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
N_SHUFFLES = 100

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

    real_metrics = compute_metrics(X)

    shuffled_alphas, shuffled_prs = [], []
    t0 = time.time()
    rows = np.arange(T)[:, None]
    for r in range(N_SHUFFLES):
        offsets = np.random.randint(T, size=N)
        idx = (rows - offsets[None, :]) % T
        X_shuf = X[idx, np.arange(N)]
        m = compute_metrics(X_shuf)
        shuffled_alphas.append(m['alpha'])
        shuffled_prs.append(m['PR'])
    elapsed = time.time() - t0

    shuffled_alphas = np.array(shuffled_alphas)
    shuffled_prs = np.array(shuffled_prs)

    d_alpha = (real_metrics['alpha'] - shuffled_alphas.mean()) / max(shuffled_alphas.std(), 1e-10)
    d_pr = (real_metrics['PR'] - shuffled_prs.mean()) / max(shuffled_prs.std(), 1e-10)

    results[name] = {
        'real': real_metrics,
        'shuffled_mean': {
            'alpha': float(shuffled_alphas.mean()),
            'PR': float(shuffled_prs.mean()),
        },
        'shuffled_std': {
            'alpha': float(shuffled_alphas.std()),
            'PR': float(shuffled_prs.std()),
        },
        'd_alpha': float(d_alpha),
        'd_PR': float(d_pr),
        'T': int(T),
        'N': int(N),
        'elapsed_s': round(elapsed, 1),
    }

    print(f'  Real: α={real_metrics["alpha"]:.4f}, PR={real_metrics["PR"]:.1f}')
    print(f'  Shuf: α={shuffled_alphas.mean():.4f}±{shuffled_alphas.std():.4f}, PR={shuffled_prs.mean():.1f}±{shuffled_prs.std():.1f}')
    print(f'  d_α={d_alpha:.2f}σ, d_PR={d_pr:.2f}σ')

d_alphas = [r['d_alpha'] for r in results.values()]
d_prs = [r['d_PR'] for r in results.values()]
print(f'\n{"="*60}')
print(f'Summary across {len(results)} recordings:')
print(f'd_α:  mean={np.mean(d_alphas):.2f}σ, min={np.min(d_alphas):.2f}σ, max={np.max(d_alphas):.2f}σ')
print(f'd_PR: mean={np.mean(d_prs):.2f}σ, min={np.min(d_prs):.2f}σ, max={np.max(d_prs):.2f}σ')
n_surviving = sum(1 for d in d_alphas if abs(d) > 2)
print(f'Survival (|d|>2σ): α={n_surviving}/{len(results)}')

outpath = RESULTS_DIR / '015B_results.json'
with open(outpath, 'w') as fp:
    json.dump(results, fp, indent=2)
print(f'\nResults saved to {outpath}')
