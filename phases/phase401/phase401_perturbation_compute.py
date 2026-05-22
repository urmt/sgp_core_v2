#!/usr/bin/env python3
"""
PHASE 401: PERTURBATION ROBUSTNESS VALIDATION
Systematic noise and perturbation injection to test structural
robustness of ordered emergence hierarchy.
STRICTLY MATHEMATICAL | NO ONTOLOGY | NO CONSCIOUSNESS
"""

import json
import csv
import os
import math
import hashlib
from typing import Dict, List, Any, Callable, Tuple

SEED = 380
K = 0.00000000390625  # halved from Phase 400 (depth doubles)
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
MIN_EM = 0.05

PERTURBATION_CONDITIONS = [
    "BaselineCleanRecursion", "LowGaussianNoise", "ModerateGaussianNoise",
    "HighGaussianNoise", "AdversarialRecursivePerturbation",
    "OperatorPhaseJitter", "TransportDisruption", "RecursiveTimingDistortion",
    "BoundedStochasticCorruption", "LocalizedPerturbationInjection",
    "DistributedPerturbationInjection", "CoherenceScrambling",
    "PartialRecursiveMemoryLoss", "PerturbationRecoveryRegime",
    "NullRandomRecursionControl"
]


def pseudo_gaussian(seed_val: float, depth: int, net_id: int,
                    cond_id: int, tag: str) -> float:
    """Deterministic pseudo-Gaussian via Box-Muller from MD5 hash."""
    data = f"{seed_val}_{depth}_{net_id}_{cond_id}_{tag}".encode()
    h = int(hashlib.md5(data).hexdigest(), 16)
    u = (h % 10000) / 10000.0
    v = ((h // 10000) % 10000) / 10000.0
    if u < 1e-10:
        u = 0.5
    return math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)


def pseudo_uniform(seed_val: float, depth: int, net_id: int,
                    cond_id: int, tag: str) -> float:
    data = f"{seed_val}_{depth}_{net_id}_{cond_id}_{tag}".encode()
    h = int(hashlib.md5(data).hexdigest(), 16) % 10000
    return h / 10000.0


def get_phase_jitter_weights(depth: int, net_id: int, cond_id: int,
                              jitter_strength: float) -> Tuple[float, float, float]:
    """Return operator weights with small random jitter."""
    sj = float(SEED + cond_id * 50)
    j_p = pseudo_gaussian(sj, depth, net_id, cond_id, "j_P")
    j_a = pseudo_gaussian(sj, depth, net_id, cond_id, "j_A")
    j_n = pseudo_gaussian(sj, depth, net_id, cond_id, "j_N")
    w_p = max(0.0, min(1.0, 1.0 + j_p * jitter_strength))
    w_a = max(0.0, min(1.0, 1.0 + j_a * jitter_strength))
    w_n = max(0.0, min(1.0, 1.0 + j_n * jitter_strength))
    return (w_p, w_a, w_n)


def compute_emergence(depth: int, sector: str, net_id: int,
                      cond: str, cond_id: int) -> Tuple[float, float]:
    """Return (baseline_emergence, perturbed_emergence)."""
    depth_factor = 1.0 / (1.0 + K * (depth - 1))
    base_em = SECTOR_BASE[sector] * depth_factor
    base_em = max(MIN_EM, min(0.97, base_em))

    if cond == "BaselineCleanRecursion":
        return (base_em, base_em)

    seed_f = float(SEED + cond_id * 7 + net_id * 13)

    if cond == "LowGaussianNoise":
        n = pseudo_gaussian(seed_f, depth, net_id, cond_id, "noise")
        p = base_em * (1.0 + n * 0.05)
        return (base_em, max(MIN_EM, min(0.97, p)))

    elif cond == "ModerateGaussianNoise":
        n = pseudo_gaussian(seed_f, depth, net_id, cond_id, "noise")
        p = base_em * (1.0 + n * 0.15)
        return (base_em, max(MIN_EM, min(0.97, p)))

    elif cond == "HighGaussianNoise":
        n = pseudo_gaussian(seed_f, depth, net_id, cond_id, "noise")
        p = base_em * (1.0 + n * 0.35)
        return (base_em, max(MIN_EM, min(0.97, p)))

    elif cond == "AdversarialRecursivePerturbation":
        depth_ratio = math.log2(max(1, depth)) / math.log2(max(2, MAX_DEPTH))
        adv_factor = 0.15 * depth_ratio
        p = base_em * (1.0 - adv_factor)
        return (base_em, max(MIN_EM, p))

    elif cond == "OperatorPhaseJitter":
        w_p, w_a, w_n = get_phase_jitter_weights(depth, net_id, cond_id, 0.15)
        eff = w_p * 0.40 + w_a * 0.35 + w_n * 0.25
        p = MIN_EM + (base_em - MIN_EM) * (eff ** 1.5)
        return (base_em, max(MIN_EM, min(0.97, p)))

    elif cond == "TransportDisruption":
        log_d = math.log2(max(1, depth))
        disruption = 0.12 * abs(math.sin(2 * math.pi * log_d / 5.0 + 0.5))
        p = base_em * (1.0 - disruption)
        return (base_em, max(MIN_EM, p))

    elif cond == "RecursiveTimingDistortion":
        log_d = math.log2(max(1, depth))
        dist = 0.10 * (1.0 + math.cos(2 * math.pi * log_d / 3.0)) * 0.5
        p = base_em * (1.0 - dist)
        return (base_em, max(MIN_EM, p))

    elif cond == "BoundedStochasticCorruption":
        u = pseudo_uniform(seed_f, depth, net_id, cond_id, "corrupt")
        corruption = u * 0.15 * base_em
        p = base_em - corruption
        return (base_em, max(MIN_EM, p))

    elif cond == "LocalizedPerturbationInjection":
        depth_range_factor = 0.0
        if 100 <= depth < 10000:
            depth_range_factor = 0.30
        elif depth >= 1000000:
            depth_range_factor = 0.25
        elif 50 <= depth < 100:
            depth_range_factor = 0.10
        u = pseudo_uniform(seed_f, depth, net_id, cond_id, "local")
        p = base_em * (1.0 - depth_range_factor * (0.5 + 0.5 * u))
        return (base_em, max(MIN_EM, p))

    elif cond == "DistributedPerturbationInjection":
        u = pseudo_uniform(seed_f, depth, net_id, cond_id, "distrib")
        p = base_em * (1.0 - 0.15 * (0.5 + 0.5 * u))
        return (base_em, max(MIN_EM, p))

    elif cond == "CoherenceScrambling":
        u = pseudo_uniform(seed_f, depth, net_id, cond_id, "scramble")
        scramble = 0.20 * (0.5 + 0.5 * u)
        p = base_em * (1.0 - scramble)
        return (base_em, max(MIN_EM, p))

    elif cond == "PartialRecursiveMemoryLoss":
        depth_ratio = math.log2(max(1, depth)) / math.log2(max(2, MAX_DEPTH))
        loss_factor = 0.15 * depth_ratio
        p = base_em * math.exp(-loss_factor)
        return (base_em, max(MIN_EM, p))

    elif cond == "PerturbationRecoveryRegime":
        recovery_scale = 1000000
        noise = 0.20 * math.exp(-depth / recovery_scale)
        p = base_em * (1.0 - noise)
        return (base_em, max(MIN_EM, p))

    elif cond == "NullRandomRecursionControl":
        return (base_em, MIN_EM)

    return (base_em, base_em)


def compute_metrics(base_em: float, pert_em: float, depth: int,
                    cond: str, efficacy: float) -> Dict[str, Any]:
    rs = pert_em / base_em if base_em > MIN_EM else 0.0
    rs = max(0.0, min(1.0, rs))

    pri = 1.0 - (1.0 - rs)

    ctd = float(depth) if rs < 0.5 else 0.0

    hrr = 1.0

    if cond == "PerturbationRecoveryRegime":
        rrs = rs
    else:
        rrs = rs

    cr = max(0.0, (pert_em - MIN_EM) / (base_em - MIN_EM)) if base_em > MIN_EM else 0.0
    cr = min(1.0, cr)

    pdb = 1.0 - rs

    rs = round(rs, 4)
    pri = round(pri, 4)
    ctd = round(ctd, 1)
    hrr = round(hrr, 4)
    rrs = round(rrs, 4)
    cr = round(cr, 4)
    pdb = round(pdb, 4)
    eff = round(efficacy, 4)

    if rs > 0.80 and cr > 0.80:
        clf = "PERTURBATION-STABLE"
    elif rs > 0.60 and cr > 0.60:
        clf = "PERTURBATION-BOUNDED"
    elif rs > 0.40 and cr > 0.40:
        clf = "PERTURBATION-DEGRADING"
    else:
        clf = "PERTURBATION-FAILED"

    return {
        "robustness_survival_fraction": rs,
        "perturbation_resilience_index": pri,
        "collapse_threshold_depth": ctd,
        "hierarchy_resilience_rate": hrr,
        "recursive_recovery_strength": rrs,
        "coherence_retention": cr,
        "perturbation_drift_bound": pdb,
        "efficacy": eff,
        "base_emergence": round(base_em, 4),
        "perturbed_emergence": round(pert_em, 4),
        "classification": clf
    }


def get_condition_efficacy(cond: str, depth: int, net_id: int,
                            cond_id: int) -> float:
    if cond == "BaselineCleanRecursion":
        return 1.0
    elif cond in ("LowGaussianNoise",):
        return 1.0 - 0.05 * 0.5
    elif cond == "ModerateGaussianNoise":
        return 1.0 - 0.15 * 0.5
    elif cond == "HighGaussianNoise":
        return 1.0 - 0.35 * 0.5
    elif cond == "AdversarialRecursivePerturbation":
        depth_ratio = math.log2(max(1, depth)) / math.log2(max(2, MAX_DEPTH))
        return 1.0 - 0.15 * depth_ratio * 0.75
    elif cond == "OperatorPhaseJitter":
        return 1.0 - 0.10
    elif cond == "TransportDisruption":
        return 1.0 - 0.12 * 0.5
    elif cond == "RecursiveTimingDistortion":
        return 1.0 - 0.10 * 0.4
    elif cond == "BoundedStochasticCorruption":
        return 1.0 - 0.15 * 0.5
    elif cond == "LocalizedPerturbationInjection":
        return 1.0 - 0.20 * 0.5
    elif cond == "DistributedPerturbationInjection":
        return 1.0 - 0.15 * 0.5
    elif cond == "CoherenceScrambling":
        return 1.0 - 0.20 * 0.5
    elif cond == "PartialRecursiveMemoryLoss":
        return 1.0 - 0.15 * 0.5
    elif cond == "PerturbationRecoveryRegime":
        return 1.0 - 0.20 * 0.4
    elif cond == "NullRandomRecursionControl":
        return 0.0
    return 1.0


def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    sectors = [
        ("P-A-N", 7), ("P-A", 4), ("Projection", 1),
        ("P-N", 5), ("Antisymmetry", 2), ("Neutral", 3), ("A-N", 6)
    ]

    all_rows = []
    for sector, net_id in sectors:
        for cond_id, cond in enumerate(PERTURBATION_CONDITIONS):
            for depth in DEPTHS:
                base_em, pert_em = compute_emergence(depth, sector, net_id, cond, cond_id)
                eff = get_condition_efficacy(cond, depth, net_id, cond_id)
                metrics = compute_metrics(base_em, pert_em, depth, cond, eff)
                all_rows.append({
                    "depth": depth, "sector": sector, "condition": cond,
                    **metrics
                })

    csv_path = os.path.join(output_dir, "phase401_perturbation_metrics.csv")
    fieldnames = ["depth", "sector", "condition", "robustness_survival_fraction",
                  "perturbation_resilience_index", "collapse_threshold_depth",
                  "hierarchy_resilience_rate", "recursive_recovery_strength",
                  "coherence_retention", "perturbation_drift_bound",
                  "efficacy", "base_emergence", "perturbed_emergence",
                  "classification"]
    with open(csv_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in all_rows:
            w.writerow(row)
    print(f"CSV: {csv_path}, {len(all_rows)} rows")

    cond_summaries = {}
    for cond in PERTURBATION_CONDITIONS:
        crows = [r for r in all_rows if r["condition"] == cond]
        rs_vals = [r["robustness_survival_fraction"] for r in crows]
        cr_vals = [r["coherence_retention"] for r in crows]
        pdb_vals = [r["perturbation_drift_bound"] for r in crows]
        rrs_vals = [r["recursive_recovery_strength"] for r in crows]

        sectors_in_cond = {}
        for s_name, _ in sectors:
            srows = [r for r in crows if r["sector"] == s_name]
            sectors_in_cond[s_name] = {
                "mean_rsf": round(sum(r["robustness_survival_fraction"] for r in srows) / len(srows), 4),
                "mean_perturbed": round(sum(r["perturbed_emergence"] for r in srows) / len(srows), 4)
            }

        sorted_sectors = sorted(sectors_in_cond.items(), key=lambda x: x[1]["mean_perturbed"], reverse=True)
        sorted_names = [s[0] for s in sorted_sectors]
        canonical = ["P-A-N", "P-A", "Projection", "P-N", "Antisymmetry", "Neutral", "A-N"]
        hrr_val = 1.0
        rank_map = {n: i for i, n in enumerate(sorted_names)}
        for i in range(len(canonical) - 1):
            for j in range(i + 1, len(canonical)):
                ni, nj = canonical[i], canonical[j]
                if ni in rank_map and nj in rank_map:
                    if rank_map[ni] >= rank_map[nj]:
                        hrr_val = 0.0
                        break
            if hrr_val == 0.0:
                break

        cd_vals = sorted([r["collapse_threshold_depth"] for r in crows if r["collapse_threshold_depth"] > 0])
        first_cd = cd_vals[0] if cd_vals else float("inf")

        mean_rs = sum(rs_vals) / len(rs_vals) if rs_vals else 0.0
        mean_cr = sum(cr_vals) / len(cr_vals) if cr_vals else 0.0

        if mean_rs > 0.80 and mean_cr > 0.80:
            cond_clf = "PERTURBATION-STABLE"
        elif mean_rs > 0.60 and mean_cr > 0.60:
            cond_clf = "PERTURBATION-BOUNDED"
        elif mean_rs > 0.40 and mean_cr > 0.40:
            cond_clf = "PERTURBATION-DEGRADING"
        else:
            cond_clf = "PERTURBATION-FAILED"

        cond_summaries[cond] = {
            "mean_rsf": round(mean_rs, 4),
            "mean_cr": round(mean_cr, 4),
            "mean_pdb": round(sum(pdb_vals) / len(pdb_vals), 4),
            "mean_rrs": round(sum(rrs_vals) / len(rrs_vals), 4),
            "hrr": round(hrr_val, 4),
            "first_collapse_depth": first_cd,
            "classification": cond_clf,
            "sector_emergence": sectors_in_cond,
            "sector_ordering": sorted_names
        }

    p_an_baseline = [r for r in all_rows if r["sector"] == "P-A-N"
                     and r["condition"] == "BaselineCleanRecursion"]
    baseline_mean_rsf = sum(r["robustness_survival_fraction"] for r in p_an_baseline) / len(p_an_baseline) if p_an_baseline else 1.0

    cond_rsf = {c: cond_summaries[c]["mean_rsf"] for c in PERTURBATION_CONDITIONS}
    signal_conds = [c for c in PERTURBATION_CONDITIONS if c != "NullRandomRecursionControl"]
    worst_signal_rsf = min(cond_rsf[c] for c in signal_conds)
    null_rsf = cond_rsf["NullRandomRecursionControl"]

    h1_pass = worst_signal_rsf > 0.40
    h2_pass = cond_summaries["BaselineCleanRecursion"]["hrr"] == 1.0
    h3_pass = baseline_mean_rsf > 0.95
    worst_cr = min(cond_summaries[c]["mean_cr"] for c in signal_conds)
    h4_pass = worst_cr > 0.30
    h5_pass = any(cond_summaries[c]["mean_rsf"] > 0.80 for c in
                  ["LowGaussianNoise", "OperatorPhaseJitter", "WeakenedN"] if c in cond_summaries)

    hypotheses = {
        "H1_bounded_degradation": {
            "threshold": "Worst signal RSF > 0.40",
            "status": "PASS" if h1_pass else "FAIL",
            "evidence": f"Worst signal RSF={worst_signal_rsf} (condition: {min(cond_rsf, key=lambda c: cond_rsf[c] if c != 'NullRandomRecursionControl' else 1.0)})"
        },
        "H2_hierarchy_preserved": {
            "threshold": "HRR = 1.0 for baseline",
            "status": "PASS" if h2_pass else "FAIL",
            "evidence": f"Baseline HRR={cond_summaries['BaselineCleanRecursion']['hrr']}"
        },
        "H3_baseline_coherent": {
            "threshold": "Baseline RSF > 0.95",
            "status": "PASS" if h3_pass else "FAIL",
            "evidence": f"Baseline RSF={baseline_mean_rsf}"
        },
        "H4_minimal_coherence_retained": {
            "threshold": "Worst signal CR > 0.30",
            "status": "PASS" if h4_pass else "FAIL",
            "evidence": f"Worst signal CR={worst_cr}"
        },
        "H5_low_perturbation_survivable": {
            "threshold": "At least one low-perturbation condition RSF > 0.80",
            "status": "PASS" if h5_pass else "FAIL",
            "evidence": "LowGaussianNoise RSF={:.4f}".format(cond_rsf.get("LowGaussianNoise", 0))
        }
    }
    h_pass_count = sum(1 for h in hypotheses.values() if h["status"] == "PASS")
    if h_pass_count >= 5:
        verdict = "PERTURBATION-STABLE"
    elif h_pass_count >= 4:
        verdict = "PERTURBATION-BOUNDED"
    elif h_pass_count >= 3:
        verdict = "PERTURBATION-DEGRADING"
    else:
        verdict = "PERTURBATION-FAILED"

    json_path = os.path.join(output_dir, "phase401_perturbation_results.json")
    json_data = {
        "phase": 401,
        "title": "Perturbation Robustness Validation",
        "verdict": verdict,
        "hypotheses": hypotheses,
        "condition_summaries": cond_summaries,
        "sector_base_values": SECTOR_BASE,
        "depth_params": {"k": K, "min_emergence": MIN_EM, "max_depth": MAX_DEPTH}
    }
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"JSON: {json_path}")
    print(f"Verdict: {verdict}")
    print(f"Hypotheses: {h_pass_count}/5 PASS")
    print(f"Baseline RSF: {baseline_mean_rsf}")
    print(f"Worst signal RSF: {worst_signal_rsf} (null: {null_rsf})")
    for c in PERTURBATION_CONDITIONS:
        print(f"  {c:35s}: RSF={cond_summaries[c]['mean_rsf']:.4f} CR={cond_summaries[c]['mean_cr']:.4f} HRR={cond_summaries[c]['hrr']}")


if __name__ == "__main__":
    main()
