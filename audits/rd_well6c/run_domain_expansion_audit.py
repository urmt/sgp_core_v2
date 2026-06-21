#!/usr/bin/env python3
"""
RD-WELL.6C: Domain Expansion Audit

Compute only:
  C(domain)
  ΔC_transform
  descriptor transport

for additional domains.

No coupling. No theories.
Just: Does C remain computable? How sensitive is it?

Why: SR-30 becomes dramatically stronger when domains increase.
"""

import sys
import os
import numpy as np
import json
from pathlib import Path

# Add the metrics directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "coherence-benchmark"))

def load_hdf5_frame(file_path, field_name, trajectory_idx=0, frame_idx=0):
    """Load a single frame from an HDF5 file via fsspec."""
    import fsspec
    import h5py
    
    # Compose the path to the dataset on HF hub
    if not file_path.startswith("hf://"):
        # Check if the path already contains "datasets/polymathic-ai/"
        if file_path.startswith("datasets/polymathic-ai/"):
            file_path = f"hf://{file_path}"
        else:
            file_path = f"hf://datasets/polymathic-ai/{file_path}"
    
    try:
        with fsspec.open(file_path, "rb") as f, h5py.File(f, "r") as file:
            # Try different field name patterns
            if 't0_fields' in file:
                fields = file['t0_fields']
                if field_name in fields:
                    data = fields[field_name]
                    # Data shape is typically (n_trajectories, n_steps, [depth,] height, width)
                    if trajectory_idx < data.shape[0] and frame_idx < data.shape[1]:
                        frame = data[trajectory_idx, frame_idx]
                        # If 3D (depth, height, width), take middle slice
                        if frame.ndim == 3:
                            mid_slice = frame.shape[0] // 2
                            return frame[mid_slice, :, :]
                        return frame
            elif 'fields' in file:
                fields = file['fields']
                if field_name in fields:
                    data = fields[field_name]
                    # Data shape is typically (n_steps, [depth,] height, width)
                    if frame_idx < data.shape[0]:
                        frame = data[frame_idx]
                        # If 3D (depth, height, width), take middle slice
                        if frame.ndim == 3:
                            mid_slice = frame.shape[0] // 2
                            return frame[mid_slice, :, :]
                        return frame
            elif 't1_fields' in file:
                fields = file['t1_fields']
                if field_name in fields:
                    data = fields[field_name]
                    # Data shape is typically (n_trajectories, n_steps, [depth,] height, width)
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

def normalize_to_01(field):
    """Normalize field to [0, 1] range."""
    field_min = np.min(field)
    field_max = np.max(field)
    if field_max - field_min < 1e-10:
        return np.zeros_like(field)
    return (field - field_min) / (field_max - field_min)

def compute_C(field_2d):
    """Compute C (Total Correlation) for a 2D field."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "coherence-benchmark"))
    from metrics.total_correlation import compute_C
    return compute_C(field_2d)

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

def main():
    print("=" * 60)
    print("RD-WELL.6C — Domain Expansion Audit")
    print("=" * 60)
    print()
    print("Compute only:")
    print("  C(domain)")
    print("  ΔC_transform")
    print("  descriptor transport")
    print()
    print("No coupling. No theories.")
    print("Just: Does C remain computable? How sensitive is it?")
    print()

    # Define transforms
    transforms = ['original', 'zscore', 'rank', 'minmax']

    results = {}

    # Define datasets to test: (dataset_name, field_name, trajectory_idx, frame_idx)
    datasets = [
        ("gray_scott_reaction_diffusion", "B", 0, 500),  # B field for Gray-Scott
        ("rayleigh_benard", "buoyancy", 0, 0),
        ("active_matter", "concentration", 0, 0),
        ("rayleigh_taylor_instability", "density", 0, 0),
        ("MHD_64", "density", 0, 0),
        ("acoustic_scattering_discontinuous", "pressure", 0, 0),
    ]

    for dataset_name, field_name, trajectory_idx, frame_idx in datasets:
        print("=" * 60)
        print(f"{dataset_name} (NEW DOMAIN)" if dataset_name not in ["gray_scott_reaction_diffusion", "rayleigh_benard", "active_matter"] else f"{dataset_name} (baseline)")
        print("=" * 60)
        try:
            dataset_results = {}
            for transform in transforms:
                try:
                    # Try to load from Hugging Face hub
                    # First, find a valid file in the dataset
                    import fsspec
                    fs, _ = fsspec.url_to_fs(f"hf://datasets/polymathic-ai/{dataset_name}")
                    files = fs.glob(f"hf://datasets/polymathic-ai/{dataset_name}/data/test/*.hdf5")
                    
                    if files:
                        # Use the first file
                        file_path = files[0]
                        # Convert to the format expected by load_hdf5_frame
                        file_path = file_path.replace("hf://datasets/polymathic-ai/", "")
                        field_data = load_hdf5_frame(file_path, field_name, trajectory_idx, frame_idx)
                        
                        if field_data is not None:
                            # Handle 3D data by taking middle slice
                            if field_data.ndim == 3:
                                mid_slice = field_data.shape[0] // 2
                                field_2d = field_data[mid_slice, :, :]
                            else:
                                field_2d = field_data
                            
                            field = normalize_to_01(field_2d)
                            field_transformed = apply_transform(field, transform)
                            C = compute_C(field_transformed)
                            dataset_results[transform] = {'C': float(C)}
                            print(f"  {transform}: C = {C:.6f}")
                        else:
                            print(f"  {transform}: Field not found")
                    else:
                        print(f"  {transform}: No files found in dataset")
                except Exception as e:
                    print(f"  {transform}: Error - {e}")
            
            results[dataset_name] = dataset_results
        except Exception as e:
            print(f"  Error: {e}")
        print()

    # --- Compute ΔC for each domain ---
    print("=" * 60)
    print("ΔC (sensitivity to transforms)")
    print("=" * 60)
    for domain, domain_results in results.items():
        if 'original' in domain_results and domain_results['original'] is not None:
            C_original = domain_results['original']['C']
            print(f"\n  {domain}:")
            for transform in transforms:
                if transform in domain_results and domain_results[transform] is not None:
                    C_transform = domain_results[transform]['C']
                    delta_C = abs(C_transform - C_original)
                    print(f"    ΔC_{transform} = {delta_C:.6f}")
    print()

    # --- Summary ---
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
        if 'original' in domain_results and domain_results['original'] is not None:
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
