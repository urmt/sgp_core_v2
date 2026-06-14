# PHASE 516 — STABILITY-PERCOLATION-THRESHOLD
# Goal:
# Determine whether recursive stability propagates
# through clustered neighborhood percolation
# rather than continuous geometry

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import kneighbors_graph
from scipy.stats import pearsonr
import networkx as nx

SEED = 516
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase515/phase515_homogeneity_results.csv"
)

features = [
    "CSR",
    "ADI",
    "RBS",
    "RTP",
    "SRD"
]

X = df[features].values
X = StandardScaler().fit_transform(X)

if "stability_score" in df.columns:
    stability = df["stability_score"].values
else:
    stability = (
        X[:,0] +
        X[:,2] +
        X[:,3] -
        X[:,4]
    )

# ============================================
# KNN GRAPH
# ============================================

k = 5

A = kneighbors_graph(
    X,
    n_neighbors=k,
    mode="connectivity",
    include_self=False
)

G = nx.from_scipy_sparse_array(A)

# ============================================
# LOCAL PERCOLATION
# ============================================

neighbor_stability = []
cluster_coeffs = []
component_sizes = []
local_variance = []

for i in range(len(X)):

    neigh = list(G.neighbors(i))

    if len(neigh) == 0:
        neighbor_stability.append(0)
        cluster_coeffs.append(0)
        component_sizes.append(1)
        local_variance.append(0)
        continue

    neigh_stab = stability[neigh]

    neighbor_stability.append(
        np.mean(neigh_stab)
    )

    local_variance.append(
        np.var(neigh_stab)
    )

    cluster_coeffs.append(
        nx.clustering(G, i)
    )

    comp = nx.node_connected_component(G, i)

    component_sizes.append(
        len(comp)
    )

df["neighbor_stability"] = neighbor_stability
df["cluster_coeff"] = cluster_coeffs
df["component_size"] = component_sizes
df["local_variance"] = local_variance

# ============================================
# CORRELATIONS
# ============================================

corr_neighbor,_ = pearsonr(
    neighbor_stability,
    stability
)

corr_cluster,_ = pearsonr(
    cluster_coeffs,
    stability
)

corr_component,_ = pearsonr(
    component_sizes,
    stability
)

corr_variance,_ = pearsonr(
    local_variance,
    stability
)

# ============================================
# PERCOLATION THRESHOLD TEST
# ============================================

thresholds = np.linspace(
    np.min(stability),
    np.max(stability),
    20
)

largest_components = []

for t in thresholds:

    nodes = [
        i for i,s in enumerate(stability)
        if s >= t
    ]

    sub = G.subgraph(nodes)

    if len(sub.nodes) == 0:
        largest_components.append(0)
        continue

    largest = max(
        [
            len(c)
            for c in nx.connected_components(sub)
        ]
    )

    largest_components.append(largest)

largest_components = np.array(
    largest_components
)

# detect sharp collapse
diffs = np.diff(
    largest_components
)

max_drop = np.min(diffs)

# ============================================
# VERDICT
# ============================================

if corr_neighbor > 0.80 and max_drop < -5:
    verdict = "PERCOLATION-THRESHOLD-STRUCTURE"
elif corr_neighbor > 0.60:
    verdict = "PARTIAL-PERCOLATION-STRUCTURE"
else:
    verdict = "NONPERCOLATING-SPACE"

# ============================================
# SAVE
# ============================================

summary = {
    "phase": 516,
    "neighbor_corr":
        float(corr_neighbor),
    "cluster_corr":
        float(corr_cluster),
    "component_corr":
        float(corr_component),
    "variance_corr":
        float(corr_variance),
    "max_component_drop":
        float(max_drop),
    "largest_component_initial":
        int(largest_components[0]),
    "largest_component_final":
        int(largest_components[-1]),
    "verdict":
        verdict
}

summary_df = pd.DataFrame([summary])

summary_df.to_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_summary.csv",
    index=False
)

df.to_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv",
    index=False
)

print("\n=== PHASE 516 COMPLETE ===")
print(summary_df.to_string(index=False))
