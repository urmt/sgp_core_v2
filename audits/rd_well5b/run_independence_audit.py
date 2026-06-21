#!/usr/bin/env python3
"""
RD-WELL.5B.1 — Independence Audit: Compute corr(C, S_i)

Question: Are the stabilization metrics independent of C?

If |r| > 0.8, the stabilization metric may be measuring
nearly the same thing as C.
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


def compute_s1_spectral_entropy_windowed(A_data):
    """Compute S1 for each possible window position."""
    A_mean = A_data.mean(axis=(1, 2))
    window = 50
    N = len(A_mean) - window + 1
    values = []
    for start in range(N):
        window_data = A_mean[start:start+window]
        fft_vals = np.fft.rfft(window_data)
        power = np.abs(fft_vals)**2
        power_prob = power / (power.sum() + 1e-10)
        H = -np.sum(power_prob * np.log(power_prob + 1e-10))
        values.append(H)
    return np.array(values)


def compute_s2_temporal_derivative_windowed(A_data):
    """Compute S2 for each window position."""
    A_mean = A_data.mean(axis=(1, 2))
    N = len(A_mean)
    values = []
    for i in range(N):
        if i == 0:
            values.append(abs(A_mean[1] - A_mean[0]) if N > 1 else 0)
        elif i == N - 1:
            values.append(abs(A_mean[-1] - A_mean[-2]))
        else:
            values.append(abs(A_mean[i] - A_mean[i-1]))
    return np.array(values)


def compute_s3_morphology_windowed(A_data, threshold=0.5):
    """Compute S3 for each window position."""
    binary = (A_data > threshold).astype(int)
    pixel_counts = binary.sum(axis=(1, 2))
    values = []
    for i in range(len(pixel_counts)):
        if i == 0:
            values.append(0)
        else:
            values.append(abs(pixel_counts[i] - pixel_counts[i-1]))
    return np.array(values)


def compute_C_over_windows(A_data, B_data):
    """Compute C at each time step using cumulative window."""
    A_mean = A_data.mean(axis=(1, 2))
    B_mean = B_data.mean(axis=(1, 2))

    C_values = []
    for t in range(10, len(A_mean) + 1):  # need at least 10 points for C
        X = np.stack([A_mean[:t], B_mean[:t]], axis=0)
        try:
            C_val = compute_C(X, estimator='gaussian')
            C_values.append(C_val)
        except:
            C_values.append(np.nan)
    return np.array(C_values)


def main():
    print("RD-WELL.5B.1 — Independence Audit")
    print("=" * 60)
    print("Computing correlation between C and each stabilization metric")
    print("=" * 60)

    # Load data
    fs, path = fsspec.core.url_to_fs(BUBBLES_URL)

    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']

        # Use first trajectory, first 200 steps
        A_data = field_A[0, :200]
        B_data = field_B[0, :200]

    print(f"\nLoaded data: {A_data.shape}")

    # ============================================================
    # Compute C over time
    # ============================================================
    print("\nComputing C over time...")
    C_values = compute_C_over_windows(A_data, B_data)
    print(f"C series shape: {C_values.shape}")
    print(f"C range: [{np.nanmin(C_values):.4f}, {np.nanmax(C_values):.4f}]")

    # ============================================================
    # Compute S1 and align
    # ============================================================
    print("\nComputing S1 (spectral entropy)...")
    s1_values = compute_s1_spectral_entropy_windowed(A_data)
    # Align lengths: C starts at t=10, S1 window=50
    min_len = min(len(C_values), len(s1_values[40:]))  # offset S1
    C_trim = C_values[:min_len]
    s1_trim = s1_values[40:40+min_len]
    
    # Remove any NaN values
    valid = ~np.isnan(C_trim) & ~np.isnan(s1_trim)
    C_valid = C_trim[valid]
    s1_valid = s1_trim[valid]

    if len(C_valid) > 10:
        corr_s1 = np.corrcoef(C_valid, s1_valid)[0, 1]
    else:
        corr_s1 = np.nan

    print(f"S1 correlation with C: r = {corr_s1:.4f}")

    # ============================================================
    # Compute S2 and align
    # ============================================================
    print("\nComputing S2 (temporal derivative)...")
    s2_values = compute_s2_temporal_derivative_windowed(A_data)
    min_len = min(len(C_values), len(s2_values[9:]))
    C_trim2 = C_values[:min_len]
    s2_trim = s2_values[9:9+min_len]

    valid = ~np.isnan(C_trim2) & ~np.isnan(s2_trim)
    C_valid2 = C_trim2[valid]
    s2_valid = s2_trim[valid]

    if len(C_valid2) > 10:
        corr_s2 = np.corrcoef(C_valid2, s2_valid)[0, 1]
    else:
        corr_s2 = np.nan

    print(f"S2 correlation with C: r = {corr_s2:.4f}")

    # ============================================================
    # Compute S3 and align
    # ============================================================
    print("\nComputing S3 (morphology persistence)...")
    s3_values = compute_s3_morphology_windowed(A_data)
    min_len = min(len(C_values), len(s3_values[9:]))
    C_trim3 = C_values[:min_len]
    s3_trim = s3_values[9:9+min_len]

    valid = ~np.isnan(C_trim3) & ~np.isnan(s3_trim)
    C_valid3 = C_trim3[valid]
    s3_valid = s3_trim[valid]

    if len(C_valid3) > 10:
        corr_s3 = np.corrcoef(C_valid3, s3_valid)[0, 1]
    else:
        corr_s3 = np.nan

    print(f"S3 correlation with C: r = {corr_s3:.4f}")

    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "=" * 60)
    print("INDEPENDENCE AUDIT SUMMARY")
    print("=" * 60)

    results = {
        'S1_spectral_entropy': {'correlation': float(corr_s1), 'independent': bool(abs(corr_s1) < 0.8) if not np.isnan(corr_s1) else None},
        'S2_temporal_derivative': {'correlation': float(corr_s2), 'independent': bool(abs(corr_s2) < 0.8) if not np.isnan(corr_s2) else None},
        'S3_morphology_persistence': {'correlation': float(corr_s3), 'independent': bool(abs(corr_s3) < 0.8) if not np.isnan(corr_s3) else None},
    }

    for metric, data in results.items():
        status = "INDEPENDENT" if data['independent'] else "COUPLED" if data['independent'] is not None else "UNKNOWN"
        print(f"\n{metric}:")
        print(f"  r = {data['correlation']:.4f}")
        print(f"  status = {status}")

    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well5b"
    os.makedirs(output_dir, exist_ok=True)

    output = {
        'description': 'Independence audit: correlation between C and stabilization metrics',
        'results': results,
    }

    output_file = os.path.join(output_dir, "independence_audit.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
