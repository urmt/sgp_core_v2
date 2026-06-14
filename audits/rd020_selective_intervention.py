"""RD-020: Selective Removal Intervention.

Test whether C tracks structural importance rather than density.
6 conditions × 10 reps = 60 runs.

Strategies:
  S0: random (control)
  S1: largest grains
  S2: smallest grains
  S3: highest-degree grains (contact network hubs)
  S4: lowest-degree grains (peripheral)
  S5: highest-force grains (force-chain backbone)
"""

import numpy as np
import sys, time, json
sys.path.insert(0, "coherence-benchmark")
from metrics import *
from adapters.granular import _soft_sphere_force

SEP = "=" * 78


def _granular_run_selective(
    n_grains=50, n_steps=1000, removal_step=500, removal_fraction=0.1,
    friction=0.3, seed=42, box_width=40.0, removal_strategy="random",
):
    """Modified granular run with selective removal strategies.

    At step `removal_step`, computes the current structural state
    (positions, velocities, contact network, force network) and selects
    grains for removal based on the chosen strategy.
    """
    rng = np.random.default_rng(seed)
    radii = rng.uniform(0.8, 1.5, n_grains)
    masses = radii ** 2

    x = rng.uniform(2, box_width - 2, n_grains)
    y = rng.uniform(5, 30, n_grains)
    vx = rng.uniform(-0.5, 0.5, n_grains)
    vy = rng.uniform(-0.5, 0.5, n_grains)

    gy = -1.0; dt = 0.01; stiffness = 500.0; damping = 2.0
    n_remove = max(1, int(n_grains * removal_fraction))
    removed = np.zeros(n_grains, dtype=bool)

    all_x = np.zeros((n_grains, n_steps))
    all_y = np.zeros((n_grains, n_steps))
    all_vx = np.zeros((n_grains, n_steps))
    all_vy = np.zeros((n_grains, n_steps))

    # Pre-removal structural metrics (for analysis)
    pre_metrics = {
        "removed_idx": None,
        "removed_radii_mean": None,
        "removed_degree_mean": None,
        "removed_force_mean": None,
        "removed_clustering_mean": None,
        "removed_speed_mean": None,
        "kept_degree_mean": None,
        "kept_force_mean": None,
    }

    for step in range(n_steps):
        if step == removal_step:
            active = np.where(~removed)[0]

            if removal_strategy == "random":
                remove_idx = rng.choice(active, size=n_remove, replace=False)

            elif removal_strategy == "largest":
                # Remove largest grains
                order = np.argsort(-radii[active])  # descending
                remove_idx = active[order[:n_remove]]

            elif removal_strategy == "smallest":
                # Remove smallest grains
                order = np.argsort(radii[active])  # ascending
                remove_idx = active[order[:n_remove]]

            elif removal_strategy == "highest_degree" or removal_strategy == "lowest_degree":
                # Build contact network at this step
                deg = np.zeros(n_grains)
                adj = [[] for _ in range(n_grains)]
                for i in active:
                    for j in active:
                        if i >= j: continue
                        d = np.sqrt((x[j] - x[i])**2 + (y[j] - y[i])**2)
                        thresh = radii[i] + radii[j] + 0.3
                        if d < thresh:
                            adj[i].append(j)
                            adj[j].append(i)
                            deg[i] += 1
                            deg[j] += 1
                if removal_strategy == "highest_degree":
                    order = np.argsort(-deg[active])  # descending
                else:
                    order = np.argsort(deg[active])   # ascending
                remove_idx = active[order[:n_remove]]
                pre_metrics["removed_degree_mean"] = float(np.mean(deg[remove_idx]))
                pre_metrics["kept_degree_mean"] = float(np.mean(deg[[i for i in active if i not in remove_idx]]))

            elif removal_strategy == "highest_force":
                # Compute per-grain incident force at this step
                force_mag = np.zeros(n_grains)
                for i in active:
                    for j in active:
                        if i >= j: continue
                        dx = x[j] - x[i]; dy = y[j] - y[i]
                        if abs(dx) > 3.0 or abs(dy) > 3.0: continue
                        fx, fy, ov = _soft_sphere_force(dx, dy, radii[i], radii[j], stiffness, damping)
                        f_mag = np.sqrt(fx**2 + fy**2)
                        force_mag[i] += f_mag
                        force_mag[j] += f_mag
                order = np.argsort(-force_mag[active])
                remove_idx = active[order[:n_remove]]
                pre_metrics["removed_force_mean"] = float(np.mean(force_mag[remove_idx]))
                active_kept = [i for i in active if i not in remove_idx]
                if active_kept:
                    pre_metrics["kept_force_mean"] = float(np.mean(force_mag[active_kept]))
            else:
                # Fallback to random
                remove_idx = rng.choice(active, size=n_remove, replace=False)

            removed[remove_idx] = True
            pre_metrics["removed_idx"] = [int(i) for i in remove_idx]
            pre_metrics["removed_radii_mean"] = float(np.mean(radii[remove_idx]))
            pre_metrics["removed_speed_mean"] = float(np.mean(np.sqrt(
                vx[remove_idx]**2 + vy[remove_idx]**2
            )))

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

    return all_y, all_x, all_vx, all_vy, radii, removed, pre_metrics


