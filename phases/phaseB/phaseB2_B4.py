"""
Phase B2: Universality clustering from transfer matrix
Phase B3: Representation alignment (CCA)
Phase B4: Feature stability analysis
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_decomposition import CCA
from sklearn.metrics import r2_score
from sklearn.model_selection import LeaveOneOut
from scipy.stats import pearsonr, spearmanr
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')

SEED = 2001
rng = np.random.default_rng(SEED)

df = pd.read_csv('/home/student/sgp_core_v2/phases/phaseA/phaseA_metrics.csv')
domains = sorted(df['domain'].unique())
desc_cols = ['CSR', 'RBS', 'ADI', 'RTP', 'SRD']
targets = ['stability_return_time', 'stability_recovery_rate', 'stability_final_dev',
           'stability_max_dev', 'fertility_state_diversity', 'fertility_transition_entropy']
# Exclude degenerate targets
exclude = ['fertility_novelty_rate', 'fertility_state_coverage']

def clean(df, domain=None, target=None):
    m = pd.Series(True, index=df.index)
    if domain: m &= df['domain'] == domain
    if target: m &= df[target].notna() & np.isfinite(df[target].values)
    for c in desc_cols: m &= df[c].notna() & np.isfinite(df[c].values)
    return m

# ============================================================
# PHASE B2: UNIVERSALITY CLUSTERING
# ============================================================
print('='*70)
print('PHASE B2 — UNIVERSALITY CLUSTERING')
print('='*70)

# Build transfer distance matrix: 1 - max(R², 0) for each (A→B, B→A) mean
n_dom = len(domains)
dist_mat = np.zeros((n_dom, n_dom))

for i, d1 in enumerate(domains):
    for j, d2 in enumerate(domains):
        if i == j:
            dist_mat[i, j] = 0
            continue
        # Mean of best R² across targets for both directions
        left, right = [], []
        for t in targets:
            tr_mask = clean(df, domain=d1, target=t)
            te_mask = clean(df, domain=d2, target=t)
            if tr_mask.sum() < 10 or te_mask.sum() < 10: continue
            X_tr = StandardScaler().fit_transform(df.loc[tr_mask, desc_cols])
            X_te = StandardScaler().fit_transform(df.loc[te_mask, desc_cols])
            lr = LinearRegression().fit(X_tr, df.loc[tr_mask, t].values)
            left.append(max(0, r2_score(df.loc[te_mask, t].values, lr.predict(X_te))))
            
            tr_mask2 = clean(df, domain=d2, target=t)
            te_mask2 = clean(df, domain=d1, target=t)
            X_tr2 = StandardScaler().fit_transform(df.loc[tr_mask2, desc_cols])
            X_te2 = StandardScaler().fit_transform(df.loc[te_mask2, desc_cols])
            lr2 = LinearRegression().fit(X_tr2, df.loc[tr_mask2, t].values)
            right.append(max(0, r2_score(df.loc[te_mask2, t].values, lr2.predict(X_te2))))
        
        # Distance: average of transfer failure
        both = np.mean(left + right) if left + right else 0
        dist_mat[i, j] = 1 - both  # 0 = perfect transfer, 1 = no transfer

print('Transfer distance matrix:')
print(f'{"":<25s}', end='')
for d in domains:
    print(f'{d[:15]:>15s}', end='')
print()
for i, d in enumerate(domains):
    print(f'{d:<20s}', end='')
    for j in range(n_dom):
        print(f'{dist_mat[i,j]:>15.4f}', end='')
    print()

# Hierarchical clustering
Z = linkage(squareform(dist_mat), method='average')
print('\nHierarchical clustering linkage:')
for i, row in enumerate(Z):
    print(f'  Step {i}: merge clusters {int(row[0])} and {int(row[1])}, dist={row[2]:.4f}')

# Find clusters at threshold
if len(domains) <= 4:
    print(f'\nDomains: {domains} at threshold 0.5:')
    clusters = fcluster(Z, 0.5, criterion='distance')
    for i, d in enumerate(domains):
        print(f'  {d:25s} → cluster {clusters[i]}')

# ============================================================
# PHASE B3: REPRESENTATION ALIGNMENT (CCA)
# ============================================================
print('\n' + '='*70)
print('PHASE B3 — REPRESENTATION ALIGNMENT (CCA)')
print('='*70)

target = 'fertility_state_diversity'
mask = {}
X_s, y_s = {}, {}
for d in domains:
    m = clean(df, domain=d, target=target)
    mask[d] = m
    X_s[d] = StandardScaler().fit_transform(df.loc[m, desc_cols])
    y_s[d] = df.loc[m, target].values

print('\nCanonical Correlation Analysis between domain pairs:')
for i, d1 in enumerate(domains):
    for d2 in domains[i+1:]:
        # Subsample to same size
        n = min(len(y_s[d1]), len(y_s[d2]))
        idx1 = rng.choice(len(y_s[d1]), n, replace=False)
        idx2 = rng.choice(len(y_s[d2]), n, replace=False)
        X1 = X_s[d1][idx1]
        X2 = X_s[d2][idx2]
        
        try:
            cca = CCA(n_components=min(3, X1.shape[1], X2.shape[1]))
            cca.fit(X1, X2)
            X1_c, X2_c = cca.transform(X1, X2)
            # Canonical correlations
            corrs = []
            for k in range(X1_c.shape[1]):
                r, _ = pearsonr(X1_c[:, k], X2_c[:, k])
                corrs.append(r)
            print(f'  {d1:25s} ↔ {d2:25s}  canonical corrs: {[f"{c:.4f}" for c in corrs]}')
            print(f'    Mean canonical corr: {np.mean(corrs):.4f}')
            
            # Test: predict target in d2 using CCA-aligned space from d1
            if X1_c.shape[1] >= 1:
                cca_lr = LinearRegression().fit(X1_c, y_s[d1][idx1])
                # Transform d2 into d1 space
                pred_d2 = cca_lr.predict(X2_c)
                r2_trans = r2_score(y_s[d2][idx2], pred_d2)
                r_trans, _ = pearsonr(y_s[d2][idx2], pred_d2)
                print(f'    CCA-transfer R²={r2_trans:.4f}  r={r_trans:.4f}')
        except Exception as e:
            print(f'  {d1:25s} ↔ {d2:25s}  CCA failed: {e}')

# ============================================================
# PHASE B4: FEATURE STABILITY
# ============================================================
print('\n' + '='*70)
print('PHASE B4 — FEATURE STABILITY / IMPORTANCE')
print('='*70)

target = 'fertility_state_diversity'
print(f'\nTarget: {target}')
for domain in domains:
    mask = clean(df, domain=domain, target=target)
    X = StandardScaler().fit_transform(df.loc[mask, desc_cols])
    y = df.loc[mask, target].values
    
    # Linear coefficients
    lr = LinearRegression().fit(X, y)
    
    # RF feature importance
    rf = RandomForestRegressor(n_estimators=100, random_state=SEED)
    rf.fit(X, y)
    
    # Permutation importance
    n_perm = 500
    perm_imp = np.zeros((n_perm, len(desc_cols)))
    baseline = r2_score(y, lr.predict(X))
    for p in range(n_perm):
        for f in range(len(desc_cols)):
            X_perm = X.copy()
            X_perm[:, f] = rng.permutation(X_perm[:, f])
            perm_imp[p, f] = baseline - r2_score(y, LinearRegression().fit(X_perm, y).predict(X_perm))
    
    # SHAP-free feature importance
    print(f'\n  {domain:25s}:')
    print(f'  {"Feature":>8s}  {"Lin_coef":>10s}  {"RF_imp":>10s}  {"Perm_imp":>10s}  {"Perm_std":>10s}')
    for f, col in enumerate(desc_cols):
        lc = lr.coef_[f]
        rf_i = rf.feature_importances_[f]
        pi = np.mean(perm_imp[:, f])
        ps = np.std(perm_imp[:, f])
        print(f'  {col:>8s}  {lc:>10.4f}  {rf_i:>10.4f}  {pi:>10.6f}  {ps:>10.6f}')

# ============ Cross-domain feature importance similarity ============
print('\nFeature importance similarity across domains:')
print(f'{"":<25s}', end='')
for d in domains:
    print(f'{d[:15]:>15s}', end='')
print()

# Compute pairwise correlation of linear coefficients
for i, d1 in enumerate(domains):
    print(f'{d1:<20s}', end='')
    for j, d2 in enumerate(domains):
        mask1 = clean(df, domain=d1, target='fertility_state_diversity')
        mask2 = clean(df, domain=d2, target='fertility_state_diversity')
        X1 = StandardScaler().fit_transform(df.loc[mask1, desc_cols])
        y1 = df.loc[mask1, 'fertility_state_diversity'].values
        X2 = StandardScaler().fit_transform(df.loc[mask2, desc_cols])
        y2 = df.loc[mask2, 'fertility_state_diversity'].values
        c1 = LinearRegression().fit(X1, y1).coef_
        c2 = LinearRegression().fit(X2, y2).coef_
        r, _ = pearsonr(c1, c2)
        print(f'{r:>15.4f}', end='')
    print()

# ============ Save summaries ============
print('\n=== PHASES B2–B4 COMPLETE ===')
