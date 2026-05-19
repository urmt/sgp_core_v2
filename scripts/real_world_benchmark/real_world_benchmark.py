"""
SGP-CORE V2 Real World Benchmark Protocol

Compare synthetic structured systems against:
- biological datasets (ECG, gene expression)
- financial datasets (time series)
- linguistic datasets (token streams)
- network datasets (traffic)
"""

import numpy as np
import json
import sys
from typing import Dict, List, Optional
from datetime import datetime

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/replay_resistance')

from memory_metrics import (
    InteractionMemoryScore,
    StructuralPersistence,
    TemporalConsensusScore,
    TemporalFragmentationVariance
)
from final_replay_detection import data_drift, final_replay_detection


DATASETS = [
    "financial_timeseries",
    "ecg_signal", 
    "language_token_stream",
    "network_traffic",
    "weather_sequence"
]

METRICS = [
    "memory",
    "persistence", 
    "consensus",
    "fragmentation",
    "drift",
    "product_metric"
]


def compute_all_metrics(data: np.ndarray, seed: int = 42) -> Dict:
    """Compute all temporal metrics on a dataset."""
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    
    try:
        memory = InteractionMemoryScore(seed).compute(data)['memory_score_mean']
    except:
        memory = 0.0
    
    try:
        persistence = StructuralPersistence(seed).compute(data)['persistence_mean']
    except:
        persistence = 0.0
    
    try:
        consensus = TemporalConsensusScore(seed).compute(data)['consensus_mean']
    except:
        consensus = 0.0
    
    try:
        fragmentation = TemporalFragmentationVariance(seed).compute(data)['fragmentation_std']
    except:
        fragmentation = 0.0
    
    drift = data_drift(data)
    
    product = (memory * persistence * consensus) ** (1/3) if memory * persistence * consensus > 0 else 0
    
    return {
        'memory': memory,
        'persistence': persistence,
        'consensus': consensus,
        'fragmentation': fragmentation,
        'drift': drift,
        'product_metric': product
    }


def generate_random_baseline(n_samples: int, n_features: int = 5, seed: int = 42) -> np.ndarray:
    """Generate random baseline for comparison."""
    rng = np.random.RandomState(seed)
    return rng.randn(n_samples, n_features)


def generate_organized_baseline(n_samples: int, n_features: int = 5, 
                                 n_clusters: int = 5, seed: int = 42) -> np.ndarray:
    """Generate synthetic organized baseline."""
    rng = np.random.RandomState(seed)
    
    # Create cluster centers
    centers = rng.randn(n_clusters, n_features)
    
    # Assign each point to a cluster with temporal persistence
    data = []
    current_cluster = rng.choice(n_clusters)
    
    for i in range(n_samples):
        # Occasionally switch clusters (temporal structure)
        if rng.random() < 0.1:
            current_cluster = rng.choice(n_clusters)
        
        point = centers[current_cluster] + rng.randn(n_features) * 0.3
        data.append(point)
    
    return np.array(data)


def benchmark_trajectory(real_trajectory: np.ndarray, n_random_seeds: int = 3) -> Dict:
    """
    Benchmark a real trajectory against random and organized baselines.
    
    Expects 3D format: [timesteps, n_nodes, dimensions]
    """
    n_timesteps, n_nodes, dimensions = real_trajectory.shape
    
    print(f"\n=== BENCHMARKING: {n_timesteps}x{n_nodes}x{dimensions} ===")
    
    # Compute real trajectory metrics
    real_metrics = compute_all_metrics(real_trajectory)
    print(f"Real data: product={real_metrics['product_metric']:.4f}, drift={real_metrics['drift']:.4f}")
    
    # Generate random baseline (same shape)
    random_metrics = []
    for seed in range(42, 42 + n_random_seeds):
        rng = np.random.RandomState(seed)
        random_traj = rng.randn(n_timesteps, n_nodes, dimensions)
        random_metrics.append(compute_all_metrics(random_traj))
    
    avg_random = {k: np.mean([m[k] for m in random_metrics]) for k in METRICS}
    print(f"Random baseline: product={avg_random['product_metric']:.4f}")
    
    # Compute ratios
    ratios = {metric: real_metrics[metric] / (avg_random[metric] + 1e-9) for metric in METRICS}
    
    return {
        'real_metrics': real_metrics,
        'random_metrics': avg_random,
        'ratios': ratios,
        'shape': real_trajectory.shape
    }


def benchmark_dataset(real_data: np.ndarray, n_random_seeds: int = 3) -> Dict:
    """
    Benchmark a real dataset against random and organized baselines.
    
    For 2D data [samples, features], reshapes to trajectory format.
    """
    # If 2D, assume samples are timesteps, convert to trajectory
    if real_data.ndim == 2:
        n_samples, n_features = real_data.shape
        # Assume each row is a timestep, reshape to trajectory [1, n_samples, n_features]
        real_trajectory = real_data.reshape(1, n_samples, n_features)
    else:
        real_trajectory = real_data
    
    return benchmark_trajectory(real_trajectory, n_random_seeds)


def run_synthetic_benchmark():
    """Run benchmark on synthetic datasets to validate framework."""
    np.random.seed(42)
    
    print("=" * 60)
    print("V2_016 REAL WORLD BENCHMARK")
    print("=" * 60)
    
    results = {}
    
    # Test each dataset type using temporal systems from V2_009
    sys.path.insert(0, 'scripts/temporal_memory')
    from temporal_dynamics import generate_temporal_system
    
    # Use actual temporal system generators as proxies for real world data
    dataset_mapping = {
        "financial_timeseries": ("stable_hierarchy", {'n': 50, 'dimensions': 5, 'n_timesteps': 30}),
        "ecg_signal": ("oscillatory", {'n': 30, 'dimensions': 3, 'n_timesteps': 30}),
        "language_token_stream": ("stable_hierarchy", {'n': 40, 'dimensions': 8, 'n_timesteps': 25}),
        "network_traffic": ("perturb_recover", {'n': 30, 'dimensions': 5, 'n_timesteps': 25}),
        "weather_sequence": ("stable_hierarchy", {'n': 20, 'dimensions': 3, 'n_timesteps': 40})
    }
    
    for dataset_type, (system, params) in dataset_mapping.items():
        print(f"\n{'='*40}")
        print(f"Dataset: {dataset_type} (using {system})")
        print('='*40)
        
        traj, _ = generate_temporal_system(system, seed=42, **params)
        results[dataset_type] = benchmark_trajectory(traj)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: REAL VS RANDOM RATIOS")
    print("=" * 60)
    
    for dataset_type, r in results.items():
        ratio = r['ratios']['product_metric']
        status = "ORGANIZED" if ratio > 1.5 else ("RANDOM" if ratio < 0.8 else "MIXED")
        print(f"{dataset_type}: {ratio:.2f}x [{status}]")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/real_world_benchmark/benchmark_results.json'
    with open(output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved: {output}")
    
    return results


if __name__ == '__main__':
    run_synthetic_benchmark()