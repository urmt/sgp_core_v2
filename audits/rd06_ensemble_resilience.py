"""RD-6: Ensemble Resilience Test
200 independent granular realizations, fixed 50% removal.
Test: Does pre-perturbation C predict recovery?
"""

import sys, os, json, time
import numpy as np
from scipy import stats

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, "coherence-benchmark")

from t901_analysis import _granular_run, _bin_data, _sliding_C

# ─── Config ───
N_RUNS = 200
REMOVAL_FRAC = 0.50
N_GRAINS = 50
N_STEPS = 1000
REMOVAL_STEP = 500
FRICTION = 0.30
BASE_SEED = 2000

# ─── Run ensemble ───
results = []
t0 = time.time()

for i in range(N_RUNS):
    seed = BASE_SEED + i
    all_y, all_x, _, _, _, _ = _granular_run(
        n_grains=N_GRAINS, n_steps=N_STEPS, removal_step=REMOVAL_STEP,
        removal_fraction=REMOVAL_FRAC, friction=FRICTION, seed=seed,
    )
    X = _bin_data(all_y, all_x, n_bins=10)
    times, c_vals = _sliding_C(X, window=50, step=10)

    # Pre-perturbation: steps 100-490
    pre_mask = (times >= 100) & (times < REMOVAL_STEP)
    C_pre = float(np.nanmean(c_vals[pre_mask]))

    # Perturbation response: steps 500-600
    pert_mask = (times >= REMOVAL_STEP) & (times <= REMOVAL_STEP + 100)
    C_min = float(np.nanmin(c_vals[pert_mask])) if np.sum(pert_mask) >= 1 else np.nan
    dC = C_min - C_pre if not np.isnan(C_min) else np.nan

    # τ_rec: first time C >= 0.95 * C_pre after perturbation
    post_mask = times > REMOVAL_STEP
    post_times = times[post_mask]
    post_c = c_vals[post_mask]
    threshold = 0.95 * C_pre

    tau_rec = np.nan
    for k in range(len(post_c)):
        if not np.isnan(post_c[k]) and post_c[k] >= threshold:
            tau_rec = float(post_times[k] - REMOVAL_STEP)
            break

    # C_final: mean of last 100 steps
    late_mask = times >= (N_STEPS - 100)
    C_final = float(np.nanmean(c_vals[late_mask])) if np.sum(late_mask) >= 3 else np.nan
    C_ratio = C_final / C_pre if (not np.isnan(C_final) and C_pre > 0) else np.nan

    # Collapse: C_final < 0.05 (essentially zero)
    collapsed = bool(np.isnan(C_final) or C_final < 0.05)

    results.append({
        "run": i, "seed": seed,
        "C_pre": round(C_pre, 4),
        "C_min": round(C_min, 4) if not np.isnan(C_min) else None,
        "dC": round(dC, 4) if not np.isnan(dC) else None,
        "tau_rec": round(tau_rec, 1) if not np.isnan(tau_rec) else None,
        "C_final": round(C_final, 4) if not np.isnan(C_final) else None,
        "C_ratio": round(C_ratio, 4) if not np.isnan(C_ratio) else None,
        "collapsed": collapsed,
    })

    if (i + 1) % 50 == 0:
        elapsed = time.time() - t0
        print(f"  [{i+1}/{N_RUNS}] {elapsed:.0f}s elapsed, {sum(1 for r in results if r['collapsed'])} collapsed so far")

elapsed = time.time() - t0
n_collapsed = sum(1 for r in results if r["collapsed"])
n_survived = N_RUNS - n_collapsed
print(f"\nEnsemble complete: {N_RUNS} runs in {elapsed:.0f}s")
print(f"  Survived: {n_survived}  |  Collapsed: {n_collapsed}  |  Collapse rate: {n_collapsed/N_RUNS*100:.1f}%")

# Save raw
with open("audits/rd06_ensemble_raw.json", "w") as f:
    json.dump(results, f, indent=2)

# ─── Analysis ───
print("\n" + "=" * 80)
print("RD-6: ENSEMBLE RESILIENCE ANALYSIS")
print("=" * 80)

c_pre_all = np.array([r["C_pre"] for r in results])
collapsed_all = np.array([1 if r["collapsed"] else 0 for r in results])
survived_mask = ~collapsed_all.astype(bool)
collapsed_mask = collapsed_all.astype(bool)

# Split by survival
c_pre_survived = c_pre_all[survived_mask]
c_pre_collapsed = c_pre_all[collapsed_mask]

