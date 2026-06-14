#!/usr/bin/env python3
"""Compare all metrics on recovery data: which best detects perturbation and predicts recovery?

Granular: sliding window for C, I_pred, C_sigma, MSE — compare dip signal
Forest: pre/post metrics per plot — which separates recovery vs collapse?

The key question: does C predict recovery better than competitors?
"""

import sys, json, numpy as np
sys.path.insert(0, ".")
from metrics import *
from adapters.ecosystem import EcosystemAdapter
from adapters.granular import GranularAdapter

np.random.seed(42)


def _drop_extinct(X):
    mask = np.nanvar(X, axis=1) > 1e-10
    return X[mask] if mask.sum() >= 2 else X


def metric_trajectory(X: np.ndarray, window: int, step: int) -> dict:
    """Compute C, I_pred, C_sigma, MSE at each sliding window."""
    T = X.shape[1]
    times, c_vals, ip_vals, cs_vals, mse_vals = [], [], [], [], []
    for t in range(0, T - window + 1, step):
        seg = X[:, t:t + window]
        seg = _drop_extinct(seg)
        times.append(t + window // 2)
        c_vals.append(compute_C(seg, "gaussian"))
        try:
            ip_vals.append(compute_predictive_information(seg, tau=1))
        except Exception:
            ip_vals.append(np.nan)
        try:
            cs_vals.append(compute_statistical_complexity(seg, tau=1))
        except Exception:
            cs_vals.append(np.nan)
        try:
            mse_vals.append(compute_mse(seg, scales=[1]).get(1, np.nan))
        except Exception:
            mse_vals.append(np.nan)
    return {
        "times": times,
        "C": c_vals, "I_pred": ip_vals,
        "C_sigma": cs_vals, "MSE_s1": mse_vals,
    }


def dip_score(traj: dict) -> dict:
    """Quantify perturbation detectability for each metric.

    Signal-to-noise: (pre_mean - post_min) / (pre_std + 1e-10)
    """
    scores = {}
    for name in ["C", "I_pred", "C_sigma", "MSE_s1"]:
        vals = np.array(traj[name])
        if np.all(np.isnan(vals)):
            scores[name] = {"dip": np.nan, "snr": np.nan}
            continue
        pre = vals[(np.array(traj["times"]) >= 400) & (np.array(traj["times"]) < 500)]
        post = vals[(np.array(traj["times"]) >= 500) & (np.array(traj["times"]) <= 600)]
        if len(pre) < 2 or len(post) < 2:
            scores[name] = {"dip": np.nan, "snr": np.nan}
            continue
        pre_mean, pre_std = np.nanmean(pre), np.nanstd(pre)
        post_min = np.nanmin(post)
        dip = float(pre_mean - post_min)
        snr = float(dip / max(pre_std, 1e-10))
        scores[name] = {"dip": round(dip, 4), "snr": round(snr, 2)}
    return scores


def granular_analysis():
    print("\n" + "=" * 70)
    print("  COMPETITOR COMPARISON: GRANULAR RECOVERY")
    print("=" * 70)

    X, _ = GranularAdapter().load()
    traj = metric_trajectory(X, window=200, step=20)
    scores = dip_score(traj)

    print(f"\n  {'Metric':>12s}  {'Dip':>8s}  {'SNR':>8s}")
    print("  " + "-" * 30)
    for name in ["C", "I_pred", "C_sigma", "MSE_s1"]:
        s = scores[name]
        print(f"  {name:>12s}  {s['dip']:>8.4f}  {s['snr']:>8.2f}")

    print(f"\n  Winner (highest SNR): {max(scores, key=lambda n: scores[n]['snr'])}")
    t_arr = np.array(traj["times"])
    for name in traj:
        if name == "times":
            continue
        vals = np.array(traj[name], dtype=float)
        pre_vals = vals[(t_arr >= 400) & (t_arr < 500)]
        post_vals = vals[(t_arr >= 500) & (t_arr <= 600)]
        rec_vals = vals[(t_arr >= 600) & (t_arr <= 800)]
        p_mean = float(np.nanmean(pre_vals)) if not np.all(np.isnan(pre_vals)) else None
        po_min = float(np.nanmin(post_vals)) if not np.all(np.isnan(post_vals)) else None
        r_max = float(np.nanmax(rec_vals)) if not np.all(np.isnan(rec_vals)) else None
        if p_mean is not None:
            print(f"\n  {name}:")
            print(f"    Pre  = {p_mean:.4f}")
            if po_min is not None:
                print(f"    Min  = {po_min:.4f} (Δ = {p_mean - po_min:.4f})")
            if r_max is not None and p_mean > 0:
                print(f"    Post = {r_max:.4f} (restored to {r_max / p_mean * 100:.0f}% of pre)")

    return {"trajectory": traj, "dip_scores": scores}


def _per_plot_metrics(X: np.ndarray, drought: int) -> dict:
    """All metrics on one plot, pre and post drought."""
    X = _drop_extinct(X)
    pre = X[:, :drought]
    post = X[:, drought + 1:]
    if pre.shape[1] < 3 or post.shape[1] < 3:
        return {}
    def _safe(fn, x):
        try: return fn(x, tau=1)
        except Exception: return np.nan
    return {
        "pre_C": compute_C(pre, "gaussian"),
        "post_C": compute_C(post, "gaussian"),
        "pre_I_pred": _safe(compute_predictive_information, pre),
        "post_I_pred": _safe(compute_predictive_information, post),
        "pre_C_sigma": _safe(compute_statistical_complexity, pre),
        "post_C_sigma": _safe(compute_statistical_complexity, post),
        "pre_MSE_s1": compute_mse(pre, scales=[1]).get(1, np.nan),
        "post_MSE_s1": compute_mse(post, scales=[1]).get(1, np.nan),
    }


def forest_analysis():
    print("\n" + "=" * 70)
    print("  COMPETITOR COMPARISON: FOREST SUCCESSION")
    print("=" * 70)

    adapter = EcosystemAdapter(n_plots=24)
    all_plots = adapter.load_all_plots()

    metrics_by_plot = []
    for i, (X, meta) in enumerate(all_plots):
        m = _per_plot_metrics(X, meta["perturbation_time"])
        if m:
            m["plot"] = i
            m["recovered"] = m["post_C"] > 0.5 * m["pre_C"]
            metrics_by_plot.append(m)

    recovered = [m for m in metrics_by_plot if m["recovered"]]
    collapsed = [m for m in metrics_by_plot if not m["recovered"]]

    # Compute separation for each metric: how well does the CHANGE in each
    # metric discriminate recovery from collapse?
    print(f"\n  {'Metric':>15s}  {'Δ in Recovery':>14s}  {'Δ in Collapse':>14s}  {'Separation':>10s}")
    print("  " + "-" * 55)
    for name in ["C", "I_pred", "C_sigma", "MSE_s1"]:
        pre_k = f"pre_{name}"
        post_k = f"post_{name}"
        rec_deltas = [m[post_k] / max(m[pre_k], 1e-10) for m in recovered if pre_k in m and post_k in m]
        col_deltas = [m[post_k] / max(m[pre_k], 1e-10) for m in collapsed if pre_k in m and post_k in m]
        if not rec_deltas or not col_deltas:
            continue
        r_avg = float(np.mean(rec_deltas))
        c_avg = float(np.mean(col_deltas))
        sep = r_avg - c_avg
        print(f"  {name:>15s}  {r_avg:>14.3f}  {c_avg:>14.3f}  {sep:>+10.3f}")

    print(f"\n  Recovery plots:  {len(recovered)}")
    print(f"  Collapse plots:  {len(collapsed)}")
    print(f"  Total:           {len(metrics_by_plot)}")
    print(f"\n  C restoration:    {np.mean([m['post_C']/max(m['pre_C'],1e-10) for m in recovered]):.2%}")
    print(f"  I_pred change:    {np.mean([m['post_I_pred']/max(m['pre_I_pred'],1e-10) for m in recovered]):.2f}")
    print(f"  MSE change:       {np.mean([m['post_MSE_s1']/max(m['pre_MSE_s1'],1e-10) for m in recovered]):.2f}")

    return {"per_plot": metrics_by_plot}


def print_summary(granular, forest):
    g_scores = granular["dip_scores"]
    best_g = max(g_scores, key=lambda n: g_scores[n]["snr"])

    f_plots = forest["per_plot"]
    rec = [p for p in f_plots if p["recovered"]]
    col = [p for p in f_plots if not p["recovered"]]

    print("\n" + "=" * 70)
    print("  COMPETITOR COMPARISON — SUMMARY")
    print("=" * 70)

    print(f"""
  Granular perturbation detection (highest SNR):
    Best: {best_g} (SNR = {g_scores[best_g]['snr']:.1f})
    C SNR:    {g_scores['C']['snr']:.1f}

  Forest recovery vs collapse separation:
    C:        {np.mean([p['post_C']/max(p['pre_C'],1e-10) for p in rec]):.2f} rec vs {np.mean([p['post_C']/max(p['pre_C'],1e-10) for p in col]):.2f} col
    MSE_s1:   {np.mean([p['post_MSE_s1']/max(p['pre_MSE_s1'],1e-10) for p in rec]):.2f} rec vs {np.mean([p['post_MSE_s1']/max(p['pre_MSE_s1'],1e-10) for p in col]):.2f} col
    I_pred:   {np.mean([p['post_I_pred']/max(p['pre_I_pred'],1e-10) for p in rec]):.2f} rec vs {np.mean([p['post_I_pred']/max(p['pre_I_pred'],1e-10) for p in col]):.2f} col
""")


if __name__ == "__main__":
    g = granular_analysis()
    f = forest_analysis()
    print_summary(g, f)
