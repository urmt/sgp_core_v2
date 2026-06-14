#!/usr/bin/env python3
"""
T035: Cross-Family Invariant Relationship Search
=================================================
T034 showed Φ-space does NOT transfer across unseen families.

T035 determines whether any mathematical RELATIONSHIPS survive
family boundaries even when the coordinate system itself does not.

Uses existing T031-T034 outputs only.
"""

import sys, json, warnings, time, itertools
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from scipy.stats import pearsonr
from scipy.spatial.distance import pdist, squareform
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
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

N_PERM = 200
N_BOOT = 200

# ============================================================
# STEP 1-2: BUILD VARIABLE POOL
# ============================================================

def build_variable_pool():
    """Build complete variable pool from existing outputs."""
    f = pd.read_csv(OUT / "t030_ensemble_features.csv")
    Phi = np.load(OUT / "t030_ensemble_Phi.npy")

    families = np.array([s.split("_")[0] for s in f["system"].values])
    unique_fams = sorted(np.unique(families))
    fam_idx = np.array([np.searchsorted(unique_fams, fi) for fi in families])

    # 17 raw features
    raw_names = ["pc1", "pc2", "effective_rank", "tau_m1", "tau_m2", "tau_m3", "tau_m4",
                 "temporal_corr", "phase_corr", "pc1_ratio", "replay_displacement",
                 "abl_full_pc1", "abl_no_m1_pc1", "abl_no_m2_pc1", "abl_no_m3_pc1",
                 "abl_no_m4_pc1", "m2_contribution"]
    X_raw = f[raw_names].values.astype(float)

    # Phi coordinates
    phi_names = ["C", "F", "A", "R"]

    # Derived quantities
    from scipy.spatial.distance import pdist, squareform
    D = squareform(pdist(X_raw, metric="euclidean"))

    # PR (participation ratio of raw features)
    cov = np.cov(X_raw, rowvar=False)
    evals = np.linalg.eigvalsh(cov)
    evals = np.maximum(evals, 1e-12)
    pr = (np.sum(evals) ** 2) / (np.sum(evals ** 2))

    # effective_rank (already in features)
    er = f["effective_rank"].values

    # spectral_entropy
    x_mean = X_raw.mean(axis=0)
    devs = np.abs(X_raw - x_mean)
    dev_norm = devs / (devs.sum(axis=1, keepdims=True) + 1e-12)
    spectral_entropy = -np.sum(dev_norm * np.log(dev_norm + 1e-12), axis=1)

    # mean_curvature (per-system)
    n = len(X_raw)
    K = min(5, n - 1)
    mean_curvature = np.zeros(n)
    local_dim = np.zeros(n)
    laminarity = np.zeros(n)
    divergence_rate = np.zeros(n)

    for i in range(n):
        nn_idx = np.argsort(D[i])[1:K+1]
        if len(nn_idx) >= 3:
            local_X = X_raw[nn_idx]
            diffs = np.diff(local_X, axis=0)
            mean_curvature[i] = np.mean(np.abs(np.diff(diffs, axis=0))) if len(diffs) > 1 else 0.0
        if len(nn_idx) >= 4:
            local_X = X_raw[nn_idx]
            local_centered = local_X - local_X.mean(axis=0)
            local_cov = np.cov(local_centered, rowvar=False)
            local_evals = np.linalg.eigvalsh(local_cov)
            local_evals = np.maximum(local_evals, 1e-12)
            local_dim[i] = (np.sum(local_evals) ** 2) / (np.sum(local_evals ** 2) + 1e-12)
        nn_dists = D[i][nn_idx]
        laminarity[i] = np.std(nn_dists) / (np.mean(nn_dists) + 1e-12)
        nn1 = D[i][np.argsort(D[i])[1]] if n > 1 else 1.0
        divergence_rate[i] = np.log(nn1 + 1e-12)

    # Assemble all variables
    all_vars = np.column_stack([
        X_raw,  # 17
        Phi,    # 4 (C,F,A,R)
        np.full(n, pr),  # 1
        er,     # 1
        spectral_entropy,  # 1
        mean_curvature,    # 1
        local_dim,         # 1
        laminarity,        # 1
        divergence_rate,   # 1
    ])

    all_names = raw_names + phi_names + ["PR", "effective_rank", "spectral_entropy",
                                          "mean_curvature", "local_dim", "laminarity",
                                          "divergence_rate"]

    print(f"  Variable pool: {all_vars.shape[1]} variables, {n} systems, {len(unique_fams)} families")
    return all_vars, all_names, families, unique_fams, fam_idx


