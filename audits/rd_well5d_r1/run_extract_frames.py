#!/usr/bin/env python3
"""
RD-WELL.5D.R1 — Extract 10 Frames from Each Domain

Extract:
- Rayleigh-Bénard: buoyancy, pressure, velocity magnitude (t=0-9)
- Active Matter: concentration, velocity magnitude (t=0-9)

Store in:
- audits/rd_well5d_r1/rayleigh_benard_frames/
- audits/rd_well5d_r1/active_matter_frames/

No metrics. No C. No stabilization. Only successful extraction.
"""

import fsspec
import h5py
import numpy as np
import os


def extract_rayleigh_benard(output_dir):
    """Extract 10 frames from Rayleigh-Bénard."""
    print("\n" + "=" * 60)
    print("EXTRACTING RAYLEIGH-BÉNARD FRAMES")
    print("=" * 60)

    url = 'https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Rayleigh_1e8_Prandtl_1.hdf5'

    fs, path = fsspec.core.url_to_fs(url)

    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        # Extract fields
        buoyancy = f['t0_fields']['buoyancy'][0, :10]  # (10, 512, 128)
        pressure = f['t0_fields']['pressure'][0, :10]  # (10, 512, 128)
        velocity = f['t1_fields']['velocity'][0, :10]  # (10, 512, 128, 2)

        # Compute velocity magnitude
        velocity_mag = np.sqrt(velocity[..., 0]**2 + velocity[..., 1]**2)

        print(f"Buoyancy shape: {buoyancy.shape}")
        print(f"Pressure shape: {pressure.shape}")
        print(f"Velocity magnitude shape: {velocity_mag.shape}")

        # Create output directory
        rb_dir = os.path.join(output_dir, 'rayleigh_benard_frames')
        os.makedirs(rb_dir, exist_ok=True)

        # Save frames
        np.save(os.path.join(rb_dir, 'buoyancy.npy'), buoyancy)
        np.save(os.path.join(rb_dir, 'pressure.npy'), pressure)
        np.save(os.path.join(rb_dir, 'velocity_magnitude.npy'), velocity_mag)

        # Verify
        print(f"\nVerification:")
        print(f"  Buoyancy: min={buoyancy.min():.4f}, max={buoyancy.max():.4f}, mean={buoyancy.mean():.4f}")
        print(f"  Pressure: min={pressure.min():.4f}, max={pressure.max():.4f}, mean={pressure.mean():.4f}")
        print(f"  Velocity mag: min={velocity_mag.min():.4f}, max={velocity_mag.max():.4f}, mean={velocity_mag.mean():.4f}")

        print(f"\n✓ Saved to: {rb_dir}")

        return {
            'status': 'success',
            'buoyancy_shape': buoyancy.shape,
            'pressure_shape': pressure.shape,
            'velocity_mag_shape': velocity_mag.shape,
        }


def extract_active_matter(output_dir):
    """Extract 10 frames from Active Matter."""
    print("\n" + "=" * 60)
    print("EXTRACTING ACTIVE MATTER FRAMES")
    print("=" * 60)

    url = 'https://huggingface.co/datasets/polymathic-ai/active_matter/resolve/main/data/train/active_matter_L_10.0_zeta_1.0_alpha_-1.0.hdf5'

    fs, path = fsspec.core.url_to_fs(url)

    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        # Extract fields
        concentration = f['t0_fields']['concentration'][0, :10]  # (10, 256, 256)
        velocity = f['t1_fields']['velocity'][0, :10]  # (10, 256, 256, 2)

        # Compute velocity magnitude
        velocity_mag = np.sqrt(velocity[..., 0]**2 + velocity[..., 1]**2)

        print(f"Concentration shape: {concentration.shape}")
        print(f"Velocity magnitude shape: {velocity_mag.shape}")

        # Create output directory
        am_dir = os.path.join(output_dir, 'active_matter_frames')
        os.makedirs(am_dir, exist_ok=True)

        # Save frames
        np.save(os.path.join(am_dir, 'concentration.npy'), concentration)
        np.save(os.path.join(am_dir, 'velocity_magnitude.npy'), velocity_mag)

        # Verify
        print(f"\nVerification:")
        print(f"  Concentration: min={concentration.min():.4f}, max={concentration.max():.4f}, mean={concentration.mean():.4f}")
        print(f"  Velocity mag: min={velocity_mag.min():.4f}, max={velocity_mag.max():.4f}, mean={velocity_mag.mean():.4f}")

        print(f"\n✓ Saved to: {am_dir}")

        return {
            'status': 'success',
            'concentration_shape': concentration.shape,
            'velocity_mag_shape': velocity_mag.shape,
        }


def main():
    print("RD-WELL.5D.R1 — Extract 10 Frames from Each Domain")
    print("=" * 60)
    print("No metrics. No C. No stabilization. Only successful extraction.")
    print("=" * 60)

    output_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1"
    os.makedirs(output_dir, exist_ok=True)

    # Extract Rayleigh-Bénard
    rb_result = extract_rayleigh_benard(output_dir)

    # Extract Active Matter
    am_result = extract_active_matter(output_dir)

    # Summary
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)

    print(f"\nRayleigh-Bénard:")
    print(f"  Status: {rb_result['status']}")
    print(f"  Buoyancy shape: {rb_result['buoyancy_shape']}")
    print(f"  Pressure shape: {rb_result['pressure_shape']}")
    print(f"  Velocity mag shape: {rb_result['velocity_mag_shape']}")

    print(f"\nActive Matter:")
    print(f"  Status: {am_result['status']}")
    print(f"  Concentration shape: {am_result['concentration_shape']}")
    print(f"  Velocity mag shape: {am_result['velocity_mag_shape']}")

    print("\n" + "=" * 60)
    print("Status: Extraction complete. No analysis performed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
