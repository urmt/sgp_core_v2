# PHASE 514 — TOPOLOGICAL-STABILITY-ORGANIZATION
# Goal:
# Test whether recursive stability is organized
# by local topology rather than geometry

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from scipy.stats import pearsonr

SEED = 514
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase513/phase513_radial_results.csv"
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
# LOCAL TOPOLOGY
# ============================================

k = 5

nbrs = NearestNeighbors(
    n_neighbors=k
).fit(X)

distances, indices = nbrs.kneighbors(X)

local_density = []
local_stability_var = []
neighbor_alignment = []

for i in range(len(X)):

    neigh = indices[i][1:]

    d = np.mean(distances[i][1:])

    local_density.append(
        1 / (d + 1e-8)
    )

    local_stability_var.append(
        np.std(stability[neigh])
    )

    center = X[i]

    sims = []

    for j in neigh:

        c = np.dot(center, X[j]) / (
            np.linalg.norm(center)
            * np.linalg.norm(X[j])
            + 1e-8
        )

        sims.append(c)

    neighbor_alignment.append(
        np.mean(sims)
    )

df["local_density"] = local_density
df["local_stability_var"] = local_stability_var
df["neighbor_alignment"] = neighbor_alignment

# ============================================
# CORRELATIONS
# ============================================

density_corr,_ = pearsonr(
    local_density,
    stability
)

alignment_corr,_ = pearsonr(
    neighbor_alignment,
    stability
)

variance_corr,_ = pearsonr(
    local_stability_var,
    stability
)

# ============================================
# TOPOLOGICAL COHERENCE
# ============================================

topological_coherence = (
    abs(density_corr)
    + abs(alignment_corr)
    + abs(variance_corr)
) / 3

# ============================================
# VERDICT
# ============================================

if topological_coherence > 0.65:
    verdict = "TOPOLOGICAL-STABILITY-SPACE"
elif topological_coherence > 0.35:
    verdict = "PARTIAL-TOPOLOGICAL-STRUCTURE"
else:
    verdict = "TOPOLOGICALLY-DISORDERED"

# ============================================
# OUTPUT
# ============================================

summary = {
    "phase": 514,
    "density_corr":
        float(density_corr),
    "alignment_corr":
        float(alignment_corr),
    "variance_corr":
        float(variance_corr),
    "topological_coherence":
        float(topological_coherence),
    "verdict":
        verdict
}

summary_df = pd.DataFrame([summary])

summary_df.to_csv(
    "/home/student/sgp_core_v2/phases/phase514/phase514_summary.csv",
    index=False
)

df.to_csv(
    "/home/student/sgp_core_v2/phases/phase514/phase514_topology_results.csv",
    index=False
)

print("\n=== PHASE 514 COMPLETE ===")
print(summary_df.to_string(index=False))