# ─── 1. Summary statistics ───
print("\n─── 1. Summary Statistics ───")
print(f"  C_pre (all):       {np.mean(c_pre_all):.4f} ± {np.std(c_pre_all):.4f}  (n={N_RUNS})")
print(f"  C_pre (survived):  {np.mean(c_pre_survived):.4f} ± {np.std(c_pre_survived):.4f}  (n={n_survived})")
print(f"  C_pre (collapsed): {np.mean(c_pre_collapsed):.4f} ± {np.std(c_pre_collapsed):.4f}  (n={n_collapsed})")

# Welch's t-test
if n_collapsed > 0 and n_survived > 0:
    t_stat, p_val = stats.ttest_ind(c_pre_survived, c_pre_collapsed, equal_var=False)
    print(f"\n  Welch's t-test (survived vs collapsed C_pre):")
    print(f"    t = {t_stat:.3f}, p = {p_val:.4f}")
    # Cohen's d
    pooled_std = np.sqrt((np.std(c_pre_survived)**2 + np.std(c_pre_collapsed)**2) / 2)
    cohens_d = (np.mean(c_pre_survived) - np.mean(c_pre_collapsed)) / pooled_std if pooled_std > 0 else 0
    print(f"    Cohen's d = {cohens_d:.3f}")

# Effect size: rank-biserial correlation
if n_collapsed > 0 and n_survived > 0:
    # Mean rank of C_pre among survivors vs collapsed
    ranks = stats.rankdata(c_pre_all)
    r_rank = np.mean(ranks[survived_mask]) - np.mean(ranks[collapsed_mask])
    r_rank = r_rank / N_RUNS  # normalize
    print(f"    Rank-biserial r = {r_rank:.3f}")

# ─── 2. Correlations ───
print("\n─── 2. Correlations (C_pre vs recovery metrics, survivors only) ───")

survivor_results = [r for r in results if not r["collapsed"]]

for metric_name, metric_key in [("τ_rec", "tau_rec"), ("C_final/C_pre", "C_ratio")]:
    vals = [(r["C_pre"], r[metric_key]) for r in survivor_results if r[metric_key] is not None]
    if len(vals) > 2:
        x, y = zip(*vals)
        x, y = np.array(x), np.array(y)
        r_pearson, p_pearson = stats.pearsonr(x, y)
        r_spearman, p_spearman = stats.spearmanr(x, y)
        print(f"  C_pre vs {metric_name}:")
        print(f"    Pearson r = {r_pearson:.3f}  (p = {p_pearson:.4f})")
        print(f"    Spearman ρ = {r_spearman:.3f}  (p = {p_spearman:.4f})")
        print(f"    n = {len(vals)}")

# ─── 3. Logistic regression: collapse ~ C_pre ───
print("\n─── 3. Logistic Regression: collapse ~ C_pre ───")
from scipy.special import expit

# Manual logistic regression (no sklearn dependency)
def logistic_regression(x, y, max_iter=1000, lr=0.01):
    """Simple gradient ascent for logistic regression."""
    n = len(x)
    # Standardize x
    x_mean, x_std = np.mean(x), np.std(x)
    x_norm = (x - x_mean) / max(x_std, 1e-10)
    # Initialize
    w, b = 0.0, 0.0
    for _ in range(max_iter):
        z = w * x_norm + b
        p = expit(z)
        # Gradient
        gw = np.mean((p - y) * x_norm)
        gb = np.mean(p - y)
        w -= lr * gw
        b -= lr * gb
    # Coefficients on original scale
    w_orig = w / max(x_std, 1e-10)
    b_orig = b - w_orig * x_mean
    # Standard errors
    p_final = expit(w * x_norm + b)
    var_w = np.mean(p_final * (1 - p_final) * x_norm**2)
    se_w = 1.0 / np.sqrt(max(var_w * n, 1e-10))
    se_w_orig = se_w / max(x_std, 1e-10)
    return w_orig, b_orig, se_w_orig

w, b, se_w = logistic_regression(c_pre_all, collapsed_all.astype(float))
z_score = w / se_w if se_w > 0 else 0
p_logistic = 2 * (1 - stats.norm.cdf(abs(z_score)))

print(f"  Coefficients:")
print(f"    β₁ (C_pre) = {w:.3f} ± {se_w:.3f}")
print(f"    z = {z_score:.3f}, p = {p_logistic:.4f}")
print(f"    OR = {np.exp(w):.3f} per unit C_pre")

# Predicted probabilities
p_collapse = expit(w * c_pre_all + b)
print(f"  Predicted collapse probability at C_pre=0.3: {expit(w*0.3+b):.3f}")
print(f"  Predicted collapse probability at C_pre=0.5: {expit(w*0.5+b):.3f}")
print(f"  Predicted collapse probability at C_pre=0.7: {expit(w*0.7+b):.3f}")

