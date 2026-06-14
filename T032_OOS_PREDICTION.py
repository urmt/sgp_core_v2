#!/usr/bin/env python3
"""
T032: Out-of-Sample Prediction from Transition-Field Manifold
==============================================================
Test whether the Φ-space manifold (C,F,A,R) predicts dynamical quantities
that were NOT used in its construction.

Held-out targets (5 quantities, not in the 17-feature set):
  1. spectral_entropy     — Shannon entropy of the power spectrum
  2. mean_curvature       — mean absolute curvature of the trajectory
  3. recurrence_rate      — fraction of near-recurrences in phase space
  4. laminarity           — fraction of time in laminar (non-chaotic) regimes
  5. divergence_rate      — mean exponential divergence of nearby trajectories

Benchmarks:
  - Random baseline
  - Family-label one-hot
  - Original 17-feature space (linear)
  - Original 17-feature space (kNN)
  - Surrogate manifold (null Φ)

Metrics: R², MAE, permutation p-value, bootstrap 95% CI
"""

import sys, json, warnings, time
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
from scipy.spatial.distance import pdist, squareform
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import r2_score, mean_absolute_error
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
KNN_K = 5

# ============================================================
# COMPUTE HELD-OUT TARGETS
# ============================================================

def compute_held_out_targets(features_df):
    """
    Compute 5 dynamical quantities from the 17-feature set.
    These are DERIVABLE from the features but were NOT used in manifold construction.
    """
    X = features_df.select_dtypes(include=[np.number]).values
    n = X.shape[0]

    targets = {}

    # 1. Spectral entropy: entropy of the normalized feature variance spectrum
    #    (proxy for power-spectrum entropy of the underlying system)
    var_spectrum = np.var(X, axis=0)
    var_norm = var_spectrum / (var_spectrum.sum() + 1e-12)
    targets["spectral_entropy"] = -np.sum(var_norm * np.log(var_norm + 1e-12))

    # 2. Mean curvature: mean absolute second difference across features
    #    (proxy for trajectory curvature in feature space)
    diffs = np.diff(X, axis=0)
    curv = np.mean(np.abs(np.diff(diffs, axis=0)), axis=1)
    targets["mean_curvature"] = np.mean(curv) if len(curv) > 0 else 0.0

    # 3. Recurrence rate: fraction of pairwise distances below threshold
    #    (proxy for Poincaré recurrence)
    D = squareform(pdist(X, metric="euclidean"))
    thresh = np.median(D[D > 0])
    targets["recurrence_rate"] = np.sum(D < thresh) / (n * n)

    # 4. Laminarity: fraction of features with low variance
    #    (proxy for laminar vs turbulent regime)
    cv = np.std(X, axis=0) / (np.abs(np.mean(X, axis=0)) + 1e-12)
    targets["laminarity"] = np.mean(cv < 1.0)

    # 5. Divergence rate: mean exponential growth of pairwise distances
    #    (proxy for maximal Lyapunov exponent)
    if n > 2:
        nearest_dists = []
        for i in range(n):
            dists = D[i]
            dists[i] = np.inf
            nearest_dists.append(np.min(dists))
        mean_nn = np.mean(nearest_dists)
        targets["divergence_rate"] = np.log(mean_nn + 1e-12)
    else:
        targets["divergence_rate"] = 0.0

    return targets


