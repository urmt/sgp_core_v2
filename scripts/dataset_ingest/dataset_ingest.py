"""
SGP-CORE V2 Real World Dataset Ingest Protocol

Standardize ingestion and preprocessing of real datasets
before evaluation by V2_015 pipeline.
"""

import numpy as np
import json
import os
from typing import Dict, Optional, List
from pathlib import Path


SUPPORTED_FORMATS = [".csv", ".txt", ".npy", ".json"]


def normalize_sequence(data: np.ndarray) -> np.ndarray:
    """Normalize sequence to zero mean, unit variance."""
    data = np.array(data, dtype=float)
    
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0) + 1e-9
    
    normalized = (data - mean) / std
    
    return normalized


def min_max_normalize(data: np.ndarray) -> np.ndarray:
    """Normalize to [0, 1] range."""
    data = np.array(data, dtype=float)
    
    min_val = np.min(data, axis=0)
    max_val = np.max(data, axis=0)
    
    range_val = max_val - min_val + 1e-9
    
    normalized = (data - min_val) / range_val
    
    return normalized


def sliding_windows(sequence: np.ndarray, window_size: int = 50, 
                    stride: int = 10) -> np.ndarray:
    """Create sliding windows from sequence."""
    windows = []
    
    for i in range(0, len(sequence) - window_size, stride):
        windows.append(sequence[i:i + window_size])
    
    if not windows:
        # If sequence too short, return as single window
        return sequence.reshape(1, -1, *sequence.shape[1:])
    
    return np.array(windows)


def validate_dataset(sequence: np.ndarray) -> Dict:
    """Validate dataset meets requirements."""
    checks = {
        "nan_free": not np.isnan(sequence).any(),
        "finite": np.isfinite(sequence).all(),
        "sufficient_length": len(sequence) >= 100,
        "multivariate": len(sequence.shape) > 1 or sequence.shape[0] > 1,
        "positive_values": (sequence >= 0).all() if sequence.ndim == 1 else True
    }
    
    checks["valid"] = all(checks.values())
    
    return checks


def to_trajectory_format(data: np.ndarray, target_format: str = "[timesteps, nodes, dimensions]") -> np.ndarray:
    """
    Convert data to trajectory format expected by temporal metrics.
    Format: [timesteps, n_nodes, dimensions]
    """
    if data.ndim == 3:
        # Already in trajectory format
        return data
    
    if data.ndim == 2:
        # [samples, features] - treat as [timesteps, 1, features]
        n_timesteps, n_features = data.shape
        trajectory = data.reshape(n_timesteps, 1, n_features)
        return trajectory
    
    if data.ndim == 1:
        # [samples] - treat as [timesteps, 1, 1]
        n_timesteps = len(data)
        trajectory = data.reshape(n_timesteps, 1, 1)
        return trajectory
    
    raise ValueError(f"Cannot convert {data.ndim}D data to trajectory format")


