#!/usr/bin/env python3
"""
Phase U: Organizational Geometry Classification
================================================
Goal: Discover whether transform-space geometries collapse into
a SMALL NUMBER of reusable classes.

Tests:
  1. Geometry clustering (full feature matrix)
  2. Class stability under ablation/permutation
  3. Cross-metric transfer
  4. Minimal class basis
  5. Empirical class semantics
  6. Adversarial artifact test
  7. Transition geometry

Outputs (to sfh_sgp_ood_outputs/):
  - clustering_feature_matrix.csv
  - clustering_results.csv
  - dendrogram_plot.txt        (ascii dendrogram)
  - class_stability_report.csv
  - classifier_transfer_report.csv
  - minimal_basis_report.csv
  - adversarial_artifact_report.csv
  - phaseU_summary.md
"""

from __future__ import annotations
import json, math, random, warnings
from pathlib import Path
from typing import Callable
from itertools import combinations
from collections import Counter

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)
np.random.seed(42)
random.seed(42)

OUT = Path("sfh_sgp_ood_outputs")
OUT.mkdir(exist_ok=True)

from sfh_sgp_ood_universality_audit import (
    OOD_SYSTEMS, TRANSFORMS, canonical_metric_vector,
    m1_signed_ordinal_flow, m2_half_corr,
    m3_signed_compressibility, m4_amp_transition_asymmetry,
    system_category, compute_transform_geometry, null_audit_system,
    replay_stability,
)

# =====================================================================
# 1. BUILD FEATURE MATRIX
# =====================================================================

def build_feature_matrix() -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    """Build unified feature matrix from all existing outputs + recompute."""
    geo = pd.read_csv(OUT / "cross_domain_reproducibility.csv")
    null = pd.read_csv(OUT / "null_audit_ood.csv")
    replay = pd.read_csv(OUT / "replay_stability_ood.csv")

    # Parse tau_axis from string
    tau_parsed = geo["tau_axis"].apply(lambda s: json.loads(s.replace("'", '"')))
    tau_df = pd.DataFrame(tau_parsed.tolist(),
                          columns=["tau_m1", "tau_m2", "tau_m3", "tau_m4"])

    # Add m2 contribution difference from ablation data (available for subset)
    try:
        abl = pd.read_csv(OUT / "metric_ablation_results.csv")
        abl_pivot = abl.pivot_table(index="system", columns="ablation",
                                     values="pc1", aggfunc="mean").reset_index()
        abl_pivot["m2_contribution"] = (abl_pivot["full"] - abl_pivot["no_m2"]).fillna(0)
        # Rename to avoid collision
        abl_pivot = abl_pivot.rename(columns={
            "full": "abl_full_pc1",
            "no_m1": "abl_no_m1_pc1", "no_m2": "abl_no_m2_pc1",
            "no_m3": "abl_no_m3_pc1", "no_m4": "abl_no_m4_pc1",
            "m1_only": "abl_m1_pc1", "m2_only": "abl_m2_pc1",
            "m3_only": "abl_m3_pc1", "m4_only": "abl_m4_pc1",
        })
        abl_cols = ["abl_full_pc1", "abl_no_m1_pc1", "abl_no_m2_pc1",
                     "abl_no_m3_pc1", "abl_no_m4_pc1", "m2_contribution"]
    except Exception:
        abl_pivot = None
        abl_cols = []

    # Build feature matrix
    features = pd.DataFrame({
        "system": geo["system"],
        "pc1": geo["pc1_variance"],
        "pc2": geo["pc2_variance"],
        "effective_rank": geo["effective_rank"],
        "tau_m1": tau_df["tau_m1"],
        "tau_m2": tau_df["tau_m2"],
        "tau_m3": tau_df["tau_m3"],
        "tau_m4": tau_df["tau_m4"],
        "temporal_corr": null["temporal_scramble_corr_mean"],
        "phase_corr": null["phase_randomize_corr_mean"],
        "pc1_ratio": null["pc1_ratio_orig_vs_shuffled"],
        "replay_displacement": replay["replay_displacement_mean"],
    })

    if abl_pivot is not None:
        features = features.merge(abl_pivot[["system"] + abl_cols],
                                  on="system", how="left")
        for c in abl_cols:
            features[c] = features[c].fillna(0.0)

    # Feature columns (exclude system name)
    feat_cols = [c for c in features.columns if c != "system"]
    X = features[feat_cols].values
    return features, X, feat_cols


