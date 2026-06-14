"""RD-019: Density Intervention Audit.

Execute the density sweep at fixed friction=0.40.
6 box_width conditions × 10 replicates = 60 runs.
"""

import numpy as np
import sys, time, json
sys.path.insert(0, "coherence-benchmark")
from metrics import *
from adapters.granular import _soft_sphere_force

SEP = "=" * 78


# ─── Modified _granular_run: ADD box_width parameter ───

def _granular_run(
    n_grains=50, n_steps=1000, removal_step=500, removal_fraction=0.1,
    friction=0.3, seed=42, box_width=40.0,
):
    rng = np.random.default_rng(seed)
    radii = rng.uniform(0.8, 1.5, n_grains)
    masses = radii ** 2
    # box_width is now a parameter (default 40.0 — preserves prior ensemble)

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

    return all_y, all_x, all_vx, all_vy, radii, removed, box_width


# ─── Binning ───

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


# ─── Mobility proxies ───

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

    return {
        "rms_velocity": rms_vel,
        "msd": msd,
        "neighbor_turnover": turnover,
        "packing_var": packing_var,
    }


# ─── Task 3: Structural validation descriptors ───

def compute_structural_validation(all_x, all_y, radii, removed, box_width, T_pre=500):
    """Density-manipulation structural checks: confirm density actually changes packing.

    Computes per-run (pre-perturbation, T_pre=500):
      - mean_nn_dist: mean nearest-neighbor distance
      - contact_count: mean number of contacts (grains within sum-of-radii+epsilon)
      - coordination_number: mean contacts per active grain
      - component_count: number of disconnected components in contact graph
      - largest_component_size: fraction of active grains in largest component
      - clustering_coefficient: mean local clustering in contact graph
    """
    active = ~removed
    x = np.nan_to_num(all_x[active, :T_pre], nan=0.0)
    y = np.nan_to_num(all_y[active, :T_pre], nan=0.0)
    n_active = active.sum()
    if n_active < 3:
        return {
            "mean_nn_dist": np.nan, "contact_count": np.nan, "coordination_number": np.nan,
            "component_count": np.nan, "largest_component_size": np.nan,
            "clustering_coefficient": np.nan,
        }

    active_radii = radii[active]
    n_samples = 10  # sample times
    sample_times = np.linspace(50, T_pre - 1, n_samples, dtype=int)

    nn_dists = []
    contact_counts = []
    coord_numbers = []
    component_counts = []
    largest_component_sizes = []
    clustering_coeffs = []

    for t in sample_times:
        pos = np.column_stack([x[:, t], y[:, t]])

        # Build adjacency: grain i, j in contact if distance < sum of radii + 0.3
        contact_matrix = np.zeros((n_active, n_active), dtype=bool)
        nn_dist_t = np.zeros(n_active)

        for i in range(n_active):
            min_d = np.inf
            for j in range(n_active):
                if i == j: continue
                d = np.linalg.norm(pos[i] - pos[j])
                threshold = active_radii[i] + active_radii[j] + 0.3
                if d < threshold:
                    contact_matrix[i, j] = True
                    contact_matrix[j, i] = True
                if d < min_d:
                    min_d = d
            nn_dist_t[i] = min_d

        nn_dists.append(np.mean(nn_dist_t))

        # Contact count: total edges
        c_count = int(np.sum(contact_matrix) / 2)
        contact_counts.append(c_count)

        # Coordination: mean contacts per grain
        deg = contact_matrix.sum(axis=1)
        coord_numbers.append(float(np.mean(deg)))

        # Components via BFS
        visited = np.zeros(n_active, dtype=bool)
        n_components = 0
        largest_size = 0
        for start in range(n_active):
            if visited[start]: continue
            n_components += 1
            # BFS
            queue = [start]
            comp_size = 0
            while queue:
                node = queue.pop()
                if visited[node]: continue
                visited[node] = True
                comp_size += 1
                neighbors = np.where(contact_matrix[node])[0]
                queue.extend([n for n in neighbors if not visited[n]])
            largest_size = max(largest_size, comp_size)

        component_counts.append(int(n_components))
        largest_component_sizes.append(float(largest_size) / n_active)

        # Clustering coefficient: fraction of triangles among neighbors
        if n_active > 5:
            cc_sum = 0
            cc_n = 0
            for i in range(n_active):
                nbrs = np.where(contact_matrix[i])[0]
                k = len(nbrs)
                if k < 2:
                    continue
                edges_among = 0
                for ii_idx in range(len(nbrs)):
                    for jj_idx in range(ii_idx + 1, len(nbrs)):
                        if contact_matrix[nbrs[ii_idx], nbrs[jj_idx]]:
                            edges_among += 1
                cc_sum += 2.0 * edges_among / (k * (k - 1))
                cc_n += 1
            if cc_n > 0:
                clustering_coeffs.append(cc_sum / cc_n)
            else:
                clustering_coeffs.append(0.0)
        else:
            clustering_coeffs.append(np.nan)

    return {
        "mean_nn_dist": float(np.mean(nn_dists)),
        "contact_count": float(np.mean(contact_counts)),
        "coordination_number": float(np.mean(coord_numbers)),
        "component_count": float(np.mean(component_counts)),
        "largest_component_size": float(np.mean(largest_component_sizes)),
        "clustering_coefficient": float(np.nanmean(clustering_coeffs)),
    }


# ─── Generate density ensemble ───

