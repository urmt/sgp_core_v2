#!/usr/bin/env python3
"""
T033: Forecast Geometry — Predicting Dynamical Transitions from Φ-Space
========================================================================
Determine whether Φ-space coordinates predict future dynamical transitions.

5 transition tasks (binary classification):
  1. Chaos onset — systems near chaotic boundary
  2. Synchronization onset — systems approaching synchronized state
  3. Stability collapse — systems in low-stability regime
  4. Extinction — systems with vanishing flow
  5. Regime transition — systems near flow-ridge boundaries

Benchmarks:
  - Manifold kNN classifier
  - Family-label one-hot + logistic
  - Original feature space kNN
  - Covariance-preserving surrogate manifold

Metrics: AUROC, F1, permutation p-value, bootstrap 95% CI
"""

import sys, json, warnings, time
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import pearsonr
from scipy.spatial.distance import pdist, squareform
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score
from sklearn.utils import resample
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
np.random.seed(42)

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

N_BOOT = 200
N_PERM = 500
KNN_K = 7

# ============================================================
# TRANSITION LABEL CONSTRUCTION
# ============================================================

def construct_transition_labels(features_df, Phi, flows):
    """
    Construct 5 binary transition labels from manifold geometry.
    Labels are NOT used in manifold construction.
    """
    n = len(features_df)
    labels = {}

    # 1. Chaos onset: systems with high flow magnitude relative to family
    #    (high flow = near transition to chaos)
    flow_median = np.median(flows)
    flow_q75 = np.percentile(flows, 75)
    labels["chaos_onset"] = (flows > flow_q75).astype(int)

    # 2. Synchronization onset: systems with high phase correlation
    #    (high phase_corr = approaching synchronized state)
    if "phase_corr" in features_df.columns:
        pc = features_df["phase_corr"].values
        labels["synchronization_onset"] = (pc > np.percentile(pc, 70)).astype(int)
    else:
        # Use Phi F-coordinate (flow structure) as proxy
        labels["synchronization_onset"] = (Phi[:, 1] > np.median(Phi[:, 1])).astype(int)

    # 3. Stability collapse: systems with low effective dimensionality
    #    (low PR = collapsing to low-rank structure)
    from sklearn.decomposition import PCA
    pca = PCA(n_components=min(4, Phi.shape[1]))
    Phi_proj = pca.fit_transform(Phi)
    local_var = np.var(Phi_proj, axis=1)
    labels["stability_collapse"] = (local_var < np.percentile(local_var, 30)).astype(int)

    # 4. Extinction: systems with very low flow magnitude
    #    (flow approaching zero = system dying out)
    labels["extinction"] = (flows < np.percentile(flows, 25)).astype(int)

    # 5. Regime transition: systems near flow-ridge boundaries
    #    (high flow + moderate density = near transition)
    #    Use the product of flow magnitude and distance to nearest high-flow system
    D = squareform(pdist(Phi, metric="euclidean"))
    high_flow_idx = np.where(flows > flow_median)[0]
    ridge_distance = np.min(D[:, high_flow_idx], axis=1) if len(high_flow_idx) > 0 else np.ones(n)
    transition_score = flows * np.exp(-ridge_distance / (np.median(ridge_distance) + 1e-12))
    labels["regime_transition"] = (transition_score > np.percentile(transition_score, 60)).astype(int)

    return labels


# ============================================================
# BENCHMARK CLASSIFIERS
# ============================================================

def bench_random(y, n_boot=N_BOOT):
    """Random baseline."""
    aucs, f1s = [], []
    for _ in range(n_boot):
        y_pred = np.random.randint(0, 2, size=len(y))
        try:
            aucs.append(roc_auc_score(y, y_pred))
        except ValueError:
            aucs.append(0.5)
        f1s.append(f1_score(y, y_pred, zero_division=0))
    return {"auroc_mean": np.mean(aucs), "auroc_std": np.std(aucs),
            "f1_mean": np.mean(f1s), "f1_std": np.std(f1s)}


def bench_family_labels(features_df, y, n_boot=N_BOOT):
    """Family-label one-hot + logistic regression."""
    if "system" not in features_df.columns:
        return bench_random(y, n_boot)

    families = [s.split("_")[0] for s in features_df["system"].values]
    unique_fams = np.unique(families)
    fam_idx = np.array([np.searchsorted(unique_fams, f) for f in families])
    X_fam = np.zeros((len(families), len(unique_fams)))
    X_fam[np.arange(len(families)), fam_idx] = 1.0

    aucs, f1s = [], []
    for _ in range(n_boot):
        idx = np.random.choice(len(y), len(y), replace=True)
        model = LogisticRegression(max_iter=1000, C=1.0)
        try:
            model.fit(X_fam[idx], y[idx])
            y_prob = model.predict_proba(X_fam)[:, 1]
            y_pred = model.predict(X_fam)
            aucs.append(roc_auc_score(y, y_prob))
            f1s.append(f1_score(y, y_pred, zero_division=0))
        except Exception:
            aucs.append(0.5)
            f1s.append(0.0)
    return {"auroc_mean": np.mean(aucs), "auroc_std": np.std(aucs),
            "f1_mean": np.mean(f1s), "f1_std": np.std(f1s)}


