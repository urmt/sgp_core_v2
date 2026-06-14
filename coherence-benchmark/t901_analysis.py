"""T901: Mobility vs Coherence Decomposition.

For 60 granular runs (6 friction × 10 replicates):
  - Pre-C, recovery metrics (already computed in previous pass)
  - NOW: mobility proxies from raw particle trajectories
  - THEN: two-factor regression models A-D
  - THEN: phase diagram
  - THEN: falsification tests
"""

import numpy as np
import sys, time, itertools, json
sys.path.insert(0, ".")
from metrics import *
from adapters.granular import _soft_sphere_force

RNG = np.random.default_rng(42)
SEP = "=" * 78


# ─── Granular simulation (same as before, returns raw positions) ───

def _granular_run(
    n_grains=50, n_steps=1000, removal_step=500, removal_fraction=0.1,
    friction=0.3, seed=42,
):
    rng = np.random.default_rng(seed)
    radii = rng.uniform(0.8, 1.5, n_grains)
    masses = radii ** 2
    box_width = 40.0

    x = rng.uniform(2, box_width - 2, n_grains)
    y = rng.uniform(5, 30, n_grains)
    vx = rng.uniform(-0.5, 0.5, n_grains)
    vy = rng.uniform(-0.5, 0.5, n_grains)

    gy = -1.0; dt = 0.01; stiffness = 500.0; damping = 2.0
    n_remove = max(1, int(n_grains * removal_fraction))
    removed = np.zeros(n_grains, dtype=bool)

    all_x = np.zeros((n_grains, n_steps))
    all_y = np.zeros((n_grains, n_steps))
    # Store velocities for mobility analysis
    all_vx = np.zeros((n_grains, n_steps))
    all_vy = np.zeros((n_grains, n_steps))

    for step in range(n_steps):
        if step == removal_step:
            remove_idx = rng.choice(np.where(~removed)[0], size=n_remove, replace=False)
            removed[remove_idx] = True

        forces_x = np.zeros(n_grains)
        forces_y = np.full(n_grains, gy * masses)

        for i in range(n_grains):
            if removed[i]: continue
            for j in range(i + 1, n_grains):
                if removed[j]: continue
                dx = x[j] - x[i]; dy = y[j] - y[i]
                if abs(dx) > 3.0 or abs(dy) > 3.0: continue
                fx, fy, ov = _soft_sphere_force(dx, dy, radii[i], radii[j], stiffness, damping)
                forces_x[i] += fx; forces_y[i] += fy
                forces_x[j] -= fx; forces_y[j] -= fy

            vx[i] += forces_x[i] / masses[i] * dt
            vy[i] += forces_y[i] / masses[i] * dt
            vx[i] *= (1.0 - friction * dt)
            vy[i] *= (1.0 - friction * dt)
            x[i] += vx[i] * dt
            y[i] += vy[i] * dt

            if x[i] - radii[i] < 0: x[i] = radii[i]; vx[i] *= -0.5
            elif x[i] + radii[i] > box_width: x[i] = box_width - radii[i]; vx[i] *= -0.5
            if y[i] - radii[i] < 0: y[i] = radii[i]; vy[i] *= -0.5

        all_x[:, step] = np.where(removed, np.nan, x)
        all_y[:, step] = np.where(removed, np.nan, y)
        all_vx[:, step] = np.where(removed, np.nan, vx)
        all_vy[:, step] = np.where(removed, np.nan, vy)

    return all_y, all_x, all_vx, all_vy, radii, removed


# ─── Binning (identical to GranularAdapter) ───

def _bin_data(positions_y, positions_x, n_bins=10):
    nan_mask = np.isnan(positions_y)
    col_means = np.nanmean(positions_y, axis=1, keepdims=True)
    positions_y = np.where(nan_mask, col_means, positions_y)
    with np.errstate(invalid="ignore"):
        final_x = np.nanmean(positions_x[:, -100:], axis=1)
    final_x = np.where(np.isnan(final_x), np.nanmean(positions_x[:, :500], axis=1), final_x)
    order = np.argsort(final_x)
    bins = np.array_split(order, n_bins)
    return np.array([np.mean(positions_y[b], axis=0) for b in bins])


