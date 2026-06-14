"""
Phase E5 — ADVERSARIAL NULL PROGRAM (CRITICAL, HIGH-PERFORMANCE).
Five strict falsification tests with full distribution persistence.
Uses existing E1 curvature where possible; vectorized operations.
"""
import numpy as np, pandas as pd, os, json, time, warnings, sys
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import r2_score
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseE'
NULL_DIR = f'{BASE}/nulls'
os.makedirs(NULL_DIR, exist_ok=True)
t0 = time.time()

# Load all data
curv = pd.read_csv(f'{BASE}/processed/curvature_metrics.csv')
poss = pd.read_csv(f'{BASE}/processed/possibility_metrics.csv')
phaseC = pd.read_csv('/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv')
phaseC['sys_idx'] = phaseC.groupby('domain').cumcount()
df = curv.merge(poss, on=['sys_idx','domain']).merge(
    phaseC[['sys_idx','domain','CSR','RBS','ADI','RTP','SRD']], on=['sys_idx','domain'])
domains = sorted(df['domain'].unique())

COLS_DESC = ['CSR','RBS','ADI','RTP','SRD']
COLS_CURV = ['tangent_rotation','local_curvature','predictive_shear',
             'geodesic_instab','jacobian_vol','desc_switch_vel']
COLS_POSS = ['poss_reachable_volume','poss_branching_diversity',
             'poss_adaptive_recovery','poss_future_entropy',
             'poss_divergence_capacity','poss_stability_fertility_coupling']
K_DEFAULT = 30

print('='*70)
print('PHASE E5 — ADVERSARIAL NULL PROGRAM (HIGH-PERFORMANCE)')
print('='*70)
print(f'Runtime budget: unlimited (optimized)')
sys.stdout.flush()

# Helper: fast curvature from descriptor data (cache-efficient)
def compute_metrics_from_domain(X, y, k=K_DEFAULT):
    N = len(X)
    metrics = np.zeros((N, 6))
    if N < 10 or np.std(y) < 1e-10:
        return metrics, np.zeros((N, 5)), np.zeros(N, dtype=int)

    nbrs = NearestNeighbors(n_neighbors=min(k+1, N)).fit(X)
    _, idx = nbrs.kneighbors(X)
    nb_idx = idx[:, 1:]

    betas = np.zeros((N, 5))
    best_desc = np.zeros(N, dtype=int)
    for i in range(N):
        nb = nb_idx[i]
        if len(nb) < 5: continue
        lr = LinearRegression().fit(X[nb], y[nb])
        betas[i] = lr.coef_
        r2s = np.zeros(5)
        for j in range(5):
            xj = X[nb, j].reshape(-1,1)
            if np.std(xj) > 1e-12 and np.std(y[nb]) > 1e-10:
                r2s[j] = r2_score(y[nb], LinearRegression().fit(xj, y[nb]).predict(xj))
        best_desc[i] = np.argmax(r2s)

    for i in range(N):
        nb = nb_idx[i]
        if len(nb) < 5: continue
        bi = betas[i]
        bv = betas[nb]
        valid = np.array([len(nb_idx[j]) >= 5 for j in nb])
        if np.sum(valid) < 2: continue
        bvv = bv[valid]
        norms = np.linalg.norm(bvv, axis=1)
        cs = np.clip(np.dot(bvv, bi) / (norms * np.linalg.norm(bi) + 1e-10), -1, 1)
        metrics[i, 0] = np.mean(np.arccos(cs))
        metrics[i, 1] = np.mean(np.sqrt(np.sum((bvv-bi)**2, axis=1)))
        preds = X[nb] @ bvv.T
        metrics[i, 2] = np.var(np.mean(preds, axis=0))
        pi = X[nb] @ bi
        ynb = y[nb[valid]]
        if np.std(ynb) > 1e-10:
            metrics[i, 3] = 1 - r2_score(ynb[:len(pi)], pi[:len(ynb)])
        metrics[i, 4] = np.var(bvv.flatten())
        metrics[i, 5] = len(np.unique(best_desc[nb[valid]])) / 5.0
    return metrics, betas, best_desc

def loocv_r2(X, y):
    N = len(y)
    X_m, X_s = np.mean(X, axis=0), np.std(X, axis=0) + 1e-10
    X_n = (X - X_m) / X_s
    yp = np.zeros(N)
    for i in range(N):
        tr = np.arange(N) != i
        yp[i] = Ridge(alpha=1.0).fit(X_n[tr], y[tr]).predict(X_n[i:i+1])[0]
    return r2_score(y, yp)

# Pre-store domain reference data
dom_data = {}
for d in domains:
    dm = df[df['domain']==d].reset_index(drop=True)
    dom_data[d] = {
        'X_desc': StandardScaler().fit_transform(dm[COLS_DESC].values),
        'y_all': dm[COLS_POSS].values,
        'y0': dm[COLS_POSS[0]].values,
        'N': len(dm),
        'curv': dm[COLS_CURV].values,
    }

