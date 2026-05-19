"""
Hardened Temporal Metrics

Combine original temporal metrics with replay resistance.
"""

import numpy as np
import json
import sys
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
from final_replay_detection import final_replay_detection


def hardened_temporal_score(system_type: str, params: Dict, seed: int = 42,
                           is_adversarial: bool = False) -> Dict:
    """
    Compute hardened temporal score that includes replay resistance.
    
    Returns:
    - consensus: original TemporalConsensusScore
    - anti_replay: replay resistance score
    - hardened_score: combined score
    - is_replay: whether replay attack detected
    """
    # Generate trajectory
    if is_adversarial:
        traj, _ = generate_temporal_adversary(system_type, seed=seed, **params)
    else:
        traj, _ = generate_temporal_system(system_type, seed=seed, **params)
    
    # Original temporal metrics
    consensus = TemporalConsensusScore(seed).compute(traj)['consensus_mean']
    
    # Replay resistance
    replay = final_replay_detection(traj, seed)
    
    # Hardened score: combine but penalize if replay detected
    if replay['is_replay']:
        # Zero out consensus if replay detected
        hardened = 0.0
    else:
        # Combine: 70% consensus, 30% anti_replay
        hardened = consensus * 0.7 + replay['anti_replay_score'] * 0.3
    
    return {
        'system': system_type,
        'consensus': consensus,
        'anti_replay': replay['anti_replay_score'],
        'data_drift': replay['data_drift'],
        'hardened_score': hardened,
        'is_replay_detected': replay['is_replay'],
        'is_adversarial': is_adversarial
    }


def test_hardened():
    """Test hardened metrics."""
    np.random.seed(42)
    
    print("=" * 60)
    print("HARDENED TEMPORAL METRICS")
    print("=" * 60)
    
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    
    # Legitimate
    print("\n=== LEGITIMATE ===")
    legitimate = ['stable_hierarchy', 'random_temporal', 'perturb_recover']
    
    for system in legitimate:
        r = hardened_temporal_score(system, params, seed=42, is_adversarial=False)
        print(f"{system}: consensus={r['consensus']:.3f}, anti_replay={r['anti_replay']:.3f}, hardened={r['hardened_score']:.3f}")
    
    # Adversarial
    print("\n=== ADVERSARIAL ===")
    adversarial = ['replay_memory_spoof', 'delayed_random_coherence', 
                   'temporal_camouflage']
    
    for system in adversarial:
        r = hardened_temporal_score(system, params, seed=42, is_adversarial=True)
        status = "DETECTED" if r['is_replay_detected'] else "PASSED"
        print(f"{system}: consensus={r['consensus']:.3f}, anti_replay={r['anti_replay']:.3f}, hardened={r['hardened_score']:.3f} [{status}]")
    
    # Summary
    print("\n=== COMPARISON ===")
    print("Original (V2_010) vs Hardened (V2_011)")
    
    # Show how replay spoof changes
    replay_orig = 0.987  # from V2_010
    replay_hard = next(r['hardened_score'] for r in [hardened_temporal_score('replay_memory_spoof', params, 42, True)])
    print(f"replay_memory_spoof: {replay_orig} -> {replay_hard:.3f}")
    
    stable_orig = 0.674
    stable_hard = next(r['hardened_score'] for r in [hardened_temporal_score('stable_hierarchy', params, 42, False)])
    print(f"stable_hierarchy: {stable_orig} -> {replay_hard:.3f}")


if __name__ == '__main__':
    test_hardened()