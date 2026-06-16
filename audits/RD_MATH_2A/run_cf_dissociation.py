#!/usr/bin/env python3
"""RD-MATH.2A: C/F Dissociation Audit

Tests whether C and F are independent dimensions by checking if all four
quadrants (high C/low F, low C/high F, high C/high F, low C/low F) exist.
"""

import numpy as np
import sys, time, json
sys.path.insert(0, "coherence-benchmark")
from metrics import compute_C, compute_predictive_information, compute_transfer_entropy_matrix
from adapters.granular import _soft_sphere_force

RNG = np.random.default_rng(42)

# Granular simulation (from t901_analysis.py)
def _granular_run(n_grains=50, n_steps=1000, removal_step=500, removal_fraction=0.1,
                  friction=0.3, seed=42):
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

    return all_y, all_x, radii, removed

# Binning
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

# Compute C
def compute_C_local(X, estimator="gaussian"):
    return compute_C(X, estimator=estimator)

# Compute F proxies
def compute_F_proxies(X, friction_levels):
    """Compute F as 4 proxies: TE, Empowerment, Novelty Rate, Recovery."""
    
    # TE proxy: mean transfer entropy
    te_matrix = compute_transfer_entropy_matrix(X, tau=1, k=1)
    F_TE = np.mean(te_matrix)
    
    # Empowerment proxy: predictive information
    I_pred = compute_predictive_information(X, tau=1, k=1)
    F_E = I_pred
    
    # Novelty rate proxy: entropy rate
    H = compute_C(X, estimator="gaussian")
    F_NR = max(0, H)  # Entropy as novelty proxy
    
    # Recovery proxy: stability after perturbation
    pre_C = compute_C_local(X[:, :500], estimator="gaussian")
    post_C = compute_C_local(X[:, 500:], estimator="gaussian")
    F_REC = post_C / max(pre_C, 1e-10)
    
    return {
        "F_TE": float(F_TE),
        "F_E": float(F_E),
        "F_NR": float(F_NR),
        "F_REC": float(F_REC),
        "F_composite": float((F_TE + F_E + F_NR + F_REC) / 4)
    }

# Run experiments
print("=== RD-MATH.2A: C/F Dissociation Audit ===")
print()

friction_levels = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8]
n_replicates = 5
results = []

for friction in friction_levels:
    for rep in range(n_replicates):
        seed = int(friction * 1000 + rep)
        print(f"Running friction={friction}, rep={rep}...", end=" ", flush=True)
        
        t0 = time.time()
        all_y, all_x, radii, removed = _granular_run(friction=friction, seed=seed)
        t_sim = time.time() - t0
        
        # Bin data
        X = _bin_data(all_y, all_x, n_bins=10)
        
        # Compute C
        t0 = time.time()
        C = compute_C_local(X, estimator="gaussian")
        t_C = time.time() - t0
        
        # Compute F proxies
        t0 = time.time()
        F = compute_F_proxies(X, friction_levels)
        t_F = time.time() - t0
        
        result = {
            "friction": friction,
            "replicate": rep,
            "C": float(C),
            **F
        }
        results.append(result)
        
        print(f"C={C:.4f}, F_comp={F['F_composite']:.4f} ({t_sim:.1f}s sim, {t_C:.1f}s C, {t_F:.1f}s F)")

# Analyze quadrants
print()
print("=== QUADRANT ANALYSIS ===")

C_values = [r["C"] for r in results]
F_values = [r["F_composite"] for r in results]

C_median = np.median(C_values)
F_median = np.median(F_values)

print(f"C median: {C_median:.4f}")
print(f"F median: {F_median:.4f}")
print()

# Classify quadrants
quadrants = {"high_C_high_F": [], "high_C_low_F": [], "low_C_high_F": [], "low_C_low_F": []}
for r in results:
    high_C = r["C"] >= C_median
    high_F = r["F_composite"] >= F_median
    
    if high_C and high_F:
        quadrants["high_C_high_F"].append(r)
    elif high_C and not high_F:
        quadrants["high_C_low_F"].append(r)
    elif not high_C and high_F:
        quadrants["low_C_high_F"].append(r)
    else:
        quadrants["low_C_low_F"].append(r)

for q_name, q_results in quadrants.items():
    print(f"{q_name}: {len(q_results)} systems")
    if q_results:
        C_vals = [r["C"] for r in q_results]
        F_vals = [r["F_composite"] for r in q_results]
        print(f"  C range: [{min(C_vals):.4f}, {max(C_vals):.4f}]")
        print(f"  F range: [{min(F_vals):.4f}, {max(F_vals):.4f}]")

# Check if all four quadrants exist
all_exist = all(len(q) > 0 for q in quadrants.values())
print()
if all_exist:
    print("RESULT: All four quadrants exist. C and F appear to be independent dimensions.")
else:
    missing = [q for q, r in quadrants.items() if len(r) == 0]
    print(f"RESULT: Missing quadrants: {missing}. C and F may not be independent.")

# Correlation
corr = np.corrcoef(C_values, F_values)[0, 1]
print(f"C-F correlation: {corr:.4f}")

# Save results
with open("audits/RD_MATH_2A/cf_dissociation_results.json", "w") as f:
    json.dump({
        "results": results,
        "quadrants": {k: len(v) for k, v in quadrants.items()},
        "C_median": float(C_median),
        "F_median": float(F_median),
        "correlation": float(corr),
        "all_exist": all_exist
    }, f, indent=2)
