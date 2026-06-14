#!/usr/bin/env python3
"""
T036: Family Boundary Geometry
===============================
Investigate WHY transfer fails by mapping family boundaries
and overlap structure in Φ-space.

Uses existing T031 outputs only.
"""

import sys, json, warnings, time
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from scipy.spatial.distance import pdist, squareform, mahalanobis
from scipy.stats import pearsonr, spearmanr, entropy
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import NearestNeighbors, KNeighborsClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
from sklearn.manifold import TSNE
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
np.random.seed(42)

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    f = pd.read_csv(OUT / "t030_ensemble_features.csv")
    Phi = np.load(OUT / "t030_ensemble_Phi.npy")
    families = np.array([s.split("_")[0] for s in f["system"].values])
    unique_fams = sorted(np.unique(families))
    fam_idx = np.array([np.searchsorted(unique_fams, fi) for fi in families])
    X_raw = f.select_dtypes(include=[float, int]).values[:, :17]
    systems = f["system"].values
    return Phi, X_raw, families, unique_fams, fam_idx, systems


# ============================================================
# TASK 1: FAMILY SEPARATION MATRIX
# ============================================================

def task1_separation_matrix(Phi, families, unique_fams):
    """Compute 4 distance metrics between every family pair."""
    n_fams = len(unique_fams)
    centroids = {}
    covs = {}
    fam_data = {}

    for fi, fam in enumerate(unique_fams):
        mask = families == fam
        fam_data[fi] = Phi[mask]
        centroids[fi] = Phi[mask].mean(axis=0)
        covs[fi] = np.cov(Phi[mask], rowvar=False) + 1e-8 * np.eye(Phi.shape[1])

    centroid_dist = np.zeros((n_fams, n_fams))
    mahal_dist = np.zeros((n_fams, n_fams))
    wasserstein_dist = np.zeros((n_fams, n_fams))
    bhattacharyya_dist = np.zeros((n_fams, n_fams))

    for i in range(n_fams):
        for j in range(n_fams):
            if i == j:
                continue
            # Centroid distance
            centroid_dist[i, j] = np.linalg.norm(centroids[i] - centroids[j])

            # Mahalanobis distance (average of both directions)
            try:
                m1 = mahalanobis(centroids[i], centroids[j], np.linalg.inv(covs[j]))
                m2 = mahalanobis(centroids[j], centroids[i], np.linalg.inv(covs[i]))
                mahal_dist[i, j] = (m1 + m2) / 2
            except Exception:
                mahal_dist[i, j] = centroid_dist[i, j]

            # Wasserstein distance (mean of per-dimension)
            try:
                from scipy.stats import wasserstein_distance
                wds = [wasserstein_distance(fam_data[i][:, d], fam_data[j][:, d])
                       for d in range(Phi.shape[1])]
                wasserstein_dist[i, j] = np.mean(wds)
            except Exception:
                wasserstein_dist[i, j] = centroid_dist[i, j]

            # Bhattacharyya distance
            try:
                mean_diff = centroids[i] - centroids[j]
                avg_cov = (covs[i] + covs[j]) / 2
                inv_avg = np.linalg.inv(avg_cov)
                bc = 0.125 * mean_diff @ inv_avg @ mean_diff + 0.5 * np.log(
                    np.linalg.det(avg_cov) / (np.sqrt(np.linalg.det(covs[i]) * np.linalg.det(covs[j]) + 1e-12) + 1e-12))
                bhattacharyya_dist[i, j] = max(0, bc)
            except Exception:
                bhattacharyya_dist[i, j] = centroid_dist[i, j]

    # Save
    rows = []
    for i, fi in enumerate(unique_fams):
        for j, fj in enumerate(unique_fams):
            rows.append({
                "family_A": fi, "family_B": fj,
                "centroid_distance": centroid_dist[i, j],
                "mahalanobis_distance": mahal_dist[i, j],
                "wasserstein_distance": wasserstein_dist[i, j],
                "bhattacharyya_distance": bhattacharyya_dist[i, j],
            })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "t036_family_distance_matrix.csv", index=False)
    print(f"  Saved t036_family_distance_matrix.csv")

    return centroid_dist, mahal_dist, unique_fams


# ============================================================
# TASK 2: FAMILY CONFUSION CLASSIFIER
# ============================================================

