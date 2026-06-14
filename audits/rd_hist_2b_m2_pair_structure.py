#!/usr/bin/env python3
"""
RD-HIST.2B.M2 — Pair Structure Audit

1. Cluster size distribution
2. Pair overlap matrix
3. Stable core detection
"""

import json
from collections import Counter, defaultdict
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

# Study ID mapping
study_ids = {
    "1": "T038", "2": "RD-10B.M5", "3": "T040", "4": "RD-5", "5": "RD-10B.J2",
    "6": "IF-3", "7": "RD-10B.J4", "8": "RD-10B.0", "9": "T043", "10": "RD-10B.R1",
    "11": "RD-10B.M6b", "12": "RD-019", "13": "IF-ST", "14": "RD-10B.J6",
    "15": "RD-06", "16": "RD-10B.3", "17": "RD-10B.R0R", "18": "RD-10B.R3b",
    "19": "RD-05", "20": "T042"
}

# ============================================================
# 1. Cluster size distribution
# ============================================================
def cluster_sizes(assignments):
    """Return sorted list of (cluster_id, size) tuples."""
    counts = Counter(assignments.values())
    return sorted(counts.items(), key=lambda x: -x[1])

c1_sizes = cluster_sizes(c1)
c2_sizes = cluster_sizes(c2)
c3_sizes = cluster_sizes(c3)

# ============================================================
# 2. Pair overlap matrix
# ============================================================
def pair_overlap(assignments_a, assignments_b, assignments_c):
    """Classify each pair by how many clusterings agree."""
    agreed_all3 = []
    agreed_exactly2 = []
    agreed_exactly1 = []
    agreed_none = []
    
    for i, s1 in enumerate(studies):
        for s2 in studies[i+1:]:
            same_a = assignments_a[s1] == assignments_a[s2]
            same_b = assignments_b[s1] == assignments_b[s2]
            same_c = assignments_c[s1] == assignments_c[s2]
            
            count = sum([same_a, same_b, same_c])
            
            if count == 3:
                agreed_all3.append((s1, s2))
            elif count == 2:
                agreed_exactly2.append((s1, s2))
            elif count == 1:
                agreed_exactly1.append((s1, s2))
            else:
                agreed_none.append((s1, s2))
    
    return agreed_all3, agreed_exactly2, agreed_exactly1, agreed_none

all3, exactly2, exactly1, none = pair_overlap(c1, c2, c3)

# ============================================================
# 3. Stable core detection
# ============================================================
def find_stable_cores(assignments_a, assignments_b, assignments_c):
    """Find groups of studies that always cluster together."""
    # Build "always together" relation
    always_together = {}
    for s in studies:
        always_together[s] = set()
    
    for i, s1 in enumerate(studies):
        for s2 in studies[i+1:]:
            same_a = assignments_a[s1] == assignments_a[s2]
            same_b = assignments_b[s1] == assignments_b[s2]
            same_c = assignments_c[s1] == assignments_c[s2]
            
            if same_a and same_b and same_c:
                always_together[s1].add(s2)
                always_together[s2].add(s1)
    
    # Find connected components (stable cores)
    visited = set()
    cores = []
    
    for s in studies:
        if s not in visited:
            core = {s}
            queue = list(always_together[s])
            while queue:
                neighbor = queue.pop()
                if neighbor not in visited:
                    visited.add(neighbor)
                    core.add(neighbor)
                    queue.extend(always_together[neighbor] - visited)
            
            if len(core) > 1:  # Only report cores with 2+ studies
                cores.append(sorted(core, key=lambda x: int(x)))
    
    return cores

stable_cores = find_stable_cores(c1, c2, c3)

# ============================================================
# Build results
# ============================================================
results = {
    "audit": "RD-HIST.2B.M2",
    "analysis": "Pair Structure Audit",
    "description": "Cluster size distribution, pair overlap, and stable core detection",
    "cluster_size_distribution": {
        "c1": [{"cluster": f"Cluster_{cid}", "size": size} for cid, size in c1_sizes],
        "c2": [{"cluster": f"Cluster_{cid}", "size": size} for cid, size in c2_sizes],
        "c3": [{"cluster": f"Cluster_{cid}", "size": size} for cid, size in c3_sizes]
    },
    "pair_overlap": {
        "agreed_all_3": len(all3),
        "agreed_exactly_2": len(exactly2),
        "agreed_exactly_1": len(exactly1),
        "agreed_none": len(none),
        "total_pairs": n * (n - 1) // 2,
        "agreed_all_3_pairs": [{"study_a": study_ids[s1], "study_b": study_ids[s2]} for s1, s2 in all3],
        "agreed_none_pairs": [{"study_a": study_ids[s1], "study_b": study_ids[s2]} for s1, s2 in none]
    },
    "stable_cores": [
        {
            "core_id": i + 1,
            "size": len(core),
            "studies": [study_ids[s] for s in core],
            "study_indices": core
        }
        for i, core in enumerate(stable_cores)
    ]
}

# Save results
with open('/home/student/sgp_core_v2/audits/RD_HIST_2B_M2_PAIR_STRUCTURE.json', 'w') as f:
    json.dump(results, f, indent=2)

# Print results
print("=" * 60)
print("RD-HIST.2B.M2 — Pair Structure Audit")
print("=" * 60)

print("\n--- 1. Cluster Size Distribution ---")
print(f"\nC1 (5 clusters):")
for item in results["cluster_size_distribution"]["c1"]:
    print(f"  {item['cluster']}: {item['size']}")
print(f"\nC2 (6 clusters):")
for item in results["cluster_size_distribution"]["c2"]:
    print(f"  {item['cluster']}: {item['size']}")
print(f"\nC3 (6 clusters):")
for item in results["cluster_size_distribution"]["c3"]:
    print(f"  {item['cluster']}: {item['size']}")

print("\n--- 2. Pair Overlap ---")
total_pairs = n * (n - 1) // 2
print(f"  Agreed by all 3:     {len(all3):4d} / {total_pairs} = {len(all3)/total_pairs:.4f}")
print(f"  Agreed by exactly 2: {len(exactly2):4d} / {total_pairs} = {len(exactly2)/total_pairs:.4f}")
print(f"  Agreed by exactly 1: {len(exactly1):4d} / {total_pairs} = {len(exactly1)/total_pairs:.4f}")
print(f"  Agreed by none:      {len(none):4d} / {total_pairs} = {len(none)/total_pairs:.4f}")

print("\n--- 3. Stable Cores (study pairs always together) ---")
if len(stable_cores) == 0:
    print("  No stable cores found.")
else:
    for core in results["stable_cores"]:
        print(f"  Core {core['core_id']} ({core['size']} studies): {', '.join(core['studies'])}")
