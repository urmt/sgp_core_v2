"""
Ensemble Hardening

Build ensemble voting to resist adversarial spoofing.
"""

import numpy as np
import json
import sys
from typing import Dict, List
sys.path.insert(0, 'scripts/temporal_memory')

from temporal_dynamics import generate_temporal_system
from memory_metrics import (
    InteractionMemoryScore, StructuralPersistence,
    TemporalFragmentationVariance, TemporalConsensusScore
)
sys.path.insert(0, 'scripts/temporal_adversarial_expansion')
from advanced_temporal_adversaries import generate_temporal_adversary


def compute_hardened_score(traj: np.ndarray, seed: int) -> Dict:
    """Compute ensemble of temporal metrics."""
    memory = InteractionMemoryScore(seed).compute(traj)
    persist = StructuralPersistence(seed).compute(traj)
    frag = TemporalFragmentationVariance(seed).compute(traj)
    consensus = TemporalConsensusScore(seed).compute(traj)
    
    # Normalize each metric to 0-1 range
    metrics = np.array([
        memory['memory_score_mean'],
        persist['persistence_mean'],
        1 - frag['fragmentation_std'],  # Low fragmentation is good
        consensus['consensus_mean']
    ])
    
    # Soft voting with weights
    weights = [0.25, 0.25, 0.2, 0.3]
    score = np.sum(metrics * weights)
    
    # Spoof penalty: if memory >> consensus, likely spoof
    memory_consensus_gap = abs(memory['memory_score_mean'] - consensus['consensus_mean'])
    spoof_penalty = min(0.3, memory_consensus_gap * 0.5)
    
    final_score = max(0, score - spoof_penalty)
    
    return {
        'hardened_score': final_score,
        'raw_ensemble': score,
        'spoof_penalty': spoof_penalty,
        'memory': memory['memory_score_mean'],
        'consensus': consensus['consensus_mean']
    }


if __name__ == '__main__':
    np.random.seed(42)
    print("=" * 60)
    print("ENSEMBLE HARDENING")
    print("=" * 60)
    
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    
    # Legitimate systems
    print("\n=== LEGITIMATE SYSTEMS ===")
    legitimate = ['stable_hierarchy', 'perturb_recover']
    for system in legitimate:
        traj, _ = generate_temporal_system(system, seed=42, **params)
        result = compute_hardened_score(traj, 42)
        print(f"{system}: hardened={result['hardened_score']:.3f} spoof_penalty={result['spoof_penalty']:.3f}")
    
    # Adversarial systems
    print("\n=== ADVERSARIAL SYSTEMS ===")
    adversarial = ['replay_memory_spoof', 'delayed_random_coherence', 'temporal_camouflage']
    for system in adversarial:
        traj, _ = generate_temporal_adversary(system, seed=42, **params)
        result = compute_hardened_score(traj, 42)
        print(f"{system}: hardened={result['hardened_score']:.3f} spoof_penalty={result['spoof_penalty']:.3f}")
    
    # Test spoof detection
    print("\n=== SPOOF DETECTION ===")
    replay_traj, _ = generate_temporal_adversary('replay_memory_spoof', seed=42, **params)
    stable_traj, _ = generate_temporal_system('stable_hierarchy', seed=42, **params)
    
    replay_result = compute_hardened_score(replay_traj, 42)
    stable_result = compute_hardened_score(stable_traj, 42)
    
    print(f"Stable: score={stable_result['hardened_score']:.3f} memory={stable_result['memory']:.3f} consensus={stable_result['consensus']:.3f}")
    print(f"Replay: score={replay_result['hardened_score']:.3f} memory={replay_result['memory']:.3f} consensus={replay_result['consensus']:.3f}")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/ensemble_hardening.json'
    with open(output, 'w') as f:
        json.dump({
            'stable': stable_result,
            'replay_spoof': replay_result
        }, f, indent=2)
    print(f"\nSaved: {output}")