#!/usr/bin/env python3
"""
RD-WELL.7A — MHD Reconnaissance Audit

Construct an operational ledger for MHD before computing C.
No theory. No coupling. No organization claims. Only operational description.
"""

import json
import numpy as np
from pathlib import Path
import sys
import os
import h5py
import fsspec

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Forbidden terms
FORBIDDEN_TERMS = [
    'organization', 'coherence', 'adaptation', 'information',
    'intelligence', 'self-awareness', 'sentience', 'consciousness'
]

# Allowed Layer 0 descriptors
LAYER_0_DESCRIPTORS = [
    'mean', 'variance', 'entropy', 'power_spectrum',
    'frame_difference', 'component_count'
]

# Allowed Layer 1a descriptors
LAYER_1A_DESCRIPTORS = [
    'autocorrelation_length', 'spectral_peak', 'temporal_derivative_norm'
]

def load_mhd_frame(file_path, trajectory_idx=0, frame_idx=0):
    """Load a single frame from MHD dataset via fsspec."""
    try:
        with fsspec.open(file_path, "rb") as f, h5py.File(f, "r") as file:
            # Explore file structure
            if 't0_fields' in file:
                fields = file['t0_fields']
                field_names = list(fields.keys())
                
                if field_names:
                    # Load first available field
                    field_name = field_names[0]
                    data = fields[field_name]
                    
                    if trajectory_idx < data.shape[0] and frame_idx < data.shape[1]:
                        frame = data[trajectory_idx, frame_idx]
                        
                        # If 3D, take middle slice
                        if frame.ndim == 3:
                            mid_slice = frame.shape[0] // 2
                            return frame[mid_slice, :, :], field_name, field_names
                        return frame, field_name, field_names
            
            elif 'fields' in file:
                fields = file['fields']
                field_names = list(fields.keys())
                
                if field_names:
                    # Load first available field
                    field_name = field_names[0]
                    data = fields[field_name]
                    
                    if trajectory_idx < data.shape[0] and frame_idx < data.shape[1]:
                        frame = data[trajectory_idx, frame_idx]
                        
                        # If 3D, take middle slice
                        if frame.ndim == 3:
                            mid_slice = frame.shape[0] // 2
                            return frame[mid_slice, :, :], field_name, field_names
                        return frame, field_name, field_names
    
    except Exception as e:
        print(f"    Error loading {file_path}: {e}")
    
    return None, None, None

def normalize_to_01(field):
    """Normalize field to [0, 1] range."""
    field_min = np.min(field)
    field_max = np.max(field)
    if field_max - field_min < 1e-10:
        return np.zeros_like(field)
    return (field - field_min) / (field_max - field_min)

def compute_entropy(field, bins=256):
    """Compute Shannon entropy of field."""
    # Normalize to [0, 1] first
    field_norm = normalize_to_01(field)
    
    # Compute histogram
    hist, _ = np.histogram(field_norm, bins=bins, density=False)
    
    # Normalize to probability distribution
    total = hist.sum()
    if total == 0:
        return 0.0
    hist = hist / total
    
    # Remove zeros
    hist = hist[hist > 0]
    
    # Compute entropy
    entropy = -np.sum(hist * np.log2(hist + 1e-10))
    
    # Ensure non-negative
    return max(0.0, float(entropy))

def compute_power_spectrum(field):
    """Compute 2D power spectrum."""
    # Normalize
    field_norm = normalize_to_01(field)
    
    # Compute 2D FFT
    fft = np.fft.fft2(field_norm)
    power = np.abs(fft) ** 2
    
    # Shift zero frequency to center
    power_shifted = np.fft.fftshift(power)
    
    return power_shifted

