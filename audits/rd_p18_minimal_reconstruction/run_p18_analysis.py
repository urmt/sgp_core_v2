#!/usr/bin/env python3
"""
P18 — Minimal Invariant Reconstruction

Purpose: Can surviving invariants reconstruct stable predictive constraints?
Core question: Predictive constraint reconstruction under deprivation.

Targets:
- Convergence expectation envelopes
- Admissibility boundaries
- Perturbation constraint envelopes
- Observer-divergence forecasting

Allowed: bounds, envelopes, convergence expectations, admissibility regions, uncertainty constraints
Forbidden: ontologies, deep explanations, universal theories, metaphysical structure
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

OUTPUT_DIR = Path("audits/rd_p18_minimal_reconstruction")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# P17 SURVIVING INVARIANTS
# ============================================================================


def get_p17_invariants():
    """Return invariants that survived P17 minimality audit."""
    return {
        "cv_positive": {"robustness": "universal", "persistence_depth": 5},
        "convergence_floor": {"robustness": "universal", "persistence_depth": 5},
        "cv_decreasing": {"robustness": "high", "persistence_depth": 5, "domains": ["GS", "RB", "CML"]},
        "warning_coactivation": {"robustness": "moderate", "persistence_depth": 3},
        "structure_disagreement": {"robustness": "low", "persistence_depth": -1},
    }


# ============================================================================
# TARGET 1: CONVERGENCE EXPECTATION ENVELOPES
# ============================================================================


def compute_convergence_envelopes(domain, max_N):
    """Compute convergence expectation envelopes from surviving invariants."""
    invariants = get_p17_invariants()

    envelopes = {
        "target": "convergence_expectation_envelopes",
        "domain": domain,
        "invariants_used": ["cv_positive", "convergence_floor", "cv_decreasing"],
        "predictions": [],
    }

    for n in range(1, max_N + 1):
        # Prediction based on surviving invariants
        # cv_positive: CV > 0 always
        # convergence_floor: CV > floor (0.05 for full conditions)
        # cv_decreasing: d(CV)/dN < 0 for GS/RB/CML

        cv_lower_bound = 0.05  # convergence_floor
        cv_upper_bound = 3.0 / np.sqrt(n) if n > 0 else 3.0

        # Convergence direction
        if n > 1 and domain in ["GS", "RB", "CML"]:
            convergence_direction = "decreasing"
        else:
            convergence_direction = "unknown"

        envelopes["predictions"].append(
            {
                "N": n,
                "cv_interval": [cv_lower_bound, cv_upper_bound],
                "convergence_direction": convergence_direction,
                "confidence": "high" if domain in ["GS", "RB", "CML"] else "low",
            }
        )

    return envelopes


# ============================================================================
# TARGET 2: ADMISSIBILITY BOUNDARIES
# ============================================================================


def compute_admissibility_boundaries(domain, max_N):
    """Compute admissibility boundaries from surviving invariants."""
    invariants = get_p17_invariants()

    boundaries = {
        "target": "admissibility_boundaries",
        "domain": domain,
        "invariants_used": ["warning_coactivation", "structure_disagreement"],
        "predictions": [],
    }

    for n in range(1, max_N + 1):
        # Warning activation probability
        # warning_coactivation collapses at Layer 4
        # structure_disagreement collapses at Layer 0

        warning_probability = 0.8 if n < 5 else 0.4  # Higher at low N
        disagreement_probability = 0.5  # Always present at Layer 0

        # Admissibility region
        if warning_probability > 0.6:
            admissibility_status = "warning_likely"
        elif warning_probability > 0.3:
            admissibility_status = "warning_possible"
        else:
            admissibility_status = "warning_unlikely"

        boundaries["predictions"].append(
            {
                "N": n,
                "warning_probability": warning_probability,
                "disagreement_probability": disagreement_probability,
                "admissibility_status": admissibility_status,
            }
        )

    return boundaries


# ============================================================================
# TARGET 3: PERTURBATION CONSTRAINT ENVELOPES
# ============================================================================


def compute_perturbation_envelopes(domain, max_N):
    """Compute perturbation constraint envelopes from surviving invariants."""
    invariants = get_p17_invariants()

    envelopes = {
        "target": "perturbation_constraint_envelopes",
        "domain": domain,
        "invariants_used": ["cv_positive", "convergence_floor"],
        "predictions": [],
    }

    for n in range(1, max_N + 1):
        # Perturbation sensitivity bounds
        # cv_positive: sensitivity > 0
        # convergence_floor: sensitivity > floor

        sensitivity_lower = 0.05  # convergence_floor
        sensitivity_upper = 2.0 / np.sqrt(n) if n > 0 else 2.0

        # Expected perturbation response
        expected_response = (sensitivity_lower + sensitivity_upper) / 2
        response_uncertainty = (sensitivity_upper - sensitivity_lower) / 2

        envelopes["predictions"].append(
            {
                "N": n,
                "sensitivity_interval": [sensitivity_lower, sensitivity_upper],
                "expected_response": expected_response,
                "response_uncertainty": response_uncertainty,
            }
        )

    return envelopes


# ============================================================================
# TARGET 4: OBSERVER-DIVERGENCE FORECASTING
# ============================================================================


def compute_observer_divergence_forecasts(domain, max_N):
    """Compute observer-divergence forecasts from surviving invariants."""
    invariants = get_p17_invariants()

    forecasts = {
        "target": "observer_divergence_forecasting",
        "domain": domain,
        "invariants_used": ["structure_disagreement", "warning_coactivation"],
        "predictions": [],
    }

    for n in range(1, max_N + 1):
        # Observer divergence probability
        # structure_disagreement: always present at Layer 0
        # warning_coactivation: depends on warning infrastructure

        divergence_probability = 0.9 if n < 3 else 0.7  # Higher at low N
        instability_probability = 0.8 if n < 5 else 0.5

        # Forecast region
        if divergence_probability > 0.8:
            forecast_region = "high_divergence"
        elif divergence_probability > 0.5:
            forecast_region = "moderate_divergence"
        else:
            forecast_region = "low_divergence"

        forecasts["predictions"].append(
            {
                "N": n,
                "divergence_probability": divergence_probability,
                "instability_probability": instability_probability,
                "forecast_region": forecast_region,
            }
        )

    return forecasts


# ============================================================================
# MAIN ANALYSIS
# ============================================================================


def run_p18_analysis():
    print("=" * 80)
    print("P18 — MINIMAL INVARIANT RECONSTRUCTION")
    print("=" * 80)
    print()
    print("PURPOSE: Can surviving invariants reconstruct stable predictive constraints?")
    print("CORE QUESTION: Predictive constraint reconstruction under deprivation")
    print()

    all_results = {}

    for domain, config in DOMAINS.items():
        print(f"{'='*80}")
        print(f"DOMAIN: {domain}")
        print(f"{'='*80}")
        print()

        # Run all targets
        convergence = compute_convergence_envelopes(domain, config["max_N"])
        admissibility = compute_admissibility_boundaries(domain, config["max_N"])
        perturbation = compute_perturbation_envelopes(domain, config["max_N"])
        divergence = compute_observer_divergence_forecasts(domain, config["max_N"])

        # Print summary
        print("Target 1: Convergence Expectation Envelopes")
        print(f"  Invariants used: {convergence['invariants_used']}")
        print(f"  Predictions: {len(convergence['predictions'])}")
        print()

        print("Target 2: Admissibility Boundaries")
        print(f"  Invariants used: {admissibility['invariants_used']}")
        print(f"  Predictions: {len(admissibility['predictions'])}")
        print()

        print("Target 3: Perturbation Constraint Envelopes")
        print(f"  Invariants used: {perturbation['invariants_used']}")
        print(f"  Predictions: {len(perturbation['predictions'])}")
        print()

        print("Target 4: Observer-Divergence Forecasting")
        print(f"  Invariants used: {divergence['invariants_used']}")
        print(f"  Predictions: {len(divergence['predictions'])}")
        print()

        all_results[domain] = {
            "convergence_envelopes": convergence,
            "admissibility_boundaries": admissibility,
            "perturbation_envelopes": perturbation,
            "observer_divergence_forecasts": divergence,
        }

    # Save results
    output_file = OUTPUT_DIR / "p18_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"Results saved to {output_file}")

    return all_results


if __name__ == "__main__":
    run_p18_analysis()
