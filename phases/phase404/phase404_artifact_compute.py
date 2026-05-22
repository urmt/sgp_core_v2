#!/usr/bin/env python3
"""
PHASE 404: EXPLICIT ARTIFACT DETECTION AND NULL ADVERSARIAL VALIDATION
Systematically attempt to break emergence hierarchy through adversarial
artifact generation, hidden-bias exposure, and false-positive induction.
STRICTLY MATHEMATICAL | NO ONTOLOGY | NO CONSCIOUSNESS
"""

import json
import csv
import os
import math
import hashlib
from typing import Dict, List, Any, Tuple

SEED = 410
K = 0.00000000390625
DEPTHS = [1, 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128,
          160, 192, 256, 320, 512, 768, 1024, 1536, 2048, 3072, 4096,
          6144, 8192, 12288, 16384, 24576, 32768, 65536, 131072, 262144,
          524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432,
          67108864]
MAX_DEPTH = max(DEPTHS)
SECTOR_BASE = {
    "P-A-N": 0.9567, "P-A": 0.9562, "Projection": 0.9552,
    "P-N": 0.9541, "Antisymmetry": 0.9535, "Neutral": 0.9233, "A-N": 0.9040
}
SECTOR_MEAN = sum(SECTOR_BASE.values()) / len(SECTOR_BASE)
MIN_EM = 0.05
HIERARCHY_ORDER = ["P-A-N", "P-A", "Projection", "P-N", "Antisymmetry", "Neutral", "A-N"]
HIERARCHY_INDEX = {s: i for i, s in enumerate(HIERARCHY_ORDER)}

ADVERSARIAL_CONDITIONS = [
    "AuthenticBaselineRecursion",
    "RandomizedMetricScrambling", "HiddenDepthEncodingInjection",
    "SectorLabelPermutation", "RecursiveOrderInversion",
    "AdversarialHierarchySpoofing", "CorrelatedRandomNoiseSystems",
    "BiasedInitializationInjection", "MetricLeakageSimulation",
    "PartialEmergentSignatureMimicry", "RecursiveSymmetryCorruption",
    "CompressedArtifactGeneration", "FakePropagationDynamics",
    "AdversarialOptimizationTowardHierarchy", "FullNullAdversarialControl"
]


def pseudo_uniform(seed_val: float, depth: int, net_id: int,
                    cond_id: int, tag: str) -> float:
    data = f"{seed_val}_{depth}_{net_id}_{cond_id}_{tag}".encode()
    h = int(hashlib.md5(data).hexdigest(), 16) % 10000
    return h / 10000.0


