#!/usr/bin/env python3
"""
RD-WELL.5D.R3 — Cross-Domain Comparison (Decontaminated)

Compare only operational phenomena across independent worlds using ONLY Layer 0 and Layer 1 descriptors.

Layer 0 — Raw: mean, variance, entropy, power spectrum, component count, frame difference
Layer 1 — Derived: stabilization, boundary formation, periodicity, drift, repetition

Layer 2 — Interpretive: organization, coherence, adaptation, information (FORBIDDEN)
"""

import numpy as np
import os
import json


def compute_layer_0_descriptors(field):
    """Compute Layer 0 (raw) descriptors for a field."""
    descriptors = {}

    # Mean over time
    means = []
    for t in range(field.shape[0]):
        means.append(float(field[t].mean()))
    descriptors['mean_over_time'] = means

    # Variance over time
    variances = []
    for t in range(field.shape[0]):
        variances.append(float(field[t].var()))
    descriptors['variance_over_time'] = variances

    # Frame-to-frame difference
    frame_diffs = []
    for t in range(1, field.shape[0]):
        diff = np.abs(field[t] - field[t-1]).mean()
        frame_diffs.append(float(diff))
    descriptors['frame_to_frame_difference'] = frame_diffs

    # Spatial autocorrelation (simplified)
    autocorrelations = []
    for t in range(field.shape[0]):
        frame = field[t]
        # Simple autocorrelation: correlation with shifted version
        if frame.shape[0] > 1:
            shifted = np.roll(frame, 1, axis=0)
            corr = np.corrcoef(frame.flatten(), shifted.flatten())[0, 1]
            autocorrelations.append(float(corr) if not np.isnan(corr) else 0.0)
        else:
            autocorrelations.append(0.0)
    descriptors['spatial_autocorrelation'] = autocorrelations

    return descriptors


def compute_layer_1_descriptors(field):
    """Compute Layer 1 (derived) descriptors for a field."""
    descriptors = {}

    # Stabilization (frame difference trend)
    frame_diffs = []
    for t in range(1, field.shape[0]):
        diff = np.abs(field[t] - field[t-1]).mean()
        frame_diffs.append(float(diff))

    if len(frame_diffs) > 1:
        # Check if differences are decreasing
        decreasing = all(frame_diffs[i] >= frame_diffs[i+1] for i in range(len(frame_diffs)-1))
        descriptors['stabilization_decreasing'] = decreasing
        descriptors['stabilization_rate'] = float(np.mean(frame_diffs))
    else:
        descriptors['stabilization_decreasing'] = None
        descriptors['stabilization_rate'] = None

    # Boundary formation
    boundary_stats = []
    for t in range(min(3, field.shape[0])):
        frame = field[t]
        top_edge = float(frame[0:5].mean())
        bottom_edge = float(frame[-5:].mean())
        left_edge = float(frame[:, 0:5].mean())
        right_edge = float(frame[:, -5:].mean())

        boundary_stats.append({
            'time': t,
            'top': top_edge,
            'bottom': bottom_edge,
            'left': left_edge,
            'right': right_edge
        })
    descriptors['boundary_formation'] = boundary_stats

    # Movement (center of mass drift)
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

    descriptors['movement_magnitudes'] = movement_magnitudes

    # Repetition (similarity between consecutive frames)
    similarities = []
    for t in range(1, field.shape[0]):
        prev_frame = field[t-1]
        curr_frame = field[t]
        # Normalized difference
        diff = np.abs(curr_frame - prev_frame).mean() / (np.abs(prev_frame).mean() + 1e-10)
        similarities.append(float(1.0 - min(diff, 1.0)))
    descriptors['repetition_similarities'] = similarities

    return descriptors


def compare_domains_layer_0(rb_descriptors, am_descriptors):
    """Compare Layer 0 descriptors between Rayleigh-Bénard and Active Matter."""
    comparison = {
        'layer_0': {},
        'similarities': []
    }

    # Compare mean trends
    rb_means = rb_descriptors['mean_over_time']
    am_means = am_descriptors['mean_over_time']

    # Normalize for comparison
    rb_range = max(rb_means) - min(rb_means) if max(rb_means) != min(rb_means) else 1
    am_range = max(am_means) - min(am_means) if max(am_means) != min(am_means) else 1

    rb_normalized = [(m - min(rb_means)) / rb_range for m in rb_means]
    am_normalized = [(m - min(am_means)) / am_range for m in am_means]

    if len(rb_normalized) == len(am_normalized):
        mse = sum((rb - am)**2 for rb, am in zip(rb_normalized, am_normalized)) / len(rb_normalized)
        comparison['similarities'].append({
            'phenomenon': 'mean_intensity_trend',
            'layer': 'Layer_0',
            'similarity': 1.0 - min(mse, 1.0)
        })

    # Compare frame difference trends
    rb_diffs = rb_descriptors['frame_to_frame_difference']
    am_diffs = am_descriptors['frame_to_frame_difference']

    if len(rb_diffs) == len(am_diffs):
        # Normalize
        rb_diff_range = max(rb_diffs) - min(rb_diffs) if max(rb_diffs) != min(rb_diffs) else 1
        am_diff_range = max(am_diffs) - min(am_diffs) if max(am_diffs) != min(am_diffs) else 1

        rb_diff_normalized = [(d - min(rb_diffs)) / rb_diff_range for d in rb_diffs]
        am_diff_normalized = [(d - min(am_diffs)) / am_diff_range for d in am_diffs]

        mse = sum((rb - am)**2 for rb, am in zip(rb_diff_normalized, am_diff_normalized)) / len(rb_diff_normalized)
        comparison['similarities'].append({
            'phenomenon': 'frame_difference_trend',
            'layer': 'Layer_0',
            'similarity': 1.0 - min(mse, 1.0)
        })

    return comparison


