"""
Phase 412: Universality Classification
Determines which recursive systems belong to the SFH-SGP
universality family and which fundamentally do not.
"""

import json, os, csv, math, random
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.bool_): return bool(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)

# ======= SYSTEMS =======
# Each system scored on 10 features [0, 1]

SYSTEM_FEATURES = {
    "SFH_SGP_reference": {
        "f1_formal_operators": 1.0,
        "f2_operator_composition": 1.0,
        "f3_recursive_depth": 1.0,
        "f4_monotonic_decay": 1.0,
        "f5_separable_depth": 1.0,
        "f6_stable_hierarchy": 1.0,
        "f7_relational_states": 1.0,
        "f8_deterministic": 1.0,
        "f9_compositional": 1.0,
        "f10_similarity_emergence": 1.0,
        "phase411_rho": 1.0,
    },
    "CellularAutomata": {
        "f1_formal_operators": 0.3,
        "f2_operator_composition": 0.0,
        "f3_recursive_depth": 1.0,
        "f4_monotonic_decay": 0.5,
        "f5_separable_depth": 0.2,
        "f6_stable_hierarchy": 0.3,
        "f7_relational_states": 0.3,
        "f8_deterministic": 1.0,
        "f9_compositional": 0.0,
        "f10_similarity_emergence": 0.4,
        "phase411_rho": 0.21,
    },
    "GraphPropagation": {
        "f1_formal_operators": 0.2,
        "f2_operator_composition": 0.0,
        "f3_recursive_depth": 0.8,
        "f4_monotonic_decay": 0.7,
        "f5_separable_depth": 0.3,
        "f6_stable_hierarchy": 0.4,
        "f7_relational_states": 0.1,
        "f8_deterministic": 0.8,
        "f9_compositional": 0.0,
        "f10_similarity_emergence": 0.3,
        "phase411_rho": 0.39,
    },
    "AgentInteraction": {
        "f1_formal_operators": 0.1,
        "f2_operator_composition": 0.0,
        "f3_recursive_depth": 0.9,
        "f4_monotonic_decay": 0.4,
        "f5_separable_depth": 0.1,
        "f6_stable_hierarchy": 0.3,
        "f7_relational_states": 0.2,
        "f8_deterministic": 0.5,
        "f9_compositional": 0.0,
        "f10_similarity_emergence": 0.2,
        "phase411_rho": 0.18,
    },
    "SymbolicRecursive": {
        "f1_formal_operators": 0.4,
        "f2_operator_composition": 0.6,
        "f3_recursive_depth": 1.0,
        "f4_monotonic_decay": 0.6,
        "f5_separable_depth": 0.3,
        "f6_stable_hierarchy": 0.5,
        "f7_relational_states": 0.4,
        "f8_deterministic": 0.7,
        "f9_compositional": 0.7,
        "f10_similarity_emergence": 0.3,
        "phase411_rho": 0.18,
    },
    "TensorRecursion": {
        "f1_formal_operators": 0.6,
        "f2_operator_composition": 0.8,
        "f3_recursive_depth": 0.7,
        "f4_monotonic_decay": 0.5,
        "f5_separable_depth": 0.4,
        "f6_stable_hierarchy": 0.4,
        "f7_relational_states": 0.1,
        "f8_deterministic": 1.0,
        "f9_compositional": 0.8,
        "f10_similarity_emergence": 0.1,
        "phase411_rho": -0.07,
    },
    "EvolutionaryOpt": {
        "f1_formal_operators": 0.2,
        "f2_operator_composition": 0.3,
        "f3_recursive_depth": 0.9,
        "f4_monotonic_decay": 0.2,
        "f5_separable_depth": 0.1,
        "f6_stable_hierarchy": 0.2,
        "f7_relational_states": 0.1,
        "f8_deterministic": 0.3,
        "f9_compositional": 0.4,
        "f10_similarity_emergence": 0.2,
        "phase411_rho": -0.86,
    },
}

FEATURE_NAMES = [k for k in SYSTEM_FEATURES["SFH_SGP_reference"].keys()
                 if k.startswith("f")]
N_FEATURES = len(FEATURE_NAMES)
SYSTEM_NAMES = list(SYSTEM_FEATURES.keys())

# ======= COMPUTE MEMBERSHIP SCORES =======
# Default equal weights
DEFAULT_WEIGHTS = {f: 1.0 / N_FEATURES for f in FEATURE_NAMES}

def membership_score(features, weights):
    return sum(features[f] * weights[f] for f in FEATURE_NAMES)

print("=" * 60)
print("PHASE 412: UNIVERSALITY CLASSIFICATION")
print("=" * 60)

