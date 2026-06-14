"""
RD-9E: Surprise Persistence Audit
==================================
SP is the only surviving novelty candidate from RD-9.
This audit attempts to falsify it through:
  1. Continuity check (is SP binary?)
  2. Estimator sensitivity (parameter sweeps)
  3. Coarse graining (bin count)
  4. Physical event mapping (high vs low SP trajectories)
  5. Reconstruction test (can friction+recovery predict SP?)
  6. Domain transfer (coupled markov, modular, hierarchical, forest, sandpile)
"""

import sys
import os
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'coherence-benchmark'))

from synthetic.generators import coupled_markov, modular, hierarchical, critical
from adapters.ecosystem import EcosystemAdapter


# ============================================================================
# GRANULAR DEM (same as rd9)
# ============================================================================

def _soft_sphere_force(all_y, all_x, all_vx, all_vy, radii, dt=0.005, base_friction=0.3, base_normal=50.0):
    n_grains = len(radii)
    fx = np.zeros(n_grains)
    fy = np.zeros(n_grains) - 1.0

    for i in range(n_grains):
        for j in range(i + 1, n_grains):
            dx = all_x[j] - all_x[i]
            dy = all_y[j] - all_y[i]
            dist = np.sqrt(dx**2 + dy**2)
            overlap = radii[i] + radii[j] - dist
            if overlap > 0:
                nx, ny = dx / (dist + 1e-10), dy / (dist + 1e-10)
                fn = base_normal * overlap
                dvx = all_vx[j] - all_vx[i]
                dvy = all_vy[j] - all_vy[i]
                dvn = dvx * nx + dvy * ny
                ft = base_friction * fn if dvn < 0 else 0
                fx[i] += fn * nx + ft * (-ny)
                fy[i] += fn * ny + ft * nx
                fx[j] -= fn * nx + ft * (-ny)
                fy[j] -= fn * ny + ft * nx

    return fx, fy


def run_sim(n_grains=50, n_steps=1500, friction=0.3, seed=42, return_trajectories=False):
    rng = np.random.default_rng(seed)
    radii = np.full(n_grains, 0.25)
    all_x = rng.uniform(1, 9, n_grains)
    all_y = rng.uniform(1, 9, n_grains)
    all_vx = rng.normal(0, 0.1, n_grains)
    all_vy = rng.normal(0, 0.1, n_grains)
    dt = 0.005

    y_hist = np.zeros((n_grains, n_steps))
    x_hist = np.zeros((n_grains, n_steps))
    vx_hist = np.zeros((n_grains, n_steps))
    vy_hist = np.zeros((n_grains, n_steps))

    for t in range(n_steps):
        fx, fy = _soft_sphere_force(all_y, all_x, all_vx, all_vy, radii,
                                     dt=dt, base_friction=friction)
        all_vx += fx * dt
        all_vy += fy * dt
        damping = 1 - 0.1 * friction
        all_vx *= damping
        all_vy *= damping
        all_x += all_vx * dt
        all_y += all_vy * dt
        all_x = np.clip(all_x, 0.5, 9.5)
        all_y = np.clip(all_y, 0.5, 9.5)

        # Remove grains that fall below floor
        below = all_y < 0.2
        all_y[below] = rng.uniform(8, 9, np.sum(below))
        all_x[below] = rng.uniform(1, 9, np.sum(below))
        all_vy[below] = 0

        y_hist[:, t] = all_y
        x_hist[:, t] = all_x
        vx_hist[:, t] = all_vx
        vy_hist[:, t] = all_vy

    if return_trajectories:
        return y_hist, x_hist, vx_hist, vy_hist
    return y_hist


# ============================================================================
# SP COMPUTATION (generalized for any multivariate time series)
# ============================================================================

