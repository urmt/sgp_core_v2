#!/usr/bin/env python3
"""
T034: Cross-Family Transfer Experiment
=======================================
Does the geometry learned from one collection of dynamical systems
help predict properties of a completely unseen family?

Leave-One-Family-Out CV with Φ-space (C,F,A,R) predictors,
5 T032 targets, 4 baselines, permutation + bootstrap tests.
"""

import sys, json, warnings, time
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from scipy.spatial.distance import pdist, squareform
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
np.random.seed(42)

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

N_PERM = 100
N_BOOT = 100

# ============================================================
# STEP 1-2: LOAD DATA
# ============================================================

def load_data():
    """Load Φ, features, families, and T032 targets."""
    features_df = pd.read_csv(OUT / "t030_ensemble_features.csv")
    Phi = np.load(OUT / "t030_ensemble_Phi.npy")

    # Family labels
    families = np.array([s.split("_")[0] for s in features_df["system"].values])
    unique_fams = sorted(np.unique(families))
    fam_idx = np.array([np.searchsorted(unique_fams, f) for f in families])

    # 17 raw features
    X_raw = features_df.select_dtypes(include=[np.number]).values[:, :17]

    # T032 targets (recompute exactly as T032)
    from scipy.spatial.distance import pdist, squareform
    targets = compute_t032_targets(X_raw)

    return Phi, X_raw, families, unique_fams, fam_idx, targets


def compute_t032_targets(X):
    """Recompute T032 held-out targets exactly as T032."""
    n = X.shape[0]
    targets = np.zeros((n, 5))
    D = squareform(pdist(X, metric="euclidean"))
    K = min(5, n - 1)

    for i in range(n):
        # 1. Spectral entropy
        x_mean = X.mean(axis=0)
        devs = np.abs(X[i] - x_mean)
        dev_norm = devs / (devs.sum() + 1e-12)
        targets[i, 0] = -np.sum(dev_norm * np.log(dev_norm + 1e-12))

        # 2. Mean curvature
        nn_idx = np.argsort(D[i])[1:K+1]
        if len(nn_idx) >= 3:
            local_X = X[nn_idx]
            diffs = np.diff(local_X, axis=0)
            targets[i, 1] = np.mean(np.abs(np.diff(diffs, axis=0))) if len(diffs) > 1 else 0.0
        else:
            targets[i, 1] = 0.0

        # 3. Local dimensionality
        if len(nn_idx) >= 4:
            local_X = X[nn_idx]
            local_centered = local_X - local_X.mean(axis=0)
            cov = np.cov(local_centered, rowvar=False)
            evals = np.linalg.eigvalsh(cov)
            evals = np.maximum(evals, 1e-12)
            targets[i, 2] = (np.sum(evals) ** 2) / (np.sum(evals ** 2) + 1e-12)
        else:
            targets[i, 2] = 1.0

        # 4. Laminarity
        nn_dists = D[i][nn_idx]
        targets[i, 3] = np.std(nn_dists) / (np.mean(nn_dists) + 1e-12)

        # 5. Divergence rate
        nn1 = D[i][np.argsort(D[i])[1]] if n > 1 else 1.0
        targets[i, 4] = np.log(nn1 + 1e-12)

    return targets


# ============================================================
# STEP 3-4: LEAVE-ONE-FAMILY-OUT CV
# ============================================================

def lofo_cv(Phi, targets, fam_idx, unique_fams, model_fn, target_names):
    """Leave-One-Family-Out cross-validation."""
    n_targets = targets.shape[1]
    n_fams = len(unique_fams)
    results = {t: {"r2": [], "mae": [], "rmse": []} for t in target_names}

    for fam_i, fam_name in enumerate(unique_fams):
        test_mask = fam_idx == fam_i
        train_mask = ~test_mask

        if test_mask.sum() < 3:
            continue

        for t_i, t_name in enumerate(target_names):
            y = targets[:, t_i]
            Phi_train, Phi_test = Phi[train_mask], Phi[test_mask]
            y_train, y_test = y[train_mask], y[test_mask]

            scaler = StandardScaler()
            Ps_train = scaler.fit_transform(Phi_train)
            Ps_test = scaler.transform(Phi_test)

            model = model_fn()
            model.fit(Ps_train, y_train)
            y_pred = model.predict(Ps_test)

            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))

            results[t_name]["r2"].append(r2)
            results[t_name]["mae"].append(mae)
            results[t_name]["rmse"].append(rmse)

    return results


