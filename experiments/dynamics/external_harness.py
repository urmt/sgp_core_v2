"""
External system harness for Phase 005A Division 5 Tier 1 benchmarks.

Runs any system with representational_ed(), functional_performance(), step(), and
coupling attribute through the full dual-framework pipeline.

Generates a report card with TRACK A, TRACK B, hysteresis, and precursor scores.
"""

import numpy as np
from typing import Dict, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.dynamics.collapse_dynamics import (
    ParallelDynamicsAnalyzer,
    CoupledDynamicsAnalyzer,
    ComparativeEvaluator,
)
from experiments.dynamics.precursor_signatures import (
    ParallelPrecursorAnalyzer,
    CoupledPrecursorAnalyzer,
    PrecursorComparativeEvaluator,
    run_coupling_sweep,
)
from experiments.dynamics.hysteresis_topology import (
    run_hysteresis_sweep,
    ParallelHysteresisAnalyzer,
    CoupledHysteresisAnalyzer,
    HysteresisComparativeEvaluator,
)
from experiments.dynamics.metrics import collapse_trajectory_metrics


class ExternalSystemAdapter:
    """
    Wraps any external system for the dual-framework pipeline.

    Required interface: representational_ed(), functional_performance(), step()
    The system must also have a 'coupling' attribute.
    """

    def __init__(self, system):
        self._system = system
        self.coupling = getattr(system, 'coupling', 1.0)

    def representational_ed(self):
        return self._system.representational_ed()

    def functional_performance(self):
        return self._system.functional_performance()

    def step(self):
        return self._system.step()


def _prepare_system(system_class, coupling: float = 1.0, **kwargs):
    """Construct and optionally train a system."""
    sys = system_class(coupling=coupling, **kwargs)
    if hasattr(sys, 'train_readout'):
        sys.train_readout()
    return ExternalSystemAdapter(sys)


def run_full_evaluation(system_class, system_name: str,
                        coupling: float = 1.0,
                        dynamics_steps: int = 200,
                        **system_kwargs) -> Dict:
    """
    Run a complete dual-framework evaluation on an external system.

    Args:
        system_class: Class with representational_ed(), functional_performance(), step(), coupling
        system_name: Human-readable identifier
        coupling: Base coupling value
        dynamics_steps: Steps for dynamics analysis
        system_kwargs: Additional kwargs passed to system constructor

    Returns:
        Report card dict with all scores
    """
    print(f"\n{'=' * 64}")
    print(f"  Evaluating: {system_name}")
    print(f"  Parameters: {system_kwargs}")
    print(f"{'=' * 64}")

    system = _prepare_system(system_class, coupling=coupling, **system_kwargs)

    print(f"\n  [1/4] TRACK A — Parallel Dynamics...")
    pa = ParallelDynamicsAnalyzer(n_steps=dynamics_steps)
    track_a = pa.analyze(system)
    _print_track_a(track_a)

    sys2 = _prepare_system(system_class, coupling=coupling, **system_kwargs)
    print(f"\n  [2/4] TRACK B — Coupled Dynamics...")
    ca = CoupledDynamicsAnalyzer(n_steps=dynamics_steps)
    track_b = ca.analyze(sys2)
    _print_track_b(track_b)

    print(f"\n  [3/4] Hysteresis Sweep...")
    hyst_sweep = run_hysteresis_sweep(
        system_class, base_coupling=coupling, n_levels=10, n_steps_per=15,
        **system_kwargs
    )

    print(f"  [3/4] Hysteresis — TRACK A & B...")
    hyst_a = ParallelHysteresisAnalyzer.analyze(hyst_sweep)
    hyst_b = CoupledHysteresisAnalyzer.analyze(hyst_sweep)
    hyst_c = HysteresisComparativeEvaluator.evaluate(hyst_a, hyst_b)
    _print_hysteresis(hyst_a, hyst_b, hyst_c)

    print(f"\n  [4/4] Precursor Signatures...")
    sweep = run_coupling_sweep(
        system_class, base_coupling=coupling, n_coupling_steps=10, n_steps_per=15,
        **system_kwargs
    )
    rep_traj = np.array(sweep['representational_trajectory'])
    func_traj = np.array(sweep['functional_trajectory'])

    class SweepProxy:
        def __init__(self, rt, ft):
            self._rt, self._ft = rt, ft
            self._i = 0
        def representational_ed(self): return float(self._rt[self._i])
        def functional_performance(self): return float(self._ft[self._i])
        def step(self):
            self._i = min(self._i + 1, len(self._rt) - 1)
            return 0.0
        @property
        def coupling(self): return 1.0

    pp = ParallelPrecursorAnalyzer(n_steps=len(rep_traj))
    pc_a = pp.analyze(SweepProxy(rep_traj, func_traj))
    cp = CoupledPrecursorAnalyzer(n_steps=len(rep_traj))
    pc_b = cp.analyze(SweepProxy(rep_traj, func_traj))
    pc_c = PrecursorComparativeEvaluator.evaluate(pc_a, pc_b)
    _print_precursors(pc_a, pc_b, pc_c)

    comp = ComparativeEvaluator.evaluate(track_a, track_b)
    report = {
        'system_name': system_name,
        'system_class': system_class.__name__,
        'coupling': coupling,
        'track_a': track_a,
        'track_b': track_b,
        'comparison': comp,
        'hysteresis': {'track_a': hyst_a, 'track_b': hyst_b, 'comparison': hyst_c},
        'precursors': {'track_a': pc_a, 'track_b': pc_b, 'comparison': pc_c},
        'sweep': {
            'ed_change_pct': sweep['ed_change_pct'],
            'func_change_pct': sweep['func_change_pct'],
        }
    }
    _print_report_card(report)
    return report


