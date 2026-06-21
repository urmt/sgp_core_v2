#!/usr/bin/env python3
"""
RD-WELL.2 Blind Physics Reconnaissance - Streaming Access

Streams Gray-Scott data directly from HuggingFace without full download.
"""

import fsspec
import h5py
import numpy as np
import json
import os
import sys

# URLs for Gray-Scott files
GRAY_SCOTT_URLS = {
    'bubbles': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_bubbles_F_0.098_k_0.057.hdf5',
    'gliders': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_gliders_F_0.014_k_0.054.hdf5',
    'maze': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_maze_F_0.029_k_0.057.hdf5',
    'spirals': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_spirals_F_0.018_k_0.051.hdf5',
    'spots': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_spots_F_0.03_k_0.062.hdf5',
    'worms': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_worms_F_0.058_k_0.065.hdf5',
}

def stream_gray_scott_data(pattern_name='bubbles', sample_idx=0, time_idx=0):
    """Stream Gray-Scott data from HuggingFace."""
    url = GRAY_SCOTT_URLS[pattern_name]
    print(f"\nStreaming {pattern_name} pattern from HuggingFace...")
    
    fs, path = fsspec.core.url_to_fs(url)
    
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        # Get metadata
        print(f"Dataset name: {f.attrs['dataset_name']}")
        print(f"F: {f.attrs['F']}, k: {f.attrs['k']}")
        print(f"Number of trajectories: {f.attrs['n_trajectories']}")
        
        # Get time steps
        time_dim = f['dimensions']['time']
        print(f"Time dimension shape: {time_dim.shape}")
        
        # Get fields
        t0_fields = f['t0_fields']
        print(f"t0_fields: {list(t0_fields.keys())}")
        
        # Extract field A and B
        field_A = t0_fields['A']
        field_B = t0_fields['B']
        
        print(f"Field A shape: {field_A.shape}")
        print(f"Field B shape: {field_B.shape}")
        
        # Extract data
        A = field_A[sample_idx, time_idx]
        B = field_B[sample_idx, time_idx]
        
        print(f"Extracted A shape: {A.shape}")
        print(f"Extracted B shape: {B.shape}")
        
        return A, B, f.attrs

def compute_operational_quantities(A, B):
    """Compute operational quantities from A and B fields."""
    quantities = {}
    
    # Basic statistics
    quantities['A_mean'] = float(np.mean(A))
    quantities['A_std'] = float(np.std(A))
    quantities['A_min'] = float(np.min(A))
    quantities['A_max'] = float(np.max(A))
    
    quantities['B_mean'] = float(np.mean(B))
    quantities['B_std'] = float(np.std(B))
    quantities['B_min'] = float(np.min(B))
    quantities['B_max'] = float(np.max(B))
    
    # Spatial variance
    quantities['A_spatial_variance'] = float(np.var(A))
    quantities['B_spatial_variance'] = float(np.var(B))
    
    # Total amounts
    quantities['A_total'] = float(np.sum(A))
    quantities['B_total'] = float(np.sum(B))
    
    # Count local maxima of B
    # Simple method: points higher than all 4 neighbors
    B_padded = np.pad(B, ((1, 1), (1, 1)), mode='wrap')
    local_max = (B > B_padded[:-2, 1:-1]) & \
                (B > B_padded[2:, 1:-1]) & \
                (B > B_padded[1:-1, :-2]) & \
                (B > B_padded[1:-1, 2:])
    quantities['B_local_maxima_count'] = int(np.sum(local_max))
    
    # Count local maxima of A
    A_padded = np.pad(A, ((1, 1), (1, 1)), mode='wrap')
    local_max_A = (A > A_padded[:-2, 1:-1]) & \
                  (A > A_padded[2:, 1:-1]) & \
                  (A > A_padded[1:-1, :-2]) & \
                  (A > A_padded[1:-1, 2:])
    quantities['A_local_maxima_count'] = int(np.sum(local_max_A))
    
    return quantities

def blind_observation(quantities, pattern_name):
    """Generate blind observation from operational quantities."""
    observations = []
    
    # Describe what we see
    observations.append(f"Pattern: {pattern_name}")
    observations.append(f"A ranges from {quantities['A_min']:.6f} to {quantities['A_max']:.6f}")
    observations.append(f"B ranges from {quantities['B_min']:.6f} to {quantities['B_max']:.6f}")
    
    observations.append(f"A mean: {quantities['A_mean']:.6f}, std: {quantities['A_std']:.6f}")
    observations.append(f"B mean: {quantities['B_mean']:.6f}, std: {quantities['B_std']:.6f}")
    
    observations.append(f"A spatial variance: {quantities['A_spatial_variance']:.6f}")
    observations.append(f"B spatial variance: {quantities['B_spatial_variance']:.6f}")
    
    observations.append(f"Total A: {quantities['A_total']:.6f}")
    observations.append(f"Total B: {quantities['B_total']:.6f}")
    
    observations.append(f"Number of local maxima of A: {quantities['A_local_maxima_count']}")
    observations.append(f"Number of local maxima of B: {quantities['B_local_maxima_count']}")
    
    return observations

def main():
    print("RD-WELL.2 Blind Physics Reconnaissance - Streaming Access")
    print("=" * 60)
    print("Prohibited words: coherence, fertility, interaction, persistence,")
    print("emergence, observer, sentience, hierarchy, organization, structure,")
    print("pattern, function, purpose, adaptive, self, collective, global,")
    print("local, information, complexity, dynamics, stability, attractor,")
    print("state, variable, parameter, system")
    print("=" * 60)
    
    # Process each pattern
    all_results = {}
    
    for pattern_name in ['bubbles', 'maze', 'spirals']:
        try:
            # Stream data
            A, B, attrs = stream_gray_scott_data(pattern_name, sample_idx=0, time_idx=0)
            
            # Compute operational quantities
            print(f"\nComputing operational quantities for {pattern_name}...")
            quantities = compute_operational_quantities(A, B)
            
            # Generate blind observations
            print(f"\nGenerating blind observations for {pattern_name}...")
            observations = blind_observation(quantities, pattern_name)
            
            print("\n" + "=" * 60)
            print(f"BLIND OBSERVATIONS ({pattern_name})")
            print("=" * 60)
            for i, obs in enumerate(observations, 1):
                print(f"{i}. {obs}")
            
            # Store results
            all_results[pattern_name] = {
                'attrs': {k: str(v) for k, v in attrs.items()},
                'observations': observations,
                'quantities': quantities
            }
            
        except Exception as e:
            print(f"Error processing {pattern_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well2"
    os.makedirs(output_dir, exist_ok=True)
    
    output = {
        'dataset': 'gray_scott_reaction_diffusion',
        'prohibited_words': [
            'coherence', 'fertility', 'interaction', 'persistence', 'emergence',
            'observer', 'sentience', 'hierarchy', 'organization', 'structure',
            'pattern', 'function', 'purpose', 'adaptive', 'self', 'collective',
            'global', 'local', 'information', 'complexity', 'dynamics', 'stability',
            'attractor', 'state', 'variable', 'parameter', 'system'
        ],
        'results': all_results
    }
    
    output_file = os.path.join(output_dir, "gray_scott_blind_observations.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
