"""
Phase E2 — Possibility Space Metrics.
Constructs 6 possibility metrics distinct from fertility.
Leakage audit checks independence from raw fertility.
Saves all outputs immediately.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from scipy.stats import pearsonr, entropy
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseE'
CSV_SRC = '/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv'
df = pd.read_csv(CSV_SRC)
df['sys_idx'] = df.groupby('domain').cumcount()

fertility_targets = [c for c in df.columns if c.startswith('fertility_')]
stability_cols = [c for c in df.columns if c.startswith('stability_')]

print('='*70)
print('PHASE E2 — POSSIBILITY SPACE METRICS')
print('='*70)
t0 = time.time()

# Build possibility metrics from fertility + stability combinations
poss_cols = [
    'poss_reachable_volume',
    'poss_branching_diversity',
    'poss_adaptive_recovery',
    'poss_future_entropy',
    'poss_divergence_capacity',
    'poss_stability_fertility_coupling',
]

records = []
for _, row in df.iterrows():
    fd = row['fertility_state_diversity']
    fn = row['fertility_novelty_rate']
    fc = row['fertility_state_coverage']
    ft = row['fertility_transition_entropy']
    sr = row['stability_recovery_rate']
    sf = row['stability_final_dev']
    sm = row['stability_max_dev']
    st = row['stability_return_time']

    rv = float(fd * (fc + 1e-10))
    sv = np.array([st, sf, sm, abs(sr)])
    sv = sv / (np.max(sv) + 1e-10)
    bd = float(entropy(sv + 1e-10) / np.log(4))
    rc = 1 - sf / (sm + 1e-10)
    ar = float(abs(sr) * max(0, rc))
    ps = sm / (abs(sr) + 1e-10)
    fe = float(ft * (1 + np.log1p(ps)))
    dc = float(fd * sm)
    co = float((1 - sf / (sm + 1e-10)) * fd)

    records.append({
        'sys_idx': row['sys_idx'], 'domain': row['domain'],
        'poss_reachable_volume': rv, 'poss_branching_diversity': bd,
        'poss_adaptive_recovery': ar, 'poss_future_entropy': fe,
        'poss_divergence_capacity': dc, 'poss_stability_fertility_coupling': co,
    })

poss_df = pd.DataFrame(records)
poss_path = f'{BASE}/processed/possibility_metrics.csv'
poss_df.to_csv(poss_path, index=False)
print(f'  Possibility metrics saved: {poss_path} ({len(poss_df)} rows)')

# --- Leakage Audit: possibility vs fertility ---
merged = df.merge(poss_df, on=['sys_idx', 'domain'])
leakage_rows = []
for pc in poss_cols:
    for ft in fertility_targets:
        r, p = pearsonr(merged[pc], merged[ft])
        leakage_rows.append({
            'possibility_metric': pc,
            'fertility_metric': ft,
            'pearson_r': round(r, 6),
            'p_value': p,
            'r2': round(r**2, 6),
            'flagged': abs(r) > 0.85,
        })

leakage_df = pd.DataFrame(leakage_rows)
leakage_path = f'{BASE}/raw/leakage_audit.csv'
leakage_df.to_csv(leakage_path, index=False)
print(f'  Leakage audit saved: {leakage_path} ({len(leakage_df)} rows)')

flagged = leakage_df[leakage_df['flagged']]
if len(flagged) > 0:
    print(f'\n  LEAKAGE FLAGGED ({len(flagged)} pairs):')
    for _, r in flagged.iterrows():
        print(f'    {r["possibility_metric"]} vs {r["fertility_metric"]}: r={r["pearson_r"]:.4f}')
else:
    print('\n  No leakage detected (all |r| <= 0.85)')

# --- E2 Summary ---
poss_means = poss_df[poss_cols].mean().to_dict()
poss_stds = poss_df[poss_cols].std().to_dict()
e2_summary = {
    'phase': 'E2', 'seed': SEED,
    'n_systems': len(poss_df),
    'n_domains': len(df['domain'].unique()),
    'possibility_metrics': poss_cols,
    'metric_means': {k: round(v, 6) for k, v in poss_means.items()},
    'metric_stds': {k: round(v, 6) for k, v in poss_stds.items()},
    'n_leakage_flagged': int((leakage_df['flagged']).sum()),
    'leakage_details': [
        {k: r[k] for k in ['possibility_metric','fertility_metric','pearson_r']}
        for _, r in flagged.iterrows()
    ],
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/e2_summary.json', 'w') as f:
    json.dump(e2_summary, f, indent=2)
print(f'\n  E2 summary saved')

print(f'\nE2 COMPLETE ({time.time()-t0:.0f}s)')
