# PHASE 521 — LOCAL-SMOOTHNESS-CONSTRAINT
# Test whether recursive stability is governed by
# neighborhood smoothness rather than propagation

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import kneighbors_graph
from scipy.stats import pearsonr
import networkx as nx

SEED = 521
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase520/phase520_local_field.csv"
)

features = [
    "stability",
    "neighbor_mean",
    "neighbor_gradient",
    "local_diffusion"
]

X = df[features].values

X = StandardScaler().fit_transform(X)

stability = df["stability"].values

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
# LOCAL SMOOTHNESS
# ============================================

local_variance = []
local_range = []
laplacian_deviation = []

for i in range(len(stability)):

    nbrs = list(G.neighbors(i))

    nbr_vals = stability[nbrs]

    var = np.var(nbr_vals)

    rng = np.max(nbr_vals) - np.min(nbr_vals)

    dev = abs(
        stability[i] - np.mean(nbr_vals)
    )

    local_variance.append(var)
    local_range.append(rng)
    laplacian_deviation.append(dev)

local_variance = np.array(local_variance)
local_range = np.array(local_range)
laplacian_deviation = np.array(laplacian_deviation)

# ============================================
# CORRELATIONS
# ============================================

var_corr, _ = pearsonr(
    stability,
    local_variance
)

range_corr, _ = pearsonr(
    stability,
    local_range
)

lap_corr, _ = pearsonr(
    stability,
    laplacian_deviation
)

# ============================================
# GLOBAL SMOOTHNESS ENERGY
# ============================================

L = nx.laplacian_matrix(G).toarray()

smoothness_energy = (
    stability.T @ L @ stability
)

normalized_smoothness = (
    smoothness_energy / len(stability)
)

smoothness_index = (
    1.0 / (1.0 + normalized_smoothness)
)

# ============================================
# SHELL TEST
# ============================================

q1 = np.quantile(
    local_variance,
    0.33
)

q2 = np.quantile(
    local_variance,
    0.66
)

low_mask = local_variance <= q1
mid_mask = (
    (local_variance > q1) &
    (local_variance <= q2)
)
high_mask = local_variance > q2

low_mean = np.mean(stability[low_mask])
mid_mean = np.mean(stability[mid_mask])
high_mean = np.mean(stability[high_mask])

# ============================================
# VERDICT
# ============================================

if (
    var_corr < -0.60 and
    lap_corr < -0.60 and
    smoothness_index > 0.65
):
    verdict = "LOCAL-SMOOTHNESS-LAW"

elif (
    var_corr < -0.40
):
    verdict = "PARTIAL-SMOOTHNESS-STRUCTURE"

else:
    verdict = "NONSMOOTH-TOPOLOGY"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": df["system"],
    "stability": stability,
    "local_variance": local_variance,
    "local_range": local_range,
    "laplacian_deviation": laplacian_deviation
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase521/phase521_smoothness.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 521,
    "variance_corr": var_corr,
    "range_corr": range_corr,
    "laplacian_corr": lap_corr,
    "smoothness_index": smoothness_index,
    "low_variance_mean": low_mean,
    "mid_variance_mean": mid_mean,
    "high_variance_mean": high_mean,
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase521/phase521_summary.csv",
    index=False
)

print("\n=== PHASE 521 COMPLETE ===")
print(summary.to_string(index=False))
