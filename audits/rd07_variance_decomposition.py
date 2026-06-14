"""RD-7: Variance Decomposition
Cross-metric analysis: How much of C is genuinely novel information?

Uses:
1. t901 ensemble (60 granular runs) — within-system variance decomposition
2. benchmark_v1 (8 systems) — cross-system variance decomposition

Metrics: C, I_pred, C_sigma, MSE
Targets: dip, restoration, tau_rec (recovery outcomes)
"""

import sys, os, json
import numpy as np
from scipy import stats
from itertools import combinations

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, "coherence-benchmark")

# ─── Load data ───
with open("coherence-benchmark/results/t901_ensemble.json") as f:
    t901 = json.load(f)

with open("coherence-benchmark/results/benchmark_v1.json") as f:
    bench = json.load(f)

# ─── Extract t901 arrays ───
metrics = ["pre_C", "pre_I_pred", "pre_C_sigma", "pre_MSE_s1"]
metric_labels = ["C", "I_pred", "C_σ", "MSE"]
targets = ["dip", "restoration", "tau_rec"]
target_labels = ["ΔC (dip)", "Restoration", "τ_rec"]

X_t901 = np.column_stack([np.array([r[m] for r in t901]) for m in metrics])
Y_t901 = {t: np.array([r[t] for r in t901]) for t in targets}
friction = np.array([r["friction"] for r in t901])

# ─── Extract benchmark arrays ───
sys_names = list(bench.keys())

def extract_metric(sys_data, key):
    """Extract mean value from benchmark metric (handles dict with 'mean' or raw value)."""
    v = sys_data[key]
    if isinstance(v, dict):
        if "mean" in v:
            return v["mean"]
        # MSE: dict of scale → value, take scale 1
        if "1" in v:
            return v["1"]
        return list(v.values())[0]
    return float(v)

X_bench = np.column_stack([
    np.array([extract_metric(bench[s], "C") for s in sys_names]),
    np.array([extract_metric(bench[s], "predictive_information") for s in sys_names]),
    np.array([extract_metric(bench[s], "statistical_complexity") for s in sys_names]),
    np.array([extract_metric(bench[s], "mse") for s in sys_names]),
])

print("=" * 80)
print("RD-7: VARIANCE DECOMPOSITION")
print("=" * 80)

# ═══════════════════════════════════════════════════════════════
# PART 1: Cross-metric correlation analysis
# ═══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("PART 1: CROSS-METRIC CORRELATIONS")
print("─" * 80)

# t901 correlations
print("\n── t901 Ensemble (n=60) ──")
print(f"\n{'':>12s}", end="")
for ml in metric_labels:
    print(f"{ml:>10s}", end="")
print()

corr_t901 = np.corrcoef(X_t901.T)
for i, ml in enumerate(metric_labels):
    print(f"{ml:>12s}", end="")
    for j in range(len(metric_labels)):
        r = corr_t901[i, j]
        sig = ""
        if i != j:
            _, p = stats.pearsonr(X_t901[:, i], X_t901[:, j])
            if p < 0.001: sig = "***"
            elif p < 0.01: sig = "**"
            elif p < 0.05: sig = "*"
        print(f"{r:>9.3f}{sig}", end="")
    print()

# Benchmark correlations
print("\n── Benchmark Systems (n=8) ──")
print(f"\n{'':>12s}", end="")
for ml in metric_labels:
    print(f"{ml:>10s}", end="")
print()

corr_bench = np.corrcoef(X_bench.T)
for i, ml in enumerate(metric_labels):
    print(f"{ml:>12s}", end="")
    for j in range(len(metric_labels)):
        r = corr_bench[i, j]
        print(f"{r:>10.3f}", end="")
    print()

# ═══════════════════════════════════════════════════════════════
# PART 2: Metric → Target correlations
# ═══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("PART 2: METRIC → RECOVERY PREDICTION (t901, n=60)")
print("─" * 80)

