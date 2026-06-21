#!/usr/bin/env python3
"""
RD-WELL.4 — Apply C Metric to Cross-Domain Datasets

Computes Total Correlation (C) on Gray-Scott and Rayleigh-Bénard datasets.
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

# URLs for Rayleigh-Bénard files
RAYLEIGH_BENARD_URLS = {
    'Ra1e6_Pr1': 'https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Rayleigh_1e6_Prandtl_1.hdf5',
    'Ra1e8_Pr1': 'https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Rayleigh_1e8_Prandtl_1.hdf5',
    'Ra1e10_Pr1': 'https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Rayleigh_1e10_Prandtl_1.hdf5',
}

def compute_C_for_grayscott(pattern_name, sample_idx=0):
    """Compute C for a Gray-Scott pattern."""
    url = GRAY_SCOTT_URLS[pattern_name]
    print(f"\nComputing C for Gray-Scott {pattern_name}...")
    
    fs, path = fsspec.core.url_to_fs(url)
    
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        # Get time series for sample_idx
        A_time_series = field_A[sample_idx]  # (1001, 128, 128)
        B_time_series = field_B[sample_idx]  # (1001, 128, 128)
        
        # Flatten spatial dimensions
        A_flat = A_time_series.reshape(1001, -1)  # (1001, 128*128)
        B_flat = B_time_series.reshape(1001, -1)  # (1001, 128*128)
        
        # Compute C for A and B separately
        # X shape: (n_components, n_timepoints)
        # We'll use the mean across spatial dimensions as a single component
        A_mean = A_flat.mean(axis=1)  # (1001,)
        B_mean = B_flat.mean(axis=1)  # (1001,)
        
        # Stack A and B as components
        X = np.stack([A_mean, B_mean], axis=0)  # (2, 1001)
        
        C_val = compute_C(X, estimator='gaussian')
        print(f"  C(A,B) = {C_val:.6f}")
        
        return C_val

def compute_C_for_rayleigh_benard(config_name, sample_idx=0):
    """Compute C for a Rayleigh-Bénard configuration."""
    url = RAYLEIGH_BENARD_URLS[config_name]
    print(f"\nComputing C for Rayleigh-Bénard {config_name}...")
    
    fs, path = fsspec.core.url_to_fs(url)
    
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_buoyancy = f['t0_fields']['buoyancy']
        
        # Get time series for sample_idx
        buoyancy_time_series = field_buoyancy[sample_idx]  # (200, 512, 128)
        
        # Flatten spatial dimensions
        buoyancy_flat = buoyancy_time_series.reshape(200, -1)  # (200, 512*128)
        
        # Compute C for buoyancy
        # X shape: (n_components, n_timepoints)
        # We'll use the mean across spatial dimensions as a single component
        buoyancy_mean = buoyancy_flat.mean(axis=1)  # (200,)
        
        # Reshape for C computation
        X = buoyancy_mean.reshape(1, -1)  # (1, 200)
        
        C_val = compute_C(X, estimator='gaussian')
        print(f"  C(buoyancy) = {C_val:.6f}")
        
        return C_val

def main():
    print("RD-WELL.4 — Apply C Metric to Cross-Domain Datasets")
    print("=" * 60)
    
    results = {}
    
    # Compute C for Gray-Scott patterns
    for pattern_name in ['bubbles', 'maze', 'spirals']:
        try:
            C_val = compute_C_for_grayscott(pattern_name)
            results[f'grayscott_{pattern_name}'] = C_val
        except Exception as e:
            print(f"Error computing C for {pattern_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Compute C for Rayleigh-Bénard configurations
    for config_name in ['Ra1e6_Pr1', 'Ra1e8_Pr1', 'Ra1e10_Pr1']:
        try:
            C_val = compute_C_for_rayleigh_benard(config_name)
            results[f'rayleigh_benard_{config_name}'] = C_val
        except Exception as e:
            print(f"Error computing C for {config_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for key, val in results.items():
        print(f"  {key}: C = {val:.6f}")
    
    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well4"
    os.makedirs(output_dir, exist_ok=True)
    
    output = {
        'description': 'C metric applied to cross-domain datasets',
        'results': results
    }
    
    output_file = os.path.join(output_dir, "cross_domain_C_values.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
