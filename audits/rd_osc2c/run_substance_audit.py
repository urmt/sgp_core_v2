#!/usr/bin/env python3
"""RD-OSC.2C: Substance Agreement Audit (corrected permutation test)

Quantifies substance agreement without using labels.
Computes semantic similarity matrices, compares within-study vs between-study,
and runs permutation test with correct shuffling.
"""

import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

# Load data
with open('audits/rd_osc2b/coder_A_responses.json') as f:
    cA = json.load(f)
with open('audits/rd_osc2b/coder_B_responses.json') as f:
    cB = json.load(f)
with open('audits/rd_osc2b/coder_C_responses.json') as f:
    cC = json.load(f)
with open('audits/rd_osc2b/blind_packets_shuffled.json') as f:
    packets = json.load(f)

# Extract all 60 responses
responses = []
study_ids = []
for i in range(20):
    responses.append(cA[i]['what_changed'])
    study_ids.append(i)
    responses.append(cB[i]['what_changed'])
    study_ids.append(i)
    responses.append(cC[i]['what_changed'])
    study_ids.append(i)

# TF-IDF embedding
vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
tfidf_matrix = vectorizer.fit_transform(responses)

# Compute full similarity matrix
sim_matrix = cosine_similarity(tfidf_matrix)

# Extract within-study similarities (actual pairings)
within_sims = []
for i in range(20):
    idx_a = i * 3
    idx_b = i * 3 + 1
    idx_c = i * 3 + 2
    sim_ab = sim_matrix[idx_a, idx_b]
    sim_ac = sim_matrix[idx_a, idx_c]
    sim_bc = sim_matrix[idx_b, idx_c]
    within_sims.extend([sim_ab, sim_ac, sim_bc])

# Extract between-study similarities (different studies, any coders)
between_sims = []
for i in range(20):
    for j in range(i + 1, 20):
        for ci in range(3):
            for cj in range(3):
                idx_i = i * 3 + ci
                idx_j = j * 3 + cj
                between_sims.append(sim_matrix[idx_i, idx_j])

within_sims = np.array(within_sims)
between_sims = np.array(between_sims)

# Basic statistics
within_mean = within_sims.mean()
within_std = within_sims.std()
between_mean = between_sims.mean()
between_std = between_sims.std()

# Effect size (Cohen's d)
pooled_std = np.sqrt((within_std**2 + between_std**2) / 2)
cohens_d = (within_mean - between_mean) / pooled_std

# CORRECTED Permutation test
# Shuffle which responses are grouped together (not labels)
n_permutations = 10000
perm_diffs = []
observed_diff = within_mean - between_mean

for _ in range(n_permutations):
    # Randomly assign 60 responses to 20 groups of 3
    indices = list(range(60))
    random.shuffle(indices)
    
    perm_within = []
    for g in range(20):
        idx1 = indices[g * 3]
        idx2 = indices[g * 3 + 1]
        idx3 = indices[g * 3 + 2]
        perm_within.append(sim_matrix[idx1, idx2])
        perm_within.append(sim_matrix[idx1, idx3])
        perm_within.append(sim_matrix[idx2, idx3])
    
    perm_within = np.array(perm_within)
    perm_diffs.append(perm_within.mean() - between_mean)

perm_diffs = np.array(perm_diffs)
p_value = (perm_diffs >= observed_diff).mean()

# Confidence interval for within-study similarity
n_within = len(within_sims)
se_within = within_std / np.sqrt(n_within)
ci_95 = (within_mean - 1.96 * se_within, within_mean + 1.96 * se_within)

# Write results
results = {
    "summary": {
        "within_study_mean": float(within_mean),
        "within_study_std": float(within_std),
        "between_study_mean": float(between_mean),
        "between_study_std": float(between_std),
        "difference": float(observed_diff),
        "cohens_d": float(cohens_d),
        "p_value": float(p_value),
        "ci_95_lower": float(ci_95[0]),
        "ci_95_upper": float(ci_95[1]),
        "n_permutations": n_permutations
    },
    "per_study": []
}

for i in range(20):
    idx_a = i * 3
    idx_b = i * 3 + 1
    idx_c = i * 3 + 2
    results["per_study"].append({
        "study": packets[i]['blind_id'],
        "sim_ab": float(sim_matrix[idx_a, idx_b]),
        "sim_ac": float(sim_matrix[idx_a, idx_c]),
        "sim_bc": float(sim_matrix[idx_b, idx_c]),
        "mean": float((sim_matrix[idx_a, idx_b] + sim_matrix[idx_a, idx_c] + sim_matrix[idx_b, idx_c]) / 3)
    })

with open('audits/rd_osc2c/substance_agreement_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Print summary
print("=== RD-OSC.2C: Substance Agreement Audit (Corrected) ===")
print()
print(f"Within-study similarity:  {within_mean:.4f} ± {within_std:.4f}")
print(f"Between-study similarity: {between_mean:.4f} ± {between_std:.4f}")
print(f"Difference:               {observed_diff:.4f}")
print(f"Effect size (Cohen's d):  {cohens_d:.4f}")
print(f"95% CI for within-study:  ({ci_95[0]:.4f}, {ci_95[1]:.4f})")
print(f"Permutation p-value:      {p_value:.6f}")
print(f"Permutation mean diff:    {perm_diffs.mean():.4f}")
print()
if p_value < 0.001:
    print("RESULT: Within-study similarity is SIGNIFICANTLY greater than random (p < 0.001)")
elif p_value < 0.01:
    print("RESULT: Within-study similarity is SIGNIFICANTLY greater than random (p < 0.01)")
elif p_value < 0.05:
    print("RESULT: Within-study similarity is SIGNIFICANTLY greater than random (p < 0.05)")
else:
    print(f"RESULT: Within-study similarity is NOT significantly greater than random (p = {p_value:.4f})")
print()
print("=== Per-Study Breakdown ===")
for p in results["per_study"]:
    print(f"  {p['study']}: mean={p['mean']:.4f} (A-B={p['sim_ab']:.4f}, A-C={p['sim_ac']:.4f}, B-C={p['sim_bc']:.4f})")
