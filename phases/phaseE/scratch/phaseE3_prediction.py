"""
Phase E3 — Curvature → Possibility Prediction.
Tests whether curvature metrics predict possibility better than raw descriptors.
LOOCV within each domain, with null and raw-descriptor controls.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import r2_score, mean_squared_error
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
OUT = '/home/student/sgp_core_v2/phases/phaseE'
df = pd.read_csv(os.path.join(OUT, 'phaseE_combined.csv'))
domains = sorted(df['domain'].unique())

cols_descriptors = ['CSR','RBS','ADI','RTP','SRD']
cols_curvature = ['tangent_rotation','local_curvature','predictive_shear',
                  'geodesic_instab','jacobian_vol','desc_switch_vel']
cols_possibility = ['poss_reachable_volume','poss_branching_diversity',
                   'poss_adaptive_recovery','poss_future_entropy',
                   'poss_divergence_capacity','poss_stability_fertility_coupling']

t_start = time.time()
print('='*70)
print('PHASE E3 — CURVATURE → POSSIBILITY PREDICTION (LOOCV)')
print('='*70)

results = []

for domain in domains:
    m = df['domain'] == domain
    dm = df[m].reset_index(drop=True)
    N = len(dm)
    
    for poss_col in cols_possibility:
        y = dm[poss_col].values
        y_mean = np.mean(y)
        
        # Null: predict mean
        r2_null = r2_score(y, np.full(N, y_mean))
        rmse_null = np.sqrt(mean_squared_error(y, np.full(N, y_mean)))
        
        # Models (LOOCV through hold-one-out)
        for label, predictors in [
            ('raw_descriptors', cols_descriptors),
            ('curvature', cols_curvature),
            ('combined', cols_descriptors + cols_curvature),
        ]:
            X = dm[predictors].values
            # Normalize
            X_mean = np.mean(X, axis=0)
            X_std = np.std(X, axis=0) + 1e-10
            X_norm = (X - X_mean) / X_std
            
            y_pred = np.zeros(N)
            for i in range(N):
                train_idx = np.arange(N) != i
                X_train, X_test = X_norm[train_idx], X_norm[i:i+1]
                y_train = y[train_idx]
                
                model = Ridge(alpha=1.0).fit(X_train, y_train)
                y_pred[i] = model.predict(X_test)[0]
            
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            corr, p = pearsonr(y, y_pred)
            
            results.append({
                'domain': domain, 'possibility_metric': poss_col,
                'predictor_set': label, 'N_R2': r2, 'N_RMSE': rmse,
                'pearson_r': corr, 'pearson_p': p,
            })
    
    print(f'  {domain}: {N} systems, {len(cols_possibility)} targets → done ({time.time()-t_start:.0f}s)')

res_df = pd.DataFrame(results)
res_path = os.path.join(OUT, 'phaseE3_prediction_results.csv')
res_df.to_csv(res_path, index=False)
print(f'\nE3 saved: {res_path} ({len(res_df)} rows)')

# Summary: curvature vs descriptors, by domain and overall
print('\n--- Summary: Mean R² per predictor set ---')
summary = res_df.groupby('predictor_set').agg({'N_R2': ['mean','std']}).round(4)
print(summary)

print('\n--- Curvature wins (R² > raw_descriptors) ---')
by_col = res_df.groupby(['domain','predictor_set'])['N_R2'].mean().unstack()
if 'curvature' in by_col and 'raw_descriptors' in by_col:
    diffs = by_col['curvature'] - by_col['raw_descriptors']
    print(f'  Domain-level curv > raw in {sum(diffs > 0)}/{len(diffs)} domains')
    for d in domains:
        print(f'  {d}: curv R²={by_col.loc[d,"curvature"]:.4f} vs raw={by_col.loc[d,"raw_descriptors"]:.4f} (Δ={diffs[d]:.4f})')

# Per possibility metric
pm_summary = res_df.groupby(['predictor_set','possibility_metric'])['N_R2'].mean().unstack()
print('\n--- Mean R² per possibility metric ---')
print(pm_summary.round(4))

# Save as JSON for easy reading
summary_json = {}
for domain in domains:
    dd = res_df[res_df['domain'] == domain]
    summary_json[domain] = {}
    for _, r in dd.iterrows():
        key = f"{r['predictor_set']}__{r['possibility_metric']}"
        summary_json[domain][key] = {'R2': r['N_R2'], 'RMSE': r['N_RMSE'], 'r': r['pearson_r']}
with open(os.path.join(OUT, 'phaseE3_summary.json'), 'w') as f:
    json.dump(summary_json, f, indent=2)

print(f'E3 COMPLETE ({time.time()-t_start:.0f}s)')