def task2_family_confusion(Phi, families, unique_fams):
    """Train Φ-space -> family classifier with stratified CV."""
    le = LabelEncoder()
    y = le.fit_transform(families)

    scaler = StandardScaler()
    Xs = scaler.fit_transform(Phi)

    # Stratified 5-fold CV
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)

    y_pred = cross_val_predict(model, Xs, y, cv=cv)

    acc = accuracy_score(y, y_pred)
    bal_acc = balanced_accuracy_score(y, y_pred)
    cm = confusion_matrix(y, y_pred)

    print(f"  Accuracy: {acc:.4f}")
    print(f"  Balanced accuracy: {bal_acc:.4f}")

    # Save confusion matrix
    cm_df = pd.DataFrame(cm, index=unique_fams, columns=unique_fams)
    cm_df.to_csv(OUT / "t036_confusion_matrix.csv")

    # Figure
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(cm, aspect="auto", cmap="Blues")
    ax.set_xticks(range(len(unique_fams)))
    ax.set_xticklabels(unique_fams, fontsize=6, rotation=45, ha="right")
    ax.set_yticks(range(len(unique_fams)))
    ax.set_yticklabels(unique_fams, fontsize=6)
    plt.colorbar(im, ax=ax, label="Count")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(f"Family confusion matrix (acc={acc:.3f}, bal_acc={bal_acc:.3f})")

    for i in range(len(unique_fams)):
        for j in range(len(unique_fams)):
            color = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=5, color=color)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t036_family_confusion.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t036_family_confusion.pdf/.png")

    # Find most confused pairs
    confused = []
    for i, fi in enumerate(unique_fams):
        for j, fj in enumerate(unique_fams):
            if i != j and cm[i, j] > 0:
                confused.append((fi, fj, int(cm[i, j])))
    confused.sort(key=lambda x: x[2], reverse=True)

    return acc, bal_acc, confused


# ============================================================
# TASK 3: BOUNDARY SYSTEMS
# ============================================================

def task3_boundary_systems(Phi, families, unique_fams, systems):
    """Identify boundary systems with overlap score < 1.25."""
    centroids = {}
    for fi, fam in enumerate(unique_fams):
        mask = families == fam
        centroids[fi] = Phi[mask].mean(axis=0)

    rows = []
    for i in range(len(Phi)):
        fam = families[i]
        fi = np.searchsorted(unique_fams, fam)
        own_dist = np.linalg.norm(Phi[i] - centroids[fi])

        min_foreign_dist = np.inf
        nearest_foreign = ""
        for fj, fjam in enumerate(unique_fams):
            if fj == fi:
                continue
            d = np.linalg.norm(Phi[i] - centroids[fj])
            if d < min_foreign_dist:
                min_foreign_dist = d
                nearest_foreign = fjam

        overlap_score = min_foreign_dist / max(own_dist, 1e-12)

        rows.append({
            "system_id": i,
            "system": systems[i],
            "family": fam,
            "nearest_foreign_family": nearest_foreign,
            "overlap_score": float(overlap_score),
            "own_distance": float(own_dist),
            "foreign_distance": float(min_foreign_dist),
            "C": float(Phi[i, 0]),
            "F": float(Phi[i, 1]),
            "A": float(Phi[i, 2]),
            "R": float(Phi[i, 3]),
        })

    df = pd.DataFrame(rows)
    boundary = df[df["overlap_score"] < 1.25].copy()
    boundary.to_csv(OUT / "t036_boundary_systems.csv", index=False)
    df.to_csv(OUT / "t036_all_systems_overlap.csv", index=False)

    print(f"  Boundary systems (overlap<1.25): {len(boundary)}/{len(df)}")
    print(f"  By family:")
    for fam, cnt in boundary["family"].value_counts().items():
        print(f"    {fam}: {cnt}")

    return df, boundary


# ============================================================
# TASK 4: kNN PURITY
# ============================================================

def task4_purity(Phi, families, unique_fams):
    """Compute kNN family purity distribution."""
    k = 10
    nn = NearestNeighbors(n_neighbors=k + 1)
    nn.fit(Phi)
    _, indices = nn.kneighbors(Phi)

    purities = []
    for i in range(len(Phi)):
        neighbors = indices[i, 1:]  # exclude self
        neighbor_fams = families[neighbors]
        own_fam = families[i]
        purity = np.mean(neighbor_fams == own_fam)
        purities.append(purity)

    purities = np.array(purities)
    print(f"  Mean purity: {purities.mean():.4f}")
    print(f"  Median purity: {np.median(purities):.4f}")
    print(f"  Purity < 0.5: {(purities < 0.5).sum()}/{len(purities)}")

    # Figure
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(purities, bins=20, color="#555555", edgecolor="white", linewidth=0.3, alpha=0.85)
    ax.axvline(np.mean(purities), color="black", ls="--", lw=0.8, label=f"Mean={np.mean(purities):.3f}")
    ax.axvline(0.5, color="red", ls=":", lw=0.6, label="Purity=0.5 (random)")
    ax.set_xlabel(f"kNN family purity (k={k})")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of family purity in Φ-space")
    ax.legend(frameon=False)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t036_purity_distribution.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t036_purity_distribution.pdf/.png")

    return purities