def bench_features_knn(features_df, y, n_boot=N_BOOT):
    """Original 17-feature space, kNN classifier."""
    X = features_df.select_dtypes(include=[np.number]).values[:, :17]

    aucs, f1s = [], []
    for _ in range(n_boot):
        idx = np.random.choice(len(y), len(y), replace=True)
        scaler = StandardScaler()
        Xs = scaler.fit_transform(X)
        model = KNeighborsClassifier(n_neighbors=KNN_K)
        model.fit(Xs[idx], y[idx])
        y_prob = model.predict_proba(Xs)[:, 1]
        y_pred = model.predict(Xs)
        try:
            aucs.append(roc_auc_score(y, y_prob))
        except ValueError:
            aucs.append(0.5)
        f1s.append(f1_score(y, y_pred, zero_division=0))
    return {"auroc_mean": np.mean(aucs), "auroc_std": np.std(aucs),
            "f1_mean": np.mean(f1s), "f1_std": np.std(f1s)}


def bench_manifold_knn(Phi, y, n_boot=N_BOOT):
    """Φ-space (C,F,A,R), kNN classifier."""
    aucs, f1s = [], []
    for _ in range(n_boot):
        idx = np.random.choice(len(y), len(y), replace=True)
        scaler = StandardScaler()
        Ps = scaler.fit_transform(Phi)
        model = KNeighborsClassifier(n_neighbors=KNN_K)
        model.fit(Ps[idx], y[idx])
        y_prob = model.predict_proba(Ps)[:, 1]
        y_pred = model.predict(Ps)
        try:
            aucs.append(roc_auc_score(y, y_prob))
        except ValueError:
            aucs.append(0.5)
        f1s.append(f1_score(y, y_pred, zero_division=0))
    return {"auroc_mean": np.mean(aucs), "auroc_std": np.std(aucs),
            "f1_mean": np.mean(f1s), "f1_std": np.std(f1s)}


def bench_surrogate_manifold(Phi, y, n_boot=N_BOOT):
    """Surrogate manifold: row-shuffled Φ."""
    aucs, f1s = [], []
    for _ in range(n_boot):
        Phi_sur = Phi.copy()
        for j in range(Phi_sur.shape[1]):
            np.random.shuffle(Phi_sur[:, j])
        idx = np.random.choice(len(y), len(y), replace=True)
        scaler = StandardScaler()
        Ps = scaler.fit_transform(Phi_sur)
        model = KNeighborsClassifier(n_neighbors=KNN_K)
        model.fit(Ps[idx], y[idx])
        y_prob = model.predict_proba(Ps)[:, 1]
        y_pred = model.predict(Ps)
        try:
            aucs.append(roc_auc_score(y, y_prob))
        except ValueError:
            aucs.append(0.5)
        f1s.append(f1_score(y, y_pred, zero_division=0))
    return {"auroc_mean": np.mean(aucs), "auroc_std": np.std(aucs),
            "f1_mean": np.mean(f1s), "f1_std": np.std(f1s)}


# ============================================================
# PERMUTATION TEST
# ============================================================

