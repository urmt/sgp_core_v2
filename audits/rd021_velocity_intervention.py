"""RD-021: Velocity-Field Organization Intervention.

Test whether manipulating velocity structure changes pre_C and recovery
while leaving contact structure largely unchanged.

6 conditions × 10 reps = 60 runs.

Conditions:
  V0: control (current random init)
  V1: coherent rightward drift (all vx += u)
  V2: coherent rotational field (tangent to center of mass)
  V3: two-domain shear (top half +, bottom half -)
  V4: randomized velocity directions (preserve speed)
  V5: velocity-scrambled control (coherent then permute)
"""

import numpy as np
import sys, time, json
sys.path.insert(0, "coherence-benchmark")
from metrics import *
from adapters.granular import _soft_sphere_force

SEP = "=" * 78


def _granular_run_velocity(
    n_grains=50, n_steps=1000, removal_step=500, removal_fraction=0.1,
    friction=0.3, seed=42, box_width=40.0, velocity_condition="V0",
):
    """Modified granular run with velocity-field manipulation.

    Position initialization is identical to baseline. Velocity initialization
    is determined by `velocity_condition`.
    """
    rng = np.random.default_rng(seed)
    radii = rng.uniform(0.8, 1.5, n_grains)
    masses = radii ** 2

    x = rng.uniform(2, box_width - 2, n_grains)
    y = rng.uniform(5, 30, n_grains)

    # --- Velocity initialization per condition ---
    if velocity_condition == "V0":
        # Control: uniform random in [-0.5, 0.5]
        vx = rng.uniform(-0.5, 0.5, n_grains)
        vy = rng.uniform(-0.5, 0.5, n_grains)
    elif velocity_condition == "V1":
        # Coherent rightward drift
        vx = rng.uniform(-0.5, 0.5, n_grains) + 2.0
        vy = rng.uniform(-0.5, 0.5, n_grains)
    elif velocity_condition == "V2":
        # Coherent rotational field (tangent to center of mass)
        com_x, com_y = x.mean(), y.mean()
        rx, ry = x - com_x, y - com_y
        # Tangent: rotate 90 deg counterclockwise
        tx, ty = -ry, rx
        # Normalize to unit, scale by random magnitude in [0.3, 0.7]
        norms = np.sqrt(tx**2 + ty**2)
        norms[norms == 0] = 1
        ux, uy = tx / norms, ty / norms
        magnitudes = rng.uniform(0.3, 0.7, n_grains)
        vx = ux * magnitudes + rng.uniform(-0.1, 0.1, n_grains)
        vy = uy * magnitudes + rng.uniform(-0.1, 0.1, n_grains)
    elif velocity_condition == "V3":
        # Two-domain shear: top half vx = +u, bottom half vx = -u
        median_y = np.median(y)
        u = 2.0
        vx = np.where(y > median_y, u, -u) + rng.uniform(-0.1, 0.1, n_grains)
        vy = rng.uniform(-0.5, 0.5, n_grains)
    elif velocity_condition == "V4":
        # Randomized directions: preserve speed distribution, randomize angles
        speeds = rng.uniform(0.0, np.sqrt(0.5**2 + 0.5**2) * np.sqrt(2), n_grains)
        angles = rng.uniform(0, 2 * np.pi, n_grains)
        vx = speeds * np.cos(angles)
        vy = speeds * np.sin(angles)
    elif velocity_condition == "V5":
        # Coherent field then random permutation
        # First generate a coherent field
        com_x, com_y = x.mean(), y.mean()
        rx, ry = x - com_x, y - com_y
        tx, ty = -ry, rx
        norms = np.sqrt(tx**2 + ty**2)
        norms[norms == 0] = 1
        ux, uy = tx / norms, ty / norms
        magnitudes = rng.uniform(0.3, 0.7, n_grains)
        coherent_vx = ux * magnitudes + rng.uniform(-0.1, 0.1, n_grains)
        coherent_vy = uy * magnitudes + rng.uniform(-0.1, 0.1, n_grains)
        # Permute
        perm = rng.permutation(n_grains)
        vx = coherent_vx[perm]
        vy = coherent_vy[perm]
    else:
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

    return all_y, all_x, all_vx, all_vy, radii, removed


# ─── Binning / C / Recovery (identical) ───

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


# ─── Structural diagnostics (from RD-019) ───

