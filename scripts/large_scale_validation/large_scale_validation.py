"""
SGP-CORE V2 Large Scale Validation (Optimized)

Validate V2_013 product metric at moderate scales.
"""

import numpy as np
import json
import sys
import time
from typing import Dict

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/temporal_adversarial_expansion')
sys.path.insert(0, 'scripts/replay_resistance')

from temporal_dynamics import generate_temporal_system
from memory_metrics import (
    InteractionMemoryScore, StructuralPersistence,
    TemporalConsensusScore
)
from advanced_temporal_adversaries import generate_temporal_adversary
from final_replay_detection import data_drift, final_replay_detection


SEEDS = [1, 2, 3, 4, 5]
SCALES = [100, 250, 500, 750]  # Reduced from 2500


def product_metric(memory: float, persistence: float, consensus: float) -> float:
    return (memory * persistence * consensus) ** (1/3)


def evaluate_system(system_type: str, n: int, seed: int, 
                    params: Dict, is_adversarial: bool = False) -> Dict:
    if is_adversarial:
        traj, _ = generate_temporal_adversary(system_type, seed=seed, n=n, **params)
    else:
        traj, _ = generate_temporal_system(system_type, seed=seed, n=n, **params)
    
    memory = InteractionMemoryScore(seed).compute(traj)['memory_score_mean']
    persistence = StructuralPersistence(seed).compute(traj)['persistence_mean']
    consensus = TemporalConsensusScore(seed).compute(traj)['consensus_mean']
    
    return {
        'memory': memory,
        'persistence': persistence,
        'consensus': consensus,
        'product_score': product_metric(memory, persistence, consensus)
    }


if __name__ == '__main__':
    np.random.seed(42)
    
    print("=" * 60)
    print("V2_014 LARGE SCALE VALIDATION")
    print("=" * 60)
    
    params = {'dimensions': 5, 'n_timesteps': 20}
    results = {}
    
    # Core validation
    print("\n=== CORE SYSTEM VALIDATION ===")
    
    for n in SCALES:
        print(f"\n--- N = {n} ---")
        
        stable_scores = []
        random_scores = []
        
        for seed in SEEDS:
            np.random.seed(seed)
            
            stable = evaluate_system('stable_hierarchy', n, seed, params)
            random = evaluate_system('random_temporal', n, seed, params)
            
            stable_scores.append(stable['product_score'])
            random_scores.append(random['product_score'])
        
        stable_mean = np.mean(stable_scores)
        random_mean = np.mean(random_scores)
        ratio = stable_mean / (random_mean + 1e-9)
        
        results[n] = {
            'stable_mean': stable_mean,
            'random_mean': random_mean,
            'ratio': ratio,
            'stable_cv': np.std(stable_scores) / (stable_mean + 1e-9),
            'random_cv': np.std(random_scores) / (random_mean + 1e-9)
        }
        
        print(f"  stable: {stable_mean:.4f} ± {np.std(stable_scores):.4f}")
        print(f"  random: {random_mean:.4f} ± {np.std(random_scores):.4f}")
        print(f"  ratio: {ratio:.2f}x")
    
    # Adversarial check
    print("\n=== ADVERSARIAL CHECK (N=250) ===")
    np.random.seed(42)
    n = 250
    
    replay = evaluate_system('replay_memory_spoof', n, 42, params, is_adversarial=True)
    traj, _ = generate_temporal_adversary('replay_memory_spoof', seed=42, n=n, **params)
    drift_check = final_replay_detection(traj, 42)
    
    print(f"  replay score: {replay['product_score']:.4f}")
    print(f"  drift: {drift_check['data_drift']:.4f}")
    print(f"  detected: {drift_check['is_replay']}")
    
    # Runtime
    print("\n=== RUNTIME (N=500) ===")
    np.random.seed(42)
    start = time.time()
    evaluate_system('stable_hierarchy', 500, 42, params)
    elapsed = (time.time() - start) * 1000
    print(f"  {elapsed:.1f}ms")
    
    # Summary
    print("\n=== SUMMARY ===")
    min_ratio = min(results[n]['ratio'] for n in SCALES)
    print(f"Min ratio across scales: {min_ratio:.2f}x")
    print(f"Target (>1.5x): {'PASS' if min_ratio > 1.5 else 'FAIL'}")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/large_scale_validation/large_scale_results.json'
    with open(output, 'w') as f:
        json.dump({'results': results, 'min_ratio': min_ratio}, f, indent=2, default=str)
    print(f"\nSaved: {output}")