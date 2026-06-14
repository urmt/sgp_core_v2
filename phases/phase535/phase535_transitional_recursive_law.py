# PHASE 535 — TRANSITIONAL-RECURSIVE-LAW
# Test whether recursive stability is maximized
# specifically in TRANSITIONAL regions between
# incompatible cluster identities

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.stats import pearsonr, spearmanr
from scipy.spatial.distance import cdist

SEED = 535
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

base = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv"
)

systems = base["name"].values
stability = base["stability_score"].values

features = [
    "CSR",
    "ADI",
    "RBS",
    "RTP",
    "SRD"
]

# ============================================
# BEST SPACE
# ============================================

space = ["CSR", "ADI", "RBS"]

X = base[space].values
X = StandardScaler().fit_transform(X)

# ============================================
# CLUSTERING
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
# DISTANCE STRUCTURE
# ============================================

D = cdist(X, centroids)

sorted_idx = np.argsort(D, axis=1)
sorted_d = np.sort(D, axis=1)

d1 = sorted_d[:, 0]
d2 = sorted_d[:, 1]
d3 = sorted_d[:, 2]

c1 = sorted_idx[:, 0]
c2 = sorted_idx[:, 1]

# ============================================
# CLUSTER INCOMPATIBILITY MATRIX
# ============================================

cluster_means = []

for c in range(k):

    idx = labels == c

    cluster_means.append(
        np.mean(stability[idx])
    )

cluster_means = np.array(cluster_means)

cluster_gap = np.zeros((k, k))

for i in range(k):

    for j in range(k):

        cluster_gap[i, j] = abs(
            cluster_means[i] -
            cluster_means[j]
        )

# ============================================
# TRANSITIONALITY
# ============================================

# near two centroids simultaneously
balance = 1.0 - np.abs(d1 - d2) / (d1 + d2 + 1e-8)

# how different the two accessible clusters are
incompatibility = np.array([
    cluster_gap[c1[i], c2[i]]
    for i in range(len(X))
])

# combined transitionality
transitionality = (
    balance *
    incompatibility
)

# higher-order accessibility
triadicity = (
    d1 + d2
) / (
    d1 + d2 + d3 + 1e-8
)

# ============================================
# CORRELATIONS
# ============================================

metrics = {
    "balance": balance,
    "incompatibility": incompatibility,
    "transitionality": transitionality,
    "triadicity": triadicity
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

primary = transitionality

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
    best["metric"] == "transitionality" and
    best["pearson_r"] > 0.50 and
    best["pearson_p"] < 0.05
):
    verdict = "TRANSITIONAL-RECURSIVE-LAW"

elif (
    best["pearson_r"] > 0.30
):
    verdict = "PARTIAL-TRANSITIONALITY"

else:
    verdict = "NONTRANSITIONAL-STRUCTURE"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": systems,
    "stability": stability,
    "cluster": labels,
    "balance": balance,
    "incompatibility": incompatibility,
    "transitionality": transitionality,
    "triadicity": triadicity
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase535/phase535_transitionality.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 535,
    "best_metric": best["metric"],
    "best_pearson_r": best["pearson_r"],
    "best_pearson_p": best["pearson_p"],
    "best_spearman_rho": best["spearman_rho"],
    "low_shell_mean": low.mean(),
    "mid_shell_mean": mid.mean(),
    "high_shell_mean": high.mean(),
    "mean_transitionality": np.mean(transitionality),
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase535/phase535_summary.csv",
    index=False
)

print("\n=== PHASE 535 COMPLETE ===")
print(summary.to_string(index=False))
