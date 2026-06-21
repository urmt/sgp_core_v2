#!/usr/bin/env python3
"""
RD-WELL.5C — Cross-Pattern Coupling Audit

Repeat the same analysis (C vs S_i) on multiple Gray-Scott patterns.

Question: Does strong coupling survive independent worlds?

This directly attacks SR-30.
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

# URLs for Gray-Scott files
GRAY_SCOTT_URLS = {
    'bubbles': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_bubbles_F_0.098_k_0.057.hdf5',
    'maze': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_maze_F_0.029_k_0.057.hdf5',
    'spirals': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_spirals_F_0.018_k_0.051.hdf5',
    'spots': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_spots_F_0.022_k_0.063.hdf5',
    'worms': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_worms_F_0.040_k_0.065.hdf5',
    'gliders': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_gliders_F_0.028_k_0.062.hdf5',
}


def compute_s1_spectral_entropy(A_data):
    """S1: Spectral entropy plateau."""
    A_mean = A_data.mean(axis=(1, 2))
    window = 50
    values = []
    for start in range(len(A_mean) - window + 1):
        window_data = A_mean[start:start+window]
        fft_vals = np.fft.rfft(window_data)
        power = np.abs(fft_vals)**2
        power_prob = power / (power.sum() + 1e-10)
        H = -np.sum(power_prob * np.log(power_prob + 1e-10))
        values.append(H)
    return np.array(values)


def compute_s2_temporal_derivative(A_data):
    """S2: Temporal derivative norm."""
    A_mean = A_data.mean(axis=(1, 2))
    return np.abs(np.diff(A_mean))


def compute_s3_morphology_persistence(A_data, threshold=0.5):
    """S3: Morphology persistence."""
    binary = (A_data > threshold).astype(int)
    pixel_counts = binary.sum(axis=(1, 2))
    return np.abs(np.diff(pixel_counts))


def compute_C_over_time(A_data, B_data):
    """Compute C at each time step."""
    A_mean = A_data.mean(axis=(1, 2))
    B_mean = B_data.mean(axis=(1, 2))
    C_values = []
    for t in range(10, len(A_mean) + 1):
        X = np.stack([A_mean[:t], B_mean[:t]], axis=0)
        try:
            C_val = compute_C(X, estimator='gaussian')
            C_values.append(C_val)
        except:
            C_values.append(np.nan)
    return np.array(C_values)


def analyze_pattern(pattern_name, url):
    """Analyze one pattern: compute C, S1, S2, S3, and correlations."""
    print(f"\nAnalyzing {pattern_name}...")

    fs, path = fsspec.core.url_to_fs(url)

    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']

        # Use first trajectory, first 200 steps
        A_data = field_A[0, :200]
        B_data = field_B[0, :200]

    # Compute C
    C_values = compute_C_over_time(A_data, B_data)

    # Compute stabilization metrics
    s1_values = compute_s1_spectral_entropy(A_data)
    s2_values = compute_s2_temporal_derivative(A_data)
    s3_values = compute_s3_morphology_persistence(A_data)

    # Align lengths for correlation
    # C starts at t=10, S1 window=50, S2/S3 start at t=1
    # We'll use the common overlapping range

    results = {}

    # For each metric, compute correlation with C
    for metric_name, metric_values in [('S1', s1_values), ('S2', s2_values), ('S3', s3_values)]:
        # Determine offset
        if metric_name == 'S1':
            # S1 has window=50, so starts at t=50
            offset = 40  # C[0] corresponds to t=10, S1[0] corresponds to t=50
        else:
            # S2 and S3 start at t=1, C starts at t=10
            offset = 9

        # Trim to common length
        metric_len = len(metric_values) - offset
        c_len = len(C_values)
        min_len = min(c_len, metric_len)

        if min_len > 10:
            C_trim = C_values[:min_len]
            metric_trim = metric_values[offset:offset+min_len]

            # Remove NaN
            valid = ~np.isnan(C_trim) & ~np.isnan(metric_trim)
            C_valid = C_trim[valid]
            metric_valid = metric_trim[valid]

            if len(C_valid) > 10:
                corr = np.corrcoef(C_valid, metric_valid)[0, 1]
            else:
                corr = np.nan
        else:
            corr = np.nan

        results[metric_name] = {
            'correlation': float(corr) if not np.isnan(corr) else None,
            'abs_correlation': float(abs(corr)) if not np.isnan(corr) else None,
            'independent': bool(abs(corr) < 0.8) if not np.isnan(corr) else None,
        }

        print(f"  {metric_name} vs C: r = {corr:.4f}")

    return results


def main():
    print("RD-WELL.5C — Cross-Pattern Coupling Audit")
    print("=" * 60)
    print("Question: Does strong coupling survive independent worlds?")
    print("=" * 60)

    all_results = {}

    for pattern_name, url in GRAY_SCOTT_URLS.items():
        try:
            results = analyze_pattern(pattern_name, url)
            all_results[pattern_name] = results
        except Exception as e:
            print(f"\n{pattern_name}: ERROR - {e}")
            all_results[pattern_name] = {'error': str(e)}

    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well5c"
    os.makedirs(output_dir, exist_ok=True)

    output = {
        'description': 'Cross-pattern coupling audit',
        'results': all_results,
    }

    output_file = os.path.join(output_dir, "cross_pattern_coupling.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: Does strong coupling survive independent worlds?")
    print("=" * 60)

    patterns_tested = [p for p in all_results.keys() if 'error' not in all_results[p]]
    print(f"\nPatterns tested: {len(patterns_tested)}")

    for metric in ['S1', 'S2', 'S3']:
        strong_coupling_count = sum(
            1 for p in patterns_tested
            if all_results[p][metric]['abs_correlation'] is not None
            and all_results[p][metric]['abs_correlation'] > 0.8
        )
        print(f"\n{metric}:")
        print(f"  Strong coupling (|r| > 0.8): {strong_coupling_count}/{len(patterns_tested)} patterns")

        for p in patterns_tested:
            corr = all_results[p][metric]['correlation']
            if corr is not None:
                print(f"    {p}: r = {corr:.4f}")

    print("\n" + "=" * 60)
    print("Status: Measurement only. No conclusions drawn.")
    print("=" * 60)


if __name__ == "__main__":
    main()
