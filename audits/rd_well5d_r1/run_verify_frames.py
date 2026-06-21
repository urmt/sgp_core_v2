#!/usr/bin/env python3
"""
Verify Extracted Frames

Numerical verification that extracted frames are valid data or loading artifacts.
"""

import numpy as np
import os


def verify_frames(domain_name, frame_dir):
    """Verify frames in a directory."""
    print(f"\n{'='*60}")
    print(f"VERIFYING: {domain_name}")
    print(f"Directory: {frame_dir}")
    print(f"{'='*60}")

    if not os.path.exists(frame_dir):
        print(f"  ✗ Directory does not exist")
        return False

    files = [f for f in os.listdir(frame_dir) if f.endswith('.npy')]
    print(f"  Files found: {files}")

    all_valid = True

    for file in files:
        filepath = os.path.join(frame_dir, file)
        try:
            data = np.load(filepath)

            print(f"\n  {file}:")
            print(f"    Shape: {data.shape}")
            print(f"    Dtype: {data.dtype}")
            print(f"    Min: {data.min():.6f}")
            print(f"    Max: {data.max():.6f}")
            print(f"    Mean: {data.mean():.6f}")
            print(f"    Std: {data.std():.6f}")

            # Check for NaN or Inf
            if np.isnan(data).any():
                print(f"    ✗ Contains NaN values")
                all_valid = False
            elif np.isinf(data).any():
                print(f"    ✗ Contains Inf values")
                all_valid = False
            else:
                print(f"    ✓ No NaN or Inf values")

            # Check if all values are the same (potential loading artifact)
            if data.min() == data.max():
                print(f"    ✗ All values identical (potential loading artifact)")
                all_valid = False
            else:
                print(f"    ✓ Non-trivial values")

            # Check shape
            if data.ndim < 2:
                print(f"    ✗ Expected at least 2D array")
                all_valid = False
            else:
                print(f"    ✓ Valid shape")

        except Exception as e:
            print(f"    ✗ Error loading: {e}")
            all_valid = False

    return all_valid


def main():
    print("VERIFY EXTRACTED FRAMES")
    print("=" * 60)
    print("Numerical verification that extracted frames are valid data or loading artifacts.")
    print("=" * 60)

    base_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1"

    # Verify Rayleigh-Bénard
    rb_valid = verify_frames(
        'Rayleigh-Bénard',
        os.path.join(base_dir, 'rayleigh_benard_frames')
    )

    # Verify Active Matter
    am_valid = verify_frames(
        'Active Matter',
        os.path.join(base_dir, 'active_matter_frames')
    )

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    print(f"\nRayleigh-Bénard: {'✓ VALID' if rb_valid else '✗ INVALID'}")
    print(f"Active Matter: {'✓ VALID' if am_valid else '✗ INVALID'}")

    if rb_valid and am_valid:
        print("\n✓ All frames verified as valid data")
    else:
        print("\n✗ Some frames may be loading artifacts")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