# ─── Sliding C ───

def _sliding_C(X, window=75, step=25):
    T = X.shape[1]
    times, vals = [], []
    for t in range(0, T - window + 1, step):
        seg = X[:, t:t + window]
        times.append(t + window // 2)
        try: vals.append(compute_C(seg, "gaussian"))
        except Exception: vals.append(np.nan)
    return np.array(times), np.array(vals)


# ─── Recovery measurement ───

def measure_recovery(times, c_vals, pert_start=500):
    pre = c_vals[(times >= 100) & (times < pert_start)]
    pert = c_vals[(times >= pert_start) & (times <= pert_start + 100)]
    post = c_vals[(times >= pert_start + 100) & (times <= pert_start + 400)]

    if len(pre) < 2 or len(pert) < 2:
        return {"pre_C": np.nan, "dip": np.nan, "restoration": np.nan, "tau_rec": np.nan}

    pre_mean = float(np.nanmean(pre))
    pert_min = float(np.nanmin(pert))
    dip = pre_mean - pert_min

    post_vals = post[~np.isnan(post)]
    if len(post_vals) < 3:
        return {"pre_C": pre_mean, "dip": dip, "restoration": np.nan, "tau_rec": np.nan}

    post_final = float(np.nanmean(post_vals[-10:]))
    restoration = post_final / max(pre_mean, 1e-10)

    tau = np.nan
    for k, v in enumerate(post):
        if not np.isnan(v) and v >= pre_mean:
            tau = float(times[len(pre) + len(pert) + k] - pert_start)
            break

    return {
        "pre_C": pre_mean, "dip": dip, "restoration": restoration,
        "tau_rec": tau if not np.isnan(tau) else float(len(post) * (times[1] - times[0])),
    }


# ─── T901.2: Mobility proxies ───

def compute_mobility_proxies(all_x, all_y, all_vx, all_vy, radii, removed, T_pre=500):
    """Four mobility proxies from raw particle data.

    Only use pre-perturbation data (first T_pre steps).
    Exclude removed particles.
    """
    active = ~removed
    x = np.nan_to_num(all_x[active, :T_pre], nan=0.0)
    y = np.nan_to_num(all_y[active, :T_pre], nan=0.0)
    vx = np.nan_to_num(all_vx[active, :T_pre], nan=0.0)
    vy = np.nan_to_num(all_vy[active, :T_pre], nan=0.0)
    n_active = active.sum()
    if n_active < 3:
        return {"msd": np.nan, "rms_velocity": np.nan, "neighbor_turnover": np.nan, "packing_var": np.nan}

    # 1. RMS velocity
    speeds = np.sqrt(vx**2 + vy**2)
    rms_vel = float(np.mean(speeds))

    # 2. Mean squared displacement (t=1 to t=200)
    dx = np.diff(x, axis=1)
    dy = np.diff(y, axis=1)
    displacements = np.cumsum(dx**2 + dy**2, axis=1)
    msd = float(np.mean(displacements[:, -1])) if displacements.shape[1] > 0 else np.nan

    # 3. Neighbor turnover rate
    # Define neighbors as particles within distance 4.0 (sum of max radii ≈ 3 + margin)
    contact_dist = 4.0
    n_changes = 0
    n_steps_check = min(T_pre - 1, 200)
    step_skip = max(1, n_steps_check // 50)

    for t in range(0, n_steps_check - step_skip, step_skip):
        p1 = np.column_stack([x[:, t], y[:, t]])
        p2 = np.column_stack([x[:, t + step_skip], y[:, t + step_skip]])

        # Contacts at t
        contacts_t = set()
        for i in range(n_active):
            for j in range(i + 1, n_active):
                dij = np.linalg.norm(p1[i] - p1[j])
                if dij < contact_dist:
                    contacts_t.add((i, j))

        # Contacts at t+dt
        contacts_t2 = set()
        for i in range(n_active):
            for j in range(i + 1, n_active):
                dij = np.linalg.norm(p2[i] - p2[j])
                if dij < contact_dist:
                    contacts_t2.add((i, j))

        n_changes += len(contacts_t.symmetric_difference(contacts_t2))

    n_possible = n_active * (n_active - 1) / 2
    turnover = float(n_changes / max(50 * n_possible, 1))

    # 4. Local packing variance (std of nearest-neighbor distances)
    nn_dists = []
    for t in range(0, T_pre, 10):
        pos = np.column_stack([x[:, t], y[:, t]])
        for i in range(n_active):
            dists = [np.linalg.norm(pos[i] - pos[j]) for j in range(n_active) if j != i]
            if dists:
                nn_dists.append(min(dists))
    packing_var = float(np.std(nn_dists)) if nn_dists else np.nan

    return {
        "rms_velocity": rms_vel,
        "msd": msd,
        "neighbor_turnover": turnover,
        "packing_var": packing_var,
    }


# ─── Generate ensemble ───

def generate_ensemble():
    friction_levels = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8]
    n_reps = 10
    n_bins = 10
    rows = []

    t0 = time.time()
    for fi, friction in enumerate(friction_levels):
        print(f"\n  Friction = {friction:.2f}  [{fi+1}/{len(friction_levels)}]", flush=True)
        for rep in range(n_reps):
            seed = rep + 100 * fi
            y, x, vx, vy, radii, removed = _granular_run(
                n_grains=50, n_steps=1000, removal_step=500,
                removal_fraction=0.1, friction=friction, seed=seed,
            )

            # Binned data for C
            binned = _bin_data(y, x, n_bins=n_bins)
            times, cvals = _sliding_C(binned, window=75, step=25)
            rec = measure_recovery(times, cvals, pert_start=500)

            # Pre-perturbation competitor metrics
            pre = binned[:, :500]
            pre_ip = compute_predictive_information(pre, tau=1)
            pre_cs = compute_statistical_complexity(pre, tau=1)
            pre_mse = compute_mse(pre, scales=[1]).get(1, np.nan)

            # Mobility proxies from raw data
            mob = compute_mobility_proxies(x, y, vx, vy, radii, removed, T_pre=500)

            row = {
                "friction": friction, "rep": rep,
                "pre_C": rec["pre_C"], "dip": rec["dip"],
                "restoration": rec["restoration"], "tau_rec": rec["tau_rec"],
                "pre_I_pred": pre_ip, "pre_C_sigma": pre_cs, "pre_MSE_s1": pre_mse,
            }
            row.update(mob)
            rows.append(row)

            if (rep + 1) % 5 == 0:
                print(f"    rep {rep+1}/{n_reps} (C_pre={rec['pre_C']:.4f}, msd={mob['msd']:.2f})", flush=True)

    print(f"\n  Generated {len(rows)} runs in {time.time() - t0:.0f}s")
    return rows


# ─── T901.1: Regression models ───

def run_regressions(rows):
    print(f"\n{SEP}")
    print("  T901.1: TWO-FACTOR REGRESSION")
    print(f"{SEP}")

    try:
        import statsmodels.api as sm
        has_sm = True
    except ImportError:
        has_sm = False
        print("  statsmodels not available — using sklearn LinearRegression")

    targets = [("dip", "ΔC (dip depth)"), ("tau_rec", "τ_rec"), ("restoration", "C_final/C_pre")]
    models = [
        ("A: C only",     ["pre_C"]),
        ("B: friction",   ["friction"]),
        ("C: additive",   ["pre_C", "friction"]),
        ("D: interaction",["pre_C", "friction", "pre_C:friction"]),
    ]

    # Standardize predictors
    arr = np.array([[r["pre_C"], r["friction"], r["dip"], r["tau_rec"], r["restoration"]]
                    for r in rows])
    means = np.nanmean(arr, axis=0)
    stds = np.nanstd(arr, axis=0)
    stds[stds == 0] = 1.0
    arr_z = (arr - means) / stds

    # Check for nans
    valid = ~np.any(np.isnan(arr_z), axis=1)
    if valid.sum() < len(rows):
        print(f"\n  Dropping {len(rows) - valid.sum()} rows with NaN values")
        arr_z = arr_z[valid]
        rows_sub = [rows[i] for i in range(len(rows)) if valid[i]]

    for target, tname in targets:
        t_idx = 2 + ["dip", "tau_rec", "restoration"].index(target)
        y = arr_z[:, t_idx]

        print(f"\n  Target: {tname}")
        print(f"  {'Model':>20s}  {'R²':>8s}  {'AIC':>10s}  {'Coefficients'}")
        print(f"  {'-' * 65}")

        best_r2 = -1
        best_name = None

        for mname, predictors in models:
            n_pred = len(predictors)
            X_list = []
            col_map = {"pre_C": 0, "friction": 1}
            for p in predictors:
                if p == "pre_C:friction":
                    X_list.append(arr_z[:, 0:1] * arr_z[:, 1:2])
                else:
                    X_list.append(arr_z[:, col_map[p]:col_map[p]+1])

            if has_sm:
                X = sm.add_constant(np.column_stack(X_list) if len(X_list) > 1 else X_list[0])
            else:
                X = np.column_stack(X_list) if len(X_list) > 1 else X_list[0]

            good = ~(np.isnan(y) | np.any(np.isnan(X), axis=1))
            if good.sum() < n_pred + 2:
                print(f"  {mname:>20s}  {'N/A':>8s}  {'N/A':>10s}  {'insufficient data'}")
                continue

            if has_sm:
                model = sm.OLS(y[good], X[good]).fit()
                r2 = model.rsquared; aic = model.aic
                coeffs = "  ".join(f"{model.params[i]:+.3f}" for i in range(len(model.params)))
            else:
                from sklearn.linear_model import LinearRegression
                from sklearn.metrics import r2_score
                lr = LinearRegression().fit(X[good], y[good])
                y_pred = lr.predict(X[good])
                r2 = r2_score(y[good], y_pred)
                aic = len(y[good]) * max(np.log(r2), -10) + 2 * (n_pred + 1)
                coeffs = "  ".join(f"{lr.coef_[i]:+.3f}" for i in range(lr.coef_.shape[0]))

            if r2 > best_r2:
                best_r2 = r2; best_name = mname

            print(f"  {mname:>20s}  {r2:>8.4f}  {aic:>10.1f}  {coeffs}")

        print(f"  {'→ Best':>20s}  {best_name}")

    return rows


# ─── T901.3: Phase diagram ───

def plot_phase_diagram(rows):
    print(f"\n{SEP}")
    print("  T901.3: PHASE DIAGRAM — C_pre vs Mobility")
    print(f"{SEP}")

    # Use MSD as mobility metric
    msd_vals = np.array([r["msd"] for r in rows])
    c_vals = np.array([r["pre_C"] for r in rows])
    dip_vals = np.array([r["dip"] for r in rows])
    rest_vals = np.array([r["restoration"] for r in rows])

    valid = ~(np.isnan(msd_vals) | np.isnan(c_vals) | np.isnan(dip_vals))
    if valid.sum() < 10:
        print("  Insufficient valid data points")
        return

    c = c_vals[valid]
    m = msd_vals[valid]
    d = dip_vals[valid]
    r = rest_vals[valid]

    # Print ASCII grid for C vs MSD, colored by dip
    print(f"\n  ASCII PHASE DIAGRAM: C_pre (x) vs MSD (y) — colored by ΔC")
    print(f"  (- = negative dip (C↑), + = positive dip (C↓), 0 = near-zero)")
    print()

    x_bins = 8
    y_bins = 6
    c_min, c_max = np.nanmin(c), np.nanmax(c)
    m_min, m_max = np.nanmin(m), np.nanmax(m)

    print(f"  MSD↑  {m_max:>8.1f}  ", end="")
    for yi in range(y_bins - 1, -1, -1):
        y_lo = m_min + (m_max - m_min) * yi / y_bins
        y_hi = m_min + (m_max - m_min) * (yi + 1) / y_bins
        if yi < y_bins - 1:
            print(f"\n         {y_hi:>8.1f}  ", end="")
        for xi in range(x_bins):
            x_lo = c_min + (c_max - c_min) * xi / x_bins
            x_hi = c_min + (c_max - c_min) * (xi + 1) / x_bins
            mask = (c >= x_lo) & (c < x_hi) & (m >= y_lo) & (m < y_hi)
            if mask.sum() == 0:
                print("  .  ", end="")
            else:
                mean_d = np.mean(d[mask])
                if abs(mean_d) < 0.01:
                    print("  0  ", end="")
                elif mean_d < 0:
                    print("  -  ", end="")
                else:
                    print("  +  ", end="")
    print(f"\n         {m_min:>8.1f}")
    print(f"         {c_min:>8.3f}  ", end="")
    for xi in range(x_bins):
        x_hi = c_min + (c_max - c_min) * (xi + 1) / x_bins
        print(f"{x_hi:>5.3f}", end="")
    print("  → C_pre")

    # Regions
    print(f"\n  REGION LABELS:")
    print(f"    Top-right (high C, high MSD):    low friction = 0.05")
    print(f"    Bottom-right (high C, low MSD):  high friction = 0.80")
    print(f"    Top-left (low C, high MSD):      (no data — low friction → high C)")
    print(f"    Bottom-left (low C, low MSD):    high friction")
    print()

    # Simple quadrant analysis
    c_median = np.median(c)
    m_median = np.median(m)
    quadrants = {
        "high C, high MSD": ((c >= c_median) & (m >= m_median), "low friction"),
        "high C, low MSD": ((c >= c_median) & (m < m_median), "high friction"),
        "low C, high MSD": ((c < c_median) & (m >= m_median), "mixed"),
        "low C, low MSD": ((c < c_median) & (m < m_median), "high friction"),
    }

    print(f"  QUADRANT SUMMARY (median-split):")
    print(f"  {'Quadrant':>20s}  {'N':>4s}  {'Mean ΔC':>10s}  {'Mean Rest.':>12s}  {'Regime'}")
    print(f"  {'-' * 55}")
    for qname, (mask, regime) in quadrants.items():
        n = mask.sum()
        if n < 2: continue
        print(f"  {qname:>20s}  {n:>4d}  {np.mean(d[mask]):>+10.4f}  {np.mean(r[mask]):>12.4f}  {regime}")

    return quadrants


# ─── T901.4: Falsification ───

def run_falsification(rows):
    print(f"\n{SEP}")
    print("  T901.4: FALSIFICATION ATTEMPTS")
    print(f"{SEP}")

    print(f"""
  Goal: Find evidence that both C and mobility are needed to predict recovery.

  Strategy 1: Same C, different mobility → different recovery?
  Strategy 2: Same mobility, different C → different recovery?
""")

    # 1. Same C, different mobility
    print(f"  STRATEGY 1: Match pairs with similar C_pre (±0.01) but different MSD")
    c_vals = np.array([r["pre_C"] for r in rows])
    msd_vals = np.array([r["msd"] for r in rows])
    dip_vals = np.array([r["dip"] for r in rows])
    rest_vals = np.array([r["restoration"] for r in rows])

    n_matches = 0
    max_matches = 5
    for i in range(len(rows)):
        if n_matches >= max_matches: break
        for j in range(i + 1, len(rows)):
            if n_matches >= max_matches: break
            if np.isnan([c_vals[i], c_vals[j], msd_vals[i], msd_vals[j]]).any():
                continue
            if abs(c_vals[i] - c_vals[j]) > 0.01: continue
            msd_ratio = msd_vals[i] / max(msd_vals[j], 1e-10)
            if msd_ratio < 1.5 or msd_ratio > 1.0/1.5: continue

            n_matches += 1
            i_label = f"rep={rows[i]['rep']}, fric={rows[i]['friction']:.2f}"
            j_label = f"rep={rows[j]['rep']}, fric={rows[j]['friction']:.2f}"
            print(f"""
  Match #{n_matches}:
    Same C:      C_pre = {c_vals[i]:.4f} vs {c_vals[j]:.4f} (Δ = {abs(c_vals[i]-c_vals[j]):.4f})
    Diff mob:    MSD   = {msd_vals[i]:.2f} vs {msd_vals[j]:.2f} (ratio = {msd_ratio:.1f}x)
    Recovery:    ΔC    = {dip_vals[i]:+.4f} vs {dip_vals[j]:+.4f}
                 Rest. = {rest_vals[i]:.4f} vs {rest_vals[j]:.4f}
    IDs:         {i_label} vs {j_label}""")

    # 2. Same mobility, different C
    print(f"""
  STRATEGY 2: Match pairs with similar MSD (±10%) but different C_pre""")
    n_matches2 = 0
    for i in range(len(rows)):
        if n_matches2 >= max_matches: break
        for j in range(i + 1, len(rows)):
            if n_matches2 >= max_matches: break
            if np.isnan([c_vals[i], c_vals[j], msd_vals[i], msd_vals[j]]).any():
                continue
            msd_ratio = msd_vals[i] / max(msd_vals[j], 1e-10)
            if msd_ratio > 1.1 or msd_ratio < 1.0/1.1: continue
            if abs(c_vals[i] - c_vals[j]) < 0.02: continue

            n_matches2 += 1
            i_label = f"rep={rows[i]['rep']}, fric={rows[i]['friction']:.2f}"
            j_label = f"rep={rows[j]['rep']}, fric={rows[j]['friction']:.2f}"
            print(f"""
  Match #{n_matches2}:
    Same mob:    MSD   = {msd_vals[i]:.2f} vs {msd_vals[j]:.2f} (ratio = {msd_ratio:.2f})
    Diff C:      C_pre = {c_vals[i]:.4f} vs {c_vals[j]:.4f} (Δ = {abs(c_vals[i]-c_vals[j]):.4f})
    Recovery:    ΔC    = {dip_vals[i]:+.4f} vs {dip_vals[j]:+.4f}
                 Rest. = {rest_vals[i]:.4f} vs {rest_vals[j]:.4f}
    IDs:         {i_label} vs {j_label}""")

    # Summary
    print(f"\n  {'=' * 78}")
    print("  FALSIFICATION SUMMARY")
    print(f"  {'=' * 78}")
    print(f"""
  Strategy 1 (same C, diff MSD): {'FOUND' if n_matches > 0 else 'NONE'} — {n_matches} pairs
  Strategy 2 (same MSD, diff C): {'FOUND' if n_matches2 > 0 else 'NONE'} — {n_matches2} pairs

  If both strategies find matches where recovery differs:
    → Both C and mobility are needed (two-factor model supported)

  If only one strategy finds matches:
    → That variable may be sufficient (one-factor model supported)

  If neither finds matches:
    → Insufficient resolution or variables are collinear
""")


# ─── Main ───

def main():
    print(f"{SEP}")
    print("  T901: MOBILITY vs COHERENCE DECOMPOSITION")
    print(f"{SEP}")

    rows = generate_ensemble()

    run_regressions(rows)

    quadrants = plot_phase_diagram(rows)

    run_falsification(rows)

    # Save
    with open("results/t901_ensemble.json", "w") as f:
        json.dump([{k: (v if not (isinstance(v, float) and np.isnan(v)) else None)
                     for k, v in r.items()} for r in rows], f, indent=2)
    print(f"\n  Saved to results/t901_ensemble.json")

    # Print final data table
    print(f"\n{SEP}")
    print("  FULL DATA TABLE")
    print(f"{SEP}")
    print(f"\n  {'Fric':>5s}  {'C_pre':>7s}  {'MSD':>7s}  {'Vel':>7s}  {'Turn':>7s}  {'ΔC':>8s}  {'Rest.':>8s}  {'τ':>5s}")
    print(f"  {'-' * 57}")
    for r in sorted(rows, key=lambda x: (x["friction"], x["rep"])):
        print(f"  {r['friction']:>5.2f}  {r['pre_C']:>7.4f}  {r['msd'] if not np.isnan(r['msd']) else 0:>7.2f}  {r['rms_velocity'] if not np.isnan(r['rms_velocity']) else 0:>7.3f}  {r['neighbor_turnover'] if not np.isnan(r['neighbor_turnover']) else 0:>7.4f}  {r['dip']:>+8.4f}  {r['restoration']:>8.4f}  {r['tau_rec']:>5.0f}")

    return rows


if __name__ == "__main__":
    rows = main()
