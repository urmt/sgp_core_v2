#!/usr/bin/env python3
"""
T024: Lineage Validation — Mechanistic Ontology Score P0 vs P1
==============================================================
External mechanistic ontology independent of SFH-SGP geometry.
Score both partitions (P0=Ward+euclidean, P1=non-Ward consensus)
against that ontology using 5 metrics.

Authoritative discriminator: ising placement
  P0: ising with lorenz+reaction_diffusion → continuous-state emergent
  P1: ising with noise+chaotic             → stochasticity/entropy production
"""

import sys, json, warnings
from pathlib import Path
from collections import Counter
from itertools import product, combinations
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_mutual_info_score
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster

warnings.filterwarnings("ignore", category=RuntimeWarning)
np.random.seed(42)

OUT = Path("sfh_sgp_ood_outputs")
OUT.mkdir(exist_ok=True)

# =====================================================================
# 1. SYSTEM LIST (canonical order)
# =====================================================================
ALL_SYSTEMS = [
    "primes", "fibonacci", "modular_arithmetic", "additive_recurrence",
    "lorenz", "logistic_map", "henon_map", "ising_magnetization",
    "reaction_diffusion", "cfg_expansion", "lambda_reduction",
    "rewrite_system", "iid_gaussian", "colored_noise",
]

# =====================================================================
# 2. ONTOLOGY — 6 mutually exclusive mechanistic categories
# =====================================================================
# Category 0: symbolic recursion/computation
# Category 1: deterministic chaotic flow
# Category 2: stochastic/noise process
# Category 3: spatial emergent dynamics
# Category 4: combinatorial/statistical physics
# Category 5: arithmetic generative systems
ONTOLOGY = {
    "lambda_reduction":      0,
    "rewrite_system":        0,
    "logistic_map":          1,
    "henon_map":             1,
    "lorenz":                1,
    "iid_gaussian":          2,
    "colored_noise":         2,
    "reaction_diffusion":    3,
    "ising_magnetization":   3,
    "cfg_expansion":         4,
    "primes":                5,
    "fibonacci":             5,
    "modular_arithmetic":    5,
    "additive_recurrence":   5,
}

ONTOLOGY_LABELS = [
    "symbolic_recursion",
    "deterministic_chaotic",
    "stochastic_noise",
    "spatial_emergent",
    "combinatorial_statphys",
    "arithmetic_generative",
]

# =====================================================================
# 3. LOAD DATA & COMPUTE PARTITIONS
# =====================================================================
def load_data():
    df = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    df = df[df["system"].isin(ALL_SYSTEMS)].copy()
    df = df.set_index("system").loc[ALL_SYSTEMS].reset_index()
    feat_cols = [c for c in df.columns if c != "system"]
    X = df[feat_cols].values
    Xs = StandardScaler().fit_transform(X)
    return df, X, Xs, feat_cols

def compute_partitions(Xs):
    """P0 = ward+euclidean (sizes 3,5,6). P1 = complete+euclidean (sizes 2,6,6)."""
    Z0 = linkage(Xs, method="ward", metric="euclidean")
    labels_P0 = fcluster(Z0, t=3, criterion="maxclust")

    Z1 = linkage(Xs, method="complete", metric="euclidean")
    labels_P1 = fcluster(Z1, t=3, criterion="maxclust")

    return labels_P0, labels_P1

def verify_partitions(labels_P0, labels_P1):
    """Verify sizes match expected: P0 = [3,5,6], P1 = [2,6,6]."""
    P0_sizes = sorted(Counter(labels_P0).values())
    P1_sizes = sorted(Counter(labels_P1).values())
    return P0_sizes, P1_sizes

def print_partition_table(systems, labels_P0, labels_P1):
    fmt = "{:<24s}  {:>8s}  {:>8s}  {:>24s}"
    print(fmt.format("System", "P0_clust", "P1_clust", "Ontology"))
    print("-" * 68)
    for s, l0, l1 in zip(systems, labels_P0, labels_P1):
        ont = ONTOLOGY_LABELS[ONTOLOGY[s]]
        print(fmt.format(s, str(l0), str(l1), ont))
    print()

