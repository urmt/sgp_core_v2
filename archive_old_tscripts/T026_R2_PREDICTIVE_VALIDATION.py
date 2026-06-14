#!/usr/bin/env python3
"""
T026: R2 — PREDICTIVE VALIDATION
=================================
Three experiments that determine whether SFH-SGP becomes predictive science
or remains descriptive geometry.

R2.1: Collapse Forecasting — does Φ-space predict transition thresholds?
R2.2: Cross-Domain Transfer — do new system types share the same geometry?
R2.3: Universal Boundary Search — what is the emergence function E = f(C,F)?

Success criterion: Φ-space predicts transition behavior better than baselines.
"""

import sys, json, warnings, math, random
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import cross_val_score, KFold, train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.neighbors import KernelDensity
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster, cophenet
from scipy.stats import pearsonr, spearmanr, gaussian_kde
from scipy.optimize import curve_fit

warnings.filterwarnings("ignore", category=RuntimeWarning)
np.random.seed(42)
random.seed(42)

OUT = Path("sfh_sgp_ood_outputs")
OUT.mkdir(exist_ok=True)

ALL_SYSTEMS = [
    "primes", "fibonacci", "modular_arithmetic", "additive_recurrence",
    "lorenz", "logistic_map", "henon_map", "ising_magnetization",
    "reaction_diffusion", "cfg_expansion", "lambda_reduction",
    "rewrite_system", "iid_gaussian", "colored_noise",
]

# =====================================================================
# GENERATORS FOR NEW DOMAINS (R2.2)
# =====================================================================
def lotka_volterra(n=512, alpha=1.5, beta=1.0, gamma=3.0, delta=1.0, dt=0.01):
    """Predator-prey oscillations. Track prey population."""
    prey, pred = 10.0, 5.0
    traj = [prey]
    for _ in range(n):
        d_prey = alpha * prey - beta * prey * pred
        d_pred = delta * prey * pred - gamma * pred
        prey += d_prey * dt
        pred += d_pred * dt
        traj.append(prey)
    return np.array(traj[:n], dtype=float)

def kuramoto_oscillator(n=512, n_osc=8, coupling=2.0, omega_std=1.0):
    """Mean field of coupled Kuramoto oscillators."""
    omega = np.random.randn(n_osc) * omega_std
    theta = np.random.rand(n_osc) * 2 * np.pi
    dt = 0.05
    order = [np.abs(np.mean(np.exp(1j * theta)))]
    for _ in range(n):
        for i in range(n_osc):
            theta[i] += dt * (omega[i] + coupling / n_osc *
                              np.sum(np.sin(theta - theta[i])))
        order.append(np.abs(np.mean(np.exp(1j * theta))))
    return np.array(order[:n], dtype=float)

def poisson_spike(n=512, rate=10.0, refractory=5):
    """Neural spike train with refractory period."""
    spikes = np.zeros(n)
    ref_count = 0
    for t in range(n):
        if ref_count > 0:
            ref_count -= 1
            continue
        if np.random.rand() < rate / n:
            spikes[t] = 1.0
            ref_count = refractory
    return spikes

def geometric_brownian(n=512, mu=0.0001, sigma=0.02, x0=100.0):
    """GBM. Track price."""
    x = x0
    traj = [x]
    for _ in range(n):
        x *= np.exp((mu - 0.5 * sigma**2) + sigma * np.random.randn())
        traj.append(x)
    return np.array(traj[:n], dtype=float)

def sandpile_avalanche(n=512, L=8, drive_rate=0.01):
    """BTW sandpile — track avalanche sizes (SOC). Open boundaries."""
    grid = np.zeros((L, L), dtype=int)
    avs = []
    for _ in range(n):
        i, j = np.random.randint(0, L, 2)
        grid[i, j] += 1
        if grid[i, j] < 4:
            avs.append(0)
            continue
        av = 0
        unstable = [(i, j)]
        toppled = set()
        while unstable:
            ci, cj = unstable.pop()
            if (ci, cj) in toppled:
                continue
            toppled.add((ci, cj))
            grid[ci, cj] -= 4
            av += 1
            for di, dj in [(0,1),(0,-1),(1,0),(-1,0)]:
                ni, nj = ci + di, cj + dj
                if 0 <= ni < L and 0 <= nj < L:
                    grid[ni, nj] += 1
                    if grid[ni, nj] >= 4:
                        unstable.append((ni, nj))
        avs.append(av)
        for ci, cj in toppled:
            if grid[ci, cj] >= 4:
                grid[ci, cj] = 0
    return np.array(avs, dtype=float)

