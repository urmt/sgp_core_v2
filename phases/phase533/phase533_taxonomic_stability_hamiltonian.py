# PHASE 533 — TAXONOMIC STABILITY HAMILTONIAN
# Test whether cluster identity behaves like
# a discrete energy landscape with stable basins

import numpy as np
import pandas as pd
from itertools import combinations
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.stats import pearsonr
from scipy.spatial.distance import cdist

SEED = 533
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

base = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv"
)

features = [
    "CSR",
    "ADI",
    "RBS",
    "RTP",
    "SRD"
]

systems = base["name"].values
stability = base["stability_score"].values

# ============================================
# BEST PROJECTION
# ============================================

best_features = ["CSR", "ADI", "RBS"]

X = base[best_features].values
X = StandardScaler().fit_transform(X)

# ============================================
# KMEANS
# ============================================

km = KMeans(
    n_clusters=6,
    random_state=SEED,
    n_init=100
)

labels = km.fit_predict(X)
centroids = km.cluster_centers_

# ============================================
# ENERGY LANDSCAPE
# ============================================

distances = cdist(X, centroids)

assigned_energy = np.zeros(len(X))
alt_energy_gap = np.zeros(len(X))

for i in range(len(X)):

    d = distances[i]

    own = labels[i]

    own_energy = d[own]

    others = np.delete(d, own)

    nearest_alt = np.min(others)

    assigned_energy[i] = own_energy

    alt_energy_gap[i] = (
        nearest_alt - own_energy
    )

# ============================================
# BASIN STABILITY
# ============================================

cluster_variance = []
cluster_mean_stability = []

for c in np.unique(labels):

    idx = labels == c

    cluster_variance.append(
        np.var(stability[idx])
    )

    cluster_mean_stability.append(
        np.mean(stability[idx])
    )

cluster_variance = np.array(cluster_variance)
cluster_mean_stability = np.array(cluster_mean_stability)

# ============================================
# CORRELATIONS
# ============================================

gap_corr, gap_p = pearsonr(
    alt_energy_gap,
    stability
)

energy_corr, energy_p = pearsonr(
    assigned_energy,
    stability
)

var_corr, var_p = pearsonr(
    cluster_variance,
    cluster_mean_stability
)

# ============================================
# TRANSITION SUSCEPTIBILITY
# ============================================

susceptibility = 1.0 / (
    alt_energy_gap + 1e-6
)

sus_corr, sus_p = pearsonr(
    susceptibility,
    stability
)

# ============================================
# VERDICT
# ============================================

if (
    gap_corr > 0.60 and
    energy_corr < -0.60
):
    verdict = "DISCRETE-STABILITY-HAMILTONIAN"

elif (
    gap_corr > 0.35
):
    verdict = "PARTIAL-BASIN-STRUCTURE"

else:
    verdict = "NONENERGETIC-TAXONOMY"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": systems,
    "cluster": labels,
    "stability": stability,
    "assigned_energy": assigned_energy,
    "alt_energy_gap": alt_energy_gap,
    "susceptibility": susceptibility
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase533/phase533_basin_structure.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 533,
    "gap_corr": gap_corr,
    "gap_p": gap_p,
    "energy_corr": energy_corr,
    "energy_p": energy_p,
    "susceptibility_corr": sus_corr,
    "susceptibility_p": sus_p,
    "variance_corr": var_corr,
    "variance_p": var_p,
    "mean_gap": np.mean(alt_energy_gap),
    "mean_energy": np.mean(assigned_energy),
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase533/phase533_summary.csv",
    index=False
)

print("\n=== PHASE 533 COMPLETE ===")
print(summary.to_string(index=False))
