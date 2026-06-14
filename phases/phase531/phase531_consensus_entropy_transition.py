# PHASE 531 — CONSENSUS-ENTROPY TRANSITION
# Test whether recursive stability is governed by
# balanced multi-cluster participation rather than
# rigid invariant membership

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from itertools import combinations
from collections import Counter

SEED = 531
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
# BUILD PROJECTION ASSIGNMENTS
# ============================================

assignments = []

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

        assignments.append(labels)

assignments = np.array(assignments)

# ============================================
# ENTROPY / PARTICIPATION METRICS
# ============================================

N = len(base)

entropy = np.zeros(N)
dominance = np.zeros(N)
participation = np.zeros(N)

for i in range(N):

    labs = assignments[:, i]

    counts = Counter(labs)

    probs = np.array(
        list(counts.values())
    ) / len(labs)

    entropy[i] = -np.sum(
        probs * np.log2(probs)
    )

    dominance[i] = probs.max()

    participation[i] = 1.0 / np.sum(probs**2)

# ============================================
# CONSENSUS DISPERSION
# ============================================

dispersion = entropy / np.max(entropy)

# ============================================
# CORRELATIONS
# ============================================

ent_corr, ent_p = pearsonr(
    entropy,
    stability
)

dom_corr, dom_p = pearsonr(
    dominance,
    stability
)

part_corr, part_p = pearsonr(
    participation,
    stability
)

rank_corr, _ = spearmanr(
    participation,
    stability
)

# ============================================
# GROUP TEST
# ============================================

q1 = np.quantile(participation, 0.33)
q2 = np.quantile(participation, 0.66)

low = stability[participation <= q1]
mid = stability[
    (participation > q1) &
    (participation <= q2)
]
high = stability[participation > q2]

# ============================================
# VERDICT
# ============================================

if (
    part_corr > 0.60 and
    dom_corr < -0.50
):
    verdict = "MULTIPARTICIPATION-LAW"

elif (
    part_corr > 0.35
):
    verdict = "PARTIAL-MULTIPARTICIPATION"

else:
    verdict = "RIGID-TAXONOMIC-STRUCTURE"

# ============================================
# SAVE
# ============================================

out = pd.DataFrame({
    "system": systems,
    "stability": stability,
    "entropy": entropy,
    "dominance": dominance,
    "participation": participation,
    "dispersion": dispersion
})

out.to_csv(
    "/home/student/sgp_core_v2/phases/phase531/phase531_entropy_structure.csv",
    index=False
)

summary = pd.DataFrame([{
    "phase": 531,
    "entropy_corr": ent_corr,
    "entropy_p": ent_p,
    "dominance_corr": dom_corr,
    "dominance_p": dom_p,
    "participation_corr": part_corr,
    "participation_p": part_p,
    "rank_corr": rank_corr,
    "low_group_mean": low.mean(),
    "mid_group_mean": mid.mean(),
    "high_group_mean": high.mean(),
    "verdict": verdict
}])

summary.to_csv(
    "/home/student/sgp_core_v2/phases/phase531/phase531_summary.csv",
    index=False
)

print("\n=== PHASE 531 COMPLETE ===")
print(summary.to_string(index=False))