# ============================================================
# NULL 1: Covariance-Preserving Synthetic Manifolds
# ============================================================
print('\n--- NULL 1: Covariance-Preserving Synthetic Manifolds ---')
null1 = []
for d in domains:
    dd = dom_data[d]
    X_mu = np.mean(dd['X_desc'], axis=0)
    X_cov = np.cov(dd['X_desc'], rowvar=False)
    X_syn = StandardScaler().fit_transform(
        np.random.multivariate_normal(X_mu, X_cov, size=dd['N']))
    y_sh = np.random.permutation(dd['y0'])
    curv_syn, _, _ = compute_metrics_from_domain(X_syn, y_sh)
    r2 = loocv_r2(curv_syn, dd['y0'])
    null1.append({'domain': d, 'R2': r2})
    print(f'  {d}: R²={r2:.4f} ({time.time()-t0:.1f}s)')

pd.DataFrame(null1).to_csv(f'{NULL_DIR}/null1_covariance_synthetic.csv', index=False)

# ============================================================
# NULL 2: Neighborhood-Size Sweeps (reduced k-values)
# ============================================================
print('\n--- NULL 2: Neighborhood-Size Sweeps ---')
null2 = []
k_vals = [5, 10, 20, 30, 50]

for d in domains:
    dd = dom_data[d]
    for k in k_vals:
        if k >= dd['N']: continue
        curv_k, _, _ = compute_metrics_from_domain(dd['X_desc'], dd['y0'], k=k)
        for pj, pc in enumerate(COLS_POSS):
            r2 = loocv_r2(curv_k, dd['y_all'][:, pj])
            null2.append({'domain': d, 'k': k, 'target': pc, 'R2': r2})
    print(f'  {d}: {len(k_vals)} k-vals ({time.time()-t0:.1f}s)')

pd.DataFrame(null2).to_csv(f'{NULL_DIR}/null2_k_sensitivity.csv', index=False)

# ============================================================
# NULL 3: Descriptor Scaling Sweeps (minimal — scaling invariance test)
# ============================================================
print('\n--- NULL 3: Scaling Sensitivity (raw vs standardized) ---')
null3 = []
# Test 1: Non-standardized descriptors
for d in domains:
    dm = df[df['domain']==d].reset_index(drop=True)
    X_raw = dm[COLS_DESC].values  # NOT standardized
    curv_r, _, _ = compute_metrics_from_domain(X_raw, dom_data[d]['y0'])
    for pj, pc in enumerate(COLS_POSS):
        r2 = loocv_r2(curv_r, dom_data[d]['y_all'][:, pj])
        null3.append({'domain': d, 'variant': 'raw', 'target': pc, 'R2': r2})
    print(f'  {d} raw: done ({time.time()-t0:.1f}s)')

# Test 2: Standardized (reference — should match E1)
for d in domains:
    dd = dom_data[d]
    curv_s = dd['curv']  # from E1
    for pj, pc in enumerate(COLS_POSS):
        r2 = loocv_r2(curv_s, dd['y_all'][:, pj])
        null3.append({'domain': d, 'variant': 'standardized', 'target': pc, 'R2': r2})
    print(f'  {d} std: done ({time.time()-t0:.1f}s)')

pd.DataFrame(null3).to_csv(f'{NULL_DIR}/null3_scaling_sensitivity.csv', index=False)

# ============================================================
# NULL 4: Random Manifold Controls (3 iterations per domain)
# ============================================================
print('\n--- NULL 4: Random Manifold Controls ---')
null4 = []
n_iters = 5

for d in domains:
    dd = dom_data[d]
    N = dd['N']
    for ri in range(n_iters):
        X_rand = np.random.uniform(-2, 2, size=(N, 5))
        X_rs = StandardScaler().fit_transform(X_rand)
        y_sh = np.random.permutation(dd['y0'])
        curv_r, _, _ = compute_metrics_from_domain(X_rs, y_sh)
        r2 = loocv_r2(curv_r, dd['y0'])
        null4.append({'domain': d, 'iteration': ri, 'R2': r2})

    r2s = [r['R2'] for r in null4 if r['domain']==d]
    print(f'  {d}: mean R²={np.mean(r2s):.4f} ± {np.std(r2s):.4f} ({time.time()-t0:.1f}s)')

pd.DataFrame(null4).to_csv(f'{NULL_DIR}/null4_random_manifold_controls.csv', index=False)

# ============================================================
# NULL 5: Cross-Domain Persistence (using existing E1 curvature)
# ============================================================
print('\n--- NULL 5: Cross-Domain Persistence ---')
null5 = []

for src_d in domains:
    X_src = dom_data[src_d]['curv']
    X_src_s = StandardScaler().fit_transform(X_src)

    for tgt_d in domains:
        X_tgt = dom_data[tgt_d]['curv']
        X_tgt_s = (X_tgt - X_src.mean(axis=0)) / (X_src.std(axis=0) + 1e-10)

        for pj, pc in enumerate(COLS_POSS):
            y_src_v = dom_data[src_d]['y_all'][:, pj]
            y_tgt_v = dom_data[tgt_d]['y_all'][:, pj]
            model = Ridge(alpha=1.0).fit(X_src_s, y_src_v)
            yp = model.predict(X_tgt_s)
            r2 = r2_score(y_tgt_v, yp) if np.std(y_tgt_v) > 1e-10 else 0.0
            null5.append({'src': src_d, 'tgt': tgt_d, 'target': pc, 'R2': r2,
                          'same': src_d == tgt_d})

    print(f'  src={src_d}: {len(domains)} domains ({time.time()-t0:.1f}s)')

