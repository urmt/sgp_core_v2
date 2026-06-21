#!/usr/bin/env python3
"""
RD-WELL.5.3 — Test Temporal Ordering: Does C Increase Before Stabilization?

Operational definition of stabilization:
- Frame-to-frame variance stabilization time: t=10 (for bubbles)

Test:
- Compute C for windows before stabilization (t < 10)
- Compute C for windows after stabilization (t > 10)
- Compare
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

def main():
    print("RD-WELL.5.3 — Test Temporal Ordering")
    print("=" * 60)
    print("Operational definition of stabilization:")
    print("  Frame-to-frame variance stabilization time: t=10")
    print("=" * 60)
    
    fs, path = fsspec.core.url_to_fs(BUBBLES_URL)
    
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        # Use first trajectory
        A_data = field_A[0]  # (1001, 128, 128)
        B_data = field_B[0]  # (1001, 128, 128)
        
        # Compute mean across spatial dimensions
        A_mean = A_data.mean(axis=(1, 2))  # (1001,)
        B_mean = B_data.mean(axis=(1, 2))  # (1001,)
        
        # Stabilization time
        t_stab = 10
        
        # Compute C for different windows
        windows = {
            'before_stab_5': (0, 5),
            'before_stab_10': (0, 10),
            'after_stab_5': (10, 15),
            'after_stab_10': (10, 20),
            'full_20': (0, 20),
        }
        
        results = {}
        
        for window_name, (start, end) in windows.items():
            # Extract window
            A_window = A_mean[start:end]
            B_window = B_mean[start:end]
            
            # Stack as components
            X = np.stack([A_window, B_window], axis=0)  # (2, window_size)
            
            # Compute C
            C_val = compute_C(X, estimator='gaussian')
            
            results[window_name] = {
                'start': start,
                'end': end,
                'C': C_val,
            }
            
            print(f"  {window_name}: C={C_val:.6f}")
        
        # Analysis
        print("\n" + "=" * 60)
        print("ANALYSIS")
        print("=" * 60)
        
        C_before = results['before_stab_10']['C']
        C_after = results['after_stab_10']['C']
        
        print(f"\nC before stabilization (t=0-10): {C_before:.6f}")
        print(f"C after stabilization (t=10-20): {C_after:.6f}")
        
        if C_after > C_before:
            print(f"→ C INCREASES after stabilization")
        elif C_after < C_before:
            print(f"→ C DECREASES after stabilization")
        else:
            print(f"→ C STAYS CONSTANT")
        
        # Save results
        output_dir = "/home/student/sgp_core_v2/audits/rd_well5"
        os.makedirs(output_dir, exist_ok=True)
        
        output = {
            'description': 'Temporal ordering test: does C increase before stabilization?',
            'stabilization_time': t_stab,
            'results': results
        }
        
        output_file = os.path.join(output_dir, "temporal_ordering_test.json")
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
