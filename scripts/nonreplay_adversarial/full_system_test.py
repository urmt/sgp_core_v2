"""
Non-Replay Adversarial Detection - Full Test

Test against all temporal systems from V2_009/V2_010.
"""

import numpy as np
import json
import sys
from typing import Dict

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/temporal_adversarial_expansion')
sys.path.insert(0, 'scripts/replay_resistance')

from temporal_dynamics import generate_temporal_system
from advanced_temporal_adversaries import generate_temporal_adversary
from final_replay_detection import final_replay_detection
from nonreplay_detection import (
    temporal_transition_variance, phase_shift_instability,
    coherence_collapse, state_entropy, structural_stability,
    anti_camouflage_score
)


def comprehensive_detection(sequence, seed: int = 42) -> Dict:
    """
    Combine replay detection (V2_011) with non-replay detection (V2_012).
    
    Stage 1: Replay detection (drift < 0.05)
    Stage 2: Non-replay adversarial detection
    """
    # Stage 1: Replay check (from V2_011)
    drift = np.mean(np.abs(sequence[0] - sequence[-1]))
    is_replay = drift < 0.05
    
    if is_replay:
        return {
            'is_adversarial': True,
            'attack_type': 'replay',
            'drift': float(drift),
            'anti_replay_score': 0,
            'anti_camouflage_score': 0
        }
    
    # Stage 2: Non-replay adversarial detection
    camouflage = anti_camouflage_score(sequence, seed)
    
    # Combine scores
    is_adversarial = is_replay or camouflage['is_adversarial']
    
    return {
        'is_adversarial': is_adversarial,
        'attack_type': 'non_replay' if is_adversarial and not is_replay else ('replay' if is_replay else 'none'),
        'drift': float(drift),
        'anti_replay_score': 1.0 - min(drift / 0.3, 1.0),
        'transition_variance': camouflage['transition_variance'],
        'phase_instability': camouflage['phase_instability'],
        'coherence_collapse': camouflage['coherence_collapse'],
        'anti_camouflage_score': camouflage['anti_camouflage_score']
    }


def test_all_systems():
    """Test comprehensive detection."""
    np.random.seed(42)
    
    print("=" * 60)
    print("NON-REPLAY ADVERSARIAL DETECTION")
    print("=" * 60)
    
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    
    # Legitimate
    print("\n=== LEGITIMATE ===")
    legitimate = ['stable_hierarchy', 'random_temporal', 'perturb_recover']
    legit_results = {}
    
    for system in legitimate:
        traj, _ = generate_temporal_system(system, seed=42, **params)
        r = comprehensive_detection(traj, 42)
        legit_results[system] = r
        print(f"{system}: adversarial={r['is_adversarial']}, type={r['attack_type']}")
    
    # Adversarial (the ones that passed V2_011)
    print("\n=== ADVERSARIAL (non-replay) ===")
    adversarial = ['delayed_random_coherence', 'temporal_camouflage', 'phase_shift_replay']
    adv_results = {}
    
    for system in adversarial:
        traj, _ = generate_temporal_adversary(system, seed=42, **params)
        r = comprehensive_detection(traj, 42)
        adv_results[system] = r
        print(f"{system}: adversarial={r['is_adversarial']}, type={r['attack_type']}")
        print(f"  drift={r['drift']:.4f}, trans_var={r['transition_variance']:.4f}")
    
    # Also test replay (should be caught by V2_011)
    print("\n=== REPLAY (should be caught by V2_011) ===")
    traj, _ = generate_temporal_adversary('replay_memory_spoof', seed=42, **params)
    r = comprehensive_detection(traj, 42)
    print(f"replay_memory_spoof: adversarial={r['is_adversarial']}, type={r['attack_type']}")
    
    # Summary
    print("\n=== SUMMARY ===")
    false_pos = sum(1 for r in legit_results.values() if r['is_adversarial'])
    detected = sum(1 for r in adv_results.values() if r['is_adversarial'])
    
    print(f"False positives (legitimate flagged): {false_pos}/{len(legitimate)}")
    print(f"Adversarial detected: {detected}/{len(adversarial)}")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/nonreplay_adversarial/comprehensive_results.json'
    with open(output, 'w') as f:
        json.dump({
            'legitimate': legit_results,
            'adversarial': adv_results,
            'false_positive_rate': false_pos / len(legitimate),
            'detection_rate': detected / len(adversarial)
        }, f, indent=2, default=str)
    print(f"\nSaved: {output}")


if __name__ == '__main__':
    test_all_systems()