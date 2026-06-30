"""
Phase 005A Division 4 — Hysteresis Topology Analysis.

Analyzes path dependence, basin geometry, and loop structure in
representational dynamics using dual-framework comparative architecture.

TRACK A: Independent hysteresis in representation and function
TRACK B: Coupled hysteresis — interaction structure under reversal
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scipy.integrate import trapezoid

from .collapse_dynamics import (
    DistributedSystem, ImmuneSignalingNetwork,
    InstitutionSystem, AntColony
)


@dataclass
class HysteresisLoop:
    forward_trajectory: List[float]
    reverse_trajectory: List[float]
    loop_area: float
    path_divergence: float
    reversibility: float
    asymmetry_index: float


# ---------------------------------------------------------------------------
# Hysteresis sweep: forward (coupling down) then reverse (coupling up)
# ---------------------------------------------------------------------------

def run_hysteresis_sweep(system_class, base_coupling: float = 0.5,
                          n_levels: int = 15, n_steps_per: int = 20,
                          **kwargs) -> Dict:
    """
    Forward sweep: coupling decreases from base to near-zero.
    Reverse sweep: coupling increases back to base.
    Measures path dependence (hysteresis) between forward and reverse.
    """
    fwd_couplings = np.linspace(base_coupling, 0.01, n_levels)
    rev_couplings = np.linspace(0.01, base_coupling, n_levels)

    system = system_class(coupling=base_coupling, **kwargs)

    fwd_rep, fwd_func = [], []
    for c in fwd_couplings:
        system.coupling = c
        for _ in range(n_steps_per):
            system.step()
            fwd_rep.append(system.representational_ed())
            fwd_func.append(system.functional_performance())

    rev_rep, rev_func = [], []
    for c in rev_couplings:
        system.coupling = c
        for _ in range(n_steps_per):
            system.step()
            rev_rep.append(system.representational_ed())
            rev_func.append(system.functional_performance())

    rep_loop = HysteresisLoop(
        forward_trajectory=fwd_rep,
        reverse_trajectory=rev_rep,
        loop_area=0.0,
        path_divergence=0.0,
        reversibility=0.0,
        asymmetry_index=0.0
    )
    func_loop = HysteresisLoop(
        forward_trajectory=fwd_func,
        reverse_trajectory=rev_func,
        loop_area=0.0,
        path_divergence=0.0,
        reversibility=0.0,
        asymmetry_index=0.0
    )

    rep_loop = _compute_loop_metrics(rep_loop)
    func_loop = _compute_loop_metrics(func_loop)

    return {
        'system_type': system_class.__name__,
        'representational_hysteresis': {
            'forward': fwd_rep,
            'reverse': rev_rep,
            'loop_area': rep_loop.loop_area,
            'path_divergence': rep_loop.path_divergence,
            'reversibility': rep_loop.reversibility,
            'asymmetry_index': rep_loop.asymmetry_index
        },
        'functional_hysteresis': {
            'forward': fwd_func,
            'reverse': rev_func,
            'loop_area': func_loop.loop_area,
            'path_divergence': func_loop.path_divergence,
            'reversibility': func_loop.reversibility,
            'asymmetry_index': func_loop.asymmetry_index
        },
        'n_levels': n_levels,
        'n_steps_per': n_steps_per,
        'total_forward_steps': len(fwd_rep),
        'total_reverse_steps': len(rev_rep)
    }


def _compute_loop_metrics(loop: HysteresisLoop) -> HysteresisLoop:
    fwd = np.array(loop.forward_trajectory)
    rev = np.array(loop.reverse_trajectory)
    min_len = min(len(fwd), len(rev))
    fwd, rev = fwd[:min_len], rev[:min_len]

    fwd_norm = fwd / (fwd[0] + 1e-10)
    rev_norm = rev / (rev[0] + 1e-10)

    loop_area = float(np.trapezoid(np.abs(fwd_norm - rev_norm)))
    path_divergence = float(np.mean(np.abs(fwd_norm - rev_norm)))
    reversibility = float(1.0 - min(path_divergence, 1.0))
    asymmetry = float(np.mean(np.sign(fwd_norm - rev_norm)))

    loop.loop_area = loop_area
    loop.path_divergence = path_divergence
    loop.reversibility = reversibility
    loop.asymmetry_index = asymmetry
    return loop


# ---------------------------------------------------------------------------
# TRACK A: Parallel Hysteresis — independent rep/function reversibility
# ---------------------------------------------------------------------------

class ParallelHysteresisAnalyzer:
    """
    TRACK A: Analyzes hysteresis in representation and function independently.
    Measures path dependence separately for each modality.
    """

    @staticmethod
    def analyze(sweep_results: Dict) -> Dict:
        rep = sweep_results['representational_hysteresis']
        func = sweep_results['functional_hysteresis']

        return {
            'track': 'A_parallel',
            'representational': {
                'loop_area': rep['loop_area'],
                'path_divergence': rep['path_divergence'],
                'reversibility': rep['reversibility'],
                'asymmetry_index': rep['asymmetry_index']
            },
            'functional': {
                'loop_area': func['loop_area'],
                'path_divergence': func['path_divergence'],
                'reversibility': func['reversibility'],
                'asymmetry_index': func['asymmetry_index']
            },
            'rep_func_divergence': abs(rep['reversibility'] - func['reversibility']),
            'rep_more_reversible': rep['reversibility'] > func['reversibility']
        }


# ---------------------------------------------------------------------------
# TRACK B: Coupled Hysteresis — interaction structure under reversal
# ---------------------------------------------------------------------------

class CoupledHysteresisAnalyzer:
    """
    TRACK B: Analyzes coupled hysteresis - how representation-function
    interaction changes between forward and reverse sweeps.
    """

    @staticmethod
    def analyze(sweep_results: Dict) -> Dict:
        rep_fwd = np.array(sweep_results['representational_hysteresis']['forward'])
        rep_rev = np.array(sweep_results['representational_hysteresis']['reverse'])
        func_fwd = np.array(sweep_results['functional_hysteresis']['forward'])
        func_rev = np.array(sweep_results['functional_hysteresis']['reverse'])
        min_len = min(len(rep_fwd), len(rep_rev), len(func_fwd), len(func_rev))
        r_fwd, r_rev = rep_fwd[:min_len], rep_rev[:min_len]
        f_fwd, f_rev = func_fwd[:min_len], func_rev[:min_len]

        r_fwd_n = r_fwd / (r_fwd[0] + 1e-10)
        r_rev_n = r_rev / (r_rev[0] + 1e-10)
        f_fwd_n = f_fwd / (f_fwd[0] + 1e-10)
        f_rev_n = f_rev / (f_rev[0] + 1e-10)

        fwd_div = np.abs(r_fwd_n - f_fwd_n)
        rev_div = np.abs(r_rev_n - f_rev_n)
        coupling_hysteresis = float(np.mean(np.abs(fwd_div - rev_div)))
        forward_interaction = float(np.mean(np.abs(np.correlate(r_fwd_n - np.mean(r_fwd_n), f_fwd_n - np.mean(f_fwd_n), mode='valid'))))
        reverse_interaction = float(np.mean(np.abs(np.correlate(r_rev_n - np.mean(r_rev_n), f_rev_n - np.mean(f_rev_n), mode='valid'))))

        return {
            'track': 'B_coupled',
            'coupling_hysteresis': coupling_hysteresis,
            'forward_interaction_strength': forward_interaction,
            'reverse_interaction_strength': reverse_interaction,
            'interaction_asymmetry': abs(forward_interaction - reverse_interaction),
            'interaction_fades_on_reversal': reverse_interaction < forward_interaction * 0.8,
            'reversal_changes_coupling': coupling_hysteresis > 0.1
        }


# ---------------------------------------------------------------------------
# Comparative Evaluator
# ---------------------------------------------------------------------------

class HysteresisComparativeEvaluator:
    """
    Compares TRACK A and TRACK B hysteresis characterizations.
    """

    @staticmethod
    def evaluate(track_a: Dict, track_b: Dict) -> Dict:
        rep_hyst = track_a['representational']['loop_area']
        func_hyst = track_a['functional']['loop_area']
        coupled_hyst = track_b['coupling_hysteresis']
        interaction_asymmetry = track_b['interaction_asymmetry']

        if coupled_hyst > max(rep_hyst, func_hyst) * 1.5:
            return {
                'winner': 'B_coupled',
                'reason': 'coupled_hysteresis_exceeds_individual',
                'score_b': float(min(coupled_hyst, 1.0)),
                'score_a': float(min(max(rep_hyst, func_hyst), 1.0))
            }
        if max(rep_hyst, func_hyst) > coupled_hyst * 2:
            return {
                'winner': 'A_parallel',
                'reason': 'individual_hysteresis_dominates',
                'score_b': float(min(coupled_hyst, 1.0)),
                'score_a': float(min(max(rep_hyst, func_hyst), 1.0))
            }
        return {
            'winner': 'comparable',
            'reason': 'both_frameworks_capture_hysteresis',
            'score_b': float(min(coupled_hyst, 1.0)),
            'score_a': float(min(max(rep_hyst, func_hyst), 1.0))
        }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_all_hysteresis_analyses() -> Dict:
    systems = [
        (DistributedSystem, {'n_nodes': 20}),
        (ImmuneSignalingNetwork, {'n_signals': 10}),
        (InstitutionSystem, {'n_institutions': 8}),
        (AntColony, {'n_regions': 15}),
    ]
    results = {}
    for sys_class, params in systems:
        name = sys_class.__name__.lower()
        sweep = run_hysteresis_sweep(sys_class, base_coupling=0.5, n_levels=15, n_steps_per=20, **params)
        ta = ParallelHysteresisAnalyzer.analyze(sweep)
        tb = CoupledHysteresisAnalyzer.analyze(sweep)
        comp = HysteresisComparativeEvaluator.evaluate(ta, tb)
        results[name] = {'sweep': sweep, 'track_a': ta, 'track_b': tb, 'comparison': comp}
    return results


def main():
    print("=" * 64)
    print("  Phase 005A Division 4 — Hysteresis Topology Analysis")
    print("  Dual-Framework: TRACK A vs TRACK B Hysteresis")
    print("=" * 64)

    results = run_all_hysteresis_analyses()

    for name, r in results.items():
        sweep = r['sweep']
        ta = r['track_a']
        tb = r['track_b']
        comp = r['comparison']

        print(f"\n{'─' * 50}")
        print(f"  System: {name} ({sweep['system_type']})")
        print(f"{'─' * 50}")

        print(f"  TRACK A — Parallel Hysteresis:")
        print(f"    Rep loop area:     {ta['representational']['loop_area']:.4f}")
        print(f"    Rep reversibility: {ta['representational']['reversibility']:.4f}")
        print(f"    Func loop area:    {ta['functional']['loop_area']:.4f}")
        print(f"    Func reversibility:{ta['functional']['reversibility']:.4f}")
        print(f"    Rep-func gap:      {ta['rep_func_divergence']:.4f}")

        print(f"  TRACK B — Coupled Hysteresis:")
        print(f"    Coupling hyst:     {tb['coupling_hysteresis']:.4f}")
        print(f"    Fwd interaction:   {tb['forward_interaction_strength']:.4f}")
        print(f"    Rev interaction:   {tb['reverse_interaction_strength']:.4f}")
        print(f"    Interaction asym:  {tb['interaction_asymmetry']:.4f}")
        print(f"    Fades on reversal: {tb['interaction_fades_on_reversal']}")

        print(f"  COMPARISON:")
        print(f"    Winner:  {comp['winner']}")
        print(f"    Reason:  {comp['reason']}")

    print(f"\n{'=' * 64}")
    print("  Hysteresis topology analysis complete.")
    print(f"{'=' * 64}")

    return results


if __name__ == "__main__":
    main()
