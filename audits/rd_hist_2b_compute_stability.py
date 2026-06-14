#!/usr/bin/env python3
"""
RD-HIST.2B — Compute Assignment Stability
"""

import json

# C1 assignments (from RD-HIST.2A)
c1_assignments = {
    "1": 2, "2": 1, "3": 2, "4": 3, "5": 1, "6": 5, "7": 4, "8": 4,
    "9": 1, "10": 4, "11": 2, "12": 3, "13": 5, "14": 5, "15": 3,
    "16": 1, "17": 2, "18": 2, "19": 3, "20": 4
}

# C2 assignments (from blind LLM clustering)
c2_assignments = {
    "1": 1, "2": 4, "3": 5, "4": 2, "5": 1, "6": 6, "7": 3, "8": 6,
    "9": 1, "10": 1, "11": 4, "12": 2, "13": 5, "14": 3, "15": 5,
    "16": 1, "17": 4, "18": 3, "19": 2, "20": 6
}

# C3 assignments (from randomized blind clustering)
c3_assignments = {
    "1": 5, "2": 6, "3": 5, "4": 4, "5": 6, "6": 5, "7": 4, "8": 1,
    "9": 2, "10": 5, "11": 5, "12": 3, "13": 3, "14": 1, "15": 2,
    "16": 3, "17": 6, "18": 4, "19": 4, "20": 1
}

# Study IDs for reference
study_ids = {
    "1": "T038", "2": "RD-10B.M5", "3": "T040", "4": "RD-5", "5": "RD-10B.J2",
    "6": "IF-3", "7": "RD-10B.J4", "8": "RD-10B.0", "9": "T043", "10": "RD-10B.R1",
    "11": "RD-10B.M6b", "12": "RD-019", "13": "IF-ST", "14": "RD-10B.J6",
    "15": "RD-06", "16": "RD-10B.3", "17": "RD-10B.R0R", "18": "RD-10B.R3b",
    "19": "RD-05", "20": "T042"
}

def compute_assignment_stability(a1, a2):
    """
    Compute assignment stability between two clusterings.
    Returns same_cluster_pairs / total_pairs
    """
    statements = list(a1.keys())
    total_pairs = 0
    same_cluster_pairs = 0
    
    for i in range(len(statements)):
        for j in range(i + 1, len(statements)):
            s1 = statements[i]
            s2 = statements[j]
            total_pairs += 1
            
            # Check if both statements are in the same cluster in both clusterings
            if a1[s1] == a1[s2] and a2[s1] == a2[s2]:
                same_cluster_pairs += 1
    
    return same_cluster_pairs / total_pairs if total_pairs > 0 else 0

def compute_category_count_stability(c1_count, c2_count, c3_count):
    """
    Compute category count stability.
    Returns max - min
    """
    counts = [c1_count, c2_count, c3_count]
    return max(counts) - min(counts)

def get_cluster_members(assignments, category):
    """Get all statements in a category"""
    return [s for s, c in assignments.items() if c == category]

# Compute assignment stability for each pair
c1_c2_stability = compute_assignment_stability(c1_assignments, c2_assignments)
c1_c3_stability = compute_assignment_stability(c1_assignments, c3_assignments)
c2_c3_stability = compute_assignment_stability(c2_assignments, c3_assignments)

# Compute category count stability
category_count_spread = compute_category_count_stability(5, 6, 6)

# Build the results
results = {
    "audit": "RD-HIST.2B",
    "analysis": "Assignment Stability",
    "description": "Primary metric: Did the same studies end up together?",
    "clusterings": {
        "c1": {
            "source": "RD-HIST.2A Human Clustering",
            "category_count": 5,
            "assignments": c1_assignments
        },
        "c2": {
            "source": "Blind LLM Clustering",
            "category_count": 6,
            "assignments": c2_assignments
        },
        "c3": {
            "source": "Randomized Blind Clustering",
            "category_count": 6,
            "assignments": c3_assignments
        }
    },
    "category_count_stability": {
        "c1_categories": 5,
        "c2_categories": 6,
        "c3_categories": 6,
        "spread": category_count_spread,
        "interpretation": "Moderate" if category_count_spread <= 3 else "Unstable"
    },
    "assignment_stability": {
        "c1_vs_c2": {
            "same_cluster_pairs": int(c1_c2_stability * 190),
            "total_pairs": 190,
            "stability": round(c1_c2_stability, 4),
            "interpretation": "High" if c1_c2_stability > 0.7 else "Moderate" if c1_c2_stability > 0.5 else "Low"
        },
        "c1_vs_c3": {
            "same_cluster_pairs": int(c1_c3_stability * 190),
            "total_pairs": 190,
            "stability": round(c1_c3_stability, 4),
            "interpretation": "High" if c1_c3_stability > 0.7 else "Moderate" if c1_c3_stability > 0.5 else "Low"
        },
        "c2_vs_c3": {
            "same_cluster_pairs": int(c2_c3_stability * 190),
            "total_pairs": 190,
            "stability": round(c2_c3_stability, 4),
            "interpretation": "High" if c2_c3_stability > 0.7 else "Moderate" if c2_c3_stability > 0.5 else "Low"
        }
    },
    "pairwise_assignments": {}
}

# Compute pairwise assignments for each statement
for s in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
          "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]:
    results["pairwise_assignments"][s] = {
        "study": study_ids[s],
        "c1": c1_assignments[s],
        "c2": c2_assignments[s],
        "c3": c3_assignments[s]
    }

# Save the results
with open('/home/student/sgp_core_v2/audits/RD_HIST_2B_ASSIGNMENT_STABILITY.json', 'w') as f:
    json.dump(results, f, indent=2)

# Print summary
print("=== Assignment Stability Results ===")
print(f"\nCategory Count Spread: {category_count_spread} (C1={5}, C2={6}, C3={6})")
print(f"Interpretation: {'High' if category_count_spread <= 1 else 'Moderate' if category_count_spread <= 3 else 'Unstable'}")
print(f"\nAssignment Stability:")
print(f"  C1 vs C2: {c1_c2_stability:.4f} ({int(c1_c2_stability * 190)}/190 pairs)")
print(f"  C1 vs C3: {c1_c3_stability:.4f} ({int(c1_c3_stability * 190)}/190 pairs)")
print(f"  C2 vs C3: {c2_c3_stability:.4f} ({int(c2_c3_stability * 190)}/190 pairs)")
print(f"\nOverall: {'High' if (c1_c2_stability + c1_c3_stability + c2_c3_stability) / 3 > 0.7 else 'Moderate' if (c1_c2_stability + c1_c3_stability + c2_c3_stability) / 3 > 0.5 else 'Low'}")
