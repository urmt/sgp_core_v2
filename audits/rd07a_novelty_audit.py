"""RD-7A: Cross-Domain Novelty Audit
Can C be reconstructed from I_pred, C_σ, MSE, TE?

Tests:
1. Cross-domain: 8 benchmark systems (S1-S6 + P1 + P2)
2. Within-domain: 60 granular runs (t901)
"""

import sys, os, json
import numpy as np
from scipy import stats
from scipy.special import expit

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, "coherence-benchmark")

# ─── Load data ───
with open("coherence-benchmark/results/benchmark_v1.json") as f:
    bench = json.load(f)

with open("coherence-benchmark/results/t901_ensemble.json") as f:
    t901 = json.load(f)

def get_mean(v):
    if isinstance(v, dict):
        if "mean" in v: return v["mean"]
        if "1" in v: return v["1"]
        return list(v.values())[0]
    return float(v)

# ─── Extract benchmark arrays ───
sys_names = list(bench.keys())
sys_labels = ["S1", "S2", "S3", "S4", "S5", "S6", "P1", "P2"]
sys_types = ["independent", "fully_coupled", "coupled_markov", "modular",
             "sandpile", "hierarchical", "forest", "granular"]

C_bench = np.array([get_mean(bench[s]["C"]) for s in sys_names])
I_bench = np.array([get_mean(bench[s]["predictive_information"]) for s in sys_names])
Cs_bench = np.array([get_mean(bench[s]["statistical_complexity"]) for s in sys_names])
MSE_bench = np.array([get_mean(bench[s]["mse"]) for s in sys_names])
TE_bench = np.array([get_mean(bench[s]["transfer_entropy"]) for s in sys_names])

X_bench = np.column_stack([I_bench, Cs_bench, MSE_bench, TE_bench])
y_bench = C_bench

# ─── Extract t901 arrays ───
C_t901 = np.array([r["pre_C"] for r in t901])
I_t901 = np.array([r["pre_I_pred"] for r in t901])
Cs_t901 = np.array([r["pre_C_sigma"] for r in t901])
MSE_t901 = np.array([r["pre_MSE_s1"] for r in t901])
friction_t901 = np.array([r["friction"] for r in t901])

X_t901 = np.column_stack([I_t901, Cs_t901, MSE_t901])
y_t901 = C_t901

# ─── OLS helpers ───
def ols_fit(X, y):
    n, p = X.shape
    X_aug = np.column_stack([np.ones(n), X])
    beta = np.linalg.lstsq(X_aug, y, rcond=None)[0]
    y_hat = X_aug @ beta
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    # Adjusted R²
    r2_adj = 1 - (1 - r2) * (n - 1) / (n - p - 1) if (n - p - 1) > 0 else r2
    # RMSE
    rmse = np.sqrt(np.mean((y - y_hat) ** 2))
    return beta, r2, r2_adj, rmse, y - y_hat, y_hat

def loo_cv(X, y):
    """Leave-one-out cross-validation."""
    n = len(y)
    y_pred = np.zeros(n)
    for i in range(n):
        mask = np.arange(n) != i
        beta, _, _, _, _, _ = ols_fit(X[mask], y[mask])
        y_pred[i] = np.dot(np.concatenate([[1], X[i]]), beta)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2_loo = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    rmse_loo = np.sqrt(np.mean((y - y_pred) ** 2))
    return r2_loo, rmse_loo, y_pred

print("=" * 80)
print("RD-7A: CROSS-DOMAIN NOVELTY AUDIT")
print("Can C be reconstructed from I_pred + C_σ + MSE + TE?")
print("=" * 80)

# ═══════════════════════════════════════════════════════════════
# PART 1: Cross-domain reconstruction (8 systems)
# ═══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("PART 1: CROSS-DOMAIN (8 systems: S1-S6 + P1 + P2)")
print("─" * 80)

# Full model: C ~ I_pred + C_σ + MSE + TE
beta_b, r2_b, r2adj_b, rmse_b, resid_b, yhat_b = ols_fit(X_bench, y_bench)
r2_loo_b, rmse_loo_b, ypred_loo_b = loo_cv(X_bench, y_bench)

print(f"\n  Full model: C ~ I_pred + C_σ + MSE + TE")
print(f"    R² = {r2_b:.4f}")
print(f"    Adjusted R² = {r2adj_b:.4f}")
print(f"    RMSE = {rmse_b:.4f}")
print(f"    LOO-CV R² = {r2_loo_b:.4f}")
print(f"    LOO-CV RMSE = {rmse_loo_b:.4f}")

# Per-system breakdown
print(f"\n  {'System':>6s} {'Type':>16s} {'C_actual':>10s} {'C_pred':>10s} {'Residual':>10s} {'|Error|':>10s}")
print(f"  {'-'*65}")
for i, (sl, st) in enumerate(zip(sys_labels, sys_types)):
    print(f"  {sl:>6s} {st:>16s} {y_bench[i]:>10.4f} {yhat_b[i]:>10.4f} {resid_b[i]:>+10.4f} {abs(resid_b[i]):>10.4f}")