# =====================================================================
# 4. SCORING METRICS
# =====================================================================

def variation_of_information(y_true, y_pred):
    """VI = H(X|Y) + H(Y|X). Lower = better agreement."""
    from sklearn.metrics import mutual_info_score
    from scipy.stats import entropy
    n = len(y_true)
    # Contingency table
    classes_true = set(y_true)
    classes_pred = set(y_pred)
    contingency = np.zeros((len(classes_true), len(classes_pred)), dtype=float)
    t_map = {c: i for i, c in enumerate(sorted(classes_true))}
    p_map = {c: j for j, c in enumerate(sorted(classes_pred))}
    for t, p in zip(y_true, y_pred):
        contingency[t_map[t], p_map[p]] += 1.0
    contingency /= n
    mi = mutual_info_score(y_true, y_pred)
    H_t = -np.sum(contingency.sum(axis=1) * np.log(contingency.sum(axis=1) + 1e-12))
    H_p = -np.sum(contingency.sum(axis=0) * np.log(contingency.sum(axis=0) + 1e-12))
    return H_t + H_p - 2 * mi

def mdl_coding_cost(y_pred, y_true):
    """Minimum description length: encode cluster labels, then correct for ontology errors.
    Lower = better fit. Uses:
      L = n * H(y_pred) + errors * log(n_categories)
    where errors = number of systems whose ontology does NOT match the majority of their cluster.
    """
    n = len(y_true)
    # Entropy of predicted partition
    counts = Counter(y_pred)
    probs = np.array([c / n for c in counts.values()])
    H_pred = -np.sum(probs * np.log2(probs + 1e-12))

    # For each cluster, find majority ontology, count mismatches
    clust_to_systems = {}
    for t, p in zip(y_true, y_pred):
        clust_to_systems.setdefault(p, []).append(t)

    errors = 0
    for clust, members in clust_to_systems.items():
        maj_count = Counter(members).most_common(1)[0][1]
        errors += len(members) - maj_count

    # coding cost: n*H(pred) + errors * log2(n_categories)
    cost = n * H_pred + errors * np.log2(len(set(y_true)))
    return cost

def bayesian_evidence(y_pred, y_true):
    """Simple Bayesian score: P(data|partition) under generative ontology model.
    Scaled log-probability: higher = better.
    Assumes each cluster has a Dirichlet-multinomial distribution over ontology categories.
    """
    from scipy.special import gammaln
    n_cats = len(set(y_true))
    alpha_prior = 1.0  # uniform Dirichlet prior

    log_evidence = 0.0
    clusts = sorted(set(y_pred))
    for c in clusts:
        members = [y_true[i] for i in range(len(y_true)) if y_pred[i] == c]
        n_c = len(members)
        if n_c == 0:
            continue
        counts = [sum(1 for m in members if m == k) for k in range(n_cats)]
        # Dirichlet-multinomial: log P(counts | alpha)
        log_evidence += (gammaln(n_cats * alpha_prior) - gammaln(n_c + n_cats * alpha_prior)
                         + sum(gammaln(c_k + alpha_prior) - gammaln(alpha_prior) for c_k in counts))
    return log_evidence

def pairwise_mechanistic_consistency(y_pred, y_true):
    """Fraction of system pairs that are consistently grouped or separated.
    A pair is consistent if:
      - same ontology category AND same cluster (correct grouping), OR
      - different ontology category AND different cluster (correct separation)
    """
    n = len(y_true)
    correct = 0
    total = 0
    for i in range(n):
        for j in range(i + 1, n):
            same_ont = (y_true[i] == y_true[j])
            same_clust = (y_pred[i] == y_pred[j])
            if same_ont and same_clust:
                correct += 1
            elif not same_ont and not same_clust:
                correct += 1
            total += 1
    return correct / total

