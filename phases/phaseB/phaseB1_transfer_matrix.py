"""
Phase B1: Full pairwise transfer matrix across 4 domains.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import LeaveOneOut
from scipy.stats import spearmanr, pearsonr
import warnings
warnings.filterwarnings('ignore')

SEED = 2000
rng = np.random.default_rng(SEED)

df = pd.read_csv('/home/student/sgp_core_v2/phases/phaseA/phaseA_metrics.csv')
domains = sorted(df['domain'].unique())
desc_cols = ['CSR', 'RBS', 'ADI', 'RTP', 'SRD']
targets = ['stability_return_time', 'stability_recovery_rate', 'stability_final_dev',
           'stability_max_dev', 'fertility_state_diversity', 'fertility_novelty_rate',
           'fertility_state_coverage', 'fertility_transition_entropy']

def clean(df, domain=None, target=None):
    m = pd.Series(True, index=df.index)
    if domain: m &= df['domain'] == domain
    if target: m &= df[target].notna() & np.isfinite(df[target].values)
    for c in desc_cols: m &= df[c].notna() & np.isfinite(df[c].values)
    return m

models = {
    'Linear': LinearRegression(),
    'Ridge': Ridge(alpha=1.0, random_state=SEED),
    'RF': RandomForestRegressor(n_estimators=100, random_state=SEED),
    'GB': GradientBoostingRegressor(n_estimators=50, random_state=SEED),
}

# ============ Build full transfer tensor: [train][test][target][model] ============
results = []

for target in targets:
    for train_dom in domains:
        for test_dom in domains:
            tr_mask = clean(df, domain=train_dom, target=target)
            te_mask = clean(df, domain=test_dom, target=target)
            if tr_mask.sum() < 10 or te_mask.sum() < 10:
                continue

            X_tr = StandardScaler().fit_transform(df.loc[tr_mask, desc_cols])
            y_tr = df.loc[tr_mask, target].values
            X_te = StandardScaler().fit_transform(df.loc[te_mask, desc_cols])
            y_te = df.loc[te_mask, target].values

            for mname, model in models.items():
                m = model.__class__(**model.get_params()) if hasattr(model, 'get_params') else model.__class__()
                try:
                    m.fit(X_tr, y_tr)
                    preds = m.predict(X_te)
                    r2 = r2_score(y_te, preds)
                    r2 = max(min(r2, 1.0), -20.0)  # clip extreme negatives
                    mae = mean_absolute_error(y_te, preds)
                    rho, _ = spearmanr(y_te, preds) if np.std(preds) > 0 else (0, 1)
                except:
                    r2, mae, rho = -99, 99, 0

                results.append({
                    'target': target,
                    'train_domain': train_dom,
                    'test_domain': test_dom,
                    'model': mname,
                    'R2': round(r2, 4),
                    'MAE': round(mae, 4),
                    'Spearman_r': round(rho, 4),
                })

df_r = pd.DataFrame(results)
df_r.to_csv('/home/student/sgp_core_v2/phases/phaseB/phaseB1_transfer_matrix_full.csv', index=False)

# ============ Aggregate: mean across targets, best model per pair ============
print('='*70)
print('PHASE B1 — PAIRWISE TRANSFER MATRIX')
print('='*70)

# For each (train, test) pair, best R² across models × targets
pairs = df_r.groupby(['train_domain', 'test_domain'])
best_per_pair = pairs['R2'].max().reset_index()
mean_per_pair = pairs['R2'].mean().reset_index()

print('\nBest R² across all models × targets:')
print(f'{"Train→Test":<30s}  {"Best R²":>8s}  {"Mean R²":>8s}  {"N_train":>8s}  {"N_test":>8s}')
print('-' * 65)
for _, row in best_per_pair.iterrows():
    train, test = row['train_domain'], row['test_domain']
    best = row['R2']
    mean_r = mean_per_pair[(mean_per_pair['train_domain'] == train) & (mean_per_pair['test_domain'] == test)]['R2'].values[0]
    n_tr = clean(df, domain=train).sum()
    n_te = clean(df, domain=test).sum()
    marker = '***' if best > 0 else '   '
    print(f'{train:15s} → {test:15s}  {marker} {best:>8.4f}  {mean_r:>8.4f}  {n_tr:>4d}  {n_te:>4d}')

# ============ Transfer matrix (mean R² across targets, Linear only) ============
print('\n\nTransfer matrix: Linear regression, mean R² across targets')
print(f'{"":25s}', end='')
for td in domains:
    print(f'{td:>20s}', end='')
print()
for td in domains:
    print(f'{td:20s}', end='')
    for tt in domains:
        sub = df_r[(df_r['train_domain'] == td) & (df_r['test_domain'] == tt) & (df_r['model'] == 'Linear')]
        v = sub['R2'].mean()
        print(f'{v:>20.4f}', end='')
    print()

# ============ Transfer matrix (best model) ============
print('\n\nTransfer matrix: Best model R² (max across models)')
print(f'{"":25s}', end='')
for td in domains:
    print(f'{td:>20s}', end='')
print()
for td in domains:
    print(f'{td:20s}', end='')
    for tt in domains:
        sub = df_r[(df_r['train_domain'] == td) & (df_r['test_domain'] == tt)]
        v = sub['R2'].max()
        print(f'{v:>20.4f}', end='')
    print()

# ============ Asymmetry analysis ============
print('\n\nTransfer asymmetry (mean |A→B - B→A|):')
asym = []
for i, d1 in enumerate(domains):
    for d2 in domains[i+1:]:
        fwd = df_r[(df_r['train_domain'] == d1) & (df_r['test_domain'] == d2)]['R2'].mean()
        rev = df_r[(df_r['train_domain'] == d2) & (df_r['test_domain'] == d1)]['R2'].mean()
        diff = abs(fwd - rev)
        asym.append({'pair': f'{d1}↔{d2}', 'forward': round(fwd, 4), 'reverse': round(rev, 4), 'asymmetry': round(diff, 4)})
        print(f'  {d1:20s} ↔ {d2:20s}  fwd={fwd:.4f}  rev={rev:.4f}  |diff|={diff:.4f}')

pd.DataFrame(asym).to_csv('/home/student/sgp_core_v2/phases/phaseB/phaseB1_asymmetry.csv', index=False)

# ============ Within-domain vs cross-domain summary ============
print('\n\nWithin-domain vs Cross-domain:')
within = df_r[df_r['train_domain'] == df_r['test_domain']]['R2']
cross = df_r[df_r['train_domain'] != df_r['test_domain']]['R2']
print(f'  Within-domain:  mean={within.mean():.4f}  std={within.std():.4f}  n={len(within)}')
print(f'  Cross-domain:   mean={cross.mean():.4f}  std={cross.std():.4f}  n={len(cross)}')
print(f'  Positive cross-domain pairs: {(cross > 0).sum()} / {len(cross)} ({(cross > 0).mean()*100:.1f}%)')

# ============ Summary save ============
summary = pd.DataFrame([{
    'phase': 'B1',
    'within_mean_R2': round(within.mean(), 4),
    'cross_mean_R2': round(cross.mean(), 4),
    'cross_positive_rate': round((cross > 0).mean(), 4),
    'best_cross_R2': round(cross.max(), 4),
    'worst_cross_R2': round(cross.min(), 4),
    'mean_asymmetry': round(np.mean([a['asymmetry'] for a in asym]), 4),
}])
summary.to_csv('/home/student/sgp_core_v2/phases/phaseB/phaseB1_summary.csv', index=False)

print('\n=== PHASE B1 COMPLETE ===')
