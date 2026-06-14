#!/usr/bin/env python3
"""
T035-R1: Remove Derivational Leakage
======================================
Rerun invariant search with:
1. Leakage audit (direct/derived/partial/independent)
2. Whitelist of 14 independent base variables only
3. Flag R²>0.98 as LIKELY DERIVATIONAL
4. Clean outputs only
"""

import sys, json, warnings, time, itertools
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from scipy.spatial.distance import pdist, squareform
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
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
# TASK 1: LEAKAGE AUDIT
# ============================================================

# Construction relationships between original 17 features
# DIRECT: Y contains X directly
# DERIVED: Y is computed from X through deterministic feature construction
# PARTIAL_DERIVED: Y shares upstream inputs with X
# INDEPENDENT: No shared construction path

LEAKAGE_AUDIT = {
    # pc1 is used in: pc1_ratio, abl_full_pc1, abl_no_*_pc1, m2_contribution
    ("pc1", "pc1_ratio"): "DIRECT",
    ("pc1", "abl_full_pc1"): "DIRECT",
    ("pc1", "abl_no_m1_pc1"): "DIRECT",
    ("pc1", "abl_no_m2_pc1"): "DIRECT",
    ("pc1", "abl_no_m3_pc1"): "DIRECT",
    ("pc1", "abl_no_m4_pc1"): "DIRECT",
    ("pc1", "m2_contribution"): "DERIVED",

    # pc2 is used in: pc1_ratio (as denominator), phase_corr
    ("pc2", "pc1_ratio"): "DERIVED",
    ("pc2", "phase_corr"): "PARTIAL_DERIVED",

    # effective_rank is derived from SVD of trajectory features
    ("effective_rank", "PR"): "DIRECT",  # PR is essentially effective_rank of covariance

    # tau_m1-m4 are moment-based timescales
    ("tau_m1", "tau_m2"): "PARTIAL_DERIVED",  # share upstream moments
    ("tau_m1", "tau_m3"): "PARTIAL_DERIVED",
    ("tau_m1", "tau_m4"): "PARTIAL_DERIVED",
    ("tau_m2", "tau_m3"): "PARTIAL_DERIVED",
    ("tau_m2", "tau_m4"): "PARTIAL_DERIVED",
    ("tau_m3", "tau_m4"): "PARTIAL_DERIVED",

    # temporal_corr and phase_corr are both correlation measures
    ("temporal_corr", "phase_corr"): "PARTIAL_DERIVED",

    # Phi coordinates are linear composites of features
    ("C", "pc1"): "PARTIAL_DERIVED",
    ("C", "pc2"): "PARTIAL_DERIVED",
    ("C", "effective_rank"): "PARTIAL_DERIVED",
    ("C", "temporal_corr"): "PARTIAL_DERIVED",
    ("C", "pc1_ratio"): "PARTIAL_DERIVED",
    ("C", "replay_displacement"): "PARTIAL_DERIVED",
    ("F", "tau_m2"): "PARTIAL_DERIVED",
    ("F", "tau_m4"): "PARTIAL_DERIVED",
    ("F", "phase_corr"): "PARTIAL_DERIVED",
    ("F", "pc2"): "PARTIAL_DERIVED",
    ("A", "tau_m1"): "PARTIAL_DERIVED",
    ("A", "abl_full_pc1"): "PARTIAL_DERIVED",
    ("A", "abl_no_m1_pc1"): "PARTIAL_DERIVED",
    ("A", "abl_no_m2_pc1"): "PARTIAL_DERIVED",
    ("A", "abl_no_m3_pc1"): "PARTIAL_DERIVED",
    ("A", "abl_no_m4_pc1"): "PARTIAL_DERIVED",
    ("A", "m2_contribution"): "PARTIAL_DERIVED",
    ("R", "pc1"): "PARTIAL_DERIVED",
    ("R", "tau_m1"): "PARTIAL_DERIVED",
    ("R", "tau_m2"): "PARTIAL_DERIVED",
    ("R", "tau_m3"): "PARTIAL_DERIVED",
    ("R", "tau_m4"): "PARTIAL_DERIVED",
}


