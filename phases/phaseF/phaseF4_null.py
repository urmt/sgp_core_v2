"""
Phase F4 — Null Program.
Repeats operator signature analysis on random controls.
Rejects any operator class reproducible by nulls.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import r2_score
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseF'
NULL_DIR = f'{BASE}/nulls'
os.makedirs(NULL_DIR, exist_ok=True)

df = pd.read_csv('/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
domains = sorted(df['domain'].unique())

COLS_DESC = ['CSR','RBS','ADI','RTP','SRD']
COLS_BEHAV = [c for c in df.columns if c.startswith('fertility_') or c.startswith('stability_')]
t0 = time.time()

print('='*70)
print('PHASE F4 — NULL OPERATOR PROGRAM')
print('='*70)

def compute_signatures(X, Y, domain_label='null'):
    """Compute core operator signatures from any (descriptor, behavior) pair."""
    N = len(X)
    if N < 10: return None
    X_n = StandardScaler().fit_transform(X)
    Y1 = Y[:, 0]
    
    # Additive: linear R²
    lr = LinearRegression().fit(X_n, Y1)
    add_r2 = r2_score(Y1, lr.predict(X_n))
    
    # Multiplicative: interaction improvement + log-log slope
    X_int = np.column_stack([X_n] + [X_n[:, i]*X_n[:, j] for i in range(5) for j in range(i+1,5)])
    lr_i = LinearRegression().fit(X_int, Y1)
    mult_gain = r2_score(Y1, lr_i.predict(X_int)) - add_r2
    
    log_slopes = []
    for d in range(5):
        xd = np.abs(X[:, d]) + 1e-10
        yb = np.abs(Y1) + 1e-10
        if np.std(np.log(xd)) > 1e-6 and np.std(np.log(yb)) > 1e-6:
            s, _ = np.polyfit(np.log(xd), np.log(yb), 1)
            log_slopes.append(s)
    log_slope = np.mean(log_slopes) if log_slopes else 0
    
    # Hierarchical: tree R²
    tree = DecisionTreeRegressor(max_depth=None, min_samples_leaf=5, random_state=SEED)
    tree.fit(X_n, Y1)
    tree_r2 = r2_score(Y1, tree.predict(X_n))
    
    # Topological: neighborhood continuity
    nbrs = NearestNeighbors(n_neighbors=min(21, N)).fit(X_n)
    _, idx = nbrs.kneighbors(X_n)
    cont_pred = np.zeros(N)
    for i in range(N):
        cont_pred[i] = Y1[idx[i, 1:]].mean()
    continuity = r2_score(Y1, cont_pred)
    
    # Network: sync coupling
    neigh_corrs = []
    for i in range(min(200, N)):
        for j in idx[i, 1:6]:
            if np.std(Y1) > 1e-10:
                neigh_corrs.append(pearsonr([Y1[i]]*len(Y1), Y1)[0])
    sync = np.mean(neigh_corrs) if neigh_corrs else 0
    
    # Symmetry invariants
    sym_scores = []
    for _ in range(100):
        d = np.random.normal(0, 1, size=5)
        d /= np.linalg.norm(d) + 1e-10
        proj = X_n @ d
        if np.std(proj) < 1e-10: continue
        r2_dir = r2_score(Y1, LinearRegression().fit(proj.reshape(-1,1), Y1).predict(proj.reshape(-1,1)))
        sym_scores.append(r2_dir)
    sym_inv = 1 - np.mean(sym_scores) if sym_scores else 0.5
    
    return {
        'domain': domain_label, 'add_r2': add_r2, 'mult_gain': mult_gain,
        'log_slope': log_slope, 'tree_r2': tree_r2, 'continuity': continuity,
        'sync': sync, 'sym_inv': sym_inv,
    }

# --- NULL A: Random uniform manifolds ---
print('\n--- NULL A: Random Uniform Manifolds ---')
null_a_records = []
n_iter = 5
for d in domains:
    N = len(df[df['domain']==d])
    Y_real = df[df['domain']==d][COLS_BEHAV].values
    for ri in range(n_iter):
        X_rand = np.random.uniform(-2, 2, size=(N, 5))
        Y_shuf = Y_real[np.random.permutation(N)]
        sig = compute_signatures(X_rand, Y_shuf, f'{d}_nullA_{ri}')
        if sig:
            null_a_records.append(sig)
    print(f'  {d}: {n_iter} iterations')

pd.DataFrame(null_a_records).to_csv(f'{NULL_DIR}/nullA_uniform_manifolds.csv', index=False)

# --- NULL B: Covariance-preserving synthetic ---
print('\n--- NULL B: Covariance-Preserving Synthetic ---')
null_b_records = []
for d in domains:
    N = len(df[df['domain']==d])
    X_real = df[df['domain']==d][COLS_DESC].values
    Y_real = df[df['domain']==d][COLS_BEHAV].values
    X_mu, X_cov = np.mean(X_real, axis=0), np.cov(X_real, rowvar=False)
    for ri in range(5):
        X_syn = np.random.multivariate_normal(X_mu, X_cov, size=N)
        Y_sh = Y_real[np.random.permutation(N)]
        sig = compute_signatures(X_syn, Y_sh, f'{d}_nullB_{ri}')
        if sig:
            null_b_records.append(sig)
    print(f'  {d}: 5 iterations')

pd.DataFrame(null_b_records).to_csv(f'{NULL_DIR}/nullB_covariance_synthetic.csv', index=False)

# --- NULL C: Shuffled descriptor→behavior mapping ---
print('\n--- NULL C: Shuffled Mapping (permute Y) ---')
null_c_records = []
for d in domains:
    dm = df[df['domain']==d]
    X = StandardScaler().fit_transform(dm[COLS_DESC].values)
    Y = dm[COLS_BEHAV].values
    for ri in range(5):
        Y_sh = Y[np.random.permutation(len(Y))]
        sig = compute_signatures(X, Y_sh, f'{d}_nullC_{ri}')
        if sig:
            null_c_records.append(sig)
    print(f'  {d}: 5 iterations')

pd.DataFrame(null_c_records).to_csv(f'{NULL_DIR}/nullC_shuffled_mapping.csv', index=False)

# --- NULL D: Within-domain permutation (gold standard) ---
print('\n--- NULL D: Gold Standard (permute both X and Y) ---')
null_d_records = []
for d in domains:
    dm = df[df['domain']==d]
    X = dm[COLS_DESC].values
    Y = dm[COLS_BEHAV].values
    for ri in range(5):
        X_sh = X[np.random.permutation(len(X))]
        Y_sh = Y[np.random.permutation(len(Y))]
        sig = compute_signatures(X_sh, Y_sh, f'{d}_nullD_{ri}')
        if sig:
            null_d_records.append(sig)
    print(f'  {d}: 5 iterations')

pd.DataFrame(null_d_records).to_csv(f'{NULL_DIR}/nullD_gold_standard.csv', index=False)

# === COMPARISON ===
print('\n' + '='*70)
print('NULL COMPARISON')
print('='*70)

# Load true signatures
true_sig = pd.read_csv(f'{BASE}/processed/operator_signatures.csv')

# Map null datasets
null_sets = {
    'Uniform Manifolds': pd.read_csv(f'{NULL_DIR}/nullA_uniform_manifolds.csv'),
    'Covariance Synthetic': pd.read_csv(f'{NULL_DIR}/nullB_covariance_synthetic.csv'),
    'Shuffled Mapping': pd.read_csv(f'{NULL_DIR}/nullC_shuffled_mapping.csv'),
    'Gold Standard': pd.read_csv(f'{NULL_DIR}/nullD_gold_standard.csv'),
}

# Map between null column names and true signature columns
null_to_true = {
    'add_r2': 'additive_linear_r2',
    'mult_gain': 'multiplicative_interaction_r2_gain',
    'log_slope': 'multiplicative_log_log_slope',
    'tree_r2': 'hierarchical_tree_r2',
    'continuity': 'topological_continuity',
    'sync': 'network_sync_coupling',
    'sym_inv': 'symmetry_invariance',
}
metric_names = {
    'add_r2': 'Additive Linear R²',
    'mult_gain': 'Multiplicative Gain',
    'log_slope': 'Log-Log Slope',
    'tree_r2': 'Hierarchical Tree R²',
    'continuity': 'Topological Continuity',
    'sync': 'Network Sync',
    'sym_inv': 'Symmetry Invariance',
}

for m, mname in metric_names.items():
    true_col = null_to_true[m]
    true_mean = true_sig[true_col].mean() if true_col in true_sig.columns else 0
    print(f'\n{mname}:')
    print(f'  True:      {true_mean:.4f}')
    for null_name, null_df in null_sets.items():
        null_mean = null_df[m].mean() if m in null_df.columns else 0
        null_std = null_df[m].std() if m in null_df.columns else 0
        survived = abs(true_mean) > abs(null_mean) + 2 * null_std
        print(f'  {null_name:25s}: {null_mean:.4f} ± {null_std:.4f}  {"✓" if survived else "✗"}')

# Save all null distributions
np.savez(f'{NULL_DIR}/null_all_operator_distributions.npz',
    true_add_r2=true_sig['additive_linear_r2'].values,
    true_mult_gain=true_sig['multiplicative_interaction_r2_gain'].values if 'multiplicative_interaction_r2_gain' in true_sig.columns else [],
    true_log_slope=true_sig['multiplicative_log_log_slope'].values if 'multiplicative_log_log_slope' in true_sig.columns else [],
    true_tree_r2=true_sig['hierarchical_tree_r2'].values if 'hierarchical_tree_r2' in true_sig.columns else [],
    true_continuity=true_sig['topological_continuity'].values,
    true_sync=true_sig['network_sync_coupling'].values if 'network_sync_coupling' in true_sig.columns else [],
    true_sym_inv=true_sig['symmetry_invariance'].values if 'symmetry_invariance' in true_sig.columns else [],
)

print(f'\nF4 COMPLETE ({time.time()-t0:.0f}s)')
