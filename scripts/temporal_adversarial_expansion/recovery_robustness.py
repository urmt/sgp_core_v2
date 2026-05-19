"""
Recovery Robustness Tests

Test strong perturbation recovery.
"""

import numpy as np
import sys
from typing import Dict
sys.path.insert(0, 'scripts/temporal_memory')

from temporal_dynamics import generate_temporal_system
from memory_metrics import (
    InteractionMemoryScore, StructuralPersistence, 
    TemporalConsensusScore
)


def test_recovery(system: str, params: Dict, seed: int = 42, 
                 perturb_strength: float = 2.0) -> Dict:
    """Test recovery after perturbation."""
    try:
        # Generate base
        traj, meta = generate_temporal_system(system, seed=seed, **params)
        
        # Pre-perturbation metrics
        pre_memory = InteractionMemoryScore(seed).compute(traj[:10])['memory_score_mean']
        
        # Perturb middle
        perturbed = traj.copy()
        mid = len(traj) // 2
        perturbed[mid] += np.random.normal(0, perturb_strength, traj[0].shape)
        
        # Post-perturbation metrics
        post_memory = InteractionMemoryScore(seed + 1).compute(perturbed[mid:])['memory_score_mean']
        
        # Recovery ratio
        recovery_ratio = post_memory / (pre_memory + 1e-10)
        
        return {
            'pre_memory': pre_memory,
            'post_memory': post_memory,
            'recovery_ratio': recovery_ratio
        }
    except Exception as e:
        return {'error': str(e)}


if __name__ == '__main__':
    np.random.seed(42)
    print("=" * 60)
    print("RECOVERY ROBUSTNESS")
    print("=" * 60)
    
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    systems = ['stable_hierarchy', 'random_temporal', 'perturb_recover']
    
    results = {}
    for system in systems:
        r = test_recovery(system, params, perturb_strength=2.0)
        results[system] = r
        print(f"{system}: pre={r.get('pre_memory', 'N/A'):.3f} post={r.get('post_memory', 'N/A'):.3f} ratio={r.get('recovery_ratio', 'N/A'):.3f}")
    
    # Check if organized systems recover better
    print("\n=== RECOVERY ANALYSIS ===")
    stable_ratio = results['stable_hierarchy'].get('recovery_ratio', 0)
    random_ratio = results['random_temporal'].get('recovery_ratio', 0)
    print(f"Recovery ratio: stable={stable_ratio:.2f}x random={random_ratio:.2f}x")
    
    # Save
    import json
    output = '/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/recovery_results.json'
    with open(output, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {output}")