# PHASE 522 — CLUSTER-BOUNDARY-DYNAMICS
# Test whether stability degradation occurs primarily
# at soft cluster boundaries rather than within clusters

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import cdist
from scipy.stats import pearsonr

SEED = 522
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv"
)

features = ["CSR", "ADI", "RBS", "RTP", "SRD"]

X = df[features].values
X = StandardScaler().fit_transform(X)

stability = df["stability_score"].values

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

centers = kmeans.cluster_centers_

sil = silhouette_score(X, labels)

# ============================================
# BOUNDARY DISTANCES
# ============================================

distances = cdist(X, centers)

nearest = np.min(distances, axis=1)

sorted_dist = np.sort(distances, axis=1)

boundary_margin = (
    sorted_dist[:,1] - sorted_dist[:,0]
)

# low margin = near boundary
# high margin = deep interior

# ============================================
# CORRELATIONS
# ============================================

margin_corr, _ = pearsonr(
    stability,
    boundary_margin
)

nearest_corr, _ = pearsonr(
    stability,
    nearest
)

# ============================================
# SHELL ANALYSIS
# ============================================

q1 = np.quantile(boundary_margin, 0.33)
q2 = np.quantile(boundary_margin, 0.66)

boundary_mask = boundary_margin <= q1
mid_mask = (
    (boundary_margin > q1) &
    (boundary_margin <= q2)
)
interior_mask = boundary_margin > q2

boundary_mean = np.mean(
    stability[boundary_mask]
)

mid_mean = np.mean(
    stability[mid_mask]
)

interior_mean = np.mean(
    stability[interior_mask]
)

# ============================================
# INTRA VS INTER VARIANCE
# ============================================

intra_var = []
inter_var = []

for c in range(k):

    idx = np.where(labels == c)[0]

    if len(idx) < 2:
        continue

    intra = np.var(stability[idx])

    outside = np.var(
        stability[
            np.where(labels != c)[0]
        ]
    )

    intra_var.append(intra)
    inter_var.append(outside)

mean_intra = np.mean(intra_var)
mean_inter = np.mean(inter_var)

variance_ratio = (
    mean_inter / (mean_intra + 1e-8)
)

# ============================================
# VERDICT
# ============================================

if (
    margin_corr > 0.55 and
    variance_ratio > 1.5 and
    interior_mean > boundary_mean
):
    verdict = "BOUNDARY-REGULATED-STABILITY"

elif (
    margin_corr > 0.30
):
    verdict = "PARTIAL-BOUNDARY-STRUCTURE"

else:
    verdict = "NONBOUNDARY-ORGANIZATION"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": df["name"],
    "cluster": labels,
    "stability": stability,
    "boundary_margin": boundary_margin,
    "nearest_center_distance": nearest
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase522/phase522_boundary_metrics.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 522,
    "silhouette": sil,
    "margin_stability_corr": margin_corr,
    "nearest_distance_corr": nearest_corr,
    "boundary_mean": boundary_mean,
    "mid_mean": mid_mean,
    "interior_mean": interior_mean,
    "mean_intra_variance": mean_intra,
    "mean_inter_variance": mean_inter,
    "variance_ratio": variance_ratio,
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase522/phase522_summary.csv",
    index=False
)

print("\n=== PHASE 522 COMPLETE ===")
print(summary.to_string(index=False))
