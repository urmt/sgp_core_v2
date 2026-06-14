"""
Phase N7+N8 — COUPLING TAXONOMY + DYNAMICAL NULLS

N7: What kinds of recursive continuity couplings exist?
N8: Do coupling effects survive destruction of recursive temporal structure?

TRUE dynamical nulls: shuffle temporal ordering within trajectories.
Preserves distributions + geometry. Destroys temporal structure.
"""
import sys, numpy as np, pandas as pd, os, json, warnings, pickle
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseN_dynamical_coupling'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

sim_df = pd.read_csv(f'{BASE}/outputs/phaseN_minimal_couplings.csv')
traj_df = pd.read_csv(f'{BASE}/outputs/phaseN_temporal_trajectories.csv')
print(f'Loaded: {len(sim_df)} simulations, {len(traj_df)} trajectory steps')

# ====================================================
# N7: ORGANIZATIONAL COUPLING TAXONOMY
# ====================================================
print('='*70)
print('PHASE N7 — ORGANIZATIONAL COUPLING TAXONOMY')
print('What kinds of recursive continuity couplings exist?')
print('='*70)

# Build feature matrix for clustering
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

cluster_cols = ['final_synchronization', 'mean_order_parameter', 'phase_sync_time',
                'closure_correlation', 'transition_synchronization',
                'coupling_strength']
avail_cluster = [c for c in cluster_cols if c in sim_df.columns]

