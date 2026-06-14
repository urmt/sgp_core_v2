"""Resilience prediction ensemble: does pre-perturbation C predict recovery?

Design:
  - MAR(1) process with block-structured coupling matrix
  - 6 coupling ratios × 10 replicates = 60 systems
  - Perturbation: temporarily zero all cross-couplings
  - Question: which pre-perturbation metric best predicts recovery?

  If pre-C (or any metric) correlates with ΔC, τ_rec, or C_final/C_pre
  across coupling ratios, that metric contains predictive information
  about system resilience.
"""

import numpy as np
import sys
sys.path.insert(0, ".")

from metrics import *

SEED = 42
rng = np.random.default_rng(SEED)


def _solve_lyapunov(A, Q, max_iter=10000):
    """Solve Σ = A Σ A^T + Q for stationary covariance (discrete)."""
    n = A.shape[0]
    Sigma = np.eye(n) * 0.1
    for _ in range(max_iter):
        Sigma_new = A @ Sigma @ A.T + Q
        err = np.max(np.abs(Sigma_new - Sigma))
        Sigma = Sigma_new
        if err < 1e-10:
            break
    return Sigma


def generate_mar_ensemble(
    d=20, n_communities=4, T=500,
    coupling_within=0.7, coupling_between=0.1,
    noise_scale=0.3, seed=None,
):
    """MAR(1): X_t = A @ X_{t-1} + ε_t.

    A has block structure: strong within-community coupling,
    weak between-community coupling.
    """
    if seed is not None:
        np.random.default_rng(seed)

    comm_size = d // n_communities
    labels = np.repeat(range(n_communities), comm_size)[:d]

    A = np.zeros((d, d))
    for i in range(d):
        for j in range(d):
            if labels[i] == labels[j]:
                A[i, j] = coupling_within / comm_size
            else:
                A[i, j] = coupling_between / (d - comm_size)

    np.fill_diagonal(A, coupling_within)

    spectral_radius = max(abs(np.linalg.eigvals(A)))
    if spectral_radius >= 1.0:
        A = A / (spectral_radius * 1.05)

    Q = np.eye(d) * noise_scale**2
    Sigma = _solve_lyapunov(A, Q)

    # Generate
    X = np.zeros((d, T))
    X[:, 0] = rng.multivariate_normal(np.zeros(d), Sigma)
    for t in range(1, T):
        X[:, t] = A @ X[:, t - 1] + rng.normal(0, noise_scale, d)

    return X, labels, A, Sigma


def apply_perturbation(X, A, noise_scale, pert_start=250, pert_length=50):
    """Zero out all cross-couplings, keep only diagonal."""
    d = X.shape[0]
    T = X.shape[1]

    A_pert = np.zeros_like(A)
    np.fill_diagonal(A_pert, np.diag(A))

    X_pert = X.copy()
    for t in range(pert_start, min(pert_start + pert_length, T)):
        X_pert[:, t] = A_pert @ X_pert[:, t - 1] + rng.normal(0, noise_scale, d)

    for t in range(pert_start + pert_length, T):
        X_pert[:, t] = A @ X_pert[:, t - 1] + rng.normal(0, noise_scale, d)

    return X_pert