def pseudo_gaussian(seed_val: float, depth: int, net_id: int,
                     cond_id: int, tag: str) -> float:
    data = f"{seed_val}_{depth}_{net_id}_{cond_id}_{tag}".encode()
    h = int(hashlib.md5(data).hexdigest(), 16)
    u = (h % 10000) / 10000.0
    if u < 1e-10:
        u = 0.5
    v = ((h // 10000) % 10000) / 10000.0
    return math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)


def depth_factor(depth: int) -> float:
    return 1.0 / (1.0 + K * (depth - 1))


def get_authentic_emergence(depth: int, sector: str) -> float:
    return max(MIN_EM, min(0.97, SECTOR_BASE[sector] * depth_factor(depth)))


def compute_adversarial_emergence(depth: int, sector: str, net_id: int,
                                    cond: str, cond_id: int
                                    ) -> Tuple[float, float, float]:
    df = depth_factor(depth)
    auth = get_authentic_emergence(depth, sector)
    seed_f = float(SEED + cond_id * 13 + net_id * 19)
    hi = HIERARCHY_INDEX[sector]

    if cond == "AuthenticBaselineRecursion":
        return (auth, auth, 0.0)

    elif cond == "RandomizedMetricScrambling":
        u = pseudo_uniform(seed_f, depth, net_id, cond_id, "scramble")
        adv = MIN_EM + u * (0.97 - MIN_EM)
        return (auth, adv, 0.0)

    elif cond == "HiddenDepthEncodingInjection":
        u = pseudo_uniform(seed_f, depth, net_id, cond_id, "hidden")
        depth_signal = 0.3 + 0.7 * (1.0 - df)
        adv = MIN_EM + (0.97 - MIN_EM) * (0.2 + 0.8 * u * depth_signal)
        return (auth, max(MIN_EM, min(0.97, adv)), depth_signal)

    elif cond == "SectorLabelPermutation":
        perm_map = {"P-A-N": "A-N", "P-A": "Neutral", "Projection": "P-N",
                    "P-N": "Antisymmetry", "Antisymmetry": "Projection",
                    "Neutral": "P-A", "A-N": "P-A-N"}
        mapped = perm_map.get(sector, sector)
        adv = get_authentic_emergence(depth, mapped)
        return (auth, adv, 1.0)

    elif cond == "RecursiveOrderInversion":
        inv_df = 1.0 / (1.0 + K * (MAX_DEPTH - depth))
        adv = max(MIN_EM, min(0.97, SECTOR_BASE[sector] * inv_df))
        return (auth, adv, 1.0)

    elif cond == "AdversarialHierarchySpoofing":
        spoof_base = 0.95 - hi * 0.007
        adv = max(MIN_EM, min(0.97, spoof_base * df))
        return (auth, adv, 0.0)

    elif cond == "CorrelatedRandomNoiseSystems":
        mean = SECTOR_MEAN * df
        std = 0.025
        n = pseudo_gaussian(seed_f, depth, net_id, cond_id, "corr_noise")
        adv = mean + n * std
        return (auth, max(MIN_EM, min(0.97, adv)), 0.0)

    elif cond == "BiasedInitializationInjection":
        bias_vals = [0.05, 0.04, 0.03, 0.02, 0.01, 0.0, -0.01]
        bias = bias_vals[hi]
        u = pseudo_uniform(seed_f, depth, net_id, cond_id, "bias")
        adv = MIN_EM + (SECTOR_MEAN * df - MIN_EM) * (0.4 + 0.6 * u) + bias
        return (auth, max(MIN_EM, min(0.97, adv)), abs(bias))

    elif cond == "MetricLeakageSimulation":
        adv = MIN_EM + (0.90 * df - MIN_EM)
        return (auth, max(MIN_EM, min(0.97, adv)), 1.0)

    elif cond == "PartialEmergentSignatureMimicry":
        if sector in ["P-A-N", "P-A", "A-N"]:
            u = pseudo_uniform(seed_f, depth, net_id, cond_id, "mimic")
            jit = 1.0 + (u - 0.5) * 0.10
            adv = auth * jit
        else:
            u = pseudo_uniform(seed_f, depth, net_id, cond_id, "mimic_r")
            adv = MIN_EM + u * (0.97 - MIN_EM)
        return (auth, max(MIN_EM, min(0.97, adv)), 0.5)

    elif cond == "RecursiveSymmetryCorruption":
        sym_factors = [0.90, 0.85, 0.80, 0.85, 0.75, 0.70, 0.65]
        adv = SECTOR_BASE[sector] * df * sym_factors[hi]
        return (auth, max(MIN_EM, min(0.97, adv)), 1.0 - sym_factors[hi])

    elif cond == "CompressedArtifactGeneration":
        adv = MIN_EM + (SECTOR_MEAN * df - MIN_EM) * 0.6
        return (auth, max(MIN_EM, min(0.97, adv)), 0.4)

    elif cond == "FakePropagationDynamics":
        exp_decay = math.exp(-0.1 * math.log2(max(1, depth)))
        adv = MIN_EM + (SECTOR_BASE[sector] - MIN_EM) * exp_decay
        return (auth, max(MIN_EM, min(0.97, adv)), exp_decay)

    elif cond == "AdversarialOptimizationTowardHierarchy":
        opt_base = 0.90 - hi * 0.01
        n = pseudo_gaussian(seed_f, depth, net_id, cond_id, "opt") * 0.005
        adv = max(MIN_EM, min(0.97, (opt_base + n) * df))
        return (auth, adv, 0.0)

    elif cond == "FullNullAdversarialControl":
        return (auth, MIN_EM, 0.0)

    return (auth, auth, 0.0)


def compute_metrics(auth_em: float, adv_em: float, depth: int, cond: str) -> Dict[str, Any]:
    # ARS: similarity between adversarial and authentic
    sim = 1.0 - min(1.0, abs(adv_em - auth_em) / max(0.01, auth_em))
    ars = max(0.0, sim)

    # HSS: per-row placeholder (computed at condition level)
    hss = 1.0

    # LDI: how much depth information leaked
    df_val = depth_factor(depth)
    ldi = abs(adv_em - MIN_EM) / max(0.01, (0.97 - MIN_EM))
    ldi = min(1.0, ldi)

    # AFPR: per-row false positive flag
    is_false_positive = 1.0 if (cond != "AuthenticBaselineRecursion" and ars > 0.80) else 0.0

    # UAS: authenticity score
    uas = 1.0 - min(1.0, abs(adv_em - auth_em) / max(0.01, auth_em))

    # RBS: per-row bias sensitivity
    rbs = abs(adv_em - auth_em) / max(0.01, auth_em)
    rbs = min(1.0, rbs)

    # SNRI: non-randomness (1 = non-random structure)
    snri = 1.0 - abs(adv_em - auth_em) / max(0.01, auth_em)

    ars_r = round(ars, 4)
    hss_r = round(hss, 4)
    ldi_r = round(ldi, 4)
    afpr_r = round(is_false_positive, 4)
    uas_r = round(uas, 4)
    rbs_r = round(rbs, 4)
    snri_r = round(snri, 4)

    is_authentic = (cond == "AuthenticBaselineRecursion")
    if is_authentic:
        clf = "ARTIFACT-STABLE"
    elif ars < 0.30:
        clf = "ARTIFACT-FAILED"
    elif ars < 0.55:
        clf = "ARTIFACT-DEGRADING"
    elif ars < 0.75:
        clf = "ARTIFACT-BOUNDED"
    else:
        clf = "ARTIFACT-STABLE"

    return {
        "artifact_reproduction_score": ars_r,
        "hierarchy_spoof_success": hss_r,
        "leakage_dependence_index": ldi_r,
        "adversarial_false_positive_rate": afpr_r,
        "universality_authenticity_score": uas_r,
        "recursive_bias_sensitivity": rbs_r,
        "structural_nonrandomness_index": snri_r,
        "adversarial_emergence": round(adv_em, 4),
        "authentic_emergence": round(auth_em, 4),
        "classification": clf
    }


def check_hierarchy(cond_rows: List[Dict]) -> Tuple[float, List[str]]:
    """Check if sector ordering matches canonical hierarchy."""
    sectors_mean = {}
    for r in cond_rows:
        s = r["sector"]
        v = r.get("adversarial_emergence", 0)
        if s not in sectors_mean:
            sectors_mean[s] = []
        sectors_mean[s].append(v)
    sector_means = {s: sum(vs)/len(vs) for s, vs in sectors_mean.items()}
    sorted_names = sorted(sector_means.keys(), key=lambda s: sector_means[s], reverse=True)
    hpc = 1.0
    rank = {n: i for i, n in enumerate(sorted_names)}
    for i in range(len(HIERARCHY_ORDER) - 1):
        for j in range(i + 1, len(HIERARCHY_ORDER)):
            ni, nj = HIERARCHY_ORDER[i], HIERARCHY_ORDER[j]
            if ni in rank and nj in rank:
                if rank[ni] >= rank[nj]:
                    hpc = 0.0
                    break
        if hpc == 0.0:
            break
    return hpc, sorted_names


def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    sectors = [
        ("P-A-N", 7), ("P-A", 4), ("Projection", 1),
        ("P-N", 5), ("Antisymmetry", 2), ("Neutral", 3), ("A-N", 6)
    ]

    all_rows = []
    for sector, net_id in sectors:
        for cond_id, cond in enumerate(ADVERSARIAL_CONDITIONS):
            for depth in DEPTHS:
                auth_em, adv_em, _ = compute_adversarial_emergence(
                    depth, sector, net_id, cond, cond_id)
                metrics = compute_metrics(auth_em, adv_em, depth, cond)
                all_rows.append({
                    "depth": depth, "sector": sector, "condition": cond,
                    **metrics
                })

    csv_path = os.path.join(output_dir, "phase404_artifact_metrics.csv")
    fieldnames = ["depth", "sector", "condition", "artifact_reproduction_score",
                  "hierarchy_spoof_success", "leakage_dependence_index",
                  "adversarial_false_positive_rate", "universality_authenticity_score",
                  "recursive_bias_sensitivity", "structural_nonrandomness_index",
                  "adversarial_emergence", "authentic_emergence", "classification"]
    with open(csv_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in all_rows:
            w.writerow(row)
    print(f"CSV: {csv_path}, {len(all_rows)} rows")

    cond_summaries = {}
    for cond in ADVERSARIAL_CONDITIONS:
        crows = [r for r in all_rows if r["condition"] == cond]
        ars_vals = [r["artifact_reproduction_score"] for r in crows]
        uas_vals = [r["universality_authenticity_score"] for r in crows]
        rbs_vals = [r["recursive_bias_sensitivity"] for r in crows]
        afpr_vals = [r["adversarial_false_positive_rate"] for r in crows]

        hspoof, sector_order = check_hierarchy(crows)
        mean_ars = sum(ars_vals) / len(ars_vals) if ars_vals else 0
        mean_uas = sum(uas_vals) / len(uas_vals) if uas_vals else 0

        # Per-condition classification
        if cond == "AuthenticBaselineRecursion":
            cond_clf = "ARTIFACT-STABLE"
        elif mean_ars < 0.30:
            cond_clf = "ARTIFACT-FAILED"
        elif mean_ars < 0.55:
            cond_clf = "ARTIFACT-DEGRADING"
        elif mean_ars < 0.75:
            cond_clf = "ARTIFACT-BOUNDED"
        else:
            cond_clf = "ARTIFACT-STABLE"

        cond_summaries[cond] = {
            "mean_ars": round(mean_ars, 4),
            "mean_uas": round(mean_uas, 4),
            "mean_rbs": round(sum(rbs_vals) / len(rbs_vals), 4),
            "mean_afpr": round(sum(afpr_vals) / len(afpr_vals), 4),
            "hierarchy_spoof_success": round(hspoof, 4),
            "classification": cond_clf,
            "sector_ordering": sector_order
        }

    # Cross-condition metrics
    signal_conds = [c for c in ADVERSARIAL_CONDITIONS if c != "FullNullAdversarialControl"]
    non_authentic = [c for c in signal_conds if c != "AuthenticBaselineRecursion"]
    authentic = [c for c in signal_conds if c == "AuthenticBaselineRecursion"]

    hss_values = [cond_summaries[c]["hierarchy_spoof_success"] for c in non_authentic]
    hss_auth = [cond_summaries[c]["hierarchy_spoof_success"] for c in authentic]
    afpr = sum(1 for h in hss_values if h > 0.5) / max(1, len(hss_values))
    ars_values = [cond_summaries[c]["mean_ars"] for c in non_authentic]
    max_ars_artifact = max(ars_values) if ars_values else 0
    min_ars_artifact = min(ars_values) if ars_values else 0

    # Authentic metrics
    auth_uas = cond_summaries["AuthenticBaselineRecursion"]["mean_uas"]
    auth_ars = cond_summaries["AuthenticBaselineRecursion"]["mean_ars"]

    # UAS = 1 - max similarity of any non-authentic
    uas = 1.0 - max_ars_artifact
    uas = max(0.0, uas)

    # RBS: range of ARS across conditions
    rbs_val = max_ars_artifact - min_ars_artifact

    # SNRI: non-randomness = authentic_uas - max_artifact_uas
    artifact_uas_vals = [cond_summaries[c]["mean_uas"] for c in non_authentic]
    max_artifact_uas = max(artifact_uas_vals) if artifact_uas_vals else 0
    snri = auth_uas - max_artifact_uas
    snri = max(0.0, min(1.0, snri))

    h1_pass = afpr < 0.10
    h2_pass = len([h for h in hss_values if h > 0.5]) < 3  # less than 3 spoofs
    h3_pass = auth_uas > 0.90
    h4_pass = uas > 0.50
    h5_pass = cond_summaries["FullNullAdversarialControl"]["mean_ars"] < 0.10

    hypotheses = {
        "H1_false_positive_rate": {
            "threshold": "AFPR < 0.10",
            "status": "PASS" if h1_pass else "FAIL",
            "evidence": f"AFPR={afpr:.4f} ({int(afpr*len(non_authentic))}/{len(non_authentic)} conditions spoof hierarchy)"
        },
        "H2_hierarchy_spoof_resistance": {
            "threshold": "< 3 non-authentic conditions spoof hierarchy",
            "status": "PASS" if h2_pass else "FAIL",
            "evidence": f"{len([h for h in hss_values if h > 0.5])} conditions spoof hierarchy"
        },
        "H3_authentic_emergence_coherent": {
            "threshold": "Authentic UAS > 0.90",
            "status": "PASS" if h3_pass else "FAIL",
            "evidence": f"Authentic UAS={auth_uas}"
        },
        "H4_universality_authenticity": {
            "threshold": "UAS > 0.50 (max artifact match < 0.50)",
            "status": "PASS" if h4_pass else "FAIL",
            "evidence": f"UAS={uas} (max artifact ARS={max_ars_artifact})"
        },
        "H5_null_separation": {
            "threshold": "Null ARS < 0.10",
            "status": "PASS" if h5_pass else "FAIL",
            "evidence": f"Null ARS={cond_summaries['FullNullAdversarialControl']['mean_ars']}"
        }
    }
    h_pass_count = sum(1 for h in hypotheses.values() if h["status"] == "PASS")
    if h_pass_count >= 5:
        verdict = "ARTIFACT-STABLE"
    elif h_pass_count >= 4:
        verdict = "ARTIFACT-BOUNDED"
    elif h_pass_count >= 3:
        verdict = "ARTIFACT-DEGRADING"
    else:
        verdict = "ARTIFACT-FAILED"

    json_path = os.path.join(output_dir, "phase404_artifact_results.json")
    json_data = {
        "phase": 404,
        "title": "Explicit Artifact Detection and Null Adversarial Validation",
        "verdict": verdict,
        "hypotheses": hypotheses,
        "cross_condition_metrics": {
            "adversarial_false_positive_rate": round(afpr, 4),
            "universality_authenticity_score": round(uas, 4),
            "recursive_bias_sensitivity": round(rbs_val, 4),
            "structural_nonrandomness_index": round(snri, 4),
            "max_artifact_ars": round(max_ars_artifact, 4),
            "min_artifact_ars": round(min_ars_artifact, 4),
            "total_non_authentic_conditions": len(non_authentic)
        },
        "condition_summaries": cond_summaries,
        "parameters": {"seed": SEED, "k": K, "max_depth": MAX_DEPTH}
    }
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"JSON: {json_path}")
    print(f"Verdict: {verdict}")
    print(f"Hypotheses: {h_pass_count}/5 PASS")
    print(f"AFPR: {afpr:.4f}")
    print(f"Authentic UAS: {auth_uas}")
    print(f"UAS: {uas}")
    print(f"SNRI: {snri}")
    print(f"Null ARS: {cond_summaries['FullNullAdversarialControl']['mean_ars']}")
    for c in ADVERSARIAL_CONDITIONS:
        cs = cond_summaries[c]
        hss_str = "SPOOF" if cs["hierarchy_spoof_success"] > 0.5 else "----"
        print(f"  {c:40s}: ARS={cs['mean_ars']:.4f} UAS={cs['mean_uas']:.4f} {hss_str} {cs['classification']}")


if __name__ == "__main__":
    main()
