#!/usr/bin/env python3
"""
RD-WELL.2 Blind Physics Reconnaissance - Direct HDF5 Access

Works with the HDF5 file directly, bypassing the WellDataset class.
This allows us to work with partially downloaded files.
"""

import h5py
import numpy as np
import json
import os
import sys

def inspect_hdf5_file(filepath):
    """Inspect the structure of an HDF5 file."""
    print(f"\nInspecting: {filepath}")
    print(f"File size: {os.path.getsize(filepath) / 1e9:.2f} GB")
    
    try:
        with h5py.File(filepath, 'r') as f:
            print("\nAttributes:")
            for key, value in f.attrs.items():
                print(f"  {key}: {value}")
            
            print("\nGroups:")
            for key in f.keys():
                print(f"  {key}/")
                if hasattr(f[key], 'attrs'):
                    for attr_key, attr_value in f[key].attrs.items():
                        print(f"    {attr_key}: {attr_value}")
            
            return True
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

def extract_sample_data(filepath, sample_idx=0, time_idx=0):
    """Extract a single sample from the HDF5 file."""
    print(f"\nExtracting sample {sample_idx} at time {time_idx}...")
    
    try:
        with h5py.File(filepath, 'r') as f:
            # Get metadata
            n_trajectories = f.attrs['n_trajectories']
            print(f"Number of trajectories: {n_trajectories}")
            
            # Get time steps
            time_dim = f['dimensions']['time']
            print(f"Time dimension shape: {time_dim.shape}")
            
            # Get fields
            t0_fields = f['t0_fields']
            print(f"t0_fields: {t0_fields}")
            
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
            
            return A, B
            
    except Exception as e:
        print(f"Error extracting data: {e}")
        import traceback
        traceback.print_exc()
        return None, None

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
    
    return quantities

def blind_observation(quantities):
    """Generate blind observation from operational quantities."""
    observations = []
    
    # Describe what we see
    observations.append(f"A ranges from {quantities['A_min']:.6f} to {quantities['A_max']:.6f}")
    observations.append(f"B ranges from {quantities['B_min']:.6f} to {quantities['B_max']:.6f}")
    
    observations.append(f"A mean: {quantities['A_mean']:.6f}, std: {quantities['A_std']:.6f}")
    observations.append(f"B mean: {quantities['B_mean']:.6f}, std: {quantities['B_std']:.6f}")
    
    observations.append(f"A spatial variance: {quantities['A_spatial_variance']:.6f}")
    observations.append(f"B spatial variance: {quantities['B_spatial_variance']:.6f}")
    
    observations.append(f"Total A: {quantities['A_total']:.6f}")
    observations.append(f"Total B: {quantities['B_total']:.6f}")
    
    observations.append(f"Number of local maxima of B: {quantities['B_local_maxima_count']}")
    
    return observations

def main():
    print("RD-WELL.2 Blind Physics Reconnaissance - Direct HDF5 Access")
    print("=" * 60)
    print("Prohibited words: coherence, fertility, interaction, persistence,")
    print("emergence, observer, sentience, hierarchy, organization, structure,")
    print("pattern, function, purpose, adaptive, self, collective, global,")
    print("local, information, complexity, dynamics, stability, attractor,")
    print("state, variable, parameter, system")
    print("=" * 60)
    
    # Find the HDF5 file
    data_dir = "/home/student/sgp_core_v2/well_data/datasets/gray_scott_reaction_diffusion/data/train"
    hdf5_files = [f for f in os.listdir(data_dir) if f.endswith('.hdf5')]
    
    if not hdf5_files:
        print("No HDF5 files found")
        return
    
    filepath = os.path.join(data_dir, hdf5_files[0])
    print(f"\nUsing file: {hdf5_files[0]}")
    
    # Inspect the file structure
    if not inspect_hdf5_file(filepath):
        print("Failed to inspect file")
        return
    
    # Extract sample data
    A, B = extract_sample_data(filepath, sample_idx=0, time_idx=0)
    
    if A is None or B is None:
        print("Failed to extract data")
        return
    
    # Compute operational quantities
    print("\nComputing operational quantities...")
    quantities = compute_operational_quantities(A, B)
    
    # Generate blind observations
    print("\nGenerating blind observations...")
    observations = blind_observation(quantities)
    
    print("\n" + "=" * 60)
    print("BLIND OBSERVATIONS (Gray-Scott)")
    print("=" * 60)
    for i, obs in enumerate(observations, 1):
        print(f"{i}. {obs}")
    
    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well2"
    os.makedirs(output_dir, exist_ok=True)
    
    output = {
        'dataset': 'gray_scott_reaction_diffusion',
        'file': hdf5_files[0],
        'sample_idx': 0,
        'time_idx': 0,
        'prohibited_words': [
            'coherence', 'fertility', 'interaction', 'persistence', 'emergence',
            'observer', 'sentience', 'hierarchy', 'organization', 'structure',
            'pattern', 'function', 'purpose', 'adaptive', 'self', 'collective',
            'global', 'local', 'information', 'complexity', 'dynamics', 'stability',
            'attractor', 'state', 'variable', 'parameter', 'system'
        ],
        'observations': observations,
        'quantities': quantities
    }
    
    output_file = os.path.join(output_dir, "gray_scott_blind_observations.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
