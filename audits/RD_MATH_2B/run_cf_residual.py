#!/usr/bin/env python3
"""RD-MATH.2B: C/F Residual Audit

Step 1: Remove F proxies referencing C
Step 2: Fit F = αC + β, compute Residual_F
Step 3: Test whether Residual_F predicts future novelty, stability, adaptation, persistence
"""

import numpy as np
import sys, time, json
sys.path.insert(0, "coherence-benchmark")
from metrics import compute_C, compute_predictive_information, compute_transfer_entropy_matrix
from adapters.granular import _soft_sphere_force
from scipy.stats import linregress

RNG = np.random.default_rng(42)

# Granular simulation
def _granular_run(n_grains=50, n_steps=1000, removal_step=500, removal_fraction=0.1,
                  friction=0.3, seed=42):
    rng = np.random.default_rng(seed)
    radii = rng.uniform(0.8, 1.5, n_grains)
    masses = radii ** 2
    box_width = 40.0

    x = rng.uniform(2, box_width - 2, n_grains)
    y = rng.uniform(5, 30, n_grains)
    vx = rng.uniform(-0.5, 0.5, n_grains)
    vy = np.maximum(-0.5, np.minimum(0.5, rng.uniform(-0.5, 0.5, n_grains)))

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

# Compute F proxies (NO Recovery proxy)
def compute_F_proxies_clean(X):
    """Compute F as 3 proxies: TE, Empowerment, Novelty Rate. NO Recovery (references C)."""
    
    # TE proxy: mean transfer entropy
    te_matrix = compute_transfer_entropy_matrix(X, tau=1, k=1)
    F_TE = np.mean(te_matrix)
    
    # Empowerment proxy: predictive information
    I_pred = compute_predictive_information(X, tau=1, k=1)
    F_E = I_pred
    
    # Novelty rate proxy: entropy rate
    H = compute_C_local(X, estimator="gaussian")
    F_NR = max(0, H)
    
    return {
        "F_TE": float(F_TE),
        "F_E": float(F_E),
        "F_NR": float(F_NR),
        "F_clean": float((F_TE + F_E + F_NR) / 3)
    }

# Compute outcome variables
def compute_outcomes(X):
    """Compute future novelty, stability, adaptation, persistence."""
    
    # Split at removal step (step 500, so index 500)
    pre = X[:, :500]
    post = X[:, 500:]
    
    # Future novelty: entropy change after perturbation
    pre_C = compute_C_local(pre, estimator="gaussian")
    post_C = compute_C_local(post, estimator="gaussian")
    novelty = post_C - pre_C  # positive = increased structure
    
    # Stability: variance of C in post-perturbation window
    # (sliding window over post period)
    window = 100
    c_values = []
    for i in range(0, post.shape[1] - window, 25):
        c_values.append(compute_C_local(post[:, i:i+window], estimator="gaussian"))
    stability = -np.std(c_values)  # negative because lower variance = more stable
    
    # Adaptation: how quickly C recovers after perturbation
    # (ratio of post-C to pre-C)
    adaptation = post_C / max(pre_C, 1e-10)
    
    # Persistence: structure retention
    persistence = min(post_C, pre_C) / max(post_C, pre_C, 1e-10)
    
    return {
        "novelty": float(novelty),
        "stability": float(stability),
        "adaptation": float(adaptation),
        "persistence": float(persistence)
    }

# Run experiments
print("=== RD-MATH.2B: C/F Residual Audit ===")
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
        
        # Compute F proxies (clean, no Recovery)
        t0 = time.time()
        F = compute_F_proxies_clean(X)
        t_F = time.time() - t0
        
        # Compute outcomes
        t0 = time.time()
        outcomes = compute_outcomes(X)
        t_out = time.time() - t0
        
        result = {
            "friction": friction,
            "replicate": rep,
            "C": float(C),
            **F,
            **outcomes
        }
        results.append(result)
        
        print(f"C={C:.4f}, F_clean={F['F_clean']:.4f}, novelty={outcomes['novelty']:.4f} ({t_sim:.1f}s)")

# Fit regression
print()
print("=== REGRESSION: F_clean = αC + β ===")

C_values = np.array([r["C"] for r in results])
F_values = np.array([r["F_clean"] for r in results])

slope, intercept, r_value, p_value, std_err = linregress(C_values, F_values)
print(f"α (slope): {slope:.4f}")
print(f"β (intercept): {intercept:.4f}")
print(f"R²: {r_value**2:.4f}")
print(f"p-value: {p_value:.4e}")
print()

# Compute residuals
residuals = F_values - (slope * C_values + intercept)
print(f"Residual_F: mean={np.mean(residuals):.4f}, std={np.std(residuals):.4f}")
print()

# Test whether residuals predict outcomes
print("=== RESIDUAL PREDICTION ===")
print()

