"""
Replay Resistance - Full System Test

Test replay resistance metrics against all temporal systems.
"""

import numpy as np
import json
import sys
from typing import Dict

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/temporal_adversarial_expansion')

from temporal_dynamics import generate_temporal_system
from advanced_temporal_adversaries import generate_temporal_adversary
from replay_resistance import replay_detection_score


def test_replay_resistance(system_type: str, params: Dict, seed: int = 42, 
                          is_adversarial: bool = False) -> Dict:
    """Test a system against replay resistance metrics."""
    try:
        if is_adversarial:
            traj, _ = generate_temporal_adversary(system_type, seed=seed, **params)
        else:
            traj, _ = generate_temporal_system(system_type, seed=seed, **params)
        
        result = replay_detection_score(traj, seed)
        return result
    except Exception as e:
        return {'error': str(e)}


if __name__ == '__main__':
    np.random.seed(42)
    
    print("=" * 60)
    print("REPLAY RESISTANCE - FULL SYSTEM TEST")
    print("=" * 60)
    
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    
    # Legitimate systems
    print("\n=== LEGITIMATE SYSTEMS ===")
    legitimate = ['stable_hierarchy', 'random_temporal', 'perturb_recover']
    legit_results = {}
    
    for system in legitimate:
        r = test_replay_resistance(system, params, seed=42, is_adversarial=False)
        legit_results[system] = r
        print(f"{system}: anti_replay={r.get('anti_replay_score', 'N/A'):.3f}, is_replay={r.get('is_replay', 'N/A')}")
    
    # Adversarial systems
    print("\n=== ADVERSARIAL SYSTEMS ===")
    adversarial = {
        'replay_memory_spoof': True,
        'delayed_random_coherence': True,
        'temporal_camouflage': True,
        'phase_shift_replay': True
    }
    
    adv_results = {}
    for system, is_adv in adversarial.items():
        r = test_replay_resistance(system, params, seed=42, is_adversarial=is_adv)
        adv_results[system] = r
        detected = r.get('is_replay', False)
        print(f"{system}: anti_replay={r.get('anti_replay_score', 'N/A'):.3f}, detected={detected}")
    
    # Summary
    print("\n=== DETECTION SUMMARY ===")
    detected_count = sum(1 for r in adv_results.values() if r.get('is_replay', False))
    total_adv = len(adversarial)
    print(f"Detected: {detected_count}/{total_adv}")
    
    # Legit should not be flagged
    false_positives = sum(1 for r in legit_results.values() if r.get('is_replay', False))
    print(f"False positives (legit flagged): {false_positives}/{len(legitimate)}")
    
    # Save results
    output = '/home/student/sgp_core_v2/outputs/replay_resistance/replay_test_results.json'
    with open(output, 'w') as f:
        json.dump({
            'legitimate': legit_results,
            'adversarial': adv_results,
            'detection_rate': detected_count / total_adv,
            'false_positive_rate': false_positives / len(legitimate)
        }, f, indent=2)
    print(f"\nSaved: {output}")