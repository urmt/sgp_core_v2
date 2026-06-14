# PHASE 517 — CRITICAL-STABILITY-PERCOLATION
# Goal:
# Determine whether recursive stability obeys
# a true critical threshold law with finite-size scaling

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import kneighbors_graph
from scipy.stats import pearsonr
import networkx as nx

SEED = 517
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv"
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
# THRESHOLD SWEEP
# ============================================

thresholds = np.linspace(
    np.min(stability),
    np.max(stability),
    50
)

largest_component = []
num_components = []
susceptibility = []

for t in thresholds:

    nodes = [
        i for i,s in enumerate(stability)
        if s >= t
    ]

    sub = G.subgraph(nodes)

    if len(sub.nodes) == 0:
        largest_component.append(0)
        num_components.append(0)
        susceptibility.append(0)
        continue

    comps = [
        len(c)
        for c in nx.connected_components(sub)
    ]

    largest_component.append(max(comps))
    num_components.append(len(comps))

    if len(comps) > 1:
        susceptibility.append(
            np.var(comps)
        )
    else:
        susceptibility.append(0)

largest_component = np.array(largest_component)
num_components = np.array(num_components)
susceptibility = np.array(susceptibility)

# ============================================
# CRITICAL POINT DETECTION
# ============================================

deltas = np.diff(largest_component)

critical_idx = np.argmin(deltas)

critical_threshold = thresholds[critical_idx]

max_drop = deltas[critical_idx]

critical_susceptibility = np.max(
    susceptibility
)

# ============================================
# SCALING TEST
# ============================================

normalized_component = (
    largest_component /
    np.max(largest_component)
)

tail = normalized_component[
    critical_idx:
]

if len(tail) > 3:

    x = np.arange(len(tail)) + 1

    y = np.log(
        np.clip(tail, 1e-6, None)
    )

    slope, intercept = np.polyfit(x, y, 1)

    scaling_exponent = abs(slope)

else:
    scaling_exponent = np.nan

# ============================================
# CORRELATIONS
# ============================================

corr_threshold,_ = pearsonr(
    thresholds,
    normalized_component
)

corr_susc,_ = pearsonr(
    susceptibility,
    normalized_component
)

# ============================================
# VERDICT
# ============================================

if (
    max_drop < -8 and
    critical_susceptibility > 5 and
    scaling_exponent > 0.1
):
    verdict = "CRITICAL-PERCOLATION-LAW"

elif max_drop < -5:
    verdict = "BOUNDED-PERCOLATION"

else:
    verdict = "NONCRITICAL-STRUCTURE"

# ============================================
# SAVE
# ============================================

results = pd.DataFrame({
    "threshold": thresholds,
    "largest_component": largest_component,
    "num_components": num_components,
    "susceptibility": susceptibility,
    "normalized_component": normalized_component
})

summary = pd.DataFrame([{
    "phase": 517,
    "critical_threshold":
        float(critical_threshold),
    "max_drop":
        float(max_drop),
    "critical_susceptibility":
        float(critical_susceptibility),
    "scaling_exponent":
        float(scaling_exponent),
    "threshold_component_corr":
        float(corr_threshold),
    "susceptibility_component_corr":
        float(corr_susc),
    "verdict":
        verdict
}])

results.to_csv(
    "/home/student/sgp_core_v2/phases/phase517/phase517_percolation_curve.csv",
    index=False
)

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase517/phase517_summary.csv",
    index=False
)

print("\n=== PHASE 517 COMPLETE ===")
print(summary.to_string(index=False))
