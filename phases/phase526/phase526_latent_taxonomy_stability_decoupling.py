# PHASE 526 — LATENT-TAXONOMY-STABILITY-DECOUPLING
# Test whether cluster identity and stability magnitude
# are fundamentally decoupled organizational layers

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from scipy.stats import pearsonr, spearmanr

SEED = 526
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

base = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv"
)

p523 = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase523/phase523_cluster_identity.csv"
)

features_full = [
    "CSR",
    "ADI",
    "RBS",
    "RTP",
    "SRD"
]

features_partial = [
    "CSR",
    "ADI",
    "RBS"
]

stability = base["stability_score"].values

# ============================================
# CLUSTERINGS
# ============================================

# Phase 523 labels
labels_523 = p523["cluster"].values

# Rebuild Phase 524 clustering
X_partial = base[features_partial].values
X_partial = StandardScaler().fit_transform(X_partial)

km_partial = KMeans(
    n_clusters=6,
    random_state=SEED,
    n_init=25
)

labels_partial = km_partial.fit_predict(X_partial)

# ============================================
# WITHIN-CLUSTER STABILITY
# ============================================

cluster_means_523 = []
cluster_means_partial = []

for c in range(6):

    idx523 = np.where(labels_523 == c)[0]
    idxp = np.where(labels_partial == c)[0]

    cluster_means_523.append(
        np.mean(stability[idx523])
    )

    cluster_means_partial.append(
        np.mean(stability[idxp])
    )

cluster_means_523 = np.array(cluster_means_523)
cluster_means_partial = np.array(cluster_means_partial)

# ============================================
# STRUCTURE VS VALUE
# ============================================

ari = adjusted_rand_score(
    labels_523,
    labels_partial
)

pearson_val, _ = pearsonr(
    cluster_means_523,
    cluster_means_partial
)

spearman_val, _ = spearmanr(
    cluster_means_523,
    cluster_means_partial
)

# ============================================
# MEMBERSHIP STABILITY TEST
# ============================================

membership_match = (
    labels_523 == labels_partial
).astype(int)

membership_stability_corr, _ = pearsonr(
    membership_match,
    stability
)

# ============================================
# VALUE DISPERSION
# ============================================

dispersion_523 = np.std(cluster_means_523)
dispersion_partial = np.std(cluster_means_partial)

dispersion_ratio = (
    dispersion_partial /
    (dispersion_523 + 1e-8)
)

# ============================================
# VERDICT
# ============================================

if (
    ari > 0.45 and
    abs(pearson_val) < 0.35 and
    abs(spearman_val) < 0.35
):
    verdict = "STRUCTURE-VALUE-DECOUPLING"

elif (
    ari > 0.45
):
    verdict = "PARTIAL-DECOUPLING"

else:
    verdict = "COUPLED-TAXONOMY"

# ============================================
# SAVE
# ============================================

summary = pd.DataFrame([{
    "phase": 526,
    "ARI": ari,
    "pearson_cluster_values": pearson_val,
    "spearman_cluster_values": spearman_val,
    "membership_stability_corr": membership_stability_corr,
    "dispersion_523": dispersion_523,
    "dispersion_partial": dispersion_partial,
    "dispersion_ratio": dispersion_ratio,
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase526/phase526_summary.csv",
    index=False
)

print("\n=== PHASE 526 COMPLETE ===")
print(summary.to_string(index=False))
