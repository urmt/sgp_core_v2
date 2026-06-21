#!/usr/bin/env python3
"""
RD-WELL.5D.R2 — Blind Operational Reconnaissance

Like RD-WELL.2: describe only appearance, disappearance, repetition, stabilization, boundary formation, movement.

Forbidden: coherence, organization, emergence, complexity, information, adaptation.

No metrics. No C. No stabilization. Only operational description.
"""

import numpy as np
import os


def compute_operational_quantities(field):
    """Compute operational quantities for a field."""
    # Compute basic statistics
    mean = field.mean()
    std = field.std()
    min_val = field.min()
    max_val = field.max()

    # Compute frame-to-frame changes
    if field.shape[0] > 1:
        frame_diff = np.abs(np.diff(field, axis=0)).mean()
    else:
        frame_diff = 0.0

    # Compute spatial gradients
    if field.ndim >= 3:
        # Compute gradient in x and y directions
        grad_x = np.gradient(field, axis=-2)
        grad_y = np.gradient(field, axis=-1)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2).mean()
    else:
        grad_mag = 0.0

    return {
        'mean': float(mean),
        'std': float(std),
        'min': float(min_val),
        'max': float(max_val),
        'frame_diff': float(frame_diff),
        'gradient_magnitude': float(grad_mag),
    }


def describe_pattern(name, field, field_name):
    """Describe a pattern operationally."""
    print(f"\n{'='*60}")
    print(f"PATTERN: {name} - {field_name}")
    print(f"{'='*60}")

    print(f"\nField shape: {field.shape}")

    # Compute operational quantities
    quantities = compute_operational_quantities(field)

    print(f"\nOperational quantities:")
    print(f"  Mean: {quantities['mean']:.4f}")
    print(f"  Std: {quantities['std']:.4f}")
    print(f"  Min: {quantities['min']:.4f}")
    print(f"  Max: {quantities['max']:.4f}")
    print(f"  Frame-to-frame change: {quantities['frame_diff']:.4f}")
    print(f"  Gradient magnitude: {quantities['gradient_magnitude']:.4f}")

    # Describe appearance over time
    print(f"\nAppearance over time:")
    for t in range(min(5, field.shape[0])):
        frame = field[t]
        print(f"  t={t}: mean={frame.mean():.4f}, std={frame.std():.4f}")

    # Describe boundary formation
    print(f"\nBoundary formation:")
    if field.ndim >= 3:
        # Check for boundary effects
        for t in range(min(3, field.shape[0])):
            frame = field[t]
            # Check edges
            top_edge = frame[0:5].mean()
            bottom_edge = frame[-5:].mean()
            left_edge = frame[:, 0:5].mean()
            right_edge = frame[:, -5:].mean()
            print(f"  t={t}: top={top_edge:.4f}, bottom={bottom_edge:.4f}, left={left_edge:.4f}, right={right_edge:.4f}")

    # Describe movement
    print(f"\nMovement:")
    if field.shape[0] > 1:
        # Compute center of mass over time
        for t in range(min(5, field.shape[0])):
            frame = field[t]
            # Simple center of mass (weighted by field value)
            if frame.sum() > 0:
                y_cm = np.arange(frame.shape[0]).reshape(-1, 1) * frame / frame.sum()
                x_cm = np.arange(frame.shape[1]).reshape(1, -1) * frame / frame.sum()
                print(f"  t={t}: center_of_mass=({x_cm.sum():.2f}, {y_cm.sum():.2f})")
            else:
                print(f"  t={t}: center_of_mass=(N/A, N/A)")

    return quantities


def main():
    print("RD-WELL.5D.R2 — Blind Operational Reconnaissance")
    print("=" * 60)
    print("Describe only: appearance, disappearance, repetition, stabilization, boundary formation, movement.")
    print("Forbidden: coherence, organization, emergence, complexity, information, adaptation.")
    print("=" * 60)

    output_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r2"
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    # ============================================================
    # Rayleigh-Bénard
    # ============================================================
    print("\n" + "=" * 60)
    print("RAYLEIGH-BÉNARD")
    print("=" * 60)

    rb_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/rayleigh_benard_frames"

    # Load buoyancy
    buoyancy = np.load(os.path.join(rb_dir, 'buoyancy.npy'))
    rb_buoyancy = describe_pattern('rayleigh_benard', buoyancy, 'buoyancy')

    # Load pressure
    pressure = np.load(os.path.join(rb_dir, 'pressure.npy'))
    rb_pressure = describe_pattern('rayleigh_benard', pressure, 'pressure')

    # Load velocity magnitude
    velocity_mag = np.load(os.path.join(rb_dir, 'velocity_magnitude.npy'))
    rb_velocity = describe_pattern('rayleigh_benard', velocity_mag, 'velocity_magnitude')

    results['rayleigh_benard'] = {
        'buoyancy': rb_buoyancy,
        'pressure': rb_pressure,
        'velocity_magnitude': rb_velocity,
    }

    # ============================================================
    # Active Matter
    # ============================================================
    print("\n" + "=" * 60)
    print("ACTIVE MATTER")
    print("=" * 60)

    am_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/active_matter_frames"

    # Load concentration
    concentration = np.load(os.path.join(am_dir, 'concentration.npy'))
    am_concentration = describe_pattern('active_matter', concentration, 'concentration')

    # Load velocity magnitude
    velocity_mag = np.load(os.path.join(am_dir, 'velocity_magnitude.npy'))
    am_velocity = describe_pattern('active_matter', velocity_mag, 'velocity_magnitude')

    results['active_matter'] = {
        'concentration': am_concentration,
        'velocity_magnitude': am_velocity,
    }

    # ============================================================
    # Save results
    # ============================================================
    output_file = os.path.join(output_dir, "blind_operational_reconnaissance.json")
    with open(output_file, 'w') as f:
        import json
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print("\nRayleigh-Bénard:")
    print(f"  Buoyancy: mean={rb_buoyancy['mean']:.4f}, std={rb_buoyancy['std']:.4f}")
    print(f"  Pressure: mean={rb_pressure['mean']:.4f}, std={rb_pressure['std']:.4f}")
    print(f"  Velocity mag: mean={rb_velocity['mean']:.4f}, std={rb_velocity['std']:.4f}")

    print("\nActive Matter:")
    print(f"  Concentration: mean={am_concentration['mean']:.4f}, std={am_concentration['std']:.4f}")
    print(f"  Velocity mag: mean={am_velocity['mean']:.4f}, std={am_velocity['std']:.4f}")

    print("\n" + "=" * 60)
    print("Status: Operational reconnaissance complete. No analysis performed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