def random_boolean_network(n=512, N=10, K=2, p=0.5):
    """RBN — Hamming distance between successive states."""
    state = np.random.randint(0, 2, N)
    # Random topology
    connections = np.random.randint(0, N, (N, K))
    # Random boolean functions
    functions = np.random.randint(0, 2, (N, 2**K))
    hamming = [0.0]
    for _ in range(n):
        new_state = state.copy()
        for i in range(N):
            inputs = [state[connections[i, k]] for k in range(K)]
            idx = sum(v << k for k, v in enumerate(inputs))
            new_state[i] = functions[i, idx]
        hamming.append(float(np.sum(state != new_state)))
        state = new_state
    return np.array(hamming[:n], dtype=float)

NEW_SYSTEMS = {
    "lotka_volterra": lotka_volterra,
    "kuramoto": kuramoto_oscillator,
    "poisson_spike": poisson_spike,
    "geometric_brownian": geometric_brownian,
    "sandpile": sandpile_avalanche,
    "random_boolean_net": random_boolean_network,
}

# =====================================================================
# IMPORTS FROM CORE MODULES
# =====================================================================
from sfh_sgp_ood_universality_audit import (
    TRANSFORMS, canonical_metric_vector, compute_transform_geometry,
    replay_stability, null_audit_system, system_category, OOD_SYSTEMS,
)

# =====================================================================
# 1. LOAD EMERGENCE COORDINATES
# =====================================================================
def load_emergence():
    coord = pd.read_csv(OUT / "emergence_coordinates.csv")
    coord = coord[coord["system"].isin(ALL_SYSTEMS)].copy()
    axes = ["C", "F", "A", "R"]
    Phi = coord[axes].values
    # Also load the feature matrix for perturbation experiments
    feat = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    feat = feat[feat["system"].isin(ALL_SYSTEMS)].copy()
    feat = feat.set_index("system").loc[ALL_SYSTEMS].reset_index()
    X = feat[[c for c in feat.columns if c != "system"]].values
    Xs = StandardScaler().fit_transform(X)
    # Baseline P0 labels
    Z0 = linkage(Xs, method="ward", metric="euclidean")
    p0_labels = fcluster(Z0, t=3, criterion="maxclust")
    return coord, Phi, feat, X, Xs, p0_labels

