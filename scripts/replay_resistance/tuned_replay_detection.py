"""
Tuned Replay Resistance Metrics

Improved thresholds and metric weighting.
"""

import numpy as np
import json
import sys
from typing import Dict

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/temporal_adversarial_expansion')

from temporal_dynamics import generate_temporal_system
from advanced_temporal_adversaries import generate_temporal_adversary
from replay_resistance import (
    replay_similarity, novelty_decay, temporal_entropy,
    structural_variance_ratio, replay_detection_score
)


def tuned_replay_detection(sequence, seed: int = 42) -> Dict:
    """
    Tuned anti-replay detection with better thresholds.
    """
    similarity = replay_similarity(sequence)
    novelty = novelty_decay(sequence)
    entropy = temporal_entropy(sequence)
    variance_ratio = structural_variance_ratio(sequence)
    
    # Clip variance ratio to avoid extreme values
    variance_ratio = np.clip(variance_ratio, 0, 100)
    
    # Tuned score: focus on similarity and novelty
    # High similarity = replay (bad)
    # High novelty = real (good)
    # Low entropy = replay (bad)
    
    score = (
        (1.0 - similarity) * 0.4 +    # Cap similarity contribution
        min(novelty, 2.0) * 0.35 +     # Cap novelty
        min(entropy, 6.0) * 0.15 +     # Cap entropy
        min(variance_ratio / 10, 1.0) * 0.1  # Scale variance
    )
    
    # More lenient threshold: 0.2 instead of 0.3
    is_replay = bool(score < 0.2)
    
    return {
        "replay_similarity": float(similarity),
        "novelty_decay": float(novelty),
        "temporal_entropy": float(entropy),
        "variance_ratio": float(variance_ratio),
        "anti_replay_score": float(score),
        "is_replay": is_replay
    }


def test_all_systems():
    """Test tuned metrics against all systems."""
    np.random.seed(42)
    
    print("=" * 60)
    print("TUNED REPLAY RESISTANCE")
    print("=" * 60)
    
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    
    # Legitimate
    print("\n=== LEGITIMATE ===")
    legitimate = ['stable_hierarchy', 'random_temporal', 'perturb_recover']
    legit_results = {}
    
    for system in legitimate:
        traj, _ = generate_temporal_system(system, seed=42, **params)
        r = tuned_replay_detection(traj, 42)
        legit_results[system] = r
        print(f"{system}: anti_replay={r['anti_replay_score']:.3f}, is_replay={r['is_replay']}")
    
    # Adversarial
    print("\n=== ADVERSARIAL ===")
    adversarial = ['replay_memory_spoof', 'delayed_random_coherence', 
                   'temporal_camouflage', 'phase_shift_replay']
    adv_results = {}
    
    for system in adversarial:
        traj, _ = generate_temporal_adversary(system, seed=42, **params)
        r = tuned_replay_detection(traj, 42)
        adv_results[system] = r
        print(f"{system}: anti_replay={r['anti_replay_score']:.3f}, is_replay={r['is_replay']}")
    
    # Summary
    print("\n=== SUMMARY ===")
    detected = sum(1 for r in adv_results.values() if r['is_replay'])
    false_pos = sum(1 for r in legit_results.values() if r['is_replay'])
    
    print(f"Adversarial detected: {detected}/{len(adversarial)}")
    print(f"False positives: {false_pos}/{len(legitimate)}")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/replay_resistance/tuned_results.json'
    with open(output, 'w') as f:
        json.dump({
            'legitimate': legit_results,
            'adversarial': adv_results,
            'detection_rate': detected / len(adversarial),
            'false_positive_rate': false_pos / len(legitimate)
        }, f, indent=2)
    print(f"Saved: {output}")


if __name__ == '__main__':
    test_all_systems()