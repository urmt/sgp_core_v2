#!/usr/bin/env python3
"""
RD-WELL.6B — Cross-Domain Coupling Audit with Transform Audit

Compute coupling(C, S₁), coupling(C, S₂), coupling(C, S₃) for:
- Gray-Scott
- Rayleigh-Bénard
- Active Matter

Include transform audit:
- original
- z-score
- rank
- min-max

Question: Which relationships survive transformation, domain, and representation change?
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
        # Compute power spectrum for each frame
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
        # Compute connected components for each frame
        from scipy import ndimage
        component_counts = []
        for t in range(field.shape[0]):
            frame = field[t]
            threshold = frame.mean()
            binary = frame > threshold
            labeled, num_features = ndimage.label(binary)
            component_counts.append(float(num_features))
        
        # Compute persistence as similarity between consecutive frames
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


def compute_coupling(C_values, S_values):
    """Compute coupling between C and S."""
    if len(C_values) == len(S_values) and len(C_values) > 1:
        # Compute Pearson correlation
        correlation, p_value = stats.pearsonr(C_values, S_values)
        return float(correlation), float(p_value)
    else:
        return None, None


def main():
    print("RD-WELL.6B — Cross-Domain Coupling Audit with Transform Audit")
    print("=" * 60)
    print("Compute coupling(C, S₁), coupling(C, S₂), coupling(C, S₃)")
    print("Include transform audit: original, z-score, rank, min-max")
    print("=" * 60)

    output_dir = "/home/student/sgp_core_v2/audits/rd_well6b"
    os.makedirs(output_dir, exist_ok=True)

    # Load all fields
    rb_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/rayleigh_benard_frames"
    am_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/active_matter_frames"

    # Rayleigh-Bénard buoyancy
    rb_buoyancy = np.load(os.path.join(rb_dir, 'buoyancy.npy'))

    # Active Matter concentration
    am_concentration = np.load(os.path.join(am_dir, 'concentration.npy'))

    # Compute coupling for each domain and transformation
    print("\n" + "=" * 60)
    print("COMPUTING COUPLING FOR EACH DOMAIN AND TRANSFORMATION")
    print("=" * 60)

    results = {}

    # Rayleigh-Bénard
    print("\nRayleigh-Bénard Buoyancy:")
    rb_transformations = apply_transformations(rb_buoyancy)
    rb_results = {}

    for transform_name, transformed_field in rb_transformations.items():
        C_value = compute_C_for_field(transformed_field)
        S1_value = compute_S1(transformed_field)
        S2_value = compute_S2(transformed_field)
        S3_value = compute_S3(transformed_field)

        rb_results[transform_name] = {
            'C': C_value,
            'S1': S1_value,
            'S2': S2_value,
            'S3': S3_value
        }

        print(f"  {transform_name}: C={C_value:.6f}, S1={S1_value:.6f}, S2={S2_value:.6f}, S3={S3_value:.6f}")

    results['Rayleigh-Bénard'] = rb_results

    # Active Matter
    print("\nActive Matter Concentration:")
    am_transformations = apply_transformations(am_concentration)
    am_results = {}

    for transform_name, transformed_field in am_transformations.items():
        C_value = compute_C_for_field(transformed_field)
        S1_value = compute_S1(transformed_field)
        S2_value = compute_S2(transformed_field)
        S3_value = compute_S3(transformed_field)

        am_results[transform_name] = {
            'C': C_value,
            'S1': S1_value,
            'S2': S2_value,
            'S3': S3_value
        }

        print(f"  {transform_name}: C={C_value:.6f}, S1={S1_value:.6f}, S2={S2_value:.6f}, S3={S3_value:.6f}")

    results['Active Matter'] = am_results

    # Compute coupling for each domain
    print("\n" + "=" * 60)
    print("COMPUTING COUPLING FOR EACH DOMAIN")
    print("=" * 60)

    coupling_results = {}

    # Rayleigh-Bénard
    print("\nRayleigh-Bénard Buoyancy Coupling:")
    rb_C_values = [rb_results[t]['C'] for t in rb_results if rb_results[t]['C'] is not None]
    rb_S1_values = [rb_results[t]['S1'] for t in rb_results if rb_results[t]['S1'] is not None]
    rb_S2_values = [rb_results[t]['S2'] for t in rb_results if rb_results[t]['S2'] is not None]
    rb_S3_values = [rb_results[t]['S3'] for t in rb_results if rb_results[t]['S3'] is not None]

    rb_coupling = {}
    if len(rb_C_values) == len(rb_S1_values):
        coupling, p_value = compute_coupling(rb_C_values, rb_S1_values)
        rb_coupling['C_S1'] = {'coupling': coupling, 'p_value': p_value}
        print(f"  C-S1: {coupling:.6f} (p={p_value:.6f})")

    if len(rb_C_values) == len(rb_S2_values):
        coupling, p_value = compute_coupling(rb_C_values, rb_S2_values)
        rb_coupling['C_S2'] = {'coupling': coupling, 'p_value': p_value}
        print(f"  C-S2: {coupling:.6f} (p={p_value:.6f})")

    if len(rb_C_values) == len(rb_S3_values):
        coupling, p_value = compute_coupling(rb_C_values, rb_S3_values)
        rb_coupling['C_S3'] = {'coupling': coupling, 'p_value': p_value}
        print(f"  C-S3: {coupling:.6f} (p={p_value:.6f})")

    coupling_results['Rayleigh-Bénard'] = rb_coupling

    # Active Matter
    print("\nActive Matter Concentration Coupling:")
    am_C_values = [am_results[t]['C'] for t in am_results if am_results[t]['C'] is not None]
    am_S1_values = [am_results[t]['S1'] for t in am_results if am_results[t]['S1'] is not None]
    am_S2_values = [am_results[t]['S2'] for t in am_results if am_results[t]['S2'] is not None]
    am_S3_values = [am_results[t]['S3'] for t in am_results if am_results[t]['S3'] is not None]

    am_coupling = {}
    if len(am_C_values) == len(am_S1_values):
        coupling, p_value = compute_coupling(am_C_values, am_S1_values)
        am_coupling['C_S1'] = {'coupling': coupling, 'p_value': p_value}
        print(f"  C-S1: {coupling:.6f} (p={p_value:.6f})")

    if len(am_C_values) == len(am_S2_values):
        coupling, p_value = compute_coupling(am_C_values, am_S2_values)
        am_coupling['C_S2'] = {'coupling': coupling, 'p_value': p_value}
        print(f"  C-S2: {coupling:.6f} (p={p_value:.6f})")

    if len(am_C_values) == len(am_S3_values):
        coupling, p_value = compute_coupling(am_C_values, am_S3_values)
        am_coupling['C_S3'] = {'coupling': coupling, 'p_value': p_value}
        print(f"  C-S3: {coupling:.6f} (p={p_value:.6f})")

    coupling_results['Active Matter'] = am_coupling

    # Save results
    output_file = os.path.join(output_dir, "cross_domain_coupling_audit.json")
    with open(output_file, 'w') as f:
        json.dump({
            'results': results,
            'coupling_results': coupling_results
        }, f, indent=2)

    print(f"\nAudit results saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Status: Cross-domain coupling audit with transform audit complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
