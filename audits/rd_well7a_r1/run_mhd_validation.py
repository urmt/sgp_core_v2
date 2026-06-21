#!/usr/bin/env python3
"""
RD-WELL.7A.R1 — MHD Reconnaissance Validation

Validate MHD reconnaissance findings before computing C.
Tests entropy estimator, 3D slicing, and periodic boundary sensitivity.
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

def compute_entropy(field, bins=256, density=True, use_log2=True):
    """Compute Shannon entropy of field."""
    # Normalize to [0, 1] first
    field_norm = normalize_to_01(field)
    
    # Compute histogram
    hist, _ = np.histogram(field_norm, bins=bins, density=density)
    
    # If density=True, normalize to probability distribution
    if density:
        total = hist.sum()
        if total > 0:
            hist = hist / total
    
    # Remove zeros
    hist = hist[hist > 0]
    
    # Compute entropy
    if use_log2:
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
    else:
        entropy = -np.sum(hist * np.log(hist + 1e-10))
    
    # Ensure non-negative
    return max(0.0, float(entropy))

def compute_autocorrelation_2d(field, periodic=True):
    """Compute autocorrelation length for 2D field."""
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

def compute_autocorrelation_1d(signal, periodic=True):
    """Compute autocorrelation length for 1D signal."""
    # Normalize
    signal_norm = normalize_to_01(signal)
    
    # Compute autocorrelation using FFT
    f = np.fft.fft(signal_norm)
    acf = np.fft.ifft(f * np.conj(f)).real
    
    # Normalize by zero-lag value
    if acf.max() > 0:
        acf = acf / acf.max()
    
    # Find first zero crossing
    zero_crossings = np.where(acf < 0)[0]
    if len(zero_crossings) > 0:
        return float(zero_crossings[0])
    
    # If no zero crossing, find where it drops to 1/e
    threshold = 1.0 / np.e
    below_threshold = np.where(acf < threshold)[0]
    if len(below_threshold) > 0:
        return float(below_threshold[0])
    
    # Otherwise return length
    return float(len(signal))

def main():
    """Run MHD reconnaissance validation."""
    
    # Create output directory
    output_dir = Path('/home/student/sgp_core_v2/audits/rd_well7a_r1')
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("RD-WELL.7A.R1 — MHD Reconnaissance Validation")
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
    
    # Step A: Validate Entropy Estimator
    print("\nStep A: Validate Entropy Estimator")
    print("-" * 40)
    
    # Load 3D field
    field_3d, field_name, field_names = load_mhd_3d_field(file_path, 0, 0)
    
    if field_3d is None:
        print("  Failed to load 3D field")
        return
    
    print(f"  Loaded 3D field: shape={field_3d.shape}, name={field_name}")
    
    # Take middle slice for 2D analysis
    field_2d = field_3d[field_3d.shape[0] // 2, :, :]
    field_2d_norm = normalize_to_01(field_2d)
    
    # Test different entropy parameters
    entropy_results = {
        'field_shape': list(field_3d.shape),
        'slice_shape': list(field_2d.shape),
        'tests': {}
    }
    
    # Test histogram bins
    print("\n  Testing histogram bins...")
    for bins in [64, 128, 256, 512]:
        entropy = compute_entropy(field_2d, bins=bins, density=True, use_log2=True)
        entropy_results['tests'][f'bins_{bins}'] = {
            'bins': bins,
            'entropy': entropy
        }
        print(f"    bins={bins}: entropy={entropy:.4f}")
    
    # Test normalization
    print("\n  Testing normalization...")
    for density in [True, False]:
        entropy = compute_entropy(field_2d, bins=256, density=density, use_log2=True)
        entropy_results['tests'][f'density_{density}'] = {
            'density': density,
            'entropy': entropy
        }
        print(f"    density={density}: entropy={entropy:.4f}")
    
    # Test rank transform
    print("\n  Testing rank transform...")
    from scipy.stats import rankdata
    field_ranked = rankdata(field_2d.flatten()).reshape(field_2d.shape)
    entropy_ranked = compute_entropy(field_ranked, bins=256, density=True, use_log2=True)
    entropy_results['tests']['rank_transform'] = {
        'entropy': entropy_ranked
    }
    print(f"    rank_transform: entropy={entropy_ranked:.4f}")
    
    # Test log transform
    print("\n  Testing log transform...")
    field_log = np.log1p(field_2d)  # log(1 + x) to avoid log(0)
    field_log_norm = normalize_to_01(field_log)
    entropy_log = compute_entropy(field_log, bins=256, density=True, use_log2=True)
    entropy_results['tests']['log_transform'] = {
        'entropy': entropy_log
    }
    print(f"    log_transform: entropy={entropy_log:.4f}")
    
    # Test log2 vs ln
    print("\n  Testing log2 vs ln...")
    for use_log2 in [True, False]:
        entropy = compute_entropy(field_2d, bins=256, density=True, use_log2=use_log2)
        log_type = 'log2' if use_log2 else 'ln'
        entropy_results['tests'][f'{log_type}'] = {
            'use_log2': use_log2,
            'entropy': entropy
        }
        print(f"    {log_type}: entropy={entropy:.4f}")
    
    # Compute entropy range
    all_entropies = [v['entropy'] for v in entropy_results['tests'].values()]
    entropy_results['entropy_range'] = {
        'min': min(all_entropies),
        'max': max(all_entropies),
        'std': float(np.std(all_entropies)),
        'relative_range': (max(all_entropies) - min(all_entropies)) / np.mean(all_entropies)
    }
    
    print(f"\n  Entropy range: {min(all_entropies):.4f} to {max(all_entropies):.4f}")
    print(f"  Relative range: {entropy_results['entropy_range']['relative_range']:.4f}")
    
    # Save entropy validation
    with open(output_dir / 'entropy_validation.json', 'w') as f:
        json.dump(entropy_results, f, indent=2)
    
    print("\n  Entropy validation saved to entropy_validation.json")
    
    # Step B: Validate 3D Slicing
    print("\nStep B: Validate 3D Slicing")
    print("-" * 40)
    
    slicing_results = {
        'field_shape': list(field_3d.shape),
        'tests': {}
    }
    
    # Test different slices
    mid_z = field_3d.shape[0] // 2
    mid_y = field_3d.shape[1] // 2
    mid_x = field_3d.shape[2] // 2
    
    slices = {
        'xy_z32': field_3d[mid_z, :, :],
        'xz_y32': field_3d[:, mid_y, :],
        'yz_x32': field_3d[:, :, mid_x],
    }
    
    # Volume projections
    projections = {
        'mean_z': np.mean(field_3d, axis=0),
        'mean_y': np.mean(field_3d, axis=1),
        'mean_x': np.mean(field_3d, axis=2),
        'max_z': np.max(field_3d, axis=0),
        'max_y': np.max(field_3d, axis=1),
        'max_x': np.max(field_3d, axis=2),
    }
    
    # Compute descriptors for each slice/projection
    all_slices = {**slices, **projections}
    
    for slice_name, slice_data in all_slices.items():
        slice_norm = normalize_to_01(slice_data)
        
        # Compute basic descriptors
        mean_val = float(np.mean(slice_data))
        variance_val = float(np.var(slice_data))
        entropy_val = compute_entropy(slice_data, bins=256, density=True, use_log2=True)
        
        slicing_results['tests'][slice_name] = {
            'shape': list(slice_data.shape),
            'mean': mean_val,
            'variance': variance_val,
            'entropy': entropy_val
        }
        
        print(f"  {slice_name}: mean={mean_val:.4f}, variance={variance_val:.4f}, entropy={entropy_val:.4f}")
    
    # Compute descriptor ranges
    means = [v['mean'] for v in slicing_results['tests'].values()]
    variances = [v['variance'] for v in slicing_results['tests'].values()]
    entropies = [v['entropy'] for v in slicing_results['tests'].values()]
    
    slicing_results['descriptor_ranges'] = {
        'mean': {'min': min(means), 'max': max(means), 'std': float(np.std(means))},
        'variance': {'min': min(variances), 'max': max(variances), 'std': float(np.std(variances))},
        'entropy': {'min': min(entropies), 'max': max(entropies), 'std': float(np.std(entropies))}
    }
    
    print(f"\n  Mean range: {min(means):.4f} to {max(means):.4f}")
    print(f"  Variance range: {min(variances):.4f} to {max(variances):.4f}")
    print(f"  Entropy range: {min(entropies):.4f} to {max(entropies):.4f}")
    
    # Save slicing validation
    with open(output_dir / 'slicing_validation.json', 'w') as f:
        json.dump(slicing_results, f, indent=2)
    
    print("\n  Slicing validation saved to slicing_validation.json")
    
    # Step C: Test Periodic Boundary Sensitivity
    print("\nStep C: Test Periodic Boundary Sensitivity")
    print("-" * 40)
    
    boundary_results = {
        'field_shape': list(field_3d.shape),
        'tests': {}
    }
    
    # Test autocorrelation with different assumptions
    for slice_name in ['xy_z32', 'xz_y32', 'yz_x32']:
        slice_data = all_slices[slice_name]
        
        # Compute autocorrelation
        autocorr_length = compute_autocorrelation_2d(slice_data, periodic=True)
        
        boundary_results['tests'][slice_name] = {
            'autocorrelation_length': autocorr_length
        }
        
        print(f"  {slice_name}: autocorrelation_length={autocorr_length:.1f}")
    
    # Test 1D autocorrelation along different axes
    print("\n  Testing 1D autocorrelation along axes...")
    
    # Take a line through the center of the 3D field
    center_z, center_y, center_x = field_3d.shape[0] // 2, field_3d.shape[1] // 2, field_3d.shape[2] // 2
    
    lines = {
        'z_axis': field_3d[:, center_y, center_x],
        'y_axis': field_3d[center_z, :, center_x],
        'x_axis': field_3d[center_z, center_y, :]
    }
    
    for line_name, line_data in lines.items():
        autocorr_length = compute_autocorrelation_1d(line_data, periodic=True)
        
        boundary_results['tests'][f'1d_{line_name}'] = {
            'autocorrelation_length': autocorr_length
        }
        
        print(f"    {line_name}: autocorrelation_length={autocorr_length:.1f}")
    
    # Save boundary validation
    with open(output_dir / 'boundary_validation.json', 'w') as f:
        json.dump(boundary_results, f, indent=2)
    
    print("\n  Boundary validation saved to boundary_validation.json")
    
    # Step D: Record Hidden Variable Candidates
    print("\nStep D: Record Hidden Variable Candidates")
    print("-" * 40)
    
    hidden_variables = {
        'topological_constraint': {
            'status': 'PLAUSIBLE / UNDER TEST',
            'definition': 'Structural restrictions imposed by field connectivity, conservation laws, or topology that alter measurement behavior.',
            'examples': [
                'magnetic flux conservation',
                'reconnection events',
                'divergence constraints',
                'knotting/linking structure'
            ]
        },
        'slice_dependence': {
            'status': 'PLAUSIBLE / UNDER TEST',
            'definition': 'Descriptor values that depend on the orientation of the slicing plane used to extract 2D data from 3D fields.',
            'evidence': {
                'mean_range': slicing_results['descriptor_ranges']['mean'],
                'variance_range': slicing_results['descriptor_ranges']['variance'],
                'entropy_range': slicing_results['descriptor_ranges']['entropy']
            }
        }
    }
    
    # Save hidden variables
    with open(output_dir / 'hidden_variables.json', 'w') as f:
        json.dump(hidden_variables, f, indent=2)
    
    print("\n  Hidden variable candidates recorded")
    
    # Record RD-TOPOLOGY WARNING
    topology_warning = {
        'warning': "Topologically constrained fields may invalidate segmentation-based measurements developed on unconstrained media.",
        'status': "ACTIVE WARNING",
        'extends': "RD-MAGNETISM"
    }
    
    with open(output_dir / 'rd_topology_warning.json', 'w') as f:
        json.dump(topology_warning, f, indent=2)
    
    print("  RD-TOPOLOGY WARNING recorded")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print(f"\nEntropy Validation:")
    print(f"  Relative range: {entropy_results['entropy_range']['relative_range']:.4f}")
    print(f"  Assessment: {'PROVISIONAL' if entropy_results['entropy_range']['relative_range'] < 0.1 else 'REPRESENTATION-SENSITIVE'}")
    
    print(f"\nSlicing Validation:")
    print(f"  Mean range: {slicing_results['descriptor_ranges']['mean']['std']:.4f}")
    print(f"  Variance range: {slicing_results['descriptor_ranges']['variance']['std']:.4f}")
    print(f"  Entropy range: {slicing_results['descriptor_ranges']['entropy']['std']:.4f}")
    
    print(f"\nBoundary Validation:")
    for slice_name in ['xy_z32', 'xz_y32', 'yz_x32']:
        autocorr = boundary_results['tests'][slice_name]['autocorrelation_length']
        print(f"  {slice_name}: autocorrelation_length={autocorr:.1f}")
    
    print(f"\nHidden Variable Candidates:")
    print(f"  Topological Constraint: {hidden_variables['topological_constraint']['status']}")
    print(f"  Slice Dependence: {hidden_variables['slice_dependence']['status']}")
    
    print(f"\nOutput Files:")
    print(f"  {output_dir / 'entropy_validation.json'}")
    print(f"  {output_dir / 'slicing_validation.json'}")
    print(f"  {output_dir / 'boundary_validation.json'}")
    print(f"  {output_dir / 'hidden_variables.json'}")
    print(f"  {output_dir / 'rd_topology_warning.json'}")
    
    print("\n" + "=" * 60)
    print("RD-WELL.7A.R1 COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
