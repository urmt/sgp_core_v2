#!/usr/bin/env python3
"""
SFH-SGP Metric Ablation & Artifact Diagnostic (v5)
===================================================
Purpose: Determine whether transform-space low-dimensionality is a
property of the metric construction (artifact) or the generative system.

Design:
  - Compute transform PC1 with full 4-metric vector
  - Ablate one metric at a time (3-metric subsets)
  - Compute single-metric PC1 (each metric alone)
  - Test on: all OOD systems + adversarial controls (constant, ramp, step)

Key question:
  Does removing m2_half_corr eliminate the artifact (noise PC1 drops)?
  Or does every metric independently produce low-dimensional structure?

Outputs (to sfh_sgp_ood_outputs/):
  - metric_ablation_results.csv     (PC1 per ablation per system)
  - metric_ablation_summary.md      (analysis & recommendations)
"""

from __future__ import annotations
import json, random, warnings
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

OUT = Path("sfh_sgp_ood_outputs")
OUT.mkdir(exist_ok=True)

# Reuse generators and transforms from OOD audit
from sfh_sgp_ood_universality_audit import (
    OOD_SYSTEMS, TRANSFORMS, canonical_metric_vector,
    m1_signed_ordinal_flow, m2_half_corr,
    m3_signed_compressibility, m4_amp_transition_asymmetry,
    system_category,
)

METRICS = {
    "m1_signed_ordinal_flow": m1_signed_ordinal_flow,
    "m2_half_corr": m2_half_corr,
    "m3_signed_compressibility": m3_signed_compressibility,
    "m4_amp_transition_asymmetry": m4_amp_transition_asymmetry,
}

# Adversarial controls — minimal input types to test metric artifact
def constant_sequence(n: int = 256) -> np.ndarray:
    return np.ones(n)

def linear_ramp(n: int = 256) -> np.ndarray:
    return np.linspace(0, 1, n)

CONTROL_SYSTEMS = {
    "constant": constant_sequence,
    "linear_ramp": linear_ramp,
    "iid_gaussian": lambda n=256: np.random.randn(n),
}

def metric_vector_subset(x: np.ndarray, metric_names: list[str]) -> np.ndarray:
    vals = []
    for name in metric_names:
        fn = METRICS[name]
        try:
            v = fn(x)
            if np.isnan(v) or np.isinf(v):
                v = 0.0
        except Exception:
            v = 0.0
        vals.append(v)
    return np.array(vals, dtype=float)


def compute_pc1_with_metrics(system_name: str, gen: Callable,
                              metric_names: list[str],
                              n_samples: int = 25) -> dict:
    displacements = []
    for _ in range(n_samples):
        x = gen()
        e_base = metric_vector_subset(x, metric_names)
        for _, tf in TRANSFORMS.items():
            e_tf = metric_vector_subset(tf(x), metric_names)
            displacements.append(e_tf - e_base)
    X = np.vstack(displacements)
    if X.shape[1] < 2:
        return {"pc1": 1.0, "n_metrics": len(metric_names)}
    _, S, _ = np.linalg.svd(X - X.mean(axis=0), full_matrices=False)
    ev = (S ** 2) / max(np.sum(S ** 2), 1e-12)
    return {"pc1": float(ev[0]), "n_metrics": len(metric_names)}


def ising_fast(n: int = 256, lattice_size: int = 4, n_steps: int = 3,
                T: float = 2.5) -> np.ndarray:
    from sfh_sgp_ood_universality_audit import ising_magnetization
    return ising_magnetization(n=n, lattice_size=lattice_size,
                                n_steps=n_steps, T=T)

REPRESENTATIVE_SYSTEMS = {
    "constant": constant_sequence,
    "linear_ramp": linear_ramp,
    "iid_gaussian": lambda n=256: np.random.randn(n),
    "primes": OOD_SYSTEMS["primes"],
    "lorenz": OOD_SYSTEMS["lorenz"],
    "logistic_map": OOD_SYSTEMS["logistic_map"],
    "henon_map": OOD_SYSTEMS["henon_map"],
    "ising_magnetization": ising_fast,
    "cfg_expansion": OOD_SYSTEMS["cfg_expansion"],
}

def main():
    all_names = list(REPRESENTATIVE_SYSTEMS.keys())
    all_gens = REPRESENTATIVE_SYSTEMS

    ablation_sets = {
        "full": ["m1_signed_ordinal_flow", "m2_half_corr",
                 "m3_signed_compressibility", "m4_amp_transition_asymmetry"],
        "no_m1": ["m2_half_corr", "m3_signed_compressibility",
                    "m4_amp_transition_asymmetry"],
        "no_m2": ["m1_signed_ordinal_flow", "m3_signed_compressibility",
                    "m4_amp_transition_asymmetry"],
        "no_m3": ["m1_signed_ordinal_flow", "m2_half_corr",
                    "m4_amp_transition_asymmetry"],
        "no_m4": ["m1_signed_ordinal_flow", "m2_half_corr",
                    "m3_signed_compressibility"],
        "m1_only": ["m1_signed_ordinal_flow"],
        "m2_only": ["m2_half_corr"],
        "m3_only": ["m3_signed_compressibility"],
        "m4_only": ["m4_amp_transition_asymmetry"],
    }

    rows = []
    for sys_name in all_names:
        gen = all_gens[sys_name]
        cat = "control" if sys_name in CONTROL_SYSTEMS else system_category(sys_name)
        for ablation_name, metric_names in ablation_sets.items():
            result = compute_pc1_with_metrics(sys_name, gen, metric_names)
            rows.append({
                "system": sys_name,
                "category": cat,
                "ablation": ablation_name,
                "pc1": result["pc1"],
                "n_metrics": result["n_metrics"],
            })
        print(f"  {sys_name:25s} done")

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "metric_ablation_results.csv", index=False)

    # Generate summary
    generate_summary(df)
    print(f"\nSaved {OUT / 'metric_ablation_results.csv'}")
    print(f"Saved {OUT / 'metric_ablation_summary.md'}")


