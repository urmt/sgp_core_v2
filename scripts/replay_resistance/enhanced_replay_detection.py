"""
Enhanced Replay Detection with Temporal Pattern Analysis

Distinguish between replay (constant high similarity) vs 
real persistence (perturbation then recovery).
"""

import numpy as np
import json
import sys
from typing import Dict, List

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/temporal_adversarial_expansion')

from temporal_dynamics import generate_temporal_system
from advanced_temporal_adversaries import generate_temporal_adversary
from replay_resistance import replay_similarity, novelty_decay, temporal_entropy


def temporal_similarity_profile(sequence) -> Dict:
    """Analyze similarity over time to detect replay patterns."""
    similarities = []
    
    for i in range(len(sequence) - 1):
        a = sequence[i].flatten()
        b = sequence[i + 1].flatten()
        
        if len(a) > 1:
            c = np.corrcoef(a, b)[0, 1]
            if not np.isnan(c):
                similarities.append(c)
    
    if not similarities:
        return {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'trend': 0}
    
    # Compute profile features
    mean_sim = np.mean(similarities)
    std_sim = np.std(similarities)
    min_sim = np.min(similarities)
    max_sim = np.max(similarities)
    
    # Trend: is similarity increasing (replay) or varying (real)?
    if len(similarities) > 2:
        early = np.mean(similarities[:len(similarities)//3])
        late = np.mean(similarities[-len(similarities)//3:])
        trend = late - early
    else:
        trend = 0
    
    # Range: replay has very low range (constant)
    range_sim = max_sim - min_sim
    
    return {
        'mean': mean_sim,
        'std': std_sim,
        'min': min_sim,
        'max': max_sim,
        'trend': trend,
        'range': range_sim
    }


def enhanced_replay_detection(sequence, seed: int = 42) -> Dict:
    """
    Enhanced anti-replay detection with temporal pattern analysis.
    
    Key insight:
    - Replay: constant high similarity (low std, low range, near-zero trend)
    - Real persistence: varying similarity (higher std, higher range)
    """
    # Basic metrics
    similarity = replay_similarity(sequence)
    novelty = novelty_decay(sequence)
    entropy = temporal_entropy(sequence)
    
    # Temporal pattern analysis
    profile = temporal_similarity_profile(sequence)
    
    # Replay indicators:
    # 1. Very high mean similarity (>0.95)
    # 2. Very low std (<0.05)
    # 3. Low range (<0.1)
    # 4. Near-zero trend
    
    is_constant_replay = (
        profile['mean'] > 0.95 and
        profile['std'] < 0.05 and
        profile['range'] < 0.1 and
        abs(profile['trend']) < 0.1
    )
    
    # Score: combine basic metrics with pattern analysis
    base_score = (
        (1.0 - similarity) * 0.3 +
        min(novelty, 2.0) * 0.3 +
        min(entropy, 6.0) * 0.2 +
        (1.0 - profile['std']) * 0.2
    )
    
    # Add penalty for constant replay pattern
    if is_constant_replay:
        base_score -= 2.0
    
    is_replay = bool(base_score < 0.2 or is_constant_replay)
    
    return {
        "replay_similarity": float(similarity),
        "novelty_decay": float(novelty),
        "temporal_entropy": float(entropy),
        "similarity_mean": profile['mean'],
        "similarity_std": profile['std'],
        "similarity_range": profile['range'],
        "similarity_trend": profile['trend'],
        "is_constant_replay": is_constant_replay,
        "anti_replay_score": float(base_score),
        "is_replay": is_replay
    }


def test_enhanced():
    """Test enhanced detection."""
    np.random.seed(42)
    
    print("=" * 60)
    print("ENHANCED REPLAY DETECTION")
    print("=" * 60)
    
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    
    # Legitimate
    print("\n=== LEGITIMATE ===")
    legitimate = ['stable_hierarchy', 'random_temporal', 'perturb_recover']
    legit_results = {}
    
    for system in legitimate:
        traj, _ = generate_temporal_system(system, seed=42, **params)
        r = enhanced_replay_detection(traj, 42)
        legit_results[system] = r
        print(f"{system}: score={r['anti_replay_score']:.3f}, const_replay={r['is_constant_replay']}, is_replay={r['is_replay']}")
    
    # Adversarial
    print("\n=== ADVERSARIAL ===")
    adversarial = ['replay_memory_spoof', 'delayed_random_coherence', 
                   'temporal_camouflage', 'phase_shift_replay']
    adv_results = {}
    
    for system in adversarial:
        traj, _ = generate_temporal_adversary(system, seed=42, **params)
        r = enhanced_replay_detection(traj, 42)
        adv_results[system] = r
        print(f"{system}: score={r['anti_replay_score']:.3f}, const_replay={r['is_constant_replay']}, is_replay={r['is_replay']}")
    
    # Summary
    print("\n=== SUMMARY ===")
    detected = sum(1 for r in adv_results.values() if r['is_replay'])
    false_pos = sum(1 for r in legit_results.values() if r['is_replay'])
    
    print(f"Adversarial detected: {detected}/{len(adversarial)}")
    print(f"False positives: {false_pos}/{len(legitimate)}")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/replay_resistance/enhanced_results.json'
    with open(output, 'w') as f:
        json.dump({
            'legitimate': legit_results,
            'adversarial': adv_results,
            'detection_rate': detected / len(adversarial),
            'false_positive_rate': false_pos / len(legitimate)
        }, f, indent=2, default=str)
    print(f"Saved: {output}")


if __name__ == '__main__':
    test_enhanced()