def _print_track_a(ta: Dict):
    print(f"    Divergence:    {ta['final_divergence']:.4f} (max {ta['max_divergence']:.4f})")
    print(f"    Rep recovery:  {ta['rep_recovery_pct']:+.2f}%")
    print(f"    Func recovery: {ta['func_recovery_pct']:+.2f}%")
    print(f"    Spearman ρ:    {ta['spearman_correlation']:.4f}")
    print(f"    Dissociation:  {ta['dissociation_detected']}")
    print(f"    → {ta['interpretation']}")


def _print_track_b(tb: Dict):
    print(f"    Coupling str:  {tb['coupling_strength']:.4f}")
    print(f"    Cross-corr:    {tb['max_cross_correlation']:.4f}")
    print(f"    Lead-lag:      {tb['lead_lag_relationship']} ({tb['optimal_lag_steps']} steps)")
    print(f"    Spearman ρ:    {tb['spearman_correlation']:.4f}")
    print(f"    Interaction:   {tb['interaction_detected']}")
    print(f"    → {tb['interpretation']}")


def _print_hysteresis(ha: Dict, hb: Dict, hc: Dict):
    print(f"    TRACK A — Rep loop: {ha['representational']['loop_area']:.2f}, "
          f"rev: {ha['representational']['reversibility']:.3f}")
    print(f"    TRACK A — Func loop: {ha['functional']['loop_area']:.2f}, "
          f"rev: {ha['functional']['reversibility']:.3f}")
    print(f"    TRACK B — Coupled hyst: {hb['coupling_hysteresis']:.4f}, "
          f"interaction asym: {hb['interaction_asymmetry']:.4f}")
    print(f"    Winner: {hc['winner']} — {hc['reason']}")


def _print_precursors(pa: Dict, pb: Dict, pc: Dict):
    print(f"    TRACK A — Rep signals: {pa['total_rep_signals']}, "
          f"Func signals: {pa['total_func_signals']}")
    print(f"    TRACK B — Coupled signals: {pb['total_coupled_signals']}")
    print(f"    Winner: {pc['winner']} — {pc['reason']}")


