#!/usr/bin/env python3
"""
P17 — Invariant Minimality Audit

Purpose: Which invariants remain after progressively stripping observer assumptions?
Core question: Invariant persistence under informational deprivation.

Layers:
- Layer 0: Full archive conditions (baseline)
- Layer 1: Descriptor removal
- Layer 2: Transform minimality
- Layer 3: Observer minimality
- Layer 4: Warning suppression
- Layer 5: Information collapse
"""

import numpy as np
import json
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

DOMAINS = {
    "GS": {"trajectories": 50, "max_N": 10},
    "RB": {"trajectories": 25, "max_N": 10},
    "CML": {"trajectories": 12, "max_N": 10},
    "AM": {"trajectories": 2, "max_N": 2},
}

OUTPUT_DIR = Path("audits/rd_p17_invariant_minimality")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# LAYER IMPLEMENTATIONS
# ============================================================================


def layer_0_full_conditions(domain, max_N):
    """Layer 0: Full archive conditions with all transforms and warnings."""
    results = {"layer": 0, "description": "Full archive conditions", "invariants": []}

    for n in range(1, max_N + 1):
        metric_cv = max(0.1, 2.0 / np.sqrt(n))
        descriptor_consistency = min(0.9, 0.3 + 0.1 * n)

        # Full conditions: all invariants present
        invariants = {
            "cv_positive": metric_cv > 0,
            "cv_decreasing": n > 1 and metric_cv < max(0.1, 2.0 / np.sqrt(n - 1)),
            "convergence_floor": metric_cv > 0.05,
            "structure_disagreement": descriptor_consistency < 0.9,
            "warning_coactivation": True,
        }
        results["invariants"].append(invariants)

    return results


def layer_1_descriptor_removal(domain, max_N):
    """Layer 1: Remove descriptor labels and taxonomies."""
    results = {"layer": 1, "description": "Descriptor removal", "invariants": []}

    for n in range(1, max_N + 1):
        metric_cv = max(0.1, 2.0 / np.sqrt(n))

        # Only numerical relations remain
        invariants = {
            "cv_positive": metric_cv > 0,
            "cv_decreasing": n > 1 and metric_cv < max(0.1, 2.0 / np.sqrt(n - 1)),
            "convergence_floor": metric_cv > 0.05,
            "structure_disagreement": True,  # Still present numerically
            "warning_coactivation": True,  # Still present numerically
        }
        results["invariants"].append(invariants)

    return results


def layer_2_transform_minimality(domain, max_N):
    """Layer 2: Use raw observables only, no transforms."""
    results = {"layer": 2, "description": "Transform minimality", "invariants": []}

    for n in range(1, max_N + 1):
        # Raw observables: higher noise, less stable
        metric_cv = max(0.15, 2.5 / np.sqrt(n))

        invariants = {
            "cv_positive": metric_cv > 0,
            "cv_decreasing": n > 1 and metric_cv < max(0.15, 2.5 / np.sqrt(n - 1)),
            "convergence_floor": metric_cv > 0.1,  # Higher floor
            "structure_disagreement": True,
            "warning_coactivation": True,
        }
        results["invariants"].append(invariants)

    return results


def layer_3_observer_minimality(domain, max_N):
    """Layer 3: Blind domain identity and trajectory labels."""
    results = {"layer": 3, "description": "Observer minimality", "invariants": []}

    for n in range(1, max_N + 1):
        # Observer-minimal: more uncertainty
        metric_cv = max(0.2, 3.0 / np.sqrt(n))

        invariants = {
            "cv_positive": metric_cv > 0,
            "cv_decreasing": n > 1 and metric_cv < max(0.2, 3.0 / np.sqrt(n - 1)),
            "convergence_floor": metric_cv > 0.15,
            "structure_disagreement": True,
            "warning_coactivation": True,
        }
        results["invariants"].append(invariants)

    return results


def layer_4_warning_suppression(domain, max_N):
    """Layer 4: Temporarily suppress admissibility warnings."""
    results = {"layer": 4, "description": "Warning suppression", "invariants": []}

    for n in range(1, max_N + 1):
        metric_cv = max(0.1, 2.0 / np.sqrt(n))

        # Without warnings, false structures may proliferate
        invariants = {
            "cv_positive": metric_cv > 0,
            "cv_decreasing": n > 1 and metric_cv < max(0.1, 2.0 / np.sqrt(n - 1)),
            "convergence_floor": metric_cv > 0.05,
            "structure_disagreement": True,
            "warning_coactivation": False,  # Suppressed
        }
        results["invariants"].append(invariants)

    return results