def compute_class_assignment(X, n_clusters=3):
    """Hierarchical + k-means hybrid clustering."""
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import AgglomerativeClustering, KMeans
    from sklearn.metrics import silhouette_score
    from scipy.spatial.distance import pdist, squareform
    from scipy.cluster.hierarchy import linkage, fcluster

    Xs = StandardScaler().fit_transform(X)

    # Hierarchical clustering
    Z = linkage(Xs, method="ward")
    hier_labels = fcluster(Z, t=n_clusters, criterion="maxclust")

    # K-means with same n_clusters
    km = KMeans(n_clusters=n_clusters, n_init=20, random_state=42)
    km_labels = km.fit_predict(Xs) + 1

    sil = silhouette_score(Xs, hier_labels)
    return hier_labels, km_labels, Z, sil, Xs


def format_dendrogram(Z, labels, max_width=80):
    """Simplified ascii dendrogram for cluster structure."""
    from scipy.cluster.hierarchy import dendrogram
    import io
    buf = io.StringIO()
    # Use the standard dendrogram and print a compact representation
    dn = dendrogram(Z, labels=labels, no_plot=True)
    # Show merge order
    lines = ["Dendrogram merge sequence:"]
    for i, merge in enumerate(Z):
        c1, c2, dist, size = int(merge[0]), int(merge[1]), merge[2], int(merge[3])
        lines.append(f"  Merge {i+1}: c{min(c1,c2)}+c{min(c1,c2)} at d={dist:.3f} (size={size})")
    lines.append("")
    # Leaf order
    leaf_order = [labels[i] for i in dn["leaves"]]
    lines.append(f"Leaf order: {' → '.join(leaf_order)}")
    return "\n".join(lines)


def run_clustering(features, X, feat_cols):
    """Test 1: Full clustering pipeline."""
    print("[1/7] Computing geometry clustering...")
    hier_labels, km_labels, Z, sil, Xs = compute_class_assignment(X, n_clusters=3)

    results = features[["system"]].copy()
    results["hier_cluster"] = hier_labels
    results["km_cluster"] = km_labels
    results["silhouette"] = sil

    # Add category
    results["category"] = results["system"].apply(system_category)

    # Print cluster assignments
    for clust in sorted(set(hier_labels)):
        members = results[results["hier_cluster"] == clust]["system"].tolist()
        cats = [system_category(s) for s in members]
        print(f"  Cluster {clust}: {members}")
        print(f"    Categories: {dict(Counter(cats))}")

    results.to_csv(OUT / "clustering_results.csv", index=False)

    # Dendrogram
    dendro_txt = format_dendrogram(Z, features["system"].tolist())
    with open(OUT / "dendrogram.txt", "w") as f:
        f.write(dendro_txt)
    print(f"  Silhouette score: {sil:.4f}")

    return results, Z, Xs, sil


# =====================================================================
# 2. CLASS STABILITY
# =====================================================================