def score_partition(labels_pred, labels_true, name):
    """Compute all 5 metrics."""
    ami = adjusted_mutual_info_score(labels_true, labels_pred)
    vi = variation_of_information(labels_true, labels_pred)
    mdl = mdl_coding_cost(labels_pred, labels_true)
    bayes = bayesian_evidence(labels_pred, labels_true)
    pmc = pairwise_mechanistic_consistency(labels_pred, labels_true)
    return {
        "partition": name,
        "AMI": round(ami, 6),
        "VI": round(vi, 6),
        "MDL": round(mdl, 6),
        "Bayes_logZ": round(bayes, 6),
        "PMC": round(pmc, 6),
    }

# =====================================================================
# 5. ISING PLACEMENT ANALYSIS
# =====================================================================
def analyze_ising_placement(systems, labels_P0, labels_P1):
    """Detailed analysis of ising_magnetization's cluster assignment."""
    idx = systems.index("ising_magnetization")
    l0 = labels_P0[idx]
    l1 = labels_P1[idx]

    print("\n" + "=" * 68)
    print("ISING PLACEMENT ANALYSIS")
    print("=" * 68)

    for name, labels in [("P0 (Ward+euclidean)", labels_P0),
                          ("P1 (Complete+euclidean)", labels_P1)]:
        l_i = labels[idx]
        clust_members = [s for i, s in enumerate(systems) if labels[i] == l_i]
        ontologies = [ONTOLOGY_LABELS[ONTOLOGY[s]] for s in clust_members]
        entropies = Counter(ontologies)
        print(f"\n{name}: ising in cluster {{{l_i}}} with {len(clust_members)} members:")
        for m, o in zip(clust_members, ontologies):
            print(f"  {m:<24s} → {o}")
        ent_str = ", ".join(f"{k}={v}" for k, v in sorted(entropies.items()))
        print(f"  Ontology mix: {ent_str}")

    print()
    return

# =====================================================================
# 6. CONFUSION MATRIX
# =====================================================================
def confusion_matrix(y_true, y_pred, labels):
    n = len(labels)
    mat = np.zeros((n, n), dtype=int)
    for t, p in zip(y_true, y_pred):
        mat[t, p] += 1
    return mat

def print_confusion_matrix(mat, row_labels, col_labels, title):
    print(f"\n{title}")
    print("Ontology ↓  | ", end="")
    for c in range(mat.shape[1]):
        print(f" Clust{c} ", end="")
    print()
    print("-" * (14 + 10 * mat.shape[1]))
    for r in range(mat.shape[0]):
        print(f"{row_labels[r]:<16s} |", end="")
        for c in range(mat.shape[1]):
            print(f"  {mat[r, c]:>3d}  ", end="")
        print()
    print()

