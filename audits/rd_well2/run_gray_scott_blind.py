#!/usr/bin/env python3
"""
RD-WELL.2 Blind Physics Reconnaissance
Gray-Scott Reaction Diffusion

Observes raw evolution of Gray-Scott system.
Only operational descriptions allowed.
Prohibited: coherence, fertility, interaction, persistence, emergence, etc.
"""

import numpy as np
import json
import os
import sys

# Add the_well to path
sys.path.insert(0, '/home/student/sgp_core_v2/the_well')

def load_gray_scott_data():
    """Load Gray-Scott data using the_well API."""
    try:
        from the_well.data import WellDataset
        
        # Check what files are available
        data_dir = "/home/student/sgp_core_v2/well_data/datasets/gray_scott_reaction_diffusion/data/train"
        available_files = [f for f in os.listdir(data_dir) if f.endswith('.hdf5')]
        print(f"Available files: {available_files}")
        
        dataset = WellDataset(
            well_base_path="/home/student/sgp_core_v2/well_data/datasets",
            well_dataset_name="gray_scott_reaction_diffusion",
            well_split_name="train",
            n_steps_input=1,
            n_steps_output=1,
            return_grid=False,
            flatten_tensors=True
        )
        
        print(f"Dataset loaded: {len(dataset)} samples")
        print(f"Metadata: {dataset.metadata}")
        
        return dataset
    except Exception as e:
        print(f"Error loading dataset: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_operational_quantities(dataset, sample_idx=0):
    """Extract operational quantities from a single trajectory."""
    sample = dataset[sample_idx]
    
    # Get fields
    input_fields = sample['input_fields']  # [T, H, W, C]
    output_fields = sample['output_fields']  # [T, H, W, C]
    
    print(f"\nSample shapes:")
    print(f"  input_fields: {input_fields.shape}")
    print(f"  output_fields: {output_fields.shape}")
    
    # Combine into full trajectory
    full_trajectory = np.concatenate([input_fields, output_fields], axis=0)
    print(f"  full_trajectory: {full_trajectory.shape}")
    
    # Extract fields A and B
    if full_trajectory.shape[-1] == 2:
        A = full_trajectory[:, :, :, 0]  # [T, H, W]
        B = full_trajectory[:, :, :, 1]  # [T, H, W]
    else:
        print("Warning: Expected 2 fields (A, B)")
        return None
    
    # Compute operational quantities
    quantities = {
        'A_mean': [],
        'A_std': [],
        'A_min': [],
        'A_max': [],
        'B_mean': [],
        'B_std': [],
        'B_min': [],
        'B_max': [],
        'A_spatial_variance': [],
        'B_spatial_variance': [],
        'B_local_maxima_count': [],
        'A_total': [],
        'B_total': [],
    }
    
    for t in range(A.shape[0]):
        A_t = A[t]
        B_t = B[t]
        
        quantities['A_mean'].append(float(np.mean(A_t)))
        quantities['A_std'].append(float(np.std(A_t)))
        quantities['A_min'].append(float(np.min(A_t)))
        quantities['A_max'].append(float(np.max(A_t)))
        quantities['B_mean'].append(float(np.mean(B_t)))
        quantities['B_std'].append(float(np.std(B_t)))
        quantities['B_min'].append(float(np.min(B_t)))
        quantities['B_max'].append(float(np.max(B_t)))
        quantities['A_spatial_variance'].append(float(np.var(A_t)))
        quantities['B_spatial_variance'].append(float(np.var(B_t)))
        
        # Count local maxima of B (simple method: points higher than all neighbors)
        from scipy import ndimage
        # Create a binary image where B is at local maximum
        B_binary = (B_t > np.roll(B_t, 1, axis=0)) & \
                   (B_t > np.roll(B_t, -1, axis=0)) & \
                   (B_t > np.roll(B_t, 1, axis=1)) & \
                   (B_t > np.roll(B_t, -1, axis=1))
        quantities['B_local_maxima_count'].append(int(np.sum(B_binary)))
        
        quantities['A_total'].append(float(np.sum(A_t)))
        quantities['B_total'].append(float(np.sum(B_t)))
    
    return quantities, A, B

def blind_observation(quantities, A, B):
    """Generate blind observation from operational quantities."""
    observations = []
    
    # Time series observations
    n_timesteps = len(quantities['A_mean'])
    
    # Change in A mean
    A_mean_change = quantities['A_mean'][-1] - quantities['A_mean'][0]
    observations.append(f"A mean changed by {A_mean_change:.6f} over {n_timesteps} steps")
    
    # Change in B mean
    B_mean_change = quantities['B_mean'][-1] - quantities['B_mean'][0]
    observations.append(f"B mean changed by {B_mean_change:.6f} over {n_timesteps} steps")
    
    # Variance in A
    A_var_change = quantities['A_spatial_variance'][-1] - quantities['A_spatial_variance'][0]
    observations.append(f"A spatial variance changed by {A_var_change:.6f}")
    
    # Variance in B
    B_var_change = quantities['B_spatial_variance'][-1] - quantities['B_spatial_variance'][0]
    observations.append(f"B spatial variance changed by {B_var_change:.6f}")
    
    # Number of local maxima of B
    B_maxima_initial = quantities['B_local_maxima_count'][0]
    B_maxima_final = quantities['B_local_maxima_count'][-1]
    observations.append(f"Number of local maxima of B: {B_maxima_initial} initially, {B_maxima_final} finally")
    
    # Total A
    A_total_change = quantities['A_total'][-1] - quantities['A_total'][0]
    observations.append(f"Total A changed by {A_total_change:.6f}")
    
    # Total B
    B_total_change = quantities['B_total'][-1] - quantities['B_total'][0]
    observations.append(f"Total B changed by {B_total_change:.6f}")
    
    return observations

def main():
    print("RD-WELL.2 Blind Physics Reconnaissance")
    print("=" * 60)
    print("Prohibited words: coherence, fertility, interaction, persistence,")
    print("emergence, observer, sentience, hierarchy, organization, structure,")
    print("pattern, function, purpose, adaptive, self, collective, global,")
    print("local, information, complexity, dynamics, stability, attractor,")
    print("state, variable, parameter, system")
    print("=" * 60)
    
    # Load data
    dataset = load_gray_scott_data()
    if dataset is None:
        print("Failed to load dataset")
        return
    
    # Extract operational quantities from first sample
    print("\nExtracting operational quantities...")
    result = extract_operational_quantities(dataset, sample_idx=0)
    
    if result is None:
        print("Failed to extract quantities")
        return
    
    quantities, A, B = result
    
    # Generate blind observations
    print("\nGenerating blind observations...")
    observations = blind_observation(quantities, A, B)
    
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
        'sample_idx': 0,
        'prohibited_words': [
            'coherence', 'fertility', 'interaction', 'persistence', 'emergence',
            'observer', 'sentience', 'hierarchy', 'organization', 'structure',
            'pattern', 'function', 'purpose', 'adaptive', 'self', 'collective',
            'global', 'local', 'information', 'complexity', 'dynamics', 'stability',
            'attractor', 'state', 'variable', 'parameter', 'system'
        ],
        'observations': observations,
        'quantities': {
            'A_mean': quantities['A_mean'],
            'A_std': quantities['A_std'],
            'B_mean': quantities['B_mean'],
            'B_std': quantities['B_std'],
            'A_spatial_variance': quantities['A_spatial_variance'],
            'B_spatial_variance': quantities['B_spatial_variance'],
            'B_local_maxima_count': quantities['B_local_maxima_count'],
            'A_total': quantities['A_total'],
            'B_total': quantities['B_total'],
        }
    }
    
    output_file = os.path.join(output_dir, "gray_scott_blind_observations.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
