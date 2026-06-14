# PHASE 539 — OPTIMAL-INTERFACE-BAND
# Test whether recursive stability follows a
# TRUE INTERFACE OPTIMUM:
#
# too locked      -> low stability
# too diffuse     -> low stability
# intermediate    -> maximal stability
#
# mathematically:
# inverted-U structure

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

SEED = 539
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
# CORE METRICS
# ============================================

margin = d2 - d1

spread = (
    d1 + d2
) / (
    d1 + d2 + d3 + 1e-8
)

hybridity = (
    (1.0 / (1.0 + margin)) *
    (1.0 - spread)
)

# ============================================
# QUADRATIC OPTIMUM TEST
# ============================================

x = hybridity.reshape(-1, 1)

Xquad = np.concatenate([
    x,
    x**2
], axis=1)

model = LinearRegression()
model.fit(Xquad, stability)

pred = model.predict(Xquad)

r2 = r2_score(stability, pred)

linear_coef = model.coef_[0]
quad_coef = model.coef_[1]

# optimum location
if quad_coef != 0:
    optimum = -linear_coef / (2 * quad_coef)
else:
    optimum = np.nan

# ============================================
# PEARSON / SPEARMAN
# ============================================

r, p = pearsonr(hybridity, stability)
rs, _ = spearmanr(hybridity, stability)

# ============================================
# BAND TEST
# ============================================

q1 = np.quantile(hybridity, 0.33)
q2 = np.quantile(hybridity, 0.66)

low = stability[hybridity <= q1]
mid = stability[
    (hybridity > q1) &
    (hybridity <= q2)
]
high = stability[hybridity > q2]

# ============================================
# OPTIMALITY INDEX
# ============================================

optimality = (
    mid.mean()
    -
    0.5 * (
        low.mean() +
        high.mean()
    )
)

# ============================================
# VERDICT
# ============================================

if (
    quad_coef < 0 and
    r2 > 0.30 and
    optimality > 0.10
):
    verdict = "OPTIMAL-INTERFACE-BAND"

elif (
    quad_coef < 0 and
    optimality > 0.05
):
    verdict = "PARTIAL-INTERFACE-OPTIMUM"

else:
    verdict = "NONOPTIMAL-INTERFACE"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": systems,
    "stability": stability,
    "cluster": labels,
    "margin": margin,
    "spread": spread,
    "hybridity": hybridity,
    "predicted_stability": pred
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase539/phase539_optimal_band.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 539,
    "pearson_r": r,
    "pearson_p": p,
    "spearman_rho": rs,
    "quadratic_coef": quad_coef,
    "quadratic_r2": r2,
    "optimal_hybridity": optimum,
    "low_mean": low.mean(),
    "mid_mean": mid.mean(),
    "high_mean": high.mean(),
    "optimality_index": optimality,
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase539/phase539_summary.csv",
    index=False
)

print("\n=== PHASE 539 COMPLETE ===")
print(summary.to_string(index=False))
