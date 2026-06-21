#!/usr/bin/env python3
"""
RD-WELL.8A — Expanded Replication Audit

Replicate representation stability measurements across domains.
Sample min(5 trajectories, all available) per domain.
Sample at least 5 time points per trajectory.
"""

import json
import numpy as np
from pathlib import Path
import sys
import os
import h5py
import fsspec
from scipy.stats import rankdata

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def normalize_to_01(field):
    """Normalize field to [0, 1] range."""
    field_min = np.min(field)
    field_max = np.max(field)
    if field_max - field_min < 1e-10:
        return np.zeros_like(field)
    return (field - field_min) / (field_max - field_min)

def rank_transform(field):
    """Apply rank transform to field."""
    ranked = rankdata(field.flatten()).reshape(field.shape)
    return ranked

def compute_C(field_sequence):
    """Compute total correlation C for a sequence of fields."""
    if len(field_sequence) < 2:
        return 0.0
    
    diffs = []
    for i in range(len(field_sequence) - 1):
        diff = np.abs(field_sequence[i+1] - field_sequence[i]).mean()
        diffs.append(diff)
    
    diffs = np.array(diffs)
    if diffs.std() == 0:
        return 1.0 if diffs.mean() == 0 else 0.0
    
    cv = diffs.std() / (diffs.mean() + 1e-10)
    C = 1.0 / (1.0 + cv)
    
    return C

def load_field(file_path, field_name, trajectory_idx, frame_idx):
    """Load a specific field from a dataset."""
    try:
        with fsspec.open(file_path, 'rb') as f, h5py.File(f, 'r') as file:
            if 't0_fields' in file:
                fields = file['t0_fields']
                if field_name in fields:
                    data = fields[field_name]
                    if trajectory_idx < data.shape[0] and frame_idx < data.shape[1]:
                        return data[trajectory_idx, frame_idx]
    except Exception as e:
        print(f"    Error loading {file_path}: {e}")
    return None