def compute_autocorrelation_length(field):
    """Compute autocorrelation length."""
    # Normalize
    field_norm = normalize_to_01(field)
    
    # Compute autocorrelation using FFT
    f = np.fft.fft2(field_norm)
    acf = np.fft.ifft2(f * np.conj(f)).real
    
    # Shift zero lag to center
    acf_shifted = np.fft.fftshift(acf)
    
    # Normalize by zero-lag value
    if acf_shifted.max() > 0:
        acf_shifted = acf_shifted / acf_shifted.max()
    
    # Find first minimum
    # For a 2D field, we compute the radial profile
    center = np.array(acf_shifted.shape) // 2
    y, x = np.ogrid[:acf_shifted.shape[0], :acf_shifted.shape[1]]
    r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    
    # Compute radial profile
    r_int = r.astype(int)
    max_r = min(acf_shifted.shape[0], acf_shifted.shape[1]) // 2
    
    radial_profile = np.zeros(max_r)
    for i in range(max_r):
        mask = r_int == i
        if mask.any():
            radial_profile[i] = acf_shifted[mask].mean()
    
    # Find first zero crossing
    zero_crossings = np.where(radial_profile < 0)[0]
    if len(zero_crossings) > 0:
        return float(zero_crossings[0])
    
    # If no zero crossing, find where it drops to 1/e
    threshold = 1.0 / np.e
    below_threshold = np.where(radial_profile < threshold)[0]
    if len(below_threshold) > 0:
        return float(below_threshold[0])
    
    # Otherwise return max_r
    return float(max_r)

def compute_spectral_peak(field):
    """Compute spectral peak location."""
    # Compute power spectrum
    power = compute_power_spectrum(field)
    
    # Get radial profile
    center = np.array(power.shape) // 2
    y, x = np.ogrid[:power.shape[0], :power.shape[1]]
    r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    
    r_int = r.astype(int)
    max_r = min(power.shape[0], power.shape[1]) // 2
    
    radial_profile = np.zeros(max_r)
    for i in range(max_r):
        mask = r_int == i
        if mask.any():
            radial_profile[i] = power[mask].mean()
    
    # Find peak (excluding DC component)
    if len(radial_profile) > 1:
        peak_idx = np.argmax(radial_profile[1:]) + 1
        return float(peak_idx)
    
    return 0.0

def compute_temporal_derivative_norm(frames):
    """Compute temporal derivative norm."""
    if len(frames) < 2:
        return 0.0
    
    # Compute frame differences
    diffs = []
    for i in range(len(frames) - 1):
        diff = np.abs(frames[i+1] - frames[i]).mean()
        diffs.append(diff)
    
    return float(np.mean(diffs))

def compute_frame_difference(frame1, frame2):
    """Compute frame difference."""
    return float(np.abs(frame1 - frame2).mean())

def compute_component_count(field, threshold=0.5):
    """Compute component count using connected components."""
    # Binarize
    binary = (field > threshold).astype(int)
    
    # Simple connected components (flood fill)
    labeled = np.zeros_like(binary)
    current_label = 0
    
    for i in range(binary.shape[0]):
        for j in range(binary.shape[1]):
            if binary[i, j] == 1 and labeled[i, j] == 0:
                # New component
                current_label += 1
                
                # Flood fill
                stack = [(i, j)]
                while stack:
                    x, y = stack.pop()
                    if 0 <= x < binary.shape[0] and 0 <= y < binary.shape[1]:
                        if binary[x, y] == 1 and labeled[x, y] == 0:
                            labeled[x, y] = current_label
                            stack.extend([
                                (x+1, y), (x-1, y),
                                (x, y+1), (x, y-1)
                            ])
    
    return float(current_label)

def classify_descriptor(descriptor_name):
    """Classify descriptor by layer."""
    if descriptor_name in LAYER_0_DESCRIPTORS:
        return "Layer 0"
    elif descriptor_name in LAYER_1A_DESCRIPTORS:
        return "Layer 1a"
    elif descriptor_name in ['component_count']:
        return "Layer 1b (human-labeled)"
    else:
        return "Layer 2 (forbidden)"

