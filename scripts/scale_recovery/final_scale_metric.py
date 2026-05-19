"""
Final Scale-Invariant Metric

Test multiple approaches and pick the best.
"""

import numpy as np
import json
import sys
from typing import Dict

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/replay_resistance')

from temporal_dynamics import generate_temporal_system
from memory_metrics import (
    InteractionMemoryScore, StructuralPersistence,
    TemporalConsensusScore, TemporalFragmentationVariance
)
from final_replay_detection import data_drift


def compute_all_metrics(system: str, N: int, params: Dict, seed: int = 42) -> Dict:
    """Compute all available metrics."""
    params['n'] = N
    traj, _ = generate_temporal_system(system, seed=seed, **params)
    
    return {
        'memory': InteractionMemoryScore(seed).compute(traj)['memory_score_mean'],
        'persistence': StructuralPersistence(seed).compute(traj)['persistence_mean'],
        'consensus': TemporalConsensusScore(seed).compute(traj)['consensus_mean'],
        'frag_var': TemporalFragmentationVariance(seed).compute(traj)['fragmentation_std'],
        'drift': data_drift(traj)
    }


def test_final_scale_metric():
    """Test multiple scale-invariant formulas."""
    np.random.seed(42)
    
    print("=" * 60)
    print("FINAL SCALE-INVARIANT METRIC TEST")
    print("=" * 60)
    
    scales = [50, 100, 250, 500]
    params = {'dimensions': 5, 'n_timesteps': 20}
    
    # Get raw metrics
    stable_raw = {N: compute_all_metrics('stable_hierarchy', N, params.copy()) for N in scales}
    random_raw = {N: compute_all_metrics('random_temporal', N, params.copy()) for N in scales}
    
    print("\nRaw consensus:")
    for N in scales:
        print(f"  N={N}: stable={stable_raw[N]['consensus']:.4f}, random={random_raw[N]['consensus']:.4f}")
    
    # Test different formula approaches
    formulas = {
        'simple_weighted': lambda m, p, c, f, d: 0.3*m + 0.3*p + 0.4*c,
        'log_weighted': lambda m, p, c, f, d: 0.3*np.log1p(m) + 0.3*np.log1p(p) + 0.4*np.log1p(c),
        'sqrt_weighted': lambda m, p, c, f, d: 0.3*np.sqrt(m) + 0.3*np.sqrt(p) + 0.4*np.sqrt(c),
        'power_weighted': lambda m, p, c, f, d: 0.3*(m**0.7) + 0.3*(p**0.7) + 0.4*(c**0.7),
        'ratio_weighted': lambda m, p, c, f, d: 0.3*m + 0.3*p + 0.4*(c * (1 - f)),
        'drift_weighted': lambda m, p, c, f, d: (0.3*m + 0.3*p + 0.4*c) * (1 + d) / 2,
        'product': lambda m, p, c, f, d: (m * p * c) ** (1/3),
    }
    
    def apply_formula(formula, m, p, c, f, d):
        return formula(m, p, c, f, d)
    
    best_formula = None
    best_avg_sep = 0
    
    for name, formula in formulas.items():
        stable_scores = [apply_formula(formula, stable_raw[N]['memory'], stable_raw[N]['persistence'], stable_raw[N]['consensus'], stable_raw[N]['frag_var'], stable_raw[N]['drift']) for N in scales]
        random_scores = [apply_formula(formula, random_raw[N]['memory'], random_raw[N]['persistence'], random_raw[N]['consensus'], random_raw[N]['frag_var'], random_raw[N]['drift']) for N in scales]
        
        separations = [stable_scores[i] / (random_scores[i] + 1e-10) for i in range(len(scales))]
        avg_sep = np.mean(separations)
        
        print(f"\n{name}:")
        print(f"  separations: {np.round(separations, 4)}")
        print(f"  avg: {avg_sep:.4f}")
        
        if avg_sep > best_avg_sep:
            best_avg_sep = avg_sep
            best_formula = name
    
    print(f"\n=== BEST: {best_formula} with avg separation {best_avg_sep:.4f} ===")
    
    # Now show the best formula at each N
    formula = formulas[best_formula]
    print(f"\n=== BEST FORMULA DETAILS ===")
    print(f"Formula: {best_formula}")
    
    stable_scores = [apply_formula(formula, stable_raw[N]['memory'], stable_raw[N]['persistence'], stable_raw[N]['consensus'], stable_raw[N]['frag_var'], stable_raw[N]['drift']) for N in scales]
    random_scores = [apply_formula(formula, random_raw[N]['memory'], random_raw[N]['persistence'], random_raw[N]['consensus'], random_raw[N]['frag_var'], random_raw[N]['drift']) for N in scales]
    
    for i, N in enumerate(scales):
        sep = stable_scores[i] / (random_scores[i] + 1e-10)
        print(f"  N={N}: stable={stable_scores[i]:.4f}, random={random_scores[i]:.4f}, sep={sep:.4f}x")
    
    # Compare with V2_010
    print("\n=== COMPARISON ===")
    v2_010_raw = [1.40, 1.23, 1.08, 1.0]
    v2_013_new = [stable_scores[i] / (random_scores[i] + 1e-10) for i in range(len(scales))]
    print(f"V2_010: {v2_010_raw}")
    print(f"V2_013: {np.round(v2_013_new, 4)}")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/scale_recovery/final_scale_results.json'
    with open(output, 'w') as f:
        json.dump({
            'best_formula': best_formula,
            'scales': scales,
            'v2_010_separation': v2_010_raw,
            'v2_013_separation': v2_013_new,
            'avg_separation': best_avg_sep
        }, f, indent=2)
    print(f"\nSaved: {output}")


if __name__ == '__main__':
    test_final_scale_metric()