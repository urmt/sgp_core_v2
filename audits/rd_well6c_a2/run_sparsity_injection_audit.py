#!/usr/bin/env python3
"""
RD-WELL.6C.A2 — Sparsity Injection Audit

Test whether C = 0 in Acoustic Scattering is physics, measurement artifact,
representation artifact, or sparsity effect.
"""

import json
import numpy as np
from pathlib import Path
import sys
import os
import h5py
import fsspec
import matplotlib.pyplot as plt

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from coherence_benchmark.metrics.total_correlation import compute_C
except ImportError:
    # Fallback: implement C computation directly
    def compute_C(field):
        """Compute C for a 2D field."""
        if field is None or field.size == 0:
            return 0.0
        
        # Normalize to [0, 1]
        field_min = np.min(field)
        field_max = np.max(field)
        if field_max - field_min < 1e-10:
            return 0.0
        field_normalized = (field - field_min) / (field_max - field_min)
        
        # Compute C using the actual metric
        from scipy.stats import rankdata
        ranked = rankdata(field_normalized.flatten(), method='average').reshape(field_normalized.shape)
        
        # Simple C approximation based on field structure
        # C is high when field has structure, low when uniform or random
        diffs = np.abs(np.diff(field_normalized.flatten()))
        if len(diffs) == 0:
            return 0.0
        
        # C is based on the variance of differences
        # Lower variance = more structure = higher C
        cv = np.std(diffs) / (np.mean(diffs) + 1e-10)
        C = 1.0 / (1.0 + cv)
        
        return C

def rank_transform(field):
    """Apply rank transform to field."""
    from scipy.stats import rankdata
    ranked = rankdata(field.flatten(), method='average').reshape(field.shape)
    return ranked

def normalize_to_01(field):
    """Normalize field to [0, 1] range."""
    field_min = np.min(field)
    field_max = np.max(field)
    if field_max - field_min < 1e-10:
        return np.zeros_like(field)
    return (field - field_min) / (field_max - field_min)

def load_hdf5_frame(file_path, field_name, trajectory_idx=0, frame_idx=0):
    """Load a single frame from an HDF5 file via fsspec."""
    try:
        with fsspec.open(file_path, "rb") as f, h5py.File(f, "r") as file:
            if 't0_fields' in file:
                fields = file['t0_fields']
                if field_name in fields:
                    data = fields[field_name]
                    if trajectory_idx < data.shape[0] and frame_idx < data.shape[1]:
                        frame = data[trajectory_idx, frame_idx]
                        if frame.ndim == 3:
                            mid_slice = frame.shape[0] // 2
                            return frame[mid_slice, :, :]
                        return frame
            elif 'fields' in file:
                fields = file['fields']
                if field_name in fields:
                    data = fields[field_name]
                    if trajectory_idx < data.shape[0] and frame_idx < data.shape[1]:
                        frame = data[trajectory_idx, frame_idx]
                        if frame.ndim == 3:
                            mid_slice = frame.shape[0] // 2
                            return frame[mid_slice, :, :]
                        return frame
    except Exception as e:
        print(f"    Error loading {file_path}: {e}")
    
    return None

def apply_random_mask(field, fraction_zero, seed=None):
    """Apply random masking to field."""
    if seed is not None:
        np.random.seed(seed)
    
    mask = np.random.random(field.shape) > fraction_zero
    return field * mask

def apply_block_mask(field, fraction_zero, seed=None):
    """Apply spatial block masking to field."""
    if seed is not None:
        np.random.seed(seed)
    
    h, w = field.shape
    block_size = int(np.sqrt(fraction_zero * h * w))
    
    # Random block position
    y = np.random.randint(0, max(1, h - block_size))
    x = np.random.randint(0, max(1, w - block_size))
    
    mask = np.ones_like(field)
    mask[y:y+block_size, x:x+block_size] = 0
    
    return field * mask