# ─── Binning / C / Recovery (identical to prior passes) ───

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


def _sliding_C(X, window=75, step=25):
    T = X.shape[1]
    times, vals = [], []
    for t in range(0, T - window + 1, step):
        seg = X[:, t:t + window]
        times.append(t + window // 2)
        try: vals.append(compute_C(seg, "gaussian"))
        except Exception: vals.append(np.nan)
    return np.array(times), np.array(vals)


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


def compute_mobility_proxies(all_x, all_y, all_vx, all_vy, radii, removed, T_pre=500):
    active = ~removed
    x = np.nan_to_num(all_x[active, :T_pre], nan=0.0)
    y = np.nan_to_num(all_y[active, :T_pre], nan=0.0)
    vx = np.nan_to_num(all_vx[active, :T_pre], nan=0.0)
    vy = np.nan_to_num(all_vy[active, :T_pre], nan=0.0)
    n_active = active.sum()
    if n_active < 3:
        return {"msd": np.nan, "rms_velocity": np.nan, "neighbor_turnover": np.nan, "packing_var": np.nan}

    speeds = np.sqrt(vx**2 + vy**2)
    rms_vel = float(np.mean(speeds))

    dx = np.diff(x, axis=1)
    dy = np.diff(y, axis=1)
    displacements = np.cumsum(dx**2 + dy**2, axis=1)
    msd = float(np.mean(displacements[:, -1])) if displacements.shape[1] > 0 else np.nan

    contact_dist = 4.0
    n_changes = 0
    n_steps_check = min(T_pre - 1, 200)
    step_skip = max(1, n_steps_check // 50)

    for t in range(0, n_steps_check - step_skip, step_skip):
        p1 = np.column_stack([x[:, t], y[:, t]])
        p2 = np.column_stack([x[:, t + step_skip], y[:, t + step_skip]])
        contacts_t = set()
        for i in range(n_active):
            for j in range(i + 1, n_active):
                dij = np.linalg.norm(p1[i] - p1[j])
                if dij < contact_dist:
                    contacts_t.add((i, j))
        contacts_t2 = set()
        for i in range(n_active):
            for j in range(i + 1, n_active):
                dij = np.linalg.norm(p2[i] - p2[j])
                if dij < contact_dist:
                    contacts_t2.add((i, j))
        n_changes += len(contacts_t.symmetric_difference(contacts_t2))

    n_possible = n_active * (n_active - 1) / 2
    turnover = float(n_changes / max(50 * n_possible, 1))

    nn_dists = []
    for t in range(0, T_pre, 10):
        pos = np.column_stack([x[:, t], y[:, t]])
        for i in range(n_active):
            dists = [np.linalg.norm(pos[i] - pos[j]) for j in range(n_active) if j != i]
            if dists:
                nn_dists.append(min(dists))
    packing_var = float(np.std(nn_dists)) if nn_dists else np.nan

    return {"rms_velocity": rms_vel, "msd": msd,
            "neighbor_turnover": turnover, "packing_var": packing_var}


# ─── Generate ensemble ───

STRATEGIES = [
    ("S0", "random"),
    ("S1", "largest"),
    ("S2", "smallest"),
    ("S3", "highest_degree"),
    ("S4", "lowest_degree"),
    ("S5", "highest_force"),
]


def generate_selective_ensemble():
    """60 runs: 6 strategies × 10 reps at friction=0.40."""
    friction = 0.40
    n_reps = 10
    n_bins = 10
    rows = []

    t0 = time.time()
    for si, (slabel, sname) in enumerate(STRATEGIES):
        print(f"\n  Strategy = {slabel} ({sname})  [{si+1}/{len(STRATEGIES)}]", flush=True)
        for rep in range(n_reps):
            seed = 400 + 10 * si + rep
            y, x, vx, vy, radii, removed, pre_metrics = _granular_run_selective(
                n_grains=50, n_steps=1000, removal_step=500,
                removal_fraction=0.1, friction=friction, seed=seed,
                box_width=40.0, removal_strategy=sname,
            )

            binned = _bin_data(y, x, n_bins=n_bins)
            times, cvals = _sliding_C(binned, window=75, step=25)
            rec = measure_recovery(times, cvals, pert_start=500)

            pre = binned[:, :500]
            try:
                pre_ip = compute_predictive_information(pre, tau=1)
            except Exception:
                pre_ip = np.nan
            try:
                pre_cs = compute_statistical_complexity(pre, tau=1)
            except Exception:
                pre_cs = np.nan
            try:
                pre_mse = compute_mse(pre, scales=[1]).get(1, np.nan)
            except Exception:
                pre_mse = np.nan

            mob = compute_mobility_proxies(x, y, vx, vy, radii, removed, T_pre=500)

            row = {
                "strategy": sname, "strategy_label": slabel,
                "rep": rep, "seed": seed, "friction": friction,
                "pre_C": rec["pre_C"], "dip": rec["dip"],
                "restoration": rec["restoration"], "tau_rec": rec["tau_rec"],
                "pre_I_pred": pre_ip, "pre_C_sigma": pre_cs, "pre_MSE_s1": pre_mse,
            }
            row.update(mob)
            row.update({k: v for k, v in pre_metrics.items() if v is not None})
            rows.append(row)

            if (rep + 1) % 5 == 0:
                print(f"    rep {rep+1}/{n_reps} (C_pre={rec['pre_C']:.4f}, dip={rec['dip']:+.4f}, rest={rec['restoration']:.4f})", flush=True)

    print(f"\n  Generated {len(rows)} runs in {time.time() - t0:.0f}s")
    return rows


def add_residuals(rows):
    """Add Residual(C) — within strategy and global."""
    c_vals = np.array([r["pre_C"] for r in rows])
    global_mean = np.nanmean(c_vals)
    for r, c in zip(rows, c_vals):
        r["res_C_global"] = c - global_mean
    for sname in set(r["strategy"] for r in rows):
        mask = [i for i, r in enumerate(rows) if r["strategy"] == sname]
        level_mean = np.nanmean(c_vals[mask])
        for i in mask:
            rows[i]["res_C_within"] = c_vals[i] - level_mean
    return rows


def main():
    print(f"{SEP}")
    print("  RD-020: SELECTIVE REMOVAL INTERVENTION")
    print(f"{SEP}")
    print(f"  Friction: 0.40 (fixed)")
    print(f"  Box: 40.0 (fixed)")
    print(f"  Removal fraction: 10% (fixed)")
    print(f"  Strategies: S0 random / S1 largest / S2 smallest / S3 high-deg / S4 low-deg / S5 high-force")
    print(f"  10 replicates per strategy = 60 runs")

    rows = generate_selective_ensemble()
    rows = add_residuals(rows)

    with open("coherence-benchmark/results/rd020_selective_ensemble.json", "w") as f:
        json.dump([{k: (None if (isinstance(v, float) and np.isnan(v)) else
                        None if (isinstance(v, np.floating) and np.isnan(v)) else
                        v) for k, v in r.items()} for r in rows], f, indent=2)
    print(f"\n  Saved to coherence-benchmark/results/rd020_selective_ensemble.json")

    # Summary
    print(f"\n{SEP}")
    print("  SUMMARY TABLE (per strategy)")
    print(f"{SEP}")
    print(f"\n  {'Strat':<6s}  {'N':>3s}  {'C_pre':>7s}  {'dip':>8s}  {'Rest.':>7s}  {'τ':>5s}  {'MSD':>7s}")
    print(f"  {'-'*60}")
    for slabel, sname in STRATEGIES:
        sub = [r for r in rows if r["strategy"] == sname]
        n = len(sub)
        c = np.nanmean([r["pre_C"] for r in sub])
        d = np.nanmean([r["dip"] for r in sub])
        rest = np.nanmean([r["restoration"] for r in sub])
        tau = np.nanmean([r["tau_rec"] for r in sub])
        msd = np.nanmean([r["msd"] for r in sub])
        print(f"  {slabel+' '+sname:<6s}  {n:>3d}  {c:>7.4f}  {d:>+8.4f}  {rest:>7.4f}  {tau:>5.0f}  {msd:>7.2f}")

    return rows


if __name__ == "__main__":
    rows = main()