# ============================================================
# TASK 5: TRANSFER BARRIERS
# ============================================================

def task5_transfer_barriers(Phi, families, unique_fams, centroid_dist, purities):
    """Correlate transfer failure with geometric barriers."""
    # Load T034 results
    t034 = pd.read_csv(OUT / "t034_family_breakdown.csv")

    rows = []
    for _, row in t034.iterrows():
        fam = row["family"]
        target = row["target"]
        fam_r2 = row["r2"]

        # Family distance to all others
        fi = np.searchsorted(unique_fams, fam)
        mean_dist = np.mean([centroid_dist[fi, fj] for fj in range(len(unique_fams)) if fj != fi])
        min_dist = np.min([centroid_dist[fi, fj] for fj in range(len(unique_fams)) if fj != fi])

        # Mean purity for this family
        fam_mask = families == fam
        fam_purity = np.mean(purities[fam_mask]) if fam_mask.sum() > 0 else 0

        rows.append({
            "family": fam,
            "target": target,
            "transfer_r2": fam_r2,
            "mean_centroid_distance": float(mean_dist),
            "min_centroid_distance": float(min_dist),
            "mean_purity": float(fam_purity),
        })

    df = pd.DataFrame(rows)

    # Correlations
    corr_results = []
    for metric in ["mean_centroid_distance", "min_centroid_distance", "mean_purity"]:
        r_pear, p_pear = pearsonr(df[metric], df["transfer_r2"])
        r_spear, p_spear = spearmanr(df[metric], df["transfer_r2"])

        # Permutation test
        n_perm = 500
        r_null = []
        for _ in range(n_perm):
            y_perm = np.random.permutation(df["transfer_r2"].values)
            r_null.append(pearsonr(df[metric].values, y_perm)[0])
        p_perm = np.mean(np.abs(r_null) >= abs(r_pear))

        corr_results.append({
            "metric": metric,
            "pearson_r": float(r_pear),
            "pearson_p": float(p_pear),
            "spearman_rho": float(r_spear),
            "spearman_p": float(p_spear),
            "permutation_p": float(p_perm),
        })
        print(f"  {metric}: r={r_pear:.4f}, p={p_pear:.4f}, perm_p={p_perm:.4f}")

    corr_df = pd.DataFrame(corr_results)
    corr_df.to_csv(OUT / "t036_transfer_barriers.csv", index=False)
    df.to_csv(OUT / "t036_transfer_family_metrics.csv", index=False)
    print("  Saved t036_transfer_barriers.csv")

    return corr_results


# ============================================================
# TASK 6: META-FAMILY CLUSTERING
# ============================================================

