"""
Scale Recovery - Real System Test

Test normalization against actual temporal systems.
"""

import numpy as np
import json
import sys
from typing import Dict

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/scale_recovery')

from temporal_dynamics import generate_temporal_system
from memory_metrics import (
    InteractionMemoryScore, StructuralPersistence,
    TemporalConsensusScore
)
from scale_recovery import (
    normalized_memory, normalized_persistence, normalized_consensus,
    separation_ratio, scale_stability, scale_invariant_score
)


def test_at_scale(system: str, N: int, params: Dict, seed: int = 42) -> Dict:
    """Test a system at a specific scale."""
    params['n'] = N
    
    traj, _ = generate_temporal_system(system, seed=seed, **params)
    
    # Raw metrics
    memory = InteractionMemoryScore(seed).compute(traj)['memory_score_mean']
    persist = StructuralPersistence(seed).compute(traj)['persistence_mean']
    consensus = TemporalConsensusScore(seed).compute(traj)['consensus_mean']
    
    # Normalized metrics
    norm_memory = normalized_memory(memory, N)
    norm_persist = normalized_persistence(persist, N)
    norm_consensus = normalized_consensus(consensus, N)
    
    return {
        'N': N,
        'raw_memory': memory,
        'raw_persistence': persist,
        'raw_consensus': consensus,
        'norm_memory': norm_memory,
        'norm_persistence': norm_persist,
        'norm_consensus': norm_consensus,
        'scale_invariant': scale_invariant_score(memory, persist, consensus, N)['scale_invariant_score']
    }


def test_scale_recovery():
    """Test scale recovery with real systems."""
    np.random.seed(42)
    
    print("=" * 60)
    print("SCALE RECOVERY - REAL SYSTEMS")
    print("=" * 60)
    
    scales = [50, 100, 250, 500]
    params = {'dimensions': 5, 'n_timesteps': 20}
    
    systems = ['stable_hierarchy', 'random_temporal']
    
    # Raw metrics across scales
    print("\n=== RAW METRICS (V2_010 - COLLAPSED) ===")
    for system in systems:
        results = []
        for N in scales:
            r = test_at_scale(system, N, params.copy())
            results.append(r['raw_consensus'])
        
        print(f"{system}: {np.round(results, 4)}")
    
    # Compute raw separation
    stable_raw = [test_at_scale('stable_hierarchy', N, params.copy())['raw_consensus'] for N in scales]
    random_raw = [test_at_scale('random_temporal', N, params.copy())['raw_consensus'] for N in scales]
    raw_sep = separation_ratio(stable_raw, random_raw)
    print(f"Raw separation ratio: {raw_sep:.4f}")
    
    print("\n=== NORMALIZED METRICS (V2_013 - FIXED) ===")
    for system in systems:
        results = []
        for N in scales:
            r = test_at_scale(system, N, params.copy())
            results.append(r['norm_consensus'])
        
        print(f"{system}: {np.round(results, 4)}")
    
    # Compute normalized separation
    stable_norm = [test_at_scale('stable_hierarchy', N, params.copy())['norm_consensus'] for N in scales]
    random_norm = [test_at_scale('random_temporal', N, params.copy())['norm_consensus'] for N in scales]
    norm_sep = separation_ratio(stable_norm, random_norm)
    print(f"Normalized separation ratio: {norm_sep:.4f}")
    
    # Scale stability
    stable_stab = scale_stability(stable_norm)
    print(f"\nStable system stability: {stable_stab:.4f}")
    
    # Save results
    output = '/home/student/sgp_core_v2/outputs/scale_recovery/scale_results.json'
    with open(output, 'w') as f:
        json.dump({
            'scales': scales,
            'stable_raw': stable_raw,
            'random_raw': random_raw,
            'stable_normalized': stable_norm,
            'random_normalized': random_norm,
            'raw_separation': raw_sep,
            'normalized_separation': norm_sep,
            'stable_stability': stable_stab
        }, f, indent=2)
    print(f"\nSaved: {output}")


if __name__ == '__main__':
    test_scale_recovery()