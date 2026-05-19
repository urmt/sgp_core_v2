"""
Scale-Invariant Combined Score

Create a metric that's inherently scale-invariant by combining raw values in a specific way.
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


def scale_invariant_combined(system: str, N: int, params: Dict, seed: int = 42) -> Dict:
    """Compute scale-invariant combined score."""
    params['n'] = N
    traj, _ = generate_temporal_system(system, seed=seed, **params)
    
    # Get all raw metrics
    memory = InteractionMemoryScore(seed).compute(traj)['memory_score_mean']
    persist = StructuralPersistence(seed).compute(traj)['persistence_mean']
    consensus = TemporalConsensusScore(seed).compute(traj)['consensus_mean']
    frag_var = TemporalFragmentationVariance(seed).compute(traj)['fragmentation_std']
    drift = data_drift(traj)
    
    # Combine in scale-invariant way:
    # Key: use PRODUCTS and RATIOS instead of sums
    # Product of normalized metrics = scale invariant if both scale similarly
    
    # Normalize each to 0-1 range within its typical values
    norm_memory = memory / 1.0  # memory is 0-1
    norm_persist = persist / 1.0  # persistence is 0-1
    norm_consensus = consensus / 1.0  # consensus is 0-1
    
    # Product-based score (becomes more discriminative as more metrics agree)
    product_score = (norm_memory * norm_persist * norm_consensus) ** (1/3)
    
    # Weighted combination
    weighted = 0.3 * norm_memory + 0.3 * norm_persist + 0.4 * norm_consensus
    
    # With drift as bonus (high drift + high consensus = extra suspicious)
    drift_factor = 1.0 - min(drift / 2.0, 1.0)  # high drift = low factor
    with_drift = weighted * (1 + drift_factor) / 2
    
    return {
        'N': N,
        'memory': memory,
        'persistence': persist,
        'consensus': consensus,
        'drift': drift,
        'product_score': product_score,
        'weighted': weighted,
        'with_drift': with_drift
    }


def test_scale_invariant():
    """Test scale-invariant combined scores."""
    np.random.seed(42)
    
    print("=" * 60)
    print("SCALE-INVARIANT COMBINED SCORES")
    print("=" * 60)
    
    scales = [50, 100, 250, 500]
    params = {'dimensions': 5, 'n_timesteps': 20}
    
    results = {'stable': {}, 'random': {}}
    
    for system, key in [('stable_hierarchy', 'stable'), ('random_temporal', 'random')]:
        print(f"\n=== {system} ===")
        
        for N in scales:
            r = scale_invariant_combined(system, N, params.copy())
            results[key][N] = r
            
            print(f"  N={N}: weighted={r['weighted']:.4f}, with_drift={r['with_drift']:.4f}")
    
    # Compute separation
    print("\n=== SEPARATION ===")
    separations = []
    
    for N in scales:
        stable_w = results['stable'][N]['weighted']
        random_w = results['random'][N]['weighted']
        sep = stable_w / (random_w + 1e-10)
        separations.append(sep)
        print(f"  N={N}: {sep:.4f}x")
    
    avg_sep = np.mean(separations)
    print(f"\n  Average: {avg_sep:.4f}x")
    
    # Compare with V2_010 raw
    print("\n=== COMPARISON WITH V2_010 ===")
    raw_sep = [1.40, 1.23, 1.08, 1.0]  # from V2_010
    print(f"  V2_010 raw separation: {np.round(raw_sep, 2)}")
    print(f"  V2_013 new separation: {np.round(separations, 4)}")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/scale_recovery/invariant_results.json'
    with open(output, 'w') as f:
        json.dump({
            'stable': {str(k): v for k, v in results['stable'].items()},
            'random': {str(k): v for k, v in results['random'].items()},
            'separations': separations,
            'avg_separation': avg_sep
        }, f, indent=2, default=str)
    print(f"\nSaved: {output}")


if __name__ == '__main__':
    test_scale_invariant()