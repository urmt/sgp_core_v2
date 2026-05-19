"""
Multi-Seed Temporal Validation

Test temporal metrics with multiple seeds and adversarial systems.
"""

import numpy as np
import json
from typing import Dict
import sys
sys.path.insert(0, 'scripts/temporal_memory')

from temporal_dynamics import generate_temporal_system
from memory_metrics import (
    InteractionMemoryScore, StructuralPersistence,
    TemporalFragmentationVariance, TemporalConsensusScore
)

# Add adversarial path
sys.path.insert(0, 'scripts/temporal_adversarial_expansion')
from advanced_temporal_adversaries import generate_temporal_adversary


def test_system(system_type: str, params: Dict, n_seeds: int, seed_base: int = 42) -> Dict:
    """Test a system with multiple seeds."""
    results = {
        'memory_scores': [],
        'persistences': [],
        'frag_vars': [],
        'consensus_scores': []
    }
    
    for seed in range(seed_base, seed_base + n_seeds):
        try:
            # Map system names to generators
            adversarial_map = {
                'replay_memory_spoof': 'replay_memory_spoof',
                'delayed_random_coherence': 'delayed_random_coherence',
                'temporal_camouflage': 'temporal_camouflage'
            }
            
            if system_type in adversarial_map:
                traj, _ = generate_temporal_adversary(system_type, seed=seed, **params)
            else:
                traj, _ = generate_temporal_system(system_type, seed=seed, **params)
            
            memory = InteractionMemoryScore(seed).compute(traj)['memory_score_mean']
            persist = StructuralPersistence(seed).compute(traj)['persistence_mean']
            frag_var = TemporalFragmentationVariance(seed).compute(traj)['fragmentation_std']
            consensus = TemporalConsensusScore(seed).compute(traj)['consensus_mean']
            
            results['memory_scores'].append(memory)
            results['persistences'].append(persist)
            results['frag_vars'].append(frag_var)
            results['consensus_scores'].append(consensus)
        except Exception as e:
            print(f"Error with {system_type} seed {seed}: {e}")
    
    return {
        'memory_mean': np.mean(results['memory_scores']) if results['memory_scores'] else 0,
        'memory_std': np.std(results['memory_scores']) if results['memory_scores'] else 0,
        'persistence_mean': np.mean(results['persistences']) if results['persistences'] else 0,
        'persistence_std': np.std(results['persistences']) if results['persistences'] else 0,
        'frag_var_mean': np.mean(results['frag_vars']) if results['frag_vars'] else 0,
        'consensus_mean': np.mean(results['consensus_scores']) if results['consensus_scores'] else 0,
        'consensus_std': np.std(results['consensus_scores']) if results['consensus_scores'] else 0,
        'cv': np.std(results['consensus_scores']) / (np.mean(results['consensus_scores']) + 1e-10) if results['consensus_scores'] else 0
    }


if __name__ == '__main__':
    np.random.seed(42)
    
    print("=" * 60)
    print("MULTI-SEED TEMPORAL VALIDATION")
    print("=" * 60)
    
    # Test legitimate systems
    print("\n=== LEGITIMATE SYSTEMS ===")
    legitimate = {
        'stable_hierarchy': {'n': 30, 'dimensions': 5, 'n_timesteps': 20},
        'random_temporal': {'n': 30, 'dimensions': 5, 'n_timesteps': 20},
        'perturb_recover': {'n': 30, 'dimensions': 5, 'n_timesteps': 20, 'perturb_time': 10}
    }
    
    legit_results = {}
    for name, params in legitimate.items():
        r = test_system(name, params, n_seeds=5, seed_base=42)
        legit_results[name] = r
        print(f"{name}: consensus={r['consensus_mean']:.3f}±{r['consensus_std']:.3f} CV={r['cv']:.3f}")
    
    # Test adversarial
    print("\n=== ADVERSARIAL SYSTEMS ===")
    adversarial = {
        'replay_memory_spoof': {'n': 30, 'dimensions': 5, 'n_timesteps': 20},
        'delayed_random_coherence': {'n': 30, 'dimensions': 5, 'n_timesteps': 20},
        'temporal_camouflage': {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    }
    
    adv_results = {}
    for name, params in adversarial.items():
        r = test_system(name, params, n_seeds=5, seed_base=42)
        adv_results[name] = r
        print(f"{name}: consensus={r['consensus_mean']:.3f}±{r['consensus_std']:.3f}")
    
    # Discrimination check
    print("\n=== DISCRIMINATION ===")
    stable_consensus = legit_results['stable_hierarchy']['consensus_mean']
    random_consensus = legit_results['random_temporal']['consensus_mean']
    diff = abs(stable_consensus - random_consensus)
    print(f"Stable vs Random: {diff:.3f} (target: >0.15)")
    
    # Check if adversarial fooled legitimate
    fooled = 0
    for name, r in adv_results.items():
        if abs(r['consensus_mean'] - stable_consensus) < 0.1:
            fooled += 1
    print(f"Adversaries that fooled (within 0.1 of stable): {fooled}/{len(adversarial)}")
    
    # Save results
    output = '/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/multi_seed_results.json'
    with open(output, 'w') as f:
        json.dump({'legitimate': legit_results, 'adversarial': adv_results}, f, indent=2)
    print(f"\nSaved: {output}")