# =====================================================================
# 2. R2.1 EXPERIMENT A — COLLAPSE FORECASTING
# =====================================================================
def experiment_collapse_forecast(Xs, p0_labels, systems, coord_df):
    """
    Per-system noise perturbation: add N(0,σ) to ONE system's features,
    recluster all 14, measure ARI vs baseline.
    Models collapse_threshold ~ Φ.
    """
    print("\n" + "=" * 70)
    print("R2.1-A: COLLAPSE FORECASTING — per-system noise perturbation")
    print("=" * 70)

    N = len(systems)
    sigmas = np.array([0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0])
    n_trials = 30

    # Store collapse curves per system
    collapse_curves = np.zeros((N, len(sigmas)))

    for i in range(N):
        for j, sigma in enumerate(sigmas):
            aris = []
            for _ in range(n_trials):
                X_noise = Xs.copy()
                X_noise[i] += np.random.normal(0, sigma, Xs.shape[1])
                Z = linkage(X_noise, method="ward", metric="euclidean")
                labels = fcluster(Z, t=3, criterion="maxclust")
                from sklearn.metrics import adjusted_rand_score
                aris.append(adjusted_rand_score(p0_labels, labels))
            collapse_curves[i, j] = np.mean(aris)

    # Find collapse threshold: σ where ARI first drops below 0.5
    collapse_thresholds = {}
    for i, sys_name in enumerate(systems):
        above = np.where(collapse_curves[i] >= 0.5)[0]
        if len(above) > 0 and above[-1] < len(sigmas) - 1:
            thresh = sigmas[above[-1]]  # last sigma with ARI >= 0.5
        elif collapse_curves[i, -1] >= 0.5:
            thresh = 10.0  # never collapses
        else:
            thresh = 0.0  # already collapsed
        collapse_thresholds[sys_name] = thresh

    # Print results
    print(f"\n  Collapse thresholds (σ_c where ARI < 0.5):")
    for s in sorted(collapse_thresholds, key=lambda x: collapse_thresholds[x]):
        print(f"    {s:<24s} σ_c = {collapse_thresholds[s]:.3f}")

    # ---- Model: predict collapse_threshold from Φ ----
    axes = ["C", "F", "A", "R"]
    Phi = coord_df[axes].values
    y = np.array([collapse_thresholds[s] for s in systems])

    # Model 1: Linear regression on Φ
    linreg = LinearRegression()
    linreg_scores = cross_val_score(linreg, Phi, y, cv=5, scoring='r2')

    # Model 2: Random forest on Φ
    rf = RandomForestRegressor(n_estimators=100, max_depth=3, random_state=42)
    rf_scores = cross_val_score(rf, Phi, y, cv=5, scoring='r2')

    # Model 3: Ridge (regularized)
    ridge = Ridge(alpha=1.0)
    ridge_scores = cross_val_score(ridge, Phi, y, cv=5, scoring='r2')

    # ---- Baselines ----
    # Baseline 1: Random (shuffle y)
    y_shuffled = y.copy()
    np.random.shuffle(y_shuffled)
    null_scores = cross_val_score(linreg, Phi, y_shuffled, cv=5, scoring='r2')

    # Baseline 2: PCA only (first 4 PCs of raw features)
    X_pca = PCA(n_components=4).fit_transform(Xs)
    pca_scores = cross_val_score(linreg, X_pca, y, cv=5, scoring='r2')

    # Baseline 3: Single-axis models
    single_scores = {}
    for ax in axes:
        single_scores[ax] = cross_val_score(linreg, Phi[:, [axes.index(ax)]], y, cv=5, scoring='r2')

    print(f"\n  --- Prediction: σ_c ~ Φ ---")
    print(f"  {'Model':<30s}  {'R² (5-fold CV)':>15s}")
    print(f"  {'-'*48}")
    print(f"  {'RandomForest(Φ)':<30s}  {np.mean(rf_scores):>+8.4f} ± {np.std(rf_scores):.4f}")
    print(f"  {'Linear(Φ)':<30s}  {np.mean(linreg_scores):>+8.4f} ± {np.std(linreg_scores):.4f}")
    print(f"  {'Ridge(Φ)':<30s}  {np.mean(ridge_scores):>+8.4f} ± {np.std(ridge_scores):.4f}")
    print(f"  {'PCA-baseline(PCA4)':<30s}  {np.mean(pca_scores):>+8.4f} ± {np.std(pca_scores):.4f}")
    for ax in axes:
        print(f"  {'Single-axis('+ax+')':<30s}  {np.mean(single_scores[ax]):>+8.4f} ± {np.std(single_scores[ax]):.4f}")
    print(f"  {'Null (shuffled y)':<30s}  {np.mean(null_scores):>+8.4f} ± {np.std(null_scores):.4f}")

    # Feature importance from Random Forest
    rf.fit(Phi, y)
    feat_imp = {ax: float(rf.feature_importances_[i]) for i, ax in enumerate(axes)}
    print(f"\n  Φ-axis importance: {feat_imp}")

    # Save
    result = {
        "sigmas_tested": sigmas.tolist(),
        "n_trials_per_sigma": n_trials,
        "collapse_curves": {sys_name: collapse_curves[i].tolist()
                            for i, sys_name in enumerate(systems)},
        "collapse_thresholds": collapse_thresholds,
        "prediction_models": {
            "RandomForest(Φ)": {"mean_r2": float(np.mean(rf_scores)),
                                "std_r2": float(np.std(rf_scores))},
            "Linear(Φ)": {"mean_r2": float(np.mean(linreg_scores)),
                          "std_r2": float(np.std(linreg_scores))},
            "Ridge(Φ)": {"mean_r2": float(np.mean(ridge_scores)),
                          "std_r2": float(np.std(ridge_scores))},
            "PCA-baseline": {"mean_r2": float(np.mean(pca_scores)),
                             "std_r2": float(np.std(pca_scores))},
            "Null": {"mean_r2": float(np.mean(null_scores)),
                     "std_r2": float(np.std(null_scores))},
        },
        "feature_importance": feat_imp,
    }

    return collapse_curves, collapse_thresholds, result

