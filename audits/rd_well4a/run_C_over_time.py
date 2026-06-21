#!/usr/bin/env python3
"""
RD-WELL.4A — Compute C Over Time

Ask: Does C increase before stabilization?
Or: Does stabilization occur without increased C?

This is an actual scientific question. No ontology required.
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
}

def compute_C_over_time(pattern_name, sample_idx=0, time_windows=[100, 200, 500, 1000]):
    """Compute C over time windows."""
    url = GRAY_SCOTT_URLS[pattern_name]
    print(f"\nComputing C over time for {pattern_name}...")
    
    fs, path = fsspec.core.url_to_fs(url)
    
    results = {}
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        for window_size in time_windows:
            try:
                # Get data for this window
                A_data = field_A[sample_idx, :window_size]  # (window_size, 128, 128)
                B_data = field_B[sample_idx, :window_size]  # (window_size, 128, 128)
                
                # Compute mean across spatial dimensions
                A_mean = A_data.mean(axis=(1, 2))  # (window_size,)
                B_mean = B_data.mean(axis=(1, 2))  # (window_size,)
                
                # Stack A and B as components
                X = np.stack([A_mean, B_mean], axis=0)  # (2, window_size)
                
                # Compute C
                C_val = compute_C(X, estimator='gaussian')
                
                # Also compute C for first half and second half
                half = window_size // 2
                X_first = np.stack([A_mean[:half], B_mean[:half]], axis=0)
                X_second = np.stack([A_mean[half:], B_mean[half:]], axis=0)
                
                C_first = compute_C(X_first, estimator='gaussian')
                C_second = compute_C(X_second, estimator='gaussian')
                
                results[window_size] = {
                    'C_total': C_val,
                    'C_first_half': C_first,
                    'C_second_half': C_second,
                    'C_change': C_second - C_first,
                }
                
                print(f"  window={window_size}: C={C_val:.6f}, C_first={C_first:.6f}, C_second={C_second:.6f}, delta={C_second-C_first:.6f}")
                
            except Exception as e:
                print(f"  window={window_size}: error - {e}")
    
    return results

def main():
    print("RD-WELL.4A — Compute C Over Time")
    print("=" * 60)
    print("Question: Does C increase before stabilization?")
    print("=" * 60)
    
    all_results = {}
    
    for pattern_name in ['bubbles', 'maze', 'spirals']:
        results = compute_C_over_time(pattern_name)
        all_results[pattern_name] = results
    
    # Analysis
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    
    for pattern_name, results in all_results.items():
        print(f"\n{pattern_name}:")
        for window_size, data in sorted(results.items()):
            print(f"  window={window_size}: C={data['C_total']:.6f}, ΔC={data['C_change']:.6f}")
        
        # Check if C increases over time
        windows = sorted(results.keys())
        if len(windows) >= 2:
            first_C = results[windows[0]]['C_total']
            last_C = results[windows[-1]]['C_total']
            if last_C > first_C * 1.1:
                print(f"  → C INCREASES over time ({first_C:.6f} → {last_C:.6f})")
            elif last_C < first_C * 0.9:
                print(f"  → C DECREASES over time ({first_C:.6f} → {last_C:.6f})")
            else:
                print(f"  → C STAYS ROUGHLY CONSTANT ({first_C:.6f} → {last_C:.6f})")
    
    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well4a"
    os.makedirs(output_dir, exist_ok=True)
    
    output = {
        'description': 'C over time - asking if C increases before stabilization',
        'results': all_results
    }
    
    output_file = os.path.join(output_dir, "C_over_time.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
