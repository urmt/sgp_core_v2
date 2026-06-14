# PHASE 532 — PROJECTION-INTERNAL STABILITY LAW
# Test whether stability becomes nearly deterministic
# once projection identity itself is conditioned

import numpy as np
import pandas as pd
from itertools import combinations
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score
from scipy.stats import pearsonr

SEED = 532
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
# TEST ALL PROJECTIONS
# ============================================

projection_results = []

for r in range(2, 6):

    for combo in combinations(features, r):

        X = base[list(combo)].values
        X = StandardScaler().fit_transform(X)

        km = KMeans(
            n_clusters=6,
            random_state=SEED,
            n_init=50
        )

        labels = km.fit_predict(X)

        # ====================================
        # CLUSTER MEAN PREDICTION
        # ====================================

        pred = np.zeros(len(stability))

        for c in np.unique(labels):

            idx = labels == c

            pred[idx] = np.mean(
                stability[idx]
            )

        # ====================================
        # METRICS
        # ====================================

        corr, p = pearsonr(
            pred,
            stability
        )

        r2 = r2_score(
            stability,
            pred
        )

        within_var = []

        for c in np.unique(labels):

            idx = labels == c

            within_var.append(
                np.var(stability[idx])
            )

        mean_var = np.mean(within_var)

        projection_results.append({
            "projection": "+".join(combo),
            "corr": corr,
            "p": p,
            "r2": r2,
            "mean_cluster_variance": mean_var
        })

# ============================================
# AGGREGATE
# ============================================

proj = pd.DataFrame(projection_results)

best_idx = proj["r2"].idxmax()

best = proj.loc[best_idx]

mean_r2 = proj["r2"].mean()
std_r2 = proj["r2"].std()

mean_corr = proj["corr"].mean()

fraction_high = np.mean(
    proj["r2"] > 0.85
)

# ============================================
# VERDICT
# ============================================

if (
    fraction_high > 0.75 and
    mean_r2 > 0.80
):
    verdict = "PROJECTION-DETERMINISTIC-LAW"

elif (
    mean_r2 > 0.50
):
    verdict = "PARTIAL-PROJECTION-DETERMINISM"

else:
    verdict = "WEAK-PROJECTION-DEPENDENCE"

# ============================================
# SAVE
# ============================================

proj.to_csv(
    "/home/student/sgp_core_v2/phases/phase532/phase532_projection_scan.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 532,
    "mean_r2": mean_r2,
    "std_r2": std_r2,
    "mean_corr": mean_corr,
    "fraction_high_r2": fraction_high,
    "best_projection": best["projection"],
    "best_r2": best["r2"],
    "best_corr": best["corr"],
    "best_cluster_variance": best["mean_cluster_variance"],
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase532/phase532_summary.csv",
    index=False
)

print("\n=== PHASE 532 COMPLETE ===")
print(summary.to_string(index=False))