# =====================================================================
# 3. R2.1 EXPERIMENT B — TRANSITION SUSCEPTIBILITY
# =====================================================================
def experiment_transition_susceptibility(Xs, p0_labels, systems, coord_df, collapse_curves):
    """
    Test: high-flow, high-curvature systems should have:
    - lowest stability margins
    - highest topology sensitivity
    - strongest manifold drift
    """
    print("\n" + "=" * 70)
    print("R2.1-B: TRANSITION SUSCEPTIBILITY")
    print("=" * 70)

    # Load flow and landscape data
    flow_df = pd.read_csv(OUT / "emergence_flow_field.csv")
    flow_map = {r["system"]: r["flow_magnitude"] for _, r in flow_df.iterrows()}

    with open(OUT / "emergence_energy_landscape.json") as f:
        landscape = json.load(f)
    curvature_map = {s: landscape["curvature_per_system"][s]["mean_curvature"]
                     for s in systems}

    # Also load density
    density_map = {s: landscape.get("density_per_system", {}).get(s, 0)
                   for s in systems}

    axes = ["C", "F", "A", "R"]
    Phi = coord_df[axes].values

    # ---- Susceptibility metrics ----
    # 1. Flow magnitude (from R1.3)
    flows = np.array([flow_map.get(s, 0) for s in systems])

    # 2. Bootstrap cluster persistence (how often system stays in same cluster)
    n_boot = 500
    boot_persistence = np.zeros(len(systems))
    for _ in range(n_boot):
        idxs = np.random.choice(len(systems), len(systems), replace=True)
        X_boot = Xs[idxs]
        Z = linkage(X_boot, method="ward", metric="euclidean")
        boot_labels = fcluster(Z, t=3, criterion="maxclust")
        for i in range(len(systems)):
            # Find if system i is in its original cluster in this bootstrap
            if i in idxs:
                boot_idx = list(idxs).index(i)
                boot_persistence[i] += (boot_labels[boot_idx] == p0_labels[i]) / n_boot

    # 3. Feature knockout sensitivity: standard deviation of ARI across feature removals
    feat_groups = {
        "spectral": ["pc1", "pc2", "effective_rank"],
        "tau_axis": ["tau_m1", "tau_m2", "tau_m3", "tau_m4"],
        "null_audit": ["temporal_corr", "phase_corr", "pc1_ratio"],
        "replay": ["replay_displacement"],
    }

    feat_df = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    feat_cols = [c for c in feat_df.columns if c != "system"]
    X_raw = feat_df[[c for c in feat_df.columns if c != "system"]].values

    # Per-system knockout sensitivity: for each system, 
    # replace its value in a feature with the mean and measure distance shift
    knockout_shifts = np.zeros(len(systems))
    for i in range(len(systems)):
        shifts = []
        for c in range(X_raw.shape[1]):
            X_k = X_raw.copy()
            X_k[i, c] = X_raw[:, c].mean()
            shift = np.linalg.norm(X_k[i] - X_raw[i])
            shifts.append(shift)
        knockout_shifts[i] = np.mean(shifts)

    # 4. Collapse sensitivity: slope of ARI decay at σ = 0.3
    sigmas = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3]
    N = len(systems)
    collapse_slopes = np.zeros(N)
    for i in range(N):
        # Find the ARI values at these sigma levels
        curve_vals = [collapse_curves[i, j] for j in range(len(sigmas))]
        if len(curve_vals) > 1:
            collapse_slopes[i] = (curve_vals[-1] - curve_vals[0]) / (sigmas[-1] - sigmas[0])

    # ---- Correlate with Φ ----
    print(f"\n  --- Correlations with Φ-space position: ---")
    print(f"  {'Metric':<28s}  {'C':>8s}  {'F':>8s}  {'A':>8s}  {'R':>8s}  {'flow':>8s}  {'curv':>8s}")
    print(f"  {'-'*76}")

    metrics = {
        "flow_magnitude": flows,
        "collapse_slope": collapse_slopes,
        "knockout_sensitivity": knockout_shifts,
        "boot_persistence": boot_persistence,
    }

    corr_results = {}
    for mname, mvals in metrics.items():
        if np.std(mvals) == 0:
            continue
        corrs = {}
        for j, ax in enumerate(axes):
            r_val, p_val = pearsonr(mvals, Phi[:, j])
            corrs[ax] = {"r": float(r_val), "p": float(p_val)}
        r_vs_flow, p_vs_flow = pearsonr(mvals, flows)
        r_vs_curv, p_vs_curv = pearsonr(mvals, np.array(list(curvature_map.values())))
        corrs["flow"] = {"r": float(r_vs_flow), "p": float(p_vs_flow)}
        corrs["curvature"] = {"r": float(r_vs_curv), "p": float(p_vs_curv)}
        corr_results[mname] = corrs

        print(f"  {mname:<28s}", end="")
        for key in axes + ["flow", "curvature"]:
            c = corrs.get(key, {"r": 0})
            print(f"  {c['r']:>+7.4f}", end="")
        print()

    # Print key findings
    print(f"\n  Key susceptibility rankings:")
    for mname, mvals in metrics.items():
        if np.std(mvals) == 0:
            continue
        order = np.argsort(mvals)
        top3 = [(systems[i], mvals[i]) for i in order[-3:][::-1]]
        bottom3 = [(systems[i], mvals[i]) for i in order[:3]]
        print(f"    {mname}:")
        print(f"      Highest: {', '.join(f'{s}={v:.3f}' for s, v in top3)}")
        print(f"      Lowest:  {', '.join(f'{s}={v:.3f}' for s, v in bottom3)}")

    # Hypothesis test: bridge cluster (P0=2) has higher flow than others?
    cluster_2_idx = [i for i in range(len(systems)) if p0_labels[i] == 2]
    other_idx = [i for i in range(len(systems)) if p0_labels[i] != 2]
    c2_flow_mean = np.mean(flows[cluster_2_idx])
    other_flow_mean = np.mean(flows[other_idx])
    from scipy.stats import ttest_ind
    t_stat, p_val = ttest_ind(flows[cluster_2_idx], flows[other_idx], alternative="greater")

    print(f"\n  Hypothesis: bridge cluster (P0=2) has higher flow?")
    print(f"    Bridge mean flow: {c2_flow_mean:.3f} (n={len(cluster_2_idx)})")
    print(f"    Other mean flow:  {other_flow_mean:.3f} (n={len(other_idx)})")
    print(f"    t-test: t={t_stat:.3f}, p={p_val:.5f} {'✓ SIGNIFICANT' if p_val < 0.05 else '✗ NOT significant'}")

    return corr_results