print(f"\nFeature Space: {N_FEATURES} dimensions")
print(f"Systems: {len(SYSTEM_NAMES)}\n")

# Default classification
print("--- DEFAULT CLASSIFICATION (equal weights) ---")
results = {}
for sys_name in SYSTEM_NAMES:
    feats = SYSTEM_FEATURES[sys_name]
    score = membership_score(feats, DEFAULT_WEIGHTS)
    if score >= 0.80: label = "CORE_MEMBER"
    elif score >= 0.50: label = "PARTIAL_MEMBER"
    elif score >= 0.20: label = "PERIPHERAL"
    else: label = "EXCLUDED"
    results[sys_name] = {"features": feats, "score": round(score, 4), "label": label}
    rho = feats["phase411_rho"]
    print(f"  {sys_name:25s} score={score:.4f} {label:20s} rho={rho:+.2f}")

# ======= ATTRACTOR FAMILY CLUSTERING =======
print(f"\n--- ATTRACTOR FAMILY CLUSTERING ---")
feature_matrix = np.array([[SYSTEM_FEATURES[s][f] for f in FEATURE_NAMES]
                           for s in SYSTEM_NAMES])
distances = squareform(pdist(feature_matrix, metric='euclidean'))

linkage_matrix = linkage(feature_matrix, method='ward')
clusters = fcluster(linkage_matrix, t=2.0, criterion='distance')

family_map = {}
for i, sys_name in enumerate(SYSTEM_NAMES):
    family_map.setdefault(int(clusters[i]), []).append(sys_name)

print(f"  Number of attractor families: {len(family_map)}")
for fid in sorted(family_map):
    members = ", ".join(family_map[fid])
    print(f"  Family {fid}: {members}")

print("\n  Distance Matrix:")
print(f"  {'':25s}", end="")
for s in SYSTEM_NAMES:
    print(f"{s[:8]:8s}", end="")
print()
for i, s1 in enumerate(SYSTEM_NAMES):
    print(f"  {s1:25s}", end="")
    for j in range(len(SYSTEM_NAMES)):
        print(f"{distances[i][j]:8.3f}", end="")
    print()

# ======= EXCLUSION CLASSES =======
print(f"\n--- EXCLUSION CLASSES ---")
# Determine which features are most deficient for each non-core system
exclusion_classes = {}
for sys_name in SYSTEM_NAMES:
    if sys_name == "SFH_SGP_reference":
        continue
    feats = SYSTEM_FEATURES[sys_name]
    # Find features with score < 0.50 (significant deficiency)
    deficiencies = [(idx, f, feats[f]) for idx, f in enumerate(FEATURE_NAMES)
                    if feats[f] < 0.50]
    # Cluster deficiencies
    missing_operators = any("operator" in f for _, f, _ in deficiencies)
    missing_depth = any("depth" in f or "monotonic" in f for _, f, _ in deficiencies)
    missing_hierarchy = any("hierarchy" in f for _, f, _ in deficiencies)
    missing_relational = any("relational" in f for _, f, _ in deficiencies)
    missing_composition = any("compositional" in f for _, f, _ in deficiencies)
    missing_similarity = any("similarity" in f for _, f, _ in deficiencies)

    tags = []
    if missing_operators: tags.append("NO_OPERATORS")
    if missing_composition: tags.append("NO_COMPOSITION")
    if missing_depth: tags.append("NON_MONOTONIC")
    if missing_hierarchy: tags.append("NO_HIERARCHY")
    if missing_relational: tags.append("NON_RELATIONAL")
    if missing_similarity: tags.append("NON_SIMILARITY")

    exclusion_classes[sys_name] = {
        "deficiencies": [(f, round(v, 2)) for _, f, v in deficiencies],
        "deficiency_count": len(deficiencies),
        "exclusion_tags": tags
    }
    print(f"  {sys_name:25s}: {', '.join(tags)} ({len(deficiencies)} deficiencies)")

# ======= BOUNDARY STABILITY =======
print(f"\n--- BOUNDARY STABILITY (1000 weight perturbations) ---")
N_PERTURB = 1000
classifications_vary = {s: [] for s in SYSTEM_NAMES}

for _ in range(N_PERTURB):
    # Random weights that sum to 1
    raw = np.random.exponential(1, N_FEATURES)
    weights = {FEATURE_NAMES[i]: raw[i] / raw.sum()
               for i in range(N_FEATURES)}
    for sys_name in SYSTEM_NAMES:
        score = membership_score(SYSTEM_FEATURES[sys_name], weights)
        if score >= 0.80: lbl = "CORE_MEMBER"
        elif score >= 0.50: lbl = "PARTIAL_MEMBER"
        elif score >= 0.20: lbl = "PERIPHERAL"
        else: lbl = "EXCLUDED"
        classifications_vary[sys_name].append(lbl)

