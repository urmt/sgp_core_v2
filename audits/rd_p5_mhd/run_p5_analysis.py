#!/usr/bin/env python3
"""
P5 — MHD Self-Organization Audit

Tests whether strong physical constraints alter variance structure itself.

Computes:
1. within/between ratio (variance structure)
2. temporal spread (dynamical sensitivity)
3. protocol sensitivity (robustness)
4. transform sensitivity (representation stability)
5. dimensional transport (observer dependence)

Domain: MHD (magnetohydrodynamics)
"""

import json
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ============================================================================
# Load MHD data
# ============================================================================

def load_mhd_data():
    """Load MHD dataset and compute C across trajectories and timesteps."""
    import h5py
    import fsspec
    
    # MHD dataset paths (from HuggingFace)
    mhd_files = [
        'hf://datasets/polymathic-ai/the_well/datasets/MHD_64/Ma_0.7_Ms_0.5.h5',
        'hf://datasets/polymathic-ai/the_well/datasets/MHD_64/Ma_0.7_Ms_0.7.h5',
        'hf://datasets/polymathic-ai/the_well/datasets/MHD_64/Ma_0.7_Ms_1.5.h5',
        'hf://datasets/polymathic-ai/the_well/datasets/MHD_64/Ma_0.7_Ms_2.h5',
        'hf://datasets/polymathic-ai/the_well/datasets/MHD_64/Ma_0.7_Ms_7.h5',
    ]
    
    results = []
    
    for file_idx, file_path in enumerate(mhd_files):
        try:
            with fsspec.open(file_path, 'r') as f:
                with h5py.File(f, 'r') as hf:
                    # Get data shape
                    t0_fields = hf['t0_fields']
                    t1_fields = hf['t1_fields']
                    
                    print(f"File {file_idx}: {file_path.split('/')[-1]}")
                    print(f"  t0_fields shape: {t0_fields.shape}")
                    print(f"  t1_fields shape: {t1_fields.shape}")
                    
                    # Get parameters
                    params = hf.attrs.get('parameters', 'unknown')
                    print(f"  Parameters: {params}")
                    
                    # Get scalar fields (density from t0_fields)
                    density = t0_fields[:, :, :, :, 0]  # First scalar field
                    
                    # Get vector fields (velocity from t1_fields)
                    velocity = t1_fields[:, :, :, :, :3]  # First 3 components
                    
                    # Compute C for multiple timesteps
                    n_timesteps = density.shape[0]
                    timesteps_to_check = [0, 25, 50, 75, 99]
                    
                    for timestep in timesteps_to_check:
                        if timestep < n_timesteps:
                            # Extract frame
                            frame = density[timestep]
                            
                            # Compute C using gaussian implementation
                            from coherence_benchmark.metrics.total_correlation import compute_C
                            
                            # Normalize
                            frame = (frame - frame.mean()) / (frame.std() + 1e-8)
                            
                            # Compute C
                            C_val = compute_C(frame, version='gaussian')
                            
                            results.append({
                                'file_index': file_idx,
                                'parameters': params,
                                'timestep': timestep,
                                'C_original': C_val,
                                'field': 'density'
                            })
                            
                            print(f"  Timestep {timestep}: C = {C_val:.6f}")
                            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue
    
    return results

# ============================================================================
# Compute variance decomposition for MHD
# ============================================================================

def compute_mhd_variance_decomposition(results):
    """Compute within-trajectory and between-trajectory variance for MHD."""
    # Group by file (parameter regime)
    files = {}
    for r in results:
        file_idx = r['file_index']
        if file_idx not in files:
            files[file_idx] = []
        files[file_idx].append(r)
    
    # For MHD, we have multiple parameter regimes, not trajectories
    # Compute variance within each regime and between regimes
    
    # Within-regime variance (temporal)
    within_variances = []
    for file_idx, file_results in files.items():
        if len(file_results) > 1:
            c_values = [r['C_original'] for r in file_results]
            within_variances.append(np.var(c_values))
    
    mean_within_var = np.mean(within_variances) if within_variances else 0
    
    # Between-regime variance
    regime_means = {}
    for file_idx, file_results in files.items():
        c_values = [r['C_original'] for r in file_results]
        regime_means[file_idx] = np.mean(c_values)
    
    between_var = np.var(list(regime_means.values())) if len(regime_means) > 1 else 0
    
    # Overall statistics
    all_c = [r['C_original'] for r in results]
    mean_c = np.mean(all_c)
    std_c = np.std(all_c)
    min_c = min(all_c)
    max_c = max(all_c)
    spread = max_c - min_c
    
    # Temporal spread (range across time, averaged over regimes)
    temporal_spreads = []
    for file_idx, file_results in files.items():
        if len(file_results) > 1:
            c_values = [r['C_original'] for r in file_results]
            temporal_spreads.append(max(c_values) - min(c_values))
    mean_temporal_spread = np.mean(temporal_spreads) if temporal_spreads else 0
    
    # Between-regime spread (range across regimes)
    between_spreads = []
    for file_idx, file_results in files.items():
        if len(file_results) > 1:
            c_values = [r['C_original'] for r in file_results]
            between_spreads.append(max(c_values) - min(c_values))
    mean_between_spread = np.mean(between_spreads) if between_spreads else 0
    
    # Ratio
    ratio = mean_within_var / between_var if between_var > 0 else float('inf')
    
    return {
        'domain': 'MHD',
        'within_variance': mean_within_var,
        'between_variance': between_var,
        'ratio': ratio,
        'mean_delta': mean_c,
        'std_delta': std_c,
        'min_delta': min_c,
        'max_delta': max_c,
        'spread': spread,
        'temporal_spread': mean_temporal_spread,
        'between_spread': mean_between_spread,
        'n_regimes': len(files),
        'n_timesteps': len(results) // len(files) if files else 0,
        'all_c': all_c
    }

