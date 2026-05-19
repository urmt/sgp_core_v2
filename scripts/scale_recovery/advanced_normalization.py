"""
Advanced Scale Recovery

Try multiple normalization strategies to find the best.
"""

import numpy as np
import json
import sys

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/scale_recovery')

from temporal_dynamics import generate_temporal_system
from memory_metrics import InteractionMemoryScore, StructuralPersistence, TemporalConsensusScore


def ratio_based_separation(stable_scores: list, random_scores: list) -> float:
    """Compute ratio-based separation."""
    stable_arr = np.array(stable_scores)
    random_arr = np.array(random_scores)
    
    # Use mean ratio instead of ratio of means
    ratios = stable_arr / (random_arr + 1e-8)
    return np.mean(ratios)


def differential_separation(stable_scores: list, random_scores: list) -> float:
    """Compute differential separation (difference in normalized space)."""
    stable_arr = np.array(stable_scores)
    random_arr = np.array(random_scores)
    
    # Normalize each to 0-1 within scale
    def normalize(arr):
        min_val, max_val = arr.min(), arr.max()
        if max_val - min_val < 1e-8:
            return arr
        return (arr - min_val) / (max_val - min_val)
    
    stable_norm = normalize(stable_arr)
    random_norm = normalize(random_arr)
    
    return np.mean(stable_norm - random_norm)


def log_scale_normalization(value: float, N: int, base: float = 2.0) -> float:
    """Log-scale normalization."""
    return value / np.log(N + 1)


def sqrt_scale_normalization(value: float, N: int) -> float:
    """Square root normalization."""
    return value / np.sqrt(N)


def power_scale_normalization(value: float, N: int, power: float = 0.5) -> float:
    """Power law normalization."""
    return value / (N ** power)


def test_all_normalizations():
    """Test all normalization strategies."""
    np.random.seed(42)
    
    print("=" * 60)
    print("ADVANCED SCALE RECOVERY")
    print("=" * 60)
    
    scales = [50, 100, 250, 500]
    params = {'dimensions': 5, 'n_timesteps': 20}
    
    # Get raw consensus at each scale
    stable_raw = []
    random_raw = []
    
    for N in scales:
        params['n'] = N
        
        traj_s, _ = generate_temporal_system('stable_hierarchy', seed=42, **params)
        traj_r, _ = generate_temporal_system('random_temporal', seed=42, **params)
        
        stable_raw.append(TemporalConsensusScore(42).compute(traj_s)['consensus_mean'])
        random_raw.append(TemporalConsensusScore(42).compute(traj_r)['consensus_mean'])
    
    print("\nRaw consensus:")
    print(f"  stable: {np.round(stable_raw, 4)}")
    print(f"  random: {np.round(random_raw, 4)}")
    print(f"  raw separation: {ratio_based_separation(stable_raw, random_raw):.4f}")
    
    # Test each normalization
    normalizations = {
        'log': lambda v, n: log_scale_normalization(v, n),
        'sqrt': lambda v, n: sqrt_scale_normalization(v, n),
        'power_0.3': lambda v, n: power_scale_normalization(v, n, 0.3),
        'power_0.4': lambda v, n: power_scale_normalization(v, n, 0.4),
        'power_0.5': lambda v, n: power_scale_normalization(v, n, 0.5),
    }
    
    results = {}
    
    for name, norm_fn in normalizations.items():
        stable_norm = [norm_fn(v, n) for v, n in zip(stable_raw, scales)]
        random_norm = [norm_fn(v, n) for v, n in zip(random_raw, scales)]
        
        sep = ratio_based_separation(stable_norm, random_norm)
        diff = differential_separation(stable_norm, random_norm)
        
        results[name] = {
            'stable': stable_norm,
            'random': random_norm,
            'ratio_sep': sep,
            'diff_sep': diff
        }
        
        print(f"\n{name}:")
        print(f"  stable: {np.round(stable_norm, 4)}")
        print(f"  random: {np.round(random_norm, 4)}")
        print(f"  ratio sep: {sep:.4f}, diff sep: {diff:.4f}")
    
    # Find best
    best = max(results.items(), key=lambda x: x[1]['ratio_sep'])
    print(f"\n=== BEST: {best[0]} with ratio {best[1]['ratio_sep']:.4f} ===")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/scale_recovery/advanced_results.json'
    with open(output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Saved: {output}")


if __name__ == '__main__':
    test_all_normalizations()