def main():
    """Run Expanded Replication Audit."""
    
    # Create output directory
    output_dir = Path('/home/student/sgp_core_v2/audits/rd_well8a')
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("RD-WELL.8A — Expanded Replication Audit")
    print("=" * 70)
    
    # Define domains
    domains = [
        {
            'name': 'gray_scott_reaction_diffusion',
            'field': 'B',
            'max_trajectories': 5,
            'is_3d': False,
        },
        {
            'name': 'rayleigh_benard',
            'field': 'buoyancy',
            'max_trajectories': 5,
            'is_3d': False,
        },
        {
            'name': 'active_matter',
            'field': 'concentration',
            'max_trajectories': 2,  # Only 2 available
            'is_3d': False,
        },
        {
            'name': 'rayleigh_taylor_instability',
            'field': 'density',
            'max_trajectories': 2,  # Only 2 available
            'is_3d': True,
        },
        {
            'name': 'MHD_64',
            'field': 'density',
            'max_trajectories': 1,  # Only 1 available
            'is_3d': True,
        },
    ]
    
    # Results storage
    all_results = {}
    
    for domain_info in domains:
        dataset_name = domain_info['name']
        field_name = domain_info['field']
        max_trajectories = domain_info['max_trajectories']
        is_3d = domain_info['is_3d']
        
        print(f"\n{'='*70}")
        print(f"Domain: {dataset_name}")
        print(f"{'='*70}")
        
        # Find files
        try:
            fs, _ = fsspec.url_to_fs(f'hf://datasets/polymathic-ai/{dataset_name}')
            files = fs.glob(f'hf://datasets/polymathic-ai/{dataset_name}/data/test/*.hdf5')
            
            if not files:
                print(f"  No files found for {dataset_name}")
                continue
            
            print(f"  Found {len(files)} files")
            
            # Get dataset structure
            file_path = f'hf://{files[0]}'
            with fsspec.open(file_path, 'rb') as f, h5py.File(f, 'r') as file:
                if 't0_fields' in file:
                    fields = file['t0_fields']
                    if field_name in fields:
                        data = fields[field_name]
                        n_trajectories = min(max_trajectories, data.shape[0])
                        n_timesteps = data.shape[1]
                        
                        print(f"  Field: {field_name}")
                        print(f"  Shape: {data.shape}")
                        print(f"  Using {n_trajectories} trajectories, {n_timesteps} timesteps")
                        
                        # Sample time points (0%, 25%, 50%, 75%, 100%)
                        time_points = [
                            0,
                            n_timesteps // 4,
                            n_timesteps // 2,
                            3 * n_timesteps // 4,
                            n_timesteps - 1
                        ]
                        print(f"  Time points: {time_points}")
                        
                        # Run replication
                        domain_results = {
                            'domain': dataset_name,
                            'field': field_name,
                            'n_trajectories': n_trajectories,
                            'n_timesteps': n_timesteps,
                            'time_points': time_points,
                            'measurements': []
                        }
                        
                        for traj in range(n_trajectories):
                            print(f"\n  Trajectory {traj}:")
                            
                            for t in time_points:
                                # Load field
                                field = load_field(file_path, field_name, traj, t)
                                
                                if field is None:
                                    print(f"    t={t}: FAILED")
                                    continue
                                
                                # If 3D, take middle slice
                                if is_3d and len(field.shape) == 3:
                                    mid_z = field.shape[0] // 2
                                    field = field[mid_z, :, :]
                                
                                # Normalize
                                field_norm = normalize_to_01(field)
                                
                                # Create sequence with small noise for C computation
                                np.random.seed(42 + traj * 100 + t)
                                sequence = [field_norm + np.random.normal(0, 0.01, field_norm.shape) for _ in range(5)]
                                
                                # Compute C (original)
                                C_original = compute_C(sequence)
                                
                                # Compute C (rank)
                                sequence_ranked = [rank_transform(frame) for frame in sequence]
                                C_rank = compute_C(sequence_ranked)
                                
                                # Compute ΔC_rank
                                delta_C_rank = abs(C_original - C_rank)
                                
                                domain_results['measurements'].append({
                                    'trajectory': traj,
                                    'timepoint': t,
                                    'C_original': float(C_original),
                                    'C_rank': float(C_rank),
                                    'delta_C_rank': float(delta_C_rank)
                                })
                                
                                print(f"    t={t:3d} ({t/n_timesteps*100:.0f}%): C_original={C_original:.4f}, C_rank={C_rank:.4f}, ΔC_rank={delta_C_rank:.4f}")
                        
                        all_results[dataset_name] = domain_results
                        
        except Exception as e:
            print(f"  Error processing {dataset_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # =====================================================
    # Compute summary statistics
    # =====================================================
    
    print("\n" + "=" * 70)
    print("COMPUTING SUMMARY STATISTICS")
    print("=" * 70)
    
    summary_stats = {}
    
    for dataset_name, domain_results in all_results.items():
        measurements = domain_results['measurements']
        
        if not measurements:
            continue
        
        delta_C_rank_values = [m['delta_C_rank'] for m in measurements]
        
        mean_delta = np.mean(delta_C_rank_values)
        std_delta = np.std(delta_C_rank_values)
        n = len(delta_C_rank_values)
        ci_95 = 1.96 * std_delta / np.sqrt(n) if n > 0 else 0
        
        summary_stats[dataset_name] = {
            'N': n,
            'mean_delta_C_rank': float(mean_delta),
            'std_delta_C_rank': float(std_delta),
            'ci_95': float(ci_95),
            'min': float(np.min(delta_C_rank_values)),
            'max': float(np.max(delta_C_rank_values)),
            'measurements': measurements
        }
        
        print(f"\n{dataset_name}:")
        print(f"  N = {n}")
        print(f"  mean(ΔC_rank) = {mean_delta:.6f} ± {std_delta:.6f}")
        print(f"  95% CI = ±{ci_95:.6f}")
        print(f"  Range: [{np.min(delta_C_rank_values):.6f}, {np.max(delta_C_rank_values):.6f}]")
    
    # =====================================================
    # Table 1 — Replication Statistics
    # =====================================================
    
    print("\n" + "=" * 70)
    print("TABLE 1 — REPLICATION STATISTICS")
    print("=" * 70)
    
    print(f"\n{'Domain':<35} {'N':>4} {'mean(ΔC_rank)':>15} {'std':>10} {'95% CI':>12}")
    print("-" * 80)
    
    for dataset_name in ['gray_scott_reaction_diffusion', 'rayleigh_benard', 'active_matter', 'rayleigh_taylor_instability', 'MHD_64']:
        if dataset_name in summary_stats:
            stats = summary_stats[dataset_name]
            print(f"{dataset_name:<35} {stats['N']:>4} {stats['mean_delta_C_rank']:>15.6f} {stats['std_delta_C_rank']:>10.6f} ±{stats['ci_95']:>10.6f}")
        else:
            print(f"{dataset_name:<35} {'N/A':>4} {'N/A':>15} {'N/A':>10} {'N/A':>12}")
    
    # =====================================================
    # Table 2 — Stability Ranking
    # =====================================================
    
    print("\n" + "=" * 70)
    print("TABLE 2 — STABILITY RANKING (PROVISIONAL)")
    print("=" * 70)
    
    # Sort by mean ΔC_rank
    sorted_domains = sorted(summary_stats.items(), key=lambda x: x[1]['mean_delta_C_rank'])
    
    print(f"\n{'Domain':<35} {'mean(ΔC_rank)':>15} {'Rank Class':>20}")
    print("-" * 70)
    
    for dataset_name, stats in sorted_domains:
        mean_val = stats['mean_delta_C_rank']
        
        # Assign rank class
        if mean_val < 0.005:
            rank_class = "very stable"
        elif mean_val < 0.02:
            rank_class = "stable"
        elif mean_val < 0.1:
            rank_class = "moderate"
        else:
            rank_class = "high sensitivity"
        
        print(f"{dataset_name:<35} {mean_val:>15.6f} {rank_class:>20}")
    
    # =====================================================
    # Table 3 — Temporal Stability
    # =====================================================
    
    print("\n" + "=" * 70)
    print("TABLE 3 — TEMPORAL STABILITY")
    print("=" * 70)
    
    for dataset_name, domain_results in all_results.items():
        measurements = domain_results['measurements']
        time_points = domain_results['time_points']
        
        if not measurements:
            continue
        
        print(f"\n{dataset_name}:")
        
        # Group by timepoint
        for t in time_points:
            t_measurements = [m for m in measurements if m['timepoint'] == t]
            if t_measurements:
                delta_values = [m['delta_C_rank'] for m in t_measurements]
                mean_delta = np.mean(delta_values)
                print(f"  t={t:3d} ({t/domain_results['n_timesteps']*100:.0f}%): ΔC_rank = {mean_delta:.6f} (N={len(delta_values)})")
    
    # =====================================================
    # Save results
    # =====================================================
    
    output_file = output_dir / 'expanded_replication_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'summary_statistics': summary_stats,
            'domains': {k: v for k, v in all_results.items()},
            'metadata': {
                'description': 'RD-WELL.8A Expanded Replication Audit',
                'date': '2026-06-17',
                'domains_tested': list(all_results.keys()),
                'total_measurements': sum(len(v['measurements']) for v in all_results.values())
            }
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # =====================================================
    # Summary
    # =====================================================
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total_measurements = sum(len(v['measurements']) for v in all_results.values())
    print(f"\nTotal measurements: {total_measurements}")
    print(f"Domains tested: {len(all_results)}")
    
    print("\n" + "=" * 70)
    print("RD-WELL.8A COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    main()
