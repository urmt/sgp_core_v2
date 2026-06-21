#!/usr/bin/env python3
"""
RD-WELL.5D.R1.1 — Dataset Loader Audit (Corrected URLs)

Goal: Make loading work for Rayleigh-Bénard, Active Matter, Rayleigh-Taylor.

Correct URLs found from visualization notebooks.
"""

import fsspec
import h5py
import json
import os


def explore_dataset(url, name):
    """Explore a dataset: find schema, fields, dimensions."""
    print(f"\n{'='*60}")
    print(f"EXPLORING: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    try:
        fs, path = fsspec.core.url_to_fs(url)
        print(f"Filesystem: {fs}")
        print(f"Path: {path}")

        with h5py.File(fs.open(path, 'rb'), 'r') as f:
            print(f"\nTop-level keys: {list(f.keys())}")

            # Explore each top-level key
            for key in f.keys():
                item = f[key]
                print(f"\n  {key}:")
                print(f"    Type: {type(item)}")

                if hasattr(item, 'keys'):
                    print(f"    Sub-keys: {list(item.keys())}")

                    # Explore sub-keys
                    for subkey in item.keys():
                        subitem = item[subkey]
                        print(f"      {subkey}:")
                        print(f"        Type: {type(subitem)}")

                        if hasattr(subitem, 'shape'):
                            print(f"        Shape: {subitem.shape}")
                            print(f"        Dtype: {subitem.dtype}")

                        if hasattr(subitem, 'keys'):
                            print(f"        Sub-sub-keys: {list(subitem.keys())}")

                elif hasattr(item, 'shape'):
                    print(f"    Shape: {item.shape}")
                    print(f"    Dtype: {item.dtype}")

            # Try to extract first frame
            print(f"\nAttempting to extract first frame...")

            if 't0_fields' in f:
                fields = f['t0_fields']
                field_names = list(fields.keys())
                print(f"  Available fields: {field_names}")

                if len(field_names) > 0:
                    field1 = fields[field_names[0]]
                    print(f"  First field shape: {field1.shape}")

                    # Extract first frame
                    if field1.ndim >= 3:
                        frame = field1[0]
                        print(f"  First frame shape: {frame.shape}")
                        print(f"  First frame min: {frame.min():.4f}")
                        print(f"  First frame max: {frame.max():.4f}")
                        print(f"  First frame mean: {frame.mean():.4f}")
                        print(f"  ✓ Successfully extracted first frame")

            return {
                'status': 'success',
                'url': url,
                'top_keys': list(f.keys()),
            }

    except Exception as e:
        print(f"\n  ✗ ERROR: {e}")
        return {
            'status': 'error',
            'url': url,
            'error': str(e),
        }


def main():
    print("RD-WELL.5D.R1.1 — Dataset Loader Audit (Corrected URLs)")
    print("=" * 60)
    print("Goal: Make loading work for Rayleigh-Bénard, Active Matter, Rayleigh-Taylor")
    print("=" * 60)

    # Correct URLs from visualization notebooks
    datasets = {
        'rayleigh_benard': [
            'https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Rayleigh_1e8_Prandtl_1.hdf5',
            'https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Rayleigh_1e6_Prandtl_1.hdf5',
            'https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Rayleigh_1e10_Prandtl_1.hdf5',
        ],
        'active_matter': [
            'https://huggingface.co/datasets/polymathic-ai/active_matter/resolve/main/data/train/active_matter_activity_8.0_noise_0.001.hdf5',
            'https://huggingface.co/datasets/polymathic-ai/active_matter/resolve/main/data/train/active_matter_activity_1.0_noise_0.001.hdf5',
        ],
        'rayleigh_taylor': [
            'https://huggingface.co/datasets/polymathic-ai/rayleigh_taylor_instability/resolve/main/data/train/rayleigh_taylor_instability_A0.5_n4_2D_256x512_2000.hdf5',
            'https://huggingface.co/datasets/polymathic-ai/rayleigh_taylor_instability/resolve/main/data/train/rayleigh_taylor_instability_A0.5_n4_2D_256x512_1000.hdf5',
        ],
    }

    results = {}

    for dataset_name, urls in datasets.items():
        print(f"\n\n{'#'*60}")
        print(f"DATASET: {dataset_name}")
        print(f"{'#'*60}")

        dataset_results = []
        for url in urls:
            result = explore_dataset(url, dataset_name)
            dataset_results.append(result)

            if result['status'] == 'success':
                print(f"\n✓ Successfully loaded: {url}")
                break
            else:
                print(f"\n✗ Failed: {url}")

        results[dataset_name] = dataset_results

    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r1"
    os.makedirs(output_dir, exist_ok=True)

    output = {
        'description': 'Dataset loader audit (corrected URLs)',
        'results': results,
    }

    output_file = os.path.join(output_dir, "dataset_loader_audit_corrected.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for dataset_name, dataset_results in results.items():
        successful = [r for r in dataset_results if r['status'] == 'success']
        print(f"\n{dataset_name}:")
        print(f"  URLs tested: {len(dataset_results)}")
        print(f"  Successful: {len(successful)}")

        if successful:
            print(f"  ✓ Found working URL")
        else:
            print(f"  ✗ No working URL found")


if __name__ == "__main__":
    main()