# LOO predictions
print(f"\n  LOO predictions:")
print(f"  {'System':>6s} {'C_actual':>10s} {'C_LOO':>10s} {'|Error|':>10s}")
print(f"  {'-'*40}")
for i, sl in enumerate(sys_labels):
    err = abs(y_bench[i] - ypred_loo_b[i])
    print(f"  {sl:>6s} {y_bench[i]:>10.4f} {ypred_loo_b[i]:>10.4f} {err:>10.4f}")

# Individual metric contributions (partial R²)
print(f"\n  Partial R² (each metric's unique contribution to predicting C):")
metric_names = ["I_pred", "C_σ", "MSE", "TE"]
for i, mn in enumerate(metric_names):
    mask = [j for j in range(4) if j != i]
    _, r2_full, _, _, _, _ = ols_fit(X_bench, y_bench)
    _, r2_red, _, _, _, _ = ols_fit(X_bench[:, mask], y_bench)
    if (1 - r2_red) > 0:
        pr2 = (r2_full - r2_red) / (1 - r2_red)
    else:
        pr2 = 0
    print(f"    {mn:>8s}: unique R² = {pr2:.4f} ({pr2*100:.1f}% of unexplained)")

# ═══════════════════════════════════════════════════════════════
# PART 2: Within-domain reconstruction (60 granular runs)
# ═══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("PART 2: WITHIN-DOMAIN (60 granular runs, t901)")
print("─" * 80)

# Model: C ~ I_pred + C_σ + MSE (no TE available for t901)
beta_t, r2_t, r2adj_t, rmse_t, resid_t, yhat_t = ols_fit(X_t901, y_t901)
r2_loo_t, rmse_loo_t, ypred_loo_t = loo_cv(X_t901, y_t901)

print(f"\n  Model: C ~ I_pred + C_σ + MSE")
print(f"    R² = {r2_t:.4f}")
print(f"    Adjusted R² = {r2adj_t:.4f}")
print(f"    RMSE = {rmse_t:.4f}")
print(f"    LOO-CV R² = {r2_loo_t:.4f}")
print(f"    LOO-CV RMSE = {rmse_loo_t:.4f}")

# Per-metric correlations with C
print(f"\n  Pairwise correlations with C:")
for i, mn in enumerate(["I_pred", "C_σ", "MSE"]):
    r, p = stats.pearsonr(X_t901[:, i], y_t901)
    print(f"    C vs {mn}: r = {r:+.4f}  (p = {p:.4f})")

# Partial R²
print(f"\n  Partial R² (each metric's unique contribution):")
for i, mn in enumerate(["I_pred", "C_σ", "MSE"]):
    mask = [j for j in range(3) if j != i]
    _, r2_full, _, _, _, _ = ols_fit(X_t901, y_t901)
    _, r2_red, _, _, _, _ = ols_fit(X_t901[:, mask], y_t901)
    if (1 - r2_red) > 0:
        pr2 = (r2_full - r2_red) / (1 - r2_red)
    else:
        pr2 = 0
    print(f"    {mn:>8s}: unique R² = {pr2:.4f} ({pr2*100:.1f}% of unexplained)")

# Residual statistics
print(f"\n  Residual analysis:")
print(f"    Mean residual: {np.mean(resid_t):.6f} (should be ~0)")
print(f"    Std residual:  {np.std(resid_t):.4f}")
print(f"    Min residual:  {np.min(resid_t):.4f}")
print(f"    Max residual:  {np.max(resid_t):.4f}")
# Shapiro-Wilk normality test
if len(resid_t) <= 5000:
    w_stat, w_p = stats.shapiro(resid_t)
    print(f"    Shapiro-Wilk:  W = {w_stat:.4f}, p = {w_p:.4f} ({'normal' if w_p > 0.05 else 'NON-normal'})")

# Residual vs friction
print(f"\n  Residuals by friction level:")
for f in sorted(set(friction_t901)):
    mask = friction_t901 == f
    r_subset = resid_t[mask]
    print(f"    μ={f:.2f}: mean={np.mean(r_subset):+.4f}, std={np.std(r_subset):.4f}")

# ═══════════════════════════════════════════════════════════════
# PART 3: Individual system models (S1-S6)
# ═══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("PART 3: PER-SYSTEM RECONSTRUCTION (individual synthetic systems)")
print("─" * 80)

# For each synthetic system, generate multiple realizations and test reconstruction
import sys
sys.path.insert(0, "coherence-benchmark")
from synthetic.generators import independent, coupled_markov, fully_coupled, modular, hierarchical, critical

generators = {
    "S1_independent": independent,
    "S2_fully_coupled": fully_coupled,
    "S3_coupled_markov": coupled_markov,
    "S4_modular": modular,
    "S5_sandpile": critical,
    "S6_hierarchical": hierarchical,
}

