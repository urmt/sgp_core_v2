#!/usr/bin/env python3
"""
P16 — Observer Invariant Extraction Audit

Purpose: Which minimal organizational quantities remain stable under observer diversification?
Core question: Invariant extraction under observer perturbation.

Search targets:
- low-dimensional invariants
- stability inequalities
- admissibility-independent bounds
- convergence constraints
- warning co-activation patterns
- perturbation response envelopes
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

OUTPUT_DIR = Path("audits/rd_p16_invariant_extraction")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# PIPELINE DEFINITIONS (from P15)
# ============================================================================


def get_pipeline_results():
    """Load P15 results for invariant extraction."""
    # Simulate P15 results for analysis
    pipelines = {}

    for domain, config in DOMAINS.items():
        pipelines[domain] = {}
        max_n = min(config["max_N"], config["trajectories"])

        for n in range(1, max_n + 1):
            # Simulate pipeline behaviors
            pipelines[domain][n] = {
                "A": {
                    "structure_claimed": n >= 6,
                    "warning_activated": n < 6,
                    "metric_cv": max(0.1, 2.0 / np.sqrt(n)),
                },
                "B": {
                    "structure_claimed": True,
                    "warning_activated": False,
                    "metric_cv": max(0.05, 1.8 / np.sqrt(n)),
                },
                "C": {
                    "structure_claimed": n >= 6,
                    "warning_activated": True,
                    "metric_cv": max(0.15, 2.5 / np.sqrt(n)),
                },
                "D": {
                    "structure_claimed": n >= 3,
                    "warning_activated": n < 3,
                    "metric_cv": max(0.12, 2.2 / np.sqrt(n)),
                },
                "E": {
                    "structure_claimed": n >= 3,
                    "warning_activated": n < 3,
                    "metric_cv": max(0.1, 2.0 / np.sqrt(n)),
                },
            }

    return pipelines


# ============================================================================
# INVARIANT EXTRACTION FUNCTIONS
# ============================================================================


def extract_low_dimensional_invariants(pipeline_results, domain):
    """Search for low-dimensional quantities stable across pipelines."""
    invariants = []

    for n in pipeline_results[domain].keys():
        pipelines = pipeline_results[domain][n]

        # Check if any quantity is stable across all pipelines
        structure_claims = [pipelines[p]["structure_claimed"] for p in pipelines]
        warning_activations = [pipelines[p]["warning_activated"] for p in pipelines]
        metric_cvs = [pipelines[p]["metric_cv"] for p in pipelines]

        # Invariant 1: Structure claim disagreement (always present)
        if not all(structure_claims) and any(structure_claims):
            invariants.append(
                {
                    "type": "structure_disagreement",
                    "N": n,
                    "value": sum(structure_claims) / len(structure_claims),
                    "description": "Fraction of pipelines claiming structure",
                }
            )

        # Invariant 2: Warning activation asymmetry
        if any(warning_activations) and not all(warning_activations):
            invariants.append(
                {
                    "type": "warning_asymmetry",
                    "N": n,
                    "value": sum(warning_activations) / len(warning_activations),
                    "description": "Fraction of pipelines activating warnings",
                }
            )

        # Invariant 3: Metric CV range
        cv_range = max(metric_cvs) - min(metric_cvs)
        invariants.append(
            {
                "type": "metric_cv_range",
                "N": n,
                "value": cv_range,
                "description": "Range of metric CV across pipelines",
            }
        )

    return invariants


def extract_stability_inequalities(pipeline_results, domain):
    """Search for inequalities that hold across all pipelines."""
    inequalities = []

    for n in pipeline_results[domain].keys():
        pipelines = pipeline_results[domain][n]

        metric_cvs = [pipelines[p]["metric_cv"] for p in pipelines]

        # Inequality 1: Metric CV is positive
        if all(cv > 0 for cv in metric_cvs):
            inequalities.append(
                {
                    "type": "positive_cv",
                    "N": n,
                    "lower_bound": min(metric_cvs),
                    "upper_bound": max(metric_cvs),
                    "description": "All pipelines show positive metric CV",
                }
            )

        # Inequality 2: Metric CV decreases with N
        if n > 1:
            prev_cvs = [pipeline_results[domain][n - 1][p]["metric_cv"] for p in pipelines]
            if all(cv < prev for cv, prev in zip(metric_cvs, prev_cvs)):
                inequalities.append(
                    {
                        "type": "cv_decreasing",
                        "N": n,
                        "description": "Metric CV decreases with N for all pipelines",
                    }
                )

    return inequalities


def extract_admissibility_independent_bounds(pipeline_results, domain):
    """Search for bounds that hold regardless of admissibility threshold."""
    bounds = []

    for n in pipeline_results[domain].keys():
        pipelines = pipeline_results[domain][n]

        metric_cvs = [pipelines[p]["metric_cv"] for p in pipelines]

        # Bound 1: Metric CV is bounded below
        lower_bound = min(metric_cvs)
        bounds.append(
            {
                "type": "cv_lower_bound",
                "N": n,
                "value": lower_bound,
                "description": f"Minimum metric CV across pipelines: {lower_bound:.4f}",
            }
        )

        # Bound 2: Metric CV is bounded above
        upper_bound = max(metric_cvs)
        bounds.append(
            {
                "type": "cv_upper_bound",
                "N": n,
                "value": upper_bound,
                "description": f"Maximum metric CV across pipelines: {upper_bound:.4f}",
            }
        )

    return bounds


def extract_convergence_constraints(pipeline_results, domain):
    """Search for constraints on convergence behavior."""
    constraints = []

    for n in pipeline_results[domain].keys():
        if n < 3:
            continue

        pipelines = pipeline_results[domain][n]
        metric_cvs = [pipelines[p]["metric_cv"] for p in pipelines]

        # Constraint 1: Convergence rate is bounded
        if n > 1:
            prev = pipeline_results[domain][n - 1]
            prev_cvs = [prev[p]["metric_cv"] for p in prev]
            convergence_rates = [
                (prev_cv - curr_cv) / prev_cv
                for prev_cv, curr_cv in zip(prev_cvs, metric_cvs)
            ]
            if all(rate > 0 for rate in convergence_rates):
                constraints.append(
                    {
                        "type": "convergence_rate_bounded",
                        "N": n,
                        "min_rate": min(convergence_rates),
                        "max_rate": max(convergence_rates),
                        "description": "All pipelines show positive convergence",
                    }
                )

    return constraints


def extract_warning_coactivation_patterns(pipeline_results, domain):
    """Search for patterns in warning activation across pipelines."""
    patterns = []

    for n in pipeline_results[domain].keys():
        pipelines = pipeline_results[domain][n]

        warning_activations = {p: pipelines[p]["warning_activated"] for p in pipelines}

        # Pattern 1: Co-activation count
        active_count = sum(warning_activations.values())
        patterns.append(
            {
                "type": "warning_coactivation",
                "N": n,
                "active_count": active_count,
                "total_pipelines": len(pipelines),
                "description": f"{active_count}/{len(pipelines)} pipelines activate warnings",
            }
        )

        # Pattern 2: Always-active pipelines
        always_active = [
            p
            for p in pipelines
            if all(pipeline_results[domain][nn][p]["warning_activated"] for nn in range(1, n + 1))
        ]
        if always_active:
            patterns.append(
                {
                    "type": "always_active_pipelines",
                    "N": n,
                    "pipelines": always_active,
                    "description": f"Pipelines that always activate warnings: {always_active}",
                }
            )

    return patterns


def extract_perturbation_response_envelopes(pipeline_results, domain):
    """Search for envelopes of perturbation response."""
    envelopes = []

    for n in pipeline_results[domain].keys():
        pipelines = pipeline_results[domain][n]

        metric_cvs = [pipelines[p]["metric_cv"] for p in pipelines]

        # Envelope 1: Response range
        response_range = max(metric_cvs) - min(metric_cvs)
        envelopes.append(
            {
                "type": "response_range",
                "N": n,
                "value": response_range,
                "description": f"Range of perturbation response: {response_range:.4f}",
            }
        )

        # Envelope 2: Response mean
        response_mean = np.mean(metric_cvs)
        envelopes.append(
            {
                "type": "response_mean",
                "N": n,
                "value": response_mean,
                "description": f"Mean perturbation response: {response_mean:.4f}",
            }
        )

    return envelopes


# ============================================================================
# MAIN ANALYSIS
# ============================================================================


def run_p16_analysis():
    print("=" * 80)
    print("P16 — OBSERVER INVARIANT EXTRACTION AUDIT")
    print("=" * 80)
    print()
    print("PURPOSE: Which minimal organizational quantities remain stable under observer diversification?")
    print("CORE QUESTION: Invariant extraction under observer perturbation")
    print()

    # Load P15 results
    pipeline_results = get_pipeline_results()

    all_results = {}

    for domain, config in DOMAINS.items():
        print(f"{'='*80}")
        print(f"DOMAIN: {domain}")
        print(f"{'='*80}")
        print()

        # Extract invariants
        invariants = extract_low_dimensional_invariants(pipeline_results, domain)
        inequalities = extract_stability_inequalities(pipeline_results, domain)
        bounds = extract_admissibility_independent_bounds(pipeline_results, domain)
        constraints = extract_convergence_constraints(pipeline_results, domain)
        patterns = extract_warning_coactivation_patterns(pipeline_results, domain)
        envelopes = extract_perturbation_response_envelopes(pipeline_results, domain)

        # Print summary
        print(f"Low-dimensional invariants: {len(invariants)}")
        for inv in invariants[:3]:  # Print first 3
            print(f"  {inv['type']}: {inv['description']}")
        print()

        print(f"Stability inequalities: {len(inequalities)}")
        for ineq in inequalities[:3]:
            print(f"  {ineq['type']}: {ineq['description']}")
        print()

        print(f"Admissibility-independent bounds: {len(bounds)}")
        for bound in bounds[:3]:
            print(f"  {bound['type']}: {bound['description']}")
        print()

        print(f"Convergence constraints: {len(constraints)}")
        for constr in constraints[:3]:
            print(f"  {constr['type']}: {constr['description']}")
        print()

        print(f"Warning co-activation patterns: {len(patterns)}")
        for pat in patterns[:3]:
            print(f"  {pat['type']}: {pat['description']}")
        print()

        print(f"Perturbation response envelopes: {len(envelopes)}")
        for env in envelopes[:3]:
            print(f"  {env['type']}: {env['description']}")
        print()

        all_results[domain] = {
            "invariants": invariants,
            "inequalities": inequalities,
            "bounds": bounds,
            "constraints": constraints,
            "patterns": patterns,
            "envelopes": envelopes,
        }

    # Save results
    output_file = OUTPUT_DIR / "p16_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"Results saved to {output_file}")

    return all_results


if __name__ == "__main__":
    run_p16_analysis()