print(f"\n{'Metric':>12s}", end="")
for tl in target_labels:
    print(f"{tl:>14s}", end="")
print("  (Pearson r, * p<.05 ** p<.01 ***)")

for i, ml in enumerate(metric_labels):
    print(f"{ml:>12s}", end="")
    for t in targets:
        r, p = stats.pearsonr(X_t901[:, i], Y_t901[t])
        sig = ""
        if p < 0.001: sig = "***"
        elif p < 0.01: sig = "**"
        elif p < 0.05: sig = "*"
        print(f"{r:>10.3f}{sig:>4s}", end="")
    print()

# ═══════════════════════════════════════════════════════════════
# PART 3: Multiple regression & partial R²
# ═══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("PART 3: MULTIPLE REGRESSION & PARTIAL R² (t901, n=60)")
print("─" * 80)

def ols_fit(X, y):
    """OLS regression, returns coefficients, R², residuals."""
    n, p = X.shape
    X_aug = np.column_stack([np.ones(n), X])
    # pseudoinverse for numerical stability
    beta = np.linalg.lstsq(X_aug, y, rcond=None)[0]
    y_hat = X_aug @ beta
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return beta, r2, y - y_hat

def partial_r2_full_vs_reduced(X_full, X_reduced, y):
    """Partial R² when adding variables in X_full vs X_reduced."""
    _, r2_full, _ = ols_fit(X_full, y)
    _, r2_reduced, _ = ols_fit(X_reduced, y)
    if (1 - r2_reduced) <= 0:
        return 0.0
    return (r2_full - r2_reduced) / (1 - r2_reduced)

for ti, t in enumerate(targets):
    y = Y_t901[t]
    print(f"\n── Target: {target_labels[ti]} ──")

    # Full model: all 4 metrics
    beta_full, r2_full, _ = ols_fit(X_t901, y)
    print(f"  Full model R² = {r2_full:.4f}")

    # Unique contribution of each metric (partial R²)
    print(f"\n  {'Metric':>12s} {'Unique R²':>10s} {'% of R²':>10s} {'Partial r':>10s}")
    print(f"  {'-'*45}")

    unique_r2 = []
    for i in range(4):
        # Full model minus metric i
        mask = [j for j in range(4) if j != i]
        X_reduced = X_t901[:, mask]
        pr2 = partial_r2_full_vs_reduced(X_t901, X_reduced, y)
        unique_r2.append(pr2)

        # Partial correlation of metric i with target, controlling for others
        _, res_full, _ = ols_fit(X_reduced, y)
        _, res_metric, _ = ols_fit(X_reduced, X_t901[:, i])
        if np.std(res_full) > 0 and np.std(res_metric) > 0:
            partial_r, _ = stats.pearsonr(res_full, res_metric)
        else:
            partial_r = 0

        pct = (pr2 / r2_full * 100) if r2_full > 0 else 0
        print(f"  {metric_labels[i]:>12s} {pr2:>10.4f} {pct:>9.1f}% {partial_r:>10.3f}")

    # Shared variance
    # Compute shared R² by subtracting unique from total
    # Use approach: R²_shared = R²_total - sum(unique)
    # But this can be negative due to suppression; use adjusted
    total_unique = sum(max(u, 0) for u in unique_r2)
    shared_r2 = max(0, r2_full - total_unique)
    unexplained = max(0, 1 - r2_full)

    print(f"\n  Variance decomposition of {target_labels[ti]}:")
    print(f"    Total R²:              {r2_full:.4f} ({r2_full*100:.1f}%)")
    print(f"    Sum of unique:         {total_unique:.4f} ({total_unique*100:.1f}%)")
    print(f"    Shared (multicollin.): {shared_r2:.4f} ({shared_r2*100:.1f}%)")
    print(f"    Unexplained:           {unexplained:.4f} ({unexplained*100:.1f}%)")

