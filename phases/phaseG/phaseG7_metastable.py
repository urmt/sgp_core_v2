"""
Phase G7 — Temporal Organization & Meta-Stable Regimes.
Analyzes whether systems cluster around coherence–fertility balance points.
Searches for meta-stable organizational regimes and self-regulation patterns.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.neighbors import NearestNeighbors
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseG'
phase = pd.read_csv(f'{BASE}/processed/coherence_fertility_phase_space.csv')
curv = pd.read_csv('/home/student/sgp_core_v2/phases/phaseE/processed/curvature_metrics.csv')
domains = sorted(phase['domain'].unique())

t0 = time.time()
print('='*70)
print('PHASE G7 — META-STABLE REGIME ANALYSIS')
print('='*70)

c, f = phase['coherence'].values, phase['fertility'].values
balance = c * f

# === BALANCE POINT CLUSTERING ===
# Are there clusters of systems near particular coherence/fertility combinations?
X_phase = np.column_stack([c, f])
nbrs = NearestNeighbors(n_neighbors=min(51, len(X_phase))).fit(X_phase)
distances, indices = nbrs.kneighbors(X_phase)
local_density = 1 / (distances[:, min(10, distances.shape[1]-1)] + 1e-10)

# Find highest-density points (meta-stable regimes)
density_threshold = np.percentile(local_density, 90)
high_density = local_density >= density_threshold

# Characterize meta-stable regimes
print(f'\nHigh-density points (top 10% density): {high_density.sum()}')
hd_c = c[high_density].mean()
hd_f = f[high_density].mean()
print(f'  Mean coherence: {hd_c:.4f}')
print(f'  Mean fertility: {hd_f:.4f}')
print(f'  Mean balance:   {balance[high_density].mean():.4f}')

# Per-domain density analysis
print('\nLocal density per domain:')
for domain in domains:
    mask = phase['domain'] == domain
    dom_density = local_density[mask].mean()
    print(f'  {domain:25s}: density={dom_density:.4f}')

# === META-STABLE REGIME IDENTIFICATION ===
# Find peaks in the coherence-fertility density landscape
# Grid-based approach: discretize [0,1] × [0,1] and count systems
n_bins = 20
c_bins = np.linspace(0, 1, n_bins + 1)
f_bins = np.linspace(0, 1, n_bins + 1)
c_idx = np.digitize(c, c_bins) - 1
f_idx = np.digitize(f, f_bins) - 1

grid_counts = np.zeros((n_bins, n_bins))
grid_balance = np.zeros((n_bins, n_bins))
for i in range(len(c)):
    ci, fi = c_idx[i], f_idx[i]
    if 0 <= ci < n_bins and 0 <= fi < n_bins:
        grid_counts[ci, fi] += 1
        grid_balance[ci, fi] += balance[i]

# Normalize balance per cell
mask = grid_counts > 0
grid_balance[mask] /= grid_counts[mask]

# Find peaks: cells with >2× mean count
mean_count = grid_counts.mean()
peak_mask = grid_counts > 2 * mean_count
peak_cells = np.argwhere(peak_mask)

meta_records = []
print(f'\nMeta-stable regimes (cells with >2× mean density):')
for ci, fi in peak_cells:
    c_center = (c_bins[ci] + c_bins[ci+1]) / 2
    f_center = (f_bins[fi] + f_bins[fi+1]) / 2
    count = grid_counts[ci, fi]
    bal = grid_balance[ci, fi]
    in_cell = (c_idx == ci) & (f_idx == fi)
    dom_in_cell = phase['domain'][in_cell].value_counts()
    top_doms = dom_in_cell.head(3).to_dict()
    meta_records.append({
        'c_center': round(c_center, 3), 'f_center': round(f_center, 3),
        'n_systems': int(count), 'mean_balance': round(bal, 4),
        'top_domains': str(top_doms),
    })
    print(f'  C≈{c_center:.2f} F≈{f_center:.2f}: {int(count)} systems, bal={bal:.4f}')
    print(f'    Domains: {top_doms}')

pd.DataFrame(meta_records).to_csv(f'{BASE}/processed/metastable_regimes.csv', index=False)

# === SELF-REGULATION AROUND BALANCE ===
# Systems with moderate balance (0.2-0.4) vs extreme balance
print('\nSelf-regulation analysis:')
moderate = (balance > 0.2) & (balance < 0.4)
extreme = (balance > 0.7) | (balance < 0.01)
print(f'  Moderate balance (0.2-0.4): {moderate.sum()} systems')
print(f'  Extreme balance (>0.7 or <0.01): {extreme.sum()} systems')

# Do moderate-balance systems have distinct curvature?
if moderate.sum() > 0 and extreme.sum() > 0:
    merged = phase.merge(curv, on=['sys_idx','domain'])
    curv_cols = [c for c in curv.columns if c not in ('sys_idx','domain')]
    for cc in curv_cols:
        m_val = merged[cc][moderate].mean()
        e_val = merged[cc][extreme].mean()
        print(f'  {cc:20s}: moderate={m_val:.4f}  extreme={e_val:.4f}')

# === BALANCE STABILITY ===
# Systems near the balance point (coherence ≈ fertility)
near_balance = abs(c - f) < 0.1
print(f'\nSystems near coherence-fertility balance (|C-F|<0.1): {near_balance.sum()}')
print(f'  Mean coherence: {c[near_balance].mean():.4f}')
print(f'  Mean fertility: {f[near_balance].mean():.4f}')
print(f'  Mean balance: {balance[near_balance].mean():.4f}')

# Which domains are near balance?
for domain in domains:
    mask = phase['domain'] == domain
    nb = near_balance & mask
    pct = 100 * nb.sum() / mask.sum()
    print(f'  {domain:25s}: {nb.sum():3d}/{mask.sum():3d} ({pct:.0f}%)')

g7_summary = {
    'phase': 'G7', 'seed': SEED,
    'n_high_density_points': int(high_density.sum()),
    'n_meta_stable_regimes': len(peak_cells),
    'n_near_balance_systems': int(near_balance.sum()),
    'moderate_balance_count': int(moderate.sum()),
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/g7_summary.json', 'w') as f:
    json.dump(g7_summary, f, indent=2)

print(f'\nG7 COMPLETE ({time.time()-t0:.1f}s)')