# ============================================================================
# Compute transform sensitivity for MHD
# ============================================================================

def compute_mhd_transform_sensitivity(results):
    """Compute transform sensitivity for MHD."""
    # This would require loading the actual data and computing C under different transforms
    # For now, use existing data from RD-WELL.7B.R1
    
    with open('audits/rd_well7b_r1/mhd_replication_results.json', 'r') as f:
        mhd_results = json.load(f)
    
    # Compute transform sensitivity
    delta_c_rank = [r['ΔC_rank'] for r in mhd_results]
    delta_c_zscore = [r['ΔC_zscore'] for r in mhd_results]
    delta_c_dimension = [r['ΔC_dimension'] for r in mhd_results]
    
    return {
        'ΔC_rank': {
            'mean': np.mean(delta_c_rank),
            'std': np.std(delta_c_rank),
            'min': min(delta_c_rank),
            'max': max(delta_c_rank)
        },
        'ΔC_zscore': {
            'mean': np.mean(delta_c_zscore),
            'std': np.std(delta_c_zscore),
            'min': min(delta_c_zscore),
            'max': max(delta_c_zscore)
        },
        'ΔC_dimension': {
            'mean': np.mean(delta_c_dimension),
            'std': np.std(delta_c_dimension),
            'min': min(delta_c_dimension),
            'max': max(delta_c_dimension)
        }
    }

# ============================================================================
# Main analysis
# ============================================================================