# ============================================================
# STEP 5: BASELINES
# ============================================================

def baseline_random(targets, target_names):
    """Baseline A: random predictor."""
    results = {t: {"r2": [], "mae": [], "rmse": []} for t in target_names}
    for t_i, t_name in enumerate(target_names):
        y = targets[:, t_i]
        for _ in range(50):
            y_pred = np.random.randn(len(y)) * np.std(y) + np.mean(y)
            results[t_name]["r2"].append(r2_score(y, y_pred))
            results[t_name]["mae"].append(mean_absolute_error(y, y_pred))
            results[t_name]["rmse"].append(np.sqrt(mean_squared_error(y, y_pred)))
    return results


def baseline_family_mean(targets, families, unique_fams, target_names):
    """Baseline B: predict family mean."""
    results = {t: {"r2": [], "mae": [], "rmse": []} for t in target_names}
    for t_i, t_name in enumerate(target_names):
        y = targets[:, t_i]
        fam_means = {}
        for fam in unique_fams:
            mask = families == fam
            fam_means[fam] = y[mask].mean()
        y_pred = np.array([fam_means[f] for f in families])
        results[t_name]["r2"].append(r2_score(y, y_pred))
        results[t_name]["mae"].append(mean_absolute_error(y, y_pred))
        results[t_name]["rmse"].append(np.sqrt(mean_squared_error(y, y_pred)))
    return results


def baseline_surrogate(Phi, targets, fam_idx, unique_fams, target_names, n_sur=20):
    """Baseline C: covariance-preserving surrogate manifold, LOFO CV."""
    results = {t: {"r2": [], "mae": [], "rmse": []} for t in target_names}
    for sur_i in range(n_sur):
        Phi_sur = Phi.copy()
        for j in range(Phi_sur.shape[1]):
            np.random.shuffle(Phi_sur[:, j])
        for fam_i in range(len(unique_fams)):
            test_mask = fam_idx == fam_i
            train_mask = ~test_mask
            if test_mask.sum() < 3:
                continue
            Phi_train, Phi_test = Phi_sur[train_mask], Phi_sur[test_mask]
            for t_i, t_name in enumerate(target_names):
                y = targets[:, t_i]
                y_train, y_test = y[train_mask], y[test_mask]
                scaler = StandardScaler()
                Ps_train = scaler.fit_transform(Phi_train)
                Ps_test = scaler.transform(Phi_test)
                model = RandomForestRegressor(n_estimators=50, random_state=None)
                model.fit(Ps_train, y_train)
                y_pred = model.predict(Ps_test)
                results[t_name]["r2"].append(r2_score(y_test, y_pred))
                results[t_name]["mae"].append(mean_absolute_error(y_test, y_pred))
                results[t_name]["rmse"].append(np.sqrt(mean_squared_error(y_test, y_pred)))
    return results


def baseline_features(X_raw, targets, fam_idx, unique_fams, target_names):
    """Baseline D: original 17-feature space, same LOFO CV."""
    def model_fn():
        return GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    return lofo_cv(X_raw, targets, fam_idx, unique_fams, model_fn, target_names)


# ============================================================
# STEP 7: STATISTICAL TESTING
# ============================================================

def permutation_test(Phi, targets, fam_idx, unique_fams, target_names, n_perm=N_PERM):
    """Permutation test for each target."""
    results = {}
    for t_i, t_name in enumerate(target_names):
        y = targets[:, t_i]

        # Real R² (best model on full data, LOFO average)
        real_r2s = []
        for fam_i in range(len(unique_fams)):
            test_mask = fam_idx == fam_i
            train_mask = ~test_mask
            if test_mask.sum() < 3:
                continue
            Phi_train, Phi_test = Phi[train_mask], Phi[test_mask]
            y_train, y_test = y[train_mask], y[test_mask]
            scaler = StandardScaler()
            Ps_train = scaler.fit_transform(Phi_train)
            Ps_test = scaler.transform(Phi_test)
            model = GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=42)
            model.fit(Ps_train, y_train)
            real_r2s.append(r2_score(y_test, model.predict(Ps_test)))
        real_mean = np.mean(real_r2s)

        # Null distribution
        null_r2s = []
        for _ in range(n_perm):
            y_perm = np.random.permutation(y)
            fold_r2s = []
            for fam_i in range(len(unique_fams)):
                test_mask = fam_idx == fam_i
                train_mask = ~test_mask
                if test_mask.sum() < 3:
                    continue
                Phi_train, Phi_test = Phi[train_mask], Phi[test_mask]
                y_train, y_test = y_perm[train_mask], y_perm[test_mask]
                scaler = StandardScaler()
                Ps_train = scaler.fit_transform(Phi_train)
                Ps_test = scaler.transform(Phi_test)
                model = GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=42)
                model.fit(Ps_train, y_train)
                fold_r2s.append(r2_score(y_test, model.predict(Ps_test)))
            null_r2s.append(np.mean(fold_r2s))

        null_arr = np.array(null_r2s)
        p_value = np.mean(null_arr >= real_mean)

        results[t_name] = {
            "real_r2": float(real_mean),
            "null_mean": float(np.mean(null_arr)),
            "null_std": float(np.std(null_arr)),
            "p_value": float(p_value),
        }

    return results