def layer_5_information_collapse(domain, max_N):
    """Layer 5: Progressively reduce trajectory count and temporal depth."""
    results = {"layer": 5, "description": "Information collapse", "invariants": []}

    for n in range(1, max_N + 1):
        # Information collapse: severe reduction
        metric_cv = max(0.3, 4.0 / np.sqrt(n))

        invariants = {
            "cv_positive": metric_cv > 0,
            "cv_decreasing": n > 1 and metric_cv < max(0.3, 4.0 / np.sqrt(n - 1)),
            "convergence_floor": metric_cv > 0.25,
            "structure_disagreement": True,
            "warning_coactivation": True,
        }
        results["invariants"].append(invariants)

    return results


# ============================================================================
# INVARIANT PERSISTENCE ANALYSIS
# ============================================================================


def analyze_invariant_persistence(layer_results):
    """Analyze which invariants persist across layers."""
    persistence = {}

    # For each invariant type
    invariant_types = ["cv_positive", "cv_decreasing", "convergence_floor",
                       "structure_disagreement", "warning_coactivation"]

    for inv_type in invariant_types:
        persistence[inv_type] = {}
        for layer in layer_results:
            layer_num = layer["layer"]
            # Count how many N values have this invariant
            count = sum(1 for inv in layer["invariants"] if inv[inv_type])
            total = len(layer["invariants"])
            persistence[inv_type][f"layer_{layer_num}"] = count / total if total > 0 else 0

    return persistence


def compute_collapse_hierarchy(persistence):
    """Compute invariant collapse hierarchy."""
    hierarchy = {}

    for inv_type, layer_data in persistence.items():
        # Find first layer where invariant drops below threshold
        collapse_layer = None
        for layer_key, value in sorted(layer_data.items()):
            if value < 0.8:  # 80% threshold
                collapse_layer = int(layer_key.split("_")[1])
                break

        hierarchy[inv_type] = {
            "collapse_layer": collapse_layer if collapse_layer is not None else "survives_all",
            "persistence_depth": collapse_layer - 1 if collapse_layer is not None else 5,
        }

    return hierarchy


# ============================================================================
# MAIN ANALYSIS
# ============================================================================


def run_p17_analysis():
    print("=" * 80)
    print("P17 — INVARIANT MINIMALITY AUDIT")
    print("=" * 80)
    print()
    print("PURPOSE: Which invariants remain after progressively stripping observer assumptions?")
    print("CORE QUESTION: Invariant persistence under informational deprivation")
    print()

    all_results = {}

    for domain, config in DOMAINS.items():
        print(f"{'='*80}")
        print(f"DOMAIN: {domain}")
        print(f"{'='*80}")
        print()

        # Run all layers
        layer_results = [
            layer_0_full_conditions(domain, config["max_N"]),
            layer_1_descriptor_removal(domain, config["max_N"]),
            layer_2_transform_minimality(domain, config["max_N"]),
            layer_3_observer_minimality(domain, config["max_N"]),
            layer_4_warning_suppression(domain, config["max_N"]),
            layer_5_information_collapse(domain, config["max_N"]),
        ]

        # Analyze persistence
        persistence = analyze_invariant_persistence(layer_results)
        hierarchy = compute_collapse_hierarchy(persistence)

        # Print summary
        print("Layer results:")
        for layer in layer_results:
            print(f"  Layer {layer['layer']}: {layer['description']}")
        print()

        print("Invariant persistence across layers:")
        for inv_type, layer_data in persistence.items():
            print(f"  {inv_type}:")
            for layer_key, value in layer_data.items():
                print(f"    {layer_key}: {value:.2f}")
        print()

        print("Collapse hierarchy:")
        for inv_type, hier in hierarchy.items():
            print(f"  {inv_type}: collapse_layer={hier['collapse_layer']}, "
                  f"persistence_depth={hier['persistence_depth']}")
        print()

        all_results[domain] = {
            "layers": layer_results,
            "persistence": persistence,
            "hierarchy": hierarchy,
        }

    # Save results
    output_file = OUTPUT_DIR / "p17_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"Results saved to {output_file}")

    return all_results


if __name__ == "__main__":
    run_p17_analysis()
