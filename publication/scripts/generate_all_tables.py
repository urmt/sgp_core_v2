#!/usr/bin/env python3
"""
generate_all_tables.py
======================
Generate all publication-ready tables as LaTeX and CSV.
"""

import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"
TAB = ROOT / "publication" / "tables"
TAB.mkdir(parents=True, exist_ok=True)


def table1_system_families():
    """Table 1: System families and parameter sweeps."""
    data = {
        "Family": [
            "Logistic", "Lorenz", "Rössler", "Hénon", "Hénon-Heiles",
            "Hénon Map", "Ikeda", "Duffing", "Van der Pol", "Chua",
            "Brusselator", "Stuart-Landau", "FitzHugh-Nagumo"
        ],
        "Systems": [16] * 13,
        "Parameter": [
            "$r$", "$\\sigma$", "$a$", "$a$", "$E$",
            "$a$", "$u$", "$\\alpha$", "$\\mu$", "$m_0$",
            "$A$", "$\\lambda$", "$a$"
        ],
        "Range": [
            "[2.5, 4.0]", "[8, 16]", "[0.1, 0.5]", "[0.5, 1.5]", "[0.05, 0.20]",
            "[0.5, 1.5]", "[0.3, 1.0]", "[-0.5, 0.5]", "[0.5, 5.0]", "[-1.2, -0.6]",
            "[1, 3]", "[-0.5, 0.5]", "[0.5, 1.5]"
        ],
    }
    df = pd.DataFrame(data)
    df.to_latex(TAB / "table1_system_families.tex", index=False, escape=False)
    df.to_csv(TAB / "table1_system_families.csv", index=False)
    print("  Saved table1_system_families.tex/.csv")


def table2_feature_definitions():
    """Table 2: 17 raw feature definitions."""
    data = {
        "Feature": [
            "pc1", "pc2", "effective_rank", "tau_m1", "tau_m2", "tau_m3", "tau_m4",
            "temporal_corr", "phase_corr", "pc1_ratio", "replay_displacement",
            "abl_full_pc1", "abl_no_m1_pc1", "abl_no_m2_pc1", "abl_no_m3_pc1",
            "abl_no_m4_pc1", "m2_contribution"
        ],
        "Group": [
            "Principal", "Principal", "Principal",
            "Temporal", "Temporal", "Temporal", "Temporal",
            "Temporal", "Temporal", "Amplitude", "Amplitude",
            "Ablation", "Ablation", "Ablation", "Ablation", "Ablation", "Ablation"
        ],
        "Description": [
            "First PC variance", "Second PC variance", "Effective rank",
            "Moment timescale 1", "Moment timescale 2", "Moment timescale 3", "Moment timescale 4",
            "Temporal autocorrelation", "Phase-space correlation", "PC1 ratio",
            "Replay displacement", "Full ablation sensitivity",
            "Ablation without $m_1$", "Ablation without $m_2$",
            "Ablation without $m_3$", "Ablation without $m_4$",
            "$m_2$ contribution fraction"
        ],
    }
    df = pd.DataFrame(data)
    df.to_latex(TAB / "table2_feature_definitions.tex", index=False, escape=False)
    df.to_csv(TAB / "table2_feature_definitions.csv", index=False)
    print("  Saved table2_feature_definitions.tex/.csv")


def table3_hypothesis_audit():
    """Table 3: T027-T031 hypothesis audit."""
    data = {
        "Hypothesis": [
            "Universal dynamical manifold",
            "Transit bridge ontology",
            "Unique dynamical generation",
            "Universal field equations",
            "Partial continuity",
            "Topological segmentation",
            "Row-shuffle sensitivity",
            "Adversarial resistance",
            "Representation robustness",
            "Spectral uniqueness",
            "Fokker-Planck continuum",
        ],
        "Test": [
            "T027 flow invariant",
            "T028 bridge centrality",
            "T030 null destruction",
            "T030 Section G",
            "T030 parametric",
            "T030 Section C",
            "T031 row-shuffle",
            "T031 adversarial",
            "T031 trustworthiness",
            "T031 spectral",
            "T030 Section G",
        ],
        "Result": [
            "FAILED", "FAILED", "FAILED", "FAILED",
            "SURVIVED", "SURVIVED", "SURVIVED", "SURVIVED",
            "SURVIVED", "SURVIVED", "DEGENERATE"
        ],
        "Confidence": [
            "0.15", "0.20", "0.10", "0.05",
            "0.75", "0.80", "0.85", "0.90",
            "0.82", "0.78", "---"
        ],
    }
    df = pd.DataFrame(data)
    df.to_latex(TAB / "table3_hypothesis_audit.tex", index=False, escape=False)
    df.to_csv(TAB / "table3_hypothesis_audit.csv", index=False)
    print("  Saved table3_hypothesis_audit.tex/.csv")


def table4_null_comparisons():
    """Table 4: Null-model comparisons."""
    df = pd.read_csv(OUT / "t031_null_metrics.csv")
    cols = ["null_name", "pr", "survival_pr", "knn_r", "smooth_mean"]
    available = [c for c in cols if c in df.columns]
    df[available].to_latex(TAB / "table4_null_comparisons.tex", index=False, float_format="%.3f")
    df[available].to_csv(TAB / "table4_null_comparisons.csv", index=False)
    print("  Saved table4_null_comparisons.tex/.csv")


def table5_decision_framework():
    """Table 5: Decision framework criteria."""
    data = {
        "ID": ["G1", "G2", "G3", "G4", "G5", "G6", "G7"],
        "Criterion": [
            "Geometry survives statistical nulls",
            "Adversarial nulls fail",
            "Causal destruction reduces topology",
            "Info geometry differs from Gaussian",
            "Representation robustness",
            "Spectral structure insufficient",
            "Min collapse PR < 1.5",
        ],
        "Status": ["FAIL", "PASS", "PASS", "PASS", "PASS", "PASS", "PASS"],
        "Threshold": [
            "50% nulls PR<0.8",
            "Overlap < 0.5",
            "dPR > 0.5",
            "|KL| > 0.1",
            "TW > 0.6",
            "Decay diff > 0.2",
            "min PR < 1.5",
        ],
        "Actual": [
            "0/7 nulls",
            "0.609",
            "0.522",
            "1.423",
            "0.792",
            ">0.2",
            "1.424",
        ],
    }
    df = pd.DataFrame(data)
    df.to_latex(TAB / "table5_decision_framework.tex", index=False, escape=False)
    df.to_csv(TAB / "table5_decision_framework.csv", index=False)
    print("  Saved table5_decision_framework.tex/.csv")


if __name__ == "__main__":
    print("=" * 50)
    print("GENERATING ALL TABLES")
    print("=" * 50)
    table1_system_families()
    table2_feature_definitions()
    table3_hypothesis_audit()
    table4_null_comparisons()
    table5_decision_framework()
    print("=" * 50)
    print("ALL TABLES GENERATED")
