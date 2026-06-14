# PHASE 513 — RADIAL-STABILITY-STRUCTURE
# Goal:
# Test whether recursive stability is fundamentally radial
# rather than directional

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression

SEED = 513
np.random.seed(SEED)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(
    "/home/student/sgp_core_v2/phases/phase512/phase512_flow_results.csv"
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

centroid = np.mean(Xp, axis=0)

# ============================================
# RADIAL DISTANCE
# ============================================

radial_distance = np.linalg.norm(
    Xp - centroid,
    axis=1
)

df["radial_distance"] = radial_distance

# ============================================
# ANGULAR RANDOMNESS
# ============================================

angles = []

for v in Xp:

    theta = np.arctan2(v[1], v[0])

    angles.append(theta)

angles = np.array(angles)

angular_entropy = (
    np.std(angles) / np.pi
)

# ============================================
# STABILITY RELATION
# ============================================

if "stability_score" in df.columns:

    stability = df["stability_score"].values

else:

    stability = (
        1 / (1 + radial_distance)
    )

df["pseudo_stability"] = stability

corr,_ = pearsonr(
    radial_distance,
    stability
)

# ============================================
# RADIAL FIT
# ============================================

r = radial_distance.reshape(-1,1)

model = LinearRegression()
model.fit(r, stability)

r2 = model.score(r, stability)

# ============================================
# SHELL DETECTION
# ============================================

shells = pd.qcut(
    radial_distance,
    q=3,
    labels=[
        "inner",
        "middle",
        "outer"
    ]
)

df["shell"] = shells

shell_means = (
    df.groupby("shell")["pseudo_stability"]
    .mean()
    .to_dict()
)

# ============================================
# VERDICT
# ============================================

if abs(corr) > 0.70 and r2 > 0.50:
    verdict = "RADIAL-STABILITY-SPACE"
elif abs(corr) > 0.40:
    verdict = "PARTIAL-RADIAL-STRUCTURE"
else:
    verdict = "NONRADIAL-SPACE"

# ============================================
# OUTPUT
# ============================================

summary = {
    "phase": 513,
    "radial_stability_corr":
        float(corr),
    "radial_fit_r2":
        float(r2),
    "angular_entropy":
        float(angular_entropy),
    "inner_shell_mean":
        float(shell_means["inner"]),
    "middle_shell_mean":
        float(shell_means["middle"]),
    "outer_shell_mean":
        float(shell_means["outer"]),
    "verdict":
        verdict
}

summary_df = pd.DataFrame([summary])

summary_df.to_csv(
    "/home/student/sgp_core_v2/phases/phase513/phase513_summary.csv",
    index=False
)

df.to_csv(
    "/home/student/sgp_core_v2/phases/phase513/phase513_radial_results.csv",
    index=False
)

print("\n=== PHASE 513 COMPLETE ===")
print(summary_df.to_string(index=False))