def main():
    """Run MHD reconnaissance audit."""
    
    # Create output directory
    output_dir = Path('/home/student/sgp_core_v2/audits/rd_well7a')
    output_dir.mkdir(exist_ok=True)
    
    frames_dir = output_dir / 'mhd_frames'
    frames_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("RD-WELL.7A — MHD Reconnaissance Audit")
    print("=" * 60)
    
    # Step 1: Dataset Loader Audit
    print("\nStep 1: Dataset Loader Audit")
    print("-" * 40)
    
    # Find MHD dataset files
    try:
        fs, _ = fsspec.url_to_fs("hf://datasets/polymathic-ai/mhd_64")
        files = fs.glob("hf://datasets/polymathic-ai/mhd_64/data/test/*.hdf5")
        
        if not files:
            print("  No MHD files found!")
            return
        
        print(f"  Found {len(files)} MHD files")
        
        # Load first file to get schema
        file_path = f"hf://{files[0]}"
        
        with fsspec.open(file_path, "rb") as f, h5py.File(f, "r") as file:
            # Print file structure
            print("\n  File structure:")
            def print_structure(name, obj):
                if isinstance(obj, h5py.Dataset):
                    print(f"    {name}: shape={obj.shape}, dtype={obj.dtype}")
                elif isinstance(obj, h5py.Group):
                    print(f"    {name}/")
            
            file.visititems(print_structure)
            
            # Get schema information
            schema = {
                'file_path': file_path,
                'file_count': len(files),
                'fields': {},
                'dimensions': None,
                'trajectory_count': None,
                'timestep_count': None,
                'spatial_dimensions': None
            }
            
            # Extract field information
            if 't0_fields' in file:
                fields = file['t0_fields']
                field_names = list(fields.keys())
                schema['fields'] = {name: {
                    'shape': list(fields[name].shape),
                    'dtype': str(fields[name].dtype)
                } for name in field_names}
                
                # Get dimensions from first field
                if field_names:
                    first_field = fields[field_names[0]]
                    schema['trajectory_count'] = first_field.shape[0]
                    schema['timestep_count'] = first_field.shape[1]
                    schema['spatial_dimensions'] = list(first_field.shape[2:])
                    schema['dimensions'] = len(first_field.shape) - 2
            
            elif 'fields' in file:
                fields = file['fields']
                field_names = list(fields.keys())
                schema['fields'] = {name: {
                    'shape': list(fields[name].shape),
                    'dtype': str(fields[name].dtype)
                } for name in field_names}
                
                # Get dimensions from first field
                if field_names:
                    first_field = fields[field_names[0]]
                    schema['trajectory_count'] = first_field.shape[0]
                    schema['timestep_count'] = first_field.shape[1]
                    schema['spatial_dimensions'] = list(first_field.shape[2:])
                    schema['dimensions'] = len(first_field.shape) - 2
            
            # Save schema
            with open(output_dir / 'mhd_schema.json', 'w') as f:
                json.dump(schema, f, indent=2)
            
            print("\n  Schema saved to mhd_schema.json")
            
            # Print schema summary
            print(f"\n  Schema Summary:")
            print(f"    File count: {schema['file_count']}")
            print(f"    Fields: {list(schema['fields'].keys())}")
            print(f"    Trajectories: {schema['trajectory_count']}")
            print(f"    Timesteps: {schema['timestep_count']}")
            print(f"    Spatial dimensions: {schema['spatial_dimensions']}")
            print(f"    Dimensions: {schema['dimensions']}D")
    
    except Exception as e:
        print(f"  Error in dataset loader audit: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Extract 10 representative frames
    print("\nStep 2: Extract 10 Representative Frames")
    print("-" * 40)
    
    frames_data = []
    
    try:
        # Load frames from different files (parameter regimes)
        for file_idx, file_path_rel in enumerate(files[:5]):  # Use first 5 files
            file_path = f"hf://{file_path_rel}"
            
            # Extract parameter info from filename
            filename = file_path_rel.split('/')[-1]
            params = filename.replace('.hdf5', '').replace('MHD_', '')
            
            for frame_idx in [0, 50, 99]:  # Early, middle, late
                frame, field_name, field_names = load_mhd_frame(
                    file_path, 0, frame_idx
                )
                
                if frame is not None:
                    # Normalize frame
                    frame_normalized = normalize_to_01(frame)
                    
                    # Save frame as numpy array
                    frame_filename = f"frame_file{file_idx}_time{frame_idx}.npy"
                    np.save(frames_dir / frame_filename, frame_normalized)
                    
                    frames_data.append({
                        'file_index': file_idx,
                        'parameters': params,
                        'timepoint': frame_idx,
                        'field_name': field_name,
                        'all_fields': field_names,
                        'shape': list(frame.shape),
                        'filename': frame_filename,
                        'min': float(np.min(frame)),
                        'max': float(np.max(frame)),
                        'mean': float(np.mean(frame)),
                        'std': float(np.std(frame))
                    })
                    
                    print(f"  Extracted frame: file={file_idx} ({params}), time={frame_idx}, shape={frame.shape}")
    
    except Exception as e:
        print(f"  Error extracting frames: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n  Extracted {len(frames_data)} frames")
    
    # Step 3: Blind Operational Reconnaissance
    print("\nStep 3: Blind Operational Reconnaissance")
    print("-" * 40)
    
    operational_ledger = []
    
    for frame_info in frames_data:
        # Load frame
        frame = np.load(frames_dir / frame_info['filename'])
        
        # Compute Layer 0 descriptors
        descriptors = {
            'mean': float(np.mean(frame)),
            'variance': float(np.var(frame)),
            'entropy': compute_entropy(frame),
            'frame_difference': 0.0,  # Will compute for consecutive frames
            'component_count': compute_component_count(frame)
        }
        
        # Compute power spectrum statistics
        power = compute_power_spectrum(frame)
        descriptors['spectral_peak'] = compute_spectral_peak(frame)
        
        # Compute Layer 1a descriptors
        descriptors['autocorrelation_length'] = compute_autocorrelation_length(frame)
        descriptors['temporal_derivative_norm'] = 0.0  # Will compute for consecutive frames
        
        # Add to ledger
        operational_ledger.append({
            'file_index': frame_info['file_index'],
            'parameters': frame_info['parameters'],
            'timepoint': frame_info['timepoint'],
            'field_name': frame_info['field_name'],
            'shape': frame_info['shape'],
            'descriptors': descriptors
        })
    
    # Compute temporal derivatives for consecutive frames
    for i in range(len(operational_ledger) - 1):
        frame1 = np.load(frames_dir / frames_data[i]['filename'])
        frame2 = np.load(frames_dir / frames_data[i+1]['filename'])
        
        # Frame difference
        operational_ledger[i]['descriptors']['frame_difference'] = compute_frame_difference(frame1, frame2)
        
        # Temporal derivative norm
        operational_ledger[i]['descriptors']['temporal_derivative_norm'] = compute_temporal_derivative_norm([frame1, frame2])
    
    # Save operational ledger
    with open(output_dir / 'mhd_operational_ledger.json', 'w') as f:
        json.dump(operational_ledger, f, indent=2)
    
    print("\n  Operational ledger saved to mhd_operational_ledger.json")
    
    # Print sample descriptors
    if operational_ledger:
        print("\n  Sample descriptors (first frame):")
        sample = operational_ledger[0]['descriptors']
        for key, value in sample.items():
            print(f"    {key}: {value:.6f}")
    
    # Step 4: Descriptor Ladder Audit
    print("\nStep 4: Descriptor Ladder Audit")
    print("-" * 40)
    
    descriptor_classification = {}
    
    for desc_name in list(LAYER_0_DESCRIPTORS) + list(LAYER_1A_DESCRIPTORS) + ['component_count']:
        layer = classify_descriptor(desc_name)
        descriptor_classification[desc_name] = {
            'layer': layer,
            'is_consumable_by_metrics': layer in ['Layer 0', 'Layer 1a', 'Layer 1b (human-labeled)'],
            'is_forbidden': layer == 'Layer 2 (forbidden)'
        }
        
        print(f"  {desc_name}: {layer}")
    
    # Add forbidden terms check
    print("\n  Forbidden terms check:")
    for term in FORBIDDEN_TERMS:
        print(f"    {term}: FORBIDDEN (Layer 2)")
    
    # Step 5: Measurement Transport Preparation
    print("\nStep 5: Measurement Transport Preparation")
    print("-" * 40)
    
    # Compare MHD against other domains (computability, value ranges, transform sensitivity)
    transport_comparison = {
        'mhd': {
            'computability': 'all_descriptors_computable',
            'value_ranges': {},
            'transform_sensitivity': 'pending'
        },
        'gray_scott': {
            'computability': 'all_descriptors_computable',
            'value_ranges': {},
            'transform_sensitivity': 'tested'
        },
        'rayleigh_benard': {
            'computability': 'all_descriptors_computable',
            'value_ranges': {},
            'transform_sensitivity': 'tested'
        },
        'active_matter': {
            'computability': 'all_descriptors_computable',
            'value_ranges': {},
            'transform_sensitivity': 'tested'
        },
        'acoustic_scattering': {
            'computability': 'all_descriptors_computable',
            'value_ranges': {},
            'transform_sensitivity': 'tested'
        },
        'rayleigh_taylor': {
            'computability': 'all_descriptors_computable',
            'value_ranges': {},
            'transform_sensitivity': 'tested'
        }
    }
    
    # Compute value ranges for MHD
    if operational_ledger:
        all_descriptors = {}
        for entry in operational_ledger:
            for key, value in entry['descriptors'].items():
                if key not in all_descriptors:
                    all_descriptors[key] = []
                all_descriptors[key].append(value)
        
        transport_comparison['mhd']['value_ranges'] = {
            key: {
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'mean': float(np.mean(values)),
                'std': float(np.std(values))
            }
            for key, values in all_descriptors.items()
        }
    
    # Save transport comparison
    with open(output_dir / 'mhd_transport_comparison.json', 'w') as f:
        json.dump(transport_comparison, f, indent=2)
    
    print("\n  Transport comparison saved to mhd_transport_comparison.json")
    
    # Step 6: Save frame statistics
    print("\nStep 6: Save Frame Statistics")
    print("-" * 40)
    
    frame_statistics = {
        'frame_count': len(frames_data),
        'frames': frames_data,
        'descriptor_classification': descriptor_classification,
        'operational_ledger_summary': {
            'descriptor_count': len(operational_ledger[0]['descriptors']) if operational_ledger else 0,
            'layer_0_count': len(LAYER_0_DESCRIPTORS),
            'layer_1a_count': len(LAYER_1A_DESCRIPTORS),
            'forbidden_count': len(FORBIDDEN_TERMS)
        }
    }
    
    with open(output_dir / 'mhd_frame_statistics.json', 'w') as f:
        json.dump(frame_statistics, f, indent=2)
    
    print("\n  Frame statistics saved to mhd_frame_statistics.json")
    
    # Step 7: RD-MAGNETISM WARNING
    print("\nStep 7: RD-MAGNETISM WARNING")
    print("-" * 40)
    
    magnetism_warning = {
        'warning': "Fields possessing topological constraints may invalidate measurements that behave well in unconstrained media.",
        'status': "ACTIVE WARNING",
        'implication': "MHD may expose entirely new hidden variables.",
        'new_structures': [
            "magnetic fields",
            "reconnection",
            "turbulence",
            "multi-scale cascades",
            "topological constraints"
        ]
    }
    
    with open(output_dir / 'rd_magnetism_warning.json', 'w') as f:
        json.dump(magnetism_warning, f, indent=2)
    
    print("\n  RD-MAGNETISM WARNING recorded")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print(f"\nDataset Schema:")
    print(f"  Fields: {list(schema['fields'].keys())}")
    print(f"  Trajectories: {schema['trajectory_count']}")
    print(f"  Timesteps: {schema['timestep_count']}")
    print(f"  Spatial dimensions: {schema['spatial_dimensions']}")
    
    print(f"\nFrames Extracted: {len(frames_data)}")
    
    print(f"\nDescriptor Classification:")
    print(f"  Layer 0: {len(LAYER_0_DESCRIPTORS)} descriptors")
    print(f"  Layer 1a: {len(LAYER_1A_DESCRIPTORS)} descriptors")
    print(f"  Layer 1b: 1 descriptor (component_count)")
    print(f"  Layer 2 (forbidden): {len(FORBIDDEN_TERMS)} terms")
    
    print(f"\nOutput Files:")
    print(f"  {output_dir / 'mhd_schema.json'}")
    print(f"  {output_dir / 'mhd_operational_ledger.json'}")
    print(f"  {output_dir / 'mhd_frame_statistics.json'}")
    print(f"  {output_dir / 'mhd_transport_comparison.json'}")
    print(f"  {output_dir / 'rd_magnetism_warning.json'}")
    
    print("\n" + "=" * 60)
    print("RD-WELL.7A COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
