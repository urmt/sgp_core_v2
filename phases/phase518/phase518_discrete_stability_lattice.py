# PHASE 518 — DISCRETE-STABILITY-LATTICE
# Test whether recursive stability is organized
# by discrete lattice-shell structure instead of
# continuous geometry/percolation criticality

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.stats import pearsonr
from scipy.spatial.distance import cdist

SEED = 518
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase517/phase517_percolation_curve.csv"
)

systems = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv"
)

features = [
    "CSR",
    "ADI",
    "RBS",
    "RTP",
    "SRD"
]

X = systems[features].values
X = StandardScaler().fit_transform(X)

stability = systems["stability_score"].values

# ============================================
# K-SCAN
# ============================================

cluster_results = []

for k in range(2, 9):

    model = KMeans(
        n_clusters=k,
        random_state=SEED,
        n_init=20
    )

    labels = model.fit_predict(X)

    sil = silhouette_score(X, labels)

    centers = model.cluster_centers_

    dists = cdist(X, centers)

    shell_index = np.min(dists, axis=1)

    shell_corr, _ = pearsonr(
        shell_index,
        stability
    )

    cluster_means = []

    for i in range(k):

        vals = stability[labels == i]

        cluster_means.append(
            np.mean(vals)
        )

    separation = np.std(cluster_means)

    cluster_results.append({
        "k": k,
        "silhouette": sil,
        "shell_corr": shell_corr,
        "cluster_separation": separation
    })

cluster_df = pd.DataFrame(cluster_results)

# ============================================
# BEST K
# ============================================

best_idx = cluster_df["silhouette"].idxmax()

best = cluster_df.iloc[best_idx]

best_k = int(best["k"])

best_sil = float(best["silhouette"])

best_shell_corr = float(best["shell_corr"])

best_sep = float(best["cluster_separation"])

# ============================================
# FINAL CLUSTER MODEL
# ============================================

final_model = KMeans(
    n_clusters=best_k,
    random_state=SEED,
    n_init=20
)

labels = final_model.fit_predict(X)

cluster_stats = []

for i in range(best_k):

    vals = stability[labels == i]

    cluster_stats.append({
        "cluster": i,
        "size": len(vals),
        "mean_stability": float(np.mean(vals)),
        "std_stability": float(np.std(vals))
    })

cluster_stats = pd.DataFrame(cluster_stats)

# ============================================
# LATTICE TEST
# ============================================

ordered = cluster_stats.sort_values(
    "mean_stability"
)

means = ordered["mean_stability"].values

diffs = np.diff(means)

if len(diffs) > 0:
    lattice_spacing = np.std(diffs)
else:
    lattice_spacing = np.nan

# ============================================
# VERDICT
# ============================================

if (
    best_sil > 0.45 and
    best_sep > 0.25 and
    lattice_spacing < 0.15
):
    verdict = "DISCRETE-STABILITY-LATTICE"

elif (
    best_sil > 0.30
):
    verdict = "BOUNDED-CLUSTER-STRUCTURE"

else:
    verdict = "CONTINUOUS-DISTRIBUTION"

# ============================================
# SAVE
# ============================================

cluster_df.to_csv(
    "/home/student/sgp_core_v2/phases/phase518/phase518_k_scan.csv",
    index=False
)

cluster_stats.to_csv(
    "/home/student/sgp_core_v2/phases/phase518/phase518_cluster_stats.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 518,
    "best_k": best_k,
    "best_silhouette": best_sil,
    "best_shell_corr": best_shell_corr,
    "cluster_separation": best_sep,
    "lattice_spacing_std": lattice_spacing,
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase518/phase518_summary.csv",
    index=False
)

print("\n=== PHASE 518 COMPLETE ===")
print(summary.to_string(index=False))
