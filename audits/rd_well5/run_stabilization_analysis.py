#!/usr/bin/env python3
"""
RD-WELL.5 — Define Stabilization Operationally

Research Director suggested candidates:
- frame-to-frame variance plateau
- spectral entropy plateau
- persistent morphology score
- low temporal derivative norm

This script tests these candidates on Gray-Scott patterns.
"""

import fsspec
import h5py
import numpy as np
import json
import os
import sys
from scipy import signal
from scipy.stats import entropy

# URLs for Gray-Scott files
GRAY_SCOTT_URLS = {
    'bubbles': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_bubbles_F_0.098_k_0.057.hdf5',
    'maze': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_maze_F_0.029_k_0.057.hdf5',
    'spirals': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_spirals_F_0.018_k_0.051.hdf5',
}

def compute_frame_to_frame_variance(A_data, B_data):
    """Compute frame-to-frame variance over time."""
    # Compute mean across spatial dimensions
    A_mean = A_data.mean(axis=(1, 2))  # (time,)
    B_mean = B_data.mean(axis=(1, 2))  # (time,)
    
    # Compute frame-to-frame differences
    A_diff = np.abs(np.diff(A_mean))
    B_diff = np.abs(np.diff(B_mean))
    
    return A_diff, B_diff

def compute_spectral_entropy(A_data, B_data):
    """Compute spectral entropy over time."""
    # Compute mean across spatial dimensions
    A_mean = A_data.mean(axis=(1, 2))  # (time,)
    B_mean = B_data.mean(axis=(1, 2))  # (time,)
    
    # Compute power spectrum
    A_spectrum = np.abs(np.fft.rfft(A_mean))**2
    B_spectrum = np.abs(np.fft.rfft(B_mean))**2
    
    # Normalize to probability distribution
    A_prob = A_spectrum / A_spectrum.sum()
    B_prob = B_spectrum / B_spectrum.sum()
    
    # Compute entropy
    A_entropy = entropy(A_prob)
    B_entropy = entropy(B_prob)
    
    return A_entropy, B_entropy

def compute_temporal_derivative_norm(A_data, B_data):
    """Compute temporal derivative norm over time."""
    # Compute mean across spatial dimensions
    A_mean = A_data.mean(axis=(1, 2))  # (time,)
    B_mean = B_data.mean(axis=(1, 2))  # (time,)
    
    # Compute temporal derivatives
    A_derivative = np.gradient(A_mean)
    B_derivative = np.gradient(B_mean)
    
    # Compute norm
    A_norm = np.abs(A_derivative)
    B_norm = np.abs(B_derivative)
    
    return A_norm, B_norm

def find_stabilization_time(metric_values, threshold=0.1):
    """Find stabilization time using sliding window."""
    # Use sliding window to detect plateau
    window_size = 20
    
    if len(metric_values) < window_size:
        return None
    
    # Compute rolling mean
    rolling_mean = np.convolve(metric_values, np.ones(window_size)/window_size, mode='valid')
    
    # Find where relative change drops below threshold
    for i in range(1, len(rolling_mean)):
        relative_change = abs(rolling_mean[i] - rolling_mean[i-1]) / (abs(rolling_mean[i-1]) + 1e-10)
        if relative_change < threshold:
            return i + window_size // 2
    
    return len(metric_values)

def analyze_pattern(pattern_name):
    """Analyze stabilization for a pattern."""
    url = GRAY_SCOTT_URLS[pattern_name]
    print(f"\nAnalyzing {pattern_name}...")
    
    fs, path = fsspec.core.url_to_fs(url)
    
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        # Use first trajectory
        A_data = field_A[0]  # (1001, 128, 128)
        B_data = field_B[0]  # (1001, 128, 128)
        
        # Compute metrics
        A_diff, B_diff = compute_frame_to_frame_variance(A_data, B_data)
        A_entropy, B_entropy = compute_spectral_entropy(A_data, B_data)
        A_norm, B_norm = compute_temporal_derivative_norm(A_data, B_data)
        
        # Find stabilization times
        t_stab_A_diff = find_stabilization_time(A_diff)
        t_stab_B_diff = find_stabilization_time(B_diff)
        t_stab_A_norm = find_stabilization_time(A_norm)
        t_stab_B_norm = find_stabilization_time(B_norm)
        
        results = {
            'pattern': pattern_name,
            'stabilization_times': {
                'frame_to_frame_variance_A': t_stab_A_diff,
                'frame_to_frame_variance_B': t_stab_B_diff,
                'temporal_derivative_norm_A': t_stab_A_norm,
                'temporal_derivative_norm_B': t_stab_B_norm,
            },
            'spectral_entropy': {
                'A': A_entropy,
                'B': B_entropy,
            }
        }
        
        print(f"  Frame-to-frame variance A: stabilization at t={t_stab_A_diff}")
        print(f"  Frame-to-frame variance B: stabilization at t={t_stab_B_diff}")
        print(f"  Temporal derivative norm A: stabilization at t={t_stab_A_norm}")
        print(f"  Temporal derivative norm B: stabilization at t={t_stab_B_norm}")
        print(f"  Spectral entropy A: {A_entropy:.4f}")
        print(f"  Spectral entropy B: {B_entropy:.4f}")
        
        return results

def main():
    print("RD-WELL.5 — Define Stabilization Operationally")
    print("=" * 60)
    print("Testing candidate stabilization metrics:")
    print("1. Frame-to-frame variance plateau")
    print("2. Spectral entropy plateau")
    print("3. Low temporal derivative norm")
    print("=" * 60)
    
    all_results = {}
    
    for pattern_name in ['bubbles', 'maze', 'spirals']:
        results = analyze_pattern(pattern_name)
        all_results[pattern_name] = results
    
    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well5"
    os.makedirs(output_dir, exist_ok=True)
    
    output = {
        'description': 'Stabilization time analysis for Gray-Scott patterns',
        'results': all_results
    }
    
    output_file = os.path.join(output_dir, "stabilization_analysis.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for pattern_name, results in all_results.items():
        print(f"\n{pattern_name}:")
        for metric, value in results['stabilization_times'].items():
            print(f"  {metric}: {value}")

if __name__ == "__main__":
    main()