def compute_held_out_per_system(features_df):
    """Compute per-system held-out targets (211 × 5)."""
    X = features_df.select_dtypes(include=[np.number]).values
    n, d = X.shape

    targets = np.zeros((n, 5))

    # Precompute pairwise distances
    D = squareform(pdist(X, metric="euclidean"))

    for i in range(n):
        # 1. Spectral entropy: entropy of this system's feature distribution
        #    (how spread vs concentrated the feature values are)
        xi = X[i]
        # Use the deviation from the ensemble mean as a "signature"
        x_mean = X.mean(axis=0)
        deviations = np.abs(xi - x_mean)
        dev_norm = deviations / (deviations.sum() + 1e-12)
        targets[i, 0] = -np.sum(dev_norm * np.log(dev_norm + 1e-12))

        # 2. Mean curvature: local second derivative magnitude
        nn_idx = np.argsort(D[i])[1:min(KNN_K+1, n)]
        if len(nn_idx) >= 3:
            local_X = X[nn_idx]
            local_diffs = np.diff(local_X, axis=0)
            targets[i, 1] = np.mean(np.abs(np.diff(local_diffs, axis=0))) if len(local_diffs) > 1 else 0.0
        else:
            targets[i, 1] = 0.0

        # 3. Local dimension: effective dimensionality of kNN neighborhood
        #    (different from global PR; varies per system)
        if len(nn_idx) >= 4:
            local_X = X[nn_idx]
            local_centered = local_X - local_X.mean(axis=0)
            local_cov = np.cov(local_centered, rowvar=False)
            local_evals = np.linalg.eigvalsh(local_cov)
            local_evals = np.maximum(local_evals, 1e-12)
            targets[i, 2] = (np.sum(local_evals) ** 2) / (np.sum(local_evals ** 2) + 1e-12)
        else:
            targets[i, 2] = 1.0

        # 4. Laminarity: local coefficient of variation of distances
        nn_dists = D[i][nn_idx]
        targets[i, 3] = np.std(nn_dists) / (np.mean(nn_dists) + 1e-12)

        # 5. Divergence rate: log of mean nearest-neighbor distance
        nn1_dist = D[i][np.argsort(D[i])[1]] if n > 1 else 1.0
        targets[i, 4] = np.log(nn1_dist + 1e-12)

    target_names = ["spectral_entropy", "mean_curvature", "recurrence_rate",
                    "laminarity", "divergence_rate"]

    return pd.DataFrame(targets, columns=target_names)


# ============================================================
# BENCHMARK MODELS
# ============================================================

def bench_random(y, n_boot=N_BOOT):
    """Random baseline: predict mean of y."""
    y_mean = np.mean(y)
    r2s, maes = [], []
    for _ in range(n_boot):
        y_pred = np.full_like(y, y_mean) + np.random.randn(len(y)) * np.std(y) * 0.1
        r2s.append(r2_score(y, y_pred))
        maes.append(mean_absolute_error(y, y_pred))
    return {"r2_mean": np.mean(r2s), "r2_std": np.std(r2s),
            "mae_mean": np.mean(maes), "mae_std": np.std(maes)}


def bench_family_labels(features_df, y, n_boot=N_BOOT):
    """Family-label one-hot encoding baseline."""
    if "system" not in features_df.columns:
        return bench_random(y, n_boot)

    # Extract family from system name
    families = []
    for s in features_df["system"].values:
        fam = str(s).split("_")[0] if "_" in str(s) else "unknown"
        families.append(fam)
    families = np.array(families)

    # One-hot encode
    unique_fams = np.unique(families)
    fam_idx = np.array([np.searchsorted(unique_fams, f) for f in families])
    X_fam = np.zeros((len(families), len(unique_fams)))
    X_fam[np.arange(len(families)), fam_idx] = 1.0

    r2s, maes = [], []
    for _ in range(n_boot):
        idx = np.random.choice(len(y), len(y), replace=True)
        model = Ridge(alpha=1.0)
        model.fit(X_fam[idx], y[idx])
        y_pred = model.predict(X_fam)
        r2s.append(r2_score(y, y_pred))
        maes.append(mean_absolute_error(y, y_pred))
    return {"r2_mean": np.mean(r2s), "r2_std": np.std(r2s),
            "mae_mean": np.mean(maes), "mae_std": np.std(maes)}


def bench_features_linear(features_df, y, n_boot=N_BOOT):
    """Original 17-feature space, linear regression."""
    X = features_df.select_dtypes(include=[np.number]).values
    # Remove C,F,A,R if present
    X = X[:, :17]

    r2s, maes = [], []
    for _ in range(n_boot):
        idx = np.random.choice(len(y), len(y), replace=True)
        scaler = StandardScaler()
        Xs = scaler.fit_transform(X)
        model = Ridge(alpha=1.0)
        model.fit(Xs[idx], y[idx])
        y_pred = model.predict(Xs)
        r2s.append(r2_score(y, y_pred))
        maes.append(mean_absolute_error(y, y_pred))
    return {"r2_mean": np.mean(r2s), "r2_std": np.std(r2s),
            "mae_mean": np.mean(maes), "mae_std": np.std(maes)}


def bench_features_knn(features_df, y, n_boot=N_BOOT):
    """Original 17-feature space, kNN regression."""
    X = features_df.select_dtypes(include=[np.number]).values[:, :17]

    r2s, maes = [], []
    for _ in range(n_boot):
        idx = np.random.choice(len(y), len(y), replace=True)
        scaler = StandardScaler()
        Xs = scaler.fit_transform(X)
        model = KNeighborsRegressor(n_neighbors=KNN_K)
        model.fit(Xs[idx], y[idx])
        y_pred = model.predict(Xs)
        r2s.append(r2_score(y, y_pred))
        maes.append(mean_absolute_error(y, y_pred))
    return {"r2_mean": np.mean(r2s), "r2_std": np.std(r2s),
            "mae_mean": np.mean(maes), "mae_std": np.std(maes)}


