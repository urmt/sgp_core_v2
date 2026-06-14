"""
Phase E1 — Organizational Curvature Geometry (Full Persistence).
Computes coefficient vectors, curvature metrics, neighborhood graphs.
Saves all outputs immediately with manifest.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import r2_score
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseE'
os.makedirs(f'{BASE}/raw', exist_ok=True)
os.makedirs(f'{BASE}/processed', exist_ok=True)
os.makedirs(f'{BASE}/summaries', exist_ok=True)
os.makedirs(f'{BASE}/manifests', exist_ok=True)

CSV_SRC = '/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv'
df = pd.read_csv(CSV_SRC)
domains = sorted(df['domain'].unique())
COLS = ['CSR','RBS','ADI','RTP','SRD']
TARGET = 'fertility_state_diversity'
K = 30

df['sys_idx'] = df.groupby('domain').cumcount()
N_TOTAL = len(df)

print('='*70)
print('PHASE E1 — CURVATURE GEOMETRY (PERSISTENT)')
print('='*70)
t0 = time.time()

# --- Step 1: Precompute coefficient vectors per system ---
beta_cols = [f'beta_{c}' for c in COLS]
all_coeffs = []

for domain in domains:
    m = df['domain'] == domain
    dm = df[m].copy().reset_index(drop=True)
    N = len(dm)
    X = StandardScaler().fit_transform(dm[COLS].values)
    y = dm[TARGET].values
    
    nbrs = NearestNeighbors(n_neighbors=min(K+1, N)).fit(X)
    _, indices = nbrs.kneighbors(X)
    nb_idx = indices[:, 1:]
    
    for i in range(N):
        nb = nb_idx[i]
        if len(nb) < 5:
            all_coeffs.append(dict(zip(['sys_idx','domain']+beta_cols, [i, domain]+[0.0]*5)))
            continue
        lr = LinearRegression().fit(X[nb], y[nb])
        all_coeffs.append(dict(zip(['sys_idx','domain']+beta_cols, [i, domain]+list(lr.coef_))))

coeff_df = pd.DataFrame(all_coeffs)
coeff_path = f'{BASE}/raw/local_coeff_vectors.csv'
coeff_df.to_csv(coeff_path, index=False)
print(f'  Coefficient vectors saved: {coeff_path} ({len(coeff_df)} rows)')

# --- Step 2: Neighborhood graph with distances ---
graph_rows = []
for domain in domains:
    m = df['domain'] == domain
    dm = df[m].copy().reset_index(drop=True)
    N = len(dm)
    X = StandardScaler().fit_transform(dm[COLS].values)
    
    nbrs = NearestNeighbors(n_neighbors=min(K+1, N), metric='euclidean').fit(X)
    distances, indices = nbrs.kneighbors(X)
    
    for i in range(N):
        for j, d in zip(indices[i, 1:], distances[i, 1:]):
            graph_rows.append({'src_sys_idx': i, 'dst_sys_idx': j,
                               'domain': domain, 'euclidean_dist': d})

graph_df = pd.DataFrame(graph_rows)
graph_path = f'{BASE}/raw/neighborhood_graph.csv'
graph_df.to_csv(graph_path, index=False)
print(f'  Neighborhood graph saved: {graph_path} ({len(graph_df)} edges)')

# --- Step 3: Curvature metrics (6 geometric transition metrics) ---
curv_rows = []
for domain in domains:
    m = df['domain'] == domain
    dm = df[m].copy().reset_index(drop=True)
    N = len(dm)
    X = StandardScaler().fit_transform(dm[COLS].values)
    y = dm[TARGET].values
    
    if np.std(y) < 1e-10:
        for i in range(N):
            curv_rows.append({k:0.0 for k in['sys_idx','domain','tangent_rotation','local_curvature',
                'predictive_shear','geodesic_instab','jacobian_vol','desc_switch_vel']})
        continue
    
    nbrs = NearestNeighbors(n_neighbors=min(K+1, N)).fit(X)
    _, indices = nbrs.kneighbors(X)
    nb_idx = indices[:, 1:]
    
    # Precompute betas for neighbors
    betas = np.zeros((N, 5))
    best_desc = np.zeros(N, dtype=int)
    for i in range(N):
        nb = nb_idx[i]
        if len(nb) < 5: continue
        betas[i] = LinearRegression().fit(X[nb], y[nb]).coef_
        r2s = np.zeros(5)
        for j in range(5):
            xj = X[nb][:, j].reshape(-1,1)
            if np.std(xj) > 1e-12 and np.std(y[nb]) > 1e-10:
                r2s[j] = r2_score(y[nb], LinearRegression().fit(xj, y[nb]).predict(xj))
        best_desc[i] = np.argmax(r2s)
    
    for i in range(N):
        nb = nb_idx[i]
        if len(nb) < 5:
            curv_rows.append({'sys_idx':i,'domain':domain,
                'tangent_rotation':0,'local_curvature':0,'predictive_shear':0,
                'geodesic_instab':0,'jacobian_vol':0,'desc_switch_vel':0})
            continue
        
        beta_i = betas[i]
        nb_betas = betas[nb]
        valid = np.array([len(nb_idx[j]) >= 5 for j in nb])
        if np.sum(valid) < 2:
            curv_rows.append({'sys_idx':i,'domain':domain,
                'tangent_rotation':0,'local_curvature':0,'predictive_shear':0,
                'geodesic_instab':0,'jacobian_vol':0,'desc_switch_vel':0})
            continue
        
        nb_betas_v = nb_betas[valid]
        nb_norms = np.linalg.norm(nb_betas_v, axis=1)
        bi_norm = np.linalg.norm(beta_i)
        cos_sim = np.clip(np.dot(nb_betas_v, beta_i) / (nb_norms*bi_norm + 1e-10), -1, 1)
        tr = float(np.mean(np.arccos(cos_sim)))
        lc = float(np.mean(np.sqrt(np.sum((nb_betas_v - beta_i)**2, axis=1))))
        
        Xnb = X[nb]
        preds_v = Xnb @ nb_betas_v.T
        ps = float(np.var(np.mean(preds_v, axis=0)))
        
        pred_i = Xnb @ beta_i
        y_nb = y[nb[valid]]
        gi = float(1 - r2_score(y_nb[:len(pred_i)], pred_i[:len(y_nb)])) if np.std(y_nb) > 1e-10 else 0.0
        jv = float(np.var(nb_betas_v.flatten()))
        dsv = float(len(np.unique(best_desc[nb[valid]])) / 5.0)
        
        curv_rows.append({'sys_idx':i,'domain':domain,'tangent_rotation':tr,
            'local_curvature':lc,'predictive_shear':ps,'geodesic_instab':gi,
            'jacobian_vol':jv,'desc_switch_vel':dsv})
    
    print(f'  {domain}: {N} systems → curvature computed ({time.time()-t0:.0f}s)')

curv_df = pd.DataFrame(curv_rows)
curv_path = f'{BASE}/processed/curvature_metrics.csv'
curv_df.to_csv(curv_path, index=False)
print(f'  Curvature metrics saved: {curv_path} ({len(curv_df)} rows)')

# --- E1 Summary ---
curv_means = curv_df[[c for c in curv_df.columns if c not in ('sys_idx','domain')]].mean().to_dict()
curv_stds = curv_df[[c for c in curv_df.columns if c not in ('sys_idx','domain')]].std().to_dict()
e1_summary = {
    'phase': 'E1', 'seed': SEED, 'k': K, 'target': TARGET,
    'n_systems': N_TOTAL, 'n_domains': len(domains),
    'descriptors': COLS,
    'curvature_metric_means': {k: round(v, 6) for k, v in curv_means.items()},
    'curvature_metric_stds': {k: round(v, 6) for k, v in curv_stds.items()},
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/e1_summary.json', 'w') as f:
    json.dump(e1_summary, f, indent=2)
print(f'  E1 summary saved')

# --- Save curvature tensor (stack of Jacobians) for each domain ---
tensor_data = {}
for d in domains:
    c = coeff_df[coeff_df['domain'] == d][beta_cols].values
    tensor_data[f'{d}_coeffs'] = c
tensor_path = f'{BASE}/raw/curvature_tensors.npz'
np.savez_compressed(tensor_path, **tensor_data)
print(f'  Curvature tensors saved: {tensor_path}')

print(f'\nE1 COMPLETE ({time.time()-t0:.0f}s)')