def load_raw_dataset(filepath: str) -> Optional[np.ndarray]:
    """Load dataset from file."""
    ext = Path(filepath).suffix.lower()
    
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {ext}")
    
    try:
        if ext == ".csv":
            # Try loading with numpy
            try:
                data = np.loadtxt(filepath, delimiter=',')
            except:
                # Try with genfromtxt for inconsistent data
                data = np.genfromtxt(filepath, delimiter=',')
        elif ext == ".txt":
            data = np.loadtxt(filepath)
        elif ext == ".npy":
            data = np.load(filepath)
        elif ext == ".json":
            with open(filepath, 'r') as f:
                data = json.load(f)
            data = np.array(data)
        
        return data
    
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def preprocess_real_dataset(filepath: str, normalize: bool = True,
                             window_size: int = 50, stride: int = 10,
                             to_trajectory: bool = True) -> Dict:
    """
    Complete preprocessing pipeline for real dataset.
    
    Args:
        filepath: Path to dataset file
        normalize: Whether to normalize data
        window_size: Size of sliding windows
        stride: Stride between windows
        to_trajectory: Convert to trajectory format
    
    Returns:
        Dictionary with processed data and validation
    """
    print(f"\n=== PREPROCESSING: {filepath} ===")
    
    # Load raw data
    raw_data = load_raw_dataset(filepath)
    if raw_data is None:
        return {'error': 'Failed to load data'}
    
    print(f"Raw shape: {raw_data.shape}")
    
    # Normalize
    if normalize:
        normalized = normalize_sequence(raw_data)
        print(f"Normalized shape: {normalized.shape}")
    else:
        normalized = raw_data
    
    # Validate
    validation = validate_dataset(normalized)
    print(f"Validation: {validation}")
    
    if not validation["valid"]:
        return {
            'error': 'Dataset failed validation',
            'validation': validation,
            'raw_shape': raw_data.shape
        }
    
    # Create sliding windows
    windows = sliding_windows(normalized, window_size, stride)
    print(f"Windows shape: {windows.shape}")
    
    # Convert to trajectory format
    if to_trajectory:
        trajectory = to_trajectory_format(windows)
        print(f"Trajectory shape: {trajectory.shape}")
    else:
        trajectory = windows
    
    # Summary stats
    stats = {
        'raw_shape': list(raw_data.shape),
        'normalized_shape': list(normalized.shape),
        'windows_shape': list(windows.shape),
        'trajectory_shape': list(trajectory.shape),
        'n_timesteps': trajectory.shape[0] if trajectory.ndim >= 1 else 0,
        'n_nodes': trajectory.shape[1] if trajectory.ndim >= 2 else 0,
        'n_dimensions': trajectory.shape[2] if trajectory.ndim >= 3 else 0
    }
    
    return {
        'raw_data': raw_data,
        'normalized_data': normalized,
        'windows': windows,
        'trajectory': trajectory,
        'validation': validation,
        'stats': stats,
        'filepath': filepath
    }


def run_ingest_demo():
    """Demonstrate ingest on synthetic data."""
    np.random.seed(42)
    
    print("=" * 60)
    print("V2_016 DATASET INGEST DEMO")
    print("=" * 60)
    
    # Create synthetic dataset
    n_samples = 200
    n_features = 10
    
    # Simulated real data: organized structure
    centers = np.random.randn(5, n_features)
    data = []
    current_center = 0
    
    for i in range(n_samples):
        # Occasionally switch centers (temporal structure)
        if np.random.random() < 0.15:
            current_center = np.random.choice(5)
        data.append(centers[current_center] + np.random.randn(n_features) * 0.3)
    
    raw_data = np.array(data)
    
    print(f"\n=== SYNTHETIC DATASET ===")
    print(f"Shape: {raw_data.shape}")
    
    # Preprocess
    result = {
        'raw_data': raw_data,
        'normalized_data': normalize_sequence(raw_data),
        'validation': validate_dataset(normalize_sequence(raw_data)),
        'stats': {
            'raw_shape': list(raw_data.shape),
            'normalized_shape': list(normalize_sequence(raw_data).shape),
            'n_timesteps': raw_data.shape[0],
            'n_nodes': 1,
            'n_dimensions': raw_data.shape[1]
        }
    }
    
    # Convert to trajectory
    trajectory = to_trajectory_format(raw_data)
    print(f"Trajectory shape: {trajectory.shape}")
    
    # Create windows
    windows = sliding_windows(normalize_sequence(raw_data), window_size=30, stride=15)
    print(f"Windows shape: {windows.shape}")
    
    print("\n=== VALIDATION ===")
    for key, value in result['validation'].items():
        print(f"  {key}: {value}")
    
    print("\n=== STATUS ===")
    print("Dataset ingest framework ready!")
    
    return result


if __name__ == '__main__':
    run_ingest_demo()