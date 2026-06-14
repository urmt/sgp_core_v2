# PHASE 536 — ENTROPIC-ACCESSIBILITY-LAW
# Test whether recursive stability tracks
# GLOBAL DISTRIBUTIONAL ENTROPY across all
# cluster centroids rather than local transitions

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.stats import pearsonr, spearmanr
from scipy.spatial.distance import cdist
from scipy.special import softmax

SEED = 536
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
# DISTANCES
# ============================================

D = cdist(X, centroids)

# ============================================
# SOFT ACCESS DISTRIBUTION
# ============================================

# lower distance -> higher weight
P = softmax(-D, axis=1)

# ============================================
# ENTROPY METRICS
# ============================================

entropy = -np.sum(
    P * np.log(P + 1e-12),
    axis=1
)

max_prob = np.max(P, axis=1)

participation_ratio = (
    np.sum(P, axis=1) ** 2
) / (
    np.sum(P**2, axis=1) + 1e-12
)

gini = []

for p in P:

    diffsum = 0

    for i in p:
        for j in p:
            diffsum += abs(i - j)

    g = diffsum / (
        2 * len(p) * np.sum(p)
    )

    gini.append(g)

gini = np.array(gini)

# ============================================
# CORRELATIONS
# ============================================

metrics = {
    "entropy": entropy,
    "max_prob": max_prob,
    "participation_ratio": participation_ratio,
    "gini": gini
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

primary = entropy

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
    best["metric"] == "entropy" and
    best["pearson_r"] > 0.50 and
    best["pearson_p"] < 0.05
):
    verdict = "ENTROPIC-ACCESSIBILITY-LAW"

elif (
    best["pearson_r"] > 0.30
):
    verdict = "PARTIAL-ENTROPIC-STRUCTURE"

else:
    verdict = "NONENTROPIC-STRUCTURE"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": systems,
    "stability": stability,
    "cluster": labels,
    "entropy": entropy,
    "max_prob": max_prob,
    "participation_ratio": participation_ratio,
    "gini": gini
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase536/phase536_entropy.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 536,
    "best_metric": best["metric"],
    "best_pearson_r": best["pearson_r"],
    "best_pearson_p": best["pearson_p"],
    "best_spearman_rho": best["spearman_rho"],
    "low_entropy_mean": low.mean(),
    "mid_entropy_mean": mid.mean(),
    "high_entropy_mean": high.mean(),
    "mean_entropy": np.mean(entropy),
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase536/phase536_summary.csv",
    index=False
)

print("\n=== PHASE 536 COMPLETE ===")
print(summary.to_string(index=False))
