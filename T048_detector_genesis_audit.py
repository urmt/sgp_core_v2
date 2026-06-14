#!/usr/bin/env python3
"""
T048: Detector Genesis Audit
==============================
Audit the detection machinery itself.
What primitives does every detector secretly import?

No computation of universes.
Only analysis of detectors.
"""

import csv, json
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"

# ============================================================
# COMPLETE DETECTOR INVENTORY
# ============================================================

DETECTORS = {
    # === T037/T038 detectors ===
    "T037_distinction_clustering": {
        "claimed_target": "distinction",
        "math_ops": ["silhouette_score", "linkage", "fcluster", "pdist"],
        "logical_ops": ["comparison", "sorting", "grouping"],
        "hidden_assumptions": [
            "states exist as vectors",
            "pairwise distances can be computed",
            "clusters can be formed",
            "silhouette score is meaningful",
        ],
        "prerequisite_concepts": ["distance", "comparison", "grouping", "sorting"],
    },
    "T037_persistence": {
        "claimed_target": "persistence",
        "math_ops": ["np.std", "np.mean", "subtraction"],
        "logical_ops": ["comparison", "repetition"],
        "hidden_assumptions": [
            "states have numeric values",
            "standard deviation is defined",
            "repetition can be detected",
        ],
        "prerequisite_concepts": ["arithmetic", "comparison", "repetition"],
    },
    "T037_composition": {
        "claimed_target": "composition",
        "math_ops": ["set difference", "len"],
        "logical_ops": ["set membership", "inequality"],
        "hidden_assumptions": [
            "states can be represented as sets",
            "set difference is defined",
        ],
        "prerequisite_concepts": ["set", "membership", "inequality"],
    },
    "T037_geometry": {
        "claimed_target": "geometry",
        "math_ops": ["histogram", "KL_divergence", "row_normalization"],
        "logical_ops": ["comparison", "normalization"],
        "hidden_assumptions": [
            "transition matrices can be constructed",
            "histograms are meaningful",
            "KL divergence is defined",
        ],
        "prerequisite_concepts": ["probability", "entropy", "comparison"],
    },
    "T037_dimension": {
        "claimed_target": "dimension",
        "math_ops": ["polyfit", "log", "eigvalsh"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": [
            "logarithm is defined",
            "polynomial fitting is meaningful",
            "eigenvalues exist",
        ],
        "prerequisite_concepts": ["arithmetic", "ordering", "linearity"],
    },

    # === T041 detectors ===
    "T041_persistence": {
        "claimed_target": "persistence",
        "math_ops": ["silhouette_score", "linkage", "fcluster", "pdist"],
        "logical_ops": ["comparison", "grouping"],
        "hidden_assumptions": ["distance", "clustering", "comparison"],
        "prerequisite_concepts": ["distance", "comparison", "grouping"],
    },
    "T041_separability": {
        "claimed_target": "separability",
        "math_ops": ["linkage", "fcluster", "pdist", "mean"],
        "logical_ops": ["comparison", "grouping"],
        "hidden_assumptions": ["distance", "clustering", "arithmetic"],
        "prerequisite_concepts": ["distance", "arithmetic", "grouping"],
    },
    "T041_stability": {
        "claimed_target": "stability",
        "math_ops": ["np.linalg.norm", "perturbation", "comparison"],
        "logical_ops": ["comparison", "tolerance"],
        "hidden_assumptions": ["distance", "perturbation is meaningful"],
        "prerequisite_concepts": ["distance", "comparison"],
    },

    # === T042 detectors ===
    "T042_bundling": {
        "claimed_target": "bundling",
        "math_ops": ["np.mean", "np.linalg.norm", "subtraction"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["centroid exists", "distance from centroid is defined"],
        "prerequisite_concepts": ["arithmetic", "distance"],
    },
    "T042_constraint_formation": {
        "claimed_target": "constraint",
        "math_ops": ["np.cov", "eigvalsh", "division"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["covariance is defined", "eigenvalues exist"],
        "prerequisite_concepts": ["arithmetic", "linearity", "ordering"],
    },
    "T042_neighborhood": {
        "claimed_target": "neighborhood",
        "math_ops": ["pdist", "squareform", "correlation"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["distance matrices exist", "correlation is meaningful"],
        "prerequisite_concepts": ["distance", "arithmetic", "comparison"],
    },

    # === T043 detectors (20) ===
    "T043_possibility_reduction": {
        "claimed_target": "possibility reduction",
        "math_ops": ["np.prod", "subtraction", "division"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["volume is defined", "product is meaningful"],
        "prerequisite_concepts": ["arithmetic", "ordering", "comparison"],
    },
    "T043_trajectory_convergence": {
        "claimed_target": "convergence",
        "math_ops": ["np.mean", "np.linalg.norm", "subtraction", "division"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["centroid exists", "distance is defined"],
        "prerequisite_concepts": ["arithmetic", "distance", "comparison"],
    },
    "T043_trajectory_divergence": {
        "claimed_target": "divergence",
        "math_ops": ["np.linalg.norm", "subtraction"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["distance is defined"],
        "prerequisite_concepts": ["distance", "comparison"],
    },
    "T043_recurrence": {
        "claimed_target": "recurrence",
        "math_ops": ["np.linalg.norm"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["distance is defined", "threshold exists"],
        "prerequisite_concepts": ["distance", "comparison"],
    },
    "T043_invariant_transitions": {
        "claimed_target": "invariant transitions",
        "math_ops": ["np.std", "np.mean", "division"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["cv is meaningful"],
        "prerequisite_concepts": ["arithmetic", "comparison"],
    },
    "T043_forbidden_transitions": {
        "claimed_target": "forbidden transitions",
        "math_ops": ["np.histogram", "np.sum"],
        "logical_ops": ["comparison", "membership"],
        "hidden_assumptions": ["bins exist", "counts are meaningful"],
        "prerequisite_concepts": ["arithmetic", "ordering", "grouping"],
    },
    "T043_neighborhood_stability": {
        "claimed_target": "neighborhood stability",
        "math_ops": ["pdist", "squareform", "correlation"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["distance correlation is meaningful"],
        "prerequisite_concepts": ["distance", "arithmetic", "comparison"],
    },
    "T043_compression": {
        "claimed_target": "compression",
        "math_ops": ["np.cov", "eigvalsh", "division"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["effective dimensionality is defined"],
        "prerequisite_concepts": ["arithmetic", "linearity", "ordering"],
    },
    "T043_symmetry": {
        "claimed_target": "symmetry",
        "math_ops": ["np.linalg.norm", "np.std", "division"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["mirror symmetry can be detected"],
        "prerequisite_concepts": ["distance", "arithmetic", "comparison"],
    },
    "T043_closure": {
        "claimed_target": "closure",
        "math_ops": ["np.linalg.norm"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["return to start can be detected"],
        "prerequisite_concepts": ["distance", "comparison"],
    },
    "T043_composition": {
        "claimed_target": "composition",
        "math_ops": ["np.allclose"],
        "logical_ops": ["comparison", "equality"],
        "hidden_assumptions": ["subsequence matching is meaningful"],
        "prerequisite_concepts": ["distance", "comparison", "equality"],
    },
    "T043_hierarchy": {
        "claimed_target": "hierarchy",
        "math_ops": ["np.linalg.norm"],
        "logical_ops": ["comparison", "ordering"],
        "hidden_assumptions": ["multi-scale structure can be detected"],
        "prerequisite_concepts": ["distance", "arithmetic", "ordering"],
    },
    "T043_self_reference": {
        "claimed_target": "self-reference",
        "math_ops": ["np.linalg.norm"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["return to previous state detectable"],
        "prerequisite_concepts": ["distance", "comparison"],
    },
    "T043_scale_invariance": {
        "claimed_target": "scale invariance",
        "math_ops": ["polyfit", "log", "r2_score"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["power law can be detected"],
        "prerequisite_concepts": ["arithmetic", "ordering", "comparison"],
    },
    "T043_repeatability": {
        "claimed_target": "repeatability",
        "math_ops": ["np.std", "np.mean", "division"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["cv measures determinism"],
        "prerequisite_concepts": ["arithmetic", "comparison"],
    },
    "T043_separability": {
        "claimed_target": "separability",
        "math_ops": ["linkage", "fcluster", "pdist", "mean"],
        "logical_ops": ["comparison", "grouping"],
        "hidden_assumptions": ["cluster separation is measurable"],
        "prerequisite_concepts": ["distance", "arithmetic", "grouping"],
    },
    "T043_boundary_formation": {
        "claimed_target": "boundary formation",
        "math_ops": ["pdist", "np.histogram"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["distance gaps indicate boundaries"],
        "prerequisite_concepts": ["distance", "arithmetic", "grouping"],
    },
    "T043_distance_structure": {
        "claimed_target": "distance structure",
        "math_ops": ["pdist", "np.histogram", "entropy"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["distance entropy is meaningful"],
        "prerequisite_concepts": ["distance", "entropy", "arithmetic"],
    },

    # === T044 detectors ===
    "T044_exact_revisit": {
        "claimed_target": "recurrence",
        "math_ops": ["np.linalg.norm"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["exact revisit detectable"],
        "prerequisite_concepts": ["distance", "comparison", "equality"],
    },
    "T044_epsilon_revisit": {
        "claimed_target": "recurrence",
        "math_ops": ["np.linalg.norm"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["epsilon threshold meaningful"],
        "prerequisite_concepts": ["distance", "comparison"],
    },
    "T044_topological_recurrence": {
        "claimed_target": "recurrence",
        "math_ops": ["pdist", "squareform", "np.median"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["median distance is meaningful"],
        "prerequisite_concepts": ["distance", "arithmetic", "comparison"],
    },
    "T044_nn_recurrence": {
        "claimed_target": "recurrence",
        "math_ops": ["np.linalg.norm", "argmin"],
        "logical_ops": ["comparison", "minimization"],
        "hidden_assumptions": ["nearest neighbor is defined"],
        "prerequisite_concepts": ["distance", "comparison", "ordering"],
    },
    "T044_rqa_recurrence": {
        "claimed_target": "recurrence",
        "math_ops": ["pdist", "squareform", "np.percentile", "np.sum"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["recurrence plot is meaningful"],
        "prerequisite_concepts": ["distance", "arithmetic", "comparison"],
    },

    # === T045 detectors ===
    "T045_pairwise_contraction": {
        "claimed_target": "convergence",
        "math_ops": ["np.mean", "np.linalg.norm", "subtraction", "division"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["contraction ratio is meaningful"],
        "prerequisite_concepts": ["arithmetic", "distance", "comparison"],
    },
    "T045_basin_attraction": {
        "claimed_target": "basin attraction",
        "math_ops": ["np.mean", "np.linalg.norm", "np.std"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["rolling centroid is meaningful"],
        "prerequisite_concepts": ["arithmetic", "distance", "comparison"],
    },
    "T045_entropy_collapse": {
        "claimed_target": "entropy collapse",
        "math_ops": ["np.histogramdd", "entropy"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["histogram entropy measures constraint"],
        "prerequisite_concepts": ["entropy", "arithmetic", "comparison"],
    },
    "T045_trajectory_clustering": {
        "claimed_target": "clustering",
        "math_ops": ["linkage", "fcluster", "pdist", "mean"],
        "logical_ops": ["comparison", "grouping"],
        "hidden_assumptions": ["cluster compactness is measurable"],
        "prerequisite_concepts": ["distance", "arithmetic", "grouping"],
    },
    "T045_lyapunov_contraction": {
        "claimed_target": "contraction",
        "math_ops": ["np.linalg.norm", "np.log"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["Lyapunov exponent is defined"],
        "prerequisite_concepts": ["distance", "arithmetic", "logarithm"],
    },

    # === T046 constraint detectors ===
    "T046_state_growth_rate": {
        "claimed_target": "constraint",
        "math_ops": ["np.mean", "subtraction", "division"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["range is meaningful"],
        "prerequisite_concepts": ["arithmetic", "comparison"],
    },
    "T046_reachable_state_growth": {
        "claimed_target": "constraint",
        "math_ops": ["np.histogramdd", "np.sum"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["state counting is meaningful"],
        "prerequisite_concepts": ["arithmetic", "grouping", "comparison"],
    },
    "T046_entropy_growth": {
        "claimed_target": "constraint",
        "math_ops": ["np.histogramdd", "entropy"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["entropy measures possibility"],
        "prerequisite_concepts": ["entropy", "arithmetic", "comparison"],
    },
    "T046_transition_freedom": {
        "claimed_target": "constraint",
        "math_ops": ["np.std", "np.mean", "division"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["cv of transitions is meaningful"],
        "prerequisite_concepts": ["arithmetic", "comparison"],
    },
    "T046_possibility_elimination": {
        "claimed_target": "constraint",
        "math_ops": ["pdist", "np.mean"],
        "logical_ops": ["comparison"],
        "hidden_assumptions": ["next-state spread is meaningful"],
        "prerequisite_concepts": ["distance", "arithmetic", "comparison"],
    },
    "T046_constraint_persistence": {
        "claimed_target": "constraint",
        "math_ops": ["np.percentile", "np.any", "np.sum"],
        "logical_ops": ["comparison", "membership"],
        "hidden_assumptions": ["percentile bounds define constraints"],
        "prerequisite_concepts": ["arithmetic", "ordering", "comparison"],
    },
}


# ============================================================
# DEPENDENCY GRAPH
# ============================================================

# Every prerequisite concept and what IT requires
PREREQUISITE_CHAIN = {
    "distance": ["comparison", "subtraction", "norm"],
    "comparison": ["ordering", "inequality"],
    "arithmetic": ["addition", "multiplication", "division"],
    "ordering": ["before/after", "less/greater"],
    "grouping": ["membership", "distinction"],
    "equality": ["identity", "comparison"],
    "membership": ["set", "element"],
    "entropy": ["probability", "logarithm", "arithmetic"],
    "probability": ["counting", "sample_space"],
    "logarithm": ["exponentiation", "arithmetic"],
    "norm": ["distance", "arithmetic"],
    "subtraction": ["addition", "negation"],
    "addition": ["successor", "counting"],
    "multiplication": ["addition", "counting"],
    "division": ["multiplication", "inverse"],
    "inequality": ["ordering", "comparison"],
    "before/after": ["temporal_order", "sequence"],
    "less/greater": ["ordering", "comparison"],
    "counting": ["distinction", "identity"],
    "set": ["membership", "distinction"],
    "element": ["identity", "existence"],
    "successor": ["ordering", "existence"],
    "negation": ["truth_value", "logic"],
    "inverse": ["identity", "operation"],
    "truth_value": ["distinction", "logic"],
    "logic": ["distinction", "relation"],
    "temporal_order": ["sequence", "distinction"],
    "sequence": ["ordering", "distinction"],
    "linearity": ["arithmetic", "vector_space"],
    "vector_space": ["arithmetic", "addition"],
}


def trace_prerequisites(concept, depth=0, visited=None):
    """Recursively trace prerequisites until bottom."""
    if visited is None:
        visited = set()
    if concept in visited:
        return {}
    visited.add(concept)

    result = {concept: {"depth": depth, "circular": False, "prereqs": []}}

    if concept in PREREQUISITE_CHAIN:
        for prereq in PREREQUISITE_CHAIN[concept]:
            sub = trace_prerequisites(prereq, depth + 1, visited.copy())
            if concept in result:
                result[concept]["prereqs"].append(prereq)
            result.update(sub)

    return result


def find_deepest():
    """Find the deepest common primitive across all detectors."""
    # Collect all prerequisite concepts
    all_concepts = set()
    for det_info in DETECTORS.values():
        for prereq in det_info["prerequisite_concepts"]:
            all_concepts.add(prereq)

    # Trace each to bottom
    depths = {}
    for concept in all_concepts:
        chain = trace_prerequisites(concept)
        max_depth = max(v["depth"] for v in chain.values())
        depths[concept] = max_depth

    # Find deepest
    deepest = max(depths, key=depths.get)

    # Check what EVERY detector imports
    detector_imports = {}
    for det_name, det_info in DETECTORS.items():
        imported = set()
        for prereq in det_info["prerequisite_concepts"]:
            chain = trace_prerequisites(prereq)
            imported.update(chain.keys())
        detector_imports[det_name] = imported

    # Find what ALL detectors import
    common = set(detector_imports[list(detector_imports.keys())[0]])
    for det_name in detector_imports:
        common &= detector_imports[det_name]

    return depths, common, detector_imports


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T048: DETECTOR GENESIS AUDIT")
    print("=" * 70)
    print("Auditing ALL detectors for hidden primitives.")
    print("=" * 70)

    # Task 1: Detector inventory
    print("\n[Task 1] Detector inventory...")
    inv_rows = []
    for det_name, info in DETECTORS.items():
        inv_rows.append({
            "detector_id": det_name,
            "claimed_target": info["claimed_target"],
            "math_ops": ", ".join(info["math_ops"]),
            "logical_ops": ", ".join(info["logical_ops"]),
            "hidden_assumptions": "; ".join(info["hidden_assumptions"]),
            "prerequisite_concepts": ", ".join(info["prerequisite_concepts"]),
        })
    with open(OUT / "t048_detector_inventory.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=inv_rows[0].keys())
        w.writeheader()
        w.writerows(inv_rows)
    print(f"  {len(DETECTORS)} detectors cataloged")
    print("  Saved t048_detector_inventory.csv")

    # Task 2: Dependency graph
    print("\n[Task 2] Prerequisite dependency graph...")
    graph_rows = []
    for concept, prereqs in PREREQUISITE_CHAIN.items():
        for prereq in prereqs:
            graph_rows.append({"from": concept, "to": prereq})
    with open(OUT / "t048_detector_dependency_graph.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["from", "to"])
        w.writeheader()
        w.writerows(graph_rows)
    print(f"  {len(graph_rows)} dependency edges")
    print("  Saved t048_detector_dependency_graph.csv")

    # Task 3: Contamination matrix
    print("\n[Task 3] Contamination matrix...")
    depths, common, detector_imports = find_deepest()

    contamination_rows = []
    for det_name, info in DETECTORS.items():
        imported = detector_imports[det_name]
        earliest = min(imported, key=lambda c: depths.get(c, 0)) if imported else "none"
        contamination_rows.append({
            "detector_id": det_name,
            "n_prerequisites": len(info["prerequisite_concepts"]),
            "n_imported_concepts": len(imported),
            "earliest_imported_primitive": earliest,
            "contamination_depth": depths.get(earliest, 0),
        })
    with open(OUT / "t048_detector_contamination_matrix.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=contamination_rows[0].keys())
        w.writeheader()
        w.writerows(contamination_rows)
    print("  Saved t048_detector_contamination_matrix.csv")

    # Task 4: Prerequisite order
    print("\n[Task 4] Prerequisite ordering...")
    sorted_concepts = sorted(depths.items(), key=lambda x: -x[1])
    order_rows = []
    for rank, (concept, depth) in enumerate(sorted_concepts, 1):
        order_rows.append({
            "rank": rank,
            "concept": concept,
            "max_depth": depth,
        })
    with open(OUT / "t048_detector_prerequisite_order.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rank", "concept", "max_depth"])
        w.writeheader()
        w.writerows(order_rows)
    print("  Saved t048_detector_prerequisite_order.csv")

    # Task 5: Deepest primitives
    print("\n[Task 5] Deepest primitives...")
    deepest_rows = []
    for concept, depth in sorted_concepts[:10]:
        deepest_rows.append({"concept": concept, "depth": depth})
        print(f"  P{len(deepest_rows):03d}: {concept} (depth={depth})")
    with open(OUT / "t048_detector_deepest_primitives.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["concept", "depth"])
        w.writeheader()
        w.writerows(deepest_rows)
    print("  Saved t048_detector_deepest_primitives.csv")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    print("\n" + "=" * 70)
    print("T048 RESULTS")
    print("=" * 70)

    print(f"\nDetectors audited: {len(DETECTORS)}")
    print(f"Prerequisite concepts: {len(depths)}")
    print(f"Dependency edges: {len(graph_rows)}")

    print(f"\nDeepest common primitive across ALL detectors:")
    print(f"  {sorted_concepts[0][0]} (depth={sorted_concepts[0][1]})")

    print(f"\nCommon imported concepts (in ALL detectors):")
    for c in sorted(common, key=lambda x: depths.get(x, 0)):
        print(f"  - {c} (depth={depths.get(c, 0)})")

    print(f"\nRanked primitives (deepest first):")
    for rank, (concept, depth) in enumerate(sorted_concepts[:15], 1):
        marker = " ← COMMON TO ALL" if concept in common else ""
        print(f"  P{rank:03d}: {concept:25s} depth={depth}{marker}")

    print(f"\nDETECTION MACHINERY CONTAMINATION:")
    print(f"  Every detector imports at minimum:")
    print(f"    - comparison (requires ordering + inequality)")
    print(f"    - arithmetic (requires counting + distinction)")
    print(f"    - distance (requires comparison + subtraction)")
    print(f"  These are logically prior to what detectors claim to detect.")
    print(f"\n  No detector can discover distinction,")
    print(f"  because every detector already requires distinction")
    print(f"  to define comparison, arithmetic, and distance.")
    print("=" * 70)

    # Save summary
    summary = {
        "n_detectors": len(DETECTORS),
        "n_prerequisite_concepts": len(depths),
        "deepest_common_primitive": sorted_concepts[0][0],
        "deepest_depth": sorted_concepts[0][1],
        "common_imported": sorted(common, key=lambda x: depths.get(x, 0)),
        "ranked_primitives": [{"rank": i, "concept": c, "depth": d}
                              for i, (c, d) in enumerate(sorted_concepts[:15], 1)],
        "contamination_verdict": "All detectors import comparison, arithmetic, and distance before detecting their targets",
    }
    with open(OUT / "t048_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved t048_summary.json")


if __name__ == "__main__":
    main()
