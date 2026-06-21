#!/usr/bin/env python3
"""
RD-WELL.5.1 — Define Stabilization Operationally (Simplified)

Testing candidate stabilization metrics on one pattern.
"""

import fsspec
import h5py
import numpy as np
import json
import os
import sys

# URL for bubbles
BUBBLES_URL = 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_bubbles_F_0.098_k_0.057.hdf5'

def compute_frame_to_frame_variance(A_data, B_data):
    """Compute frame-to-frame variance over time."""
    # Compute mean across spatial dimensions
    A_mean = A_data.mean(axis=(1, 2))  # (time,)
    B_mean = B_data.mean(axis=(1, 2))  # (time,)
    
    # Compute frame-to-frame differences
    A_diff = np.abs(np.diff(A_mean))
    B_diff = np.abs(np.diff(B_mean))
    
    return A_diff, B_diff

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

def analyze_pattern():
    """Analyze stabilization for bubbles pattern."""
    print(f"\nAnalyzing bubbles...")
    
    fs, path = fsspec.core.url_to_fs(BUBBLES_URL)
    
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        # Use first trajectory
        A_data = field_A[0]  # (1001, 128, 128)
        B_data = field_B[0]  # (1001, 128, 128)
        
        # Compute frame-to-frame variance
        A_diff, B_diff = compute_frame_to_frame_variance(A_data, B_data)
        
        # Find stabilization times
        t_stab_A_diff = find_stabilization_time(A_diff)
        t_stab_B_diff = find_stabilization_time(B_diff)
        
        results = {
            'pattern': 'bubbles',
            'stabilization_times': {
                'frame_to_frame_variance_A': t_stab_A_diff,
                'frame_to_frame_variance_B': t_stab_B_diff,
            }
        }
        
        print(f"  Frame-to-frame variance A: stabilization at t={t_stab_A_diff}")
        print(f"  Frame-to-frame variance B: stabilization at t={t_stab_B_diff}")
        
        return results

def main():
    print("RD-WELL.5.1 — Define Stabilization Operationally (Simplified)")
    print("=" * 60)
    
    results = analyze_pattern()
    
    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well5"
    os.makedirs(output_dir, exist_ok=True)
    
    output = {
        'description': 'Stabilization time analysis for bubbles',
        'results': results
    }
    
    output_file = os.path.join(output_dir, "stabilization_analysis_bubbles.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
