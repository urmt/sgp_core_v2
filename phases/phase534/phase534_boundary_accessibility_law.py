# PHASE 534 — BOUNDARY-ACCESSIBILITY LAW
# Test whether recursive stability is specifically
# maximized at INTER-CLUSTER ACCESSIBILITY zones

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.stats import pearsonr, spearmanr
from scipy.spatial.distance import cdist

SEED = 534
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
# BEST SPACE FROM PHASE 532
# ============================================

space = ["CSR", "ADI", "RBS"]

X = base[space].values
X = StandardScaler().fit_transform(X)

# ============================================
# CLUSTER
# ============================================

km = KMeans(
    n_clusters=6,
    random_state=SEED,
    n_init=100
)

labels = km.fit_predict(X)
centroids = km.cluster_centers_

# ============================================
# ACCESSIBILITY METRICS
# ============================================

D = cdist(X, centroids)

nearest = np.min(D, axis=1)

sorted_d = np.sort(D, axis=1)

d1 = sorted_d[:, 0]
d2 = sorted_d[:, 1]
d3 = sorted_d[:, 2]

# --------------------------------------------
# Boundary accessibility
# --------------------------------------------

boundary_ratio = d1 / (d2 + 1e-8)

# high when near multiple clusters
multi_access = 1.0 / (
    (d2 - d1) + 1e-8
)

# triadic accessibility
triadic_access = 1.0 / (
    (d3 - d1) + 1e-8
)

# normalized entropy-like spread
spread = (
    d1 + d2
) / (
    d1 + d2 + d3 + 1e-8
)

# ============================================
# CORRELATIONS
# ============================================

metrics = {
    "boundary_ratio": boundary_ratio,
    "multi_access": multi_access,
    "triadic_access": triadic_access,
    "spread": spread
}

results = []

for name, vec in metrics.items():

    r, p = pearsonr(vec, stability)
    rs, _ = spearmanr(vec, stability)

    results.append({
        "metric": name,
        "pearson_r": r,
        "pearson_p": p,
        "spearman_rho": rs
    })

results = pd.DataFrame(results)

# ============================================
# BEST METRIC
# ============================================

best_idx = results["pearson_r"].abs().idxmax()
best = results.loc[best_idx]

# ============================================
# SHELL TEST
# ============================================

primary = multi_access

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
    best["pearson_r"] > 0.50 and
    best["pearson_p"] < 0.05
):
    verdict = "BOUNDARY-ACCESSIBILITY-LAW"

elif (
    best["pearson_r"] > 0.30
):
    verdict = "PARTIAL-BOUNDARY-ACCESSIBILITY"

else:
    verdict = "NONBOUNDARY-ACCESSIBILITY"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": systems,
    "stability": stability,
    "cluster": labels,
    "boundary_ratio": boundary_ratio,
    "multi_access": multi_access,
    "triadic_access": triadic_access,
    "spread": spread
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase534/phase534_accessibility.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 534,
    "best_metric": best["metric"],
    "best_pearson_r": best["pearson_r"],
    "best_pearson_p": best["pearson_p"],
    "best_spearman_rho": best["spearman_rho"],
    "low_shell_mean": low.mean(),
    "mid_shell_mean": mid.mean(),
    "high_shell_mean": high.mean(),
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase534/phase534_summary.csv",
    index=False
)

print("\n=== PHASE 534 COMPLETE ===")
print(summary.to_string(index=False))
