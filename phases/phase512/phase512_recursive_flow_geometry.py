# PHASE 512 — RECURSIVE-FLOW-GEOMETRY
# Goal:
# Determine whether recursive systems evolve along
# coherent flow directions inside the flat manifold

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import pearsonr

SEED = 512
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase511/phase511_curvature_results.csv"
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
# PCA FLOW SPACE
# ============================================

pca = PCA(n_components=3)
Xp = pca.fit_transform(X)

df["PC1"] = Xp[:,0]
df["PC2"] = Xp[:,1]
df["PC3"] = Xp[:,2]

# ============================================
# FLOW VECTOR FIELD
# ============================================

centroid = np.mean(Xp, axis=0)

flow_vectors = []
flow_magnitudes = []

for i in range(len(Xp)):

    vec = centroid - Xp[i]

    mag = np.linalg.norm(vec)

    if mag > 0:
        vec = vec / mag

    flow_vectors.append(vec)
    flow_magnitudes.append(mag)

flow_vectors = np.array(flow_vectors)

df["flow_mag"] = flow_magnitudes

# ============================================
# FLOW COHERENCE
# ============================================

pairwise_alignment = []

for i in range(len(flow_vectors)):
    for j in range(i+1, len(flow_vectors)):

        c = np.dot(
            flow_vectors[i],
            flow_vectors[j]
        )

        pairwise_alignment.append(c)

mean_alignment = np.mean(pairwise_alignment)

# ============================================
# FLOW-STABILITY RELATION
# ============================================

if "stability_score" in df.columns:

    corr,_ = pearsonr(
        df["flow_mag"],
        df["stability_score"]
    )

else:
    corr = np.nan

# ============================================
# FLOW REGIMES
# ============================================

df["flow_regime"] = pd.cut(
    df["flow_mag"],
    bins=3,
    labels=[
        "core",
        "intermediate",
        "peripheral"
    ]
)

# ============================================
# VERDICT
# ============================================

if mean_alignment > 0.85:
    verdict = "COHERENT-FLOW-SPACE"
elif mean_alignment > 0.50:
    verdict = "PARTIAL-FLOW-COHERENCE"
else:
    verdict = "DISORDERED-FLOW-SPACE"

# ============================================
# OUTPUT
# ============================================

summary = {
    "phase": 512,
    "mean_flow_alignment":
        float(mean_alignment),
    "mean_flow_magnitude":
        float(np.mean(flow_magnitudes)),
    "max_flow_magnitude":
        float(np.max(flow_magnitudes)),
    "flow_stability_corr":
        None if np.isnan(corr) else float(corr),
    "verdict":
        verdict
}

summary_df = pd.DataFrame([summary])

summary_df.to_csv(
    "/home/student/sgp_core_v2/phases/phase512/phase512_summary.csv",
    index=False
)

df.to_csv(
    "/home/student/sgp_core_v2/phases/phase512/phase512_flow_results.csv",
    index=False
)

print("\n=== PHASE 512 COMPLETE ===")
print(summary_df.to_string(index=False))
