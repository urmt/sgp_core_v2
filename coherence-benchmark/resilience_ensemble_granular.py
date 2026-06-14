"""Resilience prediction ensemble using granular DEM at varying friction.

Pre-C varies with friction (higher friction → more structured packing).
Perturbation: identical 10% removal at t=500.
Recovery is emergent from the physics.

Question: does pre-C predict dip magnitude, recovery timescale, or restoration fraction?
"""

import numpy as np
import sys, time
sys.path.insert(0, ".")
from metrics import *
from adapters.granular import _soft_sphere_force


RNG = np.random.default_rng(42)


def _granular_run(
    n_grains=50, n_steps=1000, removal_step=500, removal_fraction=0.1,
    friction=0.3, seed=42,
):
    """Granular DEM with friction as control parameter."""
    rng = np.random.default_rng(seed)
    radii = rng.uniform(0.8, 1.5, n_grains)
    masses = radii ** 2
    box_width = 40.0

    x = rng.uniform(2, box_width - 2, n_grains)
    y = rng.uniform(5, 30, n_grains)
    vx = rng.uniform(-0.5, 0.5, n_grains)
    vy = rng.uniform(-0.5, 0.5, n_grains)

    gy = -1.0
    dt = 0.01
    stiffness = 500.0
    damping = 2.0

    n_remove = max(1, int(n_grains * removal_fraction))
    removed = np.zeros(n_grains, dtype=bool)
    all_y = np.zeros((n_grains, n_steps))
    all_x = np.zeros((n_grains, n_steps))

    for step in range(n_steps):
        if step == removal_step:
            remove_idx = rng.choice(
                np.where(~removed)[0], size=n_remove, replace=False
            )
            removed[remove_idx] = True

        forces_x = np.zeros(n_grains)
        forces_y = np.full(n_grains, gy * masses)

        for i in range(n_grains):
            if removed[i]:
                continue
            for j in range(i + 1, n_grains):
                if removed[j]:
                    continue
                dx = x[j] - x[i]
                dy = y[j] - y[i]
                if abs(dx) > 3.0 or abs(dy) > 3.0:
                    continue
                fx, fy, ov = _soft_sphere_force(
                    dx, dy, radii[i], radii[j], stiffness, damping
                )
                forces_x[i] += fx
                forces_y[i] += fy
                forces_x[j] -= fx
                forces_y[j] -= fy

            vx[i] += forces_x[i] / masses[i] * dt
            vy[i] += forces_y[i] / masses[i] * dt
            vx[i] *= (1.0 - friction * dt)
            vy[i] *= (1.0 - friction * dt)
            x[i] += vx[i] * dt
            y[i] += vy[i] * dt

            if x[i] - radii[i] < 0:
                x[i] = radii[i]; vx[i] *= -0.5
            elif x[i] + radii[i] > box_width:
                x[i] = box_width - radii[i]; vx[i] *= -0.5
            if y[i] - radii[i] < 0:
                y[i] = radii[i]; vy[i] *= -0.5

        all_y[:, step] = np.where(removed, np.nan, y)
        all_x[:, step] = np.where(removed, np.nan, x)

    return all_y, all_x


def _bin_data(positions_y, positions_x, n_bins=10):
    """Spatial binning (same as GranularAdapter)."""
    nan_mask = np.isnan(positions_y)
    col_means = np.nanmean(positions_y, axis=1, keepdims=True)
    positions_y = np.where(nan_mask, col_means, positions_y)

    with np.errstate(invalid="ignore"):
        final_x = np.nanmean(positions_x[:, -100:], axis=1)
    final_x = np.where(np.isnan(final_x),
                       np.nanmean(positions_x[:, :500], axis=1), final_x)
    order = np.argsort(final_x)
    bins = np.array_split(order, n_bins)
    binned = np.array([np.mean(positions_y[b], axis=0) for b in bins])
    return binned


