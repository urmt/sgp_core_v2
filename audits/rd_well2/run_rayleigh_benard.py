#!/usr/bin/env python3
"""
RD-WELL.2 Blind Physics Reconnaissance - Rayleigh-Bénard Convection

Streams Rayleigh-Bénard data directly from HuggingFace.
"""

import fsspec
import h5py
import numpy as np
import json
import os

# URLs for Rayleigh-Bénard files (using different Rayleigh and Prandtl numbers)
RAYLEIGH_BENARD_URLS = {
    'Ra1e6_Pr1': 'https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Rayleigh_1e6_Prandtl_1.hdf5',
    'Ra1e8_Pr1': 'https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Rayleigh_1e8_Prandtl_1.hdf5',
    'Ra1e10_Pr1': 'https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Rayleigh_1e10_Prandtl_1.hdf5',
}

def stream_rayleigh_benard_data(config_name, sample_idx=0, time_steps=[0, 100, 500, 1000]):
    """Stream Rayleigh-Bénard data from HuggingFace."""
    url = RAYLEIGH_BENARD_URLS[config_name]
    print(f"\nStreaming {config_name} at time steps {time_steps}...")
    
    fs, path = fsspec.core.url_to_fs(url)
    
    results = {}
    attrs = {}
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        # Get metadata
        attrs = dict(f.attrs)
        print(f"Attributes: {attrs}")
        
        # Get fields
        t0_fields = f['t0_fields']
        print(f"t0_fields: {list(t0_fields.keys())}")
        
        # Check what fields are available
        field_names = list(t0_fields.keys())
        print(f"Available fields: {field_names}")
        
        # Extract buoyancy field (Rayleigh-Bénard uses buoyancy, not temperature)
        if 'buoyancy' in field_names:
            field_buoyancy = t0_fields['buoyancy']
            field_name = 'buoyancy'
        elif 'pressure' in field_names:
            field_buoyancy = t0_fields['pressure']
            field_name = 'pressure'
        else:
            print(f"No buoyancy or pressure field found. Available: {field_names}")
            return None, None
        
        print(f"Field {field_name} shape: {field_buoyancy.shape}")
        
        # Get the actual number of time steps
        n_steps = field_buoyancy.shape[1]
        print(f"Number of time steps: {n_steps}")
        
        # Adjust time steps to be within range
        valid_time_steps = [t for t in time_steps if t < n_steps]
        print(f"Valid time steps: {valid_time_steps}")
        
        for t in valid_time_steps:
            try:
                buoyancy = field_buoyancy[sample_idx, t]
                
                # Compute operational quantities
                quantities = {
                    'time_step': int(t),
                    'buoyancy_mean': float(np.mean(buoyancy)),
                    'buoyancy_std': float(np.std(buoyancy)),
                    'buoyancy_min': float(np.min(buoyancy)),
                    'buoyancy_max': float(np.max(buoyancy)),
                    'buoyancy_spatial_variance': float(np.var(buoyancy)),
                    'buoyancy_total': float(np.sum(buoyancy)),
                }
                
                # Count local maxima of buoyancy
                buoyancy_padded = np.pad(buoyancy, ((1, 1), (1, 1)), mode='wrap')
                local_max = (buoyancy > buoyancy_padded[:-2, 1:-1]) & \
                            (buoyancy > buoyancy_padded[2:, 1:-1]) & \
                            (buoyancy > buoyancy_padded[1:-1, :-2]) & \
                            (buoyancy > buoyancy_padded[1:-1, 2:])
                quantities['buoyancy_local_maxima_count'] = int(np.sum(local_max))
                
                results[t] = quantities
                
            except Exception as e:
                print(f"Error at time step {t}: {e}")
            
    return results, attrs

def blind_observation(results, config_name, attrs):
    """Generate blind observation from time series data."""
    observations = []
    
    observations.append(f"Configuration: {config_name}")
    observations.append(f"Rayleigh: {attrs['Rayleigh']}, Prandtl: {attrs['Prandtl']}")
    
    # Describe changes over time
    for t in sorted(results.keys()):
        q = results[t]
        observations.append(f"\nTime step {t}:")
        observations.append(f"  Buoyancy: mean={q['buoyancy_mean']:.4f}, std={q['buoyancy_std']:.4f}, range=[{q['buoyancy_min']:.4f}, {q['buoyancy_max']:.4f}]")
        observations.append(f"  Spatial variance: {q['buoyancy_spatial_variance']:.6f}")
        observations.append(f"  Local maxima: {q['buoyancy_local_maxima_count']}")
    
    # Describe changes between first and last time step
    if len(results) > 1:
        first_t = min(results.keys())
        last_t = max(results.keys())
        first = results[first_t]
        last = results[last_t]
        
        observations.append(f"\nChange from t={first_t} to t={last_t}:")
        observations.append(f"  Buoyancy mean: {first['buoyancy_mean']:.4f} -> {last['buoyancy_mean']:.4f} (delta={last['buoyancy_mean']-first['buoyancy_mean']:.6f})")
        observations.append(f"  Buoyancy spatial variance: {first['buoyancy_spatial_variance']:.6f} -> {last['buoyancy_spatial_variance']:.6f}")
        observations.append(f"  Buoyancy local maxima: {first['buoyancy_local_maxima_count']} -> {last['buoyancy_local_maxima_count']}")
    
    return observations

def main():
    print("RD-WELL.2 Blind Physics Reconnaissance - Rayleigh-Bénard Convection")
    print("=" * 60)
    print("Prohibited words: coherence, fertility, interaction, persistence,")
    print("emergence, observer, sentience, hierarchy, organization, structure,")
    print("pattern, function, purpose, adaptive, self, collective, global,")
    print("local, information, complexity, dynamics, stability, attractor,")
    print("state, variable, parameter, system")
    print("=" * 60)
    
    all_results = {}
    
    for config_name in ['Ra1e6_Pr1', 'Ra1e8_Pr1', 'Ra1e10_Pr1']:
        try:
            # Stream data (Rayleigh-Bénard has 200 time steps)
            results, attrs = stream_rayleigh_benard_data(config_name, sample_idx=0, time_steps=[0, 50, 100, 150, 199])
            
            if results is None:
                print(f"Failed to get results for {config_name}")
                continue
            
            # Generate blind observations
            observations = blind_observation(results, config_name, attrs)
            
            print("\n" + "=" * 60)
            print(f"BLIND OBSERVATIONS ({config_name})")
            print("=" * 60)
            for obs in observations:
                print(obs)
            
            all_results[config_name] = {
                'attrs': {k: str(v) for k, v in attrs.items()},
                'time_series': results,
                'observations': observations
            }
            
        except Exception as e:
            print(f"Error processing {config_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well2"
    os.makedirs(output_dir, exist_ok=True)
    
    output = {
        'dataset': 'rayleigh_benard',
        'prohibited_words': [
            'coherence', 'fertility', 'interaction', 'persistence', 'emergence',
            'observer', 'sentience', 'hierarchy', 'organization', 'structure',
            'pattern', 'function', 'purpose', 'adaptive', 'self', 'collective',
            'global', 'local', 'information', 'complexity', 'dynamics', 'stability',
            'attractor', 'state', 'variable', 'parameter', 'system'
        ],
        'results': all_results
    }
    
    output_file = os.path.join(output_dir, "rayleigh_benard_blind_observations.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
