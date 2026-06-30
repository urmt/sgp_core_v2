"""
Core collapse dynamics engine for Phase 005A Division 1.

Implements dual-framework comparative architecture:
  TRACK A (Parallel) — independent representational/functional evolution
  TRACK B (Coupled) — measurable interaction structure between representation and function

Systems: DistributedSystem, ImmuneSignalingNetwork, InstitutionSystem, AntColony
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from scipy.stats import spearmanr

from .metrics import VelocityMetrics, AccelerationMetrics, CurvatureMetrics, HysteresisMetrics
from .validation import ConstraintValidator
from .output import CollapseResults


class CollapsePattern(Enum):
    GRADUAL_CASCADE = "gradual_cascade"
    ABRUPT_COLLAPSE = "abrupt_collapse"
    SEQUENTIAL_CHAIN = "sequential_chain"
    PARALLEL_COLLAPSE = "parallel_collapse"
    RESISTANT_DEGRADATION = "resistant_degradation"


class CollapseState(Enum):
    INITIALIZING = "initializing"
    STABLE = "stable"
    DEGRADING = "degrading"
    CRITICAL = "critical"
    COLLAPSED = "collapsed"
    RECOVERED = "recovered"


@dataclass
class CollapseObservation:
    step: int
    timestamp: float
    state: CollapseState
    velocity_magnitude: float
    acceleration_magnitude: float
    curvature_value: float
    hysteresis_indicator: float
    system_metrics: Dict[str, float] = field(default_factory=dict)
    trajectory_point: Tuple[float, ...] = field(default_factory=tuple)


@dataclass
class CollapseEvent:
    start_step: int
    end_step: int
    pattern_type: CollapsePattern
    magnitude_change: float
    duration_steps: int
    characteristic_velocity: float
    descriptive_metrics: Dict[str, float] = field(default_factory=dict)
    associated_factors: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# System definitions (self-contained, no external dependencies)
# ---------------------------------------------------------------------------

class DistributedSystem:
    """Distributed processing system with coupling-weighted adjacency."""

    def __init__(self, n_nodes: int = 20, coupling: float = 0.5, noise: float = 0.01):
        self.n_nodes = n_nodes
        self.coupling = coupling
        self.noise = noise
        state = np.random.randn(n_nodes) * 0.1
        self.state = state
        adj = np.random.randn(n_nodes, n_nodes) * 0.1
        np.fill_diagonal(adj, 0.0)
        self.adjacency = adj
        self.original_adj = adj.copy()

    def step(self) -> float:
        interaction = self.adjacency @ self.state * self.coupling
        self.state = np.tanh(self.state + interaction + np.random.randn(self.n_nodes) * self.noise)
        return float(np.mean(np.abs(self.state)))

    def representational_ed(self) -> float:
        return float(np.mean(
            np.linalg.norm(self.state[:, None] - self.state[None, :], axis=-1)
        ))

    def functional_performance(self) -> float:
        return float(1.0 / (1.0 + np.std(self.state)))


class ImmuneSignalingNetwork:
    """Immune signaling with pathogen load tracking."""

    def __init__(self, n_signals: int = 10, coupling: float = 0.3):
        self.n_signals = n_signals
        self.coupling = coupling
        self.cytokine_levels = np.random.rand(n_signals) * 0.1
        self.pathogen_load = 1.0
        self.immune_response = np.zeros(n_signals)
        adj = np.random.randn(n_signals, n_signals) * 0.05
        np.fill_diagonal(adj, 0.0)
        self.adjacency = adj

    def step(self) -> float:
        self.pathogen_load *= (1.0 + np.random.randn() * 0.05)
        self.pathogen_load = max(self.pathogen_load, 0.01)
        signal = self.adjacency @ self.cytokine_levels * self.coupling
        self.immune_response = np.tanh(self.cytokine_levels + signal)
        self.cytokine_levels += self.immune_response * 0.1 - self.cytokine_levels * 0.05
        self.cytokine_levels += np.random.randn(self.n_signals) * 0.01
        return float(self.pathogen_load)

    def representational_ed(self) -> float:
        return float(np.mean(
            np.linalg.norm(self.cytokine_levels[:, None] - self.cytokine_levels[None, :], axis=-1)
        ))

    def functional_performance(self) -> float:
        return float(1.0 / (1.0 + self.pathogen_load))


class InstitutionSystem:
    """Institutional stability with policy coupling."""

    def __init__(self, n_institutions: int = 8, coupling: float = 0.4):
        self.n_institutions = n_institutions
        self.coupling = coupling
        self.trust_levels = np.random.rand(n_institutions) * 0.5 + 0.25
        self.policy_compliance = np.random.rand(n_institutions) * 0.5 + 0.25
        self.external_pressure = 0.0
        adj = np.random.randn(n_institutions, n_institutions) * 0.05
        np.fill_diagonal(adj, 0.0)
        self.adjacency = adj

    def step(self) -> float:
        self.external_pressure += np.random.randn() * 0.02
        influence = self.adjacency @ self.trust_levels * self.coupling
        self.trust_levels += influence * 0.1 - (self.trust_levels - 0.5) * 0.02
        self.trust_levels = np.clip(self.trust_levels, 0.0, 1.0)
        self.policy_compliance = np.clip(
            self.policy_compliance + self.trust_levels * 0.01 - self.external_pressure * 0.005
            + np.random.randn(self.n_institutions) * 0.005,
            0.0, 1.0
        )
        return float(np.mean(self.policy_compliance))

    def representational_ed(self) -> float:
        return float(np.mean(
            np.linalg.norm(self.trust_levels[:, None] - self.trust_levels[None, :], axis=-1)
        ))

    def functional_performance(self) -> float:
        return float(np.mean(self.policy_compliance))


class AntColony:
    """Ant colony foraging with pheromone-based coordination."""

    def __init__(self, n_regions: int = 15, coupling: float = 0.5):
        self.n_regions = n_regions
        self.coupling = coupling
        self.food_sources = np.random.rand(n_regions) * 0.3
        self.pheromone_levels = np.zeros(n_regions)
        self.foraging_activity = np.random.rand(n_regions) * 0.1
        adj = np.random.randn(n_regions, n_regions) * 0.1
        np.fill_diagonal(adj, 0.0)
        self.adjacency = adj

    def step(self) -> float:
        self.food_sources += np.random.randn(self.n_regions) * 0.01
        self.food_sources = np.maximum(self.food_sources, 0.0)
        diffusion = self.adjacency @ self.pheromone_levels * self.coupling
        self.pheromone_levels = np.tanh(self.pheromone_levels + diffusion)
        self.pheromone_levels += self.food_sources * 0.1
        self.pheromone_levels *= 0.95
        self.foraging_activity = np.tanh(self.pheromone_levels * 2.0)
        return float(np.mean(self.foraging_activity))

    def representational_ed(self) -> float:
        return float(np.mean(
            np.linalg.norm(self.pheromone_levels[:, None] - self.pheromone_levels[None, :], axis=-1)
        ))

    def functional_performance(self) -> float:
        return float(np.mean(self.foraging_activity))


# ---------------------------------------------------------------------------
# TRACK A: Parallel Dynamics — independent representational/functional evolution
# ---------------------------------------------------------------------------

class ParallelDynamicsAnalyzer:
    """
    TRACK A: Analyzes representation and function as independently evolving.
    Computes separate trajectories and quantifies their divergence.
    """

    def __init__(self, n_steps: int = 300):
        self.n_steps = n_steps

    def analyze(self, system) -> Dict:
        steps = self.n_steps
        rep_ed_traj = np.zeros(steps)
        func_traj = np.zeros(steps)

        for t in range(steps):
            system.step()
            rep_ed_traj[t] = system.representational_ed()
            func_traj[t] = system.functional_performance()

        rep_normalized = rep_ed_traj / (rep_ed_traj[0] + 1e-10)
        func_normalized = func_traj / (func_traj[0] + 1e-10)

        divergence = np.abs(rep_normalized - func_normalized)

        final_divergence = float(divergence[-1])
        max_divergence = float(np.max(divergence))
        mean_divergence = float(np.mean(divergence))

        if len(divergence) > 10:
            rho, p = spearmanr(rep_normalized, func_normalized)
            correlation = float(rho)
            p_value = float(p)
        else:
            correlation = 0.0
            p_value = 1.0

        rep_final = float(rep_normalized[-1])
        func_final = float(func_normalized[-1])
        rep_recovery = (rep_final - 1.0) * 100
        func_recovery = (func_final - 1.0) * 100

        return {
            'track': 'A_parallel',
            'representational_trajectory': rep_normalized.tolist(),
            'functional_trajectory': func_normalized.tolist(),
            'divergence_trajectory': divergence.tolist(),
            'final_divergence': final_divergence,
            'max_divergence': max_divergence,
            'mean_divergence': mean_divergence,
            'rep_final_normalized': rep_final,
            'func_final_normalized': func_final,
            'rep_recovery_pct': rep_recovery,
            'func_recovery_pct': func_recovery,
            'spearman_correlation': correlation,
            'spearman_p_value': p_value,
            'dissociation_detected': abs(rep_recovery - func_recovery) > 5.0,
            'interpretation': self._interpret(final_divergence, correlation, rep_recovery, func_recovery)
        }

    def _interpret(self, divergence: float, correlation: float,
                   rep_recovery: float, func_recovery: float) -> str:
        if divergence < 0.05:
            return "parallel_trajectories: representation and function evolve together"
        if abs(rep_recovery) > 5 * abs(func_recovery):
            return "representation_outpaces_function: representational change exceeds functional change"
        if abs(func_recovery) > 5 * abs(rep_recovery):
            return "function_outpaces_representation: functional change exceeds representational change"
        if rep_recovery > 0 and func_recovery < 0:
            return "dissociation: representation recovers while function declines"
        if rep_recovery < 0 and func_recovery > 0:
            return "dissociation: function recovers while representation declines"
        return "moderate_divergence: representation and function partially decoupled"


# ---------------------------------------------------------------------------
# TRACK B: Coupled Dynamics — measurable interaction structure
# ---------------------------------------------------------------------------

class CoupledDynamicsAnalyzer:
    """
    TRACK B: Analyzes coupled representation-function dynamics.
    Measures interaction structure, cross-prediction, and lead-lag relationships.
    """

    def __init__(self, n_steps: int = 300, max_lag: int = 10):
        self.n_steps = n_steps
        self.max_lag = max_lag

    def analyze(self, system) -> Dict:
        steps = self.n_steps
        rep_ed_traj = np.zeros(steps)
        func_traj = np.zeros(steps)

        for t in range(steps):
            system.step()
            rep_ed_traj[t] = system.representational_ed()
            func_traj[t] = system.functional_performance()

        rep_normalized = rep_ed_traj / (rep_ed_traj[0] + 1e-10)
        func_normalized = func_traj / (func_traj[0] + 1e-10)

        cross_corr = self._cross_correlation(rep_normalized, func_normalized)
        optimal_lag = int(np.argmax(np.abs(cross_corr)) - self.max_lag)
        max_cross_corr = float(np.max(np.abs(cross_corr)))

        coupling_strength = self._compute_coupling_strength(rep_normalized, func_normalized)

        lead_lag = "rep_leads_func" if optimal_lag < 0 else "func_leads_rep" if optimal_lag > 0 else "synchronous"

        if len(rep_normalized) > 10:
            rho, p = spearmanr(rep_normalized, func_normalized)
            correlation = float(rho)
            p_value = float(p)
        else:
            correlation = 0.0
            p_value = 1.0

        return {
            'track': 'B_coupled',
            'representational_trajectory': rep_normalized.tolist(),
            'functional_trajectory': func_normalized.tolist(),
            'cross_correlation': cross_corr.tolist(),
            'optimal_lag_steps': int(optimal_lag),
            'max_cross_correlation': max_cross_corr,
            'coupling_strength': float(coupling_strength),
            'lead_lag_relationship': lead_lag,
            'spearman_correlation': correlation,
            'spearman_p_value': p_value,
            'interaction_detected': max_cross_corr > 0.3,
            'interpretation': self._interpret(coupling_strength, max_cross_corr, lead_lag, correlation)
        }

    def _cross_correlation(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        lags = np.arange(-self.max_lag, self.max_lag + 1)
        result = np.zeros(len(lags))
        a_norm = (a - np.mean(a)) / (np.std(a) + 1e-10)
        b_norm = (b - np.mean(b)) / (np.std(b) + 1e-10)
        for i, lag in enumerate(lags):
            if lag < 0:
                x, y = a_norm[-lag:], b_norm[:lag]
            elif lag > 0:
                x, y = a_norm[lag:], b_norm[:-lag]
            else:
                x, y = a_norm, b_norm
            if len(x) > 1 and np.std(x) > 1e-10 and np.std(y) > 1e-10:
                result[i] = np.corrcoef(x, y)[0, 1]
            else:
                result[i] = 0.0
        return result

    def _compute_coupling_strength(self, a: np.ndarray, b: np.ndarray) -> float:
        diffs_a = np.diff(a)
        diffs_b = np.diff(b)
        if len(diffs_a) < 2:
            return 0.0
        return float(np.mean(np.abs(diffs_a * diffs_b)) / (np.std(diffs_a) * np.std(diffs_b) + 1e-10))

    def _interpret(self, coupling: float, cross_corr: float,
                   lead_lag: str, correlation: float) -> str:
        if coupling < 0.1 and cross_corr < 0.2:
            return "weak_coupling: representation and function evolve largely independently"
        if coupling > 0.5 or cross_corr > 0.6:
            return f"strong_coupling: {lead_lag} with correlation {correlation:.3f}"
        return f"moderate_coupling: {lead_lag}, cross-correlation {cross_corr:.3f}"


# ---------------------------------------------------------------------------
# Comparative Evaluator
# ---------------------------------------------------------------------------

class ComparativeEvaluator:
    """
    Compares TRACK A and TRACK B results across systems.
    Determines which framework better describes observed dynamics.
    """

    @staticmethod
    def evaluate(track_a_results: Dict, track_b_results: Dict) -> Dict:
        divergence = track_a_results.get('final_divergence', 0.0)
        coupling = track_b_results.get('coupling_strength', 0.0)
        cross_corr = track_b_results.get('max_cross_correlation', 0.0)
        correlation_a = track_a_results.get('spearman_correlation', 0.0)
        correlation_b = track_b_results.get('spearman_correlation', 0.0)

        if divergence < 0.05:
            parallel_support = 1.0
        elif divergence < 0.15:
            parallel_support = 0.5
        else:
            parallel_support = 0.0

        if coupling > 0.3 or cross_corr > 0.4:
            coupled_support = 1.0
        elif coupling > 0.15 or cross_corr > 0.2:
            coupled_support = 0.5
        else:
            coupled_support = 0.0

        evidence_gap = coupled_support - parallel_support

        if evidence_gap > 0.3:
            recommendation = "TRACK_B_coupled_favored"
        elif evidence_gap < -0.3:
            recommendation = "TRACK_A_parallel_favored"
        else:
            recommendation = "inconclusive_both_frameworks_possible"

        return {
            'parallel_support_score': parallel_support,
            'coupled_support_score': coupled_support,
            'evidence_gap': evidence_gap,
            'recommendation': recommendation,
            'track_a_correlation': correlation_a,
            'track_b_correlation': correlation_b,
            'key_factors': {
                'divergence': divergence,
                'coupling_strength': coupling,
                'cross_correlation': cross_corr
            }
        }


# ---------------------------------------------------------------------------
# CollapseDynamics — main orchestration class
# ---------------------------------------------------------------------------

class CollapseDynamics:
    """
    Empirical analysis of system collapse dynamics.

    Provides descriptive pattern recognition and classification
    of collapse events using dual-framework (TRACK A / TRACK B) architecture.
    """

    def __init__(self, n_steps: int = 300, max_lag: int = 10):
        self.n_steps = n_steps
        self.max_lag = max_lag
        self.parallel_analyzer = ParallelDynamicsAnalyzer(n_steps)
        self.coupled_analyzer = CoupledDynamicsAnalyzer(n_steps, max_lag)
        self.evaluator = ComparativeEvaluator()

    def analyze_system(self, system, system_name: str) -> Dict:
        track_a = self.parallel_analyzer.analyze(system)
        track_b = self.coupled_analyzer.analyze(system)
        comparison = self.evaluator.evaluate(track_a, track_b)
        return {
            'system_name': system_name,
            'system_type': type(system).__name__,
            'track_a': track_a,
            'track_b': track_b,
            'comparison': comparison
        }

    def run_all_systems(self, base_coupling: float = 0.5) -> Dict:
        systems = [
            (DistributedSystem(coupling=base_coupling), "distributed"),
            (ImmuneSignalingNetwork(coupling=base_coupling * 0.6), "immune"),
            (InstitutionSystem(coupling=base_coupling * 0.8), "institution"),
            (AntColony(coupling=base_coupling), "ant_colony"),
        ]
        results = {}
        for system, name in systems:
            results[name] = self.analyze_system(system, name)
        return results

    def compute_trajectory_metrics(self, trajectory):
        return {
            'velocity': VelocityMetrics.calculate_velocity(trajectory).tolist(),
            'acceleration': AccelerationMetrics.calculate_acceleration(
                VelocityMetrics.calculate_velocity(trajectory)
            ).tolist(),
            'curvature': CurvatureMetrics.calculate_curvature(trajectory).tolist(),
            'hysteresis': HysteresisMetrics.calculate_hysteresis_indicator(trajectory).tolist()
        }

    def validate_empirical_consistency(self, results: Dict, constraints: List[Dict]) -> Dict:
        return ConstraintValidator().validate_empirical_constraints(results, constraints)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    print("=" * 64)
    print("  Phase 005A Division 1 — Core Collapse Dynamics Engine")
    print("  Dual-Framework: TRACK A (Parallel) vs TRACK B (Coupled)")
    print("=" * 64)

    engine = CollapseDynamics(n_steps=200)
    results = engine.run_all_systems(base_coupling=0.5)

    for sys_name, sys_results in results.items():
        print(f"\n{'─' * 50}")
        print(f"  System: {sys_name} ({sys_results['system_type']})")
        print(f"{'─' * 50}")

        ta = sys_results['track_a']
        print(f"  TRACK A — Parallel:")
        print(f"    Final divergence:      {ta['final_divergence']:.4f}")
        print(f"    Max divergence:        {ta['max_divergence']:.4f}")
        print(f"    Rep recovery:          {ta['rep_recovery_pct']:.2f}%")
        print(f"    Func recovery:         {ta['func_recovery_pct']:.2f}%")
        print(f"    Spearman ρ:            {ta['spearman_correlation']:.4f}")
        print(f"    Dissociation detected: {ta['dissociation_detected']}")
        print(f"    Interpretation:        {ta['interpretation']}")

        tb = sys_results['track_b']
        print(f"  TRACK B — Coupled:")
        print(f"    Coupling strength:     {tb['coupling_strength']:.4f}")
        print(f"    Max cross-correlation: {tb['max_cross_correlation']:.4f}")
        print(f"    Optimal lag:           {tb['optimal_lag_steps']} steps")
        print(f"    Lead-lag:              {tb['lead_lag_relationship']}")
        print(f"    Spearman ρ:            {tb['spearman_correlation']:.4f}")
        print(f"    Interaction detected:  {tb['interaction_detected']}")
        print(f"    Interpretation:        {tb['interpretation']}")

        comp = sys_results['comparison']
        print(f"  COMPARISON:")
        print(f"    Parallel support:      {comp['parallel_support_score']:.2f}")
        print(f"    Coupled support:       {comp['coupled_support_score']:.2f}")
        print(f"    Evidence gap:          {comp['evidence_gap']:.2f}")
        print(f"    Recommendation:        {comp['recommendation']}")

    print(f"\n{'=' * 64}")
    print("  Analysis complete.")
    print(f"{'=' * 64}")

    return results


if __name__ == "__main__":
    main()
