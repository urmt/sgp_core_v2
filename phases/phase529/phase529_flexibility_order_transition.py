# PHASE 529 — FLEXIBILITY-ORDER TRANSITION
# Test whether taxonomic flexibility itself is the
# governing coordinate of recursive stability

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from itertools import combinations

SEED = 529
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
# ALL PROJECTION CLUSTERINGS
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
# FLEXIBILITY SCORE
# ============================================

N = len(base)

flexibility = np.zeros(N)

for i in range(N):

    assignments = clusterings[:, i]

    counts = pd.Series(assignments).value_counts()

    dominant_fraction = counts.max() / counts.sum()

    flexibility[i] = 1.0 - dominant_fraction

# ============================================
# LOCAL CONSENSUS SCORE
# ============================================

consensus_strength = np.zeros(N)

for i in range(N):

    pair_scores = []

    for j in range(N):

        if i == j:
            continue

        same = np.mean(
            clusterings[:, i] == clusterings[:, j]
        )

        pair_scores.append(same)

    consensus_strength[i] = np.mean(pair_scores)

# ============================================
# CORRELATIONS
# ============================================

flex_corr, flex_p = pearsonr(
    flexibility,
    stability
)

cons_corr, cons_p = pearsonr(
    consensus_strength,
    stability
)

rank_corr, _ = spearmanr(
    flexibility,
    stability
)

# ============================================
# GROUP COMPARISON
# ============================================

q1 = np.quantile(flexibility, 0.33)
q2 = np.quantile(flexibility, 0.66)

low_group = stability[flexibility <= q1]
mid_group = stability[
    (flexibility > q1) &
    (flexibility <= q2)
]
high_group = stability[flexibility > q2]

# ============================================
# VERDICT
# ============================================

if (
    flex_corr > 0.70 and
    cons_corr < -0.50
):
    verdict = "FLEXIBILITY-ORDER-LAW"

elif (
    flex_corr > 0.40
):
    verdict = "PARTIAL-FLEXIBILITY-STRUCTURE"

else:
    verdict = "NONFLEXIBLE-TAXONOMY"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": systems,
    "stability": stability,
    "flexibility": flexibility,
    "consensus_strength": consensus_strength
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase529/phase529_flexibility_scores.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 529,
    "flexibility_stability_corr": flex_corr,
    "flexibility_stability_p": flex_p,
    "consensus_stability_corr": cons_corr,
    "consensus_stability_p": cons_p,
    "rank_corr": rank_corr,
    "low_group_mean": low_group.mean(),
    "mid_group_mean": mid_group.mean(),
    "high_group_mean": high_group.mean(),
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase529/phase529_summary.csv",
    index=False
)

print("\n=== PHASE 529 COMPLETE ===")
print(summary.to_string(index=False))
