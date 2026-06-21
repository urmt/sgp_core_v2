#!/usr/bin/env python3
"""
RD-WELL.5.4 — Test Temporal Ordering (Simplified)

Operational definition of stabilization:
- Frame-to-frame variance stabilization time: t=10 (for bubbles)

Test:
- Compute C for window before stabilization (t=0-10)
- Compute C for window after stabilization (t=10-20)
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
    print("RD-WELL.5.4 — Test Temporal Ordering (Simplified)")
    print("=" * 60)
    
    fs, path = fsspec.core.url_to_fs(BUBBLES_URL)
    
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        # Use first trajectory, first 20 time steps
        A_data = field_A[0, :20]  # (20, 128, 128)
        B_data = field_B[0, :20]  # (20, 128, 128)
        
        # Compute mean across spatial dimensions
        A_mean = A_data.mean(axis=(1, 2))  # (20,)
        B_mean = B_data.mean(axis=(1, 2))  # (20,)
        
        # Stabilization time
        t_stab = 10
        
        # Compute C for windows
        # Before stabilization: t=0-10
        A_before = A_mean[:10]
        B_before = B_mean[:10]
        X_before = np.stack([A_before, B_before], axis=0)
        C_before = compute_C(X_before, estimator='gaussian')
        
        # After stabilization: t=10-20
        A_after = A_mean[10:20]
        B_after = B_mean[10:20]
        X_after = np.stack([A_after, B_after], axis=0)
        C_after = compute_C(X_after, estimator='gaussian')
        
        print(f"C before stabilization (t=0-10): {C_before:.6f}")
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
            'description': 'Temporal ordering test',
            'stabilization_time': t_stab,
            'results': {
                'C_before': C_before,
                'C_after': C_after,
            }
        }
        
        output_file = os.path.join(output_dir, "temporal_ordering_test_simplified.json")
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