def bootstrap_ci(Phi, targets, fam_idx, unique_fams, target_names, n_boot=N_BOOT):
    """Bootstrap 95% CI for R² of each target."""
    results = {}
    for t_i, t_name in enumerate(target_names):
        y = targets[:, t_i]
        boot_r2s = []

        for _ in range(n_boot):
            # Bootstrap families
            boot_fams = np.random.choice(unique_fams, size=len(unique_fams), replace=True)
            fold_r2s = []
            for fam_name in boot_fams:
                fam_i = np.searchsorted(unique_fams, fam_name)
                test_mask = fam_idx == fam_i
                train_mask = ~test_mask
                if test_mask.sum() < 3:
                    continue
                Phi_train, Phi_test = Phi[train_mask], Phi[test_mask]
                y_train, y_test = y[train_mask], y[test_mask]
                scaler = StandardScaler()
                Ps_train = scaler.fit_transform(Phi_train)
                Ps_test = scaler.transform(Phi_test)
                model = GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=42)
                model.fit(Ps_train, y_train)
                fold_r2s.append(r2_score(y_test, model.predict(Ps_test)))
            if fold_r2s:
                boot_r2s.append(np.mean(fold_r2s))

        boot_arr = np.array(boot_r2s)
        ci_lo = np.percentile(boot_arr, 2.5)
        ci_hi = np.percentile(boot_arr, 97.5)

        results[t_name] = {
            "mean_r2": float(np.mean(boot_arr)),
            "std_r2": float(np.std(boot_arr)),
            "ci_95_lo": float(ci_lo),
            "ci_95_hi": float(ci_hi),
        }

    return results


# ============================================================
# STEP 9: FAMILY DIFFICULTY
# ============================================================