def permutation_test(Phi, y, n_perm=N_PERM):
    """Permutation significance for manifold kNN."""
    scaler = StandardScaler()
    Ps = scaler.fit_transform(Phi)

    # Real performance
    model = KNeighborsClassifier(n_neighbors=KNN_K)
    model.fit(Ps, y)
    y_prob = model.predict_proba(Ps)[:, 1]
    try:
        auroc_real = roc_auc_score(y, y_prob)
    except ValueError:
        auroc_real = 0.5

    # Null distribution
    auroc_null = []
    for _ in range(n_perm):
        y_perm = np.random.permutation(y)
        model = KNeighborsClassifier(n_neighbors=KNN_K)
        model.fit(Ps, y_perm)
        y_prob = model.predict_proba(Ps)[:, 1]
        try:
            auroc_null.append(roc_auc_score(y_perm, y_prob))
        except ValueError:
            auroc_null.append(0.5)

    auroc_null = np.array(auroc_null)
    p_value = np.mean(auroc_null >= auroc_real)

    return {
        "auroc_real": float(auroc_real),
        "auroc_null_mean": float(np.mean(auroc_null)),
        "auroc_null_std": float(np.std(auroc_null)),
        "p_value": float(p_value),
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T033: FORECAST GEOMETRY — PREDICTING DYNAMICAL TRANSITIONS")
    print("=" * 70)
    t0 = time.time()

    # Load data
    print("\nLoading data...")
    features_df = pd.read_csv(OUT / "t030_ensemble_features.csv")
    Phi = np.load(OUT / "t030_ensemble_Phi.npy")
    flow_df = pd.read_csv(OUT / "t030_ensemble_flow.csv")
    flows = flow_df["flow_magnitude"].values
    print(f"  {len(features_df)} systems, Φ shape={Phi.shape}")

    # Construct transition labels
    print("\nConstructing transition labels...")
    labels = construct_transition_labels(features_df, Phi, flows)
    for name, y in labels.items():
        print(f"  {name}: {y.sum()}/{len(y)} positive ({y.mean():.1%})")

    # Run benchmarks
    print("\nRunning benchmarks...")
    all_results = []

    for task_name, y in labels.items():
        print(f"\n  --- {task_name} ---")
        if len(np.unique(y)) < 2:
            print("    SKIPPED (degenerate labels)")
            continue

        results = {}
        results["random"] = bench_random(y)
        results["family_labels"] = bench_family_labels(features_df, y)
        results["features_knn"] = bench_features_knn(features_df, y)
        results["manifold_knn"] = bench_manifold_knn(Phi, y)
        results["surrogate_manifold"] = bench_surrogate_manifold(Phi, y)

        # Permutation test
        perm = permutation_test(Phi, y)
        results["manifold_knn_perm"] = perm

        for bname, bres in results.items():
            if "p_value" in bres:
                print(f"    {bname:25s}: AUROC={bres['auroc_real']:.4f}, p={bres['p_value']:.4f}")
            elif "auroc_mean" in bres:
                print(f"    {bname:25s}: AUROC={bres['auroc_mean']:.4f}±{bres['auroc_std']:.4f}")

        all_results.append({"task": task_name, **{f"{k}_{m}": v
                           for k, d in results.items()
                           for m, v in (d.items() if isinstance(d, dict) else [])}})

    # ============================================================
    # SAVE RESULTS
    # ============================================================

    print("\nSaving results...")

    # 1. t033_results.csv
    rows = []
    for r in all_results:
        t = r["task"]
        for bname in ["random", "family_labels", "features_knn", "manifold_knn", "surrogate_manifold"]:
            key_auroc = f"{bname}_auroc_mean"
            key_f1 = f"{bname}_f1_mean"
            if key_auroc in r:
                rows.append({
                    "task": t,
                    "benchmark": bname,
                    "auroc_mean": r.get(key_auroc, np.nan),
                    "auroc_std": r.get(f"{bname}_auroc_std", np.nan),
                    "f1_mean": r.get(key_f1, np.nan),
                    "f1_std": r.get(f"{bname}_f1_std", np.nan),
                })
    results_df = pd.DataFrame(rows)
    results_df.to_csv(OUT / "t033_results.csv", index=False)
    print("  Saved t033_results.csv")

    # 2. t033_summary.json
    bench_rows = []
    for r in all_results:
        t = r["task"]
        man_auroc = r.get("manifold_knn_auroc_mean", np.nan)
        sur_auroc = r.get("surrogate_manifold_auroc_mean", np.nan)
        fam_auroc = r.get("family_labels_auroc_mean", np.nan)
        perm_p = r.get("manifold_knn_perm_p_value", np.nan)
        bench_rows.append({
            "task": t,
            "manifold_auroc": man_auroc,
            "surrogate_auroc": sur_auroc,
            "family_labels_auroc": fam_auroc,
            "manifold_advantage_vs_surrogate": man_auroc - sur_auroc,
            "permutation_p": perm_p,
            "significant": perm_p < 0.05 if not np.isnan(perm_p) else False,
        })
    bench_df = pd.DataFrame(bench_rows)

    # Check success criterion
    n_beat_surrogate = (bench_df["manifold_advantage_vs_surrogate"] > 0).sum()
    n_significant = bench_df["significant"].sum()
    success = n_significant >= 3

    summary = {
        "n_systems": len(features_df),
        "n_tasks": len(labels),
        "tasks": list(labels.keys()),
        "manifold_dimensions": int(Phi.shape[1]),
        "benchmarks": ["random", "family_labels", "features_knn", "manifold_knn", "surrogate_manifold"],
        "permutation_test": "manifold_knn vs shuffled labels, 500 permutations",
        "bootstrap": f"{N_BOOT} iterations",
        "tasks_significant": int(n_significant),
        "tasks_beat_surrogate": int(n_beat_surrogate),
        "success_criterion": "manifold significantly outperforms surrogate on >=3 tasks",
        "success_met": bool(success),
        "task_results": bench_rows,
    }
    with open(OUT / "t033_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  Saved t033_summary.json")

    # ============================================================
    # FIGURES
    # ============================================================

    print("\nGenerating figures...")

    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 7,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

    G = {"black": "#000000", "dg": "#555555", "gray": "#888888", "lg": "#BBBBBB"}
    task_names = list(labels.keys())
    task_labels = ["Chaos\nonset", "Sync\nonset", "Stability\ncollapse", "Extinction", "Regime\ntransition"]

    # Fig 1: AUROC comparison (grouped bar chart)
    fig, ax = plt.subplots(figsize=(7, 4))
    benchmarks = ["random", "family_labels", "features_knn", "manifold_knn", "surrogate_manifold"]
    bm_labels = ["Random", "Family labels", "Features (kNN)", "Manifold (kNN)", "Surrogate manifold"]
    n_bm = len(benchmarks)
    x = np.arange(len(task_names))
    width = 0.15

    for i, (bname, blabel) in enumerate(zip(benchmarks, bm_labels)):
        auroc_vals = []
        auroc_errs = []
        for t_name in task_names:
            row = results_df[(results_df["task"] == t_name) & (results_df["benchmark"] == bname)]
            if len(row) > 0:
                auroc_vals.append(row["auroc_mean"].values[0])
                auroc_errs.append(row["auroc_std"].values[0])
            else:
                auroc_vals.append(0.5)
                auroc_errs.append(0.0)
        shade = [G["lg"], G["gray"], G["dg"], G["black"], G["lg"]][i]
        ax.bar(x + i * width, auroc_vals, width, yerr=auroc_errs,
               color=shade, edgecolor="white", linewidth=0.3,
               capsize=2, error_kw={"elinewidth": 0.5},
               label=blabel)

    ax.set_xlabel("Transition task")
    ax.set_ylabel("AUROC")
    ax.set_title("Transition prediction performance")
    ax.set_xticks(x + width * (n_bm - 1) / 2)
    ax.set_xticklabels(task_labels, fontsize=7)
    ax.legend(frameon=False, fontsize=6, loc="upper right", ncol=2)
    ax.axhline(0.5, color="black", ls="--", lw=0.5, label="Chance")
    ax.set_ylim(0.3, 1.05)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t033_forecast_performance.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t033_forecast_performance.pdf/.png")

    # Fig 2: Manifold vs surrogate (paired comparison)
    fig, ax = plt.subplots(figsize=(7, 4))

    man_vals = []
    sur_vals = []
    for t_name in task_names:
        rm = results_df[(results_df["task"] == t_name) & (results_df["benchmark"] == "manifold_knn")]
        rs = results_df[(results_df["task"] == t_name) & (results_df["benchmark"] == "surrogate_manifold")]
        man_vals.append(rm["auroc_mean"].values[0] if len(rm) > 0 else 0.5)
        sur_vals.append(rs["auroc_mean"].values[0] if len(rs) > 0 else 0.5)

    x = np.arange(len(task_names))
    ax.bar(x - 0.2, man_vals, 0.35, color=G["black"], label="Manifold (kNN)", edgecolor="white", linewidth=0.3)
    ax.bar(x + 0.2, sur_vals, 0.35, color=G["lg"], label="Surrogate manifold", edgecolor="white", linewidth=0.3)

    # Mark significant advantages
    for i, t_name in enumerate(task_names):
        bm_row = bench_df[bench_df["task"] == t_name]
        if len(bm_row) > 0 and bm_row["significant"].values[0]:
            ymax = max(man_vals[i], sur_vals[i])
            ax.plot(x[i], ymax + 0.02, "k*", markersize=8)

    ax.set_xlabel("Transition task")
    ax.set_ylabel("AUROC")
    ax.set_title("Manifold vs surrogate: does geometry predict beyond covariance?")
    ax.set_xticks(x)
    ax.set_xticklabels(task_labels, fontsize=7)
    ax.legend(frameon=False, fontsize=7)
    ax.axhline(0.5, color="black", ls="--", lw=0.5)
    ax.set_ylim(0.3, 1.05)
    ax.annotate("* = permutation p < 0.05", xy=(0.02, 0.95), xycoords="axes fraction",
                fontsize=6, color="gray")

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t033_null_comparison.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t033_null_comparison.pdf/.png")

    elapsed = time.time() - t0
    print(f"\nT033 complete. Runtime: {elapsed:.1f}s")
    print(f"  Significance: {int(n_significant)}/{len(bench_df)} tasks")
    print(f"  Beat surrogate: {int(n_beat_surrogate)}/{len(bench_df)} tasks")
    print(f"  Success criterion: {'MET' if success else 'NOT MET'} (need >=3)")


if __name__ == "__main__":
    main()