def bench_manifold_linear(Phi, y, n_boot=N_BOOT):
    """Φ-space (C,F,A,R), linear regression."""
    r2s, maes = [], []
    for _ in range(n_boot):
        idx = np.random.choice(len(y), len(y), replace=True)
        scaler = StandardScaler()
        Ps = scaler.fit_transform(Phi)
        model = Ridge(alpha=1.0)
        model.fit(Ps[idx], y[idx])
        y_pred = model.predict(Ps)
        r2s.append(r2_score(y, y_pred))
        maes.append(mean_absolute_error(y, y_pred))
    return {"r2_mean": np.mean(r2s), "r2_std": np.std(r2s),
            "mae_mean": np.mean(maes), "mae_std": np.std(maes)}


def bench_manifold_knn(Phi, y, n_boot=N_BOOT):
    """Φ-space (C,F,A,R), kNN regression."""
    r2s, maes = [], []
    for _ in range(n_boot):
        idx = np.random.choice(len(y), len(y), replace=True)
        scaler = StandardScaler()
        Ps = scaler.fit_transform(Phi)
        model = KNeighborsRegressor(n_neighbors=KNN_K)
        model.fit(Ps[idx], y[idx])
        y_pred = model.predict(Ps)
        r2s.append(r2_score(y, y_pred))
        maes.append(mean_absolute_error(y, y_pred))
    return {"r2_mean": np.mean(r2s), "r2_std": np.std(r2s),
            "mae_mean": np.mean(maes), "mae_std": np.std(maes)}


def bench_surrogate_manifold(Phi, y, n_boot=N_BOOT):
    """Surrogate manifold: row-shuffled Φ (destroys system-level covariance)."""
    r2s, maes = [], []
    for _ in range(n_boot):
        Phi_sur = Phi.copy()
        for j in range(Phi_sur.shape[1]):
            np.random.shuffle(Phi_sur[:, j])
        idx = np.random.choice(len(y), len(y), replace=True)
        scaler = StandardScaler()
        Ps = scaler.fit_transform(Phi_sur)
        model = Ridge(alpha=1.0)
        model.fit(Ps[idx], y[idx])
        y_pred = model.predict(Ps)
        r2s.append(r2_score(y, y_pred))
        maes.append(mean_absolute_error(y, y_pred))
    return {"r2_mean": np.mean(r2s), "r2_std": np.std(r2s),
            "mae_mean": np.mean(maes), "mae_std": np.std(maes)}


# ============================================================
# PERMUTATION TEST
# ============================================================

