#!/usr/bin/env python3
"""
compute_hashes.py
=================
Compute SHA-256 hashes of all dataset files for reproducibility verification.
"""

import hashlib
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"

FILES = [
    "t030_ensemble_Phi.npy",
    "t030_ensemble_features.csv",
    "t030_ensemble_flow.csv",
    "t030_ensemble_V.npy",
    "t030_ensemble_tensors.npy",
    "t031_null_metrics.csv",
    "t031_information_geometry.csv",
    "t031_embedding_stability.csv",
    "t031_geometry_comparison.csv",
    "t031_null_rankings.csv",
    "t031_null_geometry_results.json",
]


def sha256(path):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    print("Dataset Hashes (SHA-256)")
    print("=" * 60)
    for fname in FILES:
        path = OUT / fname
        if path.exists():
            h = sha256(path)
            size = path.stat().st_size
            print(f"  {fname:<45s} {h[:16]}... ({size:,} bytes)")
        else:
            print(f"  {fname:<45s} MISSING")