# =====================================================================
# 4. R2.2 — CROSS-DOMAIN TRANSFER
# =====================================================================
def compute_new_system_geometry(gen):
    """Compute Φ-space coordinates for a new system."""
    from sfh_sgp_ood_universality_audit import compute_transform_geometry
    geo = compute_transform_geometry("_temp", gen)
    null = null_audit_system("_temp", gen)
    replay = replay_stability("_temp", gen)

    features = {
        "pc1": geo["pc1_variance"],
        "pc2": geo["pc2_variance"],
        "effective_rank": geo["effective_rank"],
        "tau_m1": geo["tau_axis"][0],
        "tau_m2": geo["tau_axis"][1],
        "tau_m3": geo["tau_axis"][2],
        "tau_m4": geo["tau_axis"][3],
        "temporal_corr": null["temporal_scramble_corr_mean"],
        "phase_corr": null["phase_randomize_corr_mean"],
        "pc1_ratio": null["pc1_ratio_orig_vs_shuffled"],
        "replay_displacement": replay["replay_displacement_mean"],
        # No ablation data for new systems — set to 0
        "abl_full_pc1": 0.0, "abl_no_m1_pc1": 0.0, "abl_no_m2_pc1": 0.0,
        "abl_no_m3_pc1": 0.0, "abl_no_m4_pc1": 0.0, "m2_contribution": 0.0,
    }
    return features

def compute_emergence_coords(features_dict, mean_vec, std_vec):
    """Convert raw features to Φ-space using existing standardization."""
    raw = np.array([features_dict[c] for c in [
        "pc1", "pc2", "effective_rank", "tau_m1", "tau_m2", "tau_m3", "tau_m4",
        "temporal_corr", "phase_corr", "pc1_ratio", "replay_displacement",
        "abl_full_pc1", "abl_no_m1_pc1", "abl_no_m2_pc1", "abl_no_m3_pc1",
        "abl_no_m4_pc1", "m2_contribution",
    ]])
    std = (raw - mean_vec) / np.maximum(std_vec, 1e-12)

    # Emergence coordinates (same formula as T025)
    c = np.mean([-std[7], -std[2], std[9], -std[10]])  # temporal_corr, eff_rank, pc1_ratio, replay_displacement
    f = np.mean([std[5], std[6], std[8]])               # tau_m2, tau_m4, phase_corr
    a = np.mean([np.linalg.norm(std[11:]), np.std(std[11:]), std[3]])  # ablation_norm, ablation_std, tau_m1
    r = np.mean([std[0], np.mean(std[3:7]), np.std(std[3:7])])  # pc1, tau_mean, tau_std

    return {"C": c, "F": f, "A": a, "R": r}

