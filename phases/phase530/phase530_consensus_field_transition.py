# PHASE 530 — CONSENSUS-FIELD TRANSITION
# Test whether stability is governed by
# global consensus embedding rather than
# local flexibility

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances
from itertools import combinations

SEED = 530
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
# BUILD CONSENSUS MATRIX
# ============================================

N = len(base)

consensus = np.zeros((N, N))

all_clusterings = []

for r in range(2, 6):

    for combo in combinations(features, r):

        X = base[list(combo)].values
        X = StandardScaler().fit_transform(X)

        km = KMeans(
            n_clusters=6,
            random_state=SEED,
            n_init=25
        )

        labels = km.fit_predict(X)

        all_clusterings.append(labels)

        for i in range(N):
            for j in range(N):

                if labels[i] == labels[j]:
                    consensus[i, j] += 1

consensus /= len(all_clusterings)

# ============================================
# CONSENSUS FIELD METRICS
# ============================================

mean_consensus = consensus.mean(axis=1)

consensus_entropy = np.zeros(N)

for i in range(N):

    row = consensus[i]

    p = row / row.sum()

    p = p[p > 0]

    consensus_entropy[i] = -np.sum(
        p * np.log2(p)
    )

# ============================================
# EMBEDDING DENSITY
# ============================================

dist = pairwise_distances(consensus)

density = np.exp(-dist).mean(axis=1)

# ============================================
# CORRELATIONS
# ============================================

mc_corr, mc_p = pearsonr(
    mean_consensus,
    stability
)

ent_corr, ent_p = pearsonr(
    consensus_entropy,
    stability
)

dens_corr, dens_p = pearsonr(
    density,
    stability
)

rank_corr, _ = spearmanr(
    density,
    stability
)

# ============================================
# VERDICT
# ============================================

if (
    mc_corr > 0.60 and
    dens_corr > 0.60
):
    verdict = "CONSENSUS-FIELD-LAW"

elif (
    mc_corr > 0.35 or
    dens_corr > 0.35
):
    verdict = "PARTIAL-CONSENSUS-STRUCTURE"

else:
    verdict = "NONCONSENSUS-ORGANIZATION"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": systems,
    "stability": stability,
    "mean_consensus": mean_consensus,
    "consensus_entropy": consensus_entropy,
    "density": density
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase530/phase530_consensus_field.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 530,
    "mean_consensus_corr": mc_corr,
    "mean_consensus_p": mc_p,
    "entropy_corr": ent_corr,
    "entropy_p": ent_p,
    "density_corr": dens_corr,
    "density_p": dens_p,
    "rank_corr": rank_corr,
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase530/phase530_summary.csv",
    index=False
)

print("\n=== PHASE 530 COMPLETE ===")
print(summary.to_string(index=False))
