# PHASE 515 — LOCAL-HOMOGENEITY-STABILITY-TEST
# Goal:
# Test whether recursive stability is governed
# primarily by neighborhood homogeneity

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression

SEED = 515
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase514/phase514_topology_results.csv"
)

features = [
    "CSR",
    "ADI",
    "RBS",
    "RTP",
    "SRD"
]

X = df[features].values
X = StandardScaler().fit_transform(X)

# ============================================
# STABILITY
# ============================================

if "stability_score" in df.columns:
    stability = df["stability_score"].values
else:
    stability = (
        X[:,0] +
        X[:,2] +
        X[:,3] -
        X[:,4]
    )

# ============================================
# LOCAL HOMOGENEITY
# ============================================

k = 5

nbrs = NearestNeighbors(
    n_neighbors=k
).fit(X)

distances, indices = nbrs.kneighbors(X)

homogeneity_scores = []
neighbor_mean_stability = []
neighbor_std_stability = []

for i in range(len(X)):

    neigh = indices[i][1:]

    neigh_stab = stability[neigh]

    std_val = np.std(neigh_stab)
    mean_val = np.mean(neigh_stab)

    homogeneity = 1 / (
        1 + std_val
    )

    homogeneity_scores.append(
        homogeneity
    )

    neighbor_mean_stability.append(
        mean_val
    )

    neighbor_std_stability.append(
        std_val
    )

df["homogeneity"] = homogeneity_scores
df["neighbor_mean_stability"] = neighbor_mean_stability
df["neighbor_std_stability"] = neighbor_std_stability

# ============================================
# CORRELATIONS
# ============================================

hom_corr,_ = pearsonr(
    homogeneity_scores,
    stability
)

mean_corr,_ = pearsonr(
    neighbor_mean_stability,
    stability
)

std_corr,_ = pearsonr(
    neighbor_std_stability,
    stability
)

# ============================================
# LINEAR FIT
# ============================================

h = np.array(
    homogeneity_scores
).reshape(-1,1)

model = LinearRegression()
model.fit(h, stability)

r2 = model.score(h, stability)

# ============================================
# SHELL HOMOGENEITY
# ============================================

quantiles = pd.qcut(
    homogeneity_scores,
    q=3,
    labels=[
        "low",
        "mid",
        "high"
    ]
)

df["homogeneity_shell"] = quantiles

shell_means = (
    df.groupby("homogeneity_shell")[
        "neighbor_mean_stability"
    ]
    .mean()
    .to_dict()
)

# ============================================
# VERDICT
# ============================================

if abs(hom_corr) > 0.70 and r2 > 0.50:
    verdict = "HOMOGENEITY-GOVERNED"
elif abs(hom_corr) > 0.40:
    verdict = "PARTIAL-HOMOGENEITY-STRUCTURE"
else:
    verdict = "WEAK-HOMOGENEITY-DEPENDENCE"

# ============================================
# OUTPUT
# ============================================

summary = {
    "phase": 515,
    "homogeneity_corr":
        float(hom_corr),
    "neighbor_mean_corr":
        float(mean_corr),
    "neighbor_std_corr":
        float(std_corr),
    "homogeneity_r2":
        float(r2),
    "low_shell_mean":
        float(shell_means["low"]),
    "mid_shell_mean":
        float(shell_means["mid"]),
    "high_shell_mean":
        float(shell_means["high"]),
    "verdict":
        verdict
}

summary_df = pd.DataFrame([summary])

summary_df.to_csv(
    "/home/student/sgp_core_v2/phases/phase515/phase515_summary.csv",
    index=False
)

df.to_csv(
    "/home/student/sgp_core_v2/phases/phase515/phase515_homogeneity_results.csv",
    index=False
)

print("\n=== PHASE 515 COMPLETE ===")
print(summary_df.to_string(index=False))