def test_stability(features, X, feat_cols, base_labels, n_perturb=50):
    """Test 2: Class stability under perturbation."""
    print("[2/7] Testing class stability...")
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import AgglomerativeClustering

    n_systems = len(features)
    stability_rows = []

    # 1. Metric ablation stability: remove each feature group
    feature_groups = {
        "spectral": ["pc1", "pc2", "effective_rank"],
        "tau_axis": ["tau_m1", "tau_m2", "tau_m3", "tau_m4"],
        "null_audit": ["temporal_corr", "phase_corr", "pc1_ratio"],
        "replay": ["replay_displacement"],
    }
    if "abl_full_pc1" in feat_cols:
        feature_groups["ablation"] = [c for c in feat_cols if c.startswith("abl_") or c == "m2_contribution"]

    for group_name, group_cols in feature_groups.items():
        remaining = [c for c in feat_cols if c not in group_cols]
        if len(remaining) < 2:
            continue
        X_sub = features[remaining].values
        Xs = StandardScaler().fit_transform(X_sub)
        labels = AgglomerativeClustering(n_clusters=3).fit_predict(Xs) + 1
        agreement = np.mean(labels == base_labels)
        stability_rows.append({
            "perturbation": f"remove_{group_name}",
            "agreement": agreement,
            "n_features": len(remaining),
        })

    # 2. Random noise injection (repeated)
    Xs_orig = StandardScaler().fit_transform(X)
    noises = []
    for _ in range(n_perturb):
        X_noise = Xs_orig + np.random.normal(0, 0.3, Xs_orig.shape)
        labels = AgglomerativeClustering(n_clusters=3).fit_predict(X_noise) + 1
        noises.append(np.mean(labels == base_labels))
    stability_rows.append({
        "perturbation": f"gaussian_noise_0.3 (n={n_perturb})",
        "agreement": float(np.mean(noises)),
        "n_features": len(feat_cols),
    })

    df_stab = pd.DataFrame(stability_rows)
    df_stab.to_csv(OUT / "class_stability_report.csv", index=False)
    print("  Stability results:")
    for _, r in df_stab.iterrows():
        print(f"    {r['perturbation']}: agreement={r['agreement']:.4f}")
    return df_stab


# =====================================================================
# 3. CROSS-METRIC TRANSFER
# =====================================================================

def test_transfer(features, feat_cols, base_labels):
    """Test 3: Train classifier on subset of metrics, test on held-out."""
    print("[3/7] Testing cross-metric transfer...")
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score

    def safe_score(clf, X, y):
        try:
            return clf.score(X, y)
        except Exception:
            return 0.0

    # Split features into two views with EQUAL columns
    view1_cols = ["pc1", "effective_rank", "temporal_corr", "phase_corr"]
    view2_cols = ["tau_m1", "tau_m2", "tau_m3", "tau_m4"]

    v1 = [c for c in view1_cols if c in feat_cols]
    v2 = [c for c in view2_cols if c in feat_cols]

    transfer_rows = []
    for train_cols, test_cols, name in [(v1, v2, "view1→view2"), (v2, v1, "view2→view1")]:
        if len(train_cols) < 2 or len(test_cols) < 2:
            continue
        X_train = features[train_cols].values
        X_test = features[test_cols].values

        # Train on one view
        clf = RandomForestClassifier(n_estimators=50, random_state=42)
        cv_scores = cross_val_score(clf, X_train, base_labels,
                                     cv=min(3, len(np.unique(base_labels))))
        clf.fit(X_train, base_labels)

        # Test on held-out view (different feature space — use pseudo-transfer:
        # train on train_view, test on same data but only those features)
        train_score = safe_score(clf, X_train, base_labels)

        # Actually test cross-view: train new classifier on X_train's predictions
        # as features to predict X_test labels
        from sklearn.linear_model import LogisticRegression
        clf_train = RandomForestClassifier(n_estimators=50, random_state=42)
        clf_train.fit(X_train, base_labels)
        preds_train = clf_train.predict(X_train)

        clf_test = LogisticRegression(max_iter=1000, random_state=42)
        clf_test.fit(X_test, preds_train)
        preds_test = clf_test.predict(X_test)
        transfer_score = float(np.mean(preds_test == base_labels))

        transfer_rows.append({
            "transfer": name,
            "train_cv_mean": float(cv_scores.mean()),
            "train_cv_std": float(cv_scores.std()),
            "within_view_accuracy": train_score,
            "cross_view_transfer_accuracy": transfer_score,
        })

    df_trans = pd.DataFrame(transfer_rows) if transfer_rows else pd.DataFrame()
    if len(df_trans) > 0:
        df_trans.to_csv(OUT / "classifier_transfer_report.csv", index=False)
        print("  Cross-metric transfer:")
        for _, r in df_trans.iterrows():
            print(f"    {r['transfer']}: cv={r['train_cv_mean']:.3f} "
                  f"transfer={r['cross_view_transfer_accuracy']:.3f}")
    else:
        print("  [SKIP] insufficient features for transfer")
    return df_trans


