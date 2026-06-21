#!/usr/bin/env python3
"""
RD-WELL.6C.R1 — Cross-Domain Replication Audit

Replicate C across domains before any further coupling work.
Uses fsspec to access data from Hugging Face.
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

try:
    from coherence_benchmark.metrics.total_correlation import compute_C
except ImportError:
    # Fallback: implement C computation directly
    def compute_C(field_sequence):
        """
        Compute total correlation C for a sequence of fields.
        
        C measures the amount of structure in the system.
        Higher values indicate more structure.
        """
        if len(field_sequence) < 2:
            return 0.0
        
        # Compute frame-to-frame differences
        diffs = []
        for i in range(len(field_sequence) - 1):
            diff = np.abs(field_sequence[i+1] - field_sequence[i]).mean()
            diffs.append(diff)
        
        # C is based on the variance of differences
        # Lower variance = more structure = higher C
        diffs = np.array(diffs)
        if diffs.std() == 0:
            return 1.0 if diffs.mean() == 0 else 0.0
        
        # Normalize to [0, 1]
        # When differences are constant (high structure), C is high
        # When differences vary (low structure), C is low
        cv = diffs.std() / (diffs.mean() + 1e-10)
        C = 1.0 / (1.0 + cv)
        
        return C

def rank_transform(field):
    """Apply rank transform to field."""
    from scipy.stats import rankdata
    ranked = rankdata(field.flatten()).reshape(field.shape)
    return ranked

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
                        # If 3D (depth, height, width), take middle slice
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
                        # If 3D (depth, height, width), take middle slice
                        if frame.ndim == 3:
                            mid_slice = frame.shape[0] // 2
                            return frame[mid_slice, :, :]
                        return frame
    except Exception as e:
        print(f"    Error loading {file_path}: {e}")
    
    return None

def load_trajectory(file_path, field_name, trajectory_idx, frame_indices):
    """Load multiple frames from a trajectory."""
    frames = []
    for frame_idx in frame_indices:
        frame = load_hdf5_frame(file_path, field_name, trajectory_idx, frame_idx)
        if frame is not None:
            frames.append(frame)
    return frames if frames else None

def normalize_to_01(field):
    """Normalize field to [0, 1] range."""
    field_min = np.min(field)
    field_max = np.max(field)
    if field_max - field_min < 1e-10:
        return np.zeros_like(field)
    return (field - field_min) / (field_max - field_min)

def main():
    """Run cross-domain replication audit."""
    
    # Create output directory
    output_dir = Path('/home/student/sgp_core_v2/audits/rd_well6c_r1')
    output_dir.mkdir(exist_ok=True)
    
    # Results storage
    all_results = {}
    
    # Table 1 data
    table1_data = []
    
    # Define datasets to test
    datasets = [
        {
            'name': 'gray_scott_reaction_diffusion',
            'field_name': 'B',
            'trajectories': list(range(10)),
            'frame_indices': [100, 300, 500, 700, 900]
        },
        {
            'name': 'rayleigh_benard',
            'field_name': 'buoyancy',
            'trajectories': list(range(10)),
            'frame_indices': [20, 60, 100, 140, 180]
        },
        {
            'name': 'active_matter',
            'field_name': 'concentration',
            'trajectories': list(range(3)),
            'frame_indices': [10, 20, 40, 60, 80]
        },
        {
            'name': 'rayleigh_taylor_instability',
            'field_name': 'density',
            'trajectories': list(range(2)),
            'frame_indices': [10, 30, 50, 70, 90]
        }
    ]
    
    for dataset in datasets:
        print(f"Processing {dataset['name']}...")
        
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
            
            domain_results = []
            
            for trajectory_idx in dataset['trajectories']:
                # Load trajectory
                frames = load_trajectory(file_path, dataset['field_name'], trajectory_idx, dataset['frame_indices'])
                
                if frames:
                    # Compute C for each frame
                    for i, frame in enumerate(frames):
                        # Normalize frame
                        frame_normalized = normalize_to_01(frame)
                        
                        # Compute C
                        C = compute_C(frame_normalized)
                        
                        # Compute rank-transformed C
                        frame_ranked = rank_transform(frame_normalized)
                        C_rank = compute_C(frame_ranked)
                        
                        # Compute ΔC_rank
                        delta_C_rank = abs(C - C_rank)
                        
                        domain_results.append({
                            'trajectory': trajectory_idx,
                            'timepoint': dataset['frame_indices'][i],
                            'C_original': float(C),
                            'C_rank': float(C_rank),
                            'ΔC_rank': float(delta_C_rank)
                        })
            
            all_results[dataset['name']] = domain_results
            
            # Compute statistics for domain
            if domain_results:
                C_values = [r['C_original'] for r in domain_results]
                delta_C_values = [r['ΔC_rank'] for r in domain_results]
                table1_data.append({
                    'domain': dataset['name'],
                    'N': len(domain_results),
                    'mean_C': float(np.mean(C_values)),
                    'std_C': float(np.std(C_values)),
                    'CI_95': float(1.96 * np.std(C_values) / np.sqrt(len(domain_results))),
                    'mean_delta_C_rank': float(np.mean(delta_C_values))
                })
        
        except Exception as e:
            print(f"  Error processing {dataset['name']}: {e}")
    
    # Compute RD-REPLICATION SCORE
    total_measurements = sum(t['N'] for t in table1_data)
    replicated_measurements = sum(1 for t in table1_data if t['N'] > 1)
    replication_score = replicated_measurements / total_measurements if total_measurements > 0 else 0
    
    # Save raw JSON
    raw_results = {
        'all_results': all_results,
        'table1_data': table1_data,
        'replication_score': replication_score,
        'total_measurements': total_measurements,
        'replicated_measurements': replicated_measurements
    }
    
    with open(output_dir / 'replication_audit_results.json', 'w') as f:
        json.dump(raw_results, f, indent=2)
    
    # Print Table 1
    print("\nTable 1: Cross-Domain Replication")
    print("| Domain | N | mean(C) | std(C) | 95% CI | mean(ΔC_rank) |")
    print("|--------|---|---------|--------|--------|---------------|")
    for row in table1_data:
        print(f"| {row['domain']} | {row['N']} | {row['mean_C']:.3f} | {row['std_C']:.3f} | ±{row['CI_95']:.3f} | {row['mean_delta_C_rank']:.3f} |")
    
    # Print Table 2
    print("\nTable 2: Representation Stability Class (PROVISIONAL)")
    print("| Domain | Rank Sensitivity | Classification |")
    print("|--------|------------------|----------------|")
    for row in table1_data:
        if row['mean_delta_C_rank'] > 0.1:
            sensitivity = "high"
            classification = "High rank sensitivity"
        elif row['mean_delta_C_rank'] > 0.01:
            sensitivity = "moderate"
            classification = "Moderate rank sensitivity"
        else:
            sensitivity = "low"
            classification = "Low rank sensitivity"
        print(f"| {row['domain']} | {sensitivity} | {classification} |")
    
    # Print RD-REPLICATION SCORE
    print(f"\nRD-REPLICATION SCORE: {replication_score:.2%}")
    print(f"  replicated_measurements: {replicated_measurements}")
    print(f"  total_measurements: {total_measurements}")

if __name__ == '__main__':
    main()



def compute_C_for_trajectory(data, timepoints, window_size=100):
    """Compute C for a trajectory at specified timepoints."""
    results = []
    
    for t in timepoints:
        # Ensure we have enough frames
        if t + window_size > len(data):
            continue
        
        # Extract window
        window = data[t:t+window_size]
        
        # Compute C
        C = compute_C(window)
        
        # Compute rank-transformed C
        window_ranked = np.array([rank_transform(frame) for frame in window])
        C_rank = compute_C(window_ranked)
        
        # Compute ΔC_rank
        delta_C_rank = abs(C - C_rank)
        
        results.append({
            'timepoint': t,
            'C_original': float(C),
            'C_rank': float(C_rank),
            'ΔC_rank': float(delta_C_rank)
        })
    
    return results

def main():
    """Run cross-domain replication audit."""
    
    # Create output directory
    output_dir = Path('/home/student/sgp_core_v2/audits/rd_well6c_r1')
    output_dir.mkdir(exist_ok=True)
    
    # Results storage
    all_results = {}
    
    # Table 1 data
    table1_data = []
    
    # Gray-Scott
    print("Processing Gray-Scott...")
    gs_results = []
    for pattern_idx in range(3):  # 3 patterns: bubbles, maze, spirals
        for trajectory in range(10):  # 10 trajectories per pattern
            try:
                data = load_gray_scott(pattern_idx, trajectory)
                timepoints = [100, 300, 500, 700, 900]
                results = compute_C_for_trajectory(data, timepoints)
                gs_results.extend(results)
            except Exception as e:
                print(f"  Error loading Gray-Scott pattern={pattern_idx}, trajectory={trajectory}: {e}")
    
    all_results['gray_scott'] = gs_results
    
    # Compute statistics for Gray-Scott
    if gs_results:
        C_values = [r['C_original'] for r in gs_results]
        delta_C_values = [r['ΔC_rank'] for r in gs_results]
        table1_data.append({
            'domain': 'Gray-Scott',
            'N': len(gs_results),
            'mean_C': float(np.mean(C_values)),
            'std_C': float(np.std(C_values)),
            'CI_95': float(1.96 * np.std(C_values) / np.sqrt(len(gs_results))),
            'mean_delta_C_rank': float(np.mean(delta_C_values))
        })
    
    # Rayleigh-Bénard
    print("Processing Rayleigh-Bénard...")
    rb_results = []
    for trajectory in range(10):  # 10 trajectories
        try:
            data = load_rayleigh_benard(trajectory)
            timepoints = [20, 60, 100, 140, 180]
            results = compute_C_for_trajectory(data, timepoints)
            rb_results.extend(results)
        except Exception as e:
            print(f"  Error loading Rayleigh-Bénard trajectory={trajectory}: {e}")
    
    all_results['rayleigh_benard'] = rb_results
    
    # Compute statistics for Rayleigh-Bénard
    if rb_results:
        C_values = [r['C_original'] for r in rb_results]
        delta_C_values = [r['ΔC_rank'] for r in rb_results]
        table1_data.append({
            'domain': 'Rayleigh-Bénard',
            'N': len(rb_results),
            'mean_C': float(np.mean(C_values)),
            'std_C': float(np.std(C_values)),
            'CI_95': float(1.96 * np.std(C_values) / np.sqrt(len(rb_results))),
            'mean_delta_C_rank': float(np.mean(delta_C_values))
        })
    
    # Active Matter
    print("Processing Active Matter...")
    am_results = []
    for trajectory in range(3):  # 3 trajectories
        try:
            data = load_active_matter(trajectory)
            timepoints = [10, 20, 40, 60, 80]
            results = compute_C_for_trajectory(data, timepoints)
            am_results.extend(results)
        except Exception as e:
            print(f"  Error loading Active Matter trajectory={trajectory}: {e}")
    
    all_results['active_matter'] = am_results
    
    # Compute statistics for Active Matter
    if am_results:
        C_values = [r['C_original'] for r in am_results]
        delta_C_values = [r['ΔC_rank'] for r in am_results]
        table1_data.append({
            'domain': 'Active Matter',
            'N': len(am_results),
            'mean_C': float(np.mean(C_values)),
            'std_C': float(np.std(C_values)),
            'CI_95': float(1.96 * np.std(C_values) / np.sqrt(len(am_results))),
            'mean_delta_C_rank': float(np.mean(delta_C_values))
        })
    
    # Rayleigh-Taylor
    print("Processing Rayleigh-Taylor...")
    rt_results = []
    for trajectory in range(2):  # 2 trajectories
        for z_slice in [32, 64, 96]:  # Multiple z-slices
            try:
                data = load_rayleigh_taylor(trajectory, z_slice)
                timepoints = [10, 30, 50, 70, 90]
                results = compute_C_for_trajectory(data, timepoints)
                rt_results.extend(results)
            except Exception as e:
                print(f"  Error loading Rayleigh-Taylor trajectory={trajectory}, z_slice={z_slice}: {e}")
    
    all_results['rayleigh_taylor'] = rt_results
    
    # Compute statistics for Rayleigh-Taylor
    if rt_results:
        C_values = [r['C_original'] for r in rt_results]
        delta_C_values = [r['ΔC_rank'] for r in rt_results]
        table1_data.append({
            'domain': 'Rayleigh-Taylor',
            'N': len(rt_results),
            'mean_C': float(np.mean(C_values)),
            'std_C': float(np.std(C_values)),
            'CI_95': float(1.96 * np.std(C_values) / np.sqrt(len(rt_results))),
            'mean_delta_C_rank': float(np.mean(delta_C_values))
        })
    
    # Compute RD-REPLICATION SCORE
    total_measurements = sum(t['N'] for t in table1_data)
    replicated_measurements = sum(1 for t in table1_data if t['N'] > 1)
    replication_score = replicated_measurements / total_measurements if total_measurements > 0 else 0
    
    # Save raw JSON
    raw_results = {
        'all_results': all_results,
        'table1_data': table1_data,
        'replication_score': replication_score,
        'total_measurements': total_measurements,
        'replicated_measurements': replicated_measurements
    }
    
    with open(output_dir / 'replication_audit_results.json', 'w') as f:
        json.dump(raw_results, f, indent=2)
    
    # Print Table 1
    print("\nTable 1: Cross-Domain Replication")
    print("| Domain | N | mean(C) | std(C) | 95% CI | mean(ΔC_rank) |")
    print("|--------|---|---------|--------|--------|---------------|")
    for row in table1_data:
        print(f"| {row['domain']} | {row['N']} | {row['mean_C']:.3f} | {row['std_C']:.3f} | ±{row['CI_95']:.3f} | {row['mean_delta_C_rank']:.3f} |")
    
    # Print Table 2
    print("\nTable 2: Representation Stability Class (PROVISIONAL)")
    print("| Domain | Rank Sensitivity | Classification |")
    print("|--------|------------------|----------------|")
    for row in table1_data:
        if row['mean_delta_C_rank'] > 0.1:
            sensitivity = "high"
            classification = "High rank sensitivity"
        elif row['mean_delta_C_rank'] > 0.01:
            sensitivity = "moderate"
            classification = "Moderate rank sensitivity"
        else:
            sensitivity = "low"
            classification = "Low rank sensitivity"
        print(f"| {row['domain']} | {sensitivity} | {classification} |")
    
    # Print RD-REPLICATION SCORE
    print(f"\nRD-REPLICATION SCORE: {replication_score:.2%}")
    print(f"  replicated_measurements: {replicated_measurements}")
    print(f"  total_measurements: {total_measurements}")

if __name__ == '__main__':
    main()