def compute_sp(ts, k=5, warmup=100, threshold_percentile=90):
    """Compute Surprise Persistence for a (n_components, T) time series.
    Returns SP value and surprise time series."""
    n_comp, T = ts.shape
    surprise_len = T - warmup
    if surprise_len < 20:
        return 0.0, np.array([])

    surprise_ts = np.zeros(surprise_len)
    count = 0

    for g in range(n_comp):
        y = ts[g, :]
        valid = ~np.isnan(y)
        if np.sum(valid) < warmup + k + 10:
            continue
        y_clean = y[valid]

        usable = len(y_clean) - warmup - k - 1
        if usable < 10:
            continue
        n = min(usable, surprise_len)

        lags = np.zeros((n, k))
        for j in range(k):
            lags[:, j] = y_clean[warmup + j:warmup + j + n]
        targets = y_clean[warmup + k:warmup + k + n]

        try:
            beta = np.linalg.lstsq(lags, targets, rcond=None)[0]
            predicted = lags @ beta
            errs = np.abs(targets - predicted)
            surprise_ts[:n] += errs
            count += 1
        except Exception:
            pass

    if count > 0:
        surprise_ts /= count

    nonzero = surprise_ts[surprise_ts > 0]
    if len(nonzero) < 10:
        return 0.0, surprise_ts

    threshold = np.percentile(nonzero, threshold_percentile)
    surprise_binary = (surprise_ts > threshold).astype(float)

    if np.sum(surprise_binary) < 5:
        return 0.0, surprise_ts

    n = len(surprise_binary)
    acf = np.correlate(surprise_binary - np.mean(surprise_binary),
                       surprise_binary - np.mean(surprise_binary), mode='full')
    acf = acf[n - 1:]
    if acf[0] > 0:
        acf /= acf[0]

    for i in range(1, len(acf)):
        if acf[i] < 1.0 / np.e:
            return float(i), surprise_ts
    return float(len(acf)), surprise_ts


def compute_sp_multi(ts_list, k=5, warmup=100, threshold_percentile=90):
    """Compute SP across multiple time series (for domain transfer).
    Returns mean SP and per-run SP values."""
    sp_values = []
    for ts in ts_list:
        sp, _ = compute_sp(ts, k=k, warmup=warmup, threshold_percentile=threshold_percentile)
        sp_values.append(sp)
    return np.mean(sp_values), sp_values


# ============================================================================
# STEP 1: CONTINUITY CHECK
# ============================================================================

def step1_continuity(n_runs=72):
    """Is SP continuous or binary?"""
    print("=" * 70)
    print("STEP 1: CONTINUITY CHECK")
    print("=" * 70)

    frictions = np.linspace(0.1, 1.5, 12)
    n_reps = 6
    sp_values = []

    t0 = time.time()
    for i, mu in enumerate(frictions):
        for r in range(n_reps):
            seed = i * 100 + r + 1000
            y = run_sim(n_grains=50, n_steps=1500, friction=mu, seed=seed)
            sp, _ = compute_sp(y, k=5, warmup=100, threshold_percentile=90)
            sp_values.append(sp)
            if (i * n_reps + r + 1) % 20 == 0:
                elapsed = time.time() - t0
                print(f"  [{i * n_reps + r + 1}/{n_runs}] {elapsed:.0f}s | μ={mu:.2f} SP={sp:.1f}")

    sp_values = np.array(sp_values)
    unique_vals = np.unique(sp_values)

    print(f"\nTotal runs: {len(sp_values)}")
    print(f"Unique SP values: {unique_vals}")
    print(f"SP distribution:")
    for v in unique_vals:
        count = np.sum(sp_values == v)
        print(f"  SP={v:.1f}: {count} runs ({100 * count / len(sp_values):.1f}%)")

    print(f"\nMean: {np.mean(sp_values):.3f}, Std: {np.std(sp_values):.3f}")
    print(f"Min: {np.min(sp_values):.1f}, Max: {np.max(sp_values):.1f}")

    if len(unique_vals) <= 3:
        print("\n⚠ SP appears DISCRETE (≤3 unique values). Likely discretization artifact.")
        is_continuous = False
    else:
        print(f"\n✓ SP has {len(unique_vals)} unique values — potentially continuous.")
        is_continuous = True

    # Try finer thresholds to see if we get more resolution
    print("\n--- Finer threshold sweep ---")
    for pct in [80, 85, 90, 95]:
        sp_fine = []
        for i, mu in enumerate(frictions):
            for r in range(n_reps):
                seed = i * 100 + r + 1000
                y = run_sim(n_grains=50, n_steps=1500, friction=mu, seed=seed)
                sp, _ = compute_sp(y, k=5, warmup=100, threshold_percentile=pct)
                sp_fine.append(sp)
        unique_fine = np.unique(sp_fine)
        print(f"  pct={pct}: {len(unique_fine)} unique values {unique_fine}")

    return sp_values, is_continuous


# ============================================================================
# STEP 2: ESTIMATOR SENSITIVITY
# ============================================================================

