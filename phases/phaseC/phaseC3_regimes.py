"""
Phase C3 — Cross-Domain Regime Classification.
Clusters domains by their descriptor-outcome geometry to identify
shared organizational regimes.
"""
import numpy as np, pandas as pd, warnings
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering, KMeans
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import silhouette_score
warnings.filterwarnings('ignore')

CSV = '/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv'
df = pd.read_csv(CSV)
domains = sorted(df['domain'].unique())
cols = ['CSR','RBS','ADI','RTP','SRD']
targets = [c for c in df.columns if c.startswith('stability_') or c.startswith('fertility_')]

print('='*70)
print('PHASE C3 — CROSS-DOMAIN REGIME CLASSIFICATION')
print('='*70)

# Build per-domain geometry profiles
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import r2_score
from scipy.stats import pearsonr

profile_features = []
domain_names = []

for domain in domains:
    m = df['domain'] == domain; N = m.sum()
    X = StandardScaler().fit_transform(df.loc[m, cols].values)
    
    # PCA profile
    pca = PCA().fit(X)
    ev = pca.explained_variance_ratio_
    
    # Descriptor means
    desc_means = df.loc[m, cols].mean().values
    
    # Descriptor importance (absolute linear coefs from full model)
    loo = LeaveOneOut()
    desc_imp = np.zeros(5)
    for t in targets:
        y = df.loc[m, t].values
        if np.std(y) < 1e-10: continue
        coefs = []
        for tr, te in loo.split(X):
            X_tr = StandardScaler().fit_transform(df.loc[m, cols].values[tr])
            X_te = StandardScaler().fit(df.loc[m, cols].values[tr]).transform(df.loc[m, cols].values[te])
            lr = LinearRegression().fit(X_tr, y[tr])
            coefs.append(lr.coef_)
        desc_imp += np.abs(np.mean(coefs, axis=0))
    desc_imp = desc_imp / (desc_imp.sum() + 1e-10)
    
    # Predictive R² vector
    r2_vec = []
    for t in targets:
        y = df.loc[m, t].values
        if np.std(y) < 1e-10: r2_vec.append(0); continue
        p = np.empty(N)
        for tr, te in loo.split(X):
            X_tr = StandardScaler().fit_transform(df.loc[m, cols].values[tr])
            X_te = StandardScaler().fit(df.loc[m, cols].values[tr]).transform(df.loc[m, cols].values[te])
            p[te[0]] = LinearRegression().fit(X_tr, y[tr]).predict(X_te)[0]
        r2_vec.append(r2_score(y, p))
    
    # Combined profile: [PC1_var, PC2_var, n_eff_dims, 5 desc_imp, 8 target_r2]
    cv = np.cumsum(ev)
    n95 = int(np.argmax(cv >= 0.95) + 1) if np.any(cv >= 0.95) else 5
    profile = [ev[0], ev[1], n95] + desc_imp.tolist() + r2_vec
    profile_features.append(profile)
    domain_names.append(domain)

P = np.array(profile_features)
P_scaled = StandardScaler().fit_transform(P)

print(f'\nDomain profiles: {P.shape[1]} features per domain')
print(f'Profile includes: PC1_var, PC2_var, n_dims, 5 desc_importances, 8 target_R²')

# 1. Pairwise distance matrix
dists = squareform(pdist(P_scaled, metric='euclidean'))
dist_df = pd.DataFrame(dists, index=domain_names, columns=domain_names)
print(f'\nPAIRWISE DOMAIN DISTANCES:')
print(f'{"":25s}', end='')
for d in domain_names: print(f'{d[:8]:8s}', end='')
print()
for i, d1 in enumerate(domain_names):
    print(f'{d1:25s}', end='')
    for j, d2 in enumerate(domain_names):
        print(f'{dists[i,j]:.2f}    ', end='')
    print()

# Closest and farthest pairs
flat_dists = [(domain_names[i], domain_names[j], dists[i,j])
              for i in range(len(domain_names)) for j in range(i+1, len(domain_names))]