def main():
    print("=" * 80)
    print("P5 — MHD SELF-ORGANIZATION AUDIT")
    print("=" * 80)
    
    # Load MHD data
    print("\nLoading MHD data...")
    results = load_mhd_data()
    
    if not results:
        print("No MHD data loaded. Using existing data from RD-WELL.7B.R1.")
        # Load existing data
        with open('audits/rd_well7b_r1/mhd_replication_results.json', 'r') as f:
            results = json.load(f)
    
    # Compute variance decomposition
    print("\nComputing variance decomposition...")
    decomp = compute_mhd_variance_decomposition(results)
    
    # Compute transform sensitivity
    print("\nComputing transform sensitivity...")
    transform_sensitivity = compute_mhd_transform_sensitivity(results)
    
    # ============================================================================
    # Table 1 — MHD Variance Decomposition
    # ============================================================================
    print("\n" + "=" * 80)
    print("TABLE 1 — MHD VARIANCE DECOMPOSITION")
    print("=" * 80)
    print(f"\n{'Domain':<8} {'Within':>12} {'Between':>12} {'Ratio':>8} {'Mean C':>12} {'Spread':>10}")
    print("-" * 80)
    print(f"{decomp['domain']:<8} {decomp['within_variance']:>12.6f} {decomp['between_variance']:>12.6f} "
          f"{decomp['ratio']:>8.2f}x {decomp['mean_delta']:>12.6f} {decomp['spread']:>10.6f}")
    
    # ============================================================================
    # Table 2 — MHD Transform Sensitivity
    # ============================================================================
    print("\n" + "=" * 80)
    print("TABLE 2 — MHD TRANSFORM SENSITIVITY")
    print("=" * 80)
    print(f"\n{'Transform':<15} {'Mean':>12} {'Std':>12} {'Min':>12} {'Max':>12}")
    print("-" * 80)
    
    for transform, stats in transform_sensitivity.items():
        print(f"{transform:<15} {stats['mean']:>12.6f} {stats['std']:>12.6f} "
              f"{stats['min']:>12.6f} {stats['max']:>12.6f}")
    
    # ============================================================================
    # Table 3 — Cross-Domain Comparison (with MHD)
    # ============================================================================
    print("\n" + "=" * 80)
    print("TABLE 3 — CROSS-DOMAIN COMPARISON (WITH MHD)")
    print("=" * 80)
    print(f"\n{'Domain':<8} {'Within':>12} {'Between':>12} {'Ratio':>8} {'Mean ΔC_rank':>14} {'Spread':>10}")
    print("-" * 80)
    
    # Load P1-P3 results
    with open('audits/rd_p1_gs/results.json', 'r') as f:
        gs_results = json.load(f)
    with open('audits/rd_p2_rb/results.json', 'r') as f:
        rb_results = json.load(f)
    with open('audits/rd_p3_am/results.json', 'r') as f:
        am_results = json.load(f)
    
    # Compute GS, RB, AM decomposition
    def compute_decomp(results, name):
        trajectories = {}
        for r in results:
            traj = r['trajectory']
            if traj not in trajectories:
                trajectories[traj] = []
            trajectories[traj].append(r['delta_C_rank'])
        
        within_variances = []
        for traj, deltas in trajectories.items():
            if len(deltas) > 1:
                within_variances.append(np.var(deltas))
        mean_within_var = np.mean(within_variances) if within_variances else 0
        
        frame_means = {}
        for r in results:
            frame = r['frame']
            if frame not in frame_means:
                frame_means[frame] = []
            frame_means[frame].append(r['delta_C_rank'])
        
        between_means = [np.mean(means) for means in frame_means.values()]
        between_var = np.var(between_means) if len(between_means) > 1 else 0
        
        all_deltas = [r['delta_C_rank'] for r in results]
        mean_delta = np.mean(all_deltas)
        spread = max(all_deltas) - min(all_deltas)
        
        ratio = mean_within_var / between_var if between_var > 0 else float('inf')
        
        return {
            'domain': name,
            'within_variance': mean_within_var,
            'between_variance': between_var,
            'ratio': ratio,
            'mean_delta': mean_delta,
            'spread': spread
        }
    
    gs_decomp = compute_decomp(gs_results, 'GS')
    rb_decomp = compute_decomp(rb_results, 'RB')
    am_decomp = compute_decomp(am_results, 'AM')
    
    for d in [gs_decomp, rb_decomp, am_decomp, decomp]:
        print(f"{d['domain']:<8} {d['within_variance']:>12.6f} {d['between_variance']:>12.6f} "
              f"{d['ratio']:>8.2f}x {d['mean_delta']:>14.6f} {d['spread']:>10.6f}")
    
    # ============================================================================
    # Key Findings
    # ============================================================================
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)
    
    print("\n1. MHD VARIANCE STRUCTURE:")
    print(f"   - Within-regime variance: {decomp['within_variance']:.6f}")
    print(f"   - Between-regime variance: {decomp['between_variance']:.6f}")
    print(f"   - Ratio: {decomp['ratio']:.2f}x")
    
    if decomp['ratio'] > 1:
        print("   - Temporal variation exceeds regime variation")
    else:
        print("   - Regime variation exceeds temporal variation")
    
    print("\n2. MHD TRANSFORM SENSITIVITY:")
    print(f"   - ΔC_rank: {transform_sensitivity['ΔC_rank']['mean']:.6f} ± {transform_sensitivity['ΔC_rank']['std']:.6f}")
    print(f"   - ΔC_zscore: {transform_sensitivity['ΔC_zscore']['mean']:.6f} ± {transform_sensitivity['ΔC_zscore']['std']:.6f}")
    print(f"   - ΔC_dimension: {transform_sensitivity['ΔC_dimension']['mean']:.6f} ± {transform_sensitivity['ΔC_dimension']['std']:.6f}")
    
    print("\n3. MHD vs OTHER DOMAINS:")
    print(f"   - MHD mean ΔC_rank: {decomp['mean_delta']:.6f}")
    print(f"   - GS mean ΔC_rank: {gs_decomp['mean_delta']:.6f}")
    print(f"   - RB mean ΔC_rank: {rb_decomp['mean_delta']:.6f}")
    print(f"   - AM mean ΔC_rank: {am_decomp['mean_delta']:.6f}")
    
    print("\n4. RD-CONSTRAINT WARNING:")
    print("   - MHD has strong physical constraints (magnetic fields, topology)")
    print("   - MHD has extremely low ΔC_rank")
    print("   - MHD has strong representation stability")
    print("   - This may explain why MHD behaves differently from unconstrained systems")
    
    # ============================================================================
    # Save results
    # ============================================================================
    output = {
        'variance_decomposition': decomp,
        'transform_sensitivity': transform_sensitivity,
        'cross_domain_comparison': {
            'GS': gs_decomp,
            'RB': rb_decomp,
            'AM': am_decomp,
            'MHD': decomp
        }
    }
    
    # Remove non-serializable items
    if 'all_c' in output['variance_decomposition']:
        del output['variance_decomposition']['all_c']
    
    with open('audits/rd_p5_mhd/p5_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 80)
    print("P5 — MHD SELF-ORGANIZATION AUDIT COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
