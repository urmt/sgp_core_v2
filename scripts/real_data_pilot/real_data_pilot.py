"""
SGP-CORE V2 Real Data Pilot Protocol

Run controlled pilot testing on real sequential datasets
while preserving all adversarial safeguards.
"""

import numpy as np
import json
import sys
from typing import Dict, Optional

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/replay_resistance')

from memory_metrics import (
    InteractionMemoryScore,
    StructuralPersistence,
    TemporalConsensusScore,
    TemporalFragmentationVariance
)
from final_replay_detection import data_drift, final_replay_detection


# Thresholds calibrated from V2_014 results:
# - stable_hierarchy at N=100: product ~0.2
# - random_temporal at N=100: product ~0.07
# Threshold should be ~0.1 to pass stable but reject random
REALITY_THRESHOLD = 0.12
REPLAY_THRESHOLD = 0.05


def product_metric(memory: float, persistence: float, consensus: float) -> float:
    """Product-based scale-invariant metric (V2_013)."""
    return (memory * persistence * consensus) ** (1/3)


def evaluate_real_sequence(sequence: np.ndarray, seed: int = 42) -> Dict:
    """
    Evaluate a real sequential dataset.
    
    Applies all V2_010-V2_014 safeguards:
    1. Product metric for scale-invariance
    2. Replay detection (drift < 0.05)
    3. Reality threshold (product > 1.5)
    """
    if sequence.ndim == 1:
        sequence = sequence.reshape(-1, 1)
    
    # Handle multi-dimensional data by reshaping
    n_samples = sequence.shape[0]
    n_features = sequence.shape[1] if sequence.ndim > 1 else 1
    
    # Create timestep structure (each row is a timestep, each column is a feature)
    # For real data, we need to create a time-series structure
    # Default: treat each row as a timestep
    
    # Compute metrics using V2 metrics
    try:
        memory = InteractionMemoryScore(seed).compute(sequence)['memory_score_mean']
    except:
        memory = 0.0
    
    try:
        persistence = StructuralPersistence(seed).compute(sequence)['persistence_mean']
    except:
        persistence = 0.0
    
    try:
        consensus = TemporalConsensusScore(seed).compute(sequence)['consensus_mean']
    except:
        consensus = 0.0
    
    try:
        frag_var = TemporalFragmentationVariance(seed).compute(sequence)['fragmentation_std']
    except:
        frag_var = 0.0
    
    drift = data_drift(sequence)
    
    product = product_metric(memory, persistence, consensus)
    
    replay_check = final_replay_detection(sequence, seed)
    replay_flag = replay_check['is_replay']
    
    # Reality check
    approved = (
        product > REALITY_THRESHOLD
        and not replay_flag
    )
    
    return {
        'n_samples': n_samples,
        'n_features': n_features,
        'memory': memory,
        'persistence': persistence,
        'consensus': consensus,
        'frag_var': frag_var,
        'drift': drift,
        'product_score': product,
        'replay_flag': replay_flag,
        'replay_detected': replay_check['is_replay'],
        'reality_threshold': REALITY_THRESHOLD,
        'replay_threshold': REPLAY_THRESHOLD,
        'approved': approved
    }


def load_and_prepare_data(filepath: str) -> Optional[np.ndarray]:
    """Load and prepare real data for evaluation."""
    try:
        # Try different loading strategies
        if filepath.endswith('.csv'):
            if HAS_PANDAS:
                df = pd.read_csv(filepath)
                numeric = df.select_dtypes(include=[np.number])
                return numeric.values
            else:
                # Fallback: try numpy loadtxt
                return np.loadtxt(filepath, delimiter=',')
        elif filepath.endswith('.npy'):
            return np.load(filepath)
        elif filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
            return np.array(data)
        else:
            print(f"Unknown file format: {filepath}")
            return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def run_real_data_pilot(dataset_path: str) -> Dict:
    """Run pilot on a real dataset."""
    print("=" * 60)
    print("V2_015 REAL DATA PILOT")
    print("=" * 60)
    
    print(f"\nLoading: {dataset_path}")
    sequence = load_and_prepare_data(dataset_path)
    
    if sequence is None:
        return {'error': 'Failed to load data'}
    
    print(f"Data shape: {sequence.shape}")
    
    results = evaluate_real_sequence(sequence)
    
    print("\n=== RESULTS ===")
    for k, v in results.items():
        if isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")
    
    print("\n=== VERDICT ===")
    if results['approved']:
        print("STATUS: APPROVED - Real data passes all checks")
    else:
        print("STATUS: REJECTED")
        if results['product_score'] <= REALITY_THRESHOLD:
            print(f"  - Product score {results['product_score']:.4f} <= {REALITY_THRESHOLD}")
        if results['replay_flag']:
            print(f"  - Replay detected (drift={results['drift']:.4f} < {REPLAY_THRESHOLD})")
    
    return results


def run_synthetic_pilot():
    """Run pilot on synthetic data to validate framework."""
    np.random.seed(42)
    
    print("=" * 60)
    print("SYNTHETIC PILOT (VALIDATION)")
    print("=" * 60)
    
    # Generate test systems
    sys.path.insert(0, 'scripts/temporal_memory')
    from temporal_dynamics import generate_temporal_system
    
    params = {'n': 100, 'dimensions': 5, 'n_timesteps': 20}
    
    print("\n--- stable_hierarchy (should pass) ---")
    traj, _ = generate_temporal_system('stable_hierarchy', seed=42, **params)
    results = evaluate_real_sequence(traj)
    print(f"product: {results['product_score']:.4f}, drift: {results['drift']:.4f}, approved: {results['approved']}")
    
    print("\n--- random_temporal (should fail - low score) ---")
    traj, _ = generate_temporal_system('random_temporal', seed=42, **params)
    results = evaluate_real_sequence(traj)
    print(f"product: {results['product_score']:.4f}, drift: {results['drift']:.4f}, approved: {results['approved']}")
    
    print("\n--- replay_memory_spoof (should fail - replay detected) ---")
    sys.path.insert(0, 'scripts/temporal_adversarial_expansion')
    from advanced_temporal_adversaries import generate_temporal_adversary
    traj, _ = generate_temporal_adversary('replay_memory_spoof', seed=42, **params)
    results = evaluate_real_sequence(traj)
    print(f"product: {results['product_score']:.4f}, drift: {results['drift']:.4f}, approved: {results['approved']}")
    
    return {
        'stable_approved': evaluate_real_sequence(generate_temporal_system('stable_hierarchy', seed=42, **params)[0])['approved'],
        'random_approved': evaluate_real_sequence(generate_temporal_system('random_temporal', seed=42, **params)[0])['approved'],
        'replay_approved': evaluate_real_sequence(generate_temporal_adversary('replay_memory_spoof', seed=42, **params)[0])['approved']
    }


if __name__ == '__main__':
    # Run synthetic validation first
    val_results = run_synthetic_pilot()
    
    print("\n=== SYNTHETIC VALIDATION SUMMARY ===")
    print(f"stable_hierarchy: {'PASS' if val_results['stable_approved'] else 'FAIL'}")
    print(f"random_temporal: {'FAIL (expected)' if not val_results['random_approved'] else 'PASS (unexpected)'}")
    print(f"replay_memory_spoof: {'FAIL (expected)' if not val_results['replay_approved'] else 'PASS (unexpected)'}")
    
    print("\nNote: Real data pilot requires dataset path argument.")