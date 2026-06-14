#!/usr/bin/env python3
"""
RD-HIST.2B.M1 — Stability Metric Audit

Compute five different clustering agreement metrics for C1, C2, C3.
No interpretation. Only metric validation.
"""

import json
import math
from collections import Counter
from itertools import combinations

# Load assignments
with open('/home/student/sgp_core_v2/audits/RD_HIST_2B_C1_HUMAN.json') as f:
    c1_data = json.load(f)
with open('/home/student/sgp_core_v2/audits/RD_HIST_2B_C2_LLM.json') as f:
    c2_data = json.load(f)
with open('/home/student/sgp_core_v2/audits/RD_HIST_2B_C3_RANDOM.json') as f:
    c3_data = json.load(f)

c1 = c1_data["assignments"]
c2 = c2_data["assignments"]
c3 = c3_data["assignments"]

studies = sorted(c1.keys(), key=lambda x: int(x))
n = len(studies)

def get_pair_set(assignments):
    """Get set of all pairs that are in the same cluster."""
    pairs = set()
    for i, s1 in enumerate(studies):
        for s2 in studies[i+1:]:
            if assignments[s1] == assignments[s2]:
                pairs.add((s1, s2))
    return pairs

def get_contingency(assignments_a, assignments_b):
    """Build contingency table for ARI/NMI."""
    # Get cluster labels
    clusters_a = sorted(set(assignments_a.values()))
    clusters_b = sorted(set(assignments_b.values()))
    
    # Build contingency table
    contingency = {}
    for ca in clusters_a:
        for cb in clusters_b:
            count = sum(1 for s in studies if assignments_a[s] == ca and assignments_b[s] == cb)
            contingency[(ca, cb)] = count
    
    return contingency, clusters_a, clusters_b

# ============================================================
# METRIC A: same_cluster_pairs / total_pairs (current, flawed)
# ============================================================
def metric_a(assignments_a, assignments_b):
    """Current metric: fraction of all pairs that are together in both clusterings."""
    total_pairs = n * (n - 1) // 2
    together_both = 0
    for i, s1 in enumerate(studies):
        for s2 in studies[i+1:]:
            if assignments_a[s1] == assignments_a[s2] and assignments_b[s1] == assignments_b[s2]:
                together_both += 1
    return together_both / total_pairs

# ============================================================
# METRIC B: Jaccard similarity on pair sets
# ============================================================
def metric_b(assignments_a, assignments_b):
    """Jaccard similarity: |intersection| / |union| of pair sets."""
    pairs_a = get_pair_set(assignments_a)
    pairs_b = get_pair_set(assignments_b)
    
    intersection = pairs_a & pairs_b
    union = pairs_a | pairs_b
    
    return len(intersection) / len(union) if len(union) > 0 else 0

# ============================================================
# METRIC C: Adjusted Rand Index
# ============================================================
def metric_c(assignments_a, assignments_b):
    """Adjusted Rand Index (corrected for chance)."""
    contingency, clusters_a, clusters_b = get_contingency(assignments_a, assignments_b)
    
    # Sum of n_ij^2
    sum_nij_sq = sum(v**2 for v in contingency.values())
    
    # Sum of a_i^2 and b_j^2
    sum_ai_sq = sum(sum(contingency[(ca, cb)] for cb in clusters_b)**2 for ca in clusters_a)
    sum_bj_sq = sum(sum(contingency[(ca, cb)] for ca in clusters_a)**2 for cb in clusters_b)
    
    # Expected index
    expected = (sum_ai_sq * sum_bj_sq) / (n * (n - 1) / 2) if n > 1 else 0
    
    # Max index
    max_index = 0.5 * (sum_ai_sq + sum_bj_sq)
    
    # ARI
    if max_index - expected == 0:
        return 0.0
    
    ari = (sum_nij_sq - expected) / (max_index - expected)
    return ari

# ============================================================
# METRIC D: Normalized Mutual Information
# ============================================================
def entropy(assignments):
    """Compute entropy H(X)."""
    counts = Counter(assignments.values())
    n = len(assignments)
    h = 0.0
    for count in counts.values():
        if count > 0:
            p = count / n
            h -= p * math.log2(p)
    return h

def mutual_information(assignments_a, assignments_b):
    """Compute mutual information I(X;Y)."""
    contingency, clusters_a, clusters_b = get_contingency(assignments_a, assignments_b)
    n = len(assignments_a)
    
    mi = 0.0
    for ca in clusters_a:
        for cb in clusters_b:
            nij = contingency[(ca, cb)]
            if nij > 0:
                ai = sum(contingency[(ca, cb2)] for cb2 in clusters_b)
                bj = sum(contingency[(ca2, cb)] for ca2 in clusters_a)
                mi += (nij / n) * math.log2((n * nij) / (ai * bj))
    return mi

def metric_d(assignments_a, assignments_b):
    """Normalized Mutual Information: I(X;Y) / sqrt(H(X) * H(Y))."""
    h_a = entropy(assignments_a)
    h_b = entropy(assignments_b)
    mi = mutual_information(assignments_a, assignments_b)
    
    if h_a == 0 or h_b == 0:
        return 0.0
    
    return mi / math.sqrt(h_a * h_b)

