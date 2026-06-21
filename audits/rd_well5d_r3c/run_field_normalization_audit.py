#!/usr/bin/env python3
"""
RD-WELL.5D.R3C — Field Normalization Audit

Question: Are measurements invariant under admissible field transformations?

Example transformations:
- x (original)
- log(x) (logarithmic)
- z-score(x) (standardized)
- rank(x) (rank-based)
- rescaled x (min-max normalized)

If C or descriptors change dramatically under harmless transformations,
we have discovered another hidden dependency.

This audit attacks:
- measurement dependence
- representation dependence
- unit dependence
"""

import numpy as np
import os
import json


def apply_transformations(field):
    """Apply admissible field transformations."""
    transformations = {}

    # Original
    transformations['original'] = field

    # Logarithmic (add small constant to avoid log(0))
    transformations['log'] = np.log(field + 1e-10)

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


def compute_measurement_invariance(field, field_name, domain_name):
    """Compute measurement invariance under field transformations."""
    transformations = apply_transformations(field)

    invariance = {}

    for transform_name, transformed_field in transformations.items():
        measurements = {}

        # Mean
        measurements['mean'] = float(transformed_field.mean())

        # Variance
        measurements['variance'] = float(transformed_field.var())

        # Frame-to-frame difference
        if transformed_field.ndim == 3 and transformed_field.shape[0] > 1:
            frame_diffs = []
            for t in range(1, transformed_field.shape[0]):
                diff = np.abs(transformed_field[t] - transformed_field[t-1]).mean()
                frame_diffs.append(float(diff))
            measurements['frame_diff_mean'] = float(np.mean(frame_diffs))
        else:
            measurements['frame_diff_mean'] = None

        invariance[transform_name] = measurements

    return invariance


def compute_invariance_scores(invariance):
    """Compute invariance scores across transformations."""
    scores = {}

    # Get original measurements
    original = invariance['original']

    for measurement in original.keys():
        if original[measurement] is None:
            continue

        original_value = original[measurement]
        transform_values = []

        for transform_name, measurements in invariance.items():
            if transform_name == 'original':
                continue
            if measurements[measurement] is not None:
                transform_values.append(measurements[measurement])

        if transform_values and original_value != 0:
            # Compute coefficient of variation across transformations
            values = [original_value] + transform_values
            mean_val = np.mean(values)
            std_val = np.std(values)
            cv = std_val / abs(mean_val) if mean_val != 0 else 0

            # Invariance score: 1 - cv (higher is more invariant)
            scores[measurement] = 1.0 - min(cv, 1.0)
        else:
            scores[measurement] = None

    return scores


def main():
    print("RD-WELL.5D.R3C — Field Normalization Audit")
    print("=" * 60)
    print("Question: Are measurements invariant under admissible field transformations?")
    print("=" * 60)

    output_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r3c"
    os.makedirs(output_dir, exist_ok=True)

    # Load all fields
    rb_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/rayleigh_benard_frames"
    am_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/active_matter_frames"

    # Rayleigh-Bénard buoyancy
    rb_buoyancy = np.load(os.path.join(rb_dir, 'buoyancy.npy'))

    # Active Matter concentration
    am_concentration = np.load(os.path.join(am_dir, 'concentration.npy'))

    # Compute measurement invariance
    print("\n" + "=" * 60)
    print("COMPUTING MEASUREMENT INVARIANCE")
    print("=" * 60)

    rb_invariance = compute_measurement_invariance(rb_buoyancy, 'buoyancy', 'Rayleigh-Bénard')
    am_invariance = compute_measurement_invariance(am_concentration, 'concentration', 'Active Matter')

    # Compute invariance scores
    print("\n" + "=" * 60)
    print("COMPUTING INVARIANCE SCORES")
    print("=" * 60)

    rb_scores = compute_invariance_scores(rb_invariance)
    am_scores = compute_invariance_scores(am_invariance)

    print("\nRayleigh-Bénard Buoyancy Invariance Scores:")
    for measurement, score in rb_scores.items():
        if score is not None:
            print(f"  {measurement}: {score:.3f}")
        else:
            print(f"  {measurement}: N/A")

    print("\nActive Matter Concentration Invariance Scores:")
    for measurement, score in am_scores.items():
        if score is not None:
            print(f"  {measurement}: {score:.3f}")
        else:
            print(f"  {measurement}: N/A")

    # Save results
    output_file = os.path.join(output_dir, "field_normalization_audit.json")
    with open(output_file, 'w') as f:
        json.dump({
            'rb_invariance': rb_invariance,
            'am_invariance': am_invariance,
            'rb_scores': rb_scores,
            'am_scores': am_scores
        }, f, indent=2)

    print(f"\nAudit results saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Status: Field normalization audit complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
