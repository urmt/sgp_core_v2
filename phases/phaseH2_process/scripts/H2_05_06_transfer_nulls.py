"""
H2_05 + H2_06 — Cross-Family Process Transfer + Null Process Controls.

H2_05: Do process-level organizational geometries generalize across families?
NOT descriptor transfer. NOT state transfer.
PROCESS GEOMETRY transfer.

H2_06: Do process-level results survive when organizational order is destroyed?
"""
import numpy as np, pandas as pd, os, json, warnings
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from scipy.stats import ks_2samp
from sklearn.utils import shuffle
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseH2_process'
PC = '/home/student/sgp_core_v2/phases/phaseC'
PE = '/home/student/sgp_core_v2/phases/phaseE'
PG = '/home/student/sgp_core_v2/phases/phaseG'
PF = '/home/student/sgp_core_v2/phases/phaseF'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

df = pd.read_csv(f'{PC}/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
curv = pd.read_csv(f'{PE}/processed/curvature_metrics.csv')
poss = pd.read_csv(f'{PE}/processed/possibility_metrics.csv')
phaseG = pd.read_csv(f'{PG}/processed/coherence_fertility_phase_space.csv')
geom = pd.read_csv(f'{PF}/processed/family_geometry_classes.csv')
merged = df.merge(phaseG, on=['sys_idx','domain']).merge(curv, on=['sys_idx','domain']).merge(poss, on=['sys_idx','domain'])
merged['process_regime'] = merged['region'].map({'constrained_generative':'CG','rigid_coherence':'RG',
                                                   'chaotic_fertility':'CH','collapse':'CL'})
cluster_map = dict(zip(geom['domain'], geom['hierarchical_cluster']))
merged['geometry_cluster'] = merged['domain'].map(cluster_map)
domains = sorted(merged['domain'].unique())

STAB_COLS = ['stability_return_time','stability_recovery_rate','stability_final_dev','stability_max_dev']
FERT_COLS = ['fertility_state_diversity','fertility_novelty_rate','fertility_state_coverage','fertility_transition_entropy']
CURV_COLS = ['tangent_rotation','local_curvature','predictive_shear','geodesic_instab','jacobian_vol','desc_switch_vel']
POSS_COLS = ['poss_reachable_volume','poss_branching_diversity','poss_adaptive_recovery',
             'poss_future_entropy','poss_divergence_capacity','poss_stability_fertility_coupling']

print('='*70)
print('H2_05 — CROSS-FAMILY PROCESS TRANSFER')
print('Question: Do PROCESS geometries generalize across organizational families?')
print('='*70)

# ─── Extract domain-level process geometry profiles ───
# A domain's process geometry is its distribution of transition_continuity,
# transition_smoothness, transition_reversibility, and curvature patterns.
# Two domains share process geometry if their joint distributions are similar.

geo_profiles = []
for domain in domains:
    dm = merged[merged['domain'] == domain]
    X_org = StandardScaler().fit_transform(dm[STAB_COLS + FERT_COLS].values)
    y_regime = dm['process_regime'].values
    domain_k = min(30, len(dm) - 1)
    
    nbrs = NearestNeighbors(n_neighbors=domain_k + 1).fit(X_org)
    _, indices = nbrs.kneighbors(X_org)
    
    continuity_vals = []
    reversibility_vals = []
    curvature_vals = []
    smoothness_vals = []
    
    for i in range(len(dm)):
        neigh_idx = indices[i, 1:]
        neigh_regimes = y_regime[neigh_idx]
        unique_regs = np.unique(neigh_regimes)
        n_unique = len(unique_regs)
        continuity = 1 - (n_unique - 1) / min(4, len(neigh_idx))
        continuity_vals.append(continuity)
        reversibility_vals.append(dm.iloc[i]['poss_stability_fertility_coupling'])
        curvature_vals.append(dm.iloc[i]['local_curvature'])
        
        neigh_fert = dm.iloc[neigh_idx]['fertility'].values
        neigh_coh = dm.iloc[neigh_idx]['coherence'].values
        smoothness = 1 / (1 + np.sqrt(np.var(neigh_fert) * np.var(neigh_coh)))
        smoothness_vals.append(smoothness)
    
    geo_profiles.append({
        'domain': domain,
        'cluster': int(cluster_map.get(domain, -1)),
        'mean_continuity': np.mean(continuity_vals),
        'mean_reversibility': np.mean(reversibility_vals),
        'mean_curvature': np.mean(curvature_vals),
        'mean_smoothness': np.mean(smoothness_vals),
        'std_continuity': np.std(continuity_vals),
        'std_reversibility': np.std(reversibility_vals),
        'std_curvature': np.std(curvature_vals),
        'std_smoothness': np.std(smoothness_vals),
    })

gprof_df = pd.DataFrame(geo_profiles)

# Compute cross-family process similarity: KS distance between process geometry
# distributions for each domain pair
print('Within-cluster vs cross-cluster process geometry similarity:')
transfer_results = []

for i, d1 in enumerate(domains):
    dm1 = merged[merged['domain'] == d1]
    X1 = StandardScaler().fit_transform(dm1[STAB_COLS + FERT_COLS + CURV_COLS].values)
    c1 = cluster_map.get(d1, -1)
    
    for d2 in domains[i+1:]:
        dm2 = merged[merged['domain'] == d2]
        X2 = StandardScaler().fit_transform(dm2[STAB_COLS + FERT_COLS + CURV_COLS].values)
        c2 = cluster_map.get(d2, -1)
        
        same_cluster = (c1 == c2)
        
        # KS distance between organizational state distributions
        # Sample to make comparable
        n_sample = min(len(X1), len(X2), 500)
        idx1 = np.random.choice(len(X1), n_sample, replace=False)
        idx2 = np.random.choice(len(X2), n_sample, replace=False)
        
        # Compare across multiple dimensions
        ks_dists = []
        for dim in range(X1.shape[1]):
            ks_stat, _ = ks_2samp(X1[idx1, dim], X2[idx2, dim])
            ks_dists.append(ks_stat)
        mean_ks = np.mean(ks_dists)
        
        transfer_results.append({
            'domain_1': d1,
            'domain_2': d2,
            'cluster_1': int(c1),
            'cluster_2': int(c2),
            'same_cluster': int(same_cluster),
            'process_geometry_ks_distance': round(mean_ks, 4),
        })

transfer_df = pd.DataFrame(transfer_results)
transfer_df.to_csv(f'{BASE}/outputs/transfer_results.csv', index=False)
print(f'Transfer results saved: {len(transfer_df)} domain pairs')

# Analysis: is process geometry MORE similar within clusters than across?
within = transfer_df[transfer_df['same_cluster'] == 1]['process_geometry_ks_distance']
across = transfer_df[transfer_df['same_cluster'] == 0]['process_geometry_ks_distance']
print(f'\nWithin-cluster process similarity: KS={within.mean():.4f} (n={len(within)} pairs)')
print(f'Across-cluster process similarity: KS={across.mean():.4f} (n={len(across)} pairs)')
print(f'Transfer ratio: {across.mean() / max(within.mean(), 1e-10):.3f} (lower = better transfer)')

# If within-cluster KS is LOWER than across-cluster, process geometry transfers
if within.mean() < across.mean():
    print('=> Process geometry PARTIALLY transfers within clusters (geometry clusters capture some process similarity)')
else:
    print('=> Process geometry DOES NOT transfer within clusters (geometry clusters reflect non-process properties)')

# Most similar domain pairs (lowest KS)
print('\nMost process-similar domain pairs (ranked):')
for _, r in transfer_df.nsmallest(5, 'process_geometry_ks_distance').iterrows():
    print(f'  {r["domain_1"]:25s} ↔ {r["domain_2"]:25s}: KS={r["process_geometry_ks_distance"]:.4f} '
          f'{"SAME CLUSTER" if r["same_cluster"] else "diff cluster"}')

print('\nMost process-dissimilar domain pairs:')
for _, r in transfer_df.nlargest(5, 'process_geometry_ks_distance').iterrows():
    print(f'  {r["domain_1"]:25s} ↔ {r["domain_2"]:25s}: KS={r["process_geometry_ks_distance"]:.4f} '
          f'{"SAME CLUSTER" if r["same_cluster"] else "diff cluster"}')

# ─────────────────────────────────────────────
# H2_06 — NULL PROCESS CONTROLS
# ─────────────────────────────────────────────
print('\n' + '='*70)
print('H2_06 — NULL PROCESS CONTROLS')
print('Do process geometry results vanish under randomized organizational order?')
print('='*70)

N_NULL = 100
null_results = []

# Null 1: Shuffle process regime labels randomly
# (does process geometry change when organizational identity is random?)
print(f'\nRunning {N_NULL} null iterations...')

for null_idx in range(N_NULL):
    if null_idx % 25 == 0: print(f'  Null {null_idx}/{N_NULL}')
    
    null_data = merged.copy()
    
    # N1: Shuffle regime labels
    n1 = null_data.copy()
    n1['process_regime'] = shuffle(n1['process_regime'].values)
    
    # Recompute CG persistence under shuffled labels
    cg_idx = np.where(n1['process_regime'].values == 'CG')[0]
    n1_cg_persistence = []
    for domain in domains:
        dm = n1[n1['domain'] == domain].reset_index(drop=True)
        if len(dm) < 10: continue
        X_org = StandardScaler().fit_transform(dm[STAB_COLS + FERT_COLS].values)
        y_regime = dm['process_regime'].values
        cg_in = np.where(y_regime == 'CG')[0]
        domain_k = min(20, len(dm) - 1)
        if len(cg_in) == 0: continue
        nbrs = NearestNeighbors(n_neighbors=domain_k + 1).fit(X_org)
        _, indices = nbrs.kneighbors(X_org)
        
        for ci in cg_in[:10]:  # sample 10 CG systems for speed
            persistence = 0
            current = ci
            for _ in range(100):
                if y_regime[current] != 'CG': break
                persistence += 1
                neighbors = indices[current, 1:]
                current = int(np.random.choice(neighbors))
            n1_cg_persistence.append(persistence)
    
    # N2: Shuffle organizational state space
    n2 = null_data.copy()
    for col in STAB_COLS + FERT_COLS:
        n2[col] = shuffle(n2[col].values)
    
    # Recompute boundary density under shuffled org space
    n2_boundary = []
    for domain in domains:
        dm = n2[n2['domain'] == domain].reset_index(drop=True)
        if len(dm) < 10: continue
        X_org = StandardScaler().fit_transform(dm[STAB_COLS + FERT_COLS].values)
        y_regime = dm['process_regime'].values
        domain_k = min(30, len(dm) - 1)
        nbrs = NearestNeighbors(n_neighbors=domain_k + 1).fit(X_org)
        _, indices = nbrs.kneighbors(X_org)
        n_boundary = 0
        for i in range(len(dm)):
            neigh_regimes = y_regime[indices[i, 1:]]
            if np.mean(neigh_regimes != y_regime[i]) > 0.3:
                n_boundary += 1
        n2_boundary.append(n_boundary / len(dm))
    
    # N3: Synthetic manifolds — shuffle both regimes AND organizational space
    n3 = null_data.copy()
    n3['process_regime'] = shuffle(n3['process_regime'].values)
    for col in STAB_COLS + FERT_COLS:
        n3[col] = shuffle(n3[col].values)
    
    null_results.append({
        'null_iteration': int(null_idx),
        'n1_mean_persistence': float(np.mean(n1_cg_persistence)) if n1_cg_persistence else 0,
        'n2_mean_boundary_density': float(np.mean(n2_boundary)) if n2_boundary else 0,
    })

null_df = pd.DataFrame(null_results)
null_df.to_csv(f'{BASE}/outputs/null_results.csv', index=False)
print(f'\nNull results saved: {len(null_df)} iterations')

# Compare true vs null values
# True persistence (from H2_03)
persist_df = pd.read_csv(f'{BASE}/outputs/persistence_metrics.csv')
true_persistence = persist_df['persistence_half_life'].mean()

# True boundary density
bdf = pd.read_csv(f'{BASE}/outputs/transition_boundary_metrics.csv')
true_boundary = (bdf['is_near_transition'] == 1).mean()

null_n1_mean = null_df['n1_mean_persistence'].mean()
null_n1_std = null_df['n1_mean_persistence'].std()
null_n2_mean = null_df['n2_mean_boundary_density'].mean()
null_n2_std = null_df['n2_mean_boundary_density'].std()

print('\nNull verification:')
print(f'  True CG half-life: {true_persistence:.2f}')
print(f'  N1 (shuffled regimes): {null_n1_mean:.2f} ± {null_n1_std:.2f}')
z_1 = (true_persistence - null_n1_mean) / max(null_n1_std, 1e-10)
print(f'  Z-score: {z_1:.2f} {"SURVIVED" if abs(z_1) > 2 else "FAILED"}')

print(f'\n  True boundary density: {true_boundary:.3f}')
print(f'  N2 (shuffled org space): {null_n2_mean:.3f} ± {null_n2_std:.3f}')
z_2 = (true_boundary - null_n2_mean) / max(null_n2_std, 1e-10)
print(f'  Z-score: {z_2:.2f} {"SURVIVED" if abs(z_2) > 2 else "FAILED"}')

n1_survive = bool(abs(z_1) > 2)
n2_survive = bool(abs(z_2) > 2)

h2_05_06_summary = {
    'phase': 'H2_05+H2_06', 'seed': SEED,
    'n_domain_pairs': len(transfer_df),
    'within_cluster_KS': float(within.mean()),
    'across_cluster_KS': float(across.mean()),
    'process_transfer_possible': bool(np.abs(within.mean()) < 0.5 and within.mean() < across.mean()),
    'most_process_similar_pair': [str(r['domain_1']) + '-' + str(r['domain_2']) for _, r in transfer_df.nsmallest(3, 'process_geometry_ks_distance').iterrows()],
    'most_process_dissimilar_pair': [str(r['domain_1']) + '-' + str(r['domain_2']) for _, r in transfer_df.nlargest(3, 'process_geometry_ks_distance').iterrows()],
    'null_N1_survived': n1_survive,
    'null_N2_survived': n2_survive,
    'null_N1_zscore': round(z_1, 3),
    'null_N2_zscore': round(z_2, 3),
    'true_half_life': float(true_persistence),
    'null_shuffled_regime_half_life': float(null_n1_mean),
    'true_boundary_density': float(true_boundary),
    'null_shuffled_org_space_boundary': float(null_n2_mean),
    'n_null_iterations': N_NULL,
}
with open(f'{BASE}/summaries/h2_05_06_summary.json', 'w') as f:
    json.dump(h2_05_06_summary, f, indent=2)
print(f'\nH2_05+H2_06 COMPLETE')
