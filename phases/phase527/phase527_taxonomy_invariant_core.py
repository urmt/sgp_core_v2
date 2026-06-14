# PHASE 527 — TAXONOMY-INVARIANT-CORE
# Test whether there exists a projection-invariant
# latent categorical core beneath stability-value variation

import numpy as np
import pandas as pd
from itertools import combinations
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from scipy.stats import pearsonr

SEED = 527
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

stability = base["stability_score"].values

# ============================================
# GENERATE ALL CLUSTERINGS
# ============================================

clusterings = []
feature_sets = []

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
        feature_sets.append(combo)

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
# INVARIANT CORE DETECTION
# ============================================

core_pairs = consensus > 0.80

core_strength = np.mean(consensus)

high_consistency_fraction = np.mean(
    consensus > 0.75
)

# ============================================
# CONSENSUS CLUSTERING
# ============================================

km_consensus = KMeans(
    n_clusters=6,
    random_state=SEED,
    n_init=25
)

consensus_labels = km_consensus.fit_predict(consensus)

# ============================================
# AGREEMENT TEST
# ============================================

aris = []

for labels in clusterings:

    ari = adjusted_rand_score(
        consensus_labels,
        labels
    )

    aris.append(ari)

mean_ari = np.mean(aris)
min_ari = np.min(aris)
max_ari = np.max(aris)

# ============================================
# STABILITY CONSISTENCY
# ============================================

cluster_means = []

for c in range(6):

    idx = np.where(consensus_labels == c)[0]

    cluster_means.append(
        np.mean(stability[idx])
    )

cluster_means = np.array(cluster_means)

stability_dispersion = np.std(cluster_means)

# ============================================
# VERDICT
# ============================================

if (
    mean_ari > 0.60 and
    high_consistency_fraction > 0.50
):
    verdict = "INVARIANT-TAXONOMIC-CORE"

elif (
    mean_ari > 0.40
):
    verdict = "PARTIAL-INVARIANT-CORE"

else:
    verdict = "NO-INVARIANT-CORE"

# ============================================
# SAVE
# ============================================

pd.DataFrame(consensus).to_csv(
    "/home/student/sgp_core_v2/phases/phase527/phase527_consensus_matrix.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 527,
    "mean_ARI_to_consensus": mean_ari,
    "min_ARI": min_ari,
    "max_ARI": max_ari,
    "core_strength": core_strength,
    "high_consistency_fraction": high_consistency_fraction,
    "stability_dispersion": stability_dispersion,
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase527/phase527_summary.csv",
    index=False
)

print("\n=== PHASE 527 COMPLETE ===")
print(summary.to_string(index=False))