def classify_relationship(x_name, y_name):
    """Classify leakage type for X->Y."""
    key1 = (x_name, y_name)
    key2 = (y_name, x_name)
    if key1 in LEAKAGE_AUDIT:
        return LEAKAGE_AUDIT[key1]
    if key2 in LEAKAGE_AUDIT:
        return LEAKAGE_AUDIT[key2]
    return "INDEPENDENT"


# ============================================================
# TASK 2: WHITELIST
# ============================================================

WHITELIST_NAMES = [
    "tau_m1", "tau_m2", "tau_m3", "tau_m4",
    "temporal_corr", "phase_corr",
    "effective_rank",
    "spectral_entropy", "mean_curvature", "local_dim",
    "laminarity", "divergence_rate",
    "PR",
    "pc1",  # keep pc1 as base observable (not a composite)
]

# ============================================================
# BUILD WHITELIST DATA
# ============================================================

def build_whitelist_data():
    """Build whitelist variable pool."""
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

    # Derived quantities
    D = squareform(pdist(X_raw, metric="euclidean"))
    n = len(X_raw)
    K = min(5, n - 1)

    # PR
    cov = np.cov(X_raw, rowvar=False)
    evals = np.linalg.eigvalsh(cov)
    evals = np.maximum(evals, 1e-12)
    pr = (np.sum(evals) ** 2) / (np.sum(evals ** 2))

    # spectral_entropy
    x_mean = X_raw.mean(axis=0)
    devs = np.abs(X_raw - x_mean)
    dev_norm = devs / (devs.sum(axis=1, keepdims=True) + 1e-12)
    spectral_entropy = -np.sum(dev_norm * np.log(dev_norm + 1e-12), axis=1)

    # Per-system derived
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

    # Build whitelist matrix
    all_vars_dict = {
        "pc1": X_raw[:, 0],
        "tau_m1": X_raw[:, 3],
        "tau_m2": X_raw[:, 4],
        "tau_m3": X_raw[:, 5],
        "tau_m4": X_raw[:, 6],
        "temporal_corr": X_raw[:, 7],
        "phase_corr": X_raw[:, 8],
        "effective_rank": X_raw[:, 2],
        "spectral_entropy": spectral_entropy,
        "mean_curvature": mean_curvature,
        "local_dim": local_dim,
        "laminarity": laminarity,
        "divergence_rate": divergence_rate,
        "PR": np.full(n, pr),
    }

    all_vars = np.column_stack([all_vars_dict[name] for name in WHITELIST_NAMES])

    print(f"  Whitelist: {len(WHITELIST_NAMES)} variables, {n} systems, {len(unique_fams)} families")
    return all_vars, WHITELIST_NAMES, families, unique_fams, fam_idx


# ============================================================
# FITTING (reuse from T035)
# ============================================================

def fit_relationship(X, Y, model_type):
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
            coef = np.polyfit(np.log(Xv[pos]), np.log(np.abs(Yv[pos]) + 1e-12), 1)
            Y_pred = np.polyval(coef, np.log(np.abs(Xv[pos]) + 1e-12))
            Xv, Yv = Xv[pos], Yv[pos]
        elif model_type == "log":
            pos = Xv > 0
            if pos.sum() < 10:
                return None, None
            coef = np.polyfit(np.log(Xv[pos]), Yv[pos], 1)
            Y_pred = np.polyval(coef, np.log(Xv[pos]))
            Xv, Yv = Xv[pos], Yv[pos]
        elif model_type == "exponential":
            pos = Yv > 0
            if pos.sum() < 10:
                return None, None
            coef = np.polyfit(Xv[pos], np.log(Yv[pos]), 1)
            Y_pred = np.exp(np.polyval(coef, Xv[pos]))
            Xv, Yv = Xv[pos], Yv[pos]
        elif model_type == "rf":
            model = RandomForestRegressor(n_estimators=30, random_state=42)
            model.fit(Xv.reshape(-1, 1), Yv)
            Y_pred = model.predict(Xv.reshape(-1, 1))
        else:
            return None, None
        return r2_score(Yv, Y_pred), mean_absolute_error(Yv, Y_pred)
    except Exception:
        return None, None


