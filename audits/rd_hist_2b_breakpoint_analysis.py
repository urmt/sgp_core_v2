#!/usr/bin/env python3
"""
RD-HIST.2B — Breakpoint Analysis
"""

import json

# Category assignments for each clustering
c1_assignments = {
    "1": 2, "2": 1, "3": 2, "4": 3, "5": 1, "6": 5, "7": 4, "8": 4,
    "9": 1, "10": 4, "11": 2, "12": 3, "13": 5, "14": 5, "15": 3,
    "16": 1, "17": 2, "18": 2, "19": 3, "20": 4
}

c2_assignments = {
    "1": 1, "2": 4, "3": 5, "4": 2, "5": 1, "6": 6, "7": 3, "8": 6,
    "9": 1, "10": 1, "11": 4, "12": 2, "13": 5, "14": 3, "15": 5,
    "16": 1, "17": 4, "18": 3, "19": 2, "20": 6
}

c3_assignments = {
    "1": 5, "2": 6, "3": 5, "4": 4, "5": 6, "6": 5, "7": 4, "8": 1,
    "9": 2, "10": 5, "11": 5, "12": 3, "13": 3, "14": 1, "15": 2,
    "16": 3, "17": 6, "18": 4, "19": 4, "20": 1
}

# Q3 responses for reference
q3_responses = {
    "1": "Universes were generated with continuous dynamics and the emergence of separable clusters was measured.",
    "2": "Audits were classified by whether descriptions collapsed or were maintained, and gain was compared.",
    "3": "Ten candidates were tested and all required separation.",
    "4": "Removal fraction was varied and recovery metrics were measured.",
    "5": "Multiple sequences were generated and the same four features appeared in all of them.",
    "6": "A co-occurrence matrix was built, noise was filtered, and clustering was applied.",
    "7": "Each junction was removed and the effect on the others was measured.",
    "8": "One world was represented in multiple ways and the same detectors were applied to each.",
    "9": "Universes were generated and detectors were applied to determine which appeared first.",
    "10": "The study sequence was re-read and the timing of gain relative to interaction was recorded.",
    "11": "Comparisons were classified by type and collapse rates were measured.",
    "12": "Box width was varied and the effect on packing structure and outcome was measured.",
    "13": "Reconstruction was tested under four degradation conditions and breakpoints were identified.",
    "14": "Each junction was expressed as an operator and composition was tested.",
    "15": "Pre-perturbation level was measured and its predictive power for recovery was tested.",
    "16": "Worlds were generated without pattern vocabulary and patterns were detected after evolution.",
    "17": "A classification scheme was applied to prior studies, separating them into two groups based on what remained stable.",
    "18": "Audits were decomposed by type and the contribution of each component was analyzed.",
    "19": "Removal fraction was varied and recovery metrics were measured.",
    "20": "Universes were analyzed for proximity structure and the chain was tested."
}

def find_breakpoints(assignments):
    """
    Find breakpoints: boundaries between clusters.
    Returns list of breakpoint positions.
    """
    statements = sorted(assignments.keys(), key=lambda x: int(x))
    breakpoints = []
    
    for i in range(len(statements) - 1):
        current = statements[i]
        next_s = statements[i + 1]
        
        # Check if current and next are in different clusters
        if assignments[current] != assignments[next_s]:
            breakpoints.append({
                "position": i + 1,
                "between": (current, next_s),
                "cluster_boundary": (assignments[current], assignments[next_s])
            })
    
    return breakpoints

def compute_breakpoint_similarity(bp1, bp2):
    """
    Compute similarity between breakpoint sets.
    Returns Jaccard similarity.
    """
    set1 = {tuple(sorted(bp["between"])) for bp in bp1}
    set2 = {tuple(sorted(bp["between"])) for bp in bp2}
    
    intersection = set1 & set2
    union = set1 | set2
    
    return len(intersection) / len(union) if len(union) > 0 else 0

# Find breakpoints for each clustering
c1_breakpoints = find_breakpoints(c1_assignments)
c2_breakpoints = find_breakpoints(c2_assignments)
c3_breakpoints = find_breakpoints(c3_assignments)

# Compute breakpoint similarity
c1_c2_similarity = compute_breakpoint_similarity(c1_breakpoints, c2_breakpoints)
c1_c3_similarity = compute_breakpoint_similarity(c1_breakpoints, c3_breakpoints)
c2_c3_similarity = compute_breakpoint_similarity(c2_breakpoints, c3_breakpoints)

# Build the results
results = {
    "audit": "RD-HIST.2B",
    "analysis": "Breakpoint Analysis",
    "description": "Where do clusterings disagree?",
    "breakpoints": {
        "c1": {
            "count": len(c1_breakpoints),
            "breakpoints": c1_breakpoints
        },
        "c2": {
            "count": len(c2_breakpoints),
            "breakpoints": c2_breakpoints
        },
        "c3": {
            "count": len(c3_breakpoints),
            "breakpoints": c3_breakpoints
        }
    },
    "breakpoint_similarity": {
        "c1_vs_c2": {
            "jaccard_similarity": round(c1_c2_similarity, 4),
            "interpretation": "High" if c1_c2_similarity > 0.7 else "Moderate" if c1_c2_similarity > 0.5 else "Low"
        },
        "c1_vs_c3": {
            "jaccard_similarity": round(c1_c3_similarity, 4),
            "interpretation": "High" if c1_c3_similarity > 0.7 else "Moderate" if c1_c3_similarity > 0.5 else "Low"
        },
        "c2_vs_c3": {
            "jaccard_similarity": round(c2_c3_similarity, 4),
            "interpretation": "High" if c2_c3_similarity > 0.7 else "Moderate" if c2_c3_similarity > 0.5 else "Low"
        }
    },
    "disagreements": []
}

# Find disagreements
for s in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
          "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]:
    if c1_assignments[s] != c2_assignments[s] or c1_assignments[s] != c3_assignments[s]:
        results["disagreements"].append({
            "study": s,
            "c1": c1_assignments[s],
            "c2": c2_assignments[s],
            "c3": c3_assignments[s],
            "q3": q3_responses[s]
        })

with open('/home/student/sgp_core_v2/audits/RD_HIST_2B_BREAKPOINT_ANALYSIS.json', 'w') as f:
    json.dump(results, f, indent=2)

print("=== Breakpoint Analysis Results ===")
print(f"\nBreakpoints:")
print(f"  C1: {len(c1_breakpoints)} breakpoints")
print(f"  C2: {len(c2_breakpoints)} breakpoints")
print(f"  C3: {len(c3_breakpoints)} breakpoints")
print(f"\nBreakpoint Similarity:")
print(f"  C1 vs C2: {c1_c2_similarity:.4f}")
print(f"  C1 vs C3: {c1_c3_similarity:.4f}")
print(f"  C2 vs C3: {c2_c3_similarity:.4f}")
print(f"\nDisagreements: {len(results['disagreements'])} studies")
print(f"\nDisagreement Details:")
for d in results["disagreements"]:
    print(f"  Study {d['study']}: C1={d['c1']}, C2={d['c2']}, C3={d['c3']}")
    print(f"    Q3: {d['q3']}")
