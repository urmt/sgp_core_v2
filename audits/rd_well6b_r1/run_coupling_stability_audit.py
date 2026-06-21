#!/usr/bin/env python3
"""
RD-WELL.6B.R1 — Coupling Stability Under Transformation

For every domain:
1. Compute C under all transforms.
2. Compute S₁, S₂, S₃ under all transforms.
3. Compute coupling matrix.
4. Report: Δr_transform

Question: Does the relationship survive change, or only the measurement?
"""

import numpy as np
import os
import sys
import json
from scipy import stats

# Add the coherence-benchmark to the path
sys.path.insert(0, '/home/student/sgp_core_v2/coherence-benchmark')

from metrics.total_correlation import compute_C


def apply_transformations(field):
    """Apply admissible field transformations."""
    transformations = {}

    # Original
    transformations['original'] = field

    # Z-score standardized
    transformations['zscore'] = (field - field.mean()) / (field.std() + 1e-10)

    # Rank-based
    flat = field.flatten()
    ranks = np.argsort(np.argsort(flat)).reshape(field.shape)
    transformations['rank'] = ranks.astype(float) / flat.size

    # Min-max normalized
    fmin = field.min()
    fmax = field.max()
    if fmax > fmin:
        transformations['minmax'] = (field - fmin) / (fmax - fmin)
    else:
        transformations['minmax'] = np.zeros_like(field)

    return transformations


def compute_C_for_field(field):
    """Compute C for a 3D field (time, height, width)."""
    if field.ndim == 3:
        reshaped = field.reshape(field.shape[0], -1)
        C_value = compute_C(reshaped)
        return float(C_value)
    else:
        return None


def compute_S1(field):
    """Compute S1 (spectral entropy) for a field."""
    if field.ndim == 3:
        entropies = []
        for t in range(field.shape[0]):
            frame = field[t]
            fft = np.fft.fft2(frame)
            power = np.abs(fft)**2
            power_norm = power / (power.sum() + 1e-10)
            entropy = -np.sum(power_norm * np.log(power_norm + 1e-10))
            entropies.append(float(entropy))
        return float(np.mean(entropies))
    else:
        return None


def compute_S2(field):
    """Compute S2 (temporal derivative norm) for a field."""
    if field.ndim == 3 and field.shape[0] > 1:
        derivatives = []
        for t in range(1, field.shape[0]):
            derivative = np.abs(field[t] - field[t-1]).mean()
            derivatives.append(float(derivative))
        return float(np.mean(derivatives))
    else:
        return None


def compute_S3(field):
    """Compute S3 (morphology persistence) for a field."""
    if field.ndim == 3 and field.shape[0] > 1:
        from scipy import ndimage
        component_counts = []
        for t in range(field.shape[0]):
            frame = field[t]
            threshold = frame.mean()
            binary = frame > threshold
            labeled, num_features = ndimage.label(binary)
            component_counts.append(float(num_features))
        
        if len(component_counts) > 1:
            similarities = []
            for t in range(1, len(component_counts)):
                similarity = 1.0 - abs(component_counts[t] - component_counts[t-1]) / max(component_counts[t], component_counts[t-1], 1)
                similarities.append(similarity)
            return float(np.mean(similarities))
        else:
            return None
    else:
        return None


def compute_coupling_stability(field, domain_name):
    """Compute coupling stability under transformations for a field."""
    transformations = apply_transformations(field)
    
    results = {}
    for transform_name, transformed_field in transformations.items():
        C_value = compute_C_for_field(transformed_field)
        S1_value = compute_S1(transformed_field)
        S2_value = compute_S2(transformed_field)
        S3_value = compute_S3(transformed_field)
        
        results[transform_name] = {
            'C': C_value,
            'S1': S1_value,
            'S2': S2_value,
            'S3': S3_value
        }
    
    # Compute coupling for each transform
    coupling_results = {}
    for transform_name, values in results.items():
        C = values['C']
        S1 = values['S1']
        S2 = values['S2']
        S3 = values['S3']
        
        # For single values, we can't compute correlation
        # We need to compute coupling across transforms
        coupling_results[transform_name] = {
            'C_S1': {'C': C, 'S1': S1},
            'C_S2': {'C': C, 'S2': S2},
            'C_S3': {'C': C, 'S3': S3}
        }
    
    return results, coupling_results


