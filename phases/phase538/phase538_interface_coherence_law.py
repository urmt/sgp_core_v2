# PHASE 538 — INTERFACE-COHERENCE-LAW
# Test whether recursive stability is maximized
# specifically at STRUCTURED INTERFACES:
#
# not fully locked,
# not fully diffuse,
# but balanced between categorical coherence
# and cross-cluster accessibility

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from scipy.stats import pearsonr, spearmanr

SEED = 538
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

sorted_d = np.sort(D, axis=1)

d1 = sorted_d[:, 0]
d2 = sorted_d[:, 1]
d3 = sorted_d[:, 2]

# ============================================
# INTERFACE METRICS
# ============================================

# assignment locking
margin = d2 - d1

# accessibility spread
spread = (
    d1 + d2
) / (
    d1 + d2 + d3 + 1e-8
)

# normalized coherence
coherence = 1.0 / (d1 + 1e-8)

# --------------------------------------------
# INTERFACE BALANCE
# maximal when:
# - moderate margin
# - moderate spread
# - finite coherence
# --------------------------------------------

margin_z = (
    margin - np.mean(margin)
) / (
    np.std(margin) + 1e-8
)

spread_z = (
    spread - np.mean(spread)
) / (
    np.std(spread) + 1e-8
)

coherence_z = (
    coherence - np.mean(coherence)
) / (
    np.std(coherence) + 1e-8
)

# penalize extremes
interface_balance = -(
    np.abs(margin_z) +
    np.abs(spread_z) +
    np.abs(coherence_z)
)

# smooth hybrid accessibility
hybridity = (
    (1.0 / (1.0 + margin)) *
    (1.0 - spread)
)

# ============================================
# CORRELATIONS
# ============================================

metrics = {
    "margin": margin,
    "spread": spread,
    "coherence": coherence,
    "interface_balance": interface_balance,
    "hybridity": hybridity
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

primary = interface_balance

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
    best["metric"] == "interface_balance" and
    best["pearson_r"] > 0.50 and
    best["pearson_p"] < 0.05
):
    verdict = "INTERFACE-COHERENCE-LAW"

elif (
    best["pearson_r"] > 0.30
):
    verdict = "PARTIAL-INTERFACE-STRUCTURE"

else:
    verdict = "NONINTERFACE-STRUCTURE"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": systems,
    "stability": stability,
    "cluster": labels,
    "margin": margin,
    "spread": spread,
    "coherence": coherence,
    "interface_balance": interface_balance,
    "hybridity": hybridity
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase538/phase538_interface.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 538,
    "best_metric": best["metric"],
    "best_pearson_r": best["pearson_r"],
    "best_pearson_p": best["pearson_p"],
    "best_spearman_rho": best["spearman_rho"],
    "low_shell_mean": low.mean(),
    "mid_shell_mean": mid.mean(),
    "high_shell_mean": high.mean(),
    "mean_interface_balance": np.mean(interface_balance),
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase538/phase538_summary.csv",
    index=False
)

print("\n=== PHASE 538 COMPLETE ===")
print(summary.to_string(index=False))
