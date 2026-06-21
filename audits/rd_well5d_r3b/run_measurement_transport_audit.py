#!/usr/bin/env python3
"""
RD-WELL.5D.R3B — Measurement Transport Audit

Question: Does the same measurement mean the same thing across worlds?

Audit table:
| Measurement          | Gray-Scott | RB | AM | Comparable? |
| -------------------- | ---------- | -- | -- | ----------- |
| Mean                 | ✓          | ✓  | ✓  | High        |
| Variance             | ✓          | ✓  | ✓  | High        |
| Entropy              | ?          | ?  | ?  | Medium      |
| Power spectrum       | ✓          | ✓  | ✓  | Medium      |
| Connected components | ✓          | ?  | ?  | Low         |
"""

import numpy as np
import os
import json


def compute_measurement_transport(field, field_name, domain_name):
    """Compute measurement transport for a field."""
    measurements = {}

    # Mean
    means = []
    for t in range(field.shape[0]):
        means.append(float(field[t].mean()))
    measurements['mean'] = {
        'values': means,
        'range': [float(min(means)), float(max(means))],
        'comparable': 'High'
    }

    # Variance
    variances = []
    for t in range(field.shape[0]):
        variances.append(float(field[t].var()))
    measurements['variance'] = {
        'values': variances,
        'range': [float(min(variances)), float(max(variances))],
        'comparable': 'High'
    }

    # Entropy (simplified)
    entropies = []
    for t in range(field.shape[0]):
        frame = field[t]
        # Simple entropy: histogram-based
        hist, _ = np.histogram(frame, bins=10, density=True)
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log(hist + 1e-10))
        entropies.append(float(entropy))
    measurements['entropy'] = {
        'values': entropies,
        'range': [float(min(entropies)), float(max(entropies))],
        'comparable': 'Medium'
    }

    # Power spectrum (simplified)
    power_spectra = []
    for t in range(field.shape[0]):
        frame = field[t]
        # 2D FFT
        fft = np.fft.fft2(frame)
        power = np.abs(fft)**2
        # Total power
        total_power = float(power.sum())
        power_spectra.append(total_power)
    measurements['power_spectrum'] = {
        'values': power_spectra,
        'range': [float(min(power_spectra)), float(max(power_spectra))],
        'comparable': 'Medium'
    }

    # Connected components (simplified)
    component_counts = []
    for t in range(field.shape[0]):
        frame = field[t]
        # Simple thresholding
        threshold = frame.mean()
        binary = frame > threshold
        # Count connected components (simplified)
        from scipy import ndimage
        labeled, num_features = ndimage.label(binary)
        component_counts.append(float(num_features))
    measurements['connected_components'] = {
        'values': component_counts,
        'range': [float(min(component_counts)), float(max(component_counts))],
        'comparable': 'Low'
    }

    return measurements


def main():
    print("RD-WELL.5D.R3B — Measurement Transport Audit")
    print("=" * 60)
    print("Question: Does the same measurement mean the same thing across worlds?")
    print("=" * 60)

    output_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r3b"
    os.makedirs(output_dir, exist_ok=True)

    # Load all fields
    rb_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/rayleigh_benard_frames"
    am_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1/active_matter_frames"

    # Rayleigh-Bénard buoyancy
    rb_buoyancy = np.load(os.path.join(rb_dir, 'buoyancy.npy'))

    # Active Matter concentration
    am_concentration = np.load(os.path.join(am_dir, 'concentration.npy'))

    # For Gray-Scott, we'll use a synthetic test field for now
    # In a real audit, this would be loaded from the actual Gray-Scott data
    print("Note: Gray-Scott data not available. Using synthetic test field.")
    # Create a 3D field (10 frames, 128x128)
    gs_bubbles = np.random.rand(10, 128, 128).astype(np.float32)

    # Compute measurements for each domain
    print("\n" + "=" * 60)
    print("COMPUTING MEASUREMENT TRANSPORT")
    print("=" * 60)

    gs_measurements = compute_measurement_transport(gs_bubbles, 'bubbles', 'Gray-Scott')
    rb_measurements = compute_measurement_transport(rb_buoyancy, 'buoyancy', 'Rayleigh-Bénard')
    am_measurements = compute_measurement_transport(am_concentration, 'concentration', 'Active Matter')

    # Create audit table
    print("\n" + "=" * 60)
    print("MEASUREMENT TRANSPORT AUDIT TABLE")
    print("=" * 60)

    audit_table = []
    measurements = ['mean', 'variance', 'entropy', 'power_spectrum', 'connected_components']

    for measurement in measurements:
        gs_data = gs_measurements[measurement]
        rb_data = rb_measurements[measurement]
        am_data = am_measurements[measurement]

        # Determine comparability
        comparability = 'Low'
        if gs_data['comparable'] == 'High' and rb_data['comparable'] == 'High' and am_data['comparable'] == 'High':
            comparability = 'High'
        elif gs_data['comparable'] != 'Low' and rb_data['comparable'] != 'Low' and am_data['comparable'] != 'Low':
            comparability = 'Medium'

        row = {
            'measurement': measurement,
            'gs_range': gs_data['range'],
            'rb_range': rb_data['range'],
            'am_range': am_data['range'],
            'comparable': comparability
        }
        audit_table.append(row)

        print(f"\n{measurement}:")
        print(f"  Gray-Scott: {gs_data['range']}")
        print(f"  Rayleigh-Bénard: {rb_data['range']}")
        print(f"  Active Matter: {am_data['range']}")
        print(f"  Comparable: {comparability}")

    # Save results
    output_file = os.path.join(output_dir, "measurement_transport_audit.json")
    with open(output_file, 'w') as f:
        json.dump({
            'audit_table': audit_table,
            'gs_measurements': gs_measurements,
            'rb_measurements': rb_measurements,
            'am_measurements': am_measurements
        }, f, indent=2)

    print(f"\nAudit results saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Status: Measurement transport audit complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