def compute_cross_transform_coupling(results):
    """Compute coupling across transformations."""
    transforms = list(results.keys())
    
    C_values = [results[t]['C'] for t in transforms if results[t]['C'] is not None]
    S1_values = [results[t]['S1'] for t in transforms if results[t]['S1'] is not None]
    S2_values = [results[t]['S2'] for t in transforms if results[t]['S2'] is not None]
    S3_values = [results[t]['S3'] for t in transforms if results[t]['S3'] is not None]
    
    coupling = {}
    
    # C-S1 coupling
    if len(C_values) == len(S1_values) and len(C_values) > 2:
        correlation, p_value = stats.pearsonr(C_values, S1_values)
        coupling['C_S1'] = {
            'correlation': float(correlation),
            'p_value': float(p_value),
            'N': len(C_values)
        }
    else:
        coupling['C_S1'] = {
            'correlation': None,
            'p_value': None,
            'N': len(C_values),
            'note': 'Insufficient data points for correlation'
        }
    
    # C-S2 coupling
    if len(C_values) == len(S2_values) and len(C_values) > 2:
        correlation, p_value = stats.pearsonr(C_values, S2_values)
        coupling['C_S2'] = {
            'correlation': float(correlation),
            'p_value': float(p_value),
            'N': len(C_values)
        }
    else:
        coupling['C_S2'] = {
            'correlation': None,
            'p_value': None,
            'N': len(C_values),
            'note': 'Insufficient data points for correlation'
        }
    
    # C-S3 coupling
    if len(C_values) == len(S3_values) and len(C_values) > 2:
        correlation, p_value = stats.pearsonr(C_values, S3_values)
        coupling['C_S3'] = {
            'correlation': float(correlation),
            'p_value': float(p_value),
            'N': len(C_values)
        }
    else:
        coupling['C_S3'] = {
            'correlation': None,
            'p_value': None,
            'N': len(C_values),
            'note': 'Insufficient data points for correlation'
        }
    
    return coupling


def main():
    print("RD-WELL.6B.R1 — Coupling Stability Under Transformation")
    print("=" * 60)
    print("For every domain:")
    print("1. Compute C under all transforms.")
    print("2. Compute S₁, S₂, S₃ under all transforms.")
    print("3. Compute coupling matrix.")
    print("4. Report: Δr_transform")
    print("=" * 60)

    output_dir = "/home/student/sgp_core_v2/audits/rd_well6b_r1"
    os.makedirs(output_dir, exist_ok=True)

    # Load all fields
    rb_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/rayleigh_benard_frames"
    am_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/active_matter_frames"

    # Rayleigh-Bénard buoyancy
    rb_buoyancy = np.load(os.path.join(rb_dir, 'buoyancy.npy'))

    # Active Matter concentration
    am_concentration = np.load(os.path.join(am_dir, 'concentration.npy'))

    # Compute coupling stability for each domain
    print("\n" + "=" * 60)
    print("COMPUTING COUPLING STABILITY FOR EACH DOMAIN")
    print("=" * 60)

    # Rayleigh-Bénard
    print("\nRayleigh-Bénard Buoyancy:")
    rb_results, rb_coupling_results = compute_coupling_stability(rb_buoyancy, 'Rayleigh-Bénard')
    
    for transform_name, values in rb_results.items():
        print(f"  {transform_name}: C={values['C']:.6f}, S1={values['S1']:.6f}, S2={values['S2']:.6f}, S3={values['S3']:.6f}")

    # Active Matter
    print("\nActive Matter Concentration:")
    am_results, am_coupling_results = compute_coupling_stability(am_concentration, 'Active Matter')
    
    for transform_name, values in am_results.items():
        print(f"  {transform_name}: C={values['C']:.6f}, S1={values['S1']:.6f}, S2={values['S2']:.6f}, S3={values['S3']:.6f}")

    # Compute cross-transform coupling
    print("\n" + "=" * 60)
    print("COMPUTING CROSS-TRANSFORM COUPLING")
    print("=" * 60)

    # Rayleigh-Bénard
    print("\nRayleigh-Bénard Buoyancy Cross-Transform Coupling:")
    rb_coupling = compute_cross_transform_coupling(rb_results)
    
    for coupling_name, coupling_data in rb_coupling.items():
        if coupling_data['correlation'] is not None:
            print(f"  {coupling_name}: r={coupling_data['correlation']:.6f}, p={coupling_data['p_value']:.6f}, N={coupling_data['N']}")
        else:
            print(f"  {coupling_name}: {coupling_data['note']}")

    # Active Matter
    print("\nActive Matter Concentration Cross-Transform Coupling:")
    am_coupling = compute_cross_transform_coupling(am_results)
    
    for coupling_name, coupling_data in am_coupling.items():
        if coupling_data['correlation'] is not None:
            print(f"  {coupling_name}: r={coupling_data['correlation']:.6f}, p={coupling_data['p_value']:.6f}, N={coupling_data['N']}")
        else:
            print(f"  {coupling_name}: {coupling_data['note']}")

    # Save results
    output_file = os.path.join(output_dir, "coupling_stability_audit.json")
    with open(output_file, 'w') as f:
        json.dump({
            'rb_results': rb_results,
            'am_results': am_results,
            'rb_coupling': rb_coupling,
            'am_coupling': am_coupling
        }, f, indent=2)

    print(f"\nAudit results saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Status: Coupling stability under transformation audit complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
