#!/usr/bin/env python3
"""
RD-WELL.5D — Cross-Domain Coupling Audit

Test whether coupling geometry extends beyond Gray-Scott.

Domains:
- Gray-Scott (bubbles, maze, spirals)
- Rayleigh-Bénard
- Active Matter
- Rayleigh-Taylor instability

Question: Which classes of observables maintain coupling to C across independent worlds?

This directly attacks SR-30.
"""

import fsspec
import h5py
import numpy as np
import json
import os
import sys

# Add the metrics directory to path
sys.path.insert(0, '/home/student/sgp_core_v2/coherence-benchmark')
from metrics.total_correlation import compute_C


def compute_s1_spectral_entropy(A_data):
    """S1: Spectral entropy plateau."""
    # Compute mean across spatial dimensions
    if A_data.ndim == 3:
        A_mean = A_data.mean(axis=(1, 2))
    elif A_data.ndim == 4:
        A_mean = A_data.mean(axis=(1, 2, 3))
    else:
        A_mean = A_data.mean(axis=-1)

    window = min(50, len(A_mean) - 1)
    if window < 10:
        return np.array([])

    values = []
    for start in range(len(A_mean) - window + 1):
        window_data = A_mean[start:start+window]
        fft_vals = np.fft.rfft(window_data)
        power = np.abs(fft_vals)**2
        power_prob = power / (power.sum() + 1e-10)
        H = -np.sum(power_prob * np.log(power_prob + 1e-10))
        values.append(H)
    return np.array(values)


def compute_s2_temporal_derivative(A_data):
    """S2: Temporal derivative norm."""
    if A_data.ndim == 3:
        A_mean = A_data.mean(axis=(1, 2))
    elif A_data.ndim == 4:
        A_mean = A_data.mean(axis=(1, 2, 3))
    else:
        A_mean = A_data.mean(axis=-1)

    return np.abs(np.diff(A_mean))


def compute_s3_morphology_persistence(A_data, threshold=0.5):
    """S3: Morphology persistence."""
    # Binarize
    binary = (A_data > threshold).astype(int)

    # Sum across spatial dimensions
    if binary.ndim == 3:
        pixel_counts = binary.sum(axis=(1, 2))
    elif binary.ndim == 4:
        pixel_counts = binary.sum(axis=(1, 2, 3))
    else:
        pixel_counts = binary.sum(axis=-1)

    return np.abs(np.diff(pixel_counts))


def compute_C_two_fields(field1, field2):
    """Compute C from two fields."""
    # Compute means
    if field1.ndim == 3:
        f1_mean = field1.mean(axis=(1, 2))
        f2_mean = field2.mean(axis=(1, 2))
    elif field1.ndim == 4:
        f1_mean = field1.mean(axis=(1, 2, 3))
        f2_mean = field2.mean(axis=(1, 2, 3))
    else:
        f1_mean = field1.mean(axis=-1)
        f2_mean = field2.mean(axis=-1)

    # Stack
    X = np.stack([f1_mean, f2_mean], axis=0)

    # Compute C
    try:
        return compute_C(X, estimator='gaussian')
    except:
        return np.nan


def compute_C_over_time(field1, field2):
    """Compute C at each time step."""
    # Compute means
    if field1.ndim == 3:
        f1_mean = field1.mean(axis=(1, 2))
        f2_mean = field2.mean(axis=(1, 2))
    elif field1.ndim == 4:
        f1_mean = field1.mean(axis=(1, 2, 3))
        f2_mean = field2.mean(axis=(1, 2, 3))
    else:
        f1_mean = field1.mean(axis=-1)
        f2_mean = field2.mean(axis=-1)

    C_values = []
    for t in range(10, len(f1_mean) + 1):
        X = np.stack([f1_mean[:t], f2_mean[:t]], axis=0)
        try:
            C_val = compute_C(X, estimator='gaussian')
            C_values.append(C_val)
        except:
            C_values.append(np.nan)
    return np.array(C_values)


def analyze_domain(domain_name, field1, field2, time_steps=200):
    """Analyze one domain: compute C, S1, S2, S3, and correlations."""
    print(f"\nAnalyzing {domain_name}...")

    # Limit to time_steps
    if field1.shape[0] > time_steps:
        field1 = field1[:time_steps]
        field2 = field2[:time_steps]

    # Compute C over time
    C_values = compute_C_over_time(field1, field2)

    # Compute stabilization metrics
    s1_values = compute_s1_spectral_entropy(field1)
    s2_values = compute_s2_temporal_derivative(field1)
    s3_values = compute_s3_morphology_persistence(field1)

    results = {}

    # For each metric, compute correlation with C
    for metric_name, metric_values in [('S1', s1_values), ('S2', s2_values), ('S3', s3_values)]:
        if len(metric_values) == 0:
            results[metric_name] = {
                'correlation': None,
                'abs_correlation': None,
                'independent': None,
            }
            print(f"  {metric_name}: no data")
            continue

        # Determine offset
        if metric_name == 'S1':
            offset = max(0, len(metric_values) - len(C_values))
        else:
            offset = max(0, len(metric_values) - len(C_values))

        # Trim to common length
        min_len = min(len(C_values), len(metric_values) - offset)

        if min_len > 10:
            C_trim = C_values[:min_len]
            metric_trim = metric_values[offset:offset+min_len]

            # Remove NaN
            valid = ~np.isnan(C_trim) & ~np.isnan(metric_trim)
            C_valid = C_trim[valid]
            metric_valid = metric_trim[valid]

            if len(C_valid) > 10:
                corr = np.corrcoef(C_valid, metric_valid)[0, 1]
            else:
                corr = np.nan
        else:
            corr = np.nan

        results[metric_name] = {
            'correlation': float(corr) if not np.isnan(corr) else None,
            'abs_correlation': float(abs(corr)) if not np.isnan(corr) else None,
            'independent': bool(abs(corr) < 0.8) if not np.isnan(corr) else None,
        }

        print(f"  {metric_name} vs C: r = {corr:.4f}")

    return results