# ═══════════════════════════════════════════════════════════════
# PART 4: Pairwise model comparison (C vs competitors)
# ═══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("PART 4: C ALONE vs C + COMPETITORS (t901, n=60)")
print("─" * 80)

for ti, t in enumerate(targets):
    y = Y_t901[t]
    print(f"\n── Target: {target_labels[ti]} ──")

    # C alone
    _, r2_c, _ = ols_fit(X_t901[:, [0]], y)
    # I_pred alone
    _, r2_i, _ = ols_fit(X_t901[:, [1]], y)
    # C_sigma alone
    _, r2_cs, _ = ols_fit(X_t901[:, [2]], y)
    # MSE alone
    _, r2_mse, _ = ols_fit(X_t901[:, [3]], y)

    print(f"  C alone:          R² = {r2_c:.4f}")
    print(f"  I_pred alone:     R² = {r2_i:.4f}")
    print(f"  C_σ alone:        R² = {r2_cs:.4f}")
    print(f"  MSE alone:        R² = {r2_mse:.4f}")

    # C + I_pred
    _, r2_ci, _ = ols_fit(X_t901[:, [0, 1]], y)
    # C + C_sigma
    _, r2_ccs, _ = ols_fit(X_t901[:, [0, 2]], y)
    # C + MSE
    _, r2_cm, _ = ols_fit(X_t901[:, [0, 3]], y)
    # All 4
    _, r2_all, _ = ols_fit(X_t901, y)

    print(f"  C + I_pred:       R² = {r2_ci:.4f}  (Δ from C alone: {r2_ci-r2_c:+.4f})")
    print(f"  C + C_σ:          R² = {r2_ccs:.4f}  (Δ from C alone: {r2_ccs-r2_c:+.4f})")
    print(f"  C + MSE:          R² = {r2_cm:.4f}  (Δ from C alone: {r2_cm-r2_c:+.4f})")
    print(f"  All 4 metrics:    R² = {r2_all:.4f}  (Δ from C alone: {r2_all-r2_c:+.4f})")

# ═══════════════════════════════════════════════════════════════
# PART 5: Synergy analysis
# ═══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("PART 5: SYNERGY ANALYSIS (t901, n=60)")
print("─" * 80)

print("\n── Pairwise synergy (does adding B to A improve prediction?) ──\n")
print(f"{'Base':>12s} {'+ Added':>12s} {'R²_base':>10s} {'R²_comb':>10s} {'ΔR²':>10s} {'Synergy?':>10s}")

for ti, t in enumerate(targets):
    y = Y_t901[t]
    for i, j in combinations(range(4), 2):
        _, r2_i, _ = ols_fit(X_t901[:, [i]], y)
        _, r2_j, _ = ols_fit(X_t901[:, [j]], y)
        _, r2_ij, _ = ols_fit(X_t901[:, [i, j]], y)

        # Synergy = R²_ij - max(R²_i, R²_j)
        # If positive, the combination is better than either alone
        synergy = r2_ij - max(r2_i, r2_j)

        if ti == 0:  # only print for first target to avoid repetition
            syn_label = "YES" if synergy > 0.005 else "no"
            print(f"{metric_labels[i]:>12s} + {metric_labels[j]:<8s} {r2_i:>10.4f} {r2_ij:>10.4f} {synergy:>+10.4f} {syn_label:>10s}")
    if ti == 0:
        print()

# ═══════════════════════════════════════════════════════════════
# PART 6: Novelty score for C
# ═══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("PART 6: C NOVELTY SCORE")
print("─" * 80)