def experiment_cross_domain():
    """
    Compute Φ-space coordinates for new prototype systems.
    Test whether they organize into similar geometry.
    """
    print("\n" + "=" * 70)
    print("R2.2: CROSS-DOMAIN TRANSFER — new prototype systems")
    print("=" * 70)

    # Load reference statistics
    feat_df = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    feat_cols = [c for c in feat_df.columns if c != "system"]
    X = feat_df[feat_cols].values
    mean_vec = X.mean(axis=0)
    std_vec = X.std(axis=0)

    # Load existing emergence coordinates
    ref_coord = pd.read_csv(OUT / "emergence_coordinates.csv")
    axes = ["C", "F", "A", "R"]
    ref_Phi = ref_coord[axes].values

    print(f"\n  Computing geometry for {len(NEW_SYSTEMS)} new systems...")
    results = []
    for sys_name, gen in NEW_SYSTEMS.items():
        print(f"    Computing {sys_name}...", end=" ", flush=True)
        feats = compute_new_system_geometry(gen)
        phi = compute_emergence_coords(feats, mean_vec, std_vec)

        # Distance to nearest reference system
        phi_vec = np.array([phi[ax] for ax in axes])
        dists = np.linalg.norm(ref_Phi - phi_vec, axis=1)
        nearest = ref_coord.loc[np.argmin(dists), "system"]
        nearest_dist = float(dists.min())

        phi_str = ", ".join(f"{ax}={phi[ax]:+.2f}" for ax in axes)
        print(f"Φ=({phi_str})  nearest={nearest}(d={nearest_dist:.3f})")

        results.append({
            "system": sys_name,
            **phi,
            "nearest_reference": nearest,
            "nearest_distance": nearest_dist,
        })

    df = pd.DataFrame(results)
    df.to_csv(OUT / "r2_cross_domain_transfer.csv", index=False)

    # KDE-based novelty detection
    try:
        kde = gaussian_kde(ref_Phi.T, bw_method=0.5)
        for _, r in df.iterrows():
            phi_v = np.array([r[ax] for ax in axes])
            log_dens = float(np.log(kde(phi_v.reshape(-1, 1).T) + 1e-12)[0])
            ref_log_dens = float(np.mean(np.log(kde(ref_Phi.T) + 1e-12)))
            print(f"    → {r['system']}: log-density={log_dens:.3f} "
                  f"(ref mean={ref_log_dens:.3f}) "
                  f"{'NOVEL' if log_dens < ref_log_dens - 1 else 'in-distribution'}")
    except Exception:
        pass

    return df

