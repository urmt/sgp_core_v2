# PHASE 511 — RECURSIVE-MANIFOLD-CURVATURE
# Goal:
# Detect whether recursive stability regimes are separated by
# curved basin geometry and bifurcation boundaries

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr

SEED = 511
np.random.seed(SEED)

# ============================================
# LOAD DATA
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase510/phase510_full_results.csv"
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
# PCA EMBEDDING
# ============================================

pca = PCA(n_components=3)
Xp = pca.fit_transform(X)

# ============================================
# LOCAL CURVATURE ESTIMATION
# ============================================

nbrs = NearestNeighbors(
    n_neighbors=6
).fit(Xp)

distances, indices = nbrs.kneighbors(Xp)

curvature = []

for i in range(len(Xp)):

    local_pts = Xp[indices[i]]

    cov = np.cov(local_pts.T)

    eig = np.linalg.eigvalsh(cov)

    eig = np.sort(eig)[::-1]

    if eig[0] > 0:
        kappa = eig[2] / eig[0]
    else:
        kappa = 0

    curvature.append(kappa)

df["curvature"] = curvature

# ============================================
# BASIN DETECTION
# ============================================

threshold = np.percentile(curvature, 75)

df["high_curvature"] = (
    df["curvature"] >= threshold
).astype(int)

# ============================================
# TRANSITION DETECTION
# ============================================

transition_scores = []

for i in range(len(Xp)):

    d = np.linalg.norm(
        Xp[i] - np.mean(Xp, axis=0)
    )

    score = d * curvature[i]

    transition_scores.append(score)

df["transition_score"] = transition_scores

# ============================================
# STABILITY RELATION
# ============================================

if "stability_score" in df.columns:

    corr,_ = pearsonr(
        df["transition_score"],
        df["stability_score"]
    )

else:
    corr = np.nan

# ============================================
# BASIN COUNT
# ============================================

basins = (
    df["high_curvature"]
    .value_counts()
    .to_dict()
)

# ============================================
# VERDICT
# ============================================

mean_curv = np.mean(curvature)

if mean_curv < 0.08:
    verdict = "FLAT-MANIFOLD"
elif mean_curv < 0.20:
    verdict = "CURVED-STABILITY-MANIFOLD"
else:
    verdict = "HIGHLY-BIFURCATING-MANIFOLD"

# ============================================
# OUTPUT
# ============================================

summary = {
    "phase": 511,
    "mean_curvature": float(mean_curv),
    "max_curvature": float(np.max(curvature)),
    "transition_stability_corr":
        None if np.isnan(corr) else float(corr),
    "high_curvature_count":
        int(np.sum(df["high_curvature"])),
    "verdict": verdict
}

summary_df = pd.DataFrame([summary])

summary_df.to_csv(
    "/home/student/sgp_core_v2/phases/phase511/phase511_summary.csv",
    index=False
)

df.to_csv(
    "/home/student/sgp_core_v2/phases/phase511/phase511_curvature_results.csv",
    index=False
)

print("\n=== PHASE 511 COMPLETE ===")
print(summary_df.to_string(index=False))