stability = {}
for sys_name in SYSTEM_NAMES:
    classes = classifications_vary[sys_name]
    dominant = max(set(classes), key=classes.count)
    stability_pct = classes.count(dominant) / N_PERTURB * 100
    all_unique = len(set(classes))
    stability[sys_name] = {
        "dominant_class": dominant,
        "stability_pct": round(stability_pct, 1),
        "classes_seen": all_unique
    }
    print(f"  {sys_name:25s}: {dominant:20s} ({stability_pct:.0f}% stable, {all_unique} classes seen)")

# ======= COMPOSITE METRICS =======
core_score = results["SFH_SGP_reference"]["score"]
non_core_scores = [results[s]["score"] for s in SYSTEM_NAMES if s != "SFH_SGP_reference"]
excluded_count = sum(1 for s in SYSTEM_NAMES if s != "SFH_SGP_reference"
                     and results[s]["label"] == "EXCLUDED")
peripheral_count = sum(1 for s in SYSTEM_NAMES if s != "SFH_SGP_reference"
                       and results[s]["label"] == "PERIPHERAL")
partial_count = sum(1 for s in SYSTEM_NAMES if s != "SFH_SGP_reference"
                    and results[s]["label"] == "PARTIAL_MEMBER")

# Correspondence gradient: correlation between membership score and Phase 411 rho
rhos = [SYSTEM_FEATURES[s]["phase411_rho"] for s in SYSTEM_NAMES]
scores = [results[s]["score"] for s in SYSTEM_NAMES]
from scipy.stats import pearsonr
corr_gradient, corr_p = pearsonr(scores, rhos)

# Mean deficiency count
mean_deficiency = np.mean([len(exclusion_classes[s]["deficiencies"])
                          for s in SYSTEM_NAMES if s != "SFH_SGP_reference"])

metrics = {
    "universality_membership_score": round(core_score, 4),
    "mean_non_core_membership": round(np.mean(non_core_scores), 4),
    "min_non_core_membership": round(min(non_core_scores), 4),
    "max_non_core_membership": round(max(non_core_scores), 4),
    "exclusion_density": round(1.0 - np.mean(non_core_scores), 4),
    "excluded_count": excluded_count,
    "peripheral_count": peripheral_count,
    "partial_count": partial_count,
    "correspondence_gradient": round(corr_gradient, 4),
    "correspondence_gradient_p": float(f"{corr_p:.4e}"),
    "mean_deficiency_count": round(mean_deficiency, 2),
    "num_attractor_families": len(family_map),
    "mean_stability_pct": round(np.mean([stability[s]["stability_pct"]
                                          for s in SYSTEM_NAMES]), 1),
}

print(f"\n{'='*60}")
print("COMPOSITE METRICS")
print(f"{'='*60}")
for k, v in metrics.items():
    print(f"  {k:40s}: {v}")

# ======= HYPOTHESES =======
h1_pass = excluded_count >= 2  # SFH-SGP requires specific constraints
h2_pass = len(set(tuple(sorted(exclusion_classes[s]["exclusion_tags"]))
                   for s in SYSTEM_NAMES if s != "SFH_SGP_reference")) >= 2
h3_pass = metrics["mean_stability_pct"] > 80.0  # boundaries are stable
h4_pass = partial_count >= 1  # partial correspondence regions exist
h5_pass = metrics["exclusion_density"] > 0.30  # bounded universality class

hypotheses = {
    "H1_SpecificConstraintsRequired": {
        "condition": ">= 2 non-core systems excluded",
        "value": excluded_count,
        "threshold": 2,
        "pass": h1_pass
    },
    "H2_ExclusionClassesIdentifiable": {
        "condition": ">= 2 distinct exclusion class types",
        "value": len(set(tuple(sorted(exclusion_classes[s]["exclusion_tags"]))
                         for s in SYSTEM_NAMES if s != "SFH_SGP_reference")),
        "threshold": 2,
        "pass": h2_pass
    },
    "H3_BoundariesReproducible": {
        "condition": "Classification stability > 80% under weight perturbation",
        "value": metrics["mean_stability_pct"],
        "threshold": 80.0,
        "pass": h3_pass
    },
    "H4_PartialCorrespondenceExists": {
        "condition": ">= 1 partial member system",
        "value": partial_count,
        "threshold": 1,
        "pass": h4_pass
    },
    "H5_BoundedUniversalityClass": {
        "condition": "exclusion_density > 0.30",
        "value": metrics["exclusion_density"],
        "threshold": 0.30,
        "pass": h5_pass
    }
}

