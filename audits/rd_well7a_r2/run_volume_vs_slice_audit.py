#!/usr/bin/env python3
"""
RD-WELL.7A.R2 — Volume vs Slice Audit

Determine whether measurement behavior survives dimensional reduction.
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

def load_mhd_3d_field(file_path, trajectory_idx=0, frame_idx=0):
    """Load a full 3D field from MHD dataset via fsspec."""
    try:
        with fsspec.open(file_path, "rb") as f, h5py.File(f, "r") as file:
            if 't0_fields' in file:
                fields = file['t0_fields']
                field_names = list(fields.keys())
                
                if field_names:
                    field_name = field_names[0]
                    data = fields[field_name]
                    
                    if trajectory_idx < data.shape[0] and frame_idx < data.shape[1]:
                        frame = data[trajectory_idx, frame_idx]
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
    hist, _ = np.histogram(field_norm, bins=bins, density=True)
    
    # Normalize to probability distribution
    total = hist.sum()
    if total > 0:
        hist = hist / total
    
    # Remove zeros
    hist = hist[hist > 0]
    
    # Compute entropy
    entropy = -np.sum(hist * np.log2(hist + 1e-10))
    
    # Ensure non-negative
    return max(0.0, float(entropy))

def compute_power_spectrum_radial(field):
    """Compute radial power spectrum."""
    # Normalize
    field_norm = normalize_to_01(field)
    
    # Compute FFT
    if field.ndim == 3:
        fft = np.fft.fftn(field_norm)
    else:
        fft = np.fft.fft2(field_norm)
    
    power = np.abs(fft) ** 2
    
    # Shift zero frequency to center
    power_shifted = np.fft.fftshift(power)
    
    # Compute radial profile
    center = np.array(power_shifted.shape) // 2
    
    if field.ndim == 3:
        z, y, x = np.ogrid[:power_shifted.shape[0], :power_shifted.shape[1], :power_shifted.shape[2]]
        r = np.sqrt((x - center[2])**2 + (y - center[1])**2 + (z - center[0])**2)
    else:
        y, x = np.ogrid[:power_shifted.shape[0], :power_shifted.shape[1]]
        r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    
    r_int = r.astype(int)
    max_r = min(power_shifted.shape) // 2
    
    radial_profile = np.zeros(max_r)
    for i in range(max_r):
        mask = r_int == i
        if mask.any():
            radial_profile[i] = power_shifted[mask].mean()
    
    return radial_profile

def compute_component_count_3d(field, threshold=0.5):
    """Compute 3D connected components."""
    # Binarize
    binary = (field > threshold).astype(int)
    
    # Simple connected components (flood fill)
    labeled = np.zeros_like(binary)
    current_label = 0
    
    for i in range(binary.shape[0]):
        for j in range(binary.shape[1]):
            for k in range(binary.shape[2]):
                if binary[i, j, k] == 1 and labeled[i, j, k] == 0:
                    # New component
                    current_label += 1
                    
                    # Flood fill
                    stack = [(i, j, k)]
                    while stack:
                        x, y, z = stack.pop()
                        if (0 <= x < binary.shape[0] and 
                            0 <= y < binary.shape[1] and 
                            0 <= z < binary.shape[2]):
                            if binary[x, y, z] == 1 and labeled[x, y, z] == 0:
                                labeled[x, y, z] = current_label
                                stack.extend([
                                    (x+1, y, z), (x-1, y, z),
                                    (x, y+1, z), (x, y-1, z),
                                    (x, y, z+1), (x, y, z-1)
                                ])
    
    return float(current_label)

def compute_component_count_2d(field, threshold=0.5):
    """Compute 2D connected components."""
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

def main():
    """Run Volume vs Slice Audit."""
    
    # Create output directory
    output_dir = Path('/home/student/sgp_core_v2/audits/rd_well7a_r2')
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("RD-WELL.7A.R2 — Volume vs Slice Audit")
    print("=" * 60)
    
    # Find MHD dataset files
    try:
        fs, _ = fsspec.url_to_fs("hf://datasets/polymathic-ai/mhd_64")
        files = fs.glob("hf://datasets/polymathic-ai/mhd_64/data/test/*.hdf5")
        
        if not files:
            print("  No MHD files found!")
            return
        
        print(f"  Found {len(files)} MHD files")
        
        # Use first file for validation
        file_path = f"hf://{files[0]}"
        
    except Exception as e:
        print(f"  Error finding MHD files: {e}")
        return
    
    # Load 3D field
    print("\nLoading 3D field...")
    field_3d, field_name, field_names = load_mhd_3d_field(file_path, 0, 0)
    
    if field_3d is None:
        print("  Failed to load 3D field")
        return
    
    print(f"  Loaded 3D field: shape={field_3d.shape}, name={field_name}")
    
    # Step A: Compute Descriptors on 3D Volume
    print("\nStep A: Compute Descriptors on 3D Volume")
    print("-" * 40)
    
    volume_descriptors = {
        'mean': float(np.mean(field_3d)),
        'variance': float(np.var(field_3d)),
        'entropy': compute_entropy(field_3d),
        'component_count': compute_component_count_3d(field_3d)
    }
    
    # Compute radial power spectrum
    power_radial_3d = compute_power_spectrum_radial(field_3d)
    volume_descriptors['power_spectrum_peak'] = float(np.argmax(power_radial_3d[1:]) + 1)
    volume_descriptors['power_spectrum_mean'] = float(np.mean(power_radial_3d))
    
    print(f"  mean: {volume_descriptors['mean']:.6f}")
    print(f"  variance: {volume_descriptors['variance']:.6f}")
    print(f"  entropy: {volume_descriptors['entropy']:.6f}")
    print(f"  component_count: {volume_descriptors['component_count']:.0f}")
    print(f"  power_spectrum_peak: {volume_descriptors['power_spectrum_peak']:.0f}")
    print(f"  power_spectrum_mean: {volume_descriptors['power_spectrum_mean']:.6f}")
    
    # Save volume descriptors
    with open(output_dir / 'volume_descriptors.json', 'w') as f:
        json.dump(volume_descriptors, f, indent=2)
    
    print("\n  Volume descriptors saved to volume_descriptors.json")
    
    # Step B: Compute Descriptors on 2D Slices/Projections
    print("\nStep B: Compute Descriptors on 2D Slices/Projections")
    print("-" * 40)
    
    mid_z = field_3d.shape[0] // 2
    mid_y = field_3d.shape[1] // 2
    mid_x = field_3d.shape[2] // 2
    
    slices = {
        'xy_z32': field_3d[mid_z, :, :],
        'xz_y32': field_3d[:, mid_y, :],
        'yz_x32': field_3d[:, :, mid_x],
    }
    
    projections = {
        'mean_z': np.mean(field_3d, axis=0),
        'mean_y': np.mean(field_3d, axis=1),
        'mean_x': np.mean(field_3d, axis=2),
        'max_z': np.max(field_3d, axis=0),
        'max_y': np.max(field_3d, axis=1),
        'max_x': np.max(field_3d, axis=2),
    }
    
    all_slices = {**slices, **projections}
    
    slice_descriptors = {}
    
    for slice_name, slice_data in all_slices.items():
        descriptors = {
            'mean': float(np.mean(slice_data)),
            'variance': float(np.var(slice_data)),
            'entropy': compute_entropy(slice_data),
            'component_count': compute_component_count_2d(slice_data)
        }
        
        # Compute radial power spectrum
        power_radial_2d = compute_power_spectrum_radial(slice_data)
        descriptors['power_spectrum_peak'] = float(np.argmax(power_radial_2d[1:]) + 1)
        descriptors['power_spectrum_mean'] = float(np.mean(power_radial_2d))
        
        slice_descriptors[slice_name] = descriptors
        
        print(f"\n  {slice_name}:")
        print(f"    mean: {descriptors['mean']:.6f}")
        print(f"    variance: {descriptors['variance']:.6f}")
        print(f"    entropy: {descriptors['entropy']:.6f}")
        print(f"    component_count: {descriptors['component_count']:.0f}")
        print(f"    power_spectrum_peak: {descriptors['power_spectrum_peak']:.0f}")
        print(f"    power_spectrum_mean: {descriptors['power_spectrum_mean']:.6f}")
    
    # Save slice descriptors
    with open(output_dir / 'slice_descriptors.json', 'w') as f:
        json.dump(slice_descriptors, f, indent=2)
    
    print("\n  Slice descriptors saved to slice_descriptors.json")
    
    # Step C: Compute Δ_measurement_dimension
    print("\nStep C: Compute Δ_measurement_dimension")
    print("-" * 40)
    
    delta_measurement = {}
    
    for slice_name, descriptors in slice_descriptors.items():
        delta = {}
        for key in volume_descriptors.keys():
            vol_val = volume_descriptors[key]
            slice_val = descriptors[key]
            
            if vol_val != 0:
                delta[key] = {
                    'absolute': abs(vol_val - slice_val),
                    'normalized': abs(vol_val - slice_val) / abs(vol_val)
                }
            else:
                delta[key] = {
                    'absolute': abs(vol_val - slice_val),
                    'normalized': 0.0
                }
        
        delta_measurement[slice_name] = delta
        
        print(f"\n  {slice_name}:")
        for key, values in delta.items():
            print(f"    {key}: Δ={values['absolute']:.6f}, Δ_norm={values['normalized']:.4f}")
    
    # Save delta measurement
    with open(output_dir / 'delta_measurement.json', 'w') as f:
        json.dump(delta_measurement, f, indent=2)
    
    print("\n  Delta measurement saved to delta_measurement.json")
    
    # Step D: Record Hidden Variable Candidates
    print("\nStep D: Record Hidden Variable Candidates")
    print("-" * 40)
    
    hidden_variables = {
        'observer_geometry': {
            'status': 'PLAUSIBLE / UNDER TEST',
            'definition': 'Measurement behavior that depends on the geometric relationship between observer and field.',
            'distinction_from_slice_dependence': {
                'slice_dependence': 'choice of projection',
                'observer_geometry': 'orientation relative to structure'
            }
        },
        'slice_dependence': {
            'status': 'PLAUSIBLE / UNDER TEST',
            'definition': 'Measurement outcomes may depend on how higher-dimensional structures are projected or observed.',
            'generalization': 'Applies to tomography, microscopy, cosmology, neuroscience, plasma diagnostics'
        }
    }
    
    # Save hidden variables
    with open(output_dir / 'hidden_variables.json', 'w') as f:
        json.dump(hidden_variables, f, indent=2)
    
    print("\n  Hidden variable candidates recorded")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print(f"\nVolume Descriptors:")
    for key, value in volume_descriptors.items():
        print(f"  {key}: {value:.6f}")
    
    print(f"\nΔ_measurement_dimension (normalized):")
    for slice_name, delta in delta_measurement.items():
        print(f"\n  {slice_name}:")
        for key, values in delta.items():
            print(f"    {key}: {values['normalized']:.4f}")
    
    print(f"\nHidden Variable Candidates:")
    print(f"  Observer Geometry: {hidden_variables['observer_geometry']['status']}")
    print(f"  Slice Dependence: {hidden_variables['slice_dependence']['status']}")
    
    print(f"\nOutput Files:")
    print(f"  {output_dir / 'volume_descriptors.json'}")
    print(f"  {output_dir / 'slice_descriptors.json'}")
    print(f"  {output_dir / 'delta_measurement.json'}")
    print(f"  {output_dir / 'hidden_variables.json'}")
    
    print("\n" + "=" * 60)
    print("RD-WELL.7A.R2 COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
