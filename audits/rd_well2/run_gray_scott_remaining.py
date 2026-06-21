#!/usr/bin/env python3
"""
RD-WELL.2 Blind Physics Reconnaissance - Remaining Gray-Scott Patterns

Streams the remaining Gray-Scott patterns (gliders, spots, worms).
"""

import fsspec
import h5py
import numpy as np
import json
import os

# URLs for remaining Gray-Scott files
GRAY_SCOTT_URLS = {
    'gliders': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_gliders_F_0.014_k_0.054.hdf5',
    'spots': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_spots_F_0.03_k_0.062.hdf5',
    'worms': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_worms_F_0.058_k_0.065.hdf5',
}

def stream_time_series(pattern_name, sample_idx=0, time_steps=[0, 100, 500, 1000]):
    """Stream multiple time steps from a Gray-Scott pattern."""
    url = GRAY_SCOTT_URLS[pattern_name]
    print(f"\nStreaming {pattern_name} pattern at time steps {time_steps}...")
    
    fs, path = fsspec.core.url_to_fs(url)
    
    results = {}
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        # Get metadata
        F = f.attrs['F']
        k = f.attrs['k']
        
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        for t in time_steps:
            A = field_A[sample_idx, t]
            B = field_B[sample_idx, t]
            
            # Compute operational quantities
            quantities = {
                'time_step': int(t),
                'A_mean': float(np.mean(A)),
                'A_std': float(np.std(A)),
                'A_min': float(np.min(A)),
                'A_max': float(np.max(A)),
                'B_mean': float(np.mean(B)),
                'B_std': float(np.std(B)),
                'B_min': float(np.min(B)),
                'B_max': float(np.max(B)),
                'A_spatial_variance': float(np.var(A)),
                'B_spatial_variance': float(np.var(B)),
                'A_total': float(np.sum(A)),
                'B_total': float(np.sum(B)),
            }
            
            # Count local maxima of B
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
            
            results[t] = quantities
            
    return results, F, k

def blind_time_series_observation(results, pattern_name, F, k):
    """Generate blind observation from time series data."""
    observations = []
    
    observations.append(f"Pattern: {pattern_name} (F={F}, k={k})")
    observations.append(f"Time steps analyzed: {list(results.keys())}")
    
    # Describe changes over time
    for t in sorted(results.keys()):
        q = results[t]
        observations.append(f"\nTime step {t}:")
        observations.append(f"  A: mean={q['A_mean']:.4f}, std={q['A_std']:.4f}, range=[{q['A_min']:.4f}, {q['A_max']:.4f}]")
        observations.append(f"  B: mean={q['B_mean']:.4f}, std={q['B_std']:.4f}, range=[{q['B_min']:.4f}, {q['B_max']:.4f}]")
        observations.append(f"  Spatial variance: A={q['A_spatial_variance']:.6f}, B={q['B_spatial_variance']:.6f}")
        observations.append(f"  Local maxima: A={q['A_local_maxima_count']}, B={q['B_local_maxima_count']}")
    
    # Describe changes between first and last time step
    first_t = min(results.keys())
    last_t = max(results.keys())
    first = results[first_t]
    last = results[last_t]
    
    observations.append(f"\nChange from t={first_t} to t={last_t}:")
    observations.append(f"  A mean: {first['A_mean']:.4f} -> {last['A_mean']:.4f} (delta={last['A_mean']-first['A_mean']:.6f})")
    observations.append(f"  B mean: {first['B_mean']:.4f} -> {last['B_mean']:.4f} (delta={last['B_mean']-first['B_mean']:.6f})")
    observations.append(f"  A spatial variance: {first['A_spatial_variance']:.6f} -> {last['A_spatial_variance']:.6f}")
    observations.append(f"  B spatial variance: {first['B_spatial_variance']:.6f} -> {last['B_spatial_variance']:.6f}")
    observations.append(f"  A local maxima: {first['A_local_maxima_count']} -> {last['A_local_maxima_count']}")
    observations.append(f"  B local maxima: {first['B_local_maxima_count']} -> {last['B_local_maxima_count']}")
    
    return observations

def main():
    print("RD-WELL.2 Blind Physics Reconnaissance - Remaining Gray-Scott Patterns")
    print("=" * 60)
    print("Prohibited words: coherence, fertility, interaction, persistence,")
    print("emergence, observer, sentience, hierarchy, organization, structure,")
    print("pattern, function, purpose, adaptive, self, collective, global,")
    print("local, information, complexity, dynamics, stability, attractor,")
    print("state, variable, parameter, system")
    print("=" * 60)
    
    all_results = {}
    
    for pattern_name in ['gliders', 'spots', 'worms']:
        try:
            # Stream time series
            results, F, k = stream_time_series(pattern_name, sample_idx=0, time_steps=[0, 100, 500, 1000])
            
            # Generate blind observations
            observations = blind_time_series_observation(results, pattern_name, F, k)
            
            print("\n" + "=" * 60)
            print(f"BLIND OBSERVATIONS ({pattern_name})")
            print("=" * 60)
            for obs in observations:
                print(obs)
            
            all_results[pattern_name] = {
                'F': F,
                'k': k,
                'time_series': results,
                'observations': observations
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
    
    output_file = os.path.join(output_dir, "gray_scott_remaining_patterns_observations.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