def step2_estimator_sensitivity(n_runs=36):
    """Vary SP parameters: k, threshold, warmup."""
    print("\n" + "=" * 70)
    print("STEP 2: ESTIMATOR SENSITIVITY")
    print("=" * 70)

    frictions = np.linspace(0.1, 1.5, 6)
    seeds = [i * 100 + 1000 for i in range(6)]

    results = {}

    # Parameter grid
    k_values = [3, 5, 10]
    threshold_values = [80, 85, 90, 95]
    warmup_values = [50, 100, 200]

    # Precompute raw time series (reuse across parameter settings)
    print("Precomputing time series...")
    raw_data = []
    for mu in frictions:
        for seed in seeds:
            y = run_sim(n_grains=50, n_steps=1500, friction=mu, seed=seed)
            raw_data.append((mu, y))

    # Sweep k
    print("\n--- Varying AR order (k) ---")
    for k in k_values:
        sp_vals = [compute_sp(y, k=k, warmup=100, threshold_percentile=90)[0] for _, y in raw_data]
        unique = np.unique(sp_vals)
        print(f"  k={k}: mean={np.mean(sp_vals):.3f}, std={np.std(sp_vals):.3f}, unique={unique}")

    # Sweep threshold
    print("\n--- Varying surprise threshold ---")
    for pct in threshold_values:
        sp_vals = [compute_sp(y, k=5, warmup=100, threshold_percentile=pct)[0] for _, y in raw_data]
        unique = np.unique(sp_vals)
        print(f"  pct={pct}: mean={np.mean(sp_vals):.3f}, std={np.std(sp_vals):.3f}, unique={unique}")

    # Sweep warmup
    print("\n--- Varying warmup ---")
    for w in warmup_values:
        sp_vals = [compute_sp(y, k=5, warmup=w, threshold_percentile=90)[0] for _, y in raw_data]
        unique = np.unique(sp_vals)
        print(f"  warmup={w}: mean={np.mean(sp_vals):.3f}, std={np.std(sp_vals):.3f}, unique={unique}")

    # Full grid: k × threshold
    print("\n--- Full parameter grid (k × threshold) ---")
    grid_results = {}
    for k in k_values:
        for pct in threshold_values:
            sp_vals = [compute_sp(y, k=k, warmup=100, threshold_percentile=pct)[0] for _, y in raw_data]
            unique = np.unique(sp_vals)
            grid_results[f"k={k}_pct={pct}"] = {
                'mean': float(np.mean(sp_vals)),
                'std': float(np.std(sp_vals)),
                'n_unique': len(unique),
                'unique': unique.tolist()
            }
            print(f"  k={k}, pct={pct}: mean={np.mean(sp_vals):.3f}, std={np.std(sp_vals):.3f}, unique={unique}")

    return grid_results


# ============================================================================
# STEP 3: COARSE GRAINING
# ============================================================================

def step3_coarse_graining(n_runs=36):
    """Does SP survive different spatial bin counts?"""
    print("\n" + "=" * 70)
    print("STEP 3: COARSE GRAINING")
    print("=" * 70)

    frictions = np.linspace(0.1, 1.5, 6)
    seeds = [i * 100 + 1000 for i in range(6)]

    bin_counts = [5, 10, 15, 20]
    results = {}

    for n_bins in bin_counts:
        sp_vals = []
        for mu in frictions:
            for seed in seeds:
                y_hist = run_sim(n_grains=50, n_steps=1500, friction=mu, seed=seed)
                # Spatial binning
                bin_edges = np.linspace(0, 10, n_bins + 1)
                binned = np.zeros((n_bins, y_hist.shape[1]))
                for t in range(y_hist.shape[1]):
                    hist, _ = np.histogram(y_hist[:, t], bins=bin_edges)
                    binned[:, t] = hist.astype(float)
                sp, _ = compute_sp(binned, k=5, warmup=100, threshold_percentile=90)
                sp_vals.append(sp)

        unique = np.unique(sp_vals)
        results[f'bins={n_bins}'] = {
            'mean': float(np.mean(sp_vals)),
            'std': float(np.std(sp_vals)),
            'n_unique': len(unique),
            'unique': unique.tolist()
        }
        print(f"  bins={n_bins}: mean={np.mean(sp_vals):.3f}, std={np.std(sp_vals):.3f}, unique={unique}")

    # Check if SP rank ordering is preserved across bin counts
    print("\n--- Rank preservation across bin counts ---")
    all_sp = np.zeros((len(frictions) * len(seeds), len(bin_counts)))
    for j, n_bins in enumerate(bin_counts):
        idx = 0
        for mu in frictions:
            for seed in seeds:
                y_hist = run_sim(n_grains=50, n_steps=1500, friction=mu, seed=seed)
                bin_edges = np.linspace(0, 10, n_bins + 1)
                binned = np.zeros((n_bins, y_hist.shape[1]))
                for t in range(y_hist.shape[1]):
                    hist, _ = np.histogram(y_hist[:, t], bins=bin_edges)
                    binned[:, t] = hist.astype(float)
                sp, _ = compute_sp(binned, k=5, warmup=100, threshold_percentile=90)
                all_sp[idx, j] = sp
                idx += 1

    # Spearman correlation between bin counts
    from scipy.stats import spearmanr
    for i in range(len(bin_counts)):
        for j in range(i + 1, len(bin_counts)):
            r, p = spearmanr(all_sp[:, i], all_sp[:, j])
            print(f"  bins={bin_counts[i]} vs bins={bin_counts[j]}: r={r:.3f}, p={p:.4f}")

    return results


