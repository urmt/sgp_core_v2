#!/usr/bin/env python3
"""
RD-WELL.5D.R3 — Operational Cross-Domain Comparison

Compare only operational phenomena across independent worlds:
- appearance
- disappearance
- repetition
- movement
- stabilization
- boundary formation

No C, no coupling, no theory.
"""

import numpy as np
import os
import json


def describe_operational_phenomena(field, field_name):
    """Describe operational phenomena for a field."""
    phenomena = {
        'field': field_name,
        'appearance': [],
        'disappearance': [],
        'repetition': [],
        'movement': [],
        'stabilization': [],
        'boundary_formation': []
    }

    # Appearance: How does the field change over time?
    for t in range(field.shape[0]):
        frame = field[t]
        mean_val = frame.mean()
        std_val = frame.std()
        min_val = frame.min()
        max_val = frame.max()

        phenomena['appearance'].append({
            'time': t,
            'mean': float(mean_val),
            'std': float(std_val),
            'range': [float(min_val), float(max_val)]
        })

    # Disappearance: Do values go to zero or constant?
    for t in range(field.shape[0]):
        frame = field[t]
        zero_fraction = (np.abs(frame) < 0.001).mean()
        constant_fraction = (frame.std() < 0.001).mean()

        phenomena['disappearance'].append({
            'time': t,
            'zero_fraction': float(zero_fraction),
            'constant_fraction': float(constant_fraction)
        })

    # Repetition: Do patterns repeat?
    if field.shape[0] > 1:
        similarities = []
        for t in range(1, field.shape[0]):
            prev_frame = field[t-1]
            curr_frame = field[t]
            # Normalized difference
            diff = np.abs(curr_frame - prev_frame).mean() / (np.abs(prev_frame).mean() + 1e-10)
            similarities.append(float(1.0 - min(diff, 1.0)))

        phenomena['repetition'] = similarities

    # Movement: How does the center of mass change?
    if field.shape[0] > 1:
        cm_history = []
        for t in range(field.shape[0]):
            frame = field[t]
            if frame.sum() > 0:
                y_cm = np.arange(frame.shape[0]).reshape(-1, 1) * frame / frame.sum()
                x_cm = np.arange(frame.shape[1]).reshape(1, -1) * frame / frame.sum()
                cm_history.append([float(x_cm.sum()), float(y_cm.sum())])
            else:
                cm_history.append([None, None])

        # Compute movement magnitude
        movement_magnitudes = []
        for t in range(1, len(cm_history)):
            if cm_history[t][0] is not None and cm_history[t-1][0] is not None:
                dx = cm_history[t][0] - cm_history[t-1][0]
                dy = cm_history[t][1] - cm_history[t-1][1]
                movement_magnitudes.append(float(np.sqrt(dx**2 + dy**2)))
            else:
                movement_magnitudes.append(None)

        phenomena['movement'] = {
            'cm_history': cm_history,
            'magnitudes': movement_magnitudes
        }

    # Stabilization: Does the rate of change decrease?
    if field.shape[0] > 2:
        frame_diffs = []
        for t in range(1, field.shape[0]):
            prev_frame = field[t-1]
            curr_frame = field[t]
            diff = np.abs(curr_frame - prev_frame).mean()
            frame_diffs.append(float(diff))

        # Check if differences are decreasing
        decreasing = all(frame_diffs[i] >= frame_diffs[i+1] for i in range(len(frame_diffs)-1))
        phenomena['stabilization'] = {
            'frame_diffs': frame_diffs,
            'decreasing': decreasing
        }

    # Boundary formation: What happens at edges?
    for t in range(min(3, field.shape[0])):
        frame = field[t]
        top_edge = frame[0:5].mean()
        bottom_edge = frame[-5:].mean()
        left_edge = frame[:, 0:5].mean()
        right_edge = frame[:, -5:].mean()

        phenomena['boundary_formation'].append({
            'time': t,
            'top': float(top_edge),
            'bottom': float(bottom_edge),
            'left': float(left_edge),
            'right': float(right_edge)
        })

    return phenomena