X = sim_df[avail_cluster].dropna().values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Find optimal number of clusters (elbow: 3-8)
inertias = []
for k in range(2, 9):
    km = KMeans(n_clusters=k, random_state=SEED, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

# Use k=4 (sweet spot for interpretability)
km = KMeans(n_clusters=4, random_state=SEED, n_init=10)
labels = km.fit_predict(X_scaled)

# Add cluster labels to sim_df (only for rows without NaNs)
valid_idx = sim_df[avail_cluster].dropna().index
sim_df.loc[valid_idx, 'coupling_cluster'] = labels

# Profile each cluster
print(f'\n=== COUPLING TAXONOMY (4 clusters) ===')
for cl in range(4):
    sub = sim_df[sim_df['coupling_cluster'] == cl]
    if len(sub) == 0: continue
    print(f'\n  Cluster {cl} (n={len(sub)}):')
    for col in avail_cluster:
        print(f'    {col:30s}: {sub[col].mean():.4f}')

# Label clusters by their dynamical signature
cluster_labels = {}
for cl in range(4):
    sub = sim_df[sim_df['coupling_cluster'] == cl]
    if len(sub) == 0: continue
    sync = sub['final_synchronization'].mean()
    sync_time = sub['phase_sync_time'].mean()
    closure_corr = sub['closure_correlation'].mean()
    
    if sync > 0.9 and sync_time < 20:
        label = 'synchronizing'
    elif sync > 0.8 and closure_corr > 0.5:
        label = 'stabilizing'
    elif sync > 0.6:
        label = 'weakly coupled'
    else:
        label = 'unsynchronized'
    cluster_labels[cl] = label
    print(f'    -> {label}')

# Distribution of clusters
print(f'\n=== TAXONOMY DISTRIBUTION ===')
for cl in range(4):
    n = (sim_df['coupling_cluster'] == cl).sum()
    label = cluster_labels.get(cl, 'unknown')
    print(f'  {label:20s}: {n} ({100*n/len(sim_df):.1f}%)')

# Save taxonomy
sim_df.to_csv(f'{BASE}/outputs/phaseN_coupling_taxonomy.csv', index=False)
n7_summary = {
    'phase': 'N7',
    'n_clusters': 4,
    'cluster_labels': cluster_labels,
    'cluster_sizes': {int(cl): int((sim_df['coupling_cluster']==cl).sum()) for cl in range(4)},
}
with open(f'{BASE}/summaries/n7_summary.json', 'w') as f:
    json.dump(n7_summary, f, indent=2)
print(f'\nSaved: phaseN_coupling_taxonomy.csv')

# ====================================================
# N8: DYNAMICAL NULL PROGRAM
# ====================================================
print('\n' + '='*70)
print('PHASE N8 — DYNAMICAL NULL PROGRAM')
print('Do coupling effects survive destruction of recursive temporal structure?')
print('='*70)

# The TRUE dynamical null: preserve trajectory values but SHUFFLE temporal ordering
# This destroys temporal dependencies while preserving distributions and local geometry

if len(traj_df) > 0:
    null_records = []
    for sim_idx in sim_df['sim_idx'].unique():
        st = traj_df[traj_df['sim_idx'] == sim_idx].copy()
        if len(st) < 10: continue
        
        # Shuffle temporal ordering of ALL variables independently
        # This destroys phase-cha continuity coupling while preserving distributions
        for col in ['theta_a', 'theta_b', 'c_a', 'c_b', 'phase_diff']:
            st[col] = np.random.permutation(st[col].values)
        
        # Recompute order parameter from shuffled phases
        shuffled_order = np.abs(np.exp(1j*st['theta_a'].values) + np.exp(1j*st['theta_b'].values)) / 2
        
        # Null metrics
        null_final_sync = shuffled_order[-20:].mean()
        null_order_param = shuffled_order.mean()
        null_closure_corr = np.corrcoef(st['c_a'], st['c_b'])[0, 1] if len(st) > 10 else 0
        if np.isnan(null_closure_corr): null_closure_corr = 0
        
        null_records.append({
            'sim_idx': sim_idx,
            'null_final_sync': null_final_sync,
            'null_order_param': null_order_param,
            'null_closure_corr': null_closure_corr,
        })
    
    null_df = pd.DataFrame(null_records)
    
    # Merge with real data
    real_metrics = sim_df[['sim_idx', 'final_synchronization', 'mean_order_parameter', 
                           'closure_correlation', 'coupling_cluster']].copy()
    comparison = real_metrics.merge(null_df, on='sim_idx', how='inner')
    
    print(f'\n=== DYNAMICAL NULL: REAL vs NULL ===')
    metrics_to_compare = [
        ('final_synchronization', 'null_final_sync'),
        ('mean_order_parameter', 'null_order_param'),
        ('closure_correlation', 'null_closure_corr'),
    ]
    
    for real_col, null_col in metrics_to_compare:
        if real_col in comparison.columns and null_col in comparison.columns:
            real_m = comparison[real_col].mean()
            null_m = comparison[null_col].mean()
            collapse = 1.0 - null_m / (real_m + 1e-10)
            print(f'\n  {real_col:30s}:')
            print(f'    Real: {real_m:.4f}')
            print(f'    Null: {null_m:.4f}')
            print(f'    Collapse: {collapse:.4f}')
            print(f'    {"SURVIVES NULL" if collapse < 0.3 else "DESTROYED BY NULL"}')
    
    # Per cluster
    print(f'\n=== EFFECT BY COUPLING TYPE ===')
    for cl in range(4):
        sub = comparison[comparison['coupling_cluster'] == cl]
        if len(sub) < 5: continue
        label = cluster_labels.get(cl, 'unknown')
        real_sync = sub['final_synchronization'].mean()
        null_sync = sub['null_final_sync'].mean()
        collapse = 1.0 - null_sync / (real_sync + 1e-10)
        print(f'  {label:20s} (n={len(sub)}): real={real_sync:.4f} null={null_sync:.4f} collapse={collapse:.4f}')
    
    null_df.to_csv(f'{BASE}/outputs/phaseN_dynamical_nulls.csv', index=False)
    print(f'\nSaved: phaseN_dynamical_nulls.csv')
    
    n8_summary = {
        'phase': 'N8',
        'synchronization_collapse': float(1.0 - comparison['null_final_sync'].mean() / (comparison['final_synchronization'].mean() + 1e-10)),
        'order_param_collapse': float(1.0 - comparison['null_order_param'].mean() / (comparison['mean_order_parameter'].mean() + 1e-10)),
        'closure_corr_collapse': float(1.0 - comparison['null_closure_corr'].mean() / (comparison['closure_correlation'].mean() + 1e-10)),
        'n_trajectories_nulled': len(null_df),
    }
else:
    print('No trajectory data available')
    n8_summary = {'phase': 'N8', 'error': 'no trajectory data'}

with open(f'{BASE}/summaries/n8_summary.json', 'w') as f:
    json.dump(n8_summary, f, indent=2)

print(f'\nN7+N8 COMPLETE')