# ============================================================
# STEP 3: RELATIONSHIP FITTING
# ============================================================

def fit_relationship(X, Y, model_type):
    """Fit a single relationship X -> Y with given model type."""
    valid = np.isfinite(X) & np.isfinite(Y)
    Xv, Yv = X[valid], Y[valid]
    if len(Xv) < 10:
        return None, None

    try:
        if model_type == "linear":
            coef = np.polyfit(Xv, Yv, 1)
            Y_pred = np.polyval(coef, Xv)
        elif model_type == "power":
            pos = Xv > 0
            if pos.sum() < 10:
                return None, None
            logX = np.log(Xv[pos])
            logY = np.log(np.abs(Yv[pos]) + 1e-12)
            coef = np.polyfit(logX, logY, 1)
            Y_pred = np.polyval(coef, np.log(np.abs(Xv[pos]) + 1e-12))
            Xv, Yv = Xv[pos], Yv[pos]
        elif model_type == "log":
            pos = Xv > 0
            if pos.sum() < 10:
                return None, None
            logX = np.log(Xv[pos])
            coef = np.polyfit(logX, Yv[pos], 1)
            Y_pred = np.polyval(coef, logX)
            Xv, Yv = Xv[pos], Yv[pos]
        elif model_type == "exponential":
            pos = Yv > 0
            if pos.sum() < 10:
                return None, None
            logY = np.log(Yv[pos])
            coef = np.polyfit(Xv[pos], logY, 1)
            Y_pred = np.exp(np.polyval(coef, Xv[pos]))
            Xv, Yv = Xv[pos], Yv[pos]
        elif model_type == "rf":
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(Xv.reshape(-1, 1), Yv)
            Y_pred = model.predict(Xv.reshape(-1, 1))
        else:
            return None, None

        r2 = r2_score(Yv, Y_pred)
        mae = mean_absolute_error(Yv, Y_pred)
        return r2, mae
    except Exception:
        return None, None


def get_slope(X, Y, model_type):
    """Extract slope for parametric models."""
    valid = np.isfinite(X) & np.isfinite(Y)
    Xv, Yv = X[valid], Y[valid]
    if len(Xv) < 10:
        return np.nan

    if model_type == "linear":
        coef = np.polyfit(Xv, Yv, 1)
        return coef[0]
    elif model_type == "power":
        pos = Xv > 0
        if pos.sum() < 10:
            return np.nan
        coef = np.polyfit(np.log(Xv[pos]), np.log(np.abs(Yv[pos]) + 1e-12), 1)
        return coef[0]
    elif model_type == "log":
        pos = Xv > 0
        if pos.sum() < 10:
            return np.nan
        coef = np.polyfit(np.log(Xv[pos]), Yv[pos], 1)
        return coef[0]
    elif model_type == "exponential":
        pos = Yv > 0
        if pos.sum() < 10:
            return np.nan
        coef = np.polyfit(Xv[pos], np.log(Yv[pos]), 1)
        return coef[0]
    return np.nan


# ============================================================
# STEP 4-6: FAMILY-BY-FAMILY + POOLED + INVARIANCE
# ============================================================

