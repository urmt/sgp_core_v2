"""
SGP-CORE V2 Scale Recovery Protocol

Fix scale-collapse problem from V2_010.
Goal: Maintain separation across N = 50, 100, 250, 500, 1000
"""

import numpy as np
from typing import Dict, List


def normalized_memory(memory_score: float, N: int) -> float:
    """Normalize memory by system size."""
    return memory_score / np.log(N + 1)


def normalized_persistence(persistence_score: float, N: int) -> float:
    """Normalize persistence by sqrt scale."""
    return persistence_score / np.sqrt(N)


def normalized_consensus(consensus_score: float, N: int) -> float:
    """Normalize consensus by log scale."""
    return consensus_score / np.log(N + 1)


def scale_stability(scores: List[float]) -> float:
    """Measures consistency across scales."""
    scores = np.array(scores)
    return 1.0 / (1.0 + np.std(scores))


def separation_ratio(real_scores: List[float], random_scores: List[float]) -> float:
    """Compute separation ratio between real and random systems."""
    real_mean = np.mean(real_scores)
    rand_mean = np.mean(random_scores)
    return real_mean / (rand_mean + 1e-8)


def scale_invariant_score(memory: float, persistence: float, consensus: float, N: int) -> Dict:
    """
    Compute scale-invariant temporal score.
    
    Key insight: scale metrics by log(N) or sqrt(N) to compensate for
    the natural metric decay at larger scales.
    """
    norm_memory = normalized_memory(memory, N)
    norm_persist = normalized_persistence(persistence, N)
    norm_consensus = normalized_consensus(consensus, N)
    
    # Combined score with weighting
    combined = (
        norm_memory * 0.3 +
        norm_persist * 0.3 +
        norm_consensus * 0.4
    )
    
    return {
        'raw_memory': memory,
        'raw_persistence': persistence,
        'raw_consensus': consensus,
        'norm_memory': norm_memory,
        'norm_persistence': norm_persist,
        'norm_consensus': norm_consensus,
        'scale_invariant_score': combined,
        'N': N
    }


def cross_scale_separation(stable_scores: List[float], random_scores: List[float]) -> Dict:
    """Compute cross-scale separation metrics."""
    ratio = separation_ratio(stable_scores, random_scores)
    stable_stab = scale_stability(stable_scores)
    random_stab = scale_stability(random_scores)
    
    return {
        'separation_ratio': ratio,
        'stable_stability': stable_stab,
        'random_stability': random_stab,
        'min_separation': min(stable_scores) / (max(random_scores) + 1e-8)
    }


if __name__ == "__main__":
    SEED = 42
    rng = np.random.RandomState(SEED)
    
    print("=" * 60)
    print("SCALE RECOVERY PROTOCOL")
    print("=" * 60)
    
    # Test with synthetic data
    scales = [50, 100, 250, 500]
    
    legit = []
    randoms = []
    
    for N in scales:
        base_real = 0.7 + rng.randn() * 0.03
        base_rand = 0.4 + rng.randn() * 0.03
        
        legit.append(normalized_memory(base_real, N))
        randoms.append(normalized_memory(base_rand, N))
    
    sep = separation_ratio(legit, randoms)
    
    print(f"\nScales: {scales}")
    print(f"Legit normalized: {np.round(legit, 4)}")
    print(f"Random normalized: {np.round(randoms, 4)}")
    print(f"Separation ratio: {sep:.4f}")
    print(f"Stable stability: {scale_stability(legit):.4f}")
    print(f"Random stability: {scale_stability(randoms):.4f}")