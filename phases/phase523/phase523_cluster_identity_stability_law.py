# PHASE 523 — CLUSTER-IDENTITY-STABILITY-LAW
# Test whether stability is primarily a categorical
# cluster-membership property rather than a geometric property

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.stats import f_oneway, pearsonr

SEED = 523
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase522/phase522_boundary_metrics.csv"
)

features = [
    "stability",
    "boundary_margin",
    "nearest_center_distance"
]

X = df[features].values
X = StandardScaler().fit_transform(X)

stability = df["stability"].values

# ============================================
# CLUSTERING
# ============================================

k = 6

kmeans = KMeans(
    n_clusters=k,
    random_state=SEED,
    n_init=25
)

labels = kmeans.fit_predict(X)

sil = silhouette_score(X, labels)

# ============================================
# CLUSTER STABILITY STATISTICS
# ============================================

cluster_means = []
cluster_vars = []
cluster_sizes = []

for c in range(k):

    vals = stability[labels == c]

    cluster_means.append(np.mean(vals))
    cluster_vars.append(np.var(vals))
    cluster_sizes.append(len(vals))

cluster_means = np.array(cluster_means)
cluster_vars = np.array(cluster_vars)

# ============================================
# BETWEEN / WITHIN ANALYSIS
# ============================================

overall_mean = np.mean(stability)

ss_between = 0
ss_within = 0

for c in range(k):

    vals = stability[labels == c]

    ss_between += (
        len(vals) *
        (np.mean(vals) - overall_mean)**2
    )

    ss_within += np.sum(
        (vals - np.mean(vals))**2
    )

explained_ratio = (
    ss_between /
    (ss_between + ss_within + 1e-8)
)

# ============================================
# ANOVA
# ============================================

groups = [
    stability[labels == c]
    for c in range(k)
]

F_stat, p_val = f_oneway(*groups)

# ============================================
# POSITIONAL RESIDUAL TEST
# ============================================

margin_corr, _ = pearsonr(
    stability,
    df["boundary_margin"]
)

distance_corr, _ = pearsonr(
    stability,
    df["nearest_center_distance"]
)

positional_strength = (
    abs(margin_corr) +
    abs(distance_corr)
) / 2

identity_dominance = (
    explained_ratio -
    positional_strength
)

# ============================================
# VERDICT
# ============================================

if (
    explained_ratio > 0.75 and
    identity_dominance > 0.45 and
    p_val < 1e-4
):
    verdict = "CLUSTER-IDENTITY-LAW"

elif (
    explained_ratio > 0.50
):
    verdict = "PARTIAL-IDENTITY-STRUCTURE"

else:
    verdict = "POSITIONAL-ORGANIZATION"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": df["system"],
    "cluster": labels,
    "stability": stability
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase523/phase523_cluster_identity.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 523,
    "silhouette": sil,
    "explained_ratio": explained_ratio,
    "anova_F": F_stat,
    "anova_p": p_val,
    "margin_corr": margin_corr,
    "distance_corr": distance_corr,
    "identity_dominance": identity_dominance,
    "mean_cluster_variance": np.mean(cluster_vars),
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase523/phase523_summary.csv",
    index=False
)

print("\n=== PHASE 523 COMPLETE ===")
print(summary.to_string(index=False))