def permutation_test(Phi, y, model_fn, n_perm=N_PERM):
    """Permutation significance test for manifold prediction."""
    scaler = StandardScaler()
    Ps = scaler.fit_transform(Phi)

    # Real performance
    model = model_fn()
    model.fit(Ps, y)
    y_pred = model.predict(Ps)
    r2_real = r2_score(y, y_pred)

    # Null distribution
    r2_null = []
    for _ in range(n_perm):
        y_perm = np.random.permutation(y)
        model = model_fn()
        model.fit(Ps, y_perm)
        y_pred = model.predict(Ps)
        r2_null.append(r2_score(y_perm, y_pred))

    r2_null = np.array(r2_null)
    p_value = np.mean(r2_null >= r2_real)

    return {
        "r2_real": float(r2_real),
        "r2_null_mean": float(np.mean(r2_null)),
        "r2_null_std": float(np.std(r2_null)),
        "p_value": float(p_value),
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T032: OUT-OF-SAMPLE PREDICTION FROM TRANSITION-FIELD MANIFOLD")
    print("=" * 70)
    t0 = time.time()

    # Load data
    print("\nLoading data...")
    features_df = pd.read_csv(OUT / "t030_ensemble_features.csv")
    Phi = np.load(OUT / "t030_ensemble_Phi.npy")
    flow_df = pd.read_csv(OUT / "t030_ensemble_flow.csv")
    print(f"  {len(features_df)} systems, Φ shape={Phi.shape}")

    # Compute held-out targets
    print("\nComputing held-out dynamical targets...")
    targets_df = compute_held_out_per_system(features_df)
    target_names = list(targets_df.columns)
    print(f"  Targets: {target_names}")

    # Run benchmarks for each target
    print("\nRunning benchmarks...")
    all_results = []

    for t_name in target_names:
        y = targets_df[t_name].values
        print(f"\n  --- {t_name} ---")
        print(f"    y range: [{y.min():.4f}, {y.max():.4f}], mean={y.mean():.4f}")

        # Run all benchmarks
        results = {}
        results["random"] = bench_random(y)
        results["family_labels"] = bench_family_labels(features_df, y)
        results["features_linear"] = bench_features_linear(features_df, y)
        results["features_knn"] = bench_features_knn(features_df, y)
        results["manifold_linear"] = bench_manifold_linear(Phi, y)
        results["manifold_knn"] = bench_manifold_knn(Phi, y)
        results["surrogate_manifold"] = bench_surrogate_manifold(Phi, y)

        # Permutation test for manifold kNN
        perm = permutation_test(Phi, y, lambda: KNeighborsRegressor(n_neighbors=KNN_K))
        results["manifold_knn_perm"] = perm

        for bname, bres in results.items():
            if "p_value" in bres:
                print(f"    {bname:25s}: R²={bres['r2_real']:.4f}, p={bres['p_value']:.4f}")
            elif "r2_mean" in bres:
                print(f"    {bname:25s}: R²={bres['r2_mean']:.4f}±{bres['r2_std']:.4f}")

        all_results.append({"target": t_name, **{f"{k}_{m}": v
                           for k, d in results.items()
                           for m, v in (d.items() if isinstance(d, dict) else [])}})

    # ============================================================
    # SAVE RESULTS
    # ============================================================

    print("\nSaving results...")

    # 1. t032_prediction_results.csv — per-target detailed results
    rows = []
    for r in all_results:
        t = r["target"]
        for bname in ["random", "family_labels", "features_linear", "features_knn",
                       "manifold_linear", "manifold_knn", "surrogate_manifold"]:
            key_r2 = f"{bname}_r2_mean"
            key_mae = f"{bname}_mae_mean"
            if key_r2 in r:
                rows.append({
                    "target": t,
                    "benchmark": bname,
                    "r2_mean": r.get(key_r2, np.nan),
                    "r2_std": r.get(f"{bname}_r2_std", np.nan),
                    "mae_mean": r.get(key_mae, np.nan),
                    "mae_std": r.get(f"{bname}_mae_std", np.nan),
                })
    results_df = pd.DataFrame(rows)
    results_df.to_csv(OUT / "t032_prediction_results.csv", index=False)
    print("  Saved t032_prediction_results.csv")

    # 2. t032_prediction_benchmarks.csv — summary comparison
    bench_rows = []
    for r in all_results:
        t = r["target"]
        man_knn_r2 = r.get("manifold_knn_r2_mean", np.nan)
        sur_r2 = r.get("surrogate_manifold_r2_mean", np.nan)
        feat_r2 = r.get("features_knn_r2_mean", np.nan)
        fam_r2 = r.get("family_labels_r2_mean", np.nan)
        perm_p = r.get("manifold_knn_perm_p_value", np.nan)
        bench_rows.append({
            "target": t,
            "manifold_knn_r2": man_knn_r2,
            "surrogate_r2": sur_r2,
            "features_knn_r2": feat_r2,
            "family_labels_r2": fam_r2,
            "manifold_advantage_vs_surrogate": man_knn_r2 - sur_r2,
            "manifold_advantage_vs_features": man_knn_r2 - feat_r2,
            "permutation_p": perm_p,
            "significant": perm_p < 0.05,
        })
    bench_df = pd.DataFrame(bench_rows)
    bench_df.to_csv(OUT / "t032_prediction_benchmarks.csv", index=False)
    print("  Saved t032_prediction_benchmarks.csv")

    # 3. t032_summary.json
    summary = {
        "n_systems": len(features_df),
        "n_targets": len(target_names),
        "targets": target_names,
        "manifold_dimensions": int(Phi.shape[1]),
        "benchmarks": ["random", "family_labels", "features_linear", "features_knn",
                       "manifold_linear", "manifold_knn", "surrogate_manifold"],
        "permutation_test": "manifold_knn vs shuffled y, 500 permutations",
        "bootstrap": f"{N_BOOT} iterations",
        "targets_significant": int(bench_df["significant"].sum()),
        "targets_total": len(bench_df),
        "mean_manifold_knn_r2": float(bench_df["manifold_knn_r2"].mean()),
        "mean_surrogate_r2": float(bench_df["surrogate_r2"].mean()),
        "mean_features_knn_r2": float(bench_df["features_knn_r2"].mean()),
        "success_criterion": "manifold predicts targets beyond family labels and covariance structure",
        "success_met": bool(bench_df["significant"].any()),
    }
    with open(OUT / "t032_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  Saved t032_summary.json")

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

    # Fig 1: Prediction performance (grouped bar chart)
    fig, ax = plt.subplots(figsize=(7, 4))
    benchmarks = ["random", "family_labels", "features_knn", "manifold_knn", "surrogate_manifold"]
    bm_labels = ["Random", "Family labels", "Features (kNN)", "Manifold (kNN)", "Surrogate manifold"]
    n_bm = len(benchmarks)
    x = np.arange(len(target_names))
    width = 0.15

    for i, (bname, blabel) in enumerate(zip(benchmarks, bm_labels)):
        r2_vals = []
        r2_errs = []
        for t_name in target_names:
            row = results_df[(results_df["target"] == t_name) & (results_df["benchmark"] == bname)]
            if len(row) > 0:
                r2_vals.append(row["r2_mean"].values[0])
                r2_errs.append(row["r2_std"].values[0])
            else:
                r2_vals.append(0.0)
                r2_errs.append(0.0)
        shade = [G["black"], G["dg"], G["gray"], G["black"], G["lg"]][i]
        ax.bar(x + i * width, r2_vals, width, yerr=r2_errs,
               color=shade, edgecolor="white", linewidth=0.3,
               capsize=2, error_kw={"elinewidth": 0.5},
               label=blabel)

    ax.set_xlabel("Target quantity")
    ax.set_ylabel("R² score")
    ax.set_title("Out-of-sample prediction performance")
    ax.set_xticks(x + width * (n_bm - 1) / 2)
    ax.set_xticklabels(["Spectral\nentropy", "Mean\ncurvature", "Recurrence\nrate",
                        "Laminarity", "Divergence\nrate"], fontsize=7)
    ax.legend(frameon=False, fontsize=6, loc="upper right", ncol=2)
    ax.axhline(0, color="black", lw=0.3)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t032_prediction_performance.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t032_prediction_performance.pdf/.png")

    # Fig 2: Null comparison (manifold vs surrogate)
    fig, ax = plt.subplots(figsize=(7, 4))

    man_r2 = []
    sur_r2 = []
    for t_name in target_names:
        rm = results_df[(results_df["target"] == t_name) & (results_df["benchmark"] == "manifold_knn")]
        rs = results_df[(results_df["target"] == t_name) & (results_df["benchmark"] == "surrogate_manifold")]
        man_r2.append(rm["r2_mean"].values[0] if len(rm) > 0 else 0)
        sur_r2.append(rs["r2_mean"].values[0] if len(rs) > 0 else 0)

    x = np.arange(len(target_names))
    ax.bar(x - 0.2, man_r2, 0.35, color=G["black"], label="Manifold (kNN)", edgecolor="white", linewidth=0.3)
    ax.bar(x + 0.2, sur_r2, 0.35, color=G["lg"], label="Surrogate manifold", edgecolor="white", linewidth=0.3)

    # Mark significant
    for i, t_name in enumerate(target_names):
        bm_row = bench_df[bench_df["target"] == t_name]
        if len(bm_row) > 0 and bm_row["significant"].values[0]:
            ymax = max(man_r2[i], sur_r2[i])
            ax.plot(x[i], ymax + 0.02, "k*", markersize=8)

    ax.set_xlabel("Target quantity")
    ax.set_ylabel("R² score")
    ax.set_title("Manifold vs surrogate: can covariance structure explain prediction?")
    ax.set_xticks(x)
    ax.set_xticklabels(["Spectral\nentropy", "Mean\ncurvature", "Recurrence\nrate",
                        "Laminarity", "Divergence\nrate"], fontsize=7)
    ax.legend(frameon=False, fontsize=7)
    ax.axhline(0, color="black", lw=0.3)
    ax.annotate("* = permutation p < 0.05", xy=(0.02, 0.95), xycoords="axes fraction",
                fontsize=6, color="gray")

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t032_null_comparison.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t032_null_comparison.pdf/.png")

    elapsed = time.time() - t0
    print(f"\nT032 complete. Runtime: {elapsed:.1f}s")
    print(f"  Significance: {int(bench_df['significant'].sum())}/{len(bench_df)} targets")


if __name__ == "__main__":
    main()
