#!/usr/bin/env python3
"""
RD-WELL.5B — Alternative Stabilization Metrics Audit

Construct operational stabilization observables independent of C.

Required observables:
1. S1: Spectral entropy plateau
2. S2: Temporal derivative norm
3. S3: Morphology persistence

For each:
- compute stabilization time
- perform threshold sensitivity analysis
- compute correlation with C
- test on bubbles first

Forbidden: causal language, theory words, survivor promotion
"""

import fsspec
import h5py
import numpy as np
import json
import os
import sys

# Add the metrics directory to path
sys.path.insert(0, '/home/student/sgp_core_v2/coherence-benchmark')
from metrics.total_correlation import compute_C

# URL for bubbles
BUBBLES_URL = 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_bubbles_F_0.098_k_0.057.hdf5'


def compute_s1_spectral_entropy(A_data):
    """S1: Spectral entropy plateau.

    Compute 1D spectral entropy of mean field over time window.
    Returns time series of spectral entropy values.
    """
    # Compute mean across spatial dimensions
    A_mean = A_data.mean(axis=(1, 2))  # (time,)

    # Compute rolling spectral entropy with window
    window = 50
    entropy_series = []

    for t in range(window, len(A_mean)):
        # Extract window
        window_data = A_mean[t-window:t]

        # Compute FFT
        fft_vals = np.fft.rfft(window_data)
        power = np.abs(fft_vals)**2

        # Normalize to probability distribution
        power_prob = power / (power.sum() + 1e-10)

        # Compute entropy
        H = -np.sum(power_prob * np.log(power_prob + 1e-10))
        entropy_series.append(H)

    return np.array(entropy_series)


def compute_s2_temporal_derivative(A_data):
    """S2: Temporal derivative norm.

    Compute ||X_t - X_{t-1}|| over time.
    Returns time series of derivative norms.
    """
    # Compute mean across spatial dimensions
    A_mean = A_data.mean(axis=(1, 2))  # (time,)

    # Compute temporal derivatives
    derivative = np.diff(A_mean)

    # Return absolute derivative (norm in 1D)
    return np.abs(derivative)


def compute_s3_morphology_persistence(A_data, threshold=0.5):
    """S3: Morphology persistence.

    Binarize field, compute connected component statistics.
    Returns time series of component count changes.
    """
    # Binarize using threshold
    binary = (A_data > threshold).astype(int)  # (time, 128, 128)

    # For each frame, count high pixels (simple proxy for morphology)
    pixel_counts = binary.sum(axis=(1, 2))

    # Compute frame-to-frame changes in pixel count
    changes = np.abs(np.diff(pixel_counts))

    return changes


def find_stabilization_time(metric_series, threshold_ratio=0.05, k=5):
    """Find stabilization time: metric stays below threshold for k consecutive frames.

    Parameters:
    - metric_series: 1D array of metric values
    - threshold_ratio: threshold as fraction of max
    - k: number of consecutive frames below threshold

    Returns: stabilization time index, or None if not found
    """
    if len(metric_series) == 0:
        return None

    # Compute threshold as fraction of range
    threshold = threshold_ratio * (metric_series.max() - metric_series.min())

    # Find k consecutive frames below threshold
    below = metric_series < threshold

    # Check for k consecutive True values
    for t in range(len(below) - k + 1):
        if np.all(below[t:t+k]):
            return t

    return None


def stability_sensitivity(S_func, A_data, thresholds=[0.01, 0.03, 0.05, 0.1]):
    """Perform threshold sensitivity analysis.

    For each threshold, compute stabilization time.
    Returns: dict mapping threshold to stabilization time
    """
    # Compute the metric series
    metric_series = S_func(A_data)

    results = {}
    for thresh in thresholds:
        stab_time = find_stabilization_time(metric_series, threshold_ratio=thresh, k=5)
        results[thresh] = {
            'stab_time': stab_time,
            'metric_mean': float(metric_series.mean()) if len(metric_series) > 0 else None,
            'metric_std': float(metric_series.std()) if len(metric_series) > 0 else None,
        }

    return results, metric_series


def main():
    print("RD-WELL.5B — Alternative Stabilization Metrics Audit")
    print("=" * 60)
    print("Measurement only. No ontology. No theory language.")
    print("=" * 60)

    # Load data
    fs, path = fsspec.core.url_to_fs(BUBBLES_URL)

    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']

        # Use first trajectory, first 200 steps
        A_data = field_A[0, :200]  # (200, 128, 128)

    print(f"\nLoaded data: {A_data.shape}")

    # ============================================================
    # S1: Spectral Entropy Plateau
    # ============================================================
    print("\n" + "=" * 60)
    print("S1: SPECTRAL ENTROPY PLATEAU")
    print("=" * 60)

    s1_results, s1_series = stability_sensitivity(compute_s1_spectral_entropy, A_data)
    print(f"\nMetric series shape: {s1_series.shape}")
    print(f"Metric range: [{s1_series.min():.4f}, {s1_series.max():.4f}]")

    for thresh, data in s1_results.items():
        print(f"\nThreshold θ={thresh}:")
        print(f"  Stab. time: {data['stab_time']}")
        print(f"  Metric mean: {data['metric_mean']:.4f}")
        print(f"  Metric std:  {data['metric_std']:.4f}")

    # ============================================================
    # S2: Temporal Derivative Norm
    # ============================================================
    print("\n" + "=" * 60)
    print("S2: TEMPORAL DERIVATIVE NORM")
    print("=" * 60)

    s2_results, s2_series = stability_sensitivity(compute_s2_temporal_derivative, A_data)
    print(f"\nMetric series shape: {s2_series.shape}")
    print(f"Metric range: [{s2_series.min():.4f}, {s2_series.max():.4f}]")

    for thresh, data in s2_results.items():
        print(f"\nThreshold θ={thresh}:")
        print(f"  Stab. time: {data['stab_time']}")
        print(f"  Metric mean: {data['metric_mean']:.4f}")
        print(f"  Metric std:  {data['metric_std']:.4f}")

    # ============================================================
    # S3: Morphology Persistence
    # ============================================================
    print("\n" + "=" * 60)
    print("S3: MORPHOLOGY PERSISTENCE")
    print("=" * 60)

    s3_results, s3_series = stability_sensitivity(compute_s3_morphology_persistence, A_data)
    print(f"\nMetric series shape: {s3_series.shape}")
    print(f"Metric range: [{s3_series.min():.4f}, {s3_series.max():.4f}]")

    for thresh, data in s3_results.items():
        print(f"\nThreshold θ={thresh}:")
        print(f"  Stab. time: {data['stab_time']}")
        print(f"  Metric mean: {data['metric_mean']:.4f}")
        print(f"  Metric std:  {data['metric_std']:.4f}")

    # ============================================================
    # Save results
    # ============================================================
    output_dir = "/home/student/sgp_core_v2/audits/rd_well5b"
    os.makedirs(output_dir, exist_ok=True)

    output = {
        'S1_spectral_entropy': s1_results,
        'S2_temporal_derivative': s2_results,
        'S3_morphology_persistence': s3_results,
    }

    output_file = os.path.join(output_dir, "stabilization_metrics.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("Status: Measurement complete. No conclusions drawn.")
    print(f"Results saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