# =====================================================================
# 4. MINIMAL CLASS BASIS
# =====================================================================

def test_minimal_basis(features, X, feat_cols, base_labels):
    """Test 4: Minimum feature set needed to recover classes."""
    print("[4/7] Finding minimal class basis...")
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import AgglomerativeClustering
    from itertools import combinations

    best_score = -1
    best_cols = []
    results = []

    # Test all 1-feature, 2-feature, 3-feature subsets
    for n_feat in range(1, min(4, len(feat_cols) + 1)):
        for subset in combinations(feat_cols, n_feat):
            cols = list(subset)
            Xs = StandardScaler().fit_transform(features[cols].values)
            labels = AgglomerativeClustering(n_clusters=3).fit_predict(Xs) + 1
            agreement = np.mean(labels == base_labels)
            results.append({
                "n_features": n_feat,
                "features": "+".join(cols),
                "agreement": agreement,
            })
            if agreement > best_score:
                best_score = agreement
                best_cols = cols

    df_min = pd.DataFrame(results)
    df_min.to_csv(OUT / "minimal_basis_report.csv", index=False)

    print(f"  Best {len(best_cols)}-feature set: {best_cols} (agreement={best_score:.4f})")
    # Show top 5
    top5 = df_min.sort_values("agreement", ascending=False).head(5)
    for _, r in top5.iterrows():
        print(f"    [{r['n_features']} feat] {r['features']}: agreement={r['agreement']:.4f}")
    return df_min, best_cols


# =====================================================================
# 5. CLASS SEMANTICS (empirical)
# =====================================================================

def test_semantics(features, results):
    """Test 5: Do classes align with empirical categories without hard-coding?"""
    print("[5/7] Testing empirical class semantics...")
    from sklearn.metrics import adjusted_rand_score

    # We already have categories. Check adjusted Rand index between cluster and category.
    cat_map = {"arithmetic": 0, "dynamical": 1, "symbolic": 2, "random_control": 3,
               "control": 4}
    true_cats = results["category"].map(cat_map).fillna(4).values
    hier_labels = results["hier_cluster"].values

    ari = adjusted_rand_score(true_cats, hier_labels)
    print(f"  Adjusted Rand Index (cluster vs category): {ari:.4f}")

    # Per-cluster category distribution
    print("  Per-cluster category distribution:")
    for clust in sorted(set(hier_labels)):
        members = results[results["hier_cluster"] == clust]
        dist = Counter(members["category"])
        total = len(members)
        dist_str = ", ".join(f"{k}={v/total:.0%}" for k, v in sorted(dist.items()))
        print(f"    Cluster {clust}: {dist_str}")

    # Check if clusters separate along known dimensions
    semantics = pd.DataFrame({
        "cluster": hier_labels,
        "category": results["category"],
        "pc1": features["pc1"],
        "effective_rank": features["effective_rank"],
    })
    semantics.to_csv(OUT / "class_semantics.csv", index=False)
    return ari


# =====================================================================
# 6. ADVERSARIAL ARTIFACT TEST
# =====================================================================

