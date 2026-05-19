"""
Scale Breaking Tests

Test if temporal metrics collapse at different scales.
"""

import numpy as np
import json
import sys
from typing import Dict
sys.path.insert(0, 'scripts/temporal_memory')

from temporal_dynamics import generate_temporal_system
from memory_metrics import (
    InteractionMemoryScore, StructuralPersistence,
    TemporalFragmentationVariance, TemporalConsensusScore
)


def test_at_scale(system_type: str, params: Dict, n_seeds: int = 3) -> Dict:
    """Test a system at specific scale."""
    results = {
        'memory': [], 'persistence': [], 'frag_var': [], 'consensus': []
    }
    
    for seed in range(42, 42 + n_seeds):
        try:
            traj, _ = generate_temporal_system(system_type, seed=seed, **params)
            
            memory = InteractionMemoryScore(seed).compute(traj)['memory_score_mean']
            persist = StructuralPersistence(seed).compute(traj)['persistence_mean']
            frag_var = TemporalFragmentationVariance(seed).compute(traj)['fragmentation_std']
            consensus = TemporalConsensusScore(seed).compute(traj)['consensus_mean']
            
            results['memory'].append(memory)
            results['persistence'].append(persist)
            results['frag_var'].append(frag_var)
            results['consensus'].append(consensus)
        except Exception as e:
            print(f"Error: {e}")
    
    return {k: np.mean(v) for k, v in results.items()}


if __name__ == '__main__':
    print("=" * 60)
    print("SCALE BREAKING TESTS")
    print("=" * 60)
    
    scales = [50, 100, 250]
    
    systems = ['stable_hierarchy', 'random_temporal', 'perturb_recover']
    scale_results = {}
    
    for n in scales:
        print(f"\n=== N = {n} ===")
        scale_results[n] = {}
        
        params = {'n': n, 'dimensions': 5, 'n_timesteps': 20}
        
        for system in systems:
            r = test_at_scale(system, params, n_seeds=2)
            scale_results[n][system] = r
            print(f"  {system}: memory={r['memory']:.3f} persist={r['persistence']:.3f} consensus={r['consensus']:.3f}")
    
    # Check discrimination at each scale
    print("\n=== DISCRIMINATION BY SCALE ===")
    for n in scales:
        stable = scale_results[n]['stable_hierarchy']['consensus']
        random = scale_results[n]['random_temporal']['consensus']
        diff = abs(stable - random)
        ratio = stable / (random + 1e-10)
        print(f"N={n}: diff={diff:.3f} ratio={ratio:.2f}x")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/scale_results.json'
    with open(output, 'w') as f:
        json.dump(scale_results, f, indent=2)
    print(f"\nSaved: {output}")