# ============================================================
# METRIC E: Variation of Information
# ============================================================
def metric_e(assignments_a, assignments_b):
    """Variation of Information: VI(X,Y) = H(X|Y) + H(Y|X) = H(X) + H(Y) - 2*I(X;Y)."""
    h_a = entropy(assignments_a)
    h_b = entropy(assignments_b)
    mi = mutual_information(assignments_a, assignments_b)
    
    return h_a + h_b - 2 * mi

# ============================================================
# Compute all metrics for all pairs
# ============================================================
pairs = [("c1", "c2", c1, c2), ("c1", "c3", c1, c3), ("c2", "c3", c2, c3)]

results = {
    "audit": "RD-HIST.2B.M1",
    "analysis": "Stability Metric Audit",
    "description": "Metric validation: are the reported stability values properties of the clusterings or artifacts of the metric?",
    "metrics": {},
    "pair_results": {}
}

for name_a, name_b, a, b in pairs:
    key = f"{name_a}_vs_{name_b}"
    results["pair_results"][key] = {
        "metric_a_current": round(metric_a(a, b), 4),
        "metric_b_jaccard": round(metric_b(a, b), 4),
        "metric_c_ari": round(metric_c(a, b), 4),
        "metric_d_nmi": round(metric_d(a, b), 4),
        "metric_e_vi": round(metric_e(a, b), 4)
    }

# Compute interpretation for each metric
results["interpretation"] = {
    "metric_a": "Low" if results["pair_results"]["c1_vs_c2"]["metric_a_current"] < 0.3 else "Moderate" if results["pair_results"]["c1_vs_c2"]["metric_a_current"] < 0.6 else "High",
    "metric_b": "Low" if results["pair_results"]["c1_vs_c2"]["metric_b_jaccard"] < 0.3 else "Moderate" if results["pair_results"]["c1_vs_c2"]["metric_b_jaccard"] < 0.6 else "High",
    "metric_c": "Low" if results["pair_results"]["c1_vs_c2"]["metric_c_ari"] < 0.3 else "Moderate" if results["pair_results"]["c1_vs_c2"]["metric_c_ari"] < 0.6 else "High",
    "metric_d": "Low" if results["pair_results"]["c1_vs_c2"]["metric_d_nmi"] < 0.3 else "Moderate" if results["pair_results"]["c1_vs_c2"]["metric_d_nmi"] < 0.6 else "High",
    "metric_e_vi": "High (more different)" if results["pair_results"]["c1_vs_c2"]["metric_e_vi"] > 2.0 else "Moderate" if results["pair_results"]["c1_vs_c2"]["metric_e_vi"] > 1.0 else "Low (more similar)"
}

# Save results
with open('/home/student/sgp_core_v2/audits/RD_HIST_2B_M1_METRIC_AUDIT.json', 'w') as f:
    json.dump(results, f, indent=2)

# Print results
print("=" * 60)
print("RD-HIST.2B.M1 — Stability Metric Audit")
print("=" * 60)

print("\n--- Raw Values ---")
for key, values in results["pair_results"].items():
    print(f"\n{key}:")
    print(f"  A (current):     {values['metric_a_current']:.4f}")
    print(f"  B (Jaccard):     {values['metric_b_jaccard']:.4f}")
    print(f"  C (ARI):         {values['metric_c_ari']:.4f}")
    print(f"  D (NMI):         {values['metric_d_nmi']:.4f}")
    print(f"  E (VI):          {values['metric_e_vi']:.4f}")

print("\n--- Interpretation Scale ---")
print("A (current): 0-0.3 Low, 0.3-0.6 Moderate, 0.6-1.0 High")
print("B (Jaccard): 0-0.3 Low, 0.3-0.6 Moderate, 0.6-1.0 High")
print("C (ARI):     0-0.3 Low, 0.3-0.6 Moderate, 0.6-1.0 High")
print("D (NMI):     0-0.3 Low, 0.3-0.6 Moderate, 0.6-1.0 High")
print("E (VI):      0-1.0 Low (similar), 1.0-2.0 Moderate, 2.0+ High (different)")

print("\n--- Do all metrics agree? ---")
for key, values in results["pair_results"].items():
    a_level = "Low" if values["metric_a_current"] < 0.3 else "Mod" if values["metric_a_current"] < 0.6 else "High"
    b_level = "Low" if values["metric_b_jaccard"] < 0.3 else "Mod" if values["metric_b_jaccard"] < 0.6 else "High"
    c_level = "Low" if values["metric_c_ari"] < 0.3 else "Mod" if values["metric_c_ari"] < 0.6 else "High"
    d_level = "Low" if values["metric_d_nmi"] < 0.3 else "Mod" if values["metric_d_nmi"] < 0.6 else "High"
    e_level = "High" if values["metric_e_vi"] > 2.0 else "Mod" if values["metric_e_vi"] > 1.0 else "Low"
    
    all_low = (a_level == "Low" and b_level == "Low" and c_level == "Low" and d_level == "Low" and e_level == "High")
    print(f"\n{key}:")
    print(f"  A={a_level} B={b_level} C={c_level} D={d_level} E(VI)={e_level}")
    if all_low:
        print(f"  ALL METRICS AGREE: stability is low")
    else:
        print(f"  METRICS DISAGREE: some indicate moderate/high agreement")