def main():
    print("RD-WELL.5D — Cross-Domain Coupling Audit")
    print("=" * 60)
    print("Question: Which classes of observables maintain coupling to C across independent worlds?")
    print("=" * 60)

    all_results = {}

    # ============================================================
    # Gray-Scott patterns
    # ============================================================
    print("\n" + "=" * 60)
    print("GRAY-SCOTT PATTERNS")
    print("=" * 60)

    gs_patterns = {
        'bubbles': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_bubbles_F_0.098_k_0.057.hdf5',
        'maze': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_maze_F_0.029_k_0.057.hdf5',
        'spirals': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_spirals_F_0.018_k_0.051.hdf5',
    }

    for pattern_name, url in gs_patterns.items():
        try:
            fs, path = fsspec.core.url_to_fs(url)
            with h5py.File(fs.open(path, 'rb'), 'r') as f:
                field_A = f['t0_fields']['A']
                field_B = f['t0_fields']['B']

                A_data = field_A[0, :200]
                B_data = field_B[0, :200]

            results = analyze_domain(pattern_name, A_data, B_data)
            all_results[f"gs_{pattern_name}"] = results
        except Exception as e:
            print(f"\n{pattern_name}: ERROR - {e}")
            all_results[f"gs_{pattern_name}"] = {'error': str(e)}

    # ============================================================
    # Rayleigh-Bénard
    # ============================================================
    print("\n" + "=" * 60)
    print("RAYLEIGH-BÉNARD")
    print("=" * 60)

    rb_url = 'https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Ra1e+08_Pr1_2D_512x128_1000.hdf5'

    try:
        fs, path = fsspec.core.url_to_fs(rb_url)
        with h5py.File(fs.open(path, 'rb'), 'r') as f:
            print(f"Keys: {list(f.keys())}")
            if 't0_fields' in f:
                fields = f['t0_fields']
                print(f"Fields: {list(fields.keys())}")

                # Get first field
                field1_name = list(fields.keys())[0]
                field1 = fields[field1_name][0, :200]

                # Get second field if available
                if len(fields.keys()) > 1:
                    field2_name = list(fields.keys())[1]
                    field2 = fields[field2_name][0, :200]
                else:
                    field2 = field1

                results = analyze_domain('rayleigh_benard', field1, field2)
                all_results['rayleigh_benard'] = results
            else:
                print("No t0_fields found")
                all_results['rayleigh_benard'] = {'error': 'No t0_fields'}
    except Exception as e:
        print(f"\nRayleigh-Bénard: ERROR - {e}")
        all_results['rayleigh_benard'] = {'error': str(e)}

    # ============================================================
    # Active Matter
    # ============================================================
    print("\n" + "=" * 60)
    print("ACTIVE MATTER")
    print("=" * 60)

    am_url = 'https://huggingface.co/datasets/polymathic-ai/active_matter/resolve/main/data/train/active_matter_activity_8.0_noise_0.001.hdf5'

    try:
        fs, path = fsspec.core.url_to_fs(am_url)
        with h5py.File(fs.open(path, 'rb'), 'r') as f:
            print(f"Keys: {list(f.keys())}")
            if 't0_fields' in f:
                fields = f['t0_fields']
                print(f"Fields: {list(fields.keys())}")

                # Get first field
                field1_name = list(fields.keys())[0]
                field1 = fields[field1_name][0, :200]

                # Get second field if available
                if len(fields.keys()) > 1:
                    field2_name = list(fields.keys())[1]
                    field2 = fields[field2_name][0, :200]
                else:
                    field2 = field1

                results = analyze_domain('active_matter', field1, field2)
                all_results['active_matter'] = results
            else:
                print("No t0_fields found")
                all_results['active_matter'] = {'error': 'No t0_fields'}
    except Exception as e:
        print(f"\nActive Matter: ERROR - {e}")
        all_results['active_matter'] = {'error': str(e)}

    # ============================================================
    # Save results
    # ============================================================
    output_dir = "/home/student/sgp_core_v2/audits/rd_well5d"
    os.makedirs(output_dir, exist_ok=True)

    output = {
        'description': 'Cross-domain coupling audit',
        'results': all_results,
    }

    output_file = os.path.join(output_dir, "cross_domain_coupling.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # ============================================================
    # Summary table
    # ============================================================
    print("\n" + "=" * 60)
    print("COUPLING GEOMETRY TABLE")
    print("=" * 60)

    # Print header
    print(f"\n{'Domain':<25} {'S₁':<12} {'S₂':<12} {'S₃':<12}")
    print("-" * 60)

    for domain, results in all_results.items():
        if 'error' in results:
            print(f"{domain:<25} {'ERROR':<12} {'ERROR':<12} {'ERROR':<12}")
        else:
            s1 = results.get('S1', {}).get('correlation', None)
            s2 = results.get('S2', {}).get('correlation', None)
            s3 = results.get('S3', {}).get('correlation', None)

            s1_str = f"{s1:.2f}" if s1 is not None else "N/A"
            s2_str = f"{s2:.2f}" if s2 is not None else "N/A"
            s3_str = f"{s3:.2f}" if s3 is not None else "N/A"

            print(f"{domain:<25} {s1_str:<12} {s2_str:<12} {s3_str:<12}")

    print("\n" + "=" * 60)
    print("Status: Measurement only. No conclusions drawn.")
    print("=" * 60)


if __name__ == "__main__":
    main()
