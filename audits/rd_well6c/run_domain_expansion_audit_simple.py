#!/usr/bin/env python3
"""
RD-WELL.6C: Domain Expansion Audit (Simplified)

Compute only:
  C(domain)
  Delta C_transform

for additional domains.

No coupling. No theories.
Just: Does C remain computable? How sensitive is it?
"""

import sys
import os
import numpy as np
import json
from pathlib import Path

# Add the metrics directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "coherence-benchmark"))

def normalize_to_01(field):
    """Normalize field to [0, 1] range."""
    field_min = np.min(field)
    field_max = np.max(field)
    if field_max - field_min < 1e-10:
        return np.zeros_like(field)
    return (field - field_min) / (field_max - field_min)

def apply_transform(field, transform):
    """Apply a transform to a field."""
    if transform == 'original':
        return field
    elif transform == 'zscore':
        mean = np.mean(field)
        std = np.std(field)
        if std < 1e-10:
            return np.zeros_like(field)
        return (field - mean) / std
    elif transform == 'rank':
        from scipy.stats import rankdata
        return rankdata(field.flatten(), method='average').reshape(field.shape)
    elif transform == 'minmax':
        return normalize_to_01(field)
    else:
        raise ValueError(f"Unknown transform: {transform}")

def load_hdf5_frame(file_path, field_name, trajectory_idx=0, frame_idx=0):
    """Load a single frame from an HDF5 file via fsspec."""
    import fsspec
    import h5py
    
    try:
        with fsspec.open(file_path, "rb") as f, h5py.File(f, "r") as file:
            if 't0_fields' in file:
                fields = file['t0_fields']
                if field_name in fields:
                    data = fields[field_name]
                    if trajectory_idx < data.shape[0] and frame_idx < data.shape[1]:
                        frame = data[trajectory_idx, frame_idx]
                        # If 3D (depth, height, width), take middle slice
                        if frame.ndim == 3:
                            mid_slice = frame.shape[0] // 2
                            return frame[mid_slice, :, :]
                        return frame
    except Exception as e:
        print(f"    Error loading {file_path}: {e}")
    
    return None

def main():
    print("=" * 60)
    print("RD-WELL.6C — Domain Expansion Audit (Simplified)")
    print("=" * 60)
    print()
    print("Compute only:")
    print("  C(domain)")
    print("  Delta C_transform")
    print()
    print("No coupling. No theories.")
    print("Just: Does C remain computable? How sensitive is it?")
    print()

    # Define transforms
    transforms = ['original', 'zscore', 'rank', 'minmax']

    # Define datasets to test: (dataset_name, field_name, trajectory_idx, frame_idx)
    datasets = [
        ("gray_scott_reaction_diffusion", "B", 0, 500),
        ("rayleigh_benard", "buoyancy", 0, 0),
        ("active_matter", "concentration", 0, 0),
        ("rayleigh_taylor_instability", "density", 0, 0),
        ("MHD_64", "density", 0, 0),
        ("acoustic_scattering_discontinuous", "pressure", 0, 0),
    ]

    results = {}

    for dataset_name, field_name, trajectory_idx, frame_idx in datasets:
        print("=" * 60)
        print(f"{dataset_name}")
        print("=" * 60)
        try:
            # Find a file
            import fsspec
            fs, _ = fsspec.url_to_fs(f"hf://datasets/polymathic-ai/{dataset_name}")
            files = fs.glob(f"hf://datasets/polymathic-ai/{dataset_name}/data/test/*.hdf5")
            
            if files:
                # Get the relative path (already includes datasets/polymathic-ai/)
                relative_path = files[0]
                # Prepend just 'hf://'
                file_path = f"hf://{relative_path}"
                
                dataset_results = {}
                for transform in transforms:
                    field = load_hdf5_frame(file_path, field_name, trajectory_idx, frame_idx)
                    if field is not None:
                        field_transformed = apply_transform(field, transform)
                        from metrics.total_correlation import compute_C
                        C = compute_C(field_transformed)
                        dataset_results[transform] = {'C': float(C)}
                        print(f"  {transform}: C = {C:.6f}")
                    else:
                        print(f"  {transform}: Field not found")
                
                results[dataset_name] = dataset_results
            else:
                print(f"  No files found")
        except Exception as e:
            print(f"  Error: {e}")
        print()

    # Compute Delta C
    print("=" * 60)
    print("Delta C (sensitivity to transforms)")
    print("=" * 60)
    for domain, domain_results in results.items():
        if 'original' in domain_results:
            C_original = domain_results['original']['C']
            print(f"\n  {domain}:")
            for transform in transforms:
                if transform in domain_results:
                    C_transform = domain_results[transform]['C']
                    delta_C = abs(C_transform - C_original)
                    print(f"    Delta C_{transform} = {delta_C:.6f}")
    print()

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("Domains tested:")
    for domain in results.keys():
        print(f"  - {domain}")
    print()
    print("C values (original):")
    for domain, domain_results in results.items():
        if 'original' in domain_results:
            C = domain_results['original']['C']
            print(f"  {domain}: C = {C:.6f}")
    print()

    # Save results
    output_file = Path(__file__).parent / "domain_expansion_audit.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_file}")

if __name__ == "__main__":
    main()
