# PHASE 510 — RECURSIVE STATE-SPACE GEOMETRY
# Goal:
# Replace failed single-invariant search with coupled stability manifold analysis

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

SEED = 510
np.random.seed(SEED)

# ============================================
# LOAD PHASE 507/508/509 DATA
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase509/phase509_results.csv"
)

# ============================================
# REQUIRED FEATURES
# ============================================

features = [
    "CSR",   # coherence survival ratio
    "ADI",   # asymmetry dependence index
    "RBS",   # recursive balance strength
    "RTP",   # recursive transport persistence
    "SRD"    # signature retention decay
]

X = df[features].values
X = StandardScaler().fit_transform(X)

labels = df["class"].values

# ============================================
# PCA GEOMETRY
# ============================================

pca = PCA(n_components=5)
Xp = pca.fit_transform(X)

explained = pca.explained_variance_ratio_

print("\n=== PCA EXPLAINED VARIANCE ===")
for i,v in enumerate(explained):
    print(f"PC{i+1}: {v:.4f}")

# ============================================
# STATE-SPACE CLUSTERING
# ============================================

clusterer = DBSCAN(
    eps=0.85,
    min_samples=3
)

clusters = clusterer.fit_predict(Xp[:,:3])

valid = len(set(clusters)) > 1 and -1 not in set(clusters)

if valid:
    sil = silhouette_score(Xp[:,:3], clusters)
else:
    sil = -1

print("\n=== CLUSTERING ===")
print("clusters:", len(set(clusters)))
print("silhouette:", sil)

# ============================================
# STABILITY MANIFOLD TEST
# ============================================

# define recursive stability manifold radius

center = np.mean(Xp[:,:3], axis=0)

distances = np.linalg.norm(Xp[:,:3] - center, axis=1)

df["manifold_distance"] = distances

# compare against stability

if "stability_score" in df.columns:
    corr,_ = pearsonr(
        df["manifold_distance"],
        df["stability_score"]
    )
else:
    corr = np.nan

print("\n=== MANIFOLD RELATION ===")
print("distance ↔ stability corr:", corr)

# ============================================
# DEFORMATION TRAJECTORY TEST
# ============================================

if "perturbation_depth" in df.columns:

    traj = []

    for sys in df["system"].unique():

        sub = df[df["system"] == sys]

        sub = sub.sort_values("perturbation_depth")

        d = sub["manifold_distance"].values

        if len(d) > 2:

            slope = np.mean(np.diff(d))

            traj.append({
                "system": sys,
                "trajectory_slope": slope
            })

    traj_df = pd.DataFrame(traj)

    print("\n=== TRAJECTORY SLOPES ===")
    print(traj_df)

# ============================================
# CLASSIFICATION
# ============================================

if explained[0] > 0.9:
    verdict = "RANK1-DOMINATED"
elif explained[:3].sum() > 0.85:
    verdict = "LOW-DIMENSIONAL-MANIFOLD"
else:
    verdict = "HIGH-DIMENSIONAL-STATE-SPACE"

print("\n=== VERDICT ===")
print(verdict)

# ============================================
# SAVE
# ============================================

out = {
    "phase": 510,
    "explained_variance": explained.tolist(),
    "silhouette": float(sil),
    "distance_stability_corr": (
        None if np.isnan(corr) else float(corr)
    ),
    "verdict": verdict
}

pd.DataFrame([out]).to_csv(
    "/home/student/sgp_core_v2/phases/phase510/phase510_summary.csv",
    index=False
)

print("\nPhase 510 complete.")
