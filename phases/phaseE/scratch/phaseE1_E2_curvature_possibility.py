"""
Phase E1+E2 — Curvature Geometry + Possibility Space (optimized).
Precomputes one coefficient vector per system from its local neighborhood,
then all geometric metrics are derived from these vectors via simple operations.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import r2_score
from scipy.stats import pearsonr, entropy
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
OUT = '/home/student/sgp_core_v2/phases/phaseE'
CSV_SRC = '/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv'
df = pd.read_csv(CSV_SRC)
domains = sorted(df['domain'].unique())
cols = ['CSR','RBS','ADI','RTP','SRD']
fertility_targets = [c for c in df.columns if c.startswith('fertility_')]
K = 30
target = 'fertility_state_diversity'

df['sys_idx'] = df.groupby('domain').cumcount()
t_start = time.time()

print('='*70)
print('PHASE E1 — CURVATURE GEOMETRY (optimized)')
print('='*70)

curv_records = []
total_systems = 0

for domain in domains:
    m = df['domain'] == domain
    dm = df[m].copy().reset_index(drop=True)
    N = len(dm)
    X = StandardScaler().fit_transform(dm[cols].values)
    y = dm[target].values
    
    if np.std(y) < 1e-10 or N < 10:
        for i in range(N):
            curv_records.append({k:0.0 for k in ['sys_idx','domain','tangent_rotation',
                'local_curvature','predictive_shear','geodesic_instab','jacobian_vol','desc_switch_vel']})
            curv_records[-1]['sys_idx'] = i
            curv_records[-1]['domain'] = domain
        continue
    
    nbrs = NearestNeighbors(n_neighbors=min(K+1, N)).fit(X)
    _, indices = nbrs.kneighbors(X)
    nb_idx = indices[:, 1:]  # exclude self
    
    # Precompute β vector for every system (coefficients of local model on its neighbors)
    betas = np.zeros((N, 5))
    best_desc = np.zeros(N, dtype=int)
    preds_nb = np.zeros((N, min(K, N-1)))
    y_pred_self = np.zeros(N)
    y_scored = np.zeros(N)
    n_nb_actual = np.zeros(N, dtype=int)
    
    for i in range(N):
        nb = nb_idx[i]
        if len(nb) < 5:
            betas[i] = 0; best_desc[i] = 0
            continue
        nbr = nb[:]
        Xnb = X[nbr]; ynb = y[nbr]
        
        # 5D local model
        lr = LinearRegression().fit(Xnb, ynb)
        betas[i] = lr.coef_
        y_pred_self[i] = np.mean(lr.predict(Xnb))
        y_scored[i] = np.mean(ynb)
        n_nb_actual[i] = len(nbr)
        
        # Single-descriptor R² to find best descriptor
        r2s = np.zeros(5)
        for j in range(5):
            xj = Xnb[:, j].reshape(-1, 1)
            if np.std(xj) > 1e-12 and np.std(ynb) > 1e-10:
                r2s[j] = r2_score(ynb, LinearRegression().fit(xj, ynb).predict(xj))
        best_desc[i] = np.argmax(r2s)
    
    # Now compute curvature metrics using precomputed betas
    for i in range(N):
        nb = nb_idx[i]
        if len(nb) < 5:
            curv_records.append({'sys_idx':i,'domain':domain,'tangent_rotation':0,
                'local_curvature':0,'predictive_shear':0,'geodesic_instab':0,
                'jacobian_vol':0,'desc_switch_vel':0})
            continue
        
        beta_i = betas[i]
        nb_betas = betas[nb]  # shape (N_nb, 5)
        nb_nn = np.array([len(nb_idx[j]) for j in nb])
        valid = nb_nn >= 5
        
        if np.sum(valid) < 2:
            curv_records.append({'sys_idx':i,'domain':domain,'tangent_rotation':0,
                'local_curvature':0,'predictive_shear':0,'geodesic_instab':0,
                'jacobian_vol':0,'desc_switch_vel':0})
            continue
        
        nb_betas_v = nb_betas[valid]
        
        # 1. Tangent Rotation: mean angle between β_i and β_j
        nb_norm = np.linalg.norm(nb_betas_v, axis=1)
        bi_norm = np.linalg.norm(beta_i)
        dot_prod = np.clip(np.dot(nb_betas_v, beta_i) / (nb_norm * bi_norm + 1e-10), -1, 1)
        tangent_rotation = float(np.mean(np.arccos(dot_prod)))
        
        # 2. Local Curvature: mean L2 diff between β_j and β_i
        local_curvature = float(np.mean(np.sqrt(np.sum((nb_betas_v - beta_i)**2, axis=1))))
        
        # 3. Predictive Shear: variance of mean predictions across neighbors
        Xnb = X[nb]
        preds_v = Xnb @ nb_betas_v.T  # (N_nb, N_valid)
        predictive_shear = float(np.var(np.mean(preds_v, axis=0)))
        
        # 4. Geodesic Instability: how poorly β_i predicts its own neighborhood
        pred_i = Xnb @ beta_i
        y_nb = y[nb[valid]]
        if y_nb.shape[0] == pred_i.shape[0] and np.std(y_nb) > 1e-10:
            geodesic_instab = float(1 - r2_score(y_nb, pred_i[:len(y_nb)]))
        else:
            geodesic_instab = 0.0
        
        # 5. Jacobian Volatility: variance of all β elements in neighborhood
        jacobian_vol = float(np.var(nb_betas_v.flatten()))
        
        # 6. Descriptor Switching Velocity: fraction of descriptors appearing as best
        best_in_nb = best_desc[nb[valid]]
        desc_switch_vel = float(len(np.unique(best_in_nb)) / 5.0)
        
        curv_records.append({'sys_idx':i,'domain':domain,'tangent_rotation':tangent_rotation,
            'local_curvature':local_curvature,'predictive_shear':predictive_shear,
            'geodesic_instab':geodesic_instab,'jacobian_vol':jacobian_vol,
            'desc_switch_vel':desc_switch_vel})
    
    total_systems += N
    print(f'  {domain}: {N} systems → done ({time.time()-t_start:.0f}s)')

curv_df = pd.DataFrame(curv_records)
curv_path = os.path.join(OUT, 'phaseE1_curvature_metrics.csv')
curv_df.to_csv(curv_path, index=False)
print(f'E1 saved: {curv_path} ({len(curv_df)} rows)')

# ============================================================
# E2: Possibility Metrics
# ============================================================
print('\n' + '='*70)
print('PHASE E2 — POSSIBILITY SPACE METRICS')
print('='*70)

poss_records = []
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
    
    poss_records.append({
        'sys_idx': row['sys_idx'], 'domain': row['domain'],
        'poss_reachable_volume': rv,
        'poss_branching_diversity': bd,
        'poss_adaptive_recovery': ar,
        'poss_future_entropy': fe,
        'poss_divergence_capacity': dc,
        'poss_stability_fertility_coupling': co,
    })

poss_df = pd.DataFrame(poss_records)
poss_path = os.path.join(OUT, 'phaseE2_possibility_metrics.csv')
poss_df.to_csv(poss_path, index=False)
print(f'E2 saved: {poss_path} ({len(poss_df)} rows)')

# Leakage check: possibility vs fertility
print('\nLeakage check (possibility vs fertility):')
merged = df.merge(poss_df, on=['sys_idx','domain'])
for pc in [c for c in poss_df.columns if c not in ('sys_idx','domain')]:
    for ft in fertility_targets:
        r, p = pearsonr(merged[pc], merged[ft])
        if abs(r) > 0.85:
            print(f'  LEAKAGE: {pc} vs {ft}: r={r:.4f}')
        elif abs(r) > 0.70:
            print(f'  WARNING: {pc} vs {ft}: r={r:.4f}')

# Combine all into one dataset
combined = merged.merge(curv_df, on=['sys_idx','domain'])
combined_path = os.path.join(OUT, 'phaseE_combined.csv')
combined.to_csv(combined_path, index=False)
print(f'\nCombined: {combined_path} ({len(combined)} rows, {len(combined.columns)} cols)')

manifest = {
    'phase': 'E1+E2', 'seed': SEED, 'k': K, 'n_systems': len(df),
    'n_domains': len(domains), 'target': target,
    'curvature_metrics': [c for c in curv_df.columns if c not in ('sys_idx','domain')],
    'possibility_metrics': [c for c in poss_df.columns if c not in ('sys_idx','domain')],
    'runtime': round(time.time()-t_start),
}
with open(os.path.join(OUT, 'phaseE_manifest.json'), 'w') as f:
    json.dump(manifest, f, indent=2)
print(f'Manifest saved')
print(f'E1+E2 COMPLETE ({time.time()-t_start:.0f}s)')
