"""
RD-OBSERVER.2 — Blinded Dataset Generator

Strips RD-specific terminology from raw data.
All observers receive identical blinded data.
"""

import json
import csv
import os

BASE = "/home/student/sgp_core_v2"


def load_t901_ensemble():
    """Load T901 granular ensemble (60 runs, 12 metrics)."""
    with open(f"{BASE}/coherence-benchmark/results/t901_ensemble.json") as f:
        return json.load(f)


def load_t081_system_results():
    """Load T081 system results (240 systems, 38 metrics)."""
    rows = []
    with open(f"{BASE}/sfh_sgp_ood_outputs/t081_system_results.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def load_rd_hist_summary():
    """Load historical reconstruction summary (without RD-specific labels)."""
    with open(f"{BASE}/audits/RD_HIST_RECONSTRUCTION_REPORT.md") as f:
        return f.read()


def blinded_t901(data):
    """
    Blind T901 ensemble: rename fields to generic labels.
    Remove friction (domain-specific parameter).
    """
    field_map = {
        "pre_C": "metric_A",
        "dip": "metric_B",
        "restoration": "metric_C",
        "tau_rec": "metric_D",
        "pre_I_pred": "metric_E",
        "pre_C_sigma": "metric_F",
        "pre_MSE_s1": "metric_G",
        "rms_velocity": "metric_H",
        "msd": "metric_I",
        "neighbor_turnover": "metric_J",
        "packing_var": "metric_K",
    }
    blinded = []
    for run in data:
        b = {"run_id": run["friction"] * 100 + run["rep"], "condition": run["friction"]}
        for old_key, new_key in field_map.items():
            b[new_key] = run[old_key]
        blinded.append(b)
    return blinded


def blinded_t081(data):
    """
    Blind T081 system results: rename fields to generic labels.
    Remove domain-specific boolean flags.
    """
    blinded = []
    for i, row in enumerate(data):
        b = {"system_id": i}
        # Copy all numeric columns with generic names
        for j, (key, val) in enumerate(row.items()):
            if key == "system_id":
                continue
            if val in ("True", "False"):
                b[f"flag_{j}"] = val == "True"
            else:
                try:
                    b[f"var_{j}"] = float(val)
                except ValueError:
                    b[f"var_{j}"] = val
        blinded.append(b)
    return blinded


def blinded_hist_summary(text):
    """
    Blind historical summary: remove RD-specific terminology.
    Replace with generic labels.
    """
    replacements = {
        "RD-HIST": "STUDY",
        "RD-": "S",
        "friction": "parameter_X",
        "coherence": "metric_alpha",
        "persistence": "property_beta",
        "interaction": "relation_gamma",
        "fertility": "capacity_delta",
        "surprise": "signal_epsilon",
        "novelty": "innovation_zeta",
        "predictive information": "forward_information",
        "statistical complexity": "structural_complexity",
        "multiscale entropy": "scale_entropy",
        "total correlation": "joint_measure",
        "manifold": "latent_space",
        "topology": "connectivity",
    }
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


def create_blinded_datasets():
    """Create all blinded datasets and save to disk."""
    out_dir = f"{BASE}/audits/rd_observer2/blinded"
    os.makedirs(out_dir, exist_ok=True)

    # 1. T901 ensemble
    t901_raw = load_t901_ensemble()
    t901_blinded = blinded_t901(t901_raw)
    with open(f"{out_dir}/dataset_granular_ensemble.json", "w") as f:
        json.dump(t901_blinded, f, indent=2)

    # 2. T081 system results
    t081_raw = load_t081_system_results()
    t081_blinded = blinded_t081(t081_raw)
    with open(f"{out_dir}/dataset_system_results.json", "w") as f:
        json.dump(t081_blinded, f, indent=2)

    # 3. Historical summary
    hist_raw = load_rd_hist_summary()
    hist_blinded = blinded_hist_summary(hist_raw)
    with open(f"{out_dir}/dataset_historical_summary.txt", "w") as f:
        f.write(hist_blinded)

    # 4. Metadata
    metadata = {
        "description": "Blinded datasets for RD-OBSERVER.2",
        "datasets": {
            "granular_ensemble": {
                "source": "T901 granular simulation",
                "n_runs": len(t901_blinded),
                "n_variables": len(t901_blinded[0]) - 2,  # minus run_id and condition
                "note": "6 friction conditions x 10 replicates. Variables renamed to generic labels.",
            },
            "system_results": {
                "source": "T081 system evaluation",
                "n_systems": len(t081_blinded),
                "n_variables": len(t081_blinded[0]) - 1,  # minus system_id
                "note": "240 systems evaluated across multiple assumptions. Variables renamed.",
            },
            "historical_summary": {
                "source": "Historical reconstruction report",
                "note": "Text summary with RD-specific terminology replaced by generic labels.",
            },
        },
        "warning": "All observers receive identical data. Observer diversity is not observer independence (SR-32).",
    }
    with open(f"{out_dir}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Blinded datasets created in {out_dir}")
    print(f"  Granular ensemble: {len(t901_blinded)} runs, {len(t901_blinded[0]) - 2} variables")
    print(f"  System results: {len(t081_blinded)} systems, {len(t081_blinded[0]) - 1} variables")
    print(f"  Historical summary: {len(hist_blinded)} characters")

    return out_dir


if __name__ == "__main__":
    create_blinded_datasets()