flat_dists.sort(key=lambda x: x[2])
print(f'\nClosest pairs:')
for d1, d2, d in flat_dists[:5]:
    print(f'  {d1:25s} ↔ {d2:25s}: d={d:.3f}')
print(f'\nFarthest pairs:')
for d1, d2, d in flat_dists[-5:]:
    print(f'  {d1:25s} ↔ {d2:25s}: d={d:.3f}')

# 2. Hierarchical clustering
Z = linkage(P_scaled, method='ward')
print(f'\nHIERARCHICAL CLUSTERING (ward linkage):')
print(f'Linkage matrix (last 5 merges):')
for i in range(max(0, len(Z)-5), len(Z)):
    c1, c2, d, n = Z[i]
    print(f'  Merge {i}: clusters ({int(c1)},{int(c2)}) at d={d:.3f}, n={int(n)}')

# Find clusters at different thresholds
for thresh in [1.0, 2.0, 3.0, 4.0, 5.0]:
    labels = AgglomerativeClustering(n_clusters=None, distance_threshold=thresh, linkage='ward').fit_predict(P_scaled)
    n_clust = len(set(labels))
    if n_clust > 1:
        clusters = {i: [] for i in range(n_clust)}
        for d, l in zip(domain_names, labels): clusters[l].append(d)
        print(f'\nClusters at d<{thresh:.1f} (k={n_clust}):')
        for i, members in clusters.items():
            print(f'  Cluster {i}: {", ".join(members)}')
    else:
        print(f'\nClusters at d<{thresh:.1f}: all domains in 1 cluster')
        break

# 3. Optimal k via silhouette
print(f'\nSILHOUETTE ANALYSIS:')
for k in range(2, min(6, len(domains))):
    labels = KMeans(n_clusters=k, random_state=2000, n_init=10).fit_predict(P_scaled)
    sil = silhouette_score(P_scaled, labels)
    print(f'  k={k}: silhouette={sil:.4f}')

# 4. Regime assignment (interpretive, based on geometry profile)
print(f'\nREGIME CLASSIFICATION (by geometry profile):')
# Identify regimes based on descriptor dominance + target profile
for domain in domains:
    m = df['domain'] == domain
    X = StandardScaler().fit_transform(df.loc[m, cols].values)
    pca = PCA().fit(X); ev = pca.explained_variance_ratio_
    
    # Determine regime family
    dc = np.abs(pca.components_[0])
    top_desc_idx = np.argmax(dc)
    top_desc = cols[top_desc_idx]
    top_weight = dc[top_desc_idx]
    
    if top_desc in ('CSR',):
        if ev[0] > 0.5:
            regime = 'SIMPLE-NONLINEARITY (CSR-dominated, low-dim)'
        else:
            regime = 'COMPLEX-NONLINEARITY (CSR-led, balanced)'
    elif top_desc == 'RBS':
        regime = 'BRANCHING-STRUCTURE (RBS-led)'
    elif top_desc == 'ADI':
        regime = 'AUTOCORRELATION-REGIME (ADI-led)'
    elif top_desc == 'RTP':
        regime = 'TRANSITION-ENTROPY (RTP-led)'
    else:
        regime = 'BALANCED-MULTI'
    
    print(f'  {domain:25s}: {regime}  (PC1={ev[0]:.3f}, top={top_desc}:{top_weight:.3f})')

# 5. Universality families
print(f'\nUNIVERSALITY FAMILIES:')
# Based on distance + clustering + shared descriptor dominance
families = {
    'BIFURCATION-FAMILY': ['nonlinear_oscillator', 'population', 'branching'],
    'GRAPH-FAMILY': ['graph_diffusion', 'kuramoto', 'coupled_map_lattice'],
    'ODE-OSCILLATOR-FAMILY': ['lotka_volterra', 'gray_scott'],
    'DISCRETE-SPATIAL': ['cellular_automata', 'coupled_map_lattice'],
    'SIMPLICIAL': ['replicator'],
}
for name, members in families.items():
    shared = set(members) & set(domain_names)
    if len(shared) >= 2:
        print(f'  {name}: {", ".join(sorted(shared))}')