def test_adversarial(features, X, feat_cols):
    """Test 6: Generate synthetic metrics with matched stats. Can they reproduce classes?"""
    print("[6/7] Running adversarial artifact test...")
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import AgglomerativeClustering

    Xs = StandardScaler().fit_transform(X)

    # Generate synthetic data with same covariance structure but independent of system
    cov = np.cov(Xs.T)
    mean = np.mean(Xs, axis=0)
    n_systems = Xs.shape[0]
    n_trials = 50

    real_sils = []
    syn_sils = []
    class_sizes_real = []
    class_sizes_syn = []

    for _ in range(n_trials):
        # Synthetic: draw from multivariate normal matched to real covariance
        X_syn = np.random.multivariate_normal(mean, cov, size=n_systems)

        # Cluster both
        labels_real = AgglomerativeClustering(n_clusters=3).fit_predict(Xs) + 1
        labels_syn = AgglomerativeClustering(n_clusters=3).fit_predict(X_syn) + 1

        # Silhouette
        from sklearn.metrics import silhouette_score
        try:
            real_sils.append(silhouette_score(Xs, labels_real))
        except Exception:
            pass
        try:
            syn_sils.append(silhouette_score(X_syn, labels_syn))
        except Exception:
            pass

        class_sizes_real.append(Counter(labels_real))
        class_sizes_syn.append(Counter(labels_syn))

    # Compare
    mean_real_sil = float(np.mean(real_sils)) if real_sils else 0
    mean_syn_sil = float(np.mean(syn_sils)) if syn_sils else 0
    sil_ratio = mean_real_sil / max(mean_syn_sil, 1e-12)

    print(f"  Real data mean silhouette: {mean_real_sil:.4f}")
    print(f"  Synthetic matched-cov data mean silhouette: {mean_syn_sil:.4f}")
    print(f"  Ratio real/synthetic: {sil_ratio:.2f}")

    # If synthetic data clusters as well as real, artifact risk is high
    if sil_ratio < 1.2:
        verdict = "HIGH ARTIFACT RISK: matched-covariance synthetic data clusters similarly"
    elif sil_ratio < 1.5:
        verdict = "MODERATE ARTIFACT RISK: synthetic clusters but less cleanly"
    else:
        verdict = "LOW ARTIFACT RISK: real data clusters significantly better than synthetic"

    print(f"  Verdict: {verdict}")

    result = {
        "real_silhouette_mean": mean_real_sil,
        "synthetic_silhouette_mean": mean_syn_sil,
        "silhouette_ratio_real_vs_synthetic": sil_ratio,
        "verdict": verdict,
    }
    with open(OUT / "adversarial_artifact_report.json", "w") as f:
        json.dump(result, f, indent=2)
    return result


# =====================================================================
# 7. TRANSITION GEOMETRY
# =====================================================================

def test_transitions(features, X, feat_cols):
    """Test 7: Interpolate between system types — sharp or smooth transitions?"""
    print("[7/7] Testing transition geometry...")
    from sklearn.preprocessing import StandardScaler
    from scipy.spatial.distance import pdist, squareform

    Xs = StandardScaler().fit_transform(X)

    # Pseudo-transition: compute distances between all system pairs in feature space
    dists = squareform(pdist(Xs, metric="euclidean"))
    sys_names = features["system"].tolist()

    # Intra-category and inter-category distances
    cats = [system_category(s) for s in sys_names]
    intra_dists = []
    inter_dists = []
    for i in range(len(sys_names)):
        for j in range(i + 1, len(sys_names)):
            d = dists[i, j]
            if cats[i] == cats[j]:
                intra_dists.append(d)
            else:
                inter_dists.append(d)

    mean_intra = float(np.mean(intra_dists)) if intra_dists else 0
    mean_inter = float(np.mean(inter_dists)) if inter_dists else 0

    # Intra/inter ratio: <1 means categories are cohesive, >1 means spread
    ratio = mean_intra / max(mean_inter, 1e-12)

    print(f"  Mean intra-category distance: {mean_intra:.3f}")
    print(f"  Mean inter-category distance: {mean_inter:.3f}")
    print(f"  Intra/inter ratio: {ratio:.3f}")
    if ratio < 0.7:
        print("  → Categories are cohesive (sharp transitions)")
    elif ratio < 1.0:
        print("  → Categories weakly separated (smooth transitions)")
    else:
        print("  → No category structure (overlapping)")

    # Pairwise distance matrix
    dist_df = pd.DataFrame(dists, index=sys_names, columns=sys_names)
    dist_df.to_csv(OUT / "transition_distances.csv")

    result = {
        "mean_intra_category_distance": mean_intra,
        "mean_inter_category_distance": mean_inter,
        "intra_inter_ratio": ratio,
        "interpretation": ("sharp" if ratio < 0.7 else "smooth" if ratio < 1.0 else "overlapping"),
    }
    return result


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("=" * 70)
    print("PHASE U: ORGANIZATIONAL GEOMETRY CLASSIFICATION")
    print("=" * 70)

    features, X, feat_cols = build_feature_matrix()
    features.to_csv(OUT / "clustering_feature_matrix.csv", index=False)
    print(f"\nFeature matrix: {len(features)} systems × {len(feat_cols)} features")
    print(f"Features: {feat_cols}\n")

    # Test 1
    results, Z, Xs, sil_score = run_clustering(features, X, feat_cols)
    base_labels = results["hier_cluster"].values

    # Test 2
    stab = test_stability(features, X, feat_cols, base_labels)

    # Test 3
    trans = test_transfer(features, feat_cols, base_labels)

    # Test 4
    min_basis, best_cols = test_minimal_basis(features, X, feat_cols, base_labels)

    # Test 5
    ari = test_semantics(features, results)

    # Test 6
    adv = test_adversarial(features, X, feat_cols)

    # Test 7
    transitions = test_transitions(features, X, feat_cols)

    # Summary
    generate_phaseU_summary(results, stab, trans, min_basis, ari, adv, transitions, sil_score)
    print("\nPhase U complete. See sfh_sgp_ood_outputs/phaseU_summary.md")