def compute_structural_diagnostics(all_x, all_y, radii, removed, box_width, T_pre=500):
    active = ~removed
    x = np.nan_to_num(all_x[active, :T_pre], nan=0.0)
    y = np.nan_to_num(all_y[active, :T_pre], nan=0.0)
    n_active = active.sum()
    if n_active < 3:
        return {"mean_nn_dist": np.nan, "contact_count": np.nan,
                "coordination_number": np.nan, "component_count": np.nan,
                "clustering_coefficient": np.nan}

    active_radii = radii[active]
    n_samples = 10
    sample_times = np.linspace(50, T_pre - 1, n_samples, dtype=int)

    nn_dists, contact_counts, coord_numbers, component_counts, clustering_coeffs = [], [], [], [], []

    for t in sample_times:
        pos = np.column_stack([x[:, t], y[:, t]])
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
        contact_counts.append(int(np.sum(contact_matrix) / 2))
        coord_numbers.append(float(np.mean(contact_matrix.sum(axis=1))))

        # Components via BFS
        visited = np.zeros(n_active, dtype=bool)
        n_components = 0
        for start in range(n_active):
            if visited[start]: continue
            n_components += 1
            queue = [start]
            while queue:
                node = queue.pop()
                if visited[node]: continue
                visited[node] = True
                for nbr in np.where(contact_matrix[node])[0]:
                    if not visited[nbr]:
                        queue.append(int(nbr))
        component_counts.append(int(n_components))

        # Clustering
        if n_active > 5:
            cc_sum = 0
            cc_n = 0
            for i in range(n_active):
                nbrs = np.where(contact_matrix[i])[0]
                k = len(nbrs)
                if k < 2: continue
                edges_among = 0
                for ii_idx in range(len(nbrs)):
                    for jj_idx in range(ii_idx + 1, len(nbrs)):
                        if contact_matrix[nbrs[ii_idx], nbrs[jj_idx]]:
                            edges_among += 1
                cc_sum += 2.0 * edges_among / (k * (k - 1))
                cc_n += 1
            clustering_coeffs.append(cc_sum / cc_n if cc_n > 0 else 0.0)
        else:
            clustering_coeffs.append(np.nan)

    return {
        "mean_nn_dist": float(np.mean(nn_dists)),
        "contact_count": float(np.mean(contact_counts)),
        "coordination_number": float(np.mean(coord_numbers)),
        "component_count": float(np.mean(component_counts)),
        "clustering_coefficient": float(np.nanmean(clustering_coeffs)),
    }


# ─── Velocity diagnostics ───

