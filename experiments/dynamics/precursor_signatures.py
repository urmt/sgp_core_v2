"""
Phase 005A Division 3 — Precursor Signature Analysis.

Detects signals preceding representational collapse using dual-framework
(TRACK A: independent precursors, TRACK B: coupled precursor interactions).
Collapse is induced via coupling sweep intervention to observe precursor events.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scipy.stats import spearmanr

from .metrics import VelocityMetrics, AccelerationMetrics
from .collapse_dynamics import (
    DistributedSystem, ImmuneSignalingNetwork,
    InstitutionSystem, AntColony
)


@dataclass
class PrecursorSignal:
    step: int
    signal_type: str
    magnitude: float
    lead_time: int
    reliability: float


# ---------------------------------------------------------------------------
# TRACK A: Parallel Precursor Analysis — independent precursor detection
# ---------------------------------------------------------------------------

class ParallelPrecursorAnalyzer:
    """
    TRACK A: Detects precursors in representation and function independently.
    Each modality is analyzed separately for early warning signals.
    """

    def __init__(self, n_steps: int = 200, lookback: int = 10):
        self.n_steps = n_steps
        self.lookback = lookback

    def analyze(self, system, collapse_step: Optional[int] = None) -> Dict:
        steps = self.n_steps
        rep_ed_traj = np.zeros(steps)
        func_traj = np.zeros(steps)

        for t in range(steps):
            system.step()
            rep_ed_traj[t] = system.representational_ed()
            func_traj[t] = system.functional_performance()

        if collapse_step is None:
            collapse_step = self._detect_collapse_step(rep_ed_traj)

        rep_precursors = self._detect_precursors(rep_ed_traj, collapse_step)
        func_precursors = self._detect_precursors(func_traj, collapse_step)

        return {
            'track': 'A_parallel',
            'collapse_step': collapse_step,
            'representational_precursors': rep_precursors,
            'functional_precursors': func_precursors,
            'total_rep_signals': len(rep_precursors),
            'total_func_signals': len(func_precursors),
            'rep_has_precursors': len(rep_precursors) > 0,
            'func_has_precursors': len(func_precursors) > 0,
            'precursor_correlation': self._compute_precursor_correlation(
                rep_precursors, func_precursors
            )
        }

    def _detect_collapse_step(self, trajectory: np.ndarray) -> int:
        if len(trajectory) < 20:
            return len(trajectory) // 2
        grad = np.abs(np.gradient(trajectory))
        grad[:5] = 0.0
        for i in range(len(grad)):
            if i >= 5 and i < len(grad) - 5:
                grad[i] = np.mean(grad[max(0,i-2):i+3])
        window_size = max(5, len(trajectory) // 10)
        max_change = 0.0
        max_idx = len(trajectory) - 1
        for i in range(window_size, len(trajectory)):
            total_change = np.trapezoid(grad[i-window_size:i])
            if total_change > max_change:
                max_change = total_change
                max_idx = i
        return max_idx

    def _detect_precursors(self, trajectory: np.ndarray, collapse_step: int) -> List[Dict]:
        precursors = []
        if collapse_step <= self.lookback:
            return precursors
        pre_window = max(0, collapse_step - self.lookback)
        window_vals = trajectory[pre_window:collapse_step]
        if len(window_vals) < 3:
            return precursors
        baseline = trajectory[:max(5, len(trajectory) // 8)]
        baseline_mean = np.mean(baseline)
        baseline_std = max(np.std(baseline), 1e-10)
        baseline_diff_std = max(np.std(np.diff(baseline)), 1e-10)
        for i in range(1, len(window_vals)):
            z = abs(window_vals[i] - baseline_mean) / baseline_std
            vel = abs(window_vals[i] - window_vals[i-1])
            if z > 1.5 or vel > 2.0 * baseline_diff_std:
                step = pre_window + i
                precursors.append({
                    'step': step,
                    'signal_type': 'velocity_surge' if vel > 2.0 * baseline_diff_std else 'deviation',
                    'magnitude': float(min(z, 5.0)),
                    'lead_time': collapse_step - step,
                    'reliability': float(min(max(z / 3.0, vel / (baseline_diff_std * 3 + 1e-10)), 1.0))
                })
        return precursors

    def _compute_precursor_correlation(self, rep: List, func: List) -> float:
        if not rep or not func:
            return 0.0
        rep_steps = {p['step']: p['magnitude'] for p in rep}
        func_steps = {p['step']: p['magnitude'] for p in func}
        common = set(rep_steps.keys()) & set(func_steps.keys())
        if len(common) < 3:
            return 0.0
        rep_vals = [rep_steps[s] for s in sorted(common)]
        func_vals = [func_steps[s] for s in sorted(common)]
        rho, _ = spearmanr(rep_vals, func_vals)
        return float(rho)


# ---------------------------------------------------------------------------
# TRACK B: Coupled Precursor Analysis — joint precursor interaction
# ---------------------------------------------------------------------------

class CoupledPrecursorAnalyzer:
    """
    TRACK B: Analyzes coupled precursor interactions between representation and function.
    Detects cross-modal early warning signals and lead-lag precursor relationships.
    """

    def __init__(self, n_steps: int = 200, lookback: int = 20):
        self.n_steps = n_steps
        self.lookback = lookback

    def analyze(self, system, collapse_step: Optional[int] = None) -> Dict:
        steps = self.n_steps
        rep_ed_traj = np.zeros(steps)
        func_traj = np.zeros(steps)

        for t in range(steps):
            system.step()
            rep_ed_traj[t] = system.representational_ed()
            func_traj[t] = system.functional_performance()

        if collapse_step is None:
            collapse_step = self._detect_collapse_step(rep_ed_traj)

        coupled_precursors = self._detect_coupled_precursors(
            rep_ed_traj, func_traj, collapse_step
        )

        joint_signals = self._compute_joint_signals(
            rep_ed_traj, func_traj, collapse_step
        )

        return {
            'track': 'B_coupled',
            'collapse_step': collapse_step,
            'coupled_precursors': coupled_precursors,
            'joint_signals': joint_signals,
            'total_coupled_signals': len(coupled_precursors),
            'has_coupled_precursors': len(coupled_precursors) > 0,
            'max_joint_anomaly': joint_signals.get('max_joint_anomaly', 0.0),
            'coupling_divergence_precursor': joint_signals.get('coupling_divergence', 0.0)
        }

    def _detect_collapse_step(self, trajectory: np.ndarray) -> int:
        if len(trajectory) < 20:
            return len(trajectory) // 2
        grad = np.abs(np.gradient(trajectory))
        grad[:5] = 0.0
        for i in range(len(grad)):
            if i >= 5 and i < len(grad) - 5:
                grad[i] = np.mean(grad[max(0,i-2):i+3])
        window_size = max(5, len(trajectory) // 10)
        max_change = 0.0
        max_idx = len(trajectory) - 1
        for i in range(window_size, len(trajectory)):
            total_change = np.trapezoid(grad[i-window_size:i])
            if total_change > max_change:
                max_change = total_change
                max_idx = i
        return max_idx

    def _detect_coupled_precursors(self, rep: np.ndarray, func: np.ndarray,
                                   collapse_step: int) -> List[Dict]:
        precursors = []
        if collapse_step <= self.lookback:
            return precursors
        pre_window = max(0, collapse_step - self.lookback)

        rep_window = rep[pre_window:collapse_step]
        func_window = func[pre_window:collapse_step]

        if len(rep_window) < 3:
            return precursors

        rep_base = rep[:pre_window] if pre_window > 5 else rep[:10]
        func_base = func[:pre_window] if pre_window > 5 else func[:10]

        for i in range(1, min(len(rep_window), len(func_window))):
            rep_change = abs(rep_window[i] - rep_window[i-1])
            func_change = abs(func_window[i] - func_window[i-1])
            divergence = abs(rep_window[i] - func_window[i])

            rep_z = abs(rep_window[i] - np.mean(rep_base)) / (np.std(rep_base) + 1e-10)
            func_z = abs(func_window[i] - np.mean(func_base)) / (np.std(func_base) + 1e-10)
            coupling_stress = rep_change * func_change / (np.std(np.diff(rep_base)) * np.std(np.diff(func_base)) + 1e-10)

            if coupling_stress > 2.0 or (rep_z > 1.5 and func_z > 1.5):
                step = pre_window + i
                if coupling_stress > 2.0:
                    signal_type = 'coupling_stress'
                    magnitude = float(min(coupling_stress / 5.0, 1.0))
                else:
                    signal_type = 'coupled_anomaly'
                    magnitude = float((rep_z + func_z) / 6.0)

                precursors.append({
                    'step': step,
                    'signal_type': signal_type,
                    'magnitude': min(magnitude, 1.0),
                    'lead_time': collapse_step - step,
                    'reliability': float(min((rep_z + func_z) / 8.0, 1.0)),
                    'divergence_at_signal': float(divergence)
                })
        return precursors

    def _compute_joint_signals(self, rep: np.ndarray, func: np.ndarray,
                                collapse_step: int) -> Dict:
        pre_window = max(0, collapse_step - self.lookback)
        rep_pre = rep[pre_window:collapse_step]
        func_pre = func[pre_window:collapse_step]
        if len(rep_pre) < 3:
            return {'max_joint_anomaly': 0.0, 'coupling_divergence': 0.0}

        joint_anomaly = np.abs(rep_pre - np.mean(rep[:20])) * np.abs(func_pre - np.mean(func[:20]))
        coupling_divergence = np.mean(np.abs(np.diff(rep_pre) * np.diff(func_pre)))

        return {
            'max_joint_anomaly': float(np.max(joint_anomaly) if len(joint_anomaly) > 0 else 0.0),
            'coupling_divergence': float(coupling_divergence),
            'joint_anomaly_timeline': joint_anomaly.tolist()
        }


# ---------------------------------------------------------------------------
# Comparative Evaluator
# ---------------------------------------------------------------------------

class PrecursorComparativeEvaluator:
    """
    Compares TRACK A and TRACK B precursor detection across systems.
    """

    @staticmethod
    def evaluate(track_a: Dict, track_b: Dict) -> Dict:
        a_signals = track_a.get('total_rep_signals', 0) + track_a.get('total_func_signals', 0)
        b_signals = track_b.get('total_coupled_signals', 0)
        a_has = track_a.get('rep_has_precursors', False) or track_a.get('func_has_precursors', False)
        b_has = track_b.get('has_coupled_precursors', False)

        if b_has and not a_has:
            return {'winner': 'B_coupled', 'reason': 'coupled_detection_only', 'score_b': 1.0, 'score_a': 0.0}
        if a_has and not b_has:
            return {'winner': 'A_parallel', 'reason': 'independent_detection_only', 'score_a': 1.0, 'score_b': 0.0}
        if a_has and b_has:
            return {
                'winner': 'both' if abs(a_signals - b_signals) < 2 else ('B_coupled' if b_signals > a_signals else 'A_parallel'),
                'reason': 'both_detected',
                'score_a': float(a_signals / (a_signals + b_signals + 1e-10)),
                'score_b': float(b_signals / (a_signals + b_signals + 1e-10))
            }
        return {'winner': 'none', 'reason': 'no_precursors_detected', 'score_a': 0.0, 'score_b': 0.0}


# ---------------------------------------------------------------------------
# Coupling sweep intervention to induce collapse
# ---------------------------------------------------------------------------

def run_coupling_sweep(system_class, base_coupling: float = 0.5,
                       n_coupling_steps: int = 20, n_steps_per: int = 30,
                       **kwargs) -> Dict:
    """
    Induce collapse via coupling sweep (Phase 004A pattern).
    Sweeps coupling from base down to near-zero over n_coupling_steps.
    """
    coupling_levels = np.linspace(base_coupling, 0.01, n_coupling_steps)
    rep_traj = []
    func_traj = []
    coupling_log = []

    system = system_class(coupling=base_coupling, **kwargs)

    for coupling in coupling_levels:
        system.coupling = coupling
        for _ in range(n_steps_per):
            system.step()
            rep_traj.append(system.representational_ed())
            func_traj.append(system.functional_performance())
            coupling_log.append(coupling)

    return {
        'system_type': system_class.__name__,
        'representational_trajectory': rep_traj,
        'functional_trajectory': func_traj,
        'coupling_log': coupling_log,
        'n_steps_total': len(rep_traj),
        'initial_ed': rep_traj[0] if rep_traj else 0,
        'final_ed': rep_traj[-1] if rep_traj else 0,
        'initial_func': func_traj[0] if func_traj else 0,
        'final_func': func_traj[-1] if func_traj else 0,
        'ed_change_pct': ((rep_traj[-1] - rep_traj[0]) / (rep_traj[0] + 1e-10)) * 100 if rep_traj else 0,
        'func_change_pct': ((func_traj[-1] - func_traj[0]) / (func_traj[0] + 1e-10)) * 100 if func_traj else 0
    }


def run_all_precursor_analyses() -> Dict:
    systems = [
        (DistributedSystem, {'n_nodes': 20}),
        (ImmuneSignalingNetwork, {'n_signals': 10}),
        (InstitutionSystem, {'n_institutions': 8}),
        (AntColony, {'n_regions': 15}),
    ]
    results = {}
    for sys_class, params in systems:
        name = sys_class.__name__.lower()
        sweep = run_coupling_sweep(sys_class, base_coupling=0.5, n_coupling_steps=20, n_steps_per=30, **params)

        rep_traj = np.array(sweep['representational_trajectory'])
        func_traj = np.array(sweep['functional_trajectory'])

        pa = ParallelPrecursorAnalyzer(n_steps=len(rep_traj))
        ca = CoupledPrecursorAnalyzer(n_steps=len(rep_traj))
        ce = PrecursorComparativeEvaluator()

        class SweepProxy:
            def __init__(self, rep_traj, func_traj):
                self._rep = rep_traj
                self._func = func_traj
                self._step = 0
            def representational_ed(self):
                return float(self._rep[self._step])
            def functional_performance(self):
                return float(self._func[self._step])
            def step(self):
                self._step = min(self._step + 1, len(self._rep) - 1)
                return 0.0

        sweep_proxy = SweepProxy(rep_traj, func_traj)
        track_a = pa.analyze(sweep_proxy)
        sweep_proxy2 = SweepProxy(rep_traj, func_traj)
        track_b = ca.analyze(sweep_proxy2)
        comparison = ce.evaluate(track_a, track_b)

        results[name] = {
            'coupling_sweep': sweep,
            'track_a': track_a,
            'track_b': track_b,
            'comparison': comparison
        }
    return results


def main():
    print("=" * 64)
    print("  Phase 005A Division 3 — Precursor Signature Analysis")
    print("  Dual-Framework: TRACK A vs TRACK B Precursor Detection")
    print("=" * 64)

    results = run_all_precursor_analyses()

    for sys_name, sys_results in results.items():
        sweep = sys_results['coupling_sweep']
        ta = sys_results['track_a']
        tb = sys_results['track_b']
        comp = sys_results['comparison']

        print(f"\n{'─' * 50}")
        print(f"  System: {sys_name} ({sweep['system_type']})")
        print(f"{'─' * 50}")

        print(f"  COUPLING SWEEP:")
        print(f"    ED change:       {sweep['ed_change_pct']:+.2f}%")
        print(f"    Func change:     {sweep['func_change_pct']:+.2f}%")

        print(f"  TRACK A — Independent Precursors:")
        print(f"    Collapse step:   {ta['collapse_step']}")
        print(f"    Rep precursors:  {ta['total_rep_signals']}")
        print(f"    Func precursors: {ta['total_func_signals']}")

        print(f"  TRACK B — Coupled Precursors:")
        print(f"    Collapse step:   {tb['collapse_step']}")
        print(f"    Coupled signals: {tb['total_coupled_signals']}")
        print(f"    Max joint anom:  {tb['max_joint_anomaly']:.4f}")

        print(f"  COMPARISON:")
        print(f"    Winner:          {comp['winner']}")
        print(f"    Reason:          {comp['reason']}")

    print(f"\n{'=' * 64}")
    print("  Precursor analysis complete.")
    print(f"{'=' * 64}")

    return results


if __name__ == "__main__":
    main()