pd.DataFrame(null5).to_csv(f'{NULL_DIR}/null5_cross_domain_persistence.csv', index=False)

# ============================================================
# COMPILE + VERDICT
# ============================================================
print('\n' + '='*70)
print('E5 NULL COMPARISON')
print('='*70)

n1 = pd.read_csv(f'{NULL_DIR}/null1_covariance_synthetic.csv')['R2'].mean()
n2 = pd.read_csv(f'{NULL_DIR}/null2_k_sensitivity.csv')
n2_def = n2[n2['k'] == K_DEFAULT]['R2'].mean()
n3 = pd.read_csv(f'{NULL_DIR}/null3_scaling_sensitivity.csv')
n3_raw = n3[n3['variant'] == 'raw']['R2'].mean()
n3_std = n3[n3['variant'] == 'standardized']['R2'].mean()
n4 = pd.read_csv(f'{NULL_DIR}/null4_random_manifold_controls.csv')
n4_m, n4_s = n4['R2'].mean(), n4['R2'].std()
n5 = pd.read_csv(f'{NULL_DIR}/null5_cross_domain_persistence.csv')
n5_within = n5[n5['same'] == True]['R2'].mean()
n5_cross = n5[n5['same'] == False]['R2'].mean()

# True curvature R² from E3
true_r2 = pd.read_csv(f'{BASE}/processed/prediction_results.csv')
true_r2 = true_r2[true_r2['predictor_set'] == 'curvature']['R2'].mean()

print(f'\nTrue curvature R²:                {true_r2:.4f}')
print(f'Null 1 (Covariance Synthetic):     {n1:.4f}  Δ={true_r2-n1:.4f}')
print(f'Null 2 (k={K_DEFAULT}):              {n2_def:.4f}  Δ={true_r2-n2_def:.4f}')
print(f'Null 3 (raw desc):                 {n3_raw:.4f}  Δ={true_r2-n3_raw:.4f}')
print(f'Null 3 (standardized):             {n3_std:.4f}  Δ={true_r2-n3_std:.4f}')
print(f'Null 4 (Random Manifolds):          {n4_m:.4f}±{n4_s:.4f}  Δ={true_r2-n4_m:.4f}')
print(f'Null 5 (Within-domain LOOCV):       {n5_within:.4f}  Δ={true_r2-n5_within:.4f}')
print(f'Null 5 (Cross-domain):              {n5_cross:.4f}  Δ={true_r2-n5_cross:.4f}')

survive = sum([
    true_r2 > n1 + 0.03,
    true_r2 > n2_def + 0.03,
    true_r2 > n3_raw + 0.03,  # raw descriptors as baseline
    true_r2 > n4_m + 3 * n4_s,
    true_r2 > n5_cross + 0.03,
])

print(f'\nE5 VERDICT: {survive}/5 nulls survived')
if survive >= 3:
    print('✓ Curvature captures genuine geometric structure beyond noise')
else:
    print('⚠ GEOMETRIC REGRESSION ARTIFACT — curvature effects not robust')

# Save all null distributions for later synthesis
np.savez(f'{NULL_DIR}/null_all_distributions.npz',
    true_r2=true_r2,
    null1_r2=n1, null1_all=pd.read_csv(f'{NULL_DIR}/null1_covariance_synthetic.csv')['R2'].values,
    null2_k_values=n2['k'].values, null2_r2=n2['R2'].values,
    null3_raw_r2=n3_raw, null3_std_r2=n3_std,
    null4_r2=n4['R2'].values,
    null5_within=n5_within, null5_cross=n5_cross,
    survive_count=survive)

e5_s = {'phase':'E5','seed':SEED,'k_default':K_DEFAULT,
        'true_r2':round(true_r2,6),
        'null1_covariance':round(float(n1),6),
        'null2_k_default':round(float(n2_def),6),
        'null3_raw':round(float(n3_raw),6),
        'null3_standardized':round(float(n3_std),6),
        'null4_random_manifold_mean':round(float(n4_m),6),
        'null4_random_manifold_std':round(float(n4_s),6),
        'null5_within_domain':round(float(n5_within),6),
        'null5_cross_domain':round(float(n5_cross),6),
        'null_survive_count':int(survive),
        'verdict':'SURVIVES' if survive>=3 else 'GEOMETRIC_REGRESSION_ARTIFACT',
        'runtime':round(time.time()-t0)}
with open(f'{BASE}/summaries/e5_summary.json','w') as f:
    json.dump(e5_s, f, indent=2)

print(f'\nE5 COMPLETE ({time.time()-t0:.0f}s)')