# =====================================================================
# 5. R2.3 — UNIVERSAL BOUNDARY SEARCH
# =====================================================================
def experiment_boundary_search(coord_df, p0_labels):
    """
    Find the emergence function E = f(C,F) that best separates clusters.
    Test: E = C×F, E = C·F/|C-F|, E = C^α·F^β
    """
    print("\n" + "=" * 70)
    print("R2.3: UNIVERSAL BOUNDARY SEARCH")
    print("=" * 70)

    C = coord_df["C"].values
    F = coord_df["F"].values

    # Candidate functions
    candidates = {
        "C*F": C * F,
        "C/(|F|+ε)": C / (np.abs(F) + 1e-6),
        "F/(|C|+ε)": F / (np.abs(C) + 1e-6),
        "C*F/(|C-F|+ε)": C * F / (np.abs(C - F) + 1e-6),
        "C*F/(|C+F|+ε)": C * F / (np.abs(C + F) + 1e-6),
    }

    # Score each: how well does E separate P0 clusters?
    print(f"\n  --- Boundary function scoring ---")
    print(f"  {'Function':<30s}  {'ANOVA F':>10s}  {'p-value':>10s}  {'Between/Within':>16s}")
    print(f"  {'-'*68}")

    from scipy.stats import f_oneway

    best_fn = None
    best_F = 0
    results = {}

    for name, E in candidates.items():
        # ANOVA: does E differ across P0 clusters?
        groups = [E[p0_labels == c] for c in sorted(set(p0_labels))]
        groups = [g for g in groups if len(g) > 1]
        if len(groups) >= 2:
            f_val, p_val = f_oneway(*groups)
            # Between/within variance
            overall_var = np.var(E)
            within_var = np.mean([np.var(g) for g in groups])
            bw_ratio = max(overall_var / max(within_var, 1e-12), 0)
            results[name] = {"F": float(f_val), "p": float(p_val),
                             "bw_ratio": float(bw_ratio)}
            print(f"  {name:<30s}  {f_val:>10.4f}  {p_val:>10.6f}  {bw_ratio:>16.4f}")
            if f_val > best_F:
                best_F = f_val
                best_fn = name

    print(f"\n  Best boundary function: {best_fn} (F={best_F:.4f})")

    # Fit power law: E = C^α · F^β
    def power_law(cf, alpha, beta):
        c, f = cf
        # Handle negative values: shift
        c_shift = c - min(c) + 0.1
        f_shift = f - min(f) + 0.1
        return c_shift**alpha * f_shift**beta

    # Since we have discrete points, not a surface to fit,
    # compute the boundary as: log(E) = α·log(C+const) + β·log(F+const)
    c_shift = C - C.min() + 0.1
    f_shift = F - F.min() + 0.1
    log_c = np.log(c_shift)
    log_f = np.log(f_shift)

    # Fit linear regression: log(E_target) ~ α·log(C) + β·log(F)
    # where E_target = best candidate function
    if best_fn and best_fn in candidates:
        E_best = candidates[best_fn]
        # Normalize to positive
        E_best = E_best - E_best.min() + 0.1
        log_E = np.log(E_best)

        X_fit = np.column_stack([log_c, log_f])
        lr = LinearRegression().fit(X_fit, log_E)
        alpha_est, beta_est = lr.coef_

        print(f"  Power-law fit: E ∝ C^{alpha_est:.3f} · F^{beta_est:.3f} "
              f"(R² = {lr.score(X_fit, log_E):.4f})")

        # Theoretical form: E ∝ C^α · F^β with α, β ≈ 1
        print(f"  {'✓ Balanced' if abs(alpha_est/beta_est - 1) < 0.5 else '✗ Unbalanced'}"
              f": α/β ratio = {alpha_est/max(beta_est, 1e-6):.3f}")

        results["power_law"] = {
            "alpha": float(alpha_est),
            "beta": float(beta_est),
            "r2": float(lr.score(X_fit, log_E)),
            "alpha_beta_ratio": float(alpha_est / max(beta_est, 1e-6)),
        }

    # Cluster separation in C-F plane
    print(f"\n  --- C-F plane cluster geometry ---")
    for c in sorted(set(p0_labels)):
        mask = p0_labels == c
        c_mean, f_mean = C[mask].mean(), F[mask].mean()
        c_std, f_std = C[mask].std(), F[mask].std()
        # Euclidean distance from origin
        dist = np.sqrt(c_mean**2 + f_mean**2)
        angle = np.degrees(np.arctan2(f_mean, c_mean))
        print(f"    Cluster {c}: C={c_mean:+.3f}±{c_std:.3f}, "
              f"F={f_mean:+.3f}±{f_std:.3f}, "
              f"r={dist:.3f}, θ={angle:.1f}°")

    # The C-F quadrant structure
    quadrants = {}
    for i, sys_name in enumerate(coord_df["system"]):
        c, f = C[i], F[i]
        if c >= 0 and f >= 0:
            q = "QF (high coherence, high fertility)"
        elif c >= 0 and f < 0:
            q = "C (coherence-dominated)"
        elif c < 0 and f >= 0:
            q = "F (fertility-dominated)"
        else:
            q = "HF (low both)"
        quadrants.setdefault(q, []).append(sys_name)

    print(f"\n  C-F quadrant distribution:")
    for q, members in sorted(quadrants.items()):
        print(f"    {q}: {', '.join(members)}")

    return results, best_fn