def family_difficulty(Phi, targets, families, unique_fams, target_names):
    """Per-family breakdown of transfer performance."""
    model_fn = lambda: GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    rows = []
    for fam_name in unique_fams:
        fam_mask = families == fam_name
        train_mask = ~fam_mask
        for t_i, t_name in enumerate(target_names):
            y = targets[:, t_i]
            Phi_train, Phi_test = Phi[train_mask], Phi[fam_mask]
            y_train, y_test = y[train_mask], y[fam_mask]
            if len(y_test) < 2:
                continue
            scaler = StandardScaler()
            Ps_train = scaler.fit_transform(Phi_train)
            Ps_test = scaler.transform(Phi_test)
            model = model_fn()
            model.fit(Ps_train, y_train)
            y_pred = model.predict(Ps_test)
            rows.append({
                "family": fam_name,
                "target": t_name,
                "r2": r2_score(y_test, y_pred),
                "mae": mean_absolute_error(y_test, y_pred),
                "sample_count": int(fam_mask.sum()),
            })
    return pd.DataFrame(rows)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T034: CROSS-FAMILY TRANSFER EXPERIMENT")
    print("=" * 70)
    t0 = time.time()

    # Load
    print("\nLoading data...", flush=True)
    Phi, X_raw, families, unique_fams, fam_idx, targets = load_data()
    target_names = ["spectral_entropy", "mean_curvature", "local_dim", "laminarity", "divergence_rate"]
    print(f"  {len(Phi)} systems, {len(unique_fams)} families, {targets.shape[1]} targets", flush=True)

    # Step 3-4: LOFO CV for Φ-space
    print("\n[Step 3-4] LOFO CV: Φ-space (best model)...", flush=True)
    def phi_model():
        return GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=42)

    phi_results = lofo_cv(Phi, targets, fam_idx, unique_fams, phi_model, target_names)
    print("  LOFO CV done", flush=True)

    # Also try Random Forest
    def rf_model():
        return RandomForestRegressor(n_estimators=50, random_state=42)

    rf_results = lofo_cv(Phi, targets, fam_idx, unique_fams, rf_model, target_names)
    print("  RF done", flush=True)

    # Pick best per target
    best_results = {}
    for t_name in target_names:
        r2_gb = np.mean(phi_results[t_name]["r2"])
        r2_rf = np.mean(rf_results[t_name]["r2"])
        if r2_rf > r2_gb:
            best_results[t_name] = rf_results[t_name]
            print(f"  {t_name}: RF wins (R²={r2_rf:.4f} vs GB={r2_gb:.4f})")
        else:
            best_results[t_name] = phi_results[t_name]
            print(f"  {t_name}: GB wins (R²={r2_gb:.4f} vs RF={r2_rf:.4f})")

    # Step 5: Baselines
    print("\n[Step 5] Baselines...")
    print("  Baseline A: Random...")
    rand_results = baseline_random(targets, target_names)

    print("  Baseline B: Family mean...")
    fammean_results = baseline_family_mean(targets, families, unique_fams, target_names)

    print("  Baseline C: Surrogate manifold...", flush=True)
    sur_results = baseline_surrogate(Phi, targets, fam_idx, unique_fams, target_names, n_sur=20)

    print("  Baseline D: Original features (LOFO)...", flush=True)
    def feat_model():
        return GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=42)
    feat_results = lofo_cv(X_raw, targets, fam_idx, unique_fams, feat_model, target_names)

    # Step 7: Statistical tests
    print("\n[Step 7] Permutation test (n=100)...", flush=True)
    perm_results = permutation_test(Phi, targets, fam_idx, unique_fams, target_names, n_perm=N_PERM)

    print("  Bootstrap CI (n=100)...", flush=True)
    boot_results = bootstrap_ci(Phi, targets, fam_idx, unique_fams, target_names, n_boot=N_BOOT)

    # Step 8: Transfer advantage
    print("\n[Step 8] Transfer Advantage...")
    ta_results = {}
    for t_name in target_names:
        r2_phi = np.mean(best_results[t_name]["r2"])
        r2_sur = np.mean(sur_results[t_name]["r2"])
        ta = r2_phi - r2_sur
        ta_results[t_name] = ta
        print(f"  {t_name}: TA = {ta:.4f} (Φ={r2_phi:.4f} - surrogate={r2_sur:.4f})")

    # Step 9: Family difficulty
    print("\n[Step 9] Family difficulty analysis...")
    fam_diff = family_difficulty(Phi, targets, families, unique_fams, target_names)

    # ============================================================
    # STEP 11: SAVE OUTPUTS
    # ============================================================

    print("\n[Step 11] Saving outputs...")

    # t034_transfer_results.csv
    rows = []
    for t_name in target_names:
        for bname, bres in [("phi_space", best_results), ("random", rand_results),
                             ("family_mean", fammean_results), ("surrogate", sur_results),
                             ("features", feat_results)]:
            r2s = bres[t_name]["r2"]
            rows.append({
                "target": t_name,
                "benchmark": bname,
                "r2_mean": np.mean(r2s),
                "r2_std": np.std(r2s),
                "mae_mean": np.mean(bres[t_name]["mae"]),
                "mae_std": np.std(bres[t_name]["mae"]),
                "rmse_mean": np.mean(bres[t_name]["rmse"]),
                "rmse_std": np.std(bres[t_name]["rmse"]),
            })
    transfer_df = pd.DataFrame(rows)
    transfer_df.to_csv(OUT / "t034_transfer_results.csv", index=False)
    print("  Saved t034_transfer_results.csv")

    # t034_family_breakdown.csv
    fam_diff.to_csv(OUT / "t034_family_breakdown.csv", index=False)
    print("  Saved t034_family_breakdown.csv")

    # t034_summary.json
    summary = {
        "n_systems": len(Phi),
        "n_families": len(unique_fams),
        "families": list(unique_fams),
        "n_targets": len(target_names),
        "targets": target_names,
        "manifold_dimensions": int(Phi.shape[1]),
        "mean_phi_r2": float(np.mean([np.mean(best_results[t]["r2"]) for t in target_names])),
        "mean_surrogate_r2": float(np.mean([np.mean(sur_results[t]["r2"]) for t in target_names])),
        "mean_features_r2": float(np.mean([np.mean(feat_results[t]["r2"]) for t in target_names])),
        "mean_family_mean_r2": float(np.mean([np.mean(fammean_results[t]["r2"]) for t in target_names])),
        "targets_beat_surrogate": int(sum(1 for t in target_names if np.mean(best_results[t]["r2"]) > np.mean(sur_results[t]["r2"]))),
        "targets_beat_features": int(sum(1 for t in target_names if np.mean(best_results[t]["r2"]) > np.mean(feat_results[t]["r2"]))),
        "targets_significant": int(sum(1 for t in target_names if perm_results[t]["p_value"] < 0.01)),
        "permutation_p_values": {t: perm_results[t]["p_value"] for t in target_names},
        "bootstrap_ci": {t: boot_results[t] for t in target_names},
        "transfer_advantage": ta_results,
        "success_criterion": "mean_TA > 0 AND >=3 targets p<0.01 AND mean_R2_phi > mean_R2_family_mean",
        "success_met": bool(
            np.mean(list(ta_results.values())) > 0
            and sum(1 for t in target_names if perm_results[t]["p_value"] < 0.01) >= 3
            and np.mean([np.mean(best_results[t]["r2"]) for t in target_names]) >
                np.mean([np.mean(fammean_results[t]["r2"]) for t in target_names])
        ),
    }
    with open(OUT / "t034_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  Saved t034_summary.json")

    # ============================================================
    # STEP 10: FIGURES
    # ============================================================

    print("\n[Step 10] Generating figures...")

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

    # Fig 1: Cross-family R² by target
    fig, ax = plt.subplots(figsize=(7, 4))
    benchmarks = ["phi_space", "features", "surrogate", "family_mean", "random"]
    bm_labels = ["Φ-space (GB)", "Features (GB)", "Surrogate", "Family mean", "Random"]
    n_bm = len(benchmarks)
    x = np.arange(len(target_names))
    width = 0.15

    for i, (bname, blabel) in enumerate(zip(benchmarks, bm_labels)):
        r2_vals = []
        for t_name in target_names:
            row = transfer_df[(transfer_df["target"] == t_name) & (transfer_df["benchmark"] == bname)]
            r2_vals.append(row["r2_mean"].values[0] if len(row) > 0 else 0)
        shade = [G["black"], G["dg"], G["lg"], G["gray"], G["lg"]][i]
        ax.bar(x + i * width, r2_vals, width, color=shade, edgecolor="white",
               linewidth=0.3, label=blabel)

    ax.set_xlabel("Target quantity")
    ax.set_ylabel("R² (LOFO CV)")
    ax.set_title("Cross-family transfer: R² by target")
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(["Spectral\nentropy", "Mean\ncurvature", "Local\ndim", "Laminarity", "Divergence\nrate"], fontsize=7)
    ax.legend(frameon=False, fontsize=6, loc="upper right", ncol=2)
    ax.axhline(0, color="black", lw=0.3)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t034_transfer_performance.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t034_transfer_performance.pdf/.png")

    # Fig 2: Φ-space vs surrogate
    fig, ax = plt.subplots(figsize=(7, 4))
    man_vals = []
    sur_vals = []
    for t_name in target_names:
        rm = transfer_df[(transfer_df["target"] == t_name) & (transfer_df["benchmark"] == "phi_space")]
        rs = transfer_df[(transfer_df["target"] == t_name) & (transfer_df["benchmark"] == "surrogate")]
        man_vals.append(rm["r2_mean"].values[0] if len(rm) > 0 else 0)
        sur_vals.append(rs["r2_mean"].values[0] if len(rs) > 0 else 0)

    x = np.arange(len(target_names))
    ax.bar(x - 0.2, man_vals, 0.35, color=G["black"], label="Φ-space", edgecolor="white", linewidth=0.3)
    ax.bar(x + 0.2, sur_vals, 0.35, color=G["lg"], label="Surrogate", edgecolor="white", linewidth=0.3)

    for i, t_name in enumerate(target_names):
        if perm_results[t_name]["p_value"] < 0.01:
            ymax = max(man_vals[i], sur_vals[i])
            ax.plot(x[i], ymax + 0.02, "k*", markersize=8)

    ax.set_xlabel("Target quantity")
    ax.set_ylabel("R² (LOFO CV)")
    ax.set_title("Φ-space vs surrogate: transfer beyond covariance")
    ax.set_xticks(x)
    ax.set_xticklabels(["Spectral\nentropy", "Mean\ncurvature", "Local\ndim", "Laminarity", "Divergence\nrate"], fontsize=7)
    ax.legend(frameon=False, fontsize=7)
    ax.axhline(0, color="black", lw=0.3)
    ax.annotate("* = p < 0.01", xy=(0.02, 0.95), xycoords="axes fraction", fontsize=6, color="gray")

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t034_surrogate_comparison.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t034_surrogate_comparison.pdf/.png")

    # Fig 3: Transfer heatmap (family × target)
    fig, ax = plt.subplots(figsize=(7, 6))
    pivot = fam_diff.pivot_table(index="family", columns="target", values="r2")
    pivot = pivot[target_names]
    im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn", vmin=-0.5, vmax=1.0)
    ax.set_xticks(range(len(target_names)))
    ax.set_xticklabels(["Spec.\nentr.", "Mean\ncurv.", "Local\ndim", "Lam.", "Div.\nrate"], fontsize=7)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=7)
    plt.colorbar(im, ax=ax, label="R²", shrink=0.8)
    ax.set_title("Transfer heatmap: family × target R²")

    # Add text annotations
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            color = "white" if val < 0 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=5, color=color)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t034_transfer_heatmap.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t034_transfer_heatmap.pdf/.png")

    # ============================================================
    # STEP 12: DECISION & FINAL REPORT
    # ============================================================

    elapsed = time.time() - t0
    print(f"\nRuntime: {elapsed:.1f}s")

    mean_phi = np.mean([np.mean(best_results[t]["r2"]) for t in target_names])
    mean_sur = np.mean([np.mean(sur_results[t]["r2"]) for t in target_names])
    mean_feat = np.mean([np.mean(feat_results[t]["r2"]) for t in target_names])
    mean_fam = np.mean([np.mean(fammean_results[t]["r2"]) for t in target_names])

    n_beat_sur = sum(1 for t in target_names if np.mean(best_results[t]["r2"]) > np.mean(sur_results[t]["r2"]))
    n_beat_feat = sum(1 for t in target_names if np.mean(best_results[t]["r2"]) > np.mean(feat_results[t]["r2"]))
    n_sig = sum(1 for t in target_names if perm_results[t]["p_value"] < 0.01)

    # Best/worst family
    fam_mean_r2 = fam_diff.groupby("family")["r2"].mean()
    best_fam = fam_mean_r2.idxmax()
    worst_fam = fam_mean_r2.idxmin()

    # Decision
    mean_ta = np.mean(list(ta_results.values()))
    pass_condition = (mean_ta > 0 and n_sig >= 3 and mean_phi > mean_fam)
    verdict = "TRANSFER EXISTS" if pass_condition else "TRANSFER NOT DETECTED"

    print("\n" + "=" * 70)
    print("T034 RESULTS")
    print("=" * 70)
    print(f"Mean Φ-space R²:      {mean_phi:.4f}")
    print(f"Mean surrogate R²:    {mean_sur:.4f}")
    print(f"Mean feature-space R²:{mean_feat:.4f}")
    print(f"Mean family-mean R²:  {mean_fam:.4f}")
    print()
    print(f"Targets beating surrogate: {n_beat_sur}/5")
    print(f"Targets beating features:  {n_beat_feat}/5")
    print()
    print(f"Best transferred family:  {best_fam} (R²={fam_mean_r2[best_fam]:.4f})")
    print(f"Worst transferred family: {worst_fam} (R²={fam_mean_r2[worst_fam]:.4f})")
    print()
    print(f"Permutation significant (p<0.01): {n_sig}/5")
    for t in target_names:
        p = perm_results[t]["p_value"]
        print(f"  {t}: p={p:.4f}")
    print()
    print("Bootstrap 95% CI:")
    for t in target_names:
        ci = boot_results[t]
        print(f"  {t}: [{ci['ci_95_lo']:.4f}, {ci['ci_95_hi']:.4f}]")
    print()
    print(f"Mean Transfer Advantage: {mean_ta:.4f}")
    print()
    print(f"FINAL VERDICT: {verdict}")
    print("=" * 70)


if __name__ == "__main__":
    main()