# ─── 4. ROC-AUC ───
print("\n─── 4. ROC-AUC ───")
# Use C_pre to predict survival (higher C_pre → survive)
# AUC for predicting survival: P(C_pre_survived > C_pre_collapsed)
if n_collapsed > 0 and n_survived > 0:
    # Mann-Whitney U = AUC
    u_stat, p_mannwhitney = stats.mannwhitneyu(c_pre_survived, c_pre_collapsed, alternative='greater')
    auc = u_stat / (n_survived * n_collapsed)
    print(f"  Mann-Whitney U = {u_stat:.0f}")
    print(f"  AUC (C_pre predicts survival) = {auc:.3f}")
    print(f"  p = {p_mannwhitney:.4f}")

    # 95% CI for AUC (DeLong approximation)
    se_auc = np.sqrt(auc * (1-auc) / min(n_survived, n_collapsed))
    ci_low = max(0, auc - 1.96 * se_auc)
    ci_high = min(1, auc + 1.96 * se_auc)
    print(f"  95% CI: [{ci_low:.3f}, {ci_high:.3f}]")

    if auc > 0.9:
        print("  → EXCELLENT discrimination")
    elif auc > 0.8:
        print("  → GOOD discrimination")
    elif auc > 0.7:
        print("  → FAIR discrimination")
    elif auc > 0.6:
        print("  → POOR discrimination")
    else:
        print("  → NO discrimination (chance level)")

# ─── 5. Bootstrap CIs ───
print("\n─── 5. Bootstrap 95% CIs (1000 iterations) ───")
rng = np.random.default_rng(42)
boot_aucs = []
boot_slopes = []
boot_cohens_d = []

for _ in range(1000):
    idx = rng.choice(N_RUNS, size=N_RUNS, replace=True)
    c_boot = c_pre_all[idx]
    col_boot = collapsed_all[idx]
    surv_boot = c_boot[col_boot == 0]
    coll_boot = c_boot[col_boot == 1]
    if len(surv_boot) > 0 and len(coll_boot) > 0:
        u = stats.mannwhitneyu(surv_boot, coll_boot, alternative='greater').statistic
        boot_aucs.append(u / (len(surv_boot) * len(coll_boot)))
        pooled = np.sqrt((np.std(surv_boot)**2 + np.std(coll_boot)**2) / 2)
        if pooled > 0:
            boot_cohens_d.append((np.mean(surv_boot) - np.mean(coll_boot)) / pooled)

auc_ci = np.percentile(boot_aucs, [2.5, 97.5])
d_ci = np.percentile(boot_cohens_d, [2.5, 97.5])
print(f"  AUC: {np.mean(boot_aucs):.3f}  95% CI [{auc_ci[0]:.3f}, {auc_ci[1]:.3f}]")
print(f"  Cohen's d: {np.mean(boot_cohens_d):.3f}  95% CI [{d_ci[0]:.3f}, {d_ci[1]:.3f}]")

# Save analysis
analysis = {
    "n_runs": N_RUNS,
    "n_survived": int(n_survived),
    "n_collapsed": int(n_collapsed),
    "collapse_rate": round(n_collapsed / N_RUNS, 4),
    "C_pre_mean_all": round(float(np.mean(c_pre_all)), 4),
    "C_pre_std_all": round(float(np.std(c_pre_all)), 4),
    "C_pre_mean_survived": round(float(np.mean(c_pre_survived)), 4),
    "C_pre_mean_collapsed": round(float(np.mean(c_pre_collapsed)), 4) if n_collapsed > 0 else None,
    "welch_t": round(float(t_stat), 3) if n_collapsed > 0 and n_survived > 0 else None,
    "welch_p": round(float(p_val), 4) if n_collapsed > 0 and n_survived > 0 else None,
    "cohens_d": round(float(cohens_d), 3) if n_collapsed > 0 and n_survived > 0 else None,
    "logistic_slope_w": round(float(w), 3),
    "logistic_se": round(float(se_w), 3),
    "logistic_z": round(float(z_score), 3),
    "logistic_p": round(float(p_logistic), 4),
    "auc": round(float(auc), 3) if n_collapsed > 0 and n_survived > 0 else None,
    "auc_ci_95": [round(float(auc_ci[0]), 3), round(float(auc_ci[1]), 3)] if n_collapsed > 0 else None,
    "cohens_d_bootstrap": round(float(np.mean(boot_cohens_d)), 3) if boot_cohens_d else None,
    "cohens_d_ci_95": [round(float(d_ci[0]), 3), round(float(d_ci[1]), 3)] if boot_cohens_d else None,
}

with open("audits/rd06_analysis.json", "w") as f:
    json.dump(analysis, f, indent=2)

print(f"\nRaw data: audits/rd06_ensemble_raw.json")
print(f"Analysis: audits/rd06_analysis.json")
