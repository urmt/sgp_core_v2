#!/usr/bin/env python3
"""RD-MATH.2B.R1: Metric Sensitivity Audit

Generate obviously distinct dynamical regimes and test whether metrics vary.
"""

import numpy as np
import sys, time, json
sys.path.insert(0, "coherence-benchmark")
from metrics import compute_C, compute_predictive_information, compute_transfer_entropy_matrix

# === DYNAMICAL REGIMES ===

def make_ordered_lattice(n_grains=50, n_steps=1000):
    """Ordered lattice: particles on grid, minimal motion."""
    rng = np.random.default_rng(42)
    n_side = int(np.sqrt(n_grains))
    x = np.linspace(5, 35, n_side)
    y = np.linspace(5, 25, n_side)
    xx, yy = np.meshgrid(x, y)
    positions_x = np.zeros((n_grains, n_steps))
    positions_y = np.zeros((n_grains, n_steps))
    
    idx = 0
    for i in range(n_side):
        for j in range(n_side):
            if idx < n_grains:
                positions_x[idx, :] = xx[i, j]
                positions_y[idx, :] = yy[i, j] + 0.01 * np.sin(np.linspace(0, 4*np.pi, n_steps))
                idx += 1
    
    return positions_y, positions_x

def make_random_gas(n_grains=50, n_steps=1000):
    """Random gas: particles move randomly, no interactions."""
    rng = np.random.default_rng(42)
    positions_x = rng.uniform(5, 35, (n_grains, n_steps))
    positions_y = rng.uniform(5, 25, (n_grains, n_steps))
    return positions_y, positions_x

def make_clustered_aggregate(n_grains=50, n_steps=1000):
    """Clustered aggregate: particles cluster in center with noise."""
    rng = np.random.default_rng(42)
    cluster_x = rng.normal(20, 3, (n_grains, n_steps))
    cluster_y = rng.normal(15, 2, (n_grains, n_steps))
    noise_x = rng.normal(0, 0.1, (n_grains, n_steps))
    noise_y = rng.normal(0, 0.1, (n_grains, n_steps))
    positions_x = cluster_x + noise_x
    positions_y = cluster_y + noise_y
    return positions_y, positions_x

def make_oscillatory(n_grains=50, n_steps=1000):
    """Oscillatory forcing: particles oscillate in place."""
    rng = np.random.default_rng(42)
    base_x = rng.uniform(5, 35, n_grains)
    base_y = rng.uniform(5, 25, n_grains)
    freq = rng.uniform(0.5, 2.0, n_grains)
    amp = rng.uniform(0.5, 2.0, n_grains)
    
    t = np.linspace(0, 4*np.pi, n_steps)
    positions_x = np.zeros((n_grains, n_steps))
    positions_y = np.zeros((n_grains, n_steps))
    
    for i in range(n_grains):
        positions_x[i, :] = base_x[i] + amp[i] * np.sin(freq[i] * t)
        positions_y[i, :] = base_y[i] + amp[i] * np.cos(freq[i] * t)
    
    return positions_y, positions_x

def make_frozen(n_grains=50, n_steps=1000):
    """Frozen solid: particles completely static."""
    rng = np.random.default_rng(42)
    positions_x = rng.uniform(5, 35, (n_grains, 1))
    positions_y = rng.uniform(5, 25, (n_grains, 1))
    positions_x = np.tile(positions_x, (1, n_steps))
    positions_y = np.tile(positions_y, (1, n_steps))
    return positions_y, positions_x

# === BINNING ===

def bin_data(positions_y, positions_x, n_bins=10):
    nan_mask = np.isnan(positions_y)
    col_means = np.nanmean(positions_y, axis=1, keepdims=True)
    positions_y = np.where(nan_mask, col_means, positions_y)
    with np.errstate(invalid="ignore"):
        final_x = np.nanmean(positions_x[:, -100:], axis=1)
    final_x = np.where(np.isnan(final_x), np.nanmean(positions_x[:, :500], axis=1), final_x)
    order = np.argsort(final_x)
    bins = np.array_split(order, n_bins)
    return np.array([np.mean(positions_y[b], axis=0) for b in bins])

# === MAIN ===

print("=== RD-MATH.2B.R1: Metric Sensitivity Audit ===")
print()

regimes = [
    ("ordered_lattice", make_ordered_lattice),
    ("random_gas", make_random_gas),
    ("clustered_aggregate", make_clustered_aggregate),
    ("oscillatory", make_oscillatory),
    ("frozen", make_frozen),
]

results = []

for name, func in regimes:
    print(f"Generating {name}...", end=" ", flush=True)
    t0 = time.time()
    positions_y, positions_x = func()
    t_gen = time.time() - t0
    
    X = bin_data(positions_y, positions_x)
    print(f"({t_gen:.2f}s)")
    
    # Compute metrics
    t0 = time.time()
    C = compute_C(X, estimator="gaussian")
    t_C = time.time() - t0
    
    t0 = time.time()
    te_matrix = compute_transfer_entropy_matrix(X, tau=1, k=1)
    TE = np.mean(te_matrix)
    t_TE = time.time() - t0
    
    t0 = time.time()
    I_pred = compute_predictive_information(X, tau=1, k=1)
    Emp = I_pred
    t_Emp = time.time() - t0
    
    t0 = time.time()
    NR = max(0, C)
    t_NR = time.time() - t0
    
    result = {
        "regime": name,
        "C": float(C),
        "TE": float(TE),
        "Empowerment": float(Emp),
        "Novelty_Rate": float(NR),
        "time_gen": float(t_gen),
        "time_C": float(t_C),
        "time_TE": float(t_TE),
        "time_Emp": float(t_Emp),
    }
    results.append(result)
    
    print(f"  C={C:.4f}, TE={TE:.6f}, Emp={Emp:.4f}, NR={NR:.4f}")

print()
print("=== SENSITIVITY ANALYSIS ===")
print()

metrics = ["C", "TE", "Empowerment", "Novelty_Rate"]
for m in metrics:
    values = [r[m] for r in results]
    mean_val = np.mean(values)
    std_val = np.std(values)
    cv = std_val / max(abs(mean_val), 1e-10)
    print(f"{m}: mean={mean_val:.6f}, std={std_val:.6f}, CV={cv:.4f}")

print()
print("=== INTER-REGIME COMPARISON ===")
print()

for m in metrics:
    values = [r[m] for r in results]
    print(f"{m}:")
    for i, r in enumerate(results):
        print(f"  {r['regime']}: {r[m]:.6f}")
    print()

# Save results
with open("audits/RD_MATH_2B_R1/metric_sensitivity_results.json", "w") as f:
    json.dump({
        "results": results,
        "metrics": {
            m: {
                "mean": float(np.mean([r[m] for r in results])),
                "std": float(np.std([r[m] for r in results])),
                "cv": float(np.std([r[m] for r in results]) / max(abs(np.mean([r[m] for r in results])), 1e-10))
            } for m in metrics
        }
    }, f, indent=2)

print("=== VERDICT ===")
print()

sensitive = []
insensitive = []
for m in metrics:
    values = [r[m] for r in results]
    cv = np.std(values) / max(abs(np.mean(values)), 1e-10)
    if cv > 0.1:
        sensitive.append(m)
    else:
        insensitive.append(m)

print(f"Sensitive metrics (CV > 0.1): {sensitive}")
print(f"Insensitive metrics (CV ≤ 0.1): {insensitive}")
