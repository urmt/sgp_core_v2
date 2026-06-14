# PHASE 537 — DISCRETE-ASSIGNMENT-LOCKING
# Test whether recursive stability is governed by
# HARD assignment geometry itself:
#
# hypothesis:
# high stability systems resist clean assignment
# to any single cluster partition

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples
from scipy.stats import pearsonr, spearmanr
from scipy.spatial.distance import cdist

SEED = 537
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

base = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv"
)

systems = base["name"].values
stability = base["stability_score"].values

space = ["CSR", "ADI", "RBS"]

X = base[space].values
X = StandardScaler().fit_transform(X)

# ============================================
# KMEANS
# ============================================

k = 6

km = KMeans(
    n_clusters=k,
    random_state=SEED,
    n_init=100
)

labels = km.fit_predict(X)
centroids = km.cluster_centers_

# ============================================
# DISTANCES
# ============================================

D = cdist(X, centroids)

sorted_d = np.sort(D, axis=1)

d1 = sorted_d[:, 0]
d2 = sorted_d[:, 1]
d3 = sorted_d[:, 2]

# ============================================
# HARD ASSIGNMENT METRICS
# ============================================

# classic margin
margin = d2 - d1

# normalized locking
locking = (
    d2 - d1
) / (
    d2 + d1 + 1e-8
)

# assignment certainty
certainty = 1.0 / (
    d1 + 1e-8
)

# local compactness
compactness = (
    d1 + d2
) / (
    d3 + 1e-8
)

# silhouette
sil = silhouette_samples(X, labels)

# ============================================
# CORRELATIONS
# ============================================

metrics = {
    "margin": margin,
    "locking": locking,
    "certainty": certainty,
    "compactness": compactness,
    "silhouette": sil
}

rows = []

for name, vec in metrics.items():

    r, p = pearsonr(vec, stability)
    rs, _ = spearmanr(vec, stability)

    rows.append({
        "metric": name,
        "pearson_r": r,
        "pearson_p": p,
        "spearman_rho": rs
    })

results = pd.DataFrame(rows)

best_idx = results["pearson_r"].abs().idxmax()
best = results.loc[best_idx]

# ============================================
# SHELL TEST
# ============================================

primary = locking

q1 = np.quantile(primary, 0.33)
q2 = np.quantile(primary, 0.66)

low = stability[primary <= q1]
mid = stability[
    (primary > q1) &
    (primary <= q2)
]
high = stability[primary > q2]

# ============================================
# VERDICT
# ============================================

if (
    best["metric"] in ["margin", "locking"] and
    abs(best["pearson_r"]) > 0.50 and
    best["pearson_p"] < 0.05
):
    verdict = "DISCRETE-ASSIGNMENT-LOCKING"

elif (
    abs(best["pearson_r"]) > 0.30
):
    verdict = "PARTIAL-ASSIGNMENT-LOCKING"

else:
    verdict = "NONLOCKING-STRUCTURE"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": systems,
    "stability": stability,
    "cluster": labels,
    "margin": margin,
    "locking": locking,
    "certainty": certainty,
    "compactness": compactness,
    "silhouette": sil
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase537/phase537_locking.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 537,
    "best_metric": best["metric"],
    "best_pearson_r": best["pearson_r"],
    "best_pearson_p": best["pearson_p"],
    "best_spearman_rho": best["spearman_rho"],
    "low_lock_mean": low.mean(),
    "mid_lock_mean": mid.mean(),
    "high_lock_mean": high.mean(),
    "mean_locking": np.mean(locking),
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase537/phase537_summary.csv",
    index=False
)

print("\n=== PHASE 537 COMPLETE ===")
print(summary.to_string(index=False))