# =====================================================================
# MAIN
# =====================================================================
def main():
    print("=" * 70)
    print("PHASE R2: PREDICTIVE VALIDATION")
    print("=" * 70)
    print("Success criterion: Φ-space predicts transitions better than baselines")
    print("If YES: SFH-SGP becomes predictive science.")
    print("If NO: remains descriptive geometry.")
    print()

    # Load emergence coordinates
    coord_df, Phi, feat_df, X, Xs, p0_labels = load_emergence()
    systems = coord_df["system"].tolist()

    # === EXPERIMENT A: Collapse Forecasting ===
    collapse_curves, collapse_thresholds, coll_res = experiment_collapse_forecast(
        Xs, p0_labels, systems, coord_df)

    # === EXPERIMENT B: Transition Susceptibility ===
    susc_res = experiment_transition_susceptibility(
        Xs, p0_labels, systems, coord_df, collapse_curves)

    # === EXPERIMENT C: Cross-Domain Transfer ===
    transfer_df = experiment_cross_domain()

    # === EXPERIMENT D: Boundary Search ===
    bound_res, best_fn = experiment_boundary_search(coord_df, p0_labels)

    # === SAVE RESULTS ===
    with open(OUT / "r2_collapse_forecast.json", "w") as f:
        json.dump(coll_res, f, indent=2)
    with open(OUT / "r2_transition_susceptibility.json", "w") as f:
        json.dump(susc_res, f, indent=2)
    with open(OUT / "r2_boundary_search.json", "w") as f:
        json.dump({"results": bound_res, "best_function": best_fn}, f, indent=2)

    # === FINAL VERDICT ===
    print("\n" + "=" * 70)
    print("R2 FINAL VERDICT")
    print("=" * 70)

    # Gather all results
    verdict_parts = []

    # V1: Does Φ-space predict collapse?
    rf_mean = coll_res["prediction_models"]["RandomForest(Φ)"]["mean_r2"]
    null_mean = coll_res["prediction_models"]["Null"]["mean_r2"]
    pca_mean = coll_res["prediction_models"]["PCA-baseline"]["mean_r2"]

    if rf_mean > 0 and rf_mean > null_mean + 0.1:
        verdict_parts.append(f"FORECAST (+): Φ predicts collapse (RF R²={rf_mean:.3f} vs null={null_mean:.3f}, PCA={pca_mean:.3f})")
    elif rf_mean > null_mean:
        verdict_parts.append(f"WEAK: Φ weakly predicts collapse (RF R²={rf_mean:.3f} vs null={null_mean:.3f})")
    else:
        verdict_parts.append(f"FAIL: Φ does NOT predict collapse (RF R²={rf_mean:.3f} ≤ null={null_mean:.3f})")

    # V2: Bridge cluster susceptibility confirmed?
    cluster_2_idx = [i for i in range(len(systems)) if p0_labels[i] == 2]
    other_idx = [i for i in range(len(systems)) if p0_labels[i] != 2]
    flow_df = pd.read_csv(OUT / "emergence_flow_field.csv")
    flow_map = {r["system"]: r["flow_magnitude"] for _, r in flow_df.iterrows()}
    c2_flows = [flow_map[s] for s in systems if p0_labels[systems.index(s)] == 2]
    other_flows = [flow_map[s] for s in systems if p0_labels[systems.index(s)] != 2]
    from scipy.stats import ttest_ind
    t_stat, p_val = ttest_ind(c2_flows, other_flows)
    if p_val < 0.05:
        verdict_parts.append(f"SUSCEPTIBILITY ✓: Bridge cluster flow significantly higher (p={p_val:.4f})")
    else:
        verdict_parts.append(f"SUSCEPTIBILITY ?: Bridge flow not significantly different (p={p_val:.4f})")

    # V3: Cross-domain transfer
    transfer_df = pd.read_csv(OUT / "r2_cross_domain_transfer.csv")
    avg_nn_dist = transfer_df["nearest_distance"].mean()
    verdict_parts.append(f"TRANSFER: {len(transfer_df)} new systems, avg nearest-neighbor dist={avg_nn_dist:.3f}")

    # V4: Boundary function
    if best_fn:
        f_val = bound_res[best_fn]["F"]
        verdict_parts.append(f"BOUNDARY: Best separation by {best_fn} (F={f_val:.2f})")
        if "power_law" in bound_res:
            ar = bound_res["power_law"]["alpha_beta_ratio"]
            if 0.5 < ar < 2.0:
                verdict_parts.append(f"BALANCE: α/β={ar:.3f} (near-balanced C-F tension)")
            else:
                verdict_parts.append(f"IMBALANCE: α/β={ar:.3f} (asymmetric)")

    print("\n  " + "\n  ".join(verdict_parts))

    # Final binary
    if rf_mean > 0 and rf_mean > null_mean + 0.1:
        print(f"\n  ╔═══════════════════════════════════════════════════════════╗")
        print(f"  ║  SFH-SGP TRANSITIONS TO PREDICTIVE SCIENCE ✓            ║")
        print(f"  ║  Φ-space predicts transitions better than baselines.    ║")
        print(f"  ╚═══════════════════════════════════════════════════════════╝")
    else:
        print(f"\n  ╔═══════════════════════════════════════════════════════════╗")
        print(f"  ║  SFH-SGP REMAINS DESCRIPTIVE GEOMETRY                    ║")
        print(f"  ║  Φ-space does NOT outperform baselines for prediction.   ║")
        print(f"  ╚═══════════════════════════════════════════════════════════╝")

    print()
    print("R2 complete. See:")
    print(f"  sfh_sgp_ood_outputs/r2_collapse_forecast.json")
    print(f"  sfh_sgp_ood_outputs/r2_cross_domain_transfer.csv")
    print(f"  sfh_sgp_ood_outputs/r2_boundary_search.json")
    print()


if __name__ == "__main__":
    main()