def compare_domains(domain1_phenomena, domain2_phenomena):
    """Compare operational phenomena between two domains."""
    comparison = {
        'domain1': domain1_phenomena['field'],
        'domain2': domain2_phenomena['field'],
        'similarities': [],
        'differences': []
    }

    # Compare appearance patterns
    d1_means = [p['mean'] for p in domain1_phenomena['appearance']]
    d2_means = [p['mean'] for p in domain2_phenomena['appearance']]

    # Normalize for comparison
    d1_range = max(d1_means) - min(d1_means) if max(d1_means) != min(d1_means) else 1
    d2_range = max(d2_means) - min(d2_means) if max(d2_means) != min(d2_means) else 1

    d1_normalized = [(m - min(d1_means)) / d1_range for m in d1_means]
    d2_normalized = [(m - min(d2_means)) / d2_range for m in d2_means]

    # Compute similarity
    if len(d1_normalized) == len(d2_normalized):
        mse = sum((d1 - d2)**2 for d1, d2 in zip(d1_normalized, d2_normalized)) / len(d1_normalized)
        comparison['similarities'].append({
            'phenomenon': 'appearance_trend',
            'similarity': 1.0 - min(mse, 1.0)
        })

    # Compare stabilization
    if domain1_phenomena['stabilization'] and domain2_phenomena['stabilization']:
        d1_diffs = domain1_phenomena['stabilization']['frame_diffs']
        d2_diffs = domain2_phenomena['stabilization']['frame_diffs']

        # Check if both stabilize
        if domain1_phenomena['stabilization']['decreasing'] and domain2_phenomena['stabilization']['decreasing']:
            comparison['similarities'].append({
                'phenomenon': 'stabilization_pattern',
                'similarity': 1.0
            })
        elif not domain1_phenomena['stabilization']['decreasing'] and not domain2_phenomena['stabilization']['decreasing']:
            comparison['similarities'].append({
                'phenomenon': 'stabilization_pattern',
                'similarity': 0.5
            })
        else:
            comparison['differences'].append({
                'phenomenon': 'stabilization_pattern',
                'domain1_decreasing': domain1_phenomena['stabilization']['decreasing'],
                'domain2_decreasing': domain2_phenomena['stabilization']['decreasing']
            })

    # Compare boundary formation
    if domain1_phenomena['boundary_formation'] and domain2_phenomena['boundary_formation']:
        d1_boundary = domain1_phenomena['boundary_formation'][0]
        d2_boundary = domain2_phenomena['boundary_formation'][0]

        # Check if boundaries are symmetric
        d1_symmetric = abs(d1_boundary['top'] - d1_boundary['bottom']) < 0.01
        d2_symmetric = abs(d2_boundary['top'] - d2_boundary['bottom']) < 0.01

        if d1_symmetric == d2_symmetric:
            comparison['similarities'].append({
                'phenomenon': 'boundary_symmetry',
                'similarity': 1.0
            })
        else:
            comparison['differences'].append({
                'phenomenon': 'boundary_symmetry',
                'domain1_symmetric': d1_symmetric,
                'domain2_symmetric': d2_symmetric
            })

    return comparison


