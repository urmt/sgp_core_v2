# PHASE 524 — MINIMAL-CLUSTER-SIGNATURE
# Identify the minimal feature subset required
# to recover the 6-category stability taxonomy

import numpy as np
import pandas as pd
from itertools import combinations
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from scipy.stats import f_oneway

SEED = 524
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase523/phase523_cluster_identity.csv"
)

full_df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv"
)

features = [
    "CSR",
    "ADI",
    "RBS",
    "RTP",
    "SRD"
]

true_labels = df["cluster"].values

# ============================================
# BASELINE
# ============================================

X_full = full_df[features].values
X_full = StandardScaler().fit_transform(X_full)

# ============================================
# SEARCH
# ============================================

results = []

for r in range(1, len(features)+1):

    for combo in combinations(features, r):

        X = full_df[list(combo)].values

        X = StandardScaler().fit_transform(X)

        km = KMeans(
            n_clusters=6,
            random_state=SEED,
            n_init=25
        )

        pred = km.fit_predict(X)

        ari = adjusted_rand_score(
            true_labels,
            pred
        )

        # cluster variance
        vars_ = []

        for c in np.unique(pred):

            vals = full_df.iloc[
                np.where(pred == c)[0]
            ]["stability_score"].values

            vars_.append(np.var(vals))

        mean_var = np.mean(vars_)

        # ANOVA
        groups = [
            full_df.iloc[
                np.where(pred == c)[0]
            ]["stability_score"].values
            for c in np.unique(pred)
        ]

        F, p = f_oneway(*groups)

        results.append({
            "features": combo,
            "n_features": r,
            "ARI": ari,
            "mean_cluster_variance": mean_var,
            "anova_F": F,
            "anova_p": p
        })

# ============================================
# BEST MODEL
# ============================================

res_df = pd.DataFrame(results)

best = res_df.sort_values(
    by=["ARI", "anova_F"],
    ascending=False
).iloc[0]

# ============================================
# VERDICT
# ============================================

if (
    best["ARI"] > 0.90 and
    best["n_features"] <= 2
):
    verdict = "MINIMAL-SIGNATURE-LAW"

elif (
    best["ARI"] > 0.75
):
    verdict = "PARTIAL-SIGNATURE-REDUCTION"

else:
    verdict = "NONREDUCIBLE-CLUSTERING"

# ============================================
# SAVE
# ============================================

res_df.to_csv(
    "/home/student/sgp_core_v2/phases/phase524/phase524_feature_search.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 524,
    "best_features": str(best["features"]),
    "n_features": int(best["n_features"]),
    "best_ARI": best["ARI"],
    "best_anova_F": best["anova_F"],
    "best_anova_p": best["anova_p"],
    "mean_cluster_variance": best["mean_cluster_variance"],
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase524/phase524_summary.csv",
    index=False
)

print("\n=== PHASE 524 COMPLETE ===")
print(summary.to_string(index=False))
