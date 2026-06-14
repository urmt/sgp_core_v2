# PHASE 520 — LOCAL-STABILITY-PROPAGATION
# Test whether stability behaves like a local propagation field
# across the distributed manifold topology

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import kneighbors_graph
from scipy.stats import pearsonr
import networkx as nx

SEED = 520
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
# GRAPH
# ============================================

k = 5

A = kneighbors_graph(
    X,
    n_neighbors=k,
    mode="connectivity",
    include_self=False
)

G = nx.from_scipy_sparse_array(A)

# ============================================
# LOCAL PROPAGATION
# ============================================

neighbor_mean = []
neighbor_gradient = []
local_diffusion = []

for i in range(len(stability)):

    nbrs = list(G.neighbors(i))

    nbr_vals = stability[nbrs]

    mean_val = np.mean(nbr_vals)

    grad = abs(
        stability[i] - mean_val
    )

    diffusion = np.mean(
        np.abs(nbr_vals - stability[i])
    )

    neighbor_mean.append(mean_val)
    neighbor_gradient.append(grad)
    local_diffusion.append(diffusion)

neighbor_mean = np.array(neighbor_mean)
neighbor_gradient = np.array(neighbor_gradient)
local_diffusion = np.array(local_diffusion)

# ============================================
# PROPAGATION METRICS
# ============================================

mean_corr, _ = pearsonr(
    stability,
    neighbor_mean
)

gradient_corr, _ = pearsonr(
    stability,
    neighbor_gradient
)

diffusion_corr, _ = pearsonr(
    stability,
    local_diffusion
)

# ============================================
# LAPLACIAN ENERGY
# ============================================

L = nx.laplacian_matrix(G).toarray()

energy = (
    stability.T @ L @ stability
)

normalized_energy = (
    energy / len(stability)
)

# ============================================
# FIELD COHERENCE
# ============================================

field_coherence = (
    1.0 / (1.0 + normalized_energy)
)

# ============================================
# VERDICT
# ============================================

if (
    mean_corr > 0.80 and
    field_coherence > 0.60 and
    diffusion_corr < -0.50
):
    verdict = "LOCAL-PROPAGATION-FIELD"

elif (
    mean_corr > 0.60
):
    verdict = "PARTIAL-PROPAGATION-STRUCTURE"

else:
    verdict = "NONPROPAGATING-TOPOLOGY"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": df["name"],
    "stability": stability,
    "neighbor_mean": neighbor_mean,
    "neighbor_gradient": neighbor_gradient,
    "local_diffusion": local_diffusion
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase520/phase520_local_field.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 520,
    "neighbor_mean_corr": mean_corr,
    "neighbor_gradient_corr": gradient_corr,
    "local_diffusion_corr": diffusion_corr,
    "laplacian_energy": float(normalized_energy),
    "field_coherence": float(field_coherence),
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase520/phase520_summary.csv",
    index=False
)

print("\n=== PHASE 520 COMPLETE ===")
print(summary.to_string(index=False))
