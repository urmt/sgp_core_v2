#!/usr/bin/env python3
"""
RD-WELL.5A — Threshold Sensitivity Audit

Test stabilization time across different thresholds.
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

def find_stabilization_time(metric_values, threshold, window_size=20):
    """Find stabilization time using sliding window."""
    if len(metric_values) < window_size:
        return None
    
    # Compute rolling mean
    rolling_mean = np.convolve(metric_values, np.ones(window_size)/window_size, mode='valid')
    
    # Find where rolling mean drops below threshold
    for i in range(len(rolling_mean)):
        if rolling_mean[i] < threshold:
            return i + window_size // 2
    
    return len(metric_values)

def main():
    print("RD-WELL.5A — Threshold Sensitivity Audit")
    print("=" * 60)
    

    fs, path = fsspec.core.url_to_fs(BUBBLES_URL)
    
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        # Use first trajectory, first 200 time steps
        A_data = field_A[0, :200]
        B_data = field_B[0, :200]
        
        # Compute mean across spatial dimensions
        A_mean = A_data.mean(axis=(1, 2))
        B_mean = B_data.mean(axis=(1, 2))
        
        # Compute frame-to-frame differences
        A_diff = np.abs(np.diff(A_mean))
        B_diff = np.abs(np.diff(B_mean))
        
        # Test different thresholds
        thresholds = [0.001, 0.005, 0.01, 0.02, 0.05]
        
        results = {}
        
        for threshold in thresholds:
            t_stab_A = find_stabilization_time(A_diff, threshold)
            t_stab_B = find_stabilization_time(B_diff, threshold)
            
            # Compute C before and after stabilization
            if t_stab_A is not None and t_stab_A > 10 and t_stab_A < 190:
                A_before = A_mean[:t_stab_A]
                B_before = B_mean[:t_stab_A]
                X_before = np.stack([A_before, B_before], axis=0)
                C_before = compute_C(X_before, estimator='gaussian')
                
                # After stabilization (next 10 steps)
                A_after = A_mean[t_stab_A:t_stab_A+10]
                B_after = B_mean[t_stab_A:t_stab_A+10]
                X_after = np.stack([A_after, B_after], axis=0)
                C_after = compute_C(X_after, estimator='gaussian')
                
                results[threshold] = {
                    't_stab_A': t_stab_A,
                    't_stab_B': t_stab_B,
                    'C_before': C_before,
                    'C_after': C_after,
                    'C_increases': C_after > C_before,
                }
                
                print(f"\nThreshold θ={threshold}:")
                print(f"  Stabilization A: t={t_stab_A}")
                print(f"  Stabilization B: t={t_stab_B}")
                print(f"  C before: {C_before:.6f}")
                print(f"  C after: {C_after:.6f}")
                print(f"  C increases: {C_after > C_before}")
            else:
                print(f"\nThreshold θ={threshold}: Stabilization not found or boundary issue")
                results[threshold] = {
                    't_stab_A': t_stab_A,
                    't_stab_B': t_stab_B,
                    'C_before': None,
                    'C_after': None,
                    'C_increases': None,
                }
        
        # Analyze stability
        print("\n" + "=" * 60)
        print("THRESHOLD STABILITY ANALYSIS")
        print("=" * 60)
        
        stable_count = sum(1 for r in results.values() if r['C_increases'] is True)
        total_count = len([r for r in results.values() if r['C_increases'] is not None])
        
        print(f"\nC increases after stabilization in {stable_count}/{total_count} thresholds")
        
        if stable_count == total_count:
            print("→ Temporal ordering STABLE across all tested thresholds")
        elif stable_count == 0:
            print("→ Temporal ordering INCONSISTENT across tested thresholds")
        else:
            print("→ Temporal ordering PARTIALLY STABLE across tested thresholds")
        
        # Save results
        output_dir = "/home/student/sgp_core_v2/audits/rd_well5a"
        os.makedirs(output_dir, exist_ok=True)
        
        output = {
            'description': 'Threshold sensitivity audit for stabilization',
            'results': {str(k): v for k, v in results.items()},
        }
        
        output_file = os.path.join(output_dir, "threshold_sensitivity_audit.json")
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
