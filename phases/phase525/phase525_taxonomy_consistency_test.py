# PHASE 525 — TAXONOMY-CONSISTENCY-TEST
# Determine whether the Phase 523 and Phase 524
# clusterings are two projections of one latent taxonomy
# or genuinely incompatible organizational regimes

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    normalized_mutual_info_score
)
from scipy.stats import pearsonr
from scipy.spatial.distance import cdist

SEED = 525
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

features_524 = ["CSR", "ADI", "RBS"]

# ============================================
# PHASE 523 LABELS
# ============================================

labels_523 = p523["cluster"].values

# ============================================
# PHASE 524 RECONSTRUCTION
# ============================================

X524 = base[features_524].values
X524 = StandardScaler().fit_transform(X524)

km524 = KMeans(
    n_clusters=6,
    random_state=SEED,
    n_init=25
)

labels_524 = km524.fit_predict(X524)

# ============================================
# TAXONOMY AGREEMENT
# ============================================

ari = adjusted_rand_score(
    labels_523,
    labels_524
)

nmi = normalized_mutual_info_score(
    labels_523,
    labels_524
)

# ============================================
# CENTROID ALIGNMENT
# ============================================

stab = base["stability_score"].values

cent523 = []
cent524 = []

for c in range(6):

    idx523 = np.where(labels_523 == c)[0]
    idx524 = np.where(labels_524 == c)[0]

    cent523.append(
        np.mean(stab[idx523])
    )

    cent524.append(
        np.mean(stab[idx524])
    )

cent523 = np.array(cent523)
cent524 = np.array(cent524)

centroid_corr, _ = pearsonr(
    cent523,
    cent524
)

# ============================================
# CROSS-MAPPING MATRIX
# ============================================

matrix = np.zeros((6,6))

for i in range(6):

    idx_i = np.where(labels_523 == i)[0]

    for j in range(6):

        idx_j = np.where(labels_524 == j)[0]

        overlap = len(
            set(idx_i).intersection(set(idx_j))
        )

        matrix[i,j] = overlap

purity = np.sum(np.max(matrix, axis=1)) / len(base)

# ============================================
# DISTANCE CONSISTENCY
# ============================================

d523 = cdist(
    np.expand_dims(cent523,1),
    np.expand_dims(cent523,1)
)

d524 = cdist(
    np.expand_dims(cent524,1),
    np.expand_dims(cent524,1)
)

tri523 = d523[np.triu_indices(6,1)]
tri524 = d524[np.triu_indices(6,1)]

distance_corr, _ = pearsonr(
    tri523,
    tri524
)

# ============================================
# VERDICT
# ============================================

if (
    ari > 0.75 and
    centroid_corr > 0.80 and
    purity > 0.80
):
    verdict = "UNIFIED-TAXONOMY"

elif (
    ari > 0.35 and
    nmi > 0.50
):
    verdict = "PARTIAL-TAXONOMIC-OVERLAP"

else:
    verdict = "COMPETING-TAXONOMIES"

# ============================================
# SAVE
# ============================================

pd.DataFrame(matrix).to_csv(
    "/home/student/sgp_core_v2/phases/phase525/phase525_overlap_matrix.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 525,
    "ARI": ari,
    "NMI": nmi,
    "purity": purity,
    "centroid_corr": centroid_corr,
    "distance_corr": distance_corr,
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase525/phase525_summary.csv",
    index=False
)

print("\n=== PHASE 525 COMPLETE ===")
print(summary.to_string(index=False))