from metrics.total_correlation import compute_C
from metrics.predictive_information import compute_predictive_information
from metrics.statistical_complexity import compute_statistical_complexity
from metrics.multiscale_entropy import compute_mse
from metrics.transfer_entropy import compute_transfer_entropy_matrix

n_realizations = 30
per_system_results = {}

print(f"\n  Generating {n_realizations} realizations per system...")
for sys_name, gen_func in generators.items():
    Cs_list = []
    for rep in range(n_realizations):
        try:
            data, _ = gen_func(n_components=8, n_timepoints=500, seed=rep*100+42)
            c_val = compute_C(data, "gaussian")
            i_val = compute_predictive_information(data, tau=1)
            cs_val = compute_statistical_complexity(data)
            mse_dict = compute_mse(data, max_scale=2)
            mse_val = mse_dict.get(1, 0)
            te_mat = compute_transfer_entropy_matrix(data, tau=1)
            te_val = np.mean(te_mat[te_mat > 0]) if np.any(te_mat > 0) else 0

            Cs_list.append([c_val, i_val, cs_val, mse_val, te_val])
        except Exception as e:
            continue

    if len(Cs_list) >= 10:
        arr = np.array(Cs_list)
        X_sys = arr[:, 1:]  # I, Cs, MSE, TE
        y_sys = arr[:, 0]   # C

        beta_s, r2_s, r2adj_s, rmse_s, _, _ = ols_fit(X_sys, y_sys)
        r2_loo_s, rmse_loo_s, _ = loo_cv(X_sys, y_sys)

        per_system_results[sys_name] = {
            "n": len(Cs_list),
            "R²": round(r2_s, 4),
            "R²_adj": round(r2adj_s, 4),
            "RMSE": round(rmse_s, 4),
            "LOO_R²": round(r2_loo_s, 4),
            "LOO_RMSE": round(rmse_loo_s, 4),
            "C_range": [round(float(np.min(y_sys)), 4), round(float(np.max(y_sys)), 4)],
        }
        print(f"    {sys_name:25s}: R²={r2_s:.4f}, LOO-R²={r2_loo_s:.4f}, C_range=[{np.min(y_sys):.3f}, {np.max(y_sys):.3f}]")

# ═══════════════════════════════════════════════════════════════
# PART 4: Verdict
# ═══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("PART 4: VERDICT")
print("─" * 80)

print(f"""
  Cross-domain (8 systems):
    R² = {r2_b:.4f}  →  {'RECONSTRUCTABLE' if r2_b > 0.8 else 'PARTIALLY RECONSTRUCTABLE' if r2_b > 0.5 else 'NOT RECONSTRUCTABLE'}
    LOO-R² = {r2_loo_b:.4f}

  Within-domain (60 granular runs):
    R² = {r2_t:.4f}  →  {'RECONSTRUCTABLE' if r2_t > 0.8 else 'PARTIALLY RECONSTRUCTABLE' if r2_t > 0.5 else 'NOT RECONSTRUCTABLE'}
    LOO-R² = {r2_loo_t:.4f}

  Verdict:""")

if r2_b > 0.8 and r2_t > 0.8:
    verdict = "C IS reconstructable from competitors. It is NOT an independent observable."
    pillar = "THEORY PILLAR REMOVED: C is a nonlinear remix of existing measures."
elif r2_b > 0.5 or r2_t > 0.5:
    verdict = "C is PARTIALLY reconstructable. It shares substantial variance with competitors but retains some unique information."
    pillar = "THEory PILLAR WEAKENED: C is mostly redundant but not entirely derivable."
else:
    verdict = "C is NOT reconstructable from competitors. It IS an independent observable."
    pillar = "THEORY PILLAR SURVIVES: C captures information not present in I_pred, C_σ, MSE, or TE."

print(f"    {verdict}")
print(f"    {pillar}")

# Save results
results = {
    "cross_domain": {
        "n_systems": 8,
        "R²": round(r2_b, 4),
        "R²_adj": round(r2adj_b, 4),
        "RMSE": round(rmse_b, 4),
        "LOO_R²": round(r2_loo_b, 4),
        "LOO_RMSE": round(rmse_loo_b, 4),
        "residuals": resid_b.tolist(),
        "predictions": yhat_b.tolist(),
        "loo_predictions": ypred_loo_b.tolist(),
        "actuals": y_bench.tolist(),
    },
    "within_domain": {
        "n_runs": 60,
        "R²": round(r2_t, 4),
        "R²_adj": round(r2adj_t, 4),
        "RMSE": round(rmse_t, 4),
        "LOO_R²": round(r2_loo_t, 4),
        "LOO_RMSE": round(rmse_loo_t, 4),
        "residuals_by_friction": {
            str(f): {
                "mean": round(float(np.mean(resid_t[friction_t901 == f])), 4),
                "std": round(float(np.std(resid_t[friction_t901 == f])), 4),
            }
            for f in sorted(set(friction_t901))
        },
    },
    "per_system": per_system_results,
    "verdict": verdict,
    "pillar_status": pillar,
}

with open("audits/rd07a_novelty_audit.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved: audits/rd07a_novelty_audit.json")