def task6_metafamilies(centroid_dist, unique_fams):
    """Hierarchical clustering of family centroids."""
    # Average linkage on centroid distance
    condensed = squareform(centroid_dist)
    Z = linkage(condensed, method="average")

    # Determine number of clusters (cut at height producing 3-5 groups)
    for n_clusters in [3, 4, 5]:
        labels = fcluster(Z, n_clusters, criterion="maxclust")
        print(f"  {n_clusters} meta-families: {dict(Counter(labels))}")

    # Use 4 meta-families
    labels = fcluster(Z, 4, criterion="maxclust")
    meta_map = {fam: int(labels[i]) for i, fam in enumerate(unique_fams)}

    # Dendrogram
    fig, ax = plt.subplots(figsize=(8, 4))
    dendrogram(Z, labels=unique_fams, ax=ax, leaf_rotation=45, leaf_font_size=7)
    ax.set_ylabel("Distance")
    ax.set_title("Family dendrogram (average linkage, centroid distance)")
    ax.axhline(y=centroid_dist[np.triu_indices(len(unique_fams), k=1)].mean(),
               color="red", ls="--", lw=0.6, label="Mean inter-family distance")
    ax.legend(frameon=False)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t036_metafamily_tree.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t036_metafamily_tree.pdf/.png")

    # t-SNE visualization (on centroids)
    from sklearn.manifold import TSNE
    centroid_matrix = np.array([centroid_dist[i] for i in range(len(unique_fams))])
    perplexity = min(5, len(unique_fams) - 1)
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
    coords = tsne.fit_transform(centroid_matrix)

    fig, ax = plt.subplots(figsize=(8, 6))
    colors_map = {1: "#e74c3c", 2: "#3498db", 3: "#2ecc71", 4: "#f39c12"}
    for i, fam in enumerate(unique_fams):
        c = colors_map.get(meta_map[fam], "gray")
        ax.scatter(coords[i, 0], coords[i, 1], s=80, c=c, edgecolors="white", linewidths=0.5)
        ax.annotate(fam, (coords[i, 0], coords[i, 1]), fontsize=6, ha="center", va="bottom")

    ax.set_title("Family centroids in t-SNE space (colored by meta-family)")
    ax.set_xlabel("t-SNE 1")
    ax.set_ylabel("t-SNE 2")
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t036_umap_families.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t036_umap_families.pdf/.png")

    return meta_map, labels


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T036: FAMILY BOUNDARY GEOMETRY")
    print("=" * 70)
    t0 = time.time()

    # Load
    print("\nLoading data...")
    Phi, X_raw, families, unique_fams, fam_idx, systems = load_data()
    print(f"  {len(Phi)} systems, {len(unique_fams)} families, Φ={Phi.shape}")

    # Task 1
    print("\n[Task 1] Family separation matrix...")
    centroid_dist, mahal_dist, _ = task1_separation_matrix(Phi, families, unique_fams)

    # Task 2
    print("\n[Task 2] Family confusion classifier...")
    acc, bal_acc, confused = task2_family_confusion(Phi, families, unique_fams)

    # Task 3
    print("\n[Task 3] Boundary system identification...")
    all_overlap, boundary = task3_boundary_systems(Phi, families, unique_fams, systems)

    # Task 4
    print("\n[Task 4] kNN purity distribution...")
    purities = task4_purity(Phi, families, unique_fams)

    # Task 5
    print("\n[Task 5] Transfer barrier analysis...")
    barriers = task5_transfer_barriers(Phi, families, unique_fams, centroid_dist, purities)

    # Task 6
    print("\n[Task 6] Meta-family clustering...")
    meta_map, meta_labels = task6_metafamilies(centroid_dist, unique_fams)

    # Task 7: Final verdict
    elapsed = time.time() - t0

    # Determine isolation
    mean_dists = {}
    for i, fam in enumerate(unique_fams):
        mean_dists[fam] = np.mean([centroid_dist[i, j] for j in range(len(unique_fams)) if j != i])
    most_isolated = max(mean_dists, key=mean_dists.get)

    # Determine overlap
    overlap_counts = boundary["family"].value_counts()
    most_overlapping = overlap_counts.idxmax() if len(overlap_counts) > 0 else "none"

    mean_purity = np.mean(purities)
    n_boundary = len(boundary)
    n_metafamilies = len(set(meta_labels))

    # Check success criterion
    any_correlation = any(b["permutation_p"] < 0.05 for b in barriers)
    success = any_correlation

    print(f"\nRuntime: {elapsed:.1f}s")
    print("\n" + "=" * 70)
    print("T036 RESULTS")
    print("=" * 70)
    print(f"Family classifier accuracy: {acc:.4f}")
    print(f"Most confused pairs:")
    for fi, fj, cnt in confused[:5]:
        print(f"  {fi} <-> {fj}: {cnt}")
    print()
    print(f"Most isolated family:     {most_isolated} (mean dist={mean_dists[most_isolated]:.4f})")
    print(f"Most overlapping family:  {most_overlapping} ({overlap_counts.get(most_overlapping, 0)} boundary systems)")
    print(f"Mean family purity:       {mean_purity:.4f}")
    print(f"Boundary systems:         {n_boundary}/{len(Phi)} ({100*n_boundary/len(Phi):.1f}%)")
    print(f"Meta-families detected:   {n_metafamilies}")
    print()
    print("Transfer barrier correlations:")
    for b in barriers:
        sig = "*" if b["permutation_p"] < 0.05 else " "
        print(f"  {b['metric']:30s}: r={b['pearson_r']:.4f}  perm_p={b['permutation_p']:.4f} {sig}")
    print()
    verdict = "TRANSFER FAILURE EXPLAINED" if success else "TRANSFER FAILURE NOT EXPLAINED"
    print(f"FINAL VERDICT: {verdict}")
    print("=" * 70)

    # Save summary
    summary = {
        "family_classifier_accuracy": float(acc),
        "family_classifier_balanced_accuracy": float(bal_acc),
        "most_confused_pairs": [{"families": (fi, fj), "count": cnt} for fi, fj, cnt in confused[:10]],
        "most_isolated_family": most_isolated,
        "most_overlapping_family": most_overlapping,
        "mean_family_purity": float(mean_purity),
        "n_boundary_systems": n_boundary,
        "n_total_systems": len(Phi),
        "n_metafamilies": n_metafamilies,
        "metafamily_map": meta_map,
        "transfer_barriers": barriers,
        "success_criterion": "at least one quantitative explanation for transfer failure",
        "success_met": success,
    }
    with open(OUT / "t036_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved t036_summary.json")


if __name__ == "__main__":
    main()
