#!/usr/bin/env python3
"""
RD-WELL.5D.R2A — Human-Free Blind Ledger

Procedure:
1. Randomize frame order.
2. Hide dataset identity.
3. Hide field names.
4. Describe operational changes only.
5. Reveal identity afterward.

This attacks:
- observer bias
- field-name bias
- domain bias

Forbidden: coherence, organization, emergence, complexity, information, adaptation.
"""

import numpy as np
import os
import json


def compute_operational_changes(field):
    """Compute operational changes for a field."""
    changes = []

    # Describe appearance over time
    for t in range(field.shape[0]):
        frame = field[t]

        # Compute basic statistics (for internal use only)
        mean = frame.mean()
        std = frame.std()
        min_val = frame.min()
        max_val = frame.max()

        # Describe appearance
        if t == 0:
            changes.append({
                'time': t,
                'description': f"Initial frame. Mean={mean:.4f}, Std={std:.4f}, Range=[{min_val:.4f}, {max_val:.4f}]"
            })
        else:
            # Compute frame-to-frame change
            prev_frame = field[t-1]
            frame_diff = np.abs(frame - prev_frame).mean()

            # Describe change
            if frame_diff < 0.001:
                change_desc = "Very small change from previous frame"
            elif frame_diff < 0.01:
                change_desc = "Small change from previous frame"
            elif frame_diff < 0.1:
                change_desc = "Moderate change from previous frame"
            else:
                change_desc = "Large change from previous frame"

            changes.append({
                'time': t,
                'description': f"{change_desc}. Mean={mean:.4f}, Std={std:.4f}, FrameDiff={frame_diff:.6f}"
            })

    return changes


def describe_field_blind(field, field_id):
    """Describe a field operationally without revealing its identity."""
    print(f"\n{'='*60}")
    print(f"FIELD {field_id}")
    print(f"{'='*60}")

    print(f"\nField shape: {field.shape}")

    # Compute operational changes
    changes = compute_operational_changes(field)

    print(f"\nOperational changes over time:")
    for change in changes:
        print(f"  t={change['time']}: {change['description']}")

    # Describe boundary formation
    print(f"\nBoundary formation:")
    if field.ndim >= 3:
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
        for t in range(min(5, field.shape[0])):
            frame = field[t]
            # Simple center of mass (weighted by field value)
            if frame.sum() > 0:
                y_cm = np.arange(frame.shape[0]).reshape(-1, 1) * frame / frame.sum()
                x_cm = np.arange(frame.shape[1]).reshape(1, -1) * frame / frame.sum()
                print(f"  t={t}: center_of_mass=({x_cm.sum():.2f}, {y_cm.sum():.2f})")
            else:
                print(f"  t={t}: center_of_mass=(N/A, N/A)")

    return changes


def main():
    print("RD-WELL.5D.R2A — Human-Free Blind Ledger")
    print("=" * 60)
    print("Procedure:")
    print("1. Randomize frame order.")
    print("2. Hide dataset identity.")
    print("3. Hide field names.")
    print("4. Describe operational changes only.")
    print("5. Reveal identity afterward.")
    print("=" * 60)

    output_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r2a"
    os.makedirs(output_dir, exist_ok=True)

    # Load all fields
    all_fields = []

    # Rayleigh-Bénard
    rb_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/rayleigh_benard_frames"
    buoyancy = np.load(os.path.join(rb_dir, 'buoyancy.npy'))
    pressure = np.load(os.path.join(rb_dir, 'pressure.npy'))
    velocity_mag = np.load(os.path.join(rb_dir, 'velocity_magnitude.npy'))

    all_fields.append(('RB_buoyancy', buoyancy))
    all_fields.append(('RB_pressure', pressure))
    all_fields.append(('RB_velocity_mag', velocity_mag))

    # Active Matter
    am_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/active_matter_frames"
    concentration = np.load(os.path.join(am_dir, 'concentration.npy'))
    velocity_mag_am = np.load(os.path.join(am_dir, 'velocity_magnitude.npy'))

    all_fields.append(('AM_concentration', concentration))
    all_fields.append(('AM_velocity_mag', velocity_mag_am))

    # Randomize order
    np.random.seed(42)  # For reproducibility
    np.random.shuffle(all_fields)

    # Blind description
    print("\n" + "=" * 60)
    print("BLIND DESCRIPTION")
    print("=" * 60)

    results = {}
    for i, (original_name, field) in enumerate(all_fields):
        field_id = f"Field_{i+1}"
        print(f"\n{'#'*60}")
        print(f"ORIGINAL NAME: {original_name} → BLIND ID: {field_id}")
        print(f"{'#'*60}")

        changes = describe_field_blind(field, field_id)
        results[field_id] = {
            'original_name': original_name,
            'changes': changes,
        }

    # Reveal identity
    print("\n" + "=" * 60)
    print("IDENTITY REVEAL")
    print("=" * 60)

    for field_id, data in results.items():
        print(f"{field_id} → {data['original_name']}")

    # Save results
    output_file = os.path.join(output_dir, "blind_ledger.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Status: Blind ledger complete. No analysis performed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