outcome_names = ["novelty", "stability", "adaptation", "persistence"]
for outcome in outcome_names:
    outcome_values = np.array([r[outcome] for r in results])
    
    # Correlation between residual and outcome
    corr = np.corrcoef(residuals, outcome_values)[0, 1]
    
    # Does residual predict outcome?
    slope_o, intercept_o, r_o, p_o, std_o = linregress(residuals, outcome_values)
    
    print(f"Residual_F → {outcome}:")
    print(f"  Correlation: {corr:.4f}")
    print(f"  R²: {r_o**2:.4f}")
    print(f"  p-value: {p_o:.4e}")
    print()

# Also test whether C alone predicts outcomes
print("=== C PREDICTION (baseline) ===")
print()

for outcome in outcome_names:
    outcome_values = np.array([r[outcome] for r in results])
    slope_c, intercept_c, r_c, p_c, std_c = linregress(C_values, outcome_values)
    print(f"C → {outcome}: R²={r_c**2:.4f}, p={p_c:.4e}")

print()

# Also test whether F_clean alone predicts outcomes
print("=== F_clean PREDICTION (baseline) ===")
print()

for outcome in outcome_names:
    outcome_values = np.array([r[outcome] for r in results])
    slope_f, intercept_f, r_f, p_f, std_f = linregress(F_values, outcome_values)
    print(f"F_clean → {outcome}: R²={r_f**2:.4f}, p={p_f:.4e}")

print()

# Interpretation
print("=== INTERPRETATION ===")
print()

# Check if residual predicts anything
max_residual_r2 = 0
best_outcome = None
for outcome in outcome_names:
    outcome_values = np.array([r[outcome] for r in results])
    slope_o, intercept_o, r_o, p_o, std_o = linregress(residuals, outcome_values)
    if r_o**2 > max_residual_r2:
        max_residual_r2 = r_o**2
        best_outcome = outcome

print(f"Best residual prediction: {best_outcome} (R²={max_residual_r2:.4f})")
print()

if max_residual_r2 < 0.1:
    print("INTERPRETATION: Residual_F ≈ 0 predictive power.")
    print("→ F largely reducible to C under current metrics.")
    print("→ F may not add independent information beyond C.")
elif max_residual_r2 < 0.3:
    print("INTERPRETATION: Residual_F has weak predictive power.")
    print("→ F contains some independent information, but weak.")
    print("→ Partial independence, not full independence.")
else:
    print("INTERPRETATION: Residual_F has strong predictive power.")
    print("→ F contains information not present in C.")
    print("→ F is not reducible to C.")

# Also test with F_TE and F_E only (without F_NR which IS C)
print("=== F_MINIMAL = (TE + Empowerment) / 2 (no entropy proxy) ===")
print()

F_minimal = np.array([(r["F_TE"] + r["F_E"]) / 2 for r in results])

slope_m, intercept_m, r_m, p_m, std_m = linregress(C_values, F_minimal)
print(f"F_minimal = αC + β: α={slope_m:.4f}, β={intercept_m:.4f}, R²={r_m**2:.4f}, p={p_m:.4e}")

residuals_m = F_minimal - (slope_m * C_values + intercept_m)
print(f"Residual_minimal: mean={np.mean(residuals_m):.6f}, std={np.std(residuals_m):.6f}")
print()

for outcome in outcome_names:
    outcome_values = np.array([r[outcome] for r in results])
    corr_m = np.corrcoef(residuals_m, outcome_values)[0, 1]
    print(f"Residual_minimal → {outcome}: R²={corr_m**2:.4f}, p={linregress(residuals_m, outcome_values)[3]:.4e}")

print()

# Save results
with open("audits/RD_MATH_2B/cf_residual_results.json", "w") as f:
    json.dump({
        "results": results,
        "regression": {
            "alpha": float(slope),
            "beta": float(intercept),
            "R2": float(r_value**2),
            "p_value": float(p_value)
        },
        "residuals": {
            "mean": float(np.mean(residuals)),
            "std": float(np.std(residuals))
        },
        "prediction": {
            "residual_to_outcome": {
                outcome: {
                    "correlation": float(np.corrcoef(residuals, np.array([r[outcome] for r in results]))[0, 1]),
                    "R2": float(linregress(residuals, np.array([r[outcome] for r in results]))[2]**2),
                    "p_value": float(linregress(residuals, np.array([r[outcome] for r in results]))[3])
                } for outcome in outcome_names
            },
            "C_to_outcome": {
                outcome: {
                    "R2": float(linregress(C_values, np.array([r[outcome] for r in results]))[2]**2),
                    "p_value": float(linregress(C_values, np.array([r[outcome] for r in results]))[3])
                } for outcome in outcome_names
            },
            "F_to_outcome": {
                outcome: {
                    "R2": float(linregress(F_values, np.array([r[outcome] for r in results]))[2]**2),
                    "p_value": float(linregress(F_values, np.array([r[outcome] for r in results]))[3])
                } for outcome in outcome_names
            }
        },
        "interpretation": {
            "best_residual_prediction": best_outcome,
            "best_R2": float(max_residual_r2),
            "reducible": bool(max_residual_r2 < 0.1)
        }
    }, f, indent=2)
