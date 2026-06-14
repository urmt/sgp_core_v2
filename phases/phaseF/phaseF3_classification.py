"""
Phase F3 — Family Geometry Classification.
Clusters domains by operator signatures into geometry classes.
No universal assumptions.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseF'
OUT = '/home/student/sgp_core_v2/phases/phaseE'
os.makedirs(f'{BASE}/processed', exist_ok=True)

sig_df = pd.read_csv(f'{BASE}/processed/operator_signatures.csv')
test_df = pd.read_csv(f'{BASE}/raw/composition_tests.csv')

t0 = time.time()
print('='*70)
print('PHASE F3 — FAMILY GEOMETRY CLASSIFICATION')
print('='*70)

# Build feature matrix from operator signatures + test results
op_features = [
    'additive_linear_r2', 'additive_superposition', 'additive_closure',
    'multiplicative_interaction_r2_gain', 'multiplicative_log_log_slope',
    'multiplicative_sensitivity_amplification',
    'hierarchical_tree_depth', 'hierarchical_tree_r2', 'hierarchical_multiscale_var_ratio',
    'topological_neighborhood_corr', 'topological_continuity', 'topological_deformation_stability',
    'network_graph_behav_corr', 'network_propagation', 'network_sync_coupling',
    'symmetry_invariance', 'symmetry_conservation',
]

test_features = [
    'composition_fidelity', 'closure_score', 'associativity_score',
    'scaling_preservation', 'transport_score', 'symmetry_score',
]

# Use only valid (non-NaN, finite) features
all_features = [c for c in op_features + test_features 
                if c in sig_df.columns or c in test_df.columns]

# Merge
merged = sig_df.merge(test_df, on='domain', how='outer')
X_raw = merged[all_features].values

# Handle NaN/Inf
X_clean = np.nan_to_num(X_raw, nan=0.0, posinf=1e6, neginf=-1e6)
X_std = StandardScaler().fit_transform(X_clean)

domains = merged['domain'].values

print(f'Features: {all_features}')
print(f'Domains: {len(domains)}')

# --- Clustering ---
# 1. Hierarchical clustering
Z = linkage(X_std, method='ward')
from scipy.cluster.hierarchy import fcluster

# Determine optimal cluster count via silhouette
best_k, best_s = 2, -1
for k in range(2, min(6, len(domains))):
    labels = fcluster(Z, k, criterion='maxclust')
    s = silhouette_score(X_std, labels)
    print(f'  k={k}: silhouette={s:.4f}')
    if s > best_s:
        best_k, best_s = k, s

labels = fcluster(Z, best_k, criterion='maxclust')
print(f'\nOptimal clusters: k={best_k} (silhouette={best_s:.4f})')

# 2. KMeans with best k
km = KMeans(n_clusters=best_k, random_state=SEED, n_init=10)
km_labels = km.fit_predict(X_std)

# --- Build classification ---
class_records = []
for i, dom in enumerate(domains):
    # Compute dominant operator type from F1 signatures
    scores = {
        'additive': np.mean([
            sig_df[sig_df['domain']==dom]['additive_linear_r2'].values[0],
            sig_df[sig_df['domain']==dom]['additive_superposition'].values[0],
        ]),
        'multiplicative': np.mean([
            sig_df[sig_df['domain']==dom]['multiplicative_interaction_r2_gain'].values[0],
            abs(sig_df[sig_df['domain']==dom]['multiplicative_log_log_slope'].values[0]),
        ]),
        'hierarchical': np.mean([
            sig_df[sig_df['domain']==dom]['hierarchical_tree_r2'].values[0],
            sig_df[sig_df['domain']==dom]['hierarchical_multiscale_var_ratio'].values[0],
        ]),
        'topological': np.mean([
            sig_df[sig_df['domain']==dom]['topological_continuity'].values[0],
            sig_df[sig_df['domain']==dom]['topological_neighborhood_corr'].values[0],
        ]),
        'network': np.mean([
            sig_df[sig_df['domain']==dom]['network_sync_coupling'].values[0],
            sig_df[sig_df['domain']==dom]['network_propagation'].values[0],
        ]),
        'symmetry': np.mean([
            sig_df[sig_df['domain']==dom]['symmetry_invariance'].values[0],
            sig_df[sig_df['domain']==dom]['symmetry_conservation'].values[0],
        ]),
    }
    dominant = max(scores, key=scores.get)
    dominant_score = scores[dominant]
    
    class_records.append({
        'domain': dom,
        'hierarchical_cluster': int(labels[i]),
        'kmeans_cluster': int(km_labels[i]),
        'dominant_operator': dominant,
        'dominant_score': round(dominant_score, 4),
        **{f'score_{k}': round(v, 4) for k, v in sorted(scores.items())},
    })

class_df = pd.DataFrame(class_records)
class_path = f'{BASE}/processed/family_geometry_classes.csv'
class_df.to_csv(class_path, index=False)
print(f'\nF3 saved: {class_path} ({len(class_df)} rows)')

# Print classification
print('\n--- Family Geometry Classification ---')
for _, r in class_df.iterrows():
    top3 = sorted([(k, v) for k, v in r.items() if k.startswith('score_')],
                  key=lambda x: -x[1])[:3]
    top3_str = ', '.join(f'{k[6:]}:{v:.3f}' for k, v in top3)
    print(f'  Cluster {r["hierarchical_cluster"]} | {r["domain"]:25s} | {r["dominant_operator"]:15s} ({r["dominant_score"]:.3f}) | [{top3_str}]')

# Cross-tab
print('\n--- Cluster composition ---')
for cl in sorted(class_df['hierarchical_cluster'].unique()):
    members = class_df[class_df['hierarchical_cluster']==cl]['domain'].values
    print(f'  Cluster {cl}: {list(members)}')

# Save distance matrix
dist_matrix = squareform(pdist(X_std, metric='euclidean'))
dist_df = pd.DataFrame(dist_matrix, index=domains, columns=domains)
dist_df.to_csv(f'{BASE}/processed/geometry_distance_matrix.csv')
print(f'\nDistance matrix saved')

f3_summary = {
    'phase': 'F3', 'seed': SEED,
    'n_domains': len(domains),
    'n_features': len(all_features),
    'features': all_features,
    'optimal_clusters': int(best_k),
    'silhouette_score': round(best_s, 4),
    'cluster_assignments': {
        int(cl): [str(d) for d in class_df[class_df['hierarchical_cluster']==cl]['domain'].values]
        for cl in sorted(class_df['hierarchical_cluster'].unique())
    },
    'dominant_operators': class_df[['domain','dominant_operator','dominant_score']].to_dict('records'),
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/f3_summary.json', 'w') as f:
    json.dump(f3_summary, f, indent=2)
print(f'F3 summary saved')
print(f'F3 COMPLETE ({time.time()-t0:.0f}s)')
