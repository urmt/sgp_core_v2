"""
Final Replay Resistance with Data Drift Detection

Key insight: Replay has almost IDENTICAL data (diff ~0.01)
while real systems have meaningful change (diff > 0.1)
"""

import numpy as np
import json
import sys
from typing import Dict

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/temporal_adversarial_expansion')

from temporal_dynamics import generate_temporal_system
from advanced_temporal_adversaries import generate_temporal_adversary


def data_drift(sequence) -> float:
    """Measure actual data change over time."""
    if len(sequence) < 2:
        return 0
    
    # Compare first and last timestep
    drift = np.mean(np.abs(sequence[0] - sequence[-1]))
    
    # Also check middle to end
    mid = len(sequence) // 2
    mid_drift = np.mean(np.abs(sequence[mid] - sequence[-1]))
    
    return (drift + mid_drift) / 2


def replay_similarity_basic(sequence) -> float:
    """Basic similarity metric."""
    corrs = []
    for i in range(len(sequence) - 1):
        a = sequence[i].flatten()
        b = sequence[i + 1].flatten()
        if len(a) > 1:
            c = np.corrcoef(a, b)[0, 1]
            if not np.isnan(c):
                corrs.append(c)
    return np.mean(corrs) if corrs else 0


def novelty_basic(sequence) -> float:
    """Basic novelty metric."""
    novelties = []
    for i in range(len(sequence) - 1):
        diff = np.mean(np.abs(sequence[i + 1] - sequence[i]))
        novelties.append(diff)
    return np.mean(novelties) if novelties else 0


def final_replay_detection(sequence, seed: int = 42) -> Dict:
    """
    Final anti-replay detection combining:
    1. Data drift (key: replay has near-zero drift)
    2. Similarity profile (replay = very high, constant)
    3. Novelty (replay = zero)
    """
    # Key metric: data drift
    drift = data_drift(sequence)
    
    # Similarity
    similarity = replay_similarity_basic(sequence)
    
    # Novelty
    novelty = novelty_basic(sequence)
    
    # Compute score
    # Replay indicators:
    # - Very low drift (<0.05)
    # - Very high similarity (>0.95)
    # - Zero novelty
    
    # Score: higher = more likely real
    # Penalize low drift heavily (most important)
    drift_score = min(drift / 0.3, 1.0) * 0.5
    similarity_score = (1.0 - similarity) * 0.2
    novelty_score = min(novelty / 1.0, 1.0) * 0.3
    
    score = drift_score + similarity_score + novelty_score
    
    # Thresholds
    is_replay = bool(
        drift < 0.05 or           # Almost identical data
        (drift < 0.1 and similarity > 0.95)  # Identical data + high similarity
    )
    
    return {
        "data_drift": float(drift),
        "replay_similarity": float(similarity),
        "novelty_decay": float(novelty),
        "anti_replay_score": float(score),
        "is_replay": is_replay,
        "is_replay_drift_only": bool(drift < 0.05)
    }


def test_final():
    """Test final detection."""
    np.random.seed(42)
    
    print("=" * 60)
    print("FINAL REPLAY RESISTANCE")
    print("=" * 60)
    
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    
    # Legitimate
    print("\n=== LEGITIMATE ===")
    legitimate = ['stable_hierarchy', 'random_temporal', 'perturb_recover']
    legit_results = {}
    
    for system in legitimate:
        traj, _ = generate_temporal_system(system, seed=42, **params)
        r = final_replay_detection(traj, 42)
        legit_results[system] = r
        print(f"{system}: drift={r['data_drift']:.4f}, sim={r['replay_similarity']:.3f}, score={r['anti_replay_score']:.3f}, is_replay={r['is_replay']}")
    
    # Adversarial
    print("\n=== ADVERSARIAL ===")
    adversarial = ['replay_memory_spoof', 'delayed_random_coherence', 
                   'temporal_camouflage', 'phase_shift_replay']
    adv_results = {}
    
    for system in adversarial:
        traj, _ = generate_temporal_adversary(system, seed=42, **params)
        r = final_replay_detection(traj, 42)
        adv_results[system] = r
        print(f"{system}: drift={r['data_drift']:.4f}, sim={r['replay_similarity']:.3f}, score={r['anti_replay_score']:.3f}, is_replay={r['is_replay']}")
    
    # Summary
    print("\n=== SUMMARY ===")
    detected = sum(1 for r in adv_results.values() if r['is_replay'])
    false_pos = sum(1 for r in legit_results.values() if r['is_replay'])
    
    print(f"Adversarial detected: {detected}/{len(adversarial)}")
    print(f"False positives: {false_pos}/{len(legitimate)}")
    
    # Also show drift-only detection
    detected_drift = sum(1 for r in adv_results.values() if r['is_replay_drift_only'])
    print(f"Detected by drift alone: {detected_drift}/{len(adversarial)}")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/replay_resistance/final_results.json'
    with open(output, 'w') as f:
        json.dump({
            'legitimate': legit_results,
            'adversarial': adv_results,
            'detection_rate': detected / len(adversarial),
            'false_positive_rate': false_pos / len(legitimate)
        }, f, indent=2, default=str)
    print(f"\nSaved: {output}")


if __name__ == '__main__':
    test_final()