def evaluate_relationship(all_vars, all_names, xi, yi, families, unique_fams, fam_idx):
    """Full evaluation of one X->Y relationship."""
    X = all_vars[:, xi]
    Y = all_vars[:, yi]
    x_name = all_names[xi]
    y_name = all_names[yi]

    results = {
        "X": x_name, "Y": y_name,
        "family_r2": {}, "family_mae": {}, "family_slope": {},
        "pooled_r2": {}, "pooled_mae": {},
        "invariance_score": np.nan,
        "cv_slope": np.nan,
        "mean_transfer_r2": np.nan,
    }

    # Test all model types
    best_model = None
    best_pooled_r2 = -np.inf

    for model_type in ["linear", "power", "log", "exponential", "rf"]:
        # Pooled fit
        r2, mae = fit_relationship(X, Y, model_type)
        if r2 is None:
            continue

        if r2 > best_pooled_r2:
            best_pooled_r2 = r2
            best_model = model_type

    if best_model is None:
        return None

    # Family-by-family fit
    slopes = []
    fam_r2s = []
    for fam_i, fam_name in enumerate(unique_fams):
        mask = fam_idx == fam_i
        if mask.sum() < 5:
            continue
        r2, mae = fit_relationship(X[mask], Y[mask], best_model)
        slope = get_slope(X[mask], Y[mask], best_model)
        if r2 is not None:
            fam_r2s.append(r2)
            slopes.append(slope)

    if len(fam_r2s) < 3:
        return None

    # Pooled fit (recompute with best model)
    pooled_r2, pooled_mae = fit_relationship(X, Y, best_model)
    if pooled_r2 is None:
        return None

    # Invariance score
    mean_fam_r2 = np.mean(fam_r2s)
    invariance = pooled_r2 / max(abs(mean_fam_r2), 1e-12) if mean_fam_r2 > 0 else np.nan

    # CV slope
    valid_slopes = [s for s in slopes if np.isfinite(s)]
    if len(valid_slopes) >= 3:
        cv_slope = np.std(valid_slopes) / max(abs(np.mean(valid_slopes)), 1e-12)
    else:
        cv_slope = np.nan

    # LOFO transfer
    transfer_r2s = []
    for fam_i in range(len(unique_fams)):
        test_mask = fam_idx == fam_i
        train_mask = ~test_mask
        if test_mask.sum() < 3 or train_mask.sum() < 10:
            continue
        X_train, X_test = X[train_mask], X[test_mask]
        Y_train, Y_test = Y[train_mask], Y[test_mask]
        r2_train, _ = fit_relationship(X_train, Y_train, best_model)
        if r2_train is None:
            continue
        # Apply training model to test
        if best_model == "linear":
            coef = np.polyfit(X_train, Y_train, 1)
            Y_pred = np.polyval(coef, X_test)
        elif best_model == "power":
            pos = X_train > 0
            pos_test = X_test > 0
            if pos.sum() < 10 or pos_test.sum() < 3:
                continue
            coef = np.polyfit(np.log(X_train[pos]), np.log(np.abs(Y_train[pos]) + 1e-12), 1)
            Y_pred = np.exp(np.polyval(coef, np.log(np.abs(X_test[pos_test]) + 1e-12)))
            Y_test = Y_test[pos_test]
        elif best_model == "log":
            pos = X_train > 0
            pos_test = X_test > 0
            if pos.sum() < 10 or pos_test.sum() < 3:
                continue
            coef = np.polyfit(np.log(X_train[pos]), Y_train[pos], 1)
            Y_pred = np.polyval(coef, np.log(X_test[pos_test]))
            Y_test = Y_test[pos_test]
        elif best_model == "exponential":
            pos = Y_train > 0
            pos_test = Y_test > 0
            if pos.sum() < 10 or pos_test.sum() < 3:
                continue
            coef = np.polyfit(X_train[pos], np.log(Y_train[pos]), 1)
            Y_pred = np.exp(np.polyval(coef, X_test[pos_test]))
            Y_test = Y_test[pos_test]
        elif best_model == "rf":
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X_train.reshape(-1, 1), Y_train)
            Y_pred = model.predict(X_test.reshape(-1, 1))

        if len(Y_test) > 0 and np.std(Y_test) > 0:
            transfer_r2s.append(r2_score(Y_test, Y_pred))

    mean_transfer_r2 = np.mean(transfer_r2s) if transfer_r2s else np.nan

    results["model"] = best_model
    results["pooled_r2"] = float(pooled_r2)
    results["pooled_mae"] = float(pooled_mae)
    results["invariance_score"] = float(invariance) if np.isfinite(invariance) else 0.0
    results["cv_slope"] = float(cv_slope) if np.isfinite(cv_slope) else 1.0
    results["mean_transfer_r2"] = float(mean_transfer_r2) if np.isfinite(mean_transfer_r2) else 0.0
    results["family_r2s"] = [float(r) for r in fam_r2s]
    results["slopes"] = [float(s) for s in valid_slopes]

    return results


