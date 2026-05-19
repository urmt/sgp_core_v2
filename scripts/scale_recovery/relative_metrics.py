"""
Scale-Invariant Temporal Metrics

Instead of normalizing the same metric, compare RELATIVE properties.
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


def relative_metric_ratio(metrics: Dict, N: int) -> Dict:
    """
    Compute relative ratios between metrics.
    
    Key insight: Instead of normalizing a single metric,
    look at the RELATIONSHIP between metrics which may be scale-invariant.
    """
    memory = metrics['memory']
    persist = metrics['persistence']
    consensus = metrics['consensus']
    frag_var = metrics['frag_var']
    drift = metrics['drift']
    
    # Ratios that might be scale-invariant
    memory_to_persist = memory / (persist + 1e-10)
    consensus_to_memory = consensus / (memory + 1e-10)
    persist_to_frag = persist / (frag_var + 1e-10)
    drift_to_memory = drift / (memory + 1e-10)
    
    return {
        'memory_to_persist': memory_to_persist,
        'consensus_to_memory': consensus_to_memory,
        'persist_to_frag': persist_to_frag,
        'drift_to_memory': drift_to_memory,
        'combined': (memory_to_persist + consensus_to_memory + persist_to_frag + drift_to_memory) / 4
    }


def test_relative_metrics():
    """Test relative metric approach."""
    np.random.seed(42)
    
    print("=" * 60)
    print("RELATIVE METRIC RATIOS")
    print("=" * 60)
    
    scales = [50, 100, 250, 500]
    params = {'dimensions': 5, 'n_timesteps': 20}
    
    results = {'stable_hierarchy': {}, 'random_temporal': {}}
    
    for system in ['stable_hierarchy', 'random_temporal']:
        print(f"\n=== {system} ===")
        ratios = []
        
        for N in scales:
            params['n'] = N
            traj, _ = generate_temporal_system(system, seed=42, **params)
            
            # Get all metrics
            metrics = {
                'memory': InteractionMemoryScore(42).compute(traj)['memory_score_mean'],
                'persistence': StructuralPersistence(42).compute(traj)['persistence_mean'],
                'consensus': TemporalConsensusScore(42).compute(traj)['consensus_mean'],
                'frag_var': TemporalFragmentationVariance(42).compute(traj)['fragmentation_std'],
                'drift': data_drift(traj)
            }
            
            ratios.append(relative_metric_ratio(metrics, N))
        
        results[system] = ratios
        
        # Show combined for each scale
        combined = [r['combined'] for r in ratios]
        print(f"  Combined ratio: {np.round(combined, 4)}")
    
    # Compute separation in relative space
    stable_combined = [r['combined'] for r in results['stable_hierarchy']]
    random_combined = [r['combined'] for r in results['random_temporal']]
    
    print("\n=== SEPARATION IN RELATIVE SPACE ===")
    for i, N in enumerate(scales):
        sep = stable_combined[i] / (random_combined[i] + 1e-10)
        print(f"  N={N}: {sep:.4f}x")
    
    # Overall
    avg_sep = np.mean([stable_combined[i] / (random_combined[i] + 1e-10) for i in range(len(scales))])
    print(f"\n  Average: {avg_sep:.4f}x")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/scale_recovery/relative_results.json'
    with open(output, 'w') as f:
        json.dump({
            'stable': results['stable_hierarchy'],
            'random': results['random_temporal'],
            'avg_separation': avg_sep
        }, f, indent=2, default=str)
    print(f"\nSaved: {output}")


if __name__ == '__main__':
    test_relative_metrics()