def main():
    print("RD-WELL.5D.R3 — Operational Cross-Domain Comparison")
    print("=" * 60)
    print("Compare only operational phenomena across independent worlds:")
    print("- appearance")
    print("- disappearance")
    print("- repetition")
    print("- movement")
    print("- stabilization")
    print("- boundary formation")
    print("=" * 60)

    output_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r3"
    os.makedirs(output_dir, exist_ok=True)

    # Load all fields
    all_fields = []

    # Rayleigh-Bénard
    rb_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/rayleigh_benard_frames"
    buoyancy = np.load(os.path.join(rb_dir, 'buoyancy.npy'))
    pressure = np.load(os.path.join(rb_dir, 'pressure.npy'))
    velocity_mag = np.load(os.path.join(rb_dir, 'velocity_magnitude.npy'))

    all_fields.append(('Rayleigh-Bénard', 'buoyancy', buoyancy))
    all_fields.append(('Rayleigh-Bénard', 'pressure', pressure))
    all_fields.append(('Rayleigh-Bénard', 'velocity_mag', velocity_mag))

    # Active Matter
    am_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/active_matter_frames"
    concentration = np.load(os.path.join(am_dir, 'concentration.npy'))
    velocity_mag_am = np.load(os.path.join(am_dir, 'velocity_magnitude.npy'))

    all_fields.append(('Active Matter', 'concentration', concentration))
    all_fields.append(('Active Matter', 'velocity_mag', velocity_mag_am))

    # Describe operational phenomena for each field
    print("\n" + "=" * 60)
    print("OPERATIONAL PHENOMENA DESCRIPTION")
    print("=" * 60)

    all_phenomena = {}
    for domain, field_name, field in all_fields:
        field_id = f"{domain}_{field_name}"
        print(f"\n{'#'*60}")
        print(f"FIELD: {field_id}")
        print(f"{'#'*60}")

        phenomena = describe_operational_phenomena(field, field_id)
        all_phenomena[field_id] = phenomena

        # Print summary
        print(f"  Appearance: {len(phenomena['appearance'])} frames")
        print(f"  Disappearance: {len(phenomena['disappearance'])} frames")
        print(f"  Repetition: {len(phenomena['repetition'])} similarities")
        if phenomena['movement']:
            print(f"  Movement: {len(phenomena['movement']['magnitudes'])} magnitudes")
        if phenomena['stabilization']:
            print(f"  Stabilization: decreasing={phenomena['stabilization']['decreasing']}")
        print(f"  Boundary formation: {len(phenomena['boundary_formation'])} frames")

    # Compare across domains
    print("\n" + "=" * 60)
    print("CROSS-DOMAIN COMPARISON")
    print("=" * 60)

    comparisons = []

    # Compare Rayleigh-Bénard buoyancy with Active Matter concentration
    rb_buoyancy = all_phenomena['Rayleigh-Bénard_buoyancy']
    am_concentration = all_phenomena['Active Matter_concentration']

    comparison = compare_domains(rb_buoyancy, am_concentration)
    comparisons.append(comparison)

    print(f"\n{comparison['domain1']} vs {comparison['domain2']}")
    print(f"  Similarities: {len(comparison['similarities'])}")
    print(f"  Differences: {len(comparison['differences'])}")

    for sim in comparison['similarities']:
        print(f"    {sim['phenomenon']}: {sim['similarity']:.3f}")

    for diff in comparison['differences']:
        print(f"    {diff['phenomenon']}: {diff}")

    # Compare Rayleigh-Bénard velocity with Active Matter velocity
    rb_velocity = all_phenomena['Rayleigh-Bénard_velocity_mag']
    am_velocity = all_phenomena['Active Matter_velocity_mag']

    comparison = compare_domains(rb_velocity, am_velocity)
    comparisons.append(comparison)

    print(f"\n{comparison['domain1']} vs {comparison['domain2']}")
    print(f"  Similarities: {len(comparison['similarities'])}")
    print(f"  Differences: {len(comparison['differences'])}")

    for sim in comparison['similarities']:
        print(f"    {sim['phenomenon']}: {sim['similarity']:.3f}")

    for diff in comparison['differences']:
        print(f"    {diff['phenomenon']}: {diff}")

    # Save results
    output_file = os.path.join(output_dir, "cross_domain_comparison.json")
    with open(output_file, 'w') as f:
        json.dump({
            'phenomena': all_phenomena,
            'comparisons': comparisons
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Status: Operational comparison complete. No metrics computed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