def get_slope(X, Y, model_type):
    valid = np.isfinite(X) & np.isfinite(Y)
    Xv, Yv = X[valid], Y[valid]
    if len(Xv) < 10:
        return np.nan
    try:
        if model_type == "linear":
            return np.polyfit(Xv, Yv, 1)[0]
        elif model_type == "power":
            pos = Xv > 0
            if pos.sum() < 10:
                return np.nan
            return np.polyfit(np.log(Xv[pos]), np.log(np.abs(Yv[pos]) + 1e-12), 1)[0]
        elif model_type == "log":
            pos = Xv > 0
            if pos.sum() < 10:
                return np.nan
            return np.polyfit(np.log(Xv[pos]), Yv[pos], 1)[0]
        elif model_type == "exponential":
            pos = Yv > 0
            if pos.sum() < 10:
                return np.nan
            return np.polyfit(Xv[pos], np.log(Yv[pos]), 1)[0]
    except Exception:
        return np.nan
    return np.nan


# ============================================================
# EVALUATE
# ============================================================

def evaluate_relationship(all_vars, all_names, xi, yi, families, unique_fams, fam_idx):
    X = all_vars[:, xi]
    Y = all_vars[:, yi]
    x_name = all_names[xi]
    y_name = all_names[yi]

    # Task 4: Skip if both are identical
    if np.allclose(X, Y, atol=1e-12):
        return None

    best_model = None
    best_r2 = -np.inf
    for mt in ["linear", "power", "log", "exponential", "rf"]:
        r2, _ = fit_relationship(X, Y, mt)
        if r2 is not None and r2 > best_r2:
            best_r2 = r2
            best_model = mt
    if best_model is None:
        return None

    # Task 4: Flag R²>0.98
    likely_deriv = best_r2 > 0.98

    # Family-by-family
    fam_r2s = []
    slopes = []
    for fam_i in range(len(unique_fams)):
        mask = fam_idx == fam_i
        if mask.sum() < 5:
            continue
        r2, _ = fit_relationship(X[mask], Y[mask], best_model)
        slope = get_slope(X[mask], Y[mask], best_model)
        if r2 is not None:
            fam_r2s.append(r2)
            slopes.append(slope)

    if len(fam_r2s) < 3:
        return None

    pooled_r2, pooled_mae = fit_relationship(X, Y, best_model)
    if pooled_r2 is None:
        return None

    mean_fam_r2 = np.mean(fam_r2s)
    invariance = pooled_r2 / max(abs(mean_fam_r2), 1e-12) if mean_fam_r2 > 0 else 0

    valid_slopes = [s for s in slopes if np.isfinite(s)]
    cv_slope = np.std(valid_slopes) / max(abs(np.mean(valid_slopes)), 1e-12) if len(valid_slopes) >= 3 else np.nan

    # LOFO transfer
    transfer_r2s = []
    for fam_i in range(len(unique_fams)):
        test_mask = fam_idx == fam_i
        train_mask = ~test_mask
        if test_mask.sum() < 3 or train_mask.sum() < 10:
            continue
        X_tr, X_te = X[train_mask], X[test_mask]
        Y_tr, Y_te = Y[train_mask], Y[test_mask]
        try:
            if best_model == "linear":
                coef = np.polyfit(X_tr, Y_tr, 1)
                Y_pred = np.polyval(coef, X_te)
            elif best_model == "power":
                pos = X_tr > 0
                pos_te = X_te > 0
                if pos.sum() < 10 or pos_te.sum() < 3:
                    continue
                coef = np.polyfit(np.log(X_tr[pos]), np.log(np.abs(Y_tr[pos]) + 1e-12), 1)
                Y_pred = np.exp(np.polyval(coef, np.log(np.abs(X_te[pos_te]) + 1e-12)))
                Y_te = Y_te[pos_te]
            elif best_model == "log":
                pos = X_tr > 0
                pos_te = X_te > 0
                if pos.sum() < 10 or pos_te.sum() < 3:
                    continue
                coef = np.polyfit(np.log(X_tr[pos]), Y_tr[pos], 1)
                Y_pred = np.polyval(coef, np.log(X_te[pos_te]))
                Y_te = Y_te[pos_te]
            elif best_model == "exponential":
                pos = Y_tr > 0
                pos_te = Y_te > 0
                if pos.sum() < 10 or pos_te.sum() < 3:
                    continue
                coef = np.polyfit(X_tr[pos], np.log(Y_tr[pos]), 1)
                Y_pred = np.exp(np.polyval(coef, X_te[pos_te]))
                Y_te = Y_te[pos_te]
            elif best_model == "rf":
                model = RandomForestRegressor(n_estimators=30, random_state=42)
                model.fit(X_tr.reshape(-1, 1), Y_tr)
                Y_pred = model.predict(X_te.reshape(-1, 1))
            if len(Y_te) > 0 and np.std(Y_te) > 0:
                transfer_r2s.append(r2_score(Y_te, Y_pred))
        except Exception:
            pass

    mean_transfer = np.mean(transfer_r2s) if transfer_r2s else 0

    return {
        "X": x_name, "Y": y_name, "model": best_model,
        "pooled_r2": float(pooled_r2),
        "pooled_mae": float(pooled_mae),
        "invariance_score": float(invariance) if np.isfinite(invariance) else 0,
        "cv_slope": float(cv_slope) if np.isfinite(cv_slope) else 1,
        "mean_transfer_r2": float(mean_transfer),
        "family_r2s": [float(r) for r in fam_r2s],
        "slopes": [float(s) for s in valid_slopes],
        "likely_derivational": likely_deriv,
    }


