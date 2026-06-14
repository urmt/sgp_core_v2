# PHASE 519 — CLUSTER-BRIDGE-TOPOLOGY
# Test whether the 6 bounded clusters are isolated
# islands or connected through sparse bridge systems

import numpy as np
import pandas as pd
import networkx as nx
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import kneighbors_graph
from scipy.stats import pearsonr

SEED = 519
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

systems = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase518/phase518_cluster_stats.csv"
)

full = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv"
)

features = [
    "CSR",
    "ADI",
    "RBS",
    "RTP",
    "SRD"
]

X = full[features].values
X = StandardScaler().fit_transform(X)

stability = full["stability_score"].values

# ============================================
# BUILD KNN GRAPH
# ============================================

k = 4

A = kneighbors_graph(
    X,
    n_neighbors=k,
    mode="distance",
    include_self=False
)

G = nx.from_scipy_sparse_array(A)

# ============================================
# CENTRALITY
# ============================================

bet = nx.betweenness_centrality(G)

deg = nx.degree_centrality(G)

bridge_scores = []

for i in range(len(X)):

    bridge_scores.append({
        "system": full.iloc[i]["name"],
        "stability": stability[i],
        "betweenness": bet[i],
        "degree": deg[i]
    })

bridge_df = pd.DataFrame(bridge_scores)

# ============================================
# BRIDGE ANALYSIS
# ============================================

bet_corr, _ = pearsonr(
    bridge_df["betweenness"],
    bridge_df["stability"]
)

deg_corr, _ = pearsonr(
    bridge_df["degree"],
    bridge_df["stability"]
)

# top bridge systems
top_bridges = bridge_df.sort_values(
    "betweenness",
    ascending=False
).head(6)

# ============================================
# COMPONENT ROBUSTNESS
# ============================================

largest_before = len(
    max(nx.connected_components(G), key=len)
)

# remove top bridge node
top_node = int(
    top_bridges.index[0]
)

G2 = G.copy()

G2.remove_node(top_node)

largest_after = len(
    max(nx.connected_components(G2), key=len)
)

fragmentation_drop = (
    largest_before - largest_after
)

# ============================================
# VERDICT
# ============================================

if (
    fragmentation_drop >= 8 and
    abs(bet_corr) > 0.40
):
    verdict = "BRIDGE-DEPENDENT-TOPOLOGY"

elif (
    fragmentation_drop >= 4
):
    verdict = "PARTIAL-BRIDGE-STRUCTURE"

else:
    verdict = "DISTRIBUTED-CLUSTER-TOPOLOGY"

# ============================================
# SAVE
# ============================================

bridge_df.to_csv(
    "/home/student/sgp_core_v2/phases/phase519/phase519_bridge_scores.csv",
    index=False
)

top_bridges.to_csv(
    "/home/student/sgp_core_v2/phases/phase519/phase519_top_bridges.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 519,
    "largest_component_before": largest_before,
    "largest_component_after": largest_after,
    "fragmentation_drop": fragmentation_drop,
    "betweenness_stability_corr": bet_corr,
    "degree_stability_corr": deg_corr,
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase519/phase519_summary.csv",
    index=False
)

print("\n=== PHASE 519 COMPLETE ===")
print(summary.to_string(index=False))