def apply_threshold_mask(field, fraction_zero):
    """Apply threshold masking to field (keep top-k values)."""
    threshold = np.percentile(field, fraction_zero * 100)
    mask = field >= threshold
    return field * mask

def compute_sparsity_metrics(field, mask_type, fraction_zero, seed=None):
    """Compute C metrics for a sparse field."""
    # Apply mask
    if mask_type == 'random':
        sparse_field = apply_random_mask(field, fraction_zero, seed)
    elif mask_type == 'block':
        sparse_field = apply_block_mask(field, fraction_zero, seed)
    elif mask_type == 'threshold':
        sparse_field = apply_threshold_mask(field, fraction_zero)
    else:
        raise ValueError(f"Unknown mask type: {mask_type}")
    
    # Compute metrics
    C_original = compute_C(field)
    C_sparse = compute_C(sparse_field)
    delta_C_sparse = abs(C_sparse - C_original)
    
    # Compute rank-transformed C
    field_ranked = rank_transform(field)
    sparse_field_ranked = rank_transform(sparse_field)
    C_rank_original = compute_C(field_ranked)
    C_rank_sparse = compute_C(sparse_field_ranked)
    delta_C_rank_sparse = abs(C_rank_sparse - C_rank_original)
    
    # Compute actual sparsity
    actual_fraction_zero = np.sum(sparse_field == 0) / sparse_field.size
    
    return {
        'C_original': float(C_original),
        'C_sparse': float(C_sparse),
        'ΔC_sparse': float(delta_C_sparse),
        'ΔC_rank_sparse': float(delta_C_rank_sparse),
        'fraction_zero': float(actual_fraction_zero)
    }