def generate_summary(df: pd.DataFrame):
    md = []
    md.append("# Metric Ablation & Artifact Diagnostic")
    md.append("")
    md.append("## Design")
    md.append("")
    md.append("For each system, compute transform PC1 using:")
    md.append("- Full 4-metric vector")
    md.append("- 3-metric subsets (remove one metric at a time)")
    md.append("- Single-metric versions (each metric alone)")
    md.append("")
    md.append("If PC1 stays high (>0.8) after removing a metric, that metric is ")
    md.append("*redundant* for the geometry. If PC1 drops sharply, that metric ")
    md.append("is the *driver* of the low-dimensional structure.")
    md.append("")
    md.append("Key artifact question: does IID Gaussian noise lose its high PC1")
    md.append("when m2_half_corr is removed?")
    md.append("")

    # Pivot table
    pivot = df.pivot_table(index="system", columns="ablation",
                           values="pc1", aggfunc="mean")
    md.append("## PC1 by Ablation Set")
    md.append("")
    md.append(pivot.to_string(float_format="%.4f"))
    md.append("")

    # IID artifact analysis
    md.append("## Artifact Driver Analysis")
    md.append("")
    iid_row = df[df["system"] == "iid_gaussian"]
    if len(iid_row) > 0:
        full_pc1 = iid_row[iid_row["ablation"] == "full"]["pc1"].values[0]
        no_m2_pc1 = iid_row[iid_row["ablation"] == "no_m2"]["pc1"].values[0] if len(iid_row[iid_row["ablation"] == "no_m2"]) > 0 else None
        if no_m2_pc1 is not None:
            drop = full_pc1 - no_m2_pc1
            md.append(f"IID Gaussian full PC1: {full_pc1:.4f}")
            md.append(f"IID Gaussian no_m2 PC1: {no_m2_pc1:.4f}")
            md.append(f"Drop when removing m2: {drop:.4f}")
            if drop > 0.3:
                md.append("**Conclusion: m2_half_corr is the dominant artifact driver.**")
                md.append("Removing it substantially reduces noise's apparent structure.")
            else:
                md.append("**Conclusion: artifact is distributed across metrics.**")
                md.append("No single metric drives the noise artifact.")
            md.append("")

    # Which metrics matter for which systems
    md.append("## Per-System Dominant Metric")
    md.append("")
    md.append("(The single metric that, when removed, drops PC1 the most)")
    md.append("")
    md.append("| System | Full PC1 | Dominant Metric | PC1 w/o it | Drop |")
    md.append("|--------|----------|-----------------|------------|------|")
    ablation_cols = ["no_m1", "no_m2", "no_m3", "no_m4"]
    metric_labels = ["no_m1 (m1_flow)", "no_m2 (m2_half_corr)",
                     "no_m3 (m3_compress)", "no_m4 (m4_transition)"]
    for sys_name in df["system"].unique():
        sys_df = df[df["system"] == sys_name]
        full = sys_df[sys_df["ablation"] == "full"]["pc1"].values
        if len(full) == 0:
            continue
        full_pc1 = full[0]
        best_drop = 0.0
        best_metric = "none"
        for col, label in zip(ablation_cols, metric_labels):
            val = sys_df[sys_df["ablation"] == col]["pc1"].values
            if len(val) > 0:
                drop = full_pc1 - val[0]
                if drop > best_drop:
                    best_drop = drop
                    best_metric = label
        md.append(f"| {sys_name:20s} | {full_pc1:.4f} | {best_metric:30s} | "
                  f"{full_pc1 - best_drop:.4f} | {best_drop:.4f} |")
    md.append("")

    # Single metric analysis
    md.append("## Single-Metric PC1 (each metric alone)")
    md.append("")
    md.append("| System | m1_flow | m2_half_corr | m3_compress | m4_transition |")
    md.append("|--------|---------|-------------|-------------|---------------|")
    for sys_name in df["system"].unique():
        sys_df = df[df["system"] == sys_name]
        m1 = sys_df[sys_df["ablation"] == "m1_only"]["pc1"].values
        m2 = sys_df[sys_df["ablation"] == "m2_only"]["pc1"].values
        m3 = sys_df[sys_df["ablation"] == "m3_only"]["pc1"].values
        m4 = sys_df[sys_df["ablation"] == "m4_only"]["pc1"].values
        md.append(f"| {sys_name:20s} | {m1[0]:.4f} | {m2[0]:.4f} | {m3[0]:.4f} | {m4[0]:.4f} |")
    md.append("")

    md.append("## Interpretation")
    md.append("")
    md.append("- If single-metric PC1 is ~1.0 for ALL systems including noise,")
    md.append("  that metric is a *trivial* organizational metric (all transforms")
    md.append("  affect it the same way).")
    md.append("- If single-metric PC1 varies by system, the metric carries")
    md.append("  system-specific information.")
    md.append("- If removing m2 drops PC1 for noise but NOT for structured systems,")
    md.append("  then structured systems have geometry BEYOND the metric artifact.")

    with open(OUT / "metric_ablation_summary.md", "w") as f:
        f.write("\n".join(md))


if __name__ == "__main__":
    main()
