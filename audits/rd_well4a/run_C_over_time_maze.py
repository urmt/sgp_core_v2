#!/usr/bin/env python3
"""
RD-WELL.4A.2 — Compute C Over Time for Maze Only

Safe finding: Observed C increased across sampled windows in one dataset (bubbles).
Temporal relation to stabilization remains under investigation.

Now testing: maze pattern only.
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

# URL for maze
MAZE_URL = 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_maze_F_0.029_k_0.057.hdf5'

def compute_C_over_time_maze():
    """Compute C over time windows for maze."""
    print(f"\nComputing C over time for maze...")
    
    fs, path = fsspec.core.url_to_fs(MAZE_URL)
    
    results = {}
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        # Use smaller windows
        windows = [50, 100, 200]
        
        for window_size in windows:
            try:
                # Get data for this window
                A_data = field_A[0, :window_size]  # (window_size, 128, 128)
                B_data = field_B[0, :window_size]  # (window_size, 128, 128)
                
                # Compute mean across spatial dimensions
                A_mean = A_data.mean(axis=(1, 2))  # (window_size,)
                B_mean = B_data.mean(axis=(1, 2))  # (window_size,)
                
                # Stack A and B as components
                X = np.stack([A_mean, B_mean], axis=0)  # (2, window_size)
                
                # Compute C
                C_val = compute_C(X, estimator='gaussian')
                
                results[window_size] = {
                    'C_total': C_val,
                }
                
                print(f"  window={window_size}: C={C_val:.6f}")
                
            except Exception as e:
                print(f"  window={window_size}: error - {e}")
    
    return results

def main():
    print("RD-WELL.4A.2 — Compute C Over Time for Maze")
    print("=" * 60)
    
    results = compute_C_over_time_maze()
    
    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well4a"
    os.makedirs(output_dir, exist_ok=True)
    
    output = {
        'description': 'C over time for maze',
        'results': results
    }
    
    output_file = os.path.join(output_dir, "C_over_time_maze.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