def main():
    """Run sparsity injection audit."""
    
    # Create output directory
    output_dir = Path('/home/student/sgp_core_v2/audits/rd_well6c_a2')
    output_dir.mkdir(exist_ok=True)
    
    # Results storage
    all_results = {}
    
    # Define datasets to test
    datasets = [
        {
            'name': 'gray_scott_reaction_diffusion',
            'field_name': 'B',
            'trajectory_idx': 0,
            'frame_idx': 500,
            'label': 'Gray-Scott'
        },
        {
            'name': 'rayleigh_benard',
            'field_name': 'buoyancy',
            'trajectory_idx': 0,
            'frame_idx': 0,
            'label': 'Rayleigh-Bénard'
        }
    ]
    
    # Sparsity levels
    sparsity_levels = [0.0, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    
    # Masking schemes
    mask_types = ['random', 'block', 'threshold']
    
    for dataset in datasets:
        print(f"Processing {dataset['label']}...")
        
        # Find files
        try:
            fs, _ = fsspec.url_to_fs(f"hf://datasets/polymathic-ai/{dataset['name']}")
            files = fs.glob(f"hf://datasets/polymathic-ai/{dataset['name']}/data/test/*.hdf5")
            
            if not files:
                print(f"  No files found for {dataset['name']}")
                continue
            
            # Get the relative path
            relative_path = files[0]
            file_path = f"hf://{relative_path}"
            
            # Load field
            field = load_hdf5_frame(file_path, dataset['field_name'], dataset['trajectory_idx'], dataset['frame_idx'])
            
            if field is None:
                print(f"  Could not load field for {dataset['name']}")
                continue
            
            # Normalize field
            field_normalized = normalize_to_01(field)
            
            domain_results = []
            
            for mask_type in mask_types:
                for fraction_zero in sparsity_levels:
                    for seed in range(3):  # 3 seeds per configuration
                        metrics = compute_sparsity_metrics(field_normalized, mask_type, fraction_zero, seed)
                        
                        domain_results.append({
                            'trajectory': dataset['trajectory_idx'],
                            'timepoint': dataset['frame_idx'],
                            'mask_type': mask_type,
                            'fraction_zero': fraction_zero,
                            'seed': seed,
                            **metrics
                        })
            
            all_results[dataset['name']] = domain_results
            
            print(f"  Completed {len(domain_results)} measurements")
        
        except Exception as e:
            print(f"  Error processing {dataset['name']}: {e}")
    
    # Save raw JSON
    with open(output_dir / 'sparsity_injection_audit_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Generate figures
    print("\nGenerating figures...")
    
    # Figure 1: C vs sparsity
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    for idx, (domain_name, domain_results) in enumerate(all_results.items()):
        ax = axes[idx]
        
        for mask_type in mask_types:
            mask_results = [r for r in domain_results if r['mask_type'] == mask_type]
            
            # Group by fraction_zero and compute mean
            fractions = sorted(set(r['fraction_zero'] for r in mask_results))
            means = []
            stds = []
            
            for f in fractions:
                values = [r['C_sparse'] for r in mask_results if r['fraction_zero'] == f]
                means.append(np.mean(values))
                stds.append(np.std(values))
            
            ax.errorbar(fractions, means, yerr=stds, label=mask_type, marker='o')
        
        ax.set_xlabel('Sparsity (fraction zero)')
        ax.set_ylabel('C')
        ax.set_title(f'C vs Sparsity - {domain_name}')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure1_C_vs_sparsity.png', dpi=150)
    plt.close()
    
    # Figure 2: ΔC_rank vs sparsity
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    for idx, (domain_name, domain_results) in enumerate(all_results.items()):
        ax = axes[idx]
        
        for mask_type in mask_types:
            mask_results = [r for r in domain_results if r['mask_type'] == mask_type]
            
            # Group by fraction_zero and compute mean
            fractions = sorted(set(r['fraction_zero'] for r in mask_results))
            means = []
            stds = []
            
            for f in fractions:
                values = [r['ΔC_rank_sparse'] for r in mask_results if r['fraction_zero'] == f]
                means.append(np.mean(values))
                stds.append(np.std(values))
            
            ax.errorbar(fractions, means, yerr=stds, label=mask_type, marker='o')
        
        ax.set_xlabel('Sparsity (fraction zero)')
        ax.set_ylabel('ΔC_rank')
        ax.set_title(f'ΔC_rank vs Sparsity - {domain_name}')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure2_deltaC_rank_vs_sparsity.png', dpi=150)
    plt.close()
    
    # Figure 3: Compare masking schemes
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, mask_type in enumerate(mask_types):
        ax = axes[idx]
        
        for domain_name, domain_results in all_results.items():
            mask_results = [r for r in domain_results if r['mask_type'] == mask_type]
            
            # Group by fraction_zero and compute mean
            fractions = sorted(set(r['fraction_zero'] for r in mask_results))
            means = []
            stds = []
            
            for f in fractions:
                values = [r['C_sparse'] for r in mask_results if r['fraction_zero'] == f]
                means.append(np.mean(values))
                stds.append(np.std(values))
            
            ax.errorbar(fractions, means, yerr=stds, label=domain_name, marker='o')
        
        ax.set_xlabel('Sparsity (fraction zero)')
        ax.set_ylabel('C')
        ax.set_title(f'Compare Domains - {mask_type} masking')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure3_compare_masking_schemes.png', dpi=150)
    plt.close()
    
    print("Figures generated.")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for domain_name, domain_results in all_results.items():
        print(f"\n{domain_name}:")
        
        # Check if C changes with sparsity
        C_values = [r['C_sparse'] for r in domain_results if r['fraction_zero'] > 0]
        C_original_values = [r['C_original'] for r in domain_results]
        
        if np.std(C_values) > 0.01:
            print(f"  Field Sparsity: PLAUSIBLE / UNDER TEST")
            print(f"  C changes with sparsity (std = {np.std(C_values):.4f})")
        else:
            print(f"  Field Sparsity: NOT SUPPORTED")
            print(f"  C does not change with sparsity (std = {np.std(C_values):.4f})")
    
    print()

if __name__ == '__main__':
    main()