# ============================================================
# STEP 7-8: PERMUTATION + BOOTSTRAP
# ============================================================

def permutation_test(all_vars, all_names, xi, yi, families, unique_fams, fam_idx, model_type, n_perm=N_PERM):
    """Permutation test for one relationship."""
    X = all_vars[:, xi]
    Y = all_vars[:, yi]

    r2_real, _ = fit_relationship(X, Y, model_type)
    if r2_real is None:
        return 1.0

    r2_null = []
    for _ in range(n_perm):
        Y_perm = np.random.permutation(Y)
        r2, _ = fit_relationship(X, Y_perm, model_type)
        if r2 is not None:
            r2_null.append(r2)

    if not r2_null:
        return 1.0

    return float(np.mean(np.array(r2_null) >= r2_real))


def bootstrap_ci(all_vars, all_names, xi, yi, families, unique_fams, fam_idx, model_type, n_boot=N_BOOT):
    """Bootstrap 95% CI for pooled R²."""
    X = all_vars[:, xi]
    Y = all_vars[:, yi]

    boot_r2s = []
    for _ in range(n_boot):
        idx = np.random.choice(len(X), len(X), replace=True)
        r2, _ = fit_relationship(X[idx], Y[idx], model_type)
        if r2 is not None:
            boot_r2s.append(r2)

    if not boot_r2s:
        return {"mean": 0, "ci_lo": 0, "ci_hi": 0}

    arr = np.array(boot_r2s)
    return {
        "mean": float(np.mean(arr)),
        "ci_lo": float(np.percentile(arr, 2.5)),
        "ci_hi": float(np.percentile(arr, 97.5)),
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T035: CROSS-FAMILY INVARIANT RELATIONSHIP SEARCH")
    print("=" * 70)
    t0 = time.time()

    # Step 1-2: Build variable pool
    print("\n[Step 1-2] Building variable pool...")
    all_vars, all_names, families, unique_fams, fam_idx = build_variable_pool()

    # Step 3-6: Evaluate all variable pairs
    print("\n[Step 3-6] Evaluating all variable pairs...")
    n_vars = all_vars.shape[1]
    all_pairs = list(itertools.combinations(range(n_vars), 2))
    print(f"  Total pairs: {len(all_pairs)}")

    all_results = []
    for pi, (xi, yi) in enumerate(all_pairs):
        if pi % 100 == 0:
            print(f"  Progress: {pi}/{len(all_pairs)}", flush=True)
        # Skip self-relationships
        if xi == yi:
            continue
        # Skip duplicate variable names (e.g., effective_rank appears twice)
        if all_names[xi] == all_names[yi]:
            continue
        res = evaluate_relationship(all_vars, all_names, xi, yi, families, unique_fams, fam_idx)
        if res is not None:
            all_results.append(res)

    print(f"  Valid relationships: {len(all_results)}")

    # Step 7: Permutation test for top candidates
    print("\n[Step 7] Permutation tests (top 50)...")
    all_results.sort(key=lambda r: r["pooled_r2"], reverse=True)
    top50 = all_results[:50]

    for i, res in enumerate(top50):
        xi = all_names.index(res["X"])
        yi = all_names.index(res["Y"])
        res["permutation_p"] = permutation_test(all_vars, all_names, xi, yi,
                                                 families, unique_fams, fam_idx, res["model"])
        if i % 10 == 0:
            print(f"  Permutation {i+1}/50 done", flush=True)

    # Step 8: Bootstrap for top 20
    print("\n[Step 8] Bootstrap CIs (top 20)...")
    top20 = all_results[:20]

    for i, res in enumerate(top20):
        xi = all_names.index(res["X"])
        yi = all_names.index(res["Y"])
        res["bootstrap_ci"] = bootstrap_ci(all_vars, all_names, xi, yi,
                                            families, unique_fams, fam_idx, res["model"])

    # Step 9: Compute final ranking score
    print("\n[Step 9] Computing ranking scores...")
    for res in all_results:
        inv = res["invariance_score"] if np.isfinite(res["invariance_score"]) else 0
        inv = max(0, min(2, inv))  # clip to [0,2]
        inv_norm = inv / 2.0  # normalize to [0,1]

        transfer = res["mean_transfer_r2"] if np.isfinite(res["mean_transfer_r2"]) else 0
        transfer_norm = max(0, min(1, (transfer + 1) / 2.0))  # map [-1,1] to [0,1]

        cv = res["cv_slope"] if np.isfinite(res["cv_slope"]) else 1
        cv_norm = max(0, min(1, 1 - min(cv, 2) / 2.0))  # lower is better

        pooled = res["pooled_r2"] if np.isfinite(res["pooled_r2"]) else 0
        pooled_norm = max(0, min(1, (pooled + 1) / 2.0))  # map [-1,1] to [0,1]

        res["ranking_score"] = (0.40 * inv_norm + 0.30 * transfer_norm +
                                 0.20 * cv_norm + 0.10 * pooled_norm)

    all_results.sort(key=lambda r: r["ranking_score"], reverse=True)

    # ============================================================
    # STEP 10: SAVE OUTPUTS
    # ============================================================

    print("\n[Step 10] Saving outputs...")

    # t035_invariant_relationships.csv (all valid)
    rows = []
    for r in all_results:
        rows.append({
            "X": r["X"], "Y": r["Y"], "model": r["model"],
            "pooled_r2": r["pooled_r2"], "pooled_mae": r["pooled_mae"],
            "invariance_score": r["invariance_score"],
            "cv_slope": r["cv_slope"],
            "mean_transfer_r2": r["mean_transfer_r2"],
            "ranking_score": r["ranking_score"],
            "permutation_p": r.get("permutation_p", np.nan),
        })
    inv_df = pd.DataFrame(rows)
    inv_df.to_csv(OUT / "t035_invariant_relationships.csv", index=False)
    print(f"  Saved t035_invariant_relationships.csv ({len(inv_df)} rows)")

    # t035_top20.csv
    top20_rows = []
    for rank, r in enumerate(top20, 1):
        ci = r.get("bootstrap_ci", {})
        top20_rows.append({
            "Rank": rank,
            "X": r["X"],
            "Y": r["Y"],
            "Model": r["model"],
            "Pooled_R2": r["pooled_r2"],
            "MeanTransfer_R2": r["mean_transfer_r2"],
            "InvarianceScore": r["invariance_score"],
            "CV_slope": r["cv_slope"],
            "Permutation_p": r.get("permutation_p", np.nan),
            "Bootstrap_CI_lo": ci.get("ci_lo", np.nan),
            "Bootstrap_CI_hi": ci.get("ci_hi", np.nan),
            "RankingScore": r["ranking_score"],
        })
    top20_df = pd.DataFrame(top20_rows)
    top20_df.to_csv(OUT / "t035_top20.csv", index=False)
    print("  Saved t035_top20.csv")

    # t035_family_stability.csv
    fam_rows = []
    for r in all_results[:50]:
        for fi, fam_name in enumerate(unique_fams):
            fam_r2s = r.get("family_r2s", [])
            if fi < len(fam_r2s):
                fam_rows.append({
                    "X": r["X"], "Y": r["Y"], "model": r["model"],
                    "family": fam_name,
                    "family_r2": fam_r2s[fi],
                })
    fam_df = pd.DataFrame(fam_rows)
    fam_df.to_csv(OUT / "t035_family_stability.csv", index=False)
    print("  Saved t035_family_stability.csv")

    # t035_summary.json
    best = all_results[0] if all_results else {}
    n_pass = sum(1 for r in all_results[:20]
                 if r["pooled_r2"] > 0.50 and r["mean_transfer_r2"] > 0.30
                 and r.get("permutation_p", 1) < 0.01 and r["cv_slope"] < 0.25)

    summary = {
        "n_relationships_tested": len(all_pairs),
        "n_valid_relationships": len(all_results),
        "n_families": len(unique_fams),
        "families": list(unique_fams),
        "n_variables": n_vars,
        "variable_names": all_names,
        "best_relationship": {
            "X": best.get("X", ""),
            "Y": best.get("Y", ""),
            "model": best.get("model", ""),
            "pooled_r2": best.get("pooled_r2", 0),
            "mean_transfer_r2": best.get("mean_transfer_r2", 0),
            "invariance_score": best.get("invariance_score", 0),
            "cv_slope": best.get("cv_slope", 0),
            "permutation_p": best.get("permutation_p", 1),
            "ranking_score": best.get("ranking_score", 0),
        },
        "n_top20_pass_criteria": n_pass,
        "success_criterion": "pooled_R2>0.50 AND transfer_R2>0.30 AND p<0.01 AND CV_slope<0.25",
        "success_met": n_pass > 0,
    }
    with open(OUT / "t035_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  Saved t035_summary.json")

    # ============================================================
    # FIGURES
    # ============================================================

    print("\n[Step 11] Generating figures...")

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

    # Fig 1: Top 20 invariant relationships
    fig, ax = plt.subplots(figsize=(7, 5))
    top20_names = [f"{r['X']}→{r['Y']}" for r in top20]
    top20_scores = [r["ranking_score"] for r in top20]
    colors = [G["black"] if r.get("permutation_p", 1) < 0.01 else G["lg"] for r in top20]

    y = np.arange(len(top20))
    ax.barh(y, top20_scores, color=colors, edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels(top20_names, fontsize=5)
    ax.set_xlabel("Ranking score", fontsize=9)
    ax.set_title("Top 20 invariant relationships")
    ax.invert_yaxis()

    # Mark significant
    for i, r in enumerate(top20):
        if r.get("permutation_p", 1) < 0.01:
            ax.plot(top20_scores[i] + 0.01, i, "k*", markersize=5)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t035_top20.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t035_top20.pdf/.png")

    # Fig 2: Transfer R² distribution
    fig, ax = plt.subplots(figsize=(7, 4))
    transfer_vals = [r["mean_transfer_r2"] for r in all_results if np.isfinite(r["mean_transfer_r2"])]
    ax.hist(transfer_vals, bins=40, color=G["gray"], edgecolor="white", linewidth=0.3)
    ax.axvline(0, color="black", ls="--", lw=0.5, label="Zero")
    ax.axvline(np.median(transfer_vals), color="black", ls="-", lw=0.8, label=f"Median={np.median(transfer_vals):.3f}")
    ax.set_xlabel("Mean transfer R² (LOFO)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of transfer R² across all relationships")
    ax.legend(frameon=False)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t035_transfer_distribution.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t035_transfer_distribution.pdf/.png")

    # Fig 3: Stability heatmap (top 20 × families)
    fig, ax = plt.subplots(figsize=(8, 6))
    n_show = min(20, len(top20))
    fam_names = list(unique_fams)
    matrix = np.zeros((n_show, len(fam_names)))
    for i, r in enumerate(top20[:n_show]):
        fam_r2s = r.get("family_r2s", [])
        for j in range(len(fam_names)):
            if j < len(fam_r2s):
                matrix[i, j] = fam_r2s[j]

    im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=-1, vmax=1)
    ax.set_xticks(range(len(fam_names)))
    ax.set_xticklabels(fam_names, fontsize=6, rotation=45, ha="right")
    ax.set_yticks(range(n_show))
    ax.set_yticklabels([f"{r['X']}→{r['Y']}" for r in top20[:n_show]], fontsize=5)
    plt.colorbar(im, ax=ax, label="Family R²", shrink=0.8)
    ax.set_title("Relationship × Family stability matrix")

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t035_stability_heatmap.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t035_stability_heatmap.pdf/.png")

    # Fig 4: Best relationship scatter
    if all_results:
        best = all_results[0]
        xi = all_names.index(best["X"])
        yi = all_names.index(best["Y"])
        X = all_vars[:, xi]
        Y = all_vars[:, yi]

        fig, ax = plt.subplots(figsize=(5, 4))
        for fi, fam_name in enumerate(unique_fams):
            mask = fam_idx == fi
            ax.scatter(X[mask], Y[mask], s=15, alpha=0.7, label=fam_name)

        # Fit line
        valid = np.isfinite(X) & np.isfinite(Y)
        Xv, Yv = X[valid], Y[valid]
        if best["model"] == "linear":
            coef = np.polyfit(Xv, Yv, 1)
            xline = np.linspace(Xv.min(), Xv.max(), 100)
            ax.plot(xline, np.polyval(coef, xline), "k--", lw=1, label="Fit")
        elif best["model"] == "rf":
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(Xv.reshape(-1, 1), Yv)
            xline = np.linspace(Xv.min(), Xv.max(), 100)
            ax.plot(xline, model.predict(xline.reshape(-1, 1)), "k--", lw=1, label="Fit")

        ax.set_xlabel(best["X"])
        ax.set_ylabel(best["Y"])
        ax.set_title(f"Best invariant: {best['X']}→{best['Y']} ({best['model']}, R²={best['pooled_r2']:.3f})")
        ax.legend(frameon=False, fontsize=5, ncol=2, loc="best")

        plt.tight_layout()
        for ext in ("pdf", "png"):
            fig.savefig(FIG / f"fig_t035_best_relationship.{ext}", format=ext, dpi=300)
        plt.close(fig)
        print("  Saved fig_t035_best_relationship.pdf/.png")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    elapsed = time.time() - t0
    print(f"\nRuntime: {elapsed:.1f}s")

    best = all_results[0] if all_results else {}
    print("\n" + "=" * 70)
    print("T035 RESULTS")
    print("=" * 70)
    print(f"Relationships Tested: {len(all_pairs)}")
    print(f"Valid Relationships:   {len(all_results)}")
    print()
    print(f"Top Invariant Relationship: {best.get('X', 'N/A')} -> {best.get('Y', 'N/A')}")
    print(f"Model Type:           {best.get('model', 'N/A')}")
    print(f"Pooled R²:            {best.get('pooled_r2', 0):.4f}")
    print(f"Transfer R²:          {best.get('mean_transfer_r2', 0):.4f}")
    print(f"Slope Stability:      CV={best.get('cv_slope', 0):.4f}")
    print(f"Permutation p-value:  {best.get('permutation_p', 1):.4f}")
    ci = best.get("bootstrap_ci", {})
    print(f"Bootstrap CI:         [{ci.get('ci_lo', 0):.4f}, {ci.get('ci_hi', 0):.4f}]")
    print()
    print("Top 10 Relationships:")
    for rank, r in enumerate(top20[:10], 1):
        p = r.get("permutation_p", 1)
        sig = "*" if p < 0.01 else " "
        print(f"  {rank:2d}. {r['X']:25s} -> {r['Y']:25s}  "
              f"R²={r['pooled_r2']:.3f}  T_R²={r['mean_transfer_r2']:.3f}  "
              f"I={r['invariance_score']:.3f}  CV={r['cv_slope']:.3f}  p={p:.3f} {sig}")

    print()
    verdict = "INVARIANT RELATIONSHIP DETECTED" if n_pass > 0 else "NO ROBUST INVARIANT DETECTED"
    print(f"FINAL VERDICT: {verdict}")
    print("=" * 70)


if __name__ == "__main__":
    main()
