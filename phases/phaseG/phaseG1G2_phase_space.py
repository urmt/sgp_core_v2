"""
Phase G1+G2 — Coherence–Fertility Phase Space + Organizational Regions.
Maps all 5000 systems into coherence × fertility space.
Identifies 4 key regions: rigid, chaotic, collapse, constrained generative.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseG'
os.makedirs(f'{BASE}/raw', exist_ok=True)
os.makedirs(f'{BASE}/processed', exist_ok=True)
os.makedirs(f'{BASE}/summaries', exist_ok=True)

# Load data
df = pd.read_csv('/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
curv = pd.read_csv('/home/student/sgp_core_v2/phases/phaseE/processed/curvature_metrics.csv')
poss = pd.read_csv('/home/student/sgp_core_v2/phases/phaseE/processed/possibility_metrics.csv')
domains = sorted(df['domain'].unique())

# Merge
merged = df.merge(curv, on=['sys_idx','domain']).merge(poss, on=['sys_idx','domain'])
t0 = time.time()

print('='*70)
print('PHASE G1+G2 — COHERENCE–FERTILITY PHASE SPACE')
print('='*70)

# === COHERENCE AXES ===
# stability_recovery_rate, stability_return_time, stability_final_dev, stability_max_dev
# For coherence: high = stable, persistent, synchronized
# Invert metrics where high = bad (return_time, final_dev, max_dev)
stab = merged[['stability_recovery_rate','stability_return_time',
               'stability_final_dev','stability_max_dev']].values.copy()
# Invert: 1 - normalized (so higher = more coherent)
for ci in [1, 2, 3]:  # invert return_time, final_dev, max_dev
    col = stab[:, ci]
    cmin, cmax = col.min(), col.max()
    if cmax > cmin:
        stab[:, ci] = 1 - (col - cmin) / (cmax - cmin)
    else:
        stab[:, ci] = 0.5
# Normalize recovery_rate
col0 = stab[:, 0]
cmin0, cmax0 = col0.min(), col0.max()
if cmax0 > cmin0:
    stab[:, 0] = (col0 - cmin0) / (cmax0 - cmin0)

# Coherence = geometric mean of normalized stability axes
coherence = np.exp(np.mean(np.log(stab + 1e-10), axis=1))
coherence = np.clip(coherence / coherence.max(), 0, 1)

# === FERTILITY AXES ===
fert_cols = [c for c in df.columns if c.startswith('fertility_')]
poss_cols = [c for c in poss.columns if c not in ('sys_idx','domain')]
all_fert = merged[fert_cols + poss_cols].values
# Normalize each
fert_norm = np.zeros_like(all_fert)
for ci in range(all_fert.shape[1]):
    col = all_fert[:, ci]
    cmin, cmax = col.min(), col.max()
    if cmax > cmin:
        fert_norm[:, ci] = (col - cmin) / (cmax - cmin)
    else:
        fert_norm[:, ci] = 0.5
fertility = np.exp(np.mean(np.log(fert_norm + 1e-10), axis=1))
fertility = np.clip(fertility / fertility.max(), 0, 1)

# === PHASE SPACE ===
phase_df = pd.DataFrame({
    'sys_idx': merged['sys_idx'], 'domain': merged['domain'],
    'coherence': coherence, 'fertility': fertility,
})

# Add region labels
median_c = np.median(coherence)
median_f = np.median(fertility)

def label_region(c, f):
    if c >= median_c and f >= median_f: return 'constrained_generative'
    if c >= median_c and f < median_f: return 'rigid_coherence'
    if c < median_c and f >= median_f: return 'chaotic_fertility'
    return 'collapse'

phase_df['region'] = [label_region(c, f) for c, f in zip(coherence, fertility)]

phase_path = f'{BASE}/processed/coherence_fertility_phase_space.csv'
phase_df.to_csv(phase_path, index=False)
print(f'\nPhase space saved: {phase_path} ({len(phase_df)} systems)')

# G2: Region statistics
print(f'\nMedian coherence: {median_c:.4f}')
print(f'Median fertility: {median_f:.4f}')
print('\nOrganizational regions:')
region_counts = phase_df['region'].value_counts()
for region, count in region_counts.items():
    pct = 100 * count / len(phase_df)
    print(f'  {region:30s}: {count:5d} ({pct:.1f}%)')

# Per-domain region occupancy
print('\nPer-domain region occupancy:')
for domain in domains:
    dd = phase_df[phase_df['domain'] == domain]
    counts = dd['region'].value_counts()
    print(f'  {domain:25s}: ', end='')
    for r in ['constrained_generative','rigid_coherence','chaotic_fertility','collapse']:
        c = counts.get(r, 0)
        print(f'{r[:8]}={c:3d} ', end='')
    print()

# Constrained generativity candidates
cg = phase_df[phase_df['region'] == 'constrained_generative']
cg_path = f'{BASE}/processed/constrained_generativity_candidates.csv'
cg.to_csv(cg_path, index=False)
print(f'\nConstrained generative candidates: {len(cg)} systems')
print(f'Saved: {cg_path}')

# Check: do any domains dominate constrained generativity?
print('\nConstrained generativity by domain:')
cg_dom = cg['domain'].value_counts()
total_dom = phase_df['domain'].value_counts()
for d in domains:
    cg_count = cg_dom.get(d, 0)
    total = total_dom.get(d, 0)
    pct = 100 * cg_count / total if total > 0 else 0
    print(f'  {d:25s}: {cg_count}/{total} ({pct:.1f}%)')

# Coherence–fertility correlation
r, p = pearsonr(coherence, fertility)
print(f'\nCoherence–fertility correlation: r={r:.4f} (p={p:.4g})')

# Summary stats per region
print('\nRegion descriptors (mean coherence, fertility, curvature):')
for region in ['constrained_generative','rigid_coherence','chaotic_fertility','collapse']:
    mask = phase_df['region'] == region
    if mask.sum() == 0: continue
    c_mean = coherence[mask].mean()
    f_mean = fertility[mask].mean()
    print(f'  {region:30s}: C={c_mean:.3f} F={f_mean:.3f} (n={mask.sum()})')

g1g2_summary = {
    'phase': 'G1+G2', 'seed': SEED,
    'n_systems': len(phase_df), 'n_domains': len(domains),
    'median_coherence': float(median_c),
    'median_fertility': float(median_f),
    'coherence_fertility_correlation': round(r, 6),
    'region_counts': region_counts.to_dict(),
    'constrained_generative_count': int(len(cg)),
    'constrained_generative_pct': round(100 * len(cg) / len(phase_df), 1),
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/g1g2_summary.json', 'w') as f:
    json.dump(g1g2_summary, f, indent=2)

print(f'\nG1+G2 COMPLETE ({time.time()-t0:.1f}s)')
