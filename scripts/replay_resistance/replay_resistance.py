"""
SGP-CORE V2 Replay Resistance Protocol

Detect and reject replay-based temporal spoofing attacks.
"""

import numpy as np
from typing import Dict

SEED = 42


def replay_similarity(sequence):
    """
    Measures repeated temporal reuse.
    High values indicate replay spoofing.
    """
    corrs = []
    
    for i in range(len(sequence) - 1):
        a = sequence[i].flatten()
        b = sequence[i + 1].flatten()
        
        if len(a) > 1 and len(b) > 1:
            c = np.corrcoef(a, b)[0, 1]
            if not np.isnan(c):
                corrs.append(c)
    
    return np.mean(corrs) if corrs else 0


def novelty_decay(sequence):
    """
    Measures whether new structure appears over time.
    Replay attacks should decay toward zero novelty.
    """
    novelties = []
    
    for i in range(len(sequence) - 1):
        diff = np.mean(np.abs(sequence[i + 1] - sequence[i]))
        novelties.append(diff)
    
    return np.mean(novelties) if novelties else 0


def temporal_entropy(sequence):
    """
    Entropy of temporal transitions.
    Replay systems should have low entropy.
    """
    transitions = []
    
    for i in range(len(sequence) - 1):
        delta = sequence[i + 1] - sequence[i]
        transitions.extend(delta.flatten())
    
    hist, _ = np.histogram(transitions, bins=30, density=True)
    hist = hist + 1e-12
    
    return -np.sum(hist * np.log(hist))


def structural_variance_ratio(sequence):
    """
    Ratio of within-timestep to between-timestep variance.
    Replay has low within-timestep variance (same data).
    """
    within_var = []
    between_var = []
    
    for i in range(len(sequence)):
        within_var.append(np.var(sequence[i]))
    
    for i in range(len(sequence) - 1):
        between_var.append(np.mean(np.abs(sequence[i + 1] - sequence[i])))
    
    within = np.mean(within_var) if within_var else 1
    between = np.mean(between_var) if between_var else 1
    
    return within / (between + 1e-10)


def replay_detection_score(sequence, seed: int = 42) -> Dict:
    """
    Compute anti-replay score.
    
    Higher score = more likely legitimate
    Lower score = more likely replay attack
    """
    similarity = replay_similarity(sequence)
    novelty = novelty_decay(sequence)
    entropy = temporal_entropy(sequence)
    variance_ratio = structural_variance_ratio(sequence)
    
    # Anti-replay score: penalize high similarity, reward novelty/entropy
    score = (
        (1.0 - similarity) * 0.35 +
        novelty * 0.25 +
        entropy * 0.2 +
        min(variance_ratio, 1.0) * 0.2
    )
    
    return {
        "replay_similarity": float(similarity),
        "novelty_decay": float(novelty),
        "temporal_entropy": float(entropy),
        "variance_ratio": float(variance_ratio),
        "anti_replay_score": float(score),
        "is_replay": bool(score < 0.3)
    }


if __name__ == "__main__":
    rng = np.random.RandomState(SEED)
    
    print("=" * 60)
    print("REPLAY RESISTANCE PROTOCOL")
    print("=" * 60)
    
    # Legit evolving system
    legit = [rng.randn(20, 20) + i * 0.01 for i in range(20)]
    
    # Replay spoof
    base = rng.randn(20, 20)
    replay = [base.copy() for _ in range(20)]
    
    legit_result = replay_detection_score(legit)
    replay_result = replay_detection_score(replay)
    
    print("\nLEGIT SYSTEM")
    for k, v in legit_result.items():
        print(f"{k}: {v:.4f}")
    
    print("\nREPLAY SPOOF")
    for k, v in replay_result.items():
        print(f"{k}: {v:.4f}")
    
    print("\n--- RESULT ---")
    print(f"Legit anti_replay: {legit_result['anti_replay_score']:.4f}")
    print(f"Replay anti_replay: {replay_result['anti_replay_score']:.4f}")
    print(f"Detection: {'PASS' if replay_result['is_replay'] else 'FAIL'}")