# Novelty = unique R² of C / total R²
# For each target, what % of explained variance is uniquely C's?
for ti, t in enumerate(targets):
    y = Y_t901[t]
    _, r2_full, _ = ols_fit(X_t901, y)

    # C unique
    pr2_c = partial_r2_full_vs_reduced(X_t901, X_t901[:, [1, 2, 3]], y)
    # I_pred unique
    pr2_i = partial_r2_full_vs_reduced(X_t901, X_t901[:, [0, 2, 3]], y)
    # C_sigma unique
    pr2_cs = partial_r2_full_vs_reduced(X_t901, X_t901[:, [0, 1, 3]], y)
    # MSE unique
    pr2_m = partial_r2_full_vs_reduced(X_t901, X_t901[:, [0, 1, 2]], y)

    novelty_c = pr2_c / r2_full if r2_full > 0 else 0
    novelty_i = pr2_i / r2_full if r2_full > 0 else 0
    novelty_cs = pr2_cs / r2_full if r2_full > 0 else 0
    novelty_m = pr2_m / r2_full if r2_full > 0 else 0

    print(f"\n  {target_labels[ti]}:")
    print(f"    C unique R²:     {pr2_c:.4f}  ({novelty_c*100:.1f}% of explained variance)")
    print(f"    I_pred unique:   {pr2_i:.4f}  ({novelty_i*100:.1f}% of explained variance)")
    print(f"    C_σ unique:      {pr2_cs:.4f}  ({novelty_cs*100:.1f}% of explained variance)")
    print(f"    MSE unique:      {pr2_m:.4f}  ({novelty_m*100:.1f}% of explained variance)")

# ═══════════════════════════════════════════════════════════════
# PART 7: Adding friction as control variable
# ═══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("PART 7: CONTROLLING FOR FRICTION (t901, n=60)")
print("─" * 80)

X_with_friction = np.column_stack([X_t901, friction.reshape(-1, 1)])
labels_with_f = metric_labels + ["friction"]

for ti, t in enumerate(targets):
    y = Y_t901[t]
    print(f"\n── Target: {target_labels[ti]} ──")

    # Full model: 4 metrics + friction
    beta_f, r2_f, _ = ols_fit(X_with_friction, y)
    print(f"  Full model (4 metrics + friction): R² = {r2_f:.4f}")

    # Without friction
    _, r2_nof, _ = ols_fit(X_t901, y)
    print(f"  Without friction:                   R² = {r2_nof:.4f}")
    print(f"  Friction contribution:              ΔR² = {r2_f - r2_nof:.4f} ({(r2_f-r2_nof)/r2_f*100:.1f}% of total)" if r2_f > 0 else "")

    # Partial R² of C controlling for friction + other metrics
    pr2_c_ctrl = partial_r2_full_vs_reduced(
        X_with_friction,
        np.column_stack([X_t901[:, [1, 2, 3]], friction.reshape(-1, 1)]),
        y
    )
    print(f"  C unique (controlling for friction + others): R² = {pr2_c_ctrl:.4f}")

# ═══════════════════════════════════════════════════════════════
# SAVE RESULTS
# ═══════════════════════════════════════════════════════════════
results = {
    "t901_n": len(t901),
    "bench_n": len(sys_names),
    "metrics": metric_labels,
    "targets": target_labels,
    "correlations_t901": corr_t901.tolist(),
    "correlations_bench": corr_bench.tolist(),
}

# Compute partial R² for each target
for ti, t in enumerate(targets):
    y = Y_t901[t]
    _, r2_full, _ = ols_fit(X_t901, y)
    unique = []
    for i in range(4):
        mask = [j for j in range(4) if j != i]
        pr2 = partial_r2_full_vs_reduced(X_t901, X_t901[:, mask], y)
        unique.append(pr2)
    results[f"partial_r2_{t}"] = {
        "r2_full": round(r2_full, 4),
        "unique": {metric_labels[i]: round(unique[i], 4) for i in range(4)},
        "shared": round(max(0, r2_full - sum(max(u, 0) for u in unique)), 4),
        "unexplained": round(max(0, 1 - r2_full), 4),
    }

with open("audits/rd07_variance_decomposition.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved: audits/rd07_variance_decomposition.json")