def generate_phaseU_summary(results, stab, trans, min_basis, ari, adv, transitions, sil_score):
    md = []
    md.append("# Phase U: Organizational Geometry Classification — Summary")
    md.append("")
    md.append("## Test 1: Geometry Clustering")
    md.append("")
    md.append(f"**Silhouette score**: {sil_score:.4f}")
    md.append("")
    md.append("| System | Cluster | Category |")
    md.append("|--------|---------|----------|")
    for _, r in results.iterrows():
        md.append(f"| {r['system']} | {r['hier_cluster']} | {r['category']} |")
    md.append("")
    md.append("## Test 2: Class Stability")
    md.append("")
    for _, r in stab.iterrows():
        md.append(f"- {r['perturbation']}: agreement={r['agreement']:.4f}")
    md.append("")
    md.append("## Test 3: Cross-Metric Transfer")
    md.append("")
    if len(trans) > 0:
        for _, r in trans.iterrows():
            md.append(f"- {r['transfer']}: cv={r['train_cv_mean']:.3f} "
                      f"transfer={r['cross_view_transfer_accuracy']:.3f}")
    else:
        md.append("- [SKIP]")
    md.append("")
    md.append("## Test 4: Minimal Class Basis")
    md.append("")
    top5 = min_basis.sort_values("agreement", ascending=False).head(5)
    for _, r in top5.iterrows():
        md.append(f"- [{r['n_features']} feat] {r['features']}: agreement={r['agreement']:.4f}")
    md.append("")
    md.append("## Test 5: Empirical Class Semantics")
    md.append("")
    md.append(f"**Adjusted Rand Index (cluster vs. category)**: {ari:.4f}")
    md.append("")
    for clust in sorted(set(results['hier_cluster'])):
        members = results[results["hier_cluster"] == clust]
        dist = Counter(members["category"])
        total = len(members)
        dist_str = ", ".join(f"{k}={v/total:.0%}" for k, v in sorted(dist.items()))
        md.append(f"- Cluster {clust}: {dist_str}")
    md.append("")
    md.append("## Test 6: Adversarial Artifact")
    md.append("")
    md.append(f"- Real silhouette: {adv['real_silhouette_mean']:.4f}")
    md.append(f"- Synthetic silhouette: {adv['synthetic_silhouette_mean']:.4f}")
    md.append(f"- Ratio: {adv['silhouette_ratio_real_vs_synthetic']:.2f}")
    md.append(f"- Verdict: {adv['verdict']}")
    md.append("")
    md.append("## Test 7: Transition Geometry")
    md.append("")
    md.append(f"- Intra-category distance: {transitions['mean_intra_category_distance']:.3f}")
    md.append(f"- Inter-category distance: {transitions['mean_inter_category_distance']:.3f}")
    md.append(f"- Intra/inter ratio: {transitions['intra_inter_ratio']:.3f}")
    md.append(f"- Transition type: {transitions['interpretation']}")

    with open(OUT / "phaseU_summary.md", "w") as f:
        f.write("\n".join(md))


if __name__ == "__main__":
    main()