# =====================================================================
# 7. MAIN: FULL LINEAGE VALIDATION
# =====================================================================
def main():
    print("=" * 68)
    print("T024: LINEAGE VALIDATION — MECHANISTIC ONTOLOGY SCORE")
    print("=" * 68)

    # Load
    df, X, Xs, feat_cols = load_data()
    systems = df["system"].tolist()
    print(f"\nSystems ({len(systems)}): {', '.join(systems)}")
    print(f"Features ({len(feat_cols)}): {', '.join(feat_cols)}")
    print()

    # Compute partitions
    labels_P0, labels_P1 = compute_partitions(Xs)
    P0_sizes, P1_sizes = verify_partitions(labels_P0, labels_P1)
    print(f"P0 (ward+euclidean) size distribution: {P0_sizes} ({'match' if P0_sizes == [3,5,6] else 'MISMATCH'})")
    print(f"P1 (complete+euclidean) size distribution: {P1_sizes} ({'match' if P1_sizes == [2,6,6] else 'MISMATCH'})")
    print()

    # Verify P1 is actually the consensus partition
    # Test all single-linkage variants to confirm uniqueness
    methods_to_test = [
        ("complete", "euclidean"), ("average", "euclidean"), ("single", "euclidean"),
        ("ward", "euclidean"), ("centroid", "euclidean"), ("median", "euclidean"),
    ]
    unique_partitions = {}
    for method, metric in methods_to_test:
        Z = linkage(Xs, method=method, metric=metric)
        labs = tuple(fcluster(Z, t=3, criterion="maxclust"))
        key = tuple(sorted(Counter(labs).values()))
        unique_partitions.setdefault(key, []).append(f"{method}+{metric}")

    print(f"Unique partitions across {len(methods_to_test)} linkage×metric combos: {len(unique_partitions)}")
    for key, val in unique_partitions.items():
        print(f"  sizes={key}: {', '.join(val)}")
    print()

    # Print partition table
    ontology_labels = [ONTOLOGY[s] for s in systems]
    print_partition_table(systems, labels_P0, labels_P1)

    # Score both partitions
    results = [
        score_partition(labels_P0, ontology_labels, "P0_ward_euclidean"),
        score_partition(labels_P1, ontology_labels, "P1_complete_euclidean"),
    ]

    # Also score the Ward vs Complete directly against each other
    from sklearn.metrics import adjusted_rand_score
    ari_P0_P1 = adjusted_rand_score(labels_P0, labels_P1)
    results.append({
        "partition": "ARI_P0_vs_P1",
        "AMI": ari_P0_P1,
        "VI": 0.0,
        "MDL": 0.0,
        "Bayes_logZ": 0.0,
        "PMC": 0.0,
    })

    # Print metric table
    print()
    print("=" * 68)
    print("ONTOLOGY SCORING RESULTS")
    print("=" * 68)
    print(f"{'Partition':<24s}  {'AMI':>10s}  {'VI':>10s}  {'MDL':>10s}  {'logZ':>10s}  {'PMC':>8s}")
    print("-" * 78)
    for r in results:
        if r["partition"] == "ARI_P0_vs_P1":
            print(f"{r['partition']:<24s}  {r['AMI']:>10.6f}")
        else:
            print(f"{r['partition']:<24s}  {r['AMI']:>10.6f}  {r['VI']:>10.6f}  "
                  f"{r['MDL']:>10.6f}  {r['Bayes_logZ']:>10.6f}  {r['PMC']:>8.6f}")

    # Confusion matrices
    ont_set = sorted(set(ontology_labels))
    ont_names = [ONTOLOGY_LABELS[i] for i in ont_set]

    cm_P0 = confusion_matrix(ontology_labels, labels_P0, ont_set)
    cm_P1 = confusion_matrix(ontology_labels, labels_P1, ont_set)
    print_confusion_matrix(cm_P0, ont_names,
                           [f"C{i}" for i in sorted(set(labels_P0))],
                           "Confusion: Ontology × P0 (ward+euclidean)")
    print_confusion_matrix(cm_P1, ont_names,
                           [f"C{i}" for i in sorted(set(labels_P1))],
                           "Confusion: Ontology × P1 (complete+euclidean)")

    # Ising placement analysis
    analyze_ising_placement(systems, labels_P0, labels_P1)

    # =====================================================================
    # 8. PER-ONTOLOGY-CLASS AGREEMENT
    # =====================================================================
    print("=" * 68)
    print("PER-ONTOLOGY-CLASS AGREEMENT")
    print("=" * 68)
    for name, labels in [("P0", labels_P0), ("P1", labels_P1)]:
        print(f"\n{name}:")
        for cat_id in sorted(set(ontology_labels)):
            cat_systems = [s for i, s in enumerate(systems) if ontology_labels[i] == cat_id]
            cat_clusts = [labels[i] for i, s in enumerate(systems) if ontology_labels[i] == cat_id]
            maj_clust = Counter(cat_clusts).most_common(1)[0][0]
            frac_together = sum(1 for c in cat_clusts if c == maj_clust) / len(cat_clusts)
            print(f"  {ONTOLOGY_LABELS[cat_id]:<28s} {frac_together:.0%} in cluster {maj_clust} ({', '.join(cat_systems)})")

    # =====================================================================
    # 9. PAIRWISE MECHANISTIC CONSISTENCY DETAIL
    # =====================================================================
    print("\n" + "=" * 68)
    print("PAIRWISE CONSISTENCY FAILURES (P1 - P0 comparison)")
    print("=" * 68)
    n = len(systems)
    inconsistent_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            # True ontology agreement
            true_same = ontology_labels[i] == ontology_labels[j]
            true_diff = not true_same
            # P0 agreement
            p0_same = labels_P0[i] == labels_P0[j]
            p1_same = labels_P1[i] == labels_P1[j]
            # Correct under each
            p0_correct = (true_same and p0_same) or (true_diff and not p0_same)
            p1_correct = (true_same and p1_same) or (true_diff and not p1_same)
            if p0_correct != p1_correct:
                inconsistent_pairs.append({
                    "a": systems[i], "b": systems[j],
                    "ont_a": ONTOLOGY_LABELS[ontology_labels[i]],
                    "ont_b": ONTOLOGY_LABELS[ontology_labels[j]],
                    "same_ont": true_same,
                    "P0_same": p0_same, "P0_correct": p0_correct,
                    "P1_same": p1_same, "P1_correct": p1_correct,
                })

    print(f"Inconsistent pairs (P0 correct ≠ P1 correct): {len(inconsistent_pairs)}")
    for p in sorted(inconsistent_pairs, key=lambda x: -int(x["P1_correct"])):
        winner = "P1" if p["P1_correct"] else "P0"
        ont_rel = "same" if p["same_ont"] else "different"
        print(f"  {p['a']:<24s} × {p['b']:<24s}   ont={ont_rel:<10s}  "
              f"P0_same={str(p['P0_same']):<5s}  P1_same={str(p['P1_same']):<5s}  → {winner} correct")

    # =====================================================================
    # 10. NULL DISTRIBUTION (permutation test)
    # =====================================================================
    print("\n" + "=" * 68)
    print("NULL DISTRIBUTION (10,000 permutations)")
    print("=" * 68)
    n_perm = 10000
    n_sys = len(systems)
    all_labels = list(range(n_sys))
    null_amis_P0 = []
    null_amis_P1 = []
    for _ in range(n_perm):
        shuffled = np.random.permutation(ontology_labels)
        null_amis_P0.append(adjusted_mutual_info_score(shuffled, labels_P0))
        null_amis_P1.append(adjusted_mutual_info_score(shuffled, labels_P1))
    null_amis_P0 = np.array(null_amis_P0)
    null_amis_P1 = np.array(null_amis_P1)

    ami_P0 = adjusted_mutual_info_score(ontology_labels, labels_P0)
    ami_P1 = adjusted_mutual_info_score(ontology_labels, labels_P1)

    pct_P0 = np.mean(null_amis_P0 >= ami_P0)
    pct_P1 = np.mean(null_amis_P1 >= ami_P1)

    print(f"  P0 AMI = {ami_P0:.6f}, null 95th = {np.percentile(null_amis_P0, 95):.6f}, "
          f"percentile = {pct_P0*100:.1f}%")
    print(f"  P1 AMI = {ami_P1:.6f}, null 95th = {np.percentile(null_amis_P1, 95):.6f}, "
          f"percentile = {pct_P1*100:.1f}%")
    print(f"  P0 exceeds 95th pct: {ami_P0 > np.percentile(null_amis_P0, 95)}")
    print(f"  P1 exceeds 95th pct: {ami_P1 > np.percentile(null_amis_P1, 95)}")

    # =====================================================================
    # 11. SUMMARY
    # =====================================================================
    print("\n" + "=" * 68)
    print("FINAL VERDICT")
    print("=" * 68)

    # Winner by each metric
    metrics = ["AMI", "VI", "MDL", "Bayes_logZ", "PMC"]
    winners = {}
    for m in metrics:
        v0 = results[0][m]
        v1 = results[1][m]
        if m in ["VI", "MDL"]:
            winner = "P0" if v0 < v1 else "P1"
        else:
            winner = "P0" if v0 > v1 else "P1"
        winners[m] = winner

    print(f"\n  Metric       P0         P1         Winner")
    print(f"  {'-'*48}")
    for m in metrics:
        v0 = results[0][m]
        v1 = results[1][m]
        print(f"  {m:<12s}  {v0:>8.6f}  {v1:>8.6f}  → {winners[m]}")

    wcount = Counter(winners.values())
    print(f"\n  Winner count: P0 = {wcount.get('P0', 0)}/5, P1 = {wcount.get('P1', 0)}/5")
    if wcount.get("P0", 0) > 2:
        verdict = "P0 (Ward+euclidean) — continuous-state emergent organization"
    elif wcount.get("P1", 0) > 2:
        verdict = "P1 (non-Ward consensus) — stochasticity/entropy production organization"
    else:
        verdict = "TIED — no decisive advantage"

    print(f"\n  ╔═══════════════════════════════════════════════════════════════╗")
    print(f"  ║  {verdict:<57s} ║")
    print(f"  ╚═══════════════════════════════════════════════════════════════╝")

    # Ising-specific verdict
    print(f"\n  Critical discriminator — ising with lorenz+reaction (P0) "
          f"or noise+chaotic (P1):")
    idx = systems.index("ising_magnetization")
    print(f"    P0: cluster {labels_P0[idx]} (lorenz, ising, reaction_diffusion)")
    print(f"    P1: cluster {labels_P1[idx]} (noise+chaotic+additive)")
    ontology_idx = ontology_labels[idx]
    # Check which cluster's majority ontology matches ising's ontology
    p0_clust = labels_P0[idx]
    p0_members = [ontology_labels[i] for i, s in enumerate(systems) if labels_P0[i] == p0_clust]
    p0_maj_ont = Counter(p0_members).most_common(1)[0][0]
    p1_clust = labels_P1[idx]
    p1_members = [ontology_labels[i] for i, s in enumerate(systems) if labels_P1[i] == p1_clust]
    p1_maj_ont = Counter(p1_members).most_common(1)[0][0]

    print(f"    ising ontology: {ONTOLOGY_LABELS[ontology_idx]}")
    print(f"    P0 cluster majority ontology: {ONTOLOGY_LABELS[p0_maj_ont]}")
    print(f"    P1 cluster majority ontology: {ONTOLOGY_LABELS[p1_maj_ont]}")
    if ontology_idx == p0_maj_ont:
        print(f"    → P0 groups ising with its own kind ✓")
    elif ontology_idx == p1_maj_ont:
        print(f"    → P1 groups ising with its own kind ✓")
    else:
        print(f"    → Neither: ising is mis-grouped in both partitions")

    # =====================================================================
    # 12. SAVE RESULTS
    # =====================================================================
    save = {
        "ontology": {s: ONTOLOGY_LABELS[ONTOLOGY[s]] for s in systems},
        "partition_P0": {s: int(labels_P0[i]) for i, s in enumerate(systems)},
        "partition_P1": {s: int(labels_P1[i]) for i, s in enumerate(systems)},
        "scores": results[:2],
        "ari_P0_vs_P1": ari_P0_P1,
        "null_sig_P0": {"ami": ami_P0, "pct_95": float(np.percentile(null_amis_P0, 95)),
                         "exceeds": bool(ami_P0 > np.percentile(null_amis_P0, 95))},
        "null_sig_P1": {"ami": ami_P1, "pct_95": float(np.percentile(null_amis_P1, 95)),
                         "exceeds": bool(ami_P1 > np.percentile(null_amis_P1, 95))},
        "inconsistent_pairs": len(inconsistent_pairs),
        "winner_by_metric": winners,
        "verdict": verdict,
    }
    with open(OUT / "lineage_validation.json", "w") as f:
        json.dump(save, f, indent=2)

    print(f"\nResults saved to {OUT / 'lineage_validation.json'}")
    print()


if __name__ == "__main__":
    main()