def generate_density_ensemble():
    """60 runs: 6 box_widths × 10 replicates at friction=0.40."""
    friction = 0.40
    box_widths = [30, 35, 40, 45, 50, 55]  # D1-D6
    n_reps = 10
    n_bins = 10
    rows = []

    t0 = time.time()
    for di, bw in enumerate(box_widths):
        print(f"\n  Box Width = {bw}  [{di+1}/{len(box_widths)}]", flush=True)
        for rep in range(n_reps):
            seed = 300 + 10 * di + rep  # Distinct seed range from existing (200-209 for μ=0.40)
            y, x, vx, vy, radii, removed, box_width = _granular_run(
                n_grains=50, n_steps=1000, removal_step=500,
                removal_fraction=0.1, friction=friction, seed=seed,
                box_width=bw,
            )

            # Binned data for C
            binned = _bin_data(y, x, n_bins=n_bins)
            times, cvals = _sliding_C(binned, window=75, step=25)
            rec = measure_recovery(times, cvals, pert_start=500)

            # Pre-perturbation competitor metrics
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

            # Mobility proxies
            mob = compute_mobility_proxies(x, y, vx, vy, radii, removed, T_pre=500)

            # Task 3: structural validation
            struct = compute_structural_validation(x, y, radii, removed, box_width, T_pre=500)

            # Effective density (grains per area)
            effective_density = 50.0 / (box_width * 30.0)

            row = {
                "friction": friction, "box_width": bw,
                "rep": rep, "seed": seed,
                "effective_density": effective_density,
                "pre_C": rec["pre_C"], "dip": rec["dip"],
                "restoration": rec["restoration"], "tau_rec": rec["tau_rec"],
                "pre_I_pred": pre_ip, "pre_C_sigma": pre_cs, "pre_MSE_s1": pre_mse,
            }
            row.update(mob)
            row.update(struct)
            rows.append(row)

            if (rep + 1) % 5 == 0:
                print(f"    rep {rep+1}/{n_reps} (C_pre={rec['pre_C']:.4f}, msd={mob['msd']:.2f}, density={effective_density:.4f})", flush=True)

    print(f"\n  Generated {len(rows)} runs in {time.time() - t0:.0f}s")
    return rows


# ─── Residual(C) computation: within and global ───

def compute_residuals(rows):
    """Add Residual(C) — within density level and global (mean-centered)."""
    c_vals = np.array([r["pre_C"] for r in rows])

    # Global residual: C - global mean
    global_mean = np.nanmean(c_vals)
    for r, c in zip(rows, c_vals):
        r["res_C_global"] = c - global_mean

    # Within density level: C - mean(C within same box_width)
    for bw in set(r["box_width"] for r in rows):
        mask = [i for i, r in enumerate(rows) if r["box_width"] == bw]
        level_vals = c_vals[mask]
        level_mean = np.nanmean(level_vals)
        for i in mask:
            rows[i]["res_C_within"] = c_vals[i] - level_mean

    return rows


# ─── Main ───

def main():
    print(f"{SEP}")
    print("  RD-019: DENSITY INTERVENTION AUDIT")
    print(f"{SEP}")
    print(f"  Friction: 0.40 (fixed)")
    print(f"  Box widths: 30, 35, 40, 45, 50, 55 (D1-D6)")
    print(f"  10 replicates per condition = 60 runs total")

    rows = generate_density_ensemble()
    rows = compute_residuals(rows)

    # Save
    with open("coherence-benchmark/results/rd019_density_ensemble.json", "w") as f:
        json.dump([{k: (None if (isinstance(v, float) and np.isnan(v)) else
                        None if (isinstance(v, np.floating) and np.isnan(v)) else
                        v) for k, v in r.items()} for r in rows], f, indent=2)
    print(f"\n  Saved to coherence-benchmark/results/rd019_density_ensemble.json")

    # Print summary
    print(f"\n{SEP}")
    print("  SUMMARY TABLE (per density level)")
    print(f"{SEP}")
    print(f"\n  {'BW':>3s}  {'Density':>8s}  {'N':>3s}  {'C_pre':>7s}  {'dip':>8s}  {'Rest.':>7s}  {'τ':>5s}  {'MSD':>7s}  {'NNdist':>7s}  {'Coord':>6s}  {'Comps':>6s}")
    print(f"  {'-' * 95}")
    for bw in [30, 35, 40, 45, 50, 55]:
        sub = [r for r in rows if r["box_width"] == bw]
        n = len(sub)
        c = np.nanmean([r["pre_C"] for r in sub])
        d = np.nanmean([r["dip"] for r in sub])
        rest = np.nanmean([r["restoration"] for r in sub])
        tau = np.nanmean([r["tau_rec"] for r in sub])
        msd = np.nanmean([r["msd"] for r in sub])
        nnd = np.nanmean([r["mean_nn_dist"] for r in sub])
        coord = np.nanmean([r["coordination_number"] for r in sub])
        comps = np.nanmean([r["component_count"] for r in sub])
        dens = sub[0]["effective_density"] if sub else 0
        print(f"  {bw:>3.0f}  {dens:>8.5f}  {n:>3d}  {c:>7.4f}  {d:>+8.4f}  {rest:>7.4f}  {tau:>5.0f}  {msd:>7.2f}  {nnd:>7.3f}  {coord:>6.2f}  {comps:>6.1f}")

    return rows


if __name__ == "__main__":
    rows = main()