def _sliding_metric(X, window=50, step=10):
    """Compute C and competitors at each sliding window."""
    T = X.shape[1]
    times, c_vals, ip_vals, cs_vals, ms_vals = [], [], [], [], []
    for t in range(0, T - window + 1, step):
        seg = X[:, t:t + window]
        times.append(t + window // 2)
        try:
            c_vals.append(compute_C(seg, "gaussian"))
        except Exception:
            c_vals.append(np.nan)
        try:
            ip_vals.append(compute_predictive_information(seg, tau=1))
        except Exception:
            ip_vals.append(np.nan)
        try:
            cs_vals.append(compute_statistical_complexity(seg, tau=1))
        except Exception:
            cs_vals.append(np.nan)
        try:
            ms_vals.append(compute_mse(seg, scales=[1]).get(1, np.nan))
        except Exception:
            ms_vals.append(np.nan)
    return np.array(times), np.array(c_vals), np.array(ip_vals), np.array(cs_vals), np.array(ms_vals)


def measure_recovery(times, metric_vals, pert_start=250, pert_end=300):
    """Extract ΔC, τ_rec, restoration fraction from trajectory."""
    pre = metric_vals[(times >= 100) & (times < pert_start)]
    pert = metric_vals[(times >= pert_start) & (times < pert_end)]
    post = metric_vals[(times >= pert_end) & (times < pert_end + 200)]

    if len(pre) < 2 or len(pert) < 2 or len(post) < 2:
        return {"pre": np.nan, "dip": np.nan, "restoration": np.nan, "tau_rec": np.nan}

    pre_mean = np.nanmean(pre)
    pert_min = np.nanmin(pert) if np.any(~np.isnan(pert)) else pre_mean
    delta = pre_mean - pert_min

    post_vals = post[~np.isnan(post)]
    if len(post_vals) < 2:
        return {"pre": pre_mean, "dip": delta, "restoration": np.nan, "tau_rec": np.nan}

    post_final = np.nanmean(post_vals[-10:])
    restoration = post_final / max(pre_mean, 1e-10)

    # Recovery time: first point where value >= pre_mean
    tau = np.nan
    for k, v in enumerate(post):
        if not np.isnan(v) and v >= pre_mean:
            tau = times[len(pre) + len(pert) + k] - pert_end
            break

    return {
        "pre": float(pre_mean),
        "dip": float(delta),
        "restoration": float(restoration),
        "tau_rec": float(tau) if not np.isnan(tau) else float(len(post)),
    }


def run_ensemble():
    print("=" * 78)
    print("  RESILIENCE PREDICTION ENSEMBLE")
    print("  Does pre-perturbation C predict recovery?")
    print("=" * 78)

    coupling_ratios = [1.5, 2.0, 3.0, 5.0, 8.0, 12.0]
    n_replicates = 10
    metric_names = ["C", "I_pred", "C_sigma", "MSE_s1"]

    rows = []
    for ratio in coupling_ratios:
        coupling_within = min(0.85, 0.15 * ratio)
        coupling_between = 0.15
        for rep in range(n_replicates):
            X, labels, A, Sigma = generate_mar_ensemble(
                d=20, n_communities=4, T=500,
                coupling_within=coupling_within,
                coupling_between=coupling_between,
                noise_scale=0.3,
            )
            X_pert = apply_perturbation(X, A, noise_scale=0.3)

            times, c, ip, cs, ms = _sliding_metric(X_pert)
            rec = {name: measure_recovery(times, vals)
                   for name, vals in zip(metric_names, [c, ip, cs, ms])}

            row = {
                "ratio": ratio,
                "rep": rep,
                "coupling_within": coupling_within,
            }
            for name in metric_names:
                row[f"{name}_pre"] = rec[name]["pre"]
                row[f"{name}_dip"] = rec[name]["dip"]
                row[f"{name}_rest"] = rec[name]["restoration"]
                row[f"{name}_tau"] = rec[name]["tau_rec"]
            rows.append(row)

    # Print results
    print(f"\n  {'Ratio':>6s}  {'Metric':>8s}  {'Pre-C':>8s}  {'Dip':>8s}  {'Rest.':>8s}  {'Tau':>6s}")
    print(f"  {'-' * 46}")
    for ratio in coupling_ratios:
        r_rows = [r for r in rows if abs(r["ratio"] - ratio) < 0.01]
        for name in metric_names:
            pres = np.array([r[f"{name}_pre"] for r in r_rows])
            dips = np.array([r[f"{name}_dip"] for r in r_rows])
            rests = np.array([r[f"{name}_rest"] for r in r_rows])
            taus = np.array([r[f"{name}_tau"] for r in r_rows])

            if np.all(np.isnan(pres)):
                continue

            p_mean = np.nanmean(pres)
            d_mean = np.nanmean(dips)
            r_mean = np.nanmean(rests)
            t_mean = np.nanmean(taus)

            print(f"  {ratio:>6.1f}  {name:>8s}  {p_mean:>8.4f}  {d_mean:>8.4f}  {r_mean:>8.4f}  {t_mean:>6.0f}")

    # Correlation analysis
    print(f"\n{'=' * 78}")
    print("  CORRELATION: PRE-PERTURBATION METRIC → RECOVERY OUTCOME")
    print("=" * 78)

    from scipy.stats import pearsonr, spearmanr

    target_metrics = ["dip", "rest", "tau"]
    target_labels = ["Δ (dip depth)", "C_final/C_pre", "τ_rec (steps)"]

    print(f"\n  PEARSON R (across all {len(rows)} systems):")
    print(f"\n  {'Metric':>8s}  {'→ ΔC':>8s}  {'→ Rest.':>8s}  {'→ τ':>8s}")
    print(f"  {'-' * 34}")
    for name in metric_names:
        vals = np.array([r[f"{name}_pre"] for r in rows])
        if np.all(np.isnan(vals)):
            continue
        corrs = []
        for target in target_metrics:
            tgt = np.array([r[f"{name}_{target}"] for r in rows])
            valid = ~(np.isnan(vals) | np.isnan(tgt))
            if valid.sum() > 5:
                r_val, p = pearsonr(vals[valid], tgt[valid])
                corrs.append(r_val)
            else:
                corrs.append(np.nan)
        print(f"  {name:>8s}  {corrs[0]:>+8.3f}  {corrs[1]:>+8.3f}  {corrs[2]:>+8.3f}")

    print(f"\n  SPEARMAN RHO:")
    print(f"\n  {'Metric':>8s}  {'→ ΔC':>8s}  {'→ Rest.':>8s}  {'→ τ':>8s}")
    print(f"  {'-' * 34}")
    for name in metric_names:
        vals = np.array([r[f"{name}_pre"] for r in rows])
        if np.all(np.isnan(vals)):
            continue
        corrs = []
        for target in target_metrics:
            tgt = np.array([r[f"{name}_{target}"] for r in rows])
            valid = ~(np.isnan(vals) | np.isnan(tgt))
            if valid.sum() > 5:
                r_val, p = spearmanr(vals[valid], tgt[valid])
                corrs.append(r_val)
            else:
                corrs.append(np.nan)
        print(f"  {name:>8s}  {corrs[0]:>+8.3f}  {corrs[1]:>+8.3f}  {corrs[2]:>+8.3f}")

    # Best predictor summary
    print(f"\n{'=' * 78}")
    print("  BEST PREDICTOR PER TARGET")
    print("=" * 78)
    for target, label in zip(target_metrics, target_labels):
        best_name = None
        best_r = -2.0
        for name in metric_names:
            vals = np.array([r[f"{name}_pre"] for r in rows])
            tgt = np.array([r[f"{name}_{target}"] for r in rows])
            valid = ~(np.isnan(vals) | np.isnan(tgt))
            if valid.sum() > 5:
                r_val, p = pearsonr(vals[valid], tgt[valid])
                if r_val > best_r:
                    best_r = r_val
                    best_name = name
        if best_name:
            print(f"  {label:>20s} → {best_name:>8s}  (r = {best_r:+.3f})")

    return rows


if __name__ == "__main__":
    rows = run_ensemble()
