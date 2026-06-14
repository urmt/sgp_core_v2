"""
Phase E4 — Predictive Curvature Concentration Regions.
Parameter sweeps identifying regions of high curvature (concentration regions),
not physical/dynamical transitions. Saves all outputs immediately.
"""
import numpy as np, pandas as pd, os, json, time, warnings
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseE'
t0 = time.time()

curv = pd.read_csv(f'{BASE}/processed/curvature_metrics.csv')
poss = pd.read_csv(f'{BASE}/processed/possibility_metrics.csv')
phaseC = pd.read_csv('/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv')
phaseC['sys_idx'] = phaseC.groupby('domain').cumcount()

df = curv.merge(poss, on=['sys_idx','domain']).merge(
    phaseC[['sys_idx','domain','CSR','RBS','ADI','RTP','SRD']], on=['sys_idx','domain'])
domains = sorted(df['domain'].unique())

COLS_CURV = ['tangent_rotation','local_curvature','predictive_shear',
             'geodesic_instab','jacobian_vol','desc_switch_vel']
COLS_DESC = ['CSR','RBS','ADI','RTP','SRD']
COLS_POSS = ['poss_reachable_volume','poss_branching_diversity',
             'poss_adaptive_recovery','poss_future_entropy',
             'poss_divergence_capacity','poss_stability_fertility_coupling']

print('='*70)
print('PHASE E4 — PREDICTIVE CURVATURE CONCENTRATION REGIONS')
print('='*70)

WINDOW = 20
records = []

for domain in domains:
    m = df['domain'] == domain
    dm = df[m].reset_index(drop=True)

    for desc_col in COLS_DESC:
        sd = dm.sort_values(desc_col).reset_index(drop=True)

        for metric_col in COLS_CURV + COLS_POSS:
            vals = sd[metric_col].values
            roll = pd.Series(vals).rolling(WINDOW, center=True).mean().values
            p75 = np.nanpercentile(roll, 75)

            for i in range(WINDOW//2, len(vals) - WINDOW//2):
                if np.isnan(roll[i]): continue
                if roll[i] > p75:
                    row = sd.iloc[i]
                    records.append({
                        'domain': domain, 'descriptor': desc_col,
                        'descriptor_value': float(row[desc_col]),
                        'metric': metric_col,
                        'metric_value': float(row[metric_col]),
                        'roll_mean': float(roll[i]),
                        'roll_p75': float(p75),
                        'above_p75': True,
                        'sys_idx': int(row['sys_idx']),
                    })

    print(f'  {domain}: {sum(1 for r in records if r["domain"]==domain)} concentration records')

conc_df = pd.DataFrame(records)
conc_path = f'{BASE}/processed/curvature_regions.csv'
conc_df.to_csv(conc_path, index=False)
print(f'\n  Curvature regions (concentration) saved: {conc_path} ({len(conc_df)} rows)')

# Parameter sweep summary: per descriptor, what value range triggers concentration?
print('\n--- Concentration structure by descriptor ---')
for desc in COLS_DESC:
    sub = conc_df[conc_df['descriptor'] == desc]
    if len(sub) == 0: continue
    val_mean = sub['descriptor_value'].mean()
    val_std = sub['descriptor_value'].std()
    print(f'  {desc}: mean={val_mean:.4f} ± {val_std:.4f} (n={len(sub)})')

# Concentration by descriptor × metric
if len(conc_df) > 0:
    cross = conc_df.groupby(['descriptor','metric']).size().unstack(fill_value=0)
    cross_path = f'{BASE}/processed/concentration_regions.csv'
    cross.to_csv(cross_path)
    print(f'\n  Concentration regions cross-tab: {cross_path}')

    desc_density = conc_df.groupby('descriptor').size().sort_values(ascending=False)
    print('\n--- Concentration count per descriptor ---')
    for d, n in desc_density.items():
        print(f'  {d}: {n}')

e4_summary = {
    'phase': 'E4', 'seed': SEED, 'rolling_window': WINDOW,
    'n_concentration_records': len(conc_df),
    'n_descriptors': len(COLS_DESC),
    'n_metrics': len(COLS_CURV + COLS_POSS),
    'descriptors': COLS_DESC,
    'metrics': COLS_CURV + COLS_POSS,
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/e4_summary.json', 'w') as f:
    json.dump(e4_summary, f, indent=2)
print(f'\n  E4 summary saved')

print(f'\nE4 COMPLETE ({time.time()-t0:.0f}s)')