def compute_velocity_diagnostics(all_vx, all_vy, all_x, all_y, radii, removed, T_pre=500):
    """Compute velocity-field organization diagnostics from pre-perturbation data.

    Reports diagnostics at THREE time windows:
      - initial (t=0): captures the manipulation effect
      - pre_perturbation (t=100-450): what the system "remembers" by the time we measure C
      - full_pre: averages over the entire pre-perturbation window

    Metrics per window:
      - velocity_alignment: |<v>| / <|v|>
      - velocity_correlation_length: r where C(r) drops to 0.5 of initial value
      - mean_neighbor_velocity_similarity: mean cos(θ) between contacting pairs
      - velocity_entropy: Shannon entropy of angle histogram (12 bins)
      - kinetic_energy: mean 0.5 * m * v^2
    """
    active = ~removed
    vx = np.nan_to_num(all_vx[active, :T_pre], nan=0.0)
    vy = np.nan_to_num(all_vy[active, :T_pre], nan=0.0)
    x = np.nan_to_num(all_x[active, :T_pre], nan=0.0)
    y = np.nan_to_num(all_y[active, :T_pre], nan=0.0)
    masses = radii[active] ** 2
    n_active = active.sum()
    if n_active < 3:
        return {}

    def diag_at_time(t):
        vt_x = vx[:, t]
        vt_y = vy[:, t]
        speeds = np.sqrt(vt_x**2 + vt_y**2)
        ke = 0.5 * float(np.mean(masses * speeds**2))
        align = float(np.sqrt(vt_x.sum()**2 + vt_y.sum()**2) / (n_active * speeds.mean() + 1e-10))

        unit_vx = vt_x / (speeds + 1e-10)
        unit_vy = vt_y / (speeds + 1e-10)
        pos = np.column_stack([x[:, t], y[:, t]])

        # Correlation length: r where spatial correlation drops below 0.5
        bins_r = np.linspace(0, 20, 21)
        dists = []
        dots = []
        for i in range(n_active):
            for j in range(i+1, n_active):
                dists.append(np.linalg.norm(pos[i] - pos[j]))
                dots.append(unit_vx[i]*unit_vx[j] + unit_vy[i]*unit_vy[j])
        dists = np.array(dists)
        dots = np.array(dots)
        bin_idx = np.digitize(dists, bins_r)
        corrs = []
        for k in range(1, len(bins_r)):
            mask = bin_idx == k
            if mask.sum() > 5:
                corrs.append(np.mean(dots[mask]))
            else:
                corrs.append(np.nan)
        corrs = np.array(corrs)
        # Find first bin where corr drops below 50% of bin-0 value
        if not np.any(np.isnan(corrs)) and len(corrs) > 0 and corrs[0] > 0:
            c0 = corrs[0]
            threshold = c0 * 0.5
            below = np.where(corrs < threshold)[0]
            if len(below) > 0:
                corrlen = float(bins_r[below[0]])
            else:
                corrlen = float(bins_r[-1])
        else:
            corrlen = np.nan

        # Neighbor velocity similarity
        contact_thresh = 4.0
        nbr_sims = []
        for i in range(n_active):
            for j in range(i+1, n_active):
                d = np.linalg.norm(pos[i] - pos[j])
                if d < contact_thresh and speeds[i] > 0 and speeds[j] > 0:
                    cos_t = (vt_x[i]*vt_x[j] + vt_y[i]*vt_y[j]) / (speeds[i] * speeds[j])
                    nbr_sims.append(cos_t)
        nbr_sim = float(np.mean(nbr_sims)) if nbr_sims else 0.0

        # Entropy
        angles = np.arctan2(unit_vy, unit_vx)
        hist, _ = np.histogram(angles, bins=12, range=(-np.pi, np.pi))
        p = hist / (hist.sum() + 1e-10)
        p = p[p > 0]
        ent = float(-np.sum(p * np.log(p)))

        return align, corrlen, nbr_sim, ent, ke

    # Window 1: initial state (t=0)
    a_i, cl_i, ns_i, e_i, ke_i = diag_at_time(0)
    # Window 2: pre-perturbation (t=100 to 450, sampled)
    a_p, cl_p, ns_p, e_p, ke_p = [], [], [], [], []
    for t in [100, 200, 300, 400]:
        try:
            ai, cli, nsi, ei, kei = diag_at_time(t)
            a_p.append(ai); cl_p.append(cli); ns_p.append(nsi); e_p.append(ei); ke_p.append(kei)
        except Exception:
            pass

    def safe(arr):
        arr = np.array([v for v in arr if v is not None and not (isinstance(v, float) and np.isnan(v))])
        return float(np.mean(arr)) if len(arr) else np.nan

    return {
        # Initial (manipulation effect)
        "vel_align_initial": a_i,
        "vel_corrlen_initial": cl_i,
        "vel_nbrsim_initial": ns_i,
        "vel_entropy_initial": e_i,
        "vel_ke_initial": ke_i,
        # Pre-perturbation (what's left after friction/washout)
        "vel_align_pre": safe(a_p),
        "vel_corrlen_pre": safe(cl_p),
        "vel_nbrsim_pre": safe(ns_p),
        "vel_entropy_pre": safe(e_p),
        "vel_ke_pre": safe(ke_p),
        # Aliases for compatibility with Director's spec
        "velocity_alignment": safe(a_p),
        "velocity_correlation_length": safe(cl_p),
        "mean_neighbor_velocity_similarity": safe(ns_p),
        "velocity_entropy": safe(e_p),
        "kinetic_energy": safe(ke_p),
    }


# ─── Generate ensemble ───

VELOCITY_CONDITIONS = ["V0", "V1", "V2", "V3", "V4", "V5"]


