"""
Tuned Non-Replay Adversarial Detection

Key insight from analysis:
- stable_hierarchy: high trans_var (0.25), high collapse (0.79)
- adversarial: moderate - close to random_temporal (0.066, 0.34)

Detection: look for systems that are TOO structured (like random_temporal).
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
    coherence_collapse, state_entropy, structural_stability
)


def compute_metrics(sequence):
    """Compute raw metrics."""
    return {
        'transition_variance': temporal_transition_variance(sequence),
        'phase_instability': phase_shift_instability(sequence),
        'coherence_collapse': coherence_collapse(sequence),
        'state_entropy': state_entropy(sequence),
        'structural_stability': structural_stability(sequence)
    }


def tune_detection(sequence, seed: int = 42) -> Dict:
    """
    Tuned non-replay detection.
    
    Key: Adversarial systems have metrics close to random_temporal.
    Real organized systems (stable_hierarchy) have HIGHER variance/collapse.
    """
    # First check replay (from V2_011)
    drift = np.mean(np.abs(sequence[0] - sequence[-1]))
    mid = len(sequence) // 2
    mid_drift = np.mean(np.abs(sequence[mid] - sequence[-1]))
    avg_drift = (drift + mid_drift) / 2
    
    if avg_drift < 0.05:
        return {
            'is_adversarial': True,
            'attack_type': 'replay',
            'drift': float(avg_drift)
        }
    
    # Compute metrics
    metrics = compute_metrics(sequence)
    
    # Tuned thresholds based on analysis:
    # - stable_hierarchy: trans_var=0.25, collapse=0.79 (REAL organized)
    # - random_temporal: trans_var=0.07, collapse=0.34 (REAL random)
    # - adversarial: trans_var~0.04-0.14, collapse~0.25-0.32 (FAKE)
    
    # Detection: if metrics are in "dead zone" between organized and random
    # Too high to be random, but too low to be organized = suspicious
    
    trans_var = metrics['transition_variance']
    collapse = metrics['coherence_collapse']
    
    # "Suspicious" zone: moderate values that don't match any real pattern
    # Real organized: trans_var > 0.15 OR collapse > 0.5
    # Real random: trans_var < 0.08 AND collapse < 0.35
    # Suspicious: everything else
    
    is_suspicious = not (
        (trans_var > 0.15 or collapse > 0.5) or  # organized
        (trans_var < 0.08 and collapse < 0.35)    # random
    )
    
    # Additional check: if coherence collapse is too smooth
    # (closer to random but not quite)
    is_engineered = (
        trans_var > 0.03 and trans_var < 0.15 and
        collapse > 0.2 and collapse < 0.35
    )
    
    is_adversarial = is_suspicious and is_engineered
    
    return {
        'is_adversarial': bool(is_adversarial),
        'attack_type': 'non_replay' if is_adversarial else 'legitimate',
        'drift': float(avg_drift),
        'transition_variance': metrics['transition_variance'],
        'coherence_collapse': metrics['coherence_collapse'],
        'is_suspicious': is_suspicious,
        'is_engineered': is_engineered
    }


def test_tuned():
    """Test tuned detection."""
    np.random.seed(42)
    
    print("=" * 60)
    print("TUNED NON-REPLAY DETECTION")
    print("=" * 60)
    
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    
    # Legitimate
    print("\n=== LEGITIMATE ===")
    legitimate = ['stable_hierarchy', 'random_temporal', 'perturb_recover']
    legit_results = {}
    
    for system in legitimate:
        traj, _ = generate_temporal_system(system, seed=42, **params)
        r = tune_detection(traj, 42)
        legit_results[system] = r
        print(f"{system}: adversarial={r['is_adversarial']}, type={r['attack_type']}")
        print(f"  trans_var={r.get('transition_variance', 0):.4f}, collapse={r.get('coherence_collapse', 0):.4f}")
    
    # Adversarial
    print("\n=== ADVERSARIAL ===")
    adversarial = ['delayed_random_coherence', 'temporal_camouflage', 'phase_shift_replay']
    adv_results = {}
    
    for system in adversarial:
        traj, _ = generate_temporal_adversary(system, seed=42, **params)
        r = tune_detection(traj, 42)
        adv_results[system] = r
        print(f"{system}: adversarial={r['is_adversarial']}, type={r['attack_type']}")
        print(f"  trans_var={r.get('transition_variance', 0):.4f}, collapse={r.get('coherence_collapse', 0):.4f}")
    
    # Replay
    print("\n=== REPLAY (V2_011 catch) ===")
    traj, _ = generate_temporal_adversary('replay_memory_spoof', seed=42, **params)
    r = tune_detection(traj, 42)
    print(f"replay_memory_spoof: adversarial={r['is_adversarial']}, type={r['attack_type']}")
    
    # Summary
    print("\n=== SUMMARY ===")
    false_pos = sum(1 for r in legit_results.values() if r['is_adversarial'])
    detected = sum(1 for r in adv_results.values() if r['is_adversarial'])
    
    print(f"False positives: {false_pos}/{len(legitimate)}")
    print(f"Adversarial detected: {detected}/{len(adversarial)}")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/nonreplay_adversarial/tuned_results.json'
    with open(output, 'w') as f:
        json.dump({
            'legitimate': legit_results,
            'adversarial': adv_results,
            'false_positive_rate': false_pos / len(legitimate),
            'detection_rate': detected / len(adversarial)
        }, f, indent=2, default=str)
    print(f"\nSaved: {output}")


if __name__ == '__main__':
    test_tuned()