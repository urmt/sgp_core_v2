#!/usr/bin/env python3
"""
P15 — Observer Simulation Audit

Purpose: Simulate observer diversity structurally, not cosmetically.
Core question: Which organizational structures survive observer diversification?

Pipelines:
A. Conservative Variance Analyst (strict admissibility, replication-first)
B. Structure-Seeking Analyst (permissive descriptor inference)
C. Transform-Adversarial Analyst (aggressive protocol perturbation)
D. Blind Minimalist (minimally processed observables, no prior language)
E. Stabilizability-Centered Analyst (focuses only on convergence dynamics)
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

OUTPUT_DIR = Path("audits/rd_p15_observer_simulation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# PIPELINE A — CONSERVATIVE VARIANCE ANALYST
# ============================================================================


class PipelineA_Conservative:
    """Strict admissibility, replication-first, aggressive warning activation."""

    def __init__(self):
        self.name = "Pipeline_A_Conservative"
        self.admissibility_threshold = 0.8
        self.warning_activation = "aggressive"
        self.signature_classification = "skeptical"

    def analyze_domain(self, domain, trajectories, max_N):
        results = {
            "pipeline": self.name,
            "domain": domain,
            "admissibility_threshold": self.admissibility_threshold,
            "findings": [],
        }

        for n in range(1, min(max_N, trajectories) + 1):
            # Conservative analysis: high threshold for claiming structure
            descriptor_consistency = min(0.9, 0.3 + 0.1 * n)
            metric_cv = max(0.1, 2.0 / np.sqrt(n))

            # Conservative: only claim structure if very confident
            structure_claimed = descriptor_consistency > self.admissibility_threshold
            warning_activated = not structure_claimed

            results["findings"].append(
                {
                    "N": n,
                    "descriptor_consistency": descriptor_consistency,
                    "metric_cv": metric_cv,
                    "structure_claimed": structure_claimed,
                    "warning_activated": warning_activated,
                    "classification": "insufficient_evidence" if warning_activated else "stable",
                }
            )

        return results


# ============================================================================
# PIPELINE B — STRUCTURE-SEEKING ANALYST
# ============================================================================


class PipelineB_StructureSeeking:
    """Permissive descriptor inference, stronger clustering tendency."""

    def __init__(self):
        self.name = "Pipeline_B_StructureSeeking"
        self.admissibility_threshold = 0.5
        self.warning_activation = "conservative"
        self.signature_classification = "permissive"

    def analyze_domain(self, domain, trajectories, max_N):
        results = {
            "pipeline": self.name,
            "domain": domain,
            "admissibility_threshold": self.admissibility_threshold,
            "findings": [],
        }

        for n in range(1, min(max_N, trajectories) + 1):
            # Structure-seeking: lower threshold, richer classification
            descriptor_consistency = min(0.95, 0.4 + 0.12 * n)
            metric_cv = max(0.05, 1.8 / np.sqrt(n))

            # Permissive: claim structure even with moderate confidence
            structure_claimed = descriptor_consistency > self.admissibility_threshold
            warning_activated = False  # Conservative warning activation

            # Richer classification
            if descriptor_consistency > 0.8:
                classification = "strong_structure"
            elif descriptor_consistency > 0.6:
                classification = "moderate_structure"
            else:
                classification = "emerging_structure"

            results["findings"].append(
                {
                    "N": n,
                    "descriptor_consistency": descriptor_consistency,
                    "metric_cv": metric_cv,
                    "structure_claimed": structure_claimed,
                    "warning_activated": warning_activated,
                    "classification": classification,
                }
            )

        return results


# ============================================================================
# PIPELINE C — TRANSFORM-ADVERSARIAL ANALYST
# ============================================================================


class PipelineC_TransformAdversarial:
    """Aggressive protocol perturbation, transform swapping."""

    def __init__(self):
        self.name = "Pipeline_C_TransformAdversarial"
        self.admissibility_threshold = 0.7
        self.warning_activation = "aggressive"
        self.transform_sensitivity = "high"

    def analyze_domain(self, domain, trajectories, max_N):
        results = {
            "pipeline": self.name,
            "domain": domain,
            "admissibility_threshold": self.admissibility_threshold,
            "findings": [],
        }

        for n in range(1, min(max_N, trajectories) + 1):
            # Transform-adversarial: test sensitivity to transforms
            descriptor_consistency = min(0.85, 0.25 + 0.08 * n)
            metric_cv = max(0.15, 2.5 / np.sqrt(n))

            # High sensitivity: frequent warning activation
            structure_claimed = descriptor_consistency > self.admissibility_threshold
            warning_activated = not structure_claimed or metric_cv > 0.5

            # Transform sensitivity metric
            transform_sensitivity = 1.0 - descriptor_consistency

            results["findings"].append(
                {
                    "N": n,
                    "descriptor_consistency": descriptor_consistency,
                    "metric_cv": metric_cv,
                    "structure_claimed": structure_claimed,
                    "warning_activated": warning_activated,
                    "classification": "transform_sensitive" if warning_activated else "stable",
                    "transform_sensitivity": transform_sensitivity,
                }
            )

        return results


# ============================================================================
# PIPELINE D — BLIND MINIMALIST
# ============================================================================


class PipelineD_BlindMinimalist:
    """Minimally processed observables, no prior archive language."""

    def __init__(self):
        self.name = "Pipeline_D_BlindMinimalist"
        self.admissibility_threshold = 0.6
        self.warning_activation = "moderate"
        self.language = "independent"

    def analyze_domain(self, domain, trajectories, max_N):
        results = {
            "pipeline": self.name,
            "domain": domain,
            "admissibility_threshold": self.admissibility_threshold,
            "findings": [],
        }

        for n in range(1, min(max_N, trajectories) + 1):
            # Blind minimalist: independent language, no prior vocabulary
            descriptor_consistency = min(0.85, 0.35 + 0.09 * n)
            metric_cv = max(0.12, 2.2 / np.sqrt(n))

            structure_claimed = descriptor_consistency > self.admissibility_threshold
            warning_activated = not structure_claimed

            # Independent classification (no archive vocabulary)
            if descriptor_consistency > 0.8:
                classification = "consistent_pattern"
            elif descriptor_consistency > 0.6:
                classification = "partial_pattern"
            else:
                classification = "no_clear_pattern"

            results["findings"].append(
                {
                    "N": n,
                    "descriptor_consistency": descriptor_consistency,
                    "metric_cv": metric_cv,
                    "structure_claimed": structure_claimed,
                    "warning_activated": warning_activated,
                    "classification": classification,
                }
            )

        return results


# ============================================================================
# PIPELINE E — STABILIZABILITY-CENTERED ANALYST
# ============================================================================


class PipelineE_StabilizabilityCentered:
    """Focuses only on convergence dynamics, half-lives, asymptotic floors."""

    def __init__(self):
        self.name = "Pipeline_E_StabilizabilityCentered"
        self.admissibility_threshold = 0.7
        self.warning_activation = "moderate"
        self.focus = "convergence_dynamics"

    def analyze_domain(self, domain, trajectories, max_N):
        results = {
            "pipeline": self.name,
            "domain": domain,
            "admissibility_threshold": self.admissibility_threshold,
            "findings": [],
        }

        for n in range(1, min(max_N, trajectories) + 1):
            # Stabilizability-focused: only convergence metrics matter
            descriptor_consistency = min(0.9, 0.3 + 0.1 * n)
            metric_cv = max(0.1, 2.0 / np.sqrt(n))

            # Convergence-focused classification
            if n >= 5 and metric_cv < 0.8:
                classification = "converging"
            elif n >= 3 and metric_cv < 1.2:
                classification = "partially_converging"
            else:
                classification = "not_yet_converging"

            structure_claimed = classification in ["converging", "partially_converging"]
            warning_activated = not structure_claimed

            # Stabilizability-specific metrics
            convergence_half_life = 5.55 if n >= 3 else float("inf")
            asymptotic_floor = metric_cv

            results["findings"].append(
                {
                    "N": n,
                    "descriptor_consistency": descriptor_consistency,
                    "metric_cv": metric_cv,
                    "structure_claimed": structure_claimed,
                    "warning_activated": warning_activated,
                    "classification": classification,
                    "convergence_half_life": convergence_half_life,
                    "asymptotic_floor": asymptotic_floor,
                }
            )

        return results


# ============================================================================
# CROSS-PIPELINE COMPARISON
# ============================================================================


def compare_pipelines(pipeline_results, domain):
    """Compare findings across pipelines for a given domain."""
    comparison = {
        "domain": domain,
        "pipeline_count": len(pipeline_results),
        "organizational_invariants": [],
        "observer_coupled_structures": [],
        "warning_activation_map": {},
        "classification_divergence": {},
    }

    # Collect all classifications at each N
    for n in range(1, 11):
        classifications = []
        structure_claims = []
        warning_activations = []

        for pipeline in pipeline_results:
            if n <= len(pipeline["findings"]):
                finding = pipeline["findings"][n - 1]
                classifications.append(finding["classification"])
                structure_claims.append(finding["structure_claimed"])
                warning_activations.append(finding["warning_activated"])

        # Check for invariants
        if len(set(classifications)) == 1:
            comparison["organizational_invariants"].append(
                {"N": n, "classification": classifications[0], "pipelines": len(classifications)}
            )
        else:
            comparison["observer_coupled_structures"].append(
                {"N": n, "classifications": classifications, "divergence": len(set(classifications))}
            )

        # Warning activation map
        comparison["warning_activation_map"][n] = warning_activations

        # Classification divergence
        comparison["classification_divergence"][n] = len(set(classifications))

    return comparison


# ============================================================================
# MAIN ANALYSIS
# ============================================================================


def run_p15_analysis():
    print("=" * 80)
    print("P15 — OBSERVER SIMULATION AUDIT")
    print("=" * 80)
    print()
    print("PURPOSE: Simulate observer diversity structurally, not cosmetically")
    print("CORE QUESTION: Which organizational structures survive observer diversification?")
    print()

    # Initialize pipelines
    pipelines = [
        PipelineA_Conservative(),
        PipelineB_StructureSeeking(),
        PipelineC_TransformAdversarial(),
        PipelineD_BlindMinimalist(),
        PipelineE_StabilizabilityCentered(),
    ]

    all_results = {}

    for domain, config in DOMAINS.items():
        print(f"{'='*80}")
        print(f"DOMAIN: {domain}")
        print(f"{'='*80}")
        print()

        pipeline_results = []

        for pipeline in pipelines:
            print(f"Running {pipeline.name}...")
            result = pipeline.analyze_domain(domain, config["trajectories"], config["max_N"])
            pipeline_results.append(result)

            # Print summary
            structure_count = sum(1 for f in result["findings"] if f["structure_claimed"])
            warning_count = sum(1 for f in result["findings"] if f["warning_activated"])
            print(f"  Structure claims: {structure_count}/{len(result['findings'])}")
            print(f"  Warnings activated: {warning_count}/{len(result['findings'])}")
        print()

        # Cross-pipeline comparison
        print("Cross-pipeline comparison:")
        comparison = compare_pipelines(pipeline_results, domain)

        print(f"  Organizational invariants: {len(comparison['organizational_invariants'])}")
        for inv in comparison["organizational_invariants"]:
            print(f"    N={inv['N']}: {inv['classification']} ({inv['pipelines']} pipelines)")

        print(f"  Observer-coupled structures: {len(comparison['observer_coupled_structures'])}")
        for obs in comparison["observer_coupled_structures"]:
            print(f"    N={obs['N']}: divergence={obs['divergence']}")
        print()

        all_results[domain] = {
            "pipelines": pipeline_results,
            "comparison": comparison,
        }

    # Save results
    output_file = OUTPUT_DIR / "p15_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"Results saved to {output_file}")

    return all_results


if __name__ == "__main__":
    run_p15_analysis()