def compare_domains_layer_1(rb_descriptors, am_descriptors):
    """Compare Layer 1 descriptors between Rayleigh-Bénard and Active Matter."""
    comparison = {
        'layer_1': {},
        'similarities': [],
        'differences': []
    }

    # Compare stabilization
    if rb_descriptors['stabilization_decreasing'] is not None and am_descriptors['stabilization_decreasing'] is not None:
        if rb_descriptors['stabilization_decreasing'] == am_descriptors['stabilization_decreasing']:
            comparison['similarities'].append({
                'phenomenon': 'stabilization_pattern',
                'layer': 'Layer_1',
                'similarity': 1.0
            })
        else:
            comparison['differences'].append({
                'phenomenon': 'stabilization_pattern',
                'layer': 'Layer_1',
                'rb_decreasing': rb_descriptors['stabilization_decreasing'],
                'am_decreasing': am_descriptors['stabilization_decreasing']
            })

    # Compare boundary formation
    if rb_descriptors['boundary_formation'] and am_descriptors['boundary_formation']:
        rb_boundary = rb_descriptors['boundary_formation'][0]
        am_boundary = am_descriptors['boundary_formation'][0]

        # Check if boundaries are symmetric
        rb_symmetric = abs(rb_boundary['top'] - rb_boundary['bottom']) < 0.01
        am_symmetric = abs(am_boundary['top'] - am_boundary['bottom']) < 0.01

        if rb_symmetric == am_symmetric:
            comparison['similarities'].append({
                'phenomenon': 'boundary_symmetry',
                'layer': 'Layer_1',
                'similarity': 1.0
            })
        else:
            comparison['differences'].append({
                'phenomenon': 'boundary_symmetry',
                'layer': 'Layer_1',
                'rb_symmetric': rb_symmetric,
                'am_symmetric': am_symmetric
            })

    return comparison


def main():
    print("RD-WELL.5D.R3 — Cross-Domain Comparison (Decontaminated)")
    print("=" * 60)
    print("Using ONLY Layer 0 and Layer 1 descriptors.")
    print("Layer 2 (interpretive) descriptors are FORBIDDEN.")
    print("=" * 60)

    output_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r3_decontaminated"
    os.makedirs(output_dir, exist_ok=True)

    # Load all fields
    rb_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/rayleigh_benard_frames"
    am_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/active_matter_frames"

    # Rayleigh-Bénard buoyancy
    rb_buoyancy = np.load(os.path.join(rb_dir, 'buoyancy.npy'))
    # Active Matter concentration
    am_concentration = np.load(os.path.join(am_dir, 'concentration.npy'))

    # Compute descriptors
    print("\n" + "=" * 60)
    print("COMPUTING LAYER 0 DESCRIPTORS")
    print("=" * 60)

    rb_buoyancy_l0 = compute_layer_0_descriptors(rb_buoyancy)
    am_concentration_l0 = compute_layer_0_descriptors(am_concentration)

    print(f"RB_buoyancy Layer 0: {list(rb_buoyancy_l0.keys())}")
    print(f"AM_concentration Layer 0: {list(am_concentration_l0.keys())}")

    print("\n" + "=" * 60)
    print("COMPUTING LAYER 1 DESCRIPTORS")
    print("=" * 60)

    rb_buoyancy_l1 = compute_layer_1_descriptors(rb_buoyancy)
    am_concentration_l1 = compute_layer_1_descriptors(am_concentration)

    print(f"RB_buoyancy Layer 1: {list(rb_buoyancy_l1.keys())}")
    print(f"AM_concentration Layer 1: {list(am_concentration_l1.keys())}")

    # Compare domains
    print("\n" + "=" * 60)
    print("CROSS-DOMAIN COMPARISON")
    print("=" * 60)

    # Layer 0 comparison
    print("\nLayer 0 Comparison:")
    l0_comparison = compare_domains_layer_0(rb_buoyancy_l0, am_concentration_l0)

    for sim in l0_comparison['similarities']:
        print(f"  {sim['phenomenon']}: {sim['similarity']:.3f} (Layer: {sim['layer']})")

    # Layer 1 comparison
    print("\nLayer 1 Comparison:")
    l1_comparison = compare_domains_layer_1(rb_buoyancy_l1, am_concentration_l1)

    for sim in l1_comparison['similarities']:
        print(f"  {sim['phenomenon']}: {sim['similarity']:.3f} (Layer: {sim['layer']})")

    for diff in l1_comparison['differences']:
        print(f"  {diff['phenomenon']}: {diff} (Layer: {diff['layer']})")

    # Save results
    output_file = os.path.join(output_dir, "cross_domain_comparison_decontaminated.json")
    with open(output_file, 'w') as f:
        json.dump({
            'rb_buoyancy_layer_0': rb_buoyancy_l0,
            'rb_buoyancy_layer_1': rb_buoyancy_l1,
            'am_concentration_layer_0': am_concentration_l0,
            'am_concentration_layer_1': am_concentration_l1,
            'l0_comparison': l0_comparison,
            'l1_comparison': l1_comparison
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Status: Cross-domain comparison complete. Using only Layer 0 and Layer 1 descriptors.")
    print("=" * 60)


if __name__ == "__main__":
    main()
