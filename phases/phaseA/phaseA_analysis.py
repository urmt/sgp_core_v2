"""
Phase A5: Adversarial predictive testing (efficient version).
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import LeaveOneOut, train_test_split
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

SEED = 1002
rng = np.random.default_rng(SEED)

df = pd.read_csv('/home/student/sgp_core_v2/phases/phaseA/phaseA_metrics.csv')
domains = df['domain'].unique()
desc_cols = ['CSR', 'RBS', 'ADI', 'RTP', 'SRD']
stab_cols = ['stability_return_time', 'stability_recovery_rate', 'stability_final_dev', 'stability_max_dev']
fert_cols = ['fertility_state_diversity', 'fertility_novelty_rate', 'fertility_state_coverage',
             'fertility_transition_entropy']
all_targets = stab_cols + fert_cols

def clean(df, domain=None, target=None):
    m = pd.Series(True, index=df.index)
    if domain: m &= df['domain'] == domain
    if target: m &= df[target].notna() & np.isfinite(df[target].values)
    for c in desc_cols: m &= df[c].notna() & np.isfinite(df[c].values)
    return m

# ============================================================
# 1. LEAKAGE DETECTION
# ============================================================
print('='*70)
print('LEAKAGE DETECTION')
print('='*70)

for target in all_targets:
    mask = clean(df, target=target)
    X = StandardScaler().fit_transform(df.loc[mask, desc_cols])
    y = df.loc[mask, target].values
    if len(y) < 10: continue
    lr = LinearRegression().fit(X, y)
    loo = LeaveOneOut()
    p = np.empty(len(y))
    for tr, te in loo.split(X):
        p[te[0]] = LinearRegression().fit(X[tr], y[tr]).predict(X[te])[0]
    r2, r, _ = r2_score(y, p), *pearsonr(y, p)
    risk = 'HIGH-RISK' if r2 > 0.5 else ('MODERATE' if r2 > 0.2 else 'LOW-RISK')
    print(f'  {target:35s}  LOOCV_R²={r2:.4f}  r={r:.4f}  {risk}')

# ============================================================
# 2. CROSS-DOMAIN GENERALIZATION (Linear only, efficient)
# ============================================================
print('\n' + '='*70)
print('CROSS-DOMAIN GENERALIZATION')
print('='*70)

target = 'stability_recovery_rate'
for test_domain in domains:
    train_domains = [d for d in domains if d != test_domain]
    tr_mask = clean(df, target=target) & df['domain'].isin(train_domains)
    te_mask = clean(df, target=target) & (df['domain'] == test_domain)
    if te_mask.sum() < 5: continue
    X_tr = StandardScaler().fit_transform(df.loc[tr_mask, desc_cols])
    X_te = StandardScaler().fit_transform(df.loc[te_mask, desc_cols])
    y_tr, y_te = df.loc[tr_mask, target].values, df.loc[te_mask, target].values
    lr = LinearRegression().fit(X_tr, y_tr)
    r2_te = r2_score(y_te, lr.predict(X_te))
    r_te, _ = pearsonr(y_te, lr.predict(X_te))
    print(f'  Train {",".join(train_domains):35s} → Test {test_domain:20s}  R²={r2_te:.4f}  r={r_te:.4f}')

# ============================================================
# 3. WITHIN-DOMAIN LOOCV
# ============================================================
print('\n' + '='*70)
print('WITHIN-DOMAIN LOOCV (Linear)')
print('='*70)

for target in all_targets:
    for domain in domains:
        mask = clean(df, domain, target)
        X = StandardScaler().fit_transform(df.loc[mask, desc_cols])
        y = df.loc[mask, target].values
        if len(y) < 10: continue
        loo = LeaveOneOut()
        p = np.empty(len(y))
        for tr, te in loo.split(X):
            p[te[0]] = LinearRegression().fit(X[tr], y[tr]).predict(X[te])[0]
        r2, r, _ = r2_score(y, p), *pearsonr(y, p)
        print(f'  {target:30s}  {domain:20s}  N={len(y):4d}  R²={r2:.4f}  r={r:.4f}')

# ============================================================
# 4. CSR+RBS LEAKAGE CHECK
# ============================================================
print('\n' + '='*70)
print('CSR+RBS LEAKAGE CHECK')
print('='*70)

csr_rbs = df['CSR'].values + df['RBS'].values
for target in all_targets:
    mask = df[target].notna() & np.isfinite(df[target].values)
    r, _ = pearsonr(csr_rbs[mask], df.loc[mask, target].values)
    flag = '*** LEAKAGE ***' if abs(r) > 0.8 else ''
    print(f'  CSR+RBS vs {target:30s}  r={r:.4f}  {flag}')

# ============================================================
# 5. SIMPLICITY CHECK (LR vs RF, train/test split)
# ============================================================
print('\n' + '='*70)
print('SIMPLICITY CHECK (Linear vs RF, 70/30 split)')
print('='*70)

target = 'stability_recovery_rate'
mask = clean(df, target=target)
X = StandardScaler().fit_transform(df.loc[mask, desc_cols])
y = df.loc[mask, target].values
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=SEED)
lr_r2 = r2_score(y_te, LinearRegression().fit(X_tr, y_tr).predict(X_te))
rf_r2 = r2_score(y_te, RandomForestRegressor(n_estimators=100, random_state=SEED).fit(X_tr, y_tr).predict(X_te))
print(f'  Linear: R²={lr_r2:.4f}  RF: R²={rf_r2:.4f}  Δ={rf_r2-lr_r2:.4f}')
note = 'nonlinear useful' if rf_r2 - lr_r2 > 0.03 else 'linear sufficient'
print(f'  -> {note}')

# ============================================================
# 6. SUMMARY
# ============================================================
print('\n' + '='*70)
print('SUMMARY')
print('='*70)

all_r2 = []
for target in all_targets:
    for domain in domains:
        mask = clean(df, domain, target)
        if mask.sum() < 10: continue
        X = StandardScaler().fit_transform(df.loc[mask, desc_cols])
        y = df.loc[mask, target].values
        loo = LeaveOneOut()
        p = np.empty(len(y))
        for tr, te in loo.split(X):
            p[te[0]] = LinearRegression().fit(X[tr], y[tr]).predict(X[te])[0]
        all_r2.append(r2_score(y, p))

all_r2 = np.array(all_r2)
print(f'  All LOOCV R²: mean={np.mean(all_r2):.4f}  max={np.max(all_r2):.4f}  min={np.min(all_r2):.4f}')
print(f'  R² > 0.3: {np.mean(all_r2 > 0.3):.3f}  R² > 0.5: {np.mean(all_r2 > 0.5):.3f}')

print('\n  CONCLUSION:')
if np.max(all_r2) > 0.5:
    print('  Moderate predictive power — structural descriptors partially predict behavior.')
elif np.mean(all_r2) > 0.1:
    print('  Weak but detectable signal. No strong predictive structure found.')
else:
    print('  No meaningful predictive relationship between structural descriptors and behavior.')

print('\n=== PHASE A COMPLETE ===')