def _print_report_card(report: Dict):
    comp = report['comparison']
    hc = report['hysteresis']['comparison']
    pc = report['precursors']['comparison']
    sweep = report['sweep']

    print(f"\n{'=' * 64}")
    print(f"  REPORT CARD — {report['system_name']}")
    print(f"{'=' * 64}")
    print(f"  Coupling sweep: ED {sweep['ed_change_pct']:+.2f}%, "
          f"Func {sweep['func_change_pct']:+.2f}%")
    print(f"  Dynamics:       {comp['recommendation']} "
          f"(gap={comp['evidence_gap']:.2f})")
    print(f"  Hysteresis:     {hc['winner']} ({hc['reason']})")
    print(f"  Precursors:     {pc['winner']} ({pc['reason']})")
    print(f"{'=' * 64}")


def main():
    from experiments.dynamics.external.hopfield_recall import HopfieldRecallSystem
    from experiments.dynamics.external.kuramoto_grid import KuramotoGridSystem
    from experiments.dynamics.external.reservoir_echo import ReservoirSystem
    from experiments.dynamics.external.gene_regulatory import GeneRegulatorySystem

    configs = [
        ("hopfield_std", HopfieldRecallSystem, 1.0, {'n_neurons': 100, 'n_patterns': 10, 'noise_std': 0.05}),
        ("hopfield_low_N", HopfieldRecallSystem, 1.0, {'n_neurons': 100, 'n_patterns': 10, 'noise_std': 0.01}),
        ("hopfield_high_N", HopfieldRecallSystem, 1.0, {'n_neurons': 100, 'n_patterns': 10, 'noise_std': 0.15}),
        ("hopfield_many_P", HopfieldRecallSystem, 1.0, {'n_neurons': 100, 'n_patterns': 20, 'noise_std': 0.05}),
        ("kuramoto_std", KuramotoGridSystem, 2.0, {'n_oscillators': 64, 'noise_std': 0.05}),
        ("kuramoto_low_K", KuramotoGridSystem, 0.5, {'n_oscillators': 64, 'noise_std': 0.05}),
        ("kuramoto_high_N", KuramotoGridSystem, 2.0, {'n_oscillators': 64, 'noise_std': 0.15}),
        ("reservoir_std", ReservoirSystem, 0.9, {'n_units': 100, 'noise_std': 0.01}),
        ("reservoir_low_sr", ReservoirSystem, 0.5, {'n_units': 100, 'noise_std': 0.01}),
        ("reservoir_high_N", ReservoirSystem, 0.9, {'n_units': 100, 'noise_std': 0.05}),
        ("gene_std", GeneRegulatorySystem, 1.0, {'n_genes': 50, 'noise_std': 0.02}),
        ("gene_low_N", GeneRegulatorySystem, 1.0, {'n_genes': 50, 'noise_std': 0.005}),
        ("gene_high_N", GeneRegulatorySystem, 1.0, {'n_genes': 50, 'noise_std': 0.08}),
    ]

    results = {}
    for name, cls, coupling, kwargs in configs:
        results[name] = run_full_evaluation(cls, name, coupling=coupling, dynamics_steps=200, **kwargs)

    print(f"\n{'=' * 64}")
    print(f"  TIER 1 SUMMARY — Hopfield Recall Benchmark")
    print(f"{'=' * 64}")
    print(f"  {'Config':<25} {'Dynamics':<10} {'Hysteresis':<10} "
          f"{'P1 OK?':<8} {'P2 OK?':<8} {'Dissociation':<22}")
    print(f"  {'─'*25} {'─'*10} {'─'*10} {'─'*8} {'─'*8} {'─'*22}")
    for name, r in results.items():
        dyn = "B_short" if r['comparison']['evidence_gap'] > 0 else "A_long"
        hys = "A_long" if r['hysteresis']['comparison']['winner'] == 'A_parallel' else "B_short"
        p1_ok = (dyn == "B_short" and hys == "A_long")
        ta = r['track_a']
        p2_ok = ta['dissociation_detected']
        print(f"  {name:<25} {dyn:<10} {hys:<10} "
              f"{'✓' if p1_ok else '✗':<8} {'✓' if p2_ok else '✗':<8} "
              f"{ta['interpretation'][:20]:<22}")

    return results


if __name__ == "__main__":
    main()