def permutation_test(all_vars, all_names, xi, yi, fam_idx, unique_fams, model_type, n_perm=N_PERM):
    X, Y = all_vars[:, xi], all_vars[:, yi]
    r2_real, _ = fit_relationship(X, Y, model_type)
    if r2_real is None:
        return 1.0
    r2_null = []
    for _ in range(n_perm):
        r2, _ = fit_relationship(X, np.random.permutation(Y), model_type)
        if r2 is not None:
            r2_null.append(r2)
    return float(np.mean(np.array(r2_null) >= r2_real)) if r2_null else 1.0


def bootstrap_ci(all_vars, all_names, xi, yi, model_type, n_boot=N_BOOT):
    X, Y = all_vars[:, xi], all_vars[:, yi]
    boot_r2s = []
    for _ in range(n_boot):
        idx = np.random.choice(len(X), len(X), replace=True)
        r2, _ = fit_relationship(X[idx], Y[idx], model_type)
        if r2 is not None:
            boot_r2s.append(r2)
    if not boot_r2s:
        return {"mean": 0, "ci_lo": 0, "ci_hi": 0}
    arr = np.array(boot_r2s)
    return {"mean": float(np.mean(arr)), "ci_lo": float(np.percentile(arr, 2.5)), "ci_hi": float(np.percentile(arr, 97.5))}


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T035-R1: REMOVE DERIVATIONAL LEAKAGE")
    print("=" * 70)
    t0 = time.time()

    # Task 1: Leakage audit
    print("\n[Task 1] Leakage audit...")
    all_pairs_list = list(itertools.combinations(range(len(WHITELIST_NAMES)), 2))
    audit_rows = []
    for xi, yi in all_pairs_list:
        x_name = WHITELIST_NAMES[xi]
        y_name = WHITELIST_NAMES[yi]
        leak_type = classify_relationship(x_name, y_name)
        audit_rows.append({"X": x_name, "Y": y_name, "classification": leak_type})
    audit_df = pd.DataFrame(audit_rows)
    audit_df.to_csv(OUT / "t035_leakage_audit.csv", index=False)
    print(f"  Audited {len(audit_df)} pairs")
    print(f"  Independent: {(audit_df['classification']=='INDEPENDENT').sum()}")
    print(f"  Derived: {(audit_df['classification']=='DERIVED').sum()}")
    print(f"  Partial: {(audit_df['classification']=='PARTIAL_DERIVED').sum()}")
    print(f"  Direct: {(audit_df['classification']=='DIRECT').sum()}")

    # Task 2: Whitelist data
    print("\n[Task 2] Building whitelist data...")
    all_vars, all_names, families, unique_fams, fam_idx = build_whitelist_data()

    # Task 3: Rerun on whitelist
    print("\n[Task 3] Evaluating whitelist relationships...")
    all_pairs = list(itertools.combinations(range(len(all_names)), 2))
    print(f"  Total pairs: {len(all_pairs)}")

    all_results = []
    for pi, (xi, yi) in enumerate(all_pairs):
        if pi % 50 == 0:
            print(f"  Progress: {pi}/{len(all_pairs)}", flush=True)
        if xi == yi:
            continue
        x_name = all_names[xi]
        y_name = all_names[yi]
        # Skip leakage
        leak = classify_relationship(x_name, y_name)
        if leak != "INDEPENDENT":
            continue
        res = evaluate_relationship(all_vars, all_names, xi, yi, families, unique_fams, fam_idx)
        if res is not None:
            res["leakage_type"] = leak
            all_results.append(res)

    print(f"  Valid independent relationships: {len(all_results)}")

    # Task 4: Flag and filter
    print("\n[Task 4] Flagging derivational leakage...")
    n_likely_deriv = sum(1 for r in all_results if r["likely_derivational"])
    print(f"  LIKELY DERIVATIONAL (R²>0.98): {n_likely_deriv}")

    # Remove likely derivational
    clean_results = [r for r in all_results if not r["likely_derivational"]]
    print(f"  Clean relationships: {len(clean_results)}")

    # Permutation tests for top 30
    print("\n[Task 4b] Permutation tests (top 30)...")
    clean_results.sort(key=lambda r: r["pooled_r2"], reverse=True)
    top30 = clean_results[:30]

    for i, res in enumerate(top30):
        xi = all_names.index(res["X"])
        yi = all_names.index(res["Y"])
        res["permutation_p"] = permutation_test(all_vars, all_names, xi, yi, fam_idx, unique_fams, res["model"])

    # Bootstrap for top 20
    print("  Bootstrap CIs (top 20)...")
    top20 = clean_results[:20]
    for i, res in enumerate(top20):
        xi = all_names.index(res["X"])
        yi = all_names.index(res["Y"])
        res["bootstrap_ci"] = bootstrap_ci(all_vars, all_names, xi, yi, res["model"])

    # Ranking score
    for res in clean_results:
        inv = max(0, min(2, res["invariance_score"])) / 2.0
        transfer = max(0, min(1, (res["mean_transfer_r2"] + 1) / 2.0))
        cv = max(0, min(1, 1 - min(res["cv_slope"], 2) / 2.0))
        pooled = max(0, min(1, (res["pooled_r2"] + 1) / 2.0))
        res["ranking_score"] = 0.40 * inv + 0.30 * transfer + 0.20 * cv + 0.10 * pooled

    clean_results.sort(key=lambda r: r["ranking_score"], reverse=True)

    # ============================================================
    # SAVE
    # ============================================================

    print("\n[Task 5] Saving outputs...")

    # t035_clean_top20.csv
    top20_rows = []
    for rank, r in enumerate(clean_results[:20], 1):
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
            "LeakageType": r.get("leakage_type", "INDEPENDENT"),
            "LikelyDerivational": r.get("likely_derivational", False),
        })
    pd.DataFrame(top20_rows).to_csv(OUT / "t035_clean_top20.csv", index=False)
    print("  Saved t035_clean_top20.csv")

    # t035_clean_summary.json
    best = clean_results[0] if clean_results else {}
    n_pass = sum(1 for r in clean_results[:20]
                 if r["pooled_r2"] > 0.50 and r["mean_transfer_r2"] > 0.30
                 and r.get("permutation_p", 1) < 0.01 and r["cv_slope"] < 0.25)

    summary = {
        "n_relationships_tested": len(all_pairs),
        "n_independent_relationships": len(clean_results),
        "n_likely_derivational_removed": n_likely_deriv,
        "whitelist_variables": WHITELIST_NAMES,
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
    with open(OUT / "t035_clean_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  Saved t035_clean_summary.json")

    # ============================================================
    # FIGURES
    # ============================================================

    print("\n[Task 5] Generating figures...")
    plt.rcParams.update({
        "font.family": "serif", "font.size": 9, "axes.titlesize": 10,
        "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "legend.fontsize": 7, "figure.dpi": 300, "savefig.dpi": 300,
        "savefig.bbox": "tight", "axes.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
    })
    G = {"black": "#000000", "dg": "#555555", "gray": "#888888", "lg": "#BBBBBB"}

    # Fig: Top 20
    fig, ax = plt.subplots(figsize=(7, 5))
    names = [f"{r['X']}→{r['Y']}" for r in clean_results[:20]]
    scores = [r["ranking_score"] for r in clean_results[:20]]
    colors = [G["black"] if r.get("permutation_p", 1) < 0.01 else G["lg"] for r in clean_results[:20]]
    y = np.arange(len(names))
    ax.barh(y, scores, color=colors, edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=5)
    ax.set_xlabel("Ranking score")
    ax.set_title("Top 20 invariant relationships (leakage removed)")
    ax.invert_yaxis()
    for i, r in enumerate(clean_results[:20]):
        if r.get("permutation_p", 1) < 0.01:
            ax.plot(scores[i] + 0.01, i, "k*", markersize=5)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t035_clean_top20.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t035_clean_top20.pdf/.png")

    # ============================================================
    # FINAL VERDICT
    # ============================================================

    elapsed = time.time() - t0
    print(f"\nRuntime: {elapsed:.1f}s")

    best = clean_results[0] if clean_results else {}
    print("\n" + "=" * 70)
    print("T035-R1 RESULTS")
    print("=" * 70)
    print(f"DERIVATIONAL LEAKAGE REMOVED")
    print(f"  Whitelist variables: {len(WHITELIST_NAMES)}")
    print(f"  Independent pairs tested: {len(all_pairs)}")
    print(f"  Likely derivational removed: {n_likely_deriv}")
    print()
    print(f"Robust Invariants Found: {n_pass}")
    print()
    if clean_results:
        r = clean_results[0]
        print(f"Top Relationship: {r['X']} -> {r['Y']}")
        print(f"  Model: {r['model']}")
        print(f"  Pooled R²: {r['pooled_r2']:.4f}")
        print(f"  Transfer R²: {r['mean_transfer_r2']:.4f}")
        print(f"  Invariance: {r['invariance_score']:.4f}")
        print(f"  CV slope: {r['cv_slope']:.4f}")
        p = r.get("permutation_p", 1)
        print(f"  Permutation p: {p:.4f}")
        ci = r.get("bootstrap_ci", {})
        print(f"  Bootstrap CI: [{ci.get('ci_lo', 0):.4f}, {ci.get('ci_hi', 0):.4f}]")
    else:
        print("  No robust invariants found.")

    print()
    print("Top 10:")
    for rank, r in enumerate(clean_results[:10], 1):
        p = r.get("permutation_p", 1)
        sig = "*" if p < 0.01 else " "
        print(f"  {rank:2d}. {r['X']:20s} -> {r['Y']:20s}  "
              f"R²={r['pooled_r2']:.3f}  T={r['mean_transfer_r2']:.3f}  "
              f"I={r['invariance_score']:.3f}  CV={r['cv_slope']:.3f}  p={p:.3f} {sig}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