def generate_velocity_ensemble():
    friction = 0.40
    n_reps = 10
    n_bins = 10
    rows = []

    t0 = time.time()
    for vi, vcond in enumerate(VELOCITY_CONDITIONS):
        print(f"\n  Velocity Condition = {vcond}  [{vi+1}/{len(VELOCITY_CONDITIONS)}]", flush=True)
        for rep in range(n_reps):
            seed = 500 + 10 * vi + rep
            y, x, vx, vy, radii, removed = _granular_run_velocity(
                n_grains=50, n_steps=1000, removal_step=500,
                removal_fraction=0.1, friction=friction, seed=seed,
                box_width=40.0, velocity_condition=vcond,
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

            struct = compute_structural_diagnostics(x, y, radii, removed, 40.0, T_pre=500)
            vdiag = compute_velocity_diagnostics(vx, vy, x, y, radii, removed, T_pre=500)

            row = {
                "velocity_condition": vcond, "rep": rep, "seed": seed, "friction": friction,
                "pre_C": rec["pre_C"], "dip": rec["dip"],
                "restoration": rec["restoration"], "tau_rec": rec["tau_rec"],
                "pre_I_pred": pre_ip, "pre_C_sigma": pre_cs, "pre_MSE_s1": pre_mse,
            }
            row.update(struct)
            row.update(vdiag)
            rows.append(row)

            if (rep + 1) % 5 == 0:
                print(f"    rep {rep+1}/{n_reps} (C_pre={rec['pre_C']:.4f}, align={vdiag['velocity_alignment']:.3f}, KE={vdiag['kinetic_energy']:.2f})", flush=True)

    print(f"\n  Generated {len(rows)} runs in {time.time() - t0:.0f}s")
    return rows


def add_residuals(rows):
    c_vals = np.array([r["pre_C"] for r in rows])
    global_mean = np.nanmean(c_vals)
    for r, c in zip(rows, c_vals):
        r["res_C_global"] = c - global_mean
    for vc in set(r["velocity_condition"] for r in rows):
        mask = [i for i, r in enumerate(rows) if r["velocity_condition"] == vc]
        level_mean = np.nanmean(c_vals[mask])
        for i in mask:
            rows[i]["res_C_within"] = c_vals[i] - level_mean
    return rows


def main():
    print(f"{SEP}")
    print("  RD-021: VELOCITY-FIELD ORGANIZATION INTERVENTION")
    print(f"{SEP}")
    print(f"  Friction: 0.40 (fixed)")
    print(f"  Box: 40.0 (fixed)")
    print(f"  Removal: 10% (fixed)")
    print(f"  Manipulating ONLY initial velocity field")
    print(f"  V0 control | V1 rightward drift | V2 rotational | V3 shear | V4 random dirs | V5 scramble")

    rows = generate_velocity_ensemble()
    rows = add_residuals(rows)

    with open("coherence-benchmark/results/rd021_velocity_ensemble.json", "w") as f:
        json.dump([{k: (None if (isinstance(v, float) and np.isnan(v)) else
                        None if (isinstance(v, np.floating) and np.isnan(v)) else
                        v) for k, v in r.items()} for r in rows], f, indent=2)
    print(f"\n  Saved to coherence-benchmark/results/rd021_velocity_ensemble.json")

    # Summary
    print(f"\n{SEP}")
    print("  SUMMARY TABLE (per velocity condition)")
    print(f"{SEP}")
    print(f"\n  {'Vcond':<5s}  {'N':>3s}  {'C_pre':>7s}  {'dip':>8s}  {'Rest.':>7s}  {'τ':>5s}  {'align':>7s}  {'corrlen':>7s}  {'nbrsim':>7s}  {'ent':>5s}  {'KE':>7s}")
    print(f"  {'-'*95}")
    for vc in VELOCITY_CONDITIONS:
        sub = [r for r in rows if r["velocity_condition"] == vc]
        n = len(sub)
        c = np.nanmean([r["pre_C"] for r in sub])
        d = np.nanmean([r["dip"] for r in sub])
        rest = np.nanmean([r["restoration"] for r in sub])
        tau = np.nanmean([r["tau_rec"] for r in sub])
        al = np.nanmean([r["velocity_alignment"] for r in sub])
        cl = np.nanmean([r["velocity_correlation_length"] for r in sub])
        ns = np.nanmean([r["mean_neighbor_velocity_similarity"] for r in sub])
        en = np.nanmean([r["velocity_entropy"] for r in sub])
        ke = np.nanmean([r["kinetic_energy"] for r in sub])
        print(f"  {vc:<5s}  {n:>3d}  {c:>7.4f}  {d:>+8.4f}  {rest:>7.4f}  {tau:>5.0f}  {al:>7.3f}  {cl:>7.2f}  {ns:>+7.3f}  {en:>5.2f}  {ke:>7.2f}")

    return rows


if __name__ == "__main__":
    rows = main()
