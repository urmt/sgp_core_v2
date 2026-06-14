"""
Phase E3 — Curvature → Possibility Prediction (Full Persistence).
LOOCV within each domain. Three predictor sets: curvature, raw descriptors, combined.
Per-domain R², model comparisons, saved immediately.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseE'
t0 = time.time()

# Load from saved persistent files
curv = pd.read_csv(f'{BASE}/processed/curvature_metrics.csv')
poss = pd.read_csv(f'{BASE}/processed/possibility_metrics.csv')
phaseC = pd.read_csv('/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv')
phaseC['sys_idx'] = phaseC.groupby('domain').cumcount()

# Merge all
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
print('PHASE E3 — CURVATURE → POSSIBILITY PREDICTION (PERSISTENT)')
print('='*70)

records = []
per_domain = []

for domain in domains:
    m = df['domain'] == domain
    dm = df[m].reset_index(drop=True)
    N = len(dm)

    for pc in COLS_POSS:
        y = dm[pc].values
        y_bar = np.mean(y)

        for label, predictors in [
            ('raw_descriptors', COLS_DESC),
            ('curvature', COLS_CURV),
            ('combined', COLS_DESC + COLS_CURV),
        ]:
            X = dm[predictors].values
            X_mu = np.mean(X, axis=0); X_sig = np.std(X, axis=0) + 1e-10
            X_n = (X - X_mu) / X_sig

            y_pred = np.zeros(N)
            for i in range(N):
                tr = np.arange(N) != i
                y_pred[i] = Ridge(alpha=1.0).fit(X_n[tr], y[tr]).predict(X_n[i:i+1])[0]

            r2 = float(r2_score(y, y_pred))
            rmse = float(np.sqrt(mean_squared_error(y, y_pred)))
            corr, pv = pearsonr(y, y_pred)
            null_r2 = float(r2_score(y, np.full(N, y_bar)))

            records.append({
                'domain': domain, 'possibility_metric': pc,
                'predictor_set': label, 'R2': r2, 'RMSE': rmse,
                'pearson_r': corr, 'pearson_p': pv, 'null_R2': null_r2,
                'N': N,
            })

    print(f'  {domain}: {N} systems × {len(COLS_POSS)} targets → done')

results_df = pd.DataFrame(records)
res_path = f'{BASE}/processed/prediction_results.csv'
results_df.to_csv(res_path, index=False)
print(f'\n  Prediction results saved: {res_path} ({len(results_df)} rows)')

# Per-domain R² (averaged across possibility metrics)
per_domain_r2 = results_df.groupby(['domain','predictor_set'])['R2'].mean().reset_index()
per_domain_path = f'{BASE}/processed/per_domain_r2.csv'
per_domain_r2.to_csv(per_domain_path, index=False)

# Model comparisons: curvature vs descriptors per (domain, metric)
comp_records = []
for domain in domains:
    for pc in COLS_POSS:
        r_curv = results_df[(results_df['domain']==domain)&(results_df['possibility_metric']==pc)&
                            (results_df['predictor_set']=='curvature')]['R2'].values[0]
        r_raw = results_df[(results_df['domain']==domain)&(results_df['possibility_metric']==pc)&
                           (results_df['predictor_set']=='raw_descriptors')]['R2'].values[0]
        r_comb = results_df[(results_df['domain']==domain)&(results_df['possibility_metric']==pc)&
                            (results_df['predictor_set']=='combined')]['R2'].values[0]
        comp_records.append({
            'domain': domain, 'possibility_metric': pc,
            'curvature_R2': r_curv, 'raw_descriptors_R2': r_raw,
            'combined_R2': r_comb,
            'curv_vs_raw_delta': r_curv - r_raw,
            'combined_vs_raw_delta': r_comb - r_raw,
            'curv_wins': r_curv > r_raw,
            'combined_wins': r_comb > r_curv,
        })

comp_df = pd.DataFrame(comp_records)
comp_path = f'{BASE}/raw/model_comparisons.csv'
comp_df.to_csv(comp_path, index=False)
print(f'  Model comparisons saved: {comp_path} ({len(comp_df)} rows)')

# --- Summary stats ---
curv_avg = results_df[results_df['predictor_set']=='curvature']['R2'].mean()
raw_avg = results_df[results_df['predictor_set']=='raw_descriptors']['R2'].mean()
comb_avg = results_df[results_df['predictor_set']=='combined']['R2'].mean()
curv_wins = (comp_df['curv_wins']).sum()
combined_wins = (comp_df['combined_wins']).sum()

e3_summary = {
    'phase': 'E3', 'seed': SEED,
    'n_predictions': len(results_df),
    'n_comparisons': len(comp_df),
    'mean_R2_curvature': round(curv_avg, 6),
    'mean_R2_raw_descriptors': round(raw_avg, 6),
    'mean_R2_combined': round(comb_avg, 6),
    'curvature_vs_raw_delta': round(curv_avg - raw_avg, 6),
    'combined_vs_raw_delta': round(comb_avg - raw_avg, 6),
    'n_curv_wins': int(curv_wins),
    'n_combined_wins': int(combined_wins),
    'n_total_comparisons': len(comp_df),
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/e3_summary.json', 'w') as f:
    json.dump(e3_summary, f, indent=2)
print(f'  E3 summary saved')

# Print key results
print(f'\n  Mean R² — curvature:      {curv_avg:.4f}')
print(f'  Mean R² — raw descriptors: {raw_avg:.4f}')
print(f'  Mean R² — combined:        {comb_avg:.4f}')
print(f'  Curvature wins in {curv_wins}/{len(comp_df)} comparisons')
print(f'  Combined wins in {combined_wins}/{len(comp_df)} comparisons')

print(f'\nE3 COMPLETE ({time.time()-t0:.0f}s)')
