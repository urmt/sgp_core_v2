#!/usr/bin/env python3
"""
RD-WELL.6A — Cross-Domain C Computation with Transform Audit

Compute C under multiple field transformations for each domain:
- original
- z-score
- rank
- min-max

Report: ΔC_transform

Question: Is C itself representation-stable?
"""

import numpy as np
import os
import sys
import json

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
    # Reshape field for C computation
    # C expects (batch, time, features) or similar
    if field.ndim == 3:
        # Flatten spatial dimensions
        batch_size = field.shape[0]
        time_steps = field.shape[1] if field.shape[1] < field.shape[2] else field.shape[2]
        features = field.shape[1] * field.shape[2] if field.shape[1] > field.shape[2] else field.shape[1] * field.shape[2]
        
        # Reshape to (batch, time, features)
        reshaped = field.reshape(batch_size, -1)
        
        # For C, we need multiple time steps
        # Use the field as a single batch with multiple features
        C_value = compute_C(reshaped)
        return float(C_value)
    else:
        return None


def main():
    print("RD-WELL.6A — Cross-Domain C Computation with Transform Audit")
    print("=" * 60)
    print("Compute C under multiple field transformations for each domain.")
    print("Report: ΔC_transform")
    print("=" * 60)

    output_dir = "/home/student/sgp_core_v2/audits/rd_well6a"
    os.makedirs(output_dir, exist_ok=True)

    # Load all fields
    rb_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/rayleigh_benard_frames"
    am_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/active_matter_frames"

    # Rayleigh-Bénard buoyancy
    rb_buoyancy = np.load(os.path.join(rb_dir, 'buoyancy.npy'))

    # Active Matter concentration
    am_concentration = np.load(os.path.join(am_dir, 'concentration.npy'))

    # Compute C under transformations
    print("\n" + "=" * 60)
    print("COMPUTING C UNDER TRANSFORMATIONS")
    print("=" * 60)

    # Rayleigh-Bénard
    print("\nRayleigh-Bénard Buoyancy:")
    rb_transformations = apply_transformations(rb_buoyancy)
    rb_C_values = {}

    for transform_name, transformed_field in rb_transformations.items():
        C_value = compute_C_for_field(transformed_field)
        rb_C_values[transform_name] = C_value
        print(f"  {transform_name}: C = {C_value:.6f}")

    # Active Matter
    print("\nActive Matter Concentration:")
    am_transformations = apply_transformations(am_concentration)
    am_C_values = {}

    for transform_name, transformed_field in am_transformations.items():
        C_value = compute_C_for_field(transformed_field)
        am_C_values[transform_name] = C_value
        print(f"  {transform_name}: C = {C_value:.6f}")

    # Compute ΔC_transform
    print("\n" + "=" * 60)
    print("COMPUTING ΔC_transform")
    print("=" * 60)

    # Rayleigh-Bénard
    print("\nRayleigh-Bénard Buoyancy ΔC_transform:")
    rb_delta_C = {}
    original_C = rb_C_values['original']
    for transform_name, C_value in rb_C_values.items():
        if C_value is not None and original_C is not None:
            delta_C = abs(C_value - original_C)
            rb_delta_C[transform_name] = delta_C
            print(f"  {transform_name}: ΔC = {delta_C:.6f}")

    # Active Matter
    print("\nActive Matter Concentration ΔC_transform:")
    am_delta_C = {}
    original_C = am_C_values['original']
    for transform_name, C_value in am_C_values.items():
        if C_value is not None and original_C is not None:
            delta_C = abs(C_value - original_C)
            am_delta_C[transform_name] = delta_C
            print(f"  {transform_name}: ΔC = {delta_C:.6f}")

    # Save results
    output_file = os.path.join(output_dir, "cross_domain_C_transform_audit.json")
    with open(output_file, 'w') as f:
        json.dump({
            'rb_C_values': rb_C_values,
            'am_C_values': am_C_values,
            'rb_delta_C': rb_delta_C,
            'am_delta_C': am_delta_C
        }, f, indent=2)

    print(f"\nAudit results saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Status: Cross-domain C computation with transform audit complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
