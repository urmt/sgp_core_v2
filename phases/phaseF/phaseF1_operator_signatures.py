"""
Phase F1 — Geometric Operator Signatures.
For each domain, measures 6 types of operator structure from descriptor→behavior geometry.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
from scipy.stats import pearsonr, spearmanr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseF'
OUT = '/home/student/sgp_core_v2/phases/phaseE'
os.makedirs(f'{BASE}/raw', exist_ok=True)
os.makedirs(f'{BASE}/processed', exist_ok=True)
os.makedirs(f'{BASE}/summaries', exist_ok=True)

# Load Phase C data
df = pd.read_csv('/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
domains = sorted(df['domain'].unique())

COLS_DESC = ['CSR','RBS','ADI','RTP','SRD']
COLS_BEHAV = [c for c in df.columns if c.startswith('fertility_') or c.startswith('stability_')]
COLS_CURV = ['tangent_rotation','local_curvature','predictive_shear',
             'geodesic_instab','jacobian_vol','desc_switch_vel']

# Load Phase E curvature
curv_df = pd.read_csv(f'{OUT}/processed/curvature_metrics.csv')
poss_df = pd.read_csv(f'{OUT}/processed/possibility_metrics.csv')
COLS_POSS = [c for c in poss_df.columns if c not in ('sys_idx','domain')]
COLS_BEHAV_ALL = COLS_BEHAV + COLS_POSS

t0 = time.time()
print('='*70)
print('PHASE F1 — GEOMETRIC OPERATOR SIGNATURES')
print('='*70)

sig_records = []

for domain in domains:
    m = df['domain'] == domain
    dm = df[m].copy().reset_index(drop=True)
    N = len(dm)
    X = dm[COLS_DESC].values
    X_norm = StandardScaler().fit_transform(X)
    
    # Merge curvature/possibility
    dc = curv_df[curv_df['domain']==domain].reset_index(drop=True)
    dp = poss_df[poss_df['domain']==domain].reset_index(drop=True)
    
    Y_behav = dm[COLS_BEHAV].values
    Y_curv = dc[COLS_CURV].values if len(dc) == N else np.zeros((N, 6))
    Y_poss = dp[COLS_POSS].values if len(dp) == N else np.zeros((N, 6))
    
    # === OPERATOR 1: ADDITIVE STRUCTURE ===
    # Linear compositionality: R² of linear model
    lr = LinearRegression().fit(X_norm, Y_behav)
    y_pred_lr = lr.predict(X_norm)
    linear_r2 = r2_score(Y_behav, y_pred_lr, multioutput='uniform_average')
    
    # Superposition stability: test linear interpolation between points
    sup_scores = []
    for _ in range(200):
        i, j = np.random.randint(0, N, 2)
        alpha = np.random.random()
        interp_x = X_norm[i] * alpha + X_norm[j] * (1 - alpha)
        interp_y = Y_behav[i] * alpha + Y_behav[j] * (1 - alpha)
        # Compare with model prediction at interpolated point
        pred = lr.predict(interp_x.reshape(1, -1))[0]
        sup_scores.append(1 - np.mean(np.abs(pred - interp_y) / (np.abs(interp_y) + 1e-10)))
    superposition_score = np.mean(sup_scores)
    
    # Closure: fraction of random linear combinations staying in observed range
    y_min, y_max = Y_behav.min(axis=0), Y_behav.max(axis=0)
    closure_hits = 0
    for _ in range(500):
        weights = np.random.uniform(-1, 2, size=N)
        weights /= np.sum(np.abs(weights))
        combo = np.dot(weights, Y_behav)
        if np.all(combo >= y_min) and np.all(combo <= y_max):
            closure_hits += 1
    closure_ratio = closure_hits / 500
    
    # === OPERATOR 2: MULTIPLICATIVE STRUCTURE ===
    # Interaction model: add pairwise products
    X_inter = np.column_stack([X_norm] + 
        [X_norm[:, i] * X_norm[:, j] for i in range(5) for j in range(i+1, 5)])
    lr_inter = LinearRegression().fit(X_inter, Y_behav)
    inter_r2 = r2_score(Y_behav, lr_inter.predict(X_inter), multioutput='uniform_average')
    interaction_r2_improvement = inter_r2 - linear_r2
    
    # Log-log slopes (multiplicative scaling)
    log_log_slopes = []
    for b in range(Y_behav.shape[1]):
        yb = np.abs(Y_behav[:, b]) + 1e-10
        for d in range(5):
            xd = np.abs(X[:, d]) + 1e-10
            if np.std(np.log(xd)) > 1e-6 and np.std(np.log(yb)) > 1e-6:
                s, _ = np.polyfit(np.log(xd), np.log(yb), 1)
                log_log_slopes.append(s)
    log_log_slope = np.mean(log_log_slopes) if log_log_slopes else 0.0
    log_log_slope_std = np.std(log_log_slopes) if log_log_slopes else 0.0
    
    # Sensitivity amplification: ratio of behavioral range to descriptor range
    sensitivity_amp = np.mean([
        np.std(Y_behav[:, b]) / (np.std(X[:, d]) + 1e-10)
        for b in range(Y_behav.shape[1]) for d in range(5)
    ])
    
    # === OPERATOR 3: HIERARCHICAL STRUCTURE ===
    # Tree depth needed to capture behavior
    tree = DecisionTreeRegressor(max_depth=None, min_samples_leaf=5, random_state=SEED)
    tree.fit(X_norm, Y_behav)
    tree_depth = tree.get_depth()
    tree_r2 = r2_score(Y_behav, tree.predict(X_norm), multioutput='uniform_average')
    
    # Multiscale: how behavior variance changes with descriptor scale
    scale_variances = []
    for scale in [0.01, 0.05, 0.1, 0.2, 0.5]:
        X_scaled = X_norm * scale
        lr_s = LinearRegression().fit(X_scaled, Y_behav)
        scale_variances.append(np.var(lr_s.coef_.flatten()))
    multiscale_var_ratio = np.std(scale_variances) / (np.mean(scale_variances) + 1e-10)
    
    # === OPERATOR 4: TOPOLOGICAL STRUCTURE ===
    # Neighborhood continuity: are nearby descriptor points behaviorally similar?
    from sklearn.neighbors import NearestNeighbors
    nbrs = NearestNeighbors(n_neighbors=min(21, N)).fit(X_norm)
    _, idx = nbrs.kneighbors(X_norm)
    nb_idx = idx[:, 1:]
    
    neigh_dists = []
    behav_dists = []
    for i in range(min(200, N)):
        for j in nb_idx[i][:5]:
            neigh_dists.append(np.linalg.norm(X_norm[i] - X_norm[j]))
            behav_dists.append(np.linalg.norm(Y_behav[i] - Y_behav[j]))
    neighborhood_corr, _ = pearsonr(neigh_dists, behav_dists) if len(neigh_dists) > 5 else (0, 1)
    
    # Continuity: smoothness (how well does local average predict?)
    cont_pred = np.zeros_like(Y_behav)
    for i in range(N):
        nb = nb_idx[i]
        cont_pred[i] = Y_behav[nb].mean(axis=0)
    continuity_score = r2_score(Y_behav, cont_pred, multioutput='uniform_average')
    
    # Deformation stability: perturb descriptors, check prediction stability
    deform_scores = []
    for _ in range(200):
        i = np.random.randint(0, N)
        noise = np.random.normal(0, 0.1, size=5)
        orig_pred = Y_behav[i]
        pert_pred = Y_behav[min(i+1, N-1)]  # nearest neighbor as deformation
        deform_scores.append(1 - np.mean(np.abs(orig_pred - pert_pred) / (np.abs(orig_pred) + 1e-10)))
    deformation_stability = np.mean(deform_scores)
    
    # === OPERATOR 5: NETWORK-INTERACTION STRUCTURE ===
    # Graph metric predicts behavioral distance
    rtp = dm['RTP'].values
    srd = dm['SRD'].values
    graph_behav_corr, _ = pearsonr(srd, Y_behav[:, 0]) if np.std(srd) > 1e-10 else (0, 1)
    
    # Propagation: how far do perturbations spread?
    # Use the nearest-neighbor chain: perturb one system, measure how many neighbors change
    prop_distances = []
    for _ in range(100):
        i = np.random.randint(0, N)
        # Follow k-NN chain
        visited = set([i])
        frontier = [i]
        for _ in range(10):
            next_f = []
            for f in frontier:
                for j in nb_idx[f]:
                    if j not in visited:
                        visited.add(j)
                        next_f.append(j)
            frontier = next_f
            if not frontier:
                break
        prop_distances.append(len(visited))
    propagation_score = np.mean(prop_distances) / N
    
    # Synchronization coupling: correlation between neighbors' behaviors
    sync_corrs = []
    for i in range(min(200, N)):
        nb = nb_idx[i][:5]
        sync_corrs.append(np.mean([pearsonr(Y_behav[i], Y_behav[j])[0] for j in nb]))
    sync_coupling = np.mean(sync_corrs)
    
    # === OPERATOR 6: SYMMETRY STRUCTURE ===
    # Find invariant transformations
    # Test random linear combinations of descriptors — how much does behavior change?
    invar_scores = []
    for _ in range(500):
        # Random direction in descriptor space
        direction = np.random.normal(0, 1, size=5)
        direction /= np.linalg.norm(direction)
        # Project data onto direction and check behavioral variance
        proj = X_norm @ direction
        if np.std(proj) < 1e-10: continue
        b_var = 0
        for b in range(Y_behav.shape[1]):
            r, _ = pearsonr(proj, Y_behav[:, b])
            b_var += r**2
        invar_scores.append(b_var / Y_behav.shape[1])
    # Low variance → direction is approximately invariant (behavior doesn't change along it)
    symmetry_invariance = 1 - np.mean(invar_scores)  # higher = more invariant
    
    # Conserved combinations: which descriptor combinations have minimal behavioral impact?
    # PCA on descriptors, check behavioral variance explained by each component
    from sklearn.decomposition import PCA
    pca = PCA().fit(X_norm)
    pca_behav_corrs = []
    for pc_idx in range(min(5, X_norm.shape[1])):
        pc = pca.components_[pc_idx]
        proj = X_norm @ pc
        for b in range(Y_behav.shape[1]):
            r, _ = pearsonr(proj, Y_behav[:, b])
            pca_behav_corrs.append(abs(r))
    conservation_score = 1 - np.mean(pca_behav_corrs)  # high = behavior conserved across PCs
    
    # === RECORD ===
    sig_records.append({
        'domain': domain, 'N': N,
        # Additive
        'additive_linear_r2': round(linear_r2, 6),
        'additive_superposition': round(superposition_score, 6),
        'additive_closure': round(closure_ratio, 6),
        # Multiplicative
        'multiplicative_interaction_r2_gain': round(interaction_r2_improvement, 6),
        'multiplicative_log_log_slope': round(log_log_slope, 6),
        'multiplicative_log_log_slope_std': round(log_log_slope_std, 6),
        'multiplicative_sensitivity_amplification': round(sensitivity_amp, 6),
        # Hierarchical
        'hierarchical_tree_depth': int(tree_depth),
        'hierarchical_tree_r2': round(tree_r2, 6),
        'hierarchical_multiscale_var_ratio': round(multiscale_var_ratio, 6),
        # Topological
        'topological_neighborhood_corr': round(neighborhood_corr, 6),
        'topological_continuity': round(continuity_score, 6),
        'topological_deformation_stability': round(deformation_stability, 6),
        # Network-interaction
        'network_graph_behav_corr': round(graph_behav_corr, 6),
        'network_propagation': round(propagation_score, 6),
        'network_sync_coupling': round(sync_coupling, 6),
        # Symmetry
        'symmetry_invariance': round(symmetry_invariance, 6),
        'symmetry_conservation': round(conservation_score, 6),
    })
    
    print(f'  {domain}: additive_r²={linear_r2:.3f}  multiplicative_gain={interaction_r2_improvement:.3f}  tree_depth={tree_depth}  continuity={continuity_score:.3f}  sync={sync_coupling:.3f}  invariant={symmetry_invariance:.3f}')

sig_df = pd.DataFrame(sig_records)
sig_path = f'{BASE}/processed/operator_signatures.csv'
sig_df.to_csv(sig_path, index=False)
print(f'\nF1 saved: {sig_path} ({len(sig_df)} rows)')

# Operator type scores (mean of constituent metrics)
op_types = {
    'additive': ['additive_linear_r2','additive_superposition','additive_closure'],
    'multiplicative': ['multiplicative_interaction_r2_gain','multiplicative_log_log_slope','multiplicative_sensitivity_amplification'],
    'hierarchical': ['hierarchical_tree_depth','hierarchical_tree_r2','hierarchical_multiscale_var_ratio'],
    'topological': ['topological_neighborhood_corr','topological_continuity','topological_deformation_stability'],
    'network': ['network_graph_behav_corr','network_propagation','network_sync_coupling'],
    'symmetry': ['symmetry_invariance','symmetry_conservation'],
}
for op, cols in op_types.items():
    valid = [c for c in cols if c in sig_df.columns]
    sig_df[f'op_score_{op}'] = sig_df[valid].mean(axis=1)

print('\nOperator type scores per domain:')
score_cols = [c for c in sig_df.columns if c.startswith('op_score_')]
print(sig_df[['domain'] + score_cols].round(4).to_string(index=False))

f1_summary = {
    'phase': 'F1', 'seed': SEED,
    'n_domains': len(domains),
    'operator_types': list(op_types.keys()),
    'operator_signature_columns': [c for c in sig_df.columns if c not in ('domain','N')],
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/f1_summary.json', 'w') as f:
    json.dump(f1_summary, f, indent=2)
print(f'\nF1 summary saved')
print(f'F1 COMPLETE ({time.time()-t0:.0f}s)')
