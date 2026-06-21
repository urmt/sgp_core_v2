#!/usr/bin/env python3
"""
RD-WELL.5.2 — Define Stabilization Operationally (Minimal)

Testing frame-to-frame variance on a small subset of data.
"""

import fsspec
import h5py
import numpy as np
import json
import os

# URL for bubbles
BUBBLES_URL = 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_bubbles_F_0.098_k_0.057.hdf5'

def main():
    print("RD-WELL.5.2 — Define Stabilization Operationally (Minimal)")
    print("=" * 60)
    
    fs, path = fsspec.core.url_to_fs(BUBBLES_URL)
    
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        # Use first trajectory, first 200 time steps
        A_data = field_A[0, :200]  # (200, 128, 128)
        B_data = field_B[0, :200]  # (200, 128, 128)
        
        # Compute mean across spatial dimensions
        A_mean = A_data.mean(axis=(1, 2))  # (200,)
        B_mean = B_data.mean(axis=(1, 2))  # (200,)
        
        # Compute frame-to-frame differences
        A_diff = np.abs(np.diff(A_mean))
        B_diff = np.abs(np.diff(B_mean))
        
        # Find stabilization time (where variance drops below threshold)
        threshold = 0.01
        
        # Simple approach: find where moving average drops below threshold
        window = 10
        A_rolling = np.convolve(A_diff, np.ones(window)/window, mode='valid')
        B_rolling = np.convolve(B_diff, np.ones(window)/window, mode='valid')
        
        # Find first time where rolling mean < threshold
        t_stab_A = None
        t_stab_B = None
        
        for i in range(len(A_rolling)):
            if A_rolling[i] < threshold:
                t_stab_A = i + window
                break
        
        for i in range(len(B_rolling)):
            if B_rolling[i] < threshold:
                t_stab_B = i + window
                break
        
        print(f"Frame-to-frame variance A: stabilization at t={t_stab_A}")
        print(f"Frame-to-frame variance B: stabilization at t={t_stab_B}")
        
        # Save results
        output_dir = "/home/student/sgp_core_v2/audits/rd_well5"
        os.makedirs(output_dir, exist_ok=True)
        
        output = {
            'description': 'Stabilization time analysis for bubbles (minimal)',
            'results': {
                'pattern': 'bubbles',
                'stabilization_times': {
                    'frame_to_frame_variance_A': t_stab_A,
                    'frame_to_frame_variance_B': t_stab_B,
                }
            }
        }
        
        output_file = os.path.join(output_dir, "stabilization_analysis_bubbles_minimal.json")
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