# ============================================================================
# STEP 4: PHYSICAL EVENT MAPPING
# ============================================================================

def step4_physical_events():
    """What physical events correspond to high vs low SP?"""
    print("\n" + "=" * 70)
    print("STEP 4: PHYSICAL EVENT MAPPING")
    print("=" * 70)

    # Run at two extreme frictions to get high and low SP
    frictions = [0.1, 0.5, 1.0, 1.5]
    all_results = []

    for mu in frictions:
        y, x, vx, vy = run_sim(n_grains=50, n_steps=1500, friction=mu,
                                 seed=42, return_trajectories=True)
        sp, surprise_ts = compute_sp(y, k=5, warmup=100, threshold_percentile=90)

        # Compute physical diagnostics
        rms_vel = np.sqrt(np.mean(vx**2 + vy**2))
        msd = np.mean((y[:, 100:] - y[:, :-100]) ** 2)
        packing_var = np.var(np.histogram(y[:, -1], bins=20, range=(0, 10))[0].astype(float))

        all_results.append({
            'friction': mu,
            'sp': sp,
            'rms_vel': float(rms_vel),
            'msd': float(msd),
            'packing_var': float(packing_var),
            'surprise_ts': surprise_ts.tolist() if len(surprise_ts) > 0 else []
        })

        print(f"  μ={mu:.1f}: SP={sp:.1f}, rms_vel={rms_vel:.2f}, msd={msd:.4f}, packing_var={packing_var:.2f}")

    # Map surprise events to physical events
    print("\n--- Surprise event timing ---")
    for r in all_results:
        if len(r['surprise_ts']) == 0:
            continue
        st = np.array(r['surprise_ts'])
        nonzero = st[st > 0]
        if len(nonzero) < 10:
            continue
        threshold = np.percentile(nonzero, 90)
        event_times = np.where(st > threshold)[0] + 100  # offset by warmup

        if len(event_times) > 0:
            # Look at grain positions at surprise events vs non-surprise
            y = run_sim(n_grains=50, n_steps=1500, friction=r['friction'], seed=42)
            print(f"  μ={r['friction']:.1f}: {len(event_times)} surprise events at t={event_times[:5]}...")

            # Are surprise events correlated with collisions?
            # Check if any grains have large position jumps at surprise times
            for t_event in event_times[:3]:
                if t_event + 1 < y.shape[1]:
                    jumps = np.abs(np.diff(y[:, t_event:t_event + 2], axis=1)).flatten()
                    max_jump = np.max(jumps)
                    print(f"    t={t_event}: max grain jump = {max_jump:.4f}")

    return all_results


# ============================================================================
# STEP 5: RECONSTRUCTION TEST
# ============================================================================

