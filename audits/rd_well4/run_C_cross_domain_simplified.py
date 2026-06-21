#!/usr/bin/env python3
"""
RD-WELL.4 — Apply C Metric to Cross-Domain Datasets (Simplified)

Computes Total Correlation (C) on Gray-Scott and Rayleigh-Bénard datasets.
Uses smaller samples for faster computation.
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
}

def compute_C_for_grayscott(pattern_name, sample_idx=0, n_timepoints=100):
    """Compute C for a Gray-Scott pattern."""
    url = GRAY_SCOTT_URLS[pattern_name]
    print(f"\nComputing C for Gray-Scott {pattern_name}...")
    
    fs, path = fsspec.core.url_to_fs(url)
    
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        # Get time series for sample_idx (use first n_timepoints)
        A_time_series = field_A[sample_idx, :n_timepoints]  # (n_timepoints, 128, 128)
        B_time_series = field_B[sample_idx, :n_timepoints]  # (n_timepoints, 128, 128)
        
        # Compute mean across spatial dimensions
        A_mean = A_time_series.mean(axis=(1, 2))  # (n_timepoints,)
        B_mean = B_time_series.mean(axis=(1, 2))  # (n_timepoints,)
        
        # Stack A and B as components
        X = np.stack([A_mean, B_mean], axis=0)  # (2, n_timepoints)
        
        C_val = compute_C(X, estimator='gaussian')
        print(f"  C(A,B) = {C_val:.6f}")
        
        return C_val

def main():
    print("RD-WELL.4 — Apply C Metric to Cross-Domain Datasets (Simplified)")
    print("=" * 60)
    
    results = {}
    
    # Compute C for Gray-Scott pattern
    pattern_name = 'bubbles'
    try:
        C_val = compute_C_for_grayscott(pattern_name, n_timepoints=100)
        results[f'grayscott_{pattern_name}'] = C_val
    except Exception as e:
        print(f"Error computing C for {pattern_name}: {e}")
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
        'description': 'C metric applied to cross-domain datasets (simplified)',
        'results': results
    }
    
    output_file = os.path.join(output_dir, "cross_domain_C_values_simplified.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
