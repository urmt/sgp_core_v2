# PHASE 528 — INVARIANT-PAIR-EXTRACTION
# Extract the truly projection-invariant system pairs
# and determine whether they form stable archetypes

import numpy as np
import pandas as pd
from itertools import combinations
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from scipy.stats import pearsonr

SEED = 528
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

base = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv"
)

features = [
    "CSR",
    "ADI",
    "RBS",
    "RTP",
    "SRD"
]

systems = base["name"].values
stability = base["stability_score"].values

# ============================================
# GENERATE ALL CLUSTERINGS
# ============================================

clusterings = []

for r in range(2, 6):

    for combo in combinations(features, r):

        X = base[list(combo)].values
        X = StandardScaler().fit_transform(X)

        km = KMeans(
            n_clusters=6,
            random_state=SEED,
            n_init=25
        )

        labels = km.fit_predict(X)

        clusterings.append(labels)

clusterings = np.array(clusterings)

# ============================================
# CONSENSUS MATRIX
# ============================================

N = len(base)

consensus = np.zeros((N, N))

for labels in clusterings:

    for i in range(N):

        for j in range(N):

            if labels[i] == labels[j]:
                consensus[i, j] += 1

consensus /= len(clusterings)

# ============================================
# INVARIANT PAIRS
# ============================================

pairs = []

for i in range(N):

    for j in range(i+1, N):

        if consensus[i, j] >= 0.80:

            pairs.append({
                "system_a": systems[i],
                "system_b": systems[j],
                "consensus": consensus[i, j],
                "stability_diff": abs(
                    stability[i] - stability[j]
                )
            })

pairs_df = pd.DataFrame(pairs)

# ============================================
# ARCHETYPE GRAPH
# ============================================

node_degree = {}

for s in systems:
    node_degree[s] = 0

for _, row in pairs_df.iterrows():

    node_degree[row["system_a"]] += 1
    node_degree[row["system_b"]] += 1

degree_vals = np.array(
    list(node_degree.values())
)

# ============================================
# CORE ANALYSIS
# ============================================

hub_threshold = np.percentile(
    degree_vals,
    90
)

hub_nodes = [
    k for k, v in node_degree.items()
    if v >= hub_threshold
]

mean_pair_consensus = (
    pairs_df["consensus"].mean()
    if len(pairs_df) > 0 else 0
)

mean_pair_stability_diff = (
    pairs_df["stability_diff"].mean()
    if len(pairs_df) > 0 else 0
)

degree_stability_corr, _ = pearsonr(
    degree_vals,
    stability
)

# ============================================
# VERDICT
# ============================================

if (
    len(hub_nodes) >= 3 and
    mean_pair_consensus > 0.85
):
    verdict = "INVARIANT-ARCHETYPE-CORE"

elif (
    len(pairs_df) > 0
):
    verdict = "SPARSE-INVARIANT-PAIRS"

else:
    verdict = "NO-STABLE-ARCHETYPES"

# ============================================
# SAVE
# ============================================

pairs_df.to_csv(
    "/home/student/sgp_core_v2/phases/phase528/phase528_invariant_pairs.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 528,
    "n_invariant_pairs": len(pairs_df),
    "mean_pair_consensus": mean_pair_consensus,
    "mean_pair_stability_diff": mean_pair_stability_diff,
    "n_hub_nodes": len(hub_nodes),
    "hub_nodes": str(hub_nodes),
    "degree_stability_corr": degree_stability_corr,
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase528/phase528_summary.csv",
    index=False
)

print("\n=== PHASE 528 COMPLETE ===")
print(summary.to_string(index=False))