def step5_reconstruction(n_runs=72):
    """Can SP be predicted from friction + recovery variables?"""
    print("\n" + "=" * 70)
    print("STEP 5: RECONSTRUCTION TEST")
    print("=" * 70)

    frictions = np.linspace(0.1, 1.5, 12)
    n_reps = 6

    data = []
    for i, mu in enumerate(frictions):
        for r in range(n_reps):
            seed = i * 100 + r + 1000
            y = run_sim(n_grains=50, n_steps=1500, friction=mu, seed=seed)
            sp, _ = compute_sp(y, k=5, warmup=100, threshold_percentile=90)

            # Compute recovery-like variables from this run
            rms_vel = np.sqrt(np.mean(y ** 2))  # simplified
            msd = np.mean((y[:, 100:] - y[:, :-100]) ** 2) if y.shape[1] > 200 else 0

            data.append({
                'friction': mu,
                'sp': sp,
                'rms_vel': float(rms_vel),
                'msd': float(msd),
                'seed': seed
            })

    X = np.array([[d['friction'], d['rms_vel'], d['msd']] for d in data])
    y_sp = np.array([d['sp'] for d in data])

    # Try to predict SP from friction + physical variables
    from scipy.stats import spearmanr

    print("Correlations with SP:")
    for name, col in [('friction', 0), ('rms_vel', 1), ('msd', 2)]:
        r, p = spearmanr(X[:, col], y_sp)
        print(f"  {name}: r={r:.3f}, p={p:.4f}")

    # Multiple regression
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import cross_val_score

        reg = LinearRegression().fit(X, y_sp)
        r2 = reg.score(X, y_sp)
        cv_scores = cross_val_score(reg, X, y_sp, cv=5, scoring='r2')
        print(f"\nRegression: R²={r2:.4f}, CV R²={cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        print(f"  Coefficients: friction={reg.coef_[0]:.4f}, rms_vel={reg.coef_[1]:.4f}, msd={reg.coef_[2]:.4f}")

        if r2 > 0.5:
            print("\n⚠ SP is PREDICTABLE from friction+physical variables → LIKELY COLLAPSE")
        else:
            print(f"\n✓ SP is NOT fully predictable (R²={r2:.4f}) → NOT collapsed")
    except ImportError:
        print("  sklearn not available, using numpy regression")
        # Simple numpy regression
        X_aug = np.column_stack([X, np.ones(len(X))])
        beta = np.linalg.lstsq(X_aug, y_sp, rcond=None)[0]
        y_pred = X_aug @ beta
        ss_res = np.sum((y_sp - y_pred) ** 2)
        ss_tot = np.sum((y_sp - np.mean(y_sp)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        print(f"\nRegression: R²={r2:.4f}")

    return data


# ============================================================================
# STEP 6: DOMAIN TRANSFER
# ============================================================================

def step6_domain_transfer():
    """Does SP appear in non-granular systems?"""
    print("\n" + "=" * 70)
    print("STEP 6: DOMAIN TRANSFER")
    print("=" * 70)

    results = {}

    # --- Coupled Markov ---
    print("\n--- Coupled Markov ---")
    sp_vals = []
    for coupling in [0.0, 0.2, 0.4, 0.6, 0.8]:
        for seed in range(10):
            ts = coupled_markov(n_components=10, n_timepoints=1000,
                                coupling=coupling, noise=0.1, seed=seed)
            sp, _ = compute_sp(ts, k=5, warmup=100, threshold_percentile=90)
            sp_vals.append(sp)
        print(f"  coupling={coupling}: SP={[sp_vals[-10 + i] for i in range(10)]}")
    sp_cm = np.array(sp_vals)
    unique_cm = np.unique(sp_cm)
    results['coupled_markov'] = {
        'values': sp_cm.tolist(),
        'unique': unique_cm.tolist(),
        'n_unique': len(unique_cm)
    }
    print(f"  Unique SP values: {unique_cm}")

    # --- Modular ---
    print("\n--- Modular ---")
    sp_vals = []
    for within in [0.1, 0.3, 0.5, 0.7]:
        for seed in range(10):
            ts = modular(n_per_module=4, n_modules=3, n_timepoints=1000,
                         within=within, between=0.1, noise=0.2, seed=seed)
            sp, _ = compute_sp(ts, k=5, warmup=100, threshold_percentile=90)
            sp_vals.append(sp)
        print(f"  within={within}: SP={[sp_vals[-10 + i] for i in range(10)]}")
    sp_mod = np.array(sp_vals)
    unique_mod = np.unique(sp_mod)
    results['modular'] = {
        'values': sp_mod.tolist(),
        'unique': unique_mod.tolist(),
        'n_unique': len(unique_mod)
    }
    print(f"  Unique SP values: {unique_mod}")

    # --- Hierarchical ---
    print("\n--- Hierarchical ---")
    sp_vals = []
    for micro_c in [0.1, 0.2, 0.4, 0.6]:
        for seed in range(10):
            ts = hierarchical(base_n=8, n_levels=3, n_timepoints=1500,
                              micro_coupling=micro_c, seed=seed)
            sp, _ = compute_sp(ts, k=5, warmup=100, threshold_percentile=90)
            sp_vals.append(sp)
        print(f"  micro_coupling={micro_c}: SP={[sp_vals[-10 + i] for i in range(10)]}")
    sp_hier = np.array(sp_vals)
    unique_hier = np.unique(sp_hier)
    results['hierarchical'] = {
        'values': sp_hier.tolist(),
        'unique': unique_hier.tolist(),
        'n_unique': len(unique_hier)
    }
    print(f"  Unique SP values: {unique_hier}")

    # --- Forest ---
    print("\n--- Forest Succession ---")
    sp_vals = []
    adapter = EcosystemAdapter(n_plots=24, n_species=20, n_years=40, drought_year=5)
    all_plots = adapter.load_all_plots()
    for plot_idx, (data, meta) in enumerate(all_plots):
        sp, _ = compute_sp(data, k=5, warmup=10, threshold_percentile=90)
        sp_vals.append(sp)
    sp_forest = np.array(sp_vals)
    unique_forest = np.unique(sp_forest)
    results['forest'] = {
        'values': sp_forest.tolist(),
        'unique': unique_forest.tolist(),
        'n_unique': len(unique_forest)
    }
    print(f"  Unique SP values: {unique_forest}")
    print(f"  SP per plot: {[f'{s:.1f}' for s in sp_vals]}")

    # --- Sandpile ---
    print("\n--- Sandpile ---")
    sp_vals = []
    for seed in range(5):
        ts = critical(system="sandpile", seed=seed)
        sp, _ = compute_sp(ts, k=5, warmup=20, threshold_percentile=90)
        sp_vals.append(sp)
    sp_sand = np.array(sp_vals)
    unique_sand = np.unique(sp_sand)
    results['sandpile'] = {
        'values': sp_sand.tolist(),
        'unique': unique_sand.tolist(),
        'n_unique': len(unique_sand)
    }
    print(f"  Unique SP values: {unique_sand}")
    print(f"  SP per seed: {[f'{s:.1f}' for s in sp_vals]}")

    # Summary
    print("\n" + "=" * 70)
    print("DOMAIN TRANSFER SUMMARY")
    print("=" * 70)
    for domain, r in results.items():
        print(f"  {domain}: {r['n_unique']} unique values, range=[{min(r['values']):.1f}, {max(r['values']):.1f}]")

    n_domains_with_variation = sum(1 for r in results.values() if r['n_unique'] > 3)
    print(f"\nDomains with SP variation (>3 unique values): {n_domains_with_variation}/5")

    if n_domains_with_variation >= 3:
        print("✓ SP appears across domains — PROMISING")
    elif n_domains_with_variation >= 1:
        print("~ SP appears in some domains — PARTIAL")
    else:
        print("⚠ SP does NOT appear across domains — LIKELY ARTIFACT")

    return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("RD-9E: SURPRISE PERSISTENCE AUDIT")
    print("=" * 70)

    t_start = time.time()

    # Step 1: Continuity
    sp_values, is_continuous = step1_continuity(n_runs=72)

    # Step 2: Estimator sensitivity
    grid_results = step2_estimator_sensitivity(n_runs=36)

    # Step 3: Coarse graining
    cg_results = step3_coarse_graining(n_runs=36)

    # Step 4: Physical events
    phys_results = step4_physical_events()

    # Step 5: Reconstruction
    recon_data = step5_reconstruction(n_runs=72)

    # Step 6: Domain transfer
    domain_results = step6_domain_transfer()

    # Save all results
    output = {
        'step1_continuity': {
            'sp_values': sp_values.tolist(),
            'is_continuous': is_continuous,
            'unique_values': np.unique(sp_values).tolist()
        },
        'step2_estimator': grid_results,
        'step3_coarse_graining': cg_results,
        'step4_physical_events': phys_results,
        'step5_reconstruction': recon_data,
        'step6_domain_transfer': domain_results,
        'elapsed_seconds': time.time() - t_start
    }

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rd9e_audit.json'), 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nTotal time: {time.time() - t_start:.0f}s")
    print("Results saved to audits/rd9e_audit.json")


if __name__ == '__main__':
    main()
