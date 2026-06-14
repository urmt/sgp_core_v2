#!/usr/bin/env python3
"""Recovery analysis on pilot datasets.

Computes C(t) via sliding window. Tests whether coherence restores
after perturbation — the core prediction of the coherence hypothesis.

Pilot A (forest succession): drought perturbation at t=5 (year 1988)
Pilot B (granular relaxation): 10% grain removal at t=500
"""

import sys, time, json
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress

sys.path.insert(0, ".")
from metrics import *
from adapters.ecosystem import EcosystemAdapter
from adapters.granular import GranularAdapter

np.random.seed(42)


def _drop_extinct(X: np.ndarray) -> np.ndarray:
    mask = np.nanvar(X, axis=1) > 1e-10
    if mask.sum() < 2:
        return X
    return X[mask]


def sliding_C(
    X: np.ndarray, window: int = 8, step: int = 2,
) -> tuple[np.ndarray, np.ndarray]:
    X = _drop_extinct(X)
    T = X.shape[1]
    times, c_vals = [], []
    for t in range(0, T - window + 1, step):
        seg = X[:, t:t + window]
        c = compute_C(seg, estimator="gaussian")
        times.append(t + window // 2)
        c_vals.append(c)
    return np.array(times), np.array(c_vals)


def analyze_forest_succession() -> dict:
    print("\n" + "=" * 70)
    print("  PILOT A: FOREST SUCCESSION — RECOVERY ANALYSIS")
    print("=" * 70)

    adapter = EcosystemAdapter(n_plots=24)
    all_plots = adapter.load_all_plots()
    per_plot = []
    n_rec, n_low = 0, 0
    pre_all, post_all = [], []

    for i, (X, meta) in enumerate(all_plots):
        X = _drop_extinct(X)
        drought = meta["perturbation_time"]
        pre_c = compute_C(X[:, :drought], "gaussian")
        post_c = compute_C(X[:, drought + 1:], "gaussian")
        pre_all.append(pre_c)
        post_all.append(post_c)
        recovered = bool(post_c > 0.5 * pre_c)
        n_rec += 1 if recovered else 0
        n_low += 0 if recovered else 1

        times, c_vals = sliding_C(X, window=8, step=2)
        post_mask = times >= drought + 1
        if post_mask.sum() >= 3 and recovered:
            models = _fit_models(times[post_mask], c_vals[post_mask])
        else:
            models = {}

        per_plot.append({
            "plot": i, "n_species": int(X.shape[0]),
            "pre_C": float(pre_c), "post_C": float(post_c),
            "recovered": recovered,
        })

    pre_avg = float(np.mean(pre_all))
    post_avg_recovered = float(np.mean([p["post_C"] for p in per_plot if p["recovered"]]))
    post_avg_all = float(np.mean(post_all))

    print(f"\n  Plots: {len(all_plots)}")
    print(f"  Pre-perturbation C:          {pre_avg:.4f}")
    print(f"  Post-perturbation C (all):    {post_avg_all:.4f}")
    print(f"  Post-perturbation C (recovered only): {post_avg_recovered:.4f}")
    print(f"  Recovery rate (post > 50% pre): {n_rec}/{n_rec + n_low}")
    print(f"  C restoration in recovered plots: {post_avg_recovered/pre_avg*100:.1f}% of pre")

    return {
        "name": "forest_succession",
        "n_plots": len(all_plots),
        "pre_C_avg": pre_avg,
        "post_C_avg_all": post_avg_all,
        "post_C_avg_recovered": post_avg_recovered,
        "n_recovered": n_rec,
        "n_collapsed": n_low,
        "restoration_pct": post_avg_recovered / pre_avg * 100 if pre_avg > 0 else 0,
        "per_plot": per_plot,
    }


def analyze_granular() -> dict:
    print("\n" + "=" * 70)
    print("  PILOT B: GRANULAR RELAXATION — RECOVERY ANALYSIS")
    print("=" * 70)

    X, meta = GranularAdapter().load()
    removal = meta["perturbation_time"]

    times, c_vals = sliding_C(X, window=200, step=20)
    pre_mean = float(np.mean(c_vals[(times >= 400) & (times < 500)]))
    post_window = c_vals[(times >= 500) & (times <= 600)]
    post_min = float(np.min(post_window))
    rec_window = c_vals[(times >= 600) & (times <= 800)]
    post_rec = float(np.max(rec_window)) if len(rec_window) else None
    final = float(np.mean(c_vals[-5:]))

    dip = pre_mean - post_min
    recovery_t = None
    if post_rec and post_rec > pre_mean:
        for ti, ci in zip(times, c_vals):
            if ti >= 500 and ci >= pre_mean:
                recovery_t = int(ti) - 500
                break

    print(f"\n  Pre-removal C (t=400-500):   {pre_mean:.4f}")
    print(f"  Post-removal min (t=500-600): {post_min:.4f}")
    print(f"  Dip magnitude:                {dip:.4f} ({dip/pre_mean*100:.1f}%)")
    print(f"  Recovery to baseline:         {recovery_t} steps" if recovery_t else "  Recovery to baseline:         not observed")
    print(f"  Final C (last 5 windows):     {final:.4f}")
    print(f"  Restoration:                  {'YES' if final > pre_mean * 0.8 else 'NO'}")

    print(f"\n  Sliding window C(t):")
    print(f"  {'time':>6s}  {'C':>8s}")
    for ti, ci in zip(times, c_vals):
        marker = "  <-- removal" if ti == 500 else ""
        print(f"  {ti:6d}  {ci:.6f}{marker}")

    return {
        "name": "granular_relaxation",
        "pre_C": pre_mean,
        "post_min": post_min,
        "dip_magnitude": float(dip),
        "dip_pct": float(dip / pre_mean * 100),
        "recovery_steps": recovery_t,
        "final_C": final,
        "restoration": final > pre_mean * 0.8,
        "times": times.tolist(),
        "C_trajectory": c_vals.tolist(),
    }


def _fit_models(t: np.ndarray, C: np.ndarray) -> dict:
    results = {}
    def logistic(x, C_eq, r, t0):
        return C_eq / (1 + np.exp(-r * (x - t0)))
    def exponential(x, C0, beta):
        return C0 * np.exp(-beta * x)

    try:
        p0 = [max(C), 0.3, t[np.argmin(C)]]
        popt, _ = curve_fit(logistic, t, C, p0=p0,
            bounds=([C.min(), 0.001, t[0]], [1.0, 5.0, t[-1]]), maxfev=5000)
        pred = logistic(t, *popt)
        rss = float(np.sum((C - pred) ** 2))
        results["coherence"] = {"C_eq": float(popt[0]), "rate": float(popt[1]),
                                "t0": float(popt[2]), "rss": rss}
    except Exception as e:
        results["coherence"] = {"error": str(e)}

    try:
        t_rel = t - t[0]
        popt, _ = curve_fit(exponential, t_rel, C, p0=[max(C[0], 0.01), 0.05],
            bounds=(0, [1.0, 5.0]), maxfev=5000)
        rss = float(np.sum((C - exponential(t_rel, *popt)) ** 2))
        results["decay"] = {"C0": float(popt[0]), "beta": float(popt[1]), "rss": rss}
    except Exception as e:
        results["decay"] = {"error": str(e)}

    try:
        slope, intercept, rv, pv, _ = linregress(t, C)
        pred = slope * t + intercept
        rss = float(np.sum((C - pred) ** 2))
        results["null_linear"] = {"slope": float(slope), "rss": rss}
    except Exception as e:
        results["null_linear"] = {"error": str(e)}

    return results


def print_summary(forest: dict, granular: dict):
    rec_label = "SUPPORTED" if granular["restoration"] else "NOT SUPPORTED"
    f_note = f" ({forest['n_recovered']}/{forest['n_plots']} plots recover)" if forest["n_recovered"] > 0 else ""

    print("\n" + "=" * 70)
    print("  RECOVERY ANALYSIS — SUMMARY")
    print("=" * 70)
    print(f"""
  Forest succession:
    Pre-perturbation C:       {forest['pre_C_avg']:.3f}
    Post-perturbation C:      {forest['post_C_avg_all']:.3f}
    Recovered plots:          {forest['n_recovered']}/{forest['n_plots']}
    Recovered C:              {forest['post_C_avg_recovered']:.3f}
    (restored to {forest['restoration_pct']:.0f}% of pre)

  Granular relaxation:
    Pre-removal C:            {granular['pre_C']:.3f}
    Dip:                      {granular['dip_magnitude']:.4f} ({granular['dip_pct']:.1f}%)
    Recovery:                 {granular['recovery_steps']} steps
    Restoration:              {'YES' if granular['restoration'] else 'NO'}

  Coherence restores after perturbation:
    {rec_label}{f_note}
""")


if __name__ == "__main__":
    t0 = time.time()
    forest = analyze_forest_succession()
    granular = analyze_granular()
    print_summary(forest, granular)
    elapsed = time.time() - t0
    print(f"  Total: {elapsed:.1f}s")

    with open("results/recovery_analysis.json", "w") as f:
        json.dump({"forest_succession": forest, "granular_relaxation": granular}, f, indent=2)
    print(f"  Saved to results/recovery_analysis.json")