def _sliding_C(X, window=75, step=25):
    """Compute C at each sliding window, return times and C values."""
    T = X.shape[1]
    times, vals = [], []
    for t in range(0, T - window + 1, step):
        seg = X[:, t:t + window]
        times.append(t + window // 2)
        try:
            vals.append(compute_C(seg, "gaussian"))
        except Exception:
            vals.append(np.nan)
    return np.array(times), np.array(vals)


def measure_recovery(times, c_vals, pert_start=500, pert_end=500):
    """Extract dip, tau_rec, restoration from C(t) trajectory."""
    pre_mask = (times >= 100) & (times < pert_start)
    pert_mask = (times >= pert_start) & (times <= pert_end + 100)
    post_mask = (times >= pert_end + 100) & (times <= pert_end + 400)

    pre = c_vals[pre_mask]
    pert_win = c_vals[pert_mask]
    post = c_vals[post_mask]

    if len(pre) < 2 or len(pert_win) < 2:
        return {"pre_C": np.nan, "dip": np.nan, "restoration": np.nan, "tau_rec": np.nan}

    pre_mean = float(np.nanmean(pre))
    pert_min = float(np.nanmin(pert_win))
    dip = pre_mean - pert_min

    post_vals = post[~np.isnan(post)]
    if len(post_vals) < 3:
        return {"pre_C": pre_mean, "dip": dip, "restoration": np.nan, "tau_rec": np.nan}

    post_final = float(np.nanmean(post_vals[-10:]))
    restoration = post_final / max(pre_mean, 1e-10)

    tau = np.nan
    for k, v in enumerate(post):
        if not np.isnan(v) and v >= pre_mean:
            tau = float(times[post_mask][k] - pert_end)
            break

    return {
        "pre_C": pre_mean,
        "dip": dip,
        "restoration": restoration,
        "tau_rec": tau if not np.isnan(tau) else float(len(post) * (times[1] - times[0])),
    }


def main():
    print("=" * 78)
    print("  RESILIENCE PREDICTION: GRANULAR ENSEMBLE")
    print("  Varying friction to modulate pre-C")
    print("=" * 78)

    friction_levels = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8]
    n_reps = 10
    n_bins = 10
    results = []

    t0 = time.time()
    for fi, friction in enumerate(friction_levels):
        print(f"\n  Friction = {friction:.2f}  [{fi+1}/{len(friction_levels)}]")
        for rep in range(n_reps):
            seed = rep + 100 * fi
            y, x = _granular_run(
                n_grains=50, n_steps=1000, removal_step=500,
                removal_fraction=0.1, friction=friction, seed=seed,
            )
            binned = _bin_data(y, x, n_bins=n_bins)
            times, cvals = _sliding_C(binned, window=75, step=25)
            rec = measure_recovery(times, cvals, pert_start=500, pert_end=500)

            # Also compute competitor metrics from pre-perturbation data
            pre = binned[:, :500]
            pre_ip = compute_predictive_information(pre, tau=1)
            pre_cs = compute_statistical_complexity(pre, tau=1)
            pre_mse = compute_mse(pre, scales=[1]).get(1, np.nan)

            results.append({
                "friction": friction,
                "rep": rep,
                "pre_C": rec["pre_C"],
                "dip": rec["dip"],
                "restoration": rec["restoration"],
                "tau_rec": rec["tau_rec"],
                "pre_I_pred": pre_ip,
                "pre_C_sigma": pre_cs,
                "pre_MSE_s1": pre_mse,
            })

            if (rep + 1) % 5 == 0:
                print(f"    rep {rep+1}/{n_reps} (C_pre = {rec['pre_C']:.4f})", flush=True)

    print(f"\n  Total time: {time.time() - t0:.0f}s")
    print(f"  Total runs: {len(results)}")

    # Print per-friction summary
    print(f"\n{'=' * 78}")
    print("  PER-FRICTION MEANS")
    print(f"{'=' * 78}")
    print(f"\n  {'Friction':>8s}  {'Pre-C':>8s}  {'Dip':>8s}  {'Rest.':>8s}  {'Tau':>6s}  {'I_pred':>8s}  {'C_sigma':>8s}  {'MSE':>8s}")
    print(f"  {'-' * 68}")
    for f in friction_levels:
        r = [r for r in results if abs(r["friction"] - f) < 0.01]
        p = np.nanmean([x["pre_C"] for x in r])
        d = np.nanmean([x["dip"] for x in r])
        rt = np.nanmean([x["restoration"] for x in r])
        ta = np.nanmean([x["tau_rec"] for x in r])
        ip = np.nanmean([x["pre_I_pred"] for x in r])
        cs = np.nanmean([x["pre_C_sigma"] for x in r])
        ms = np.nanmean([x["pre_MSE_s1"] for x in r])
        print(f"  {f:>8.2f}  {p:>8.4f}  {d:>8.4f}  {rt:>8.4f}  {ta:>6.0f}  {ip:>8.4f}  {cs:>8.4f}  {ms:>8.4f}")

    # Correlation analysis
    print(f"\n{'=' * 78}")
    print("  CORRELATION: PRE → RECOVERY (all runs pooled)")
    print("=" * 78)

    from scipy.stats import pearsonr, spearmanr

    for metric, label in [
        ("pre_C", "C"), ("pre_I_pred", "I_pred"),
        ("pre_C_sigma", "C_sigma"), ("pre_MSE_s1", "MSE_s1"),
    ]:
        vals = np.array([r[metric] for r in results])
        print(f"\n  {label} (pre-perturbation) → recovery:")
        for target, tname in [("dip", "ΔC"), ("restoration", "C_final/C_pre"), ("tau_rec", "τ_rec")]:
            tgt = np.array([r[target] for r in results])
            valid = ~(np.isnan(vals) | np.isnan(tgt))
            if valid.sum() < 5:
                continue
            r_p, p_p = pearsonr(vals[valid], tgt[valid])
            r_s, p_s = spearmanr(vals[valid], tgt[valid])
            print(f"    → {tname:>15s}:  Pearson r={r_p:+.3f} (p={p_p:.4f}), Spearman ρ={r_s:+.3f} (p={p_s:.4f})")

    # Best predictor table
    print(f"\n{'=' * 78}")
    print("  BEST PREDICTOR PER TARGET")
    print("=" * 78)

    targets = [("dip", "ΔC"), ("restoration", "C_final/C_pre"), ("tau_rec", "τ_rec")]
    all_metrics = [
        ("pre_C", "C"), ("pre_I_pred", "I_pred"),
        ("pre_C_sigma", "C_sigma"), ("pre_MSE_s1", "MSE_s1"),
    ]

    for target, tname in targets:
        best_name, best_r = None, -2.0
        for metric, mname in all_metrics:
            vals = np.array([r[metric] for r in results])
            tgt = np.array([r[target] for r in results])
            valid = ~(np.isnan(vals) | np.isnan(tgt))
            if valid.sum() < 5:
                continue
            r_val, p = pearsonr(vals[valid], tgt[valid])
            if abs(r_val) > abs(best_r):
                best_r = r_val
                best_name = mname
        if best_name:
            print(f"  {tname:>20s} → {best_name:>8s}  (|r| = {abs(best_r):.3f})")

    # Within-friction correlation
    print(f"\n{'=' * 78}")
    print("  WITHIN-FRICTION ANALYSIS")
    print("  Does pre-C predict recovery when friction is held constant?")
    print("=" * 78)

    for f in friction_levels:
        r = [r for r in results if abs(r["friction"] - f) < 0.01]
        pre = np.array([x["pre_C"] for x in r])
        dips = np.array([x["dip"] for x in r])
        taus = np.array([x["tau_rec"] for x in r])
        rest = np.array([x["restoration"] for x in r])
        print(f"\n  Friction = {f:.2f}  (n={len(r)}):")
        for target, vals, name in [
            ("dip", dips, "ΔC"), ("tau_rec", taus, "τ"),
            ("restoration", rest, "C_f/C_pre"),
        ]:
            valid = ~(np.isnan(pre) | np.isnan(vals))
            if valid.sum() < 5:
                continue
            rp, _ = pearsonr(pre[valid], vals[valid])
            rs, _ = spearmanr(pre[valid], vals[valid])
            print(f"    {name:>12s}:  Pearson r={rp:+.3f}, Spearman ρ={rs:+.3f}")

    # Direction of dip by friction
    print(f"\n{'=' * 78}")
    print("  DIP DIRECTION by friction")
    print("=" * 78)
    print(f"\n  {'Friction':>8s}  {'Mean Dip':>10s}  {'# Neg':>6s}  {'# Pos':>6s}  {'Interpretation'}")
    print(f"  {'-' * 55}")
    for f in friction_levels:
        r = [r for r in results if abs(r["friction"] - f) < 0.01]
        dips = [x["dip"] for x in r]
        n_neg = sum(1 for d in dips if d < 0)
        n_pos = sum(1 for d in dips if d > 0)
        md = np.mean(dips)
        direction = "C ↑ (reorganization)" if md < -0.01 else ("C ↓ (disruption)" if md > 0.01 else "≈unchanged")
        print(f"  {f:>8.2f}  {md:>+10.4f}  {n_neg:>6d}  {n_pos:>6d}  {direction}")

    return results


if __name__ == "__main__":
    results = main()