passes = sum(1 for h in hypotheses.values() if h["pass"])
verdict_map_5 = {5: "UNIVERSALITY-CLASSIFICATION-STABLE",
                 4: "UNIVERSALITY-CLASSIFICATION-BOUNDED",
                 3: "UNIVERSALITY-CLASSIFICATION-BOUNDED",
                 2: "UNIVERSALITY-CLASSIFICATION-DEGRADING",
                 1: "UNIVERSALITY-CLASSIFICATION-FAILED",
                 0: "UNIVERSALITY-CLASSIFICATION-FAILED"}
verdict = verdict_map_5[passes]

print(f"\n{'='*60}")
print("HYPOTHESIS EVALUATION")
print(f"{'='*60}")
for h_name, h_data in hypotheses.items():
    s = "PASS" if h_data["pass"] else "FAIL"
    print(f"  {h_name}: {h_data['value']} vs {h_data['condition']} -> {s}")

print(f"\n{'='*60}")
print(f"PHASE 412 VERDICT: {verdict}")
print(f"Hypotheses: {passes}/5 PASS")
print(f"{'='*60}")

# ======= EXCLUSION CLASS DEFINITIONS =======
exclusion_class_defs = {
    "NO_OPERATORS": "System lacks formal operator algebra (P, A, N or analogs)",
    "NO_COMPOSITION": "System lacks operator/process composition",
    "NON_MONOTONIC": "System emergence does not decay monotonically with depth",
    "NO_HIERARCHY": "System does not produce a stable hierarchy across configurations",
    "NON_RELATIONAL": "System states are not relational configurations",
    "NON_SIMILARITY": "System emergence measure is not structural similarity",
}

print(f"\n{'='*60}")
print("EXCLUSION CLASS DEFINITIONS")
print(f"{'='*60}")
for tag, desc in exclusion_class_defs.items():
    affected = [s for s in SYSTEM_NAMES if s != "SFH_SGP_reference"
                and tag in exclusion_classes[s]["exclusion_tags"]]
    print(f"  {tag:25s}: {desc}")
    print(f"  {'':25s} Affected: {', '.join(affected) if affected else 'none'}")

# ======= SAVE =======
output = {
    "phase": 412,
    "seed": 412,
    "n_systems": len(SYSTEM_NAMES),
    "n_features": N_FEATURES,
    "feature_names": FEATURE_NAMES,
    "default_weights": DEFAULT_WEIGHTS,
    "system_features": {s: {k: v for k, v in SYSTEM_FEATURES[s].items()
                           if k != "phase411_rho"} for s in SYSTEM_NAMES},
    "membership_results": results,
    "attractor_families": {fid: family_map[fid] for fid in sorted(family_map)},
    "distance_matrix": {s1: {s2: round(distances[i][j], 3)
                             for j, s2 in enumerate(SYSTEM_NAMES)}
                        for i, s1 in enumerate(SYSTEM_NAMES)},
    "exclusion_classes": exclusion_classes,
    "exclusion_class_definitions": exclusion_class_defs,
    "boundary_stability": stability,
    "composite_metrics": metrics,
    "hypotheses": {k: {sk: sv for sk, sv in v.items() if sk != "condition"}
                   for k, v in hypotheses.items()},
    "pass_count": passes,
    "total_hypotheses": 5,
    "verdict": verdict
}

results_path = os.path.join(SCRIPT_DIR, "phase412_results.json")
with open(results_path, "w") as f:
    json.dump(output, f, indent=2, cls=NumpyEncoder)
print(f"\nResults saved: {results_path}")

# CSV: per-system membership
csv_path = os.path.join(SCRIPT_DIR, "phase412_membership.csv")
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    headers = ["system", "score", "label", "stability_pct"] + FEATURE_NAMES
    w.writerow(headers)
    for sys_name in SYSTEM_NAMES:
        row = [sys_name, results[sys_name]["score"], results[sys_name]["label"],
               stability[sys_name]["stability_pct"]]
        row += [SYSTEM_FEATURES[sys_name][f] for f in FEATURE_NAMES]
        w.writerow(row)
print(f"Membership CSV: {csv_path}")

# CSV: exclusion classes
csv2_path = os.path.join(SCRIPT_DIR, "phase412_exclusion_classes.csv")
with open(csv2_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["system", "exclusion_tags", "deficiency_count"])
    for sys_name in SYSTEM_NAMES:
        if sys_name == "SFH_SGP_reference":
            continue
        tags = ";".join(exclusion_classes[sys_name]["exclusion_tags"])
        w.writerow([sys_name, tags, exclusion_classes[sys_name]["deficiency_count"]])
print(f"Exclusion CSV: {csv2_path}")
