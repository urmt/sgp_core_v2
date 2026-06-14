"""Conditional Information + Interaction Stability Analysis.

Targets two directives simultaneously:
  RD-014 P2: CONDITIONAL_INFORMATION_ANALYSIS — ΔR², AIC, permutation, LOCO
  RD-014 P3: INTERACTION_STABILITY_REPORT — bootstrap, k-fold CV, sign stability

Uses existing t901_ensemble.json data only. No new simulations.
"""

import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import KFold
import statsmodels.api as sm
import warnings
warnings.filterwarnings("ignore")

RNG = np.random.default_rng(42)

# ─── Load data ───

with open("coherence-benchmark/results/t901_ensemble.json") as f:
    raw = json.load(f)

rows = []
for r in raw:
    row = {}
    for k, v in r.items():
        if v is None:
            row[k] = np.nan
        else:
            row[k] = v
    rows.append(row)

X_names = ["pre_C", "friction", "msd", "rms_velocity", "neighbor_turnover", "packing_var"]
y_names = ["dip", "restoration", "tau_rec"]

# Build arrays
n = len(rows)
X = np.full((n, len(X_names)), np.nan)
y = np.full((n, len(y_names)), np.nan)

for i, r in enumerate(rows):
    for j, name in enumerate(X_names):
        X[i, j] = r.get(name, np.nan)
    for j, name in enumerate(y_names):
        y[i, j] = r.get(name, np.nan)

# Standardize
means = np.nanmean(X, axis=0)
stds = np.nanstd(X, axis=0)
stds[stds == 0] = 1.0
X_z = (X - means) / stds

ymeans = np.nanmean(y, axis=0)
ystds = np.nanstd(y, axis=0)
ystds[ystds == 0] = 1.0
y_z = (y - ymeans) / ystds

# Valid rows: no NaN in core predictors (pre_C, friction) and at least one y
core_idx = [0, 1]  # pre_C, friction
valid_core = ~(np.isnan(X_z[:, core_idx[0]]) | np.isnan(X_z[:, core_idx[1]]))

# ─── Helper: fit OLS with statsmodels ───

def fit_ols(X_in, y_in, add_const=True):
    good = ~(np.isnan(y_in) | np.any(np.isnan(X_in), axis=1))
    if good.sum() < X_in.shape[1] + 2:
        return None
    X_use = sm.add_constant(X_in[good]) if add_const else X_in[good]
    y_use = y_in[good]
    try:
        model = sm.OLS(y_use, X_use).fit()
        return model
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════
# PRIORITY 2: CONDITIONAL INFORMATION ANALYSIS
# ═══════════════════════════════════════════════════════════════════

print("=" * 78)
print("  PRIORITY 2: CONDITIONAL INFORMATION ANALYSIS")
print("=" * 78)

for yi, yname in enumerate(y_names):
    y_vec = y_z[:, yi]
    good = valid_core & ~np.isnan(y_vec)
    if good.sum() < 10:
        continue
    n_good = good.sum()
    print(f"\n  Target: {yname}  (n={n_good})")
    print(f"  {'Model':>40s}  {'R²':>8s}  {'ΔR²':>8s}  {'AIC':>10s}  {'BIC':>10s}")
    print(f"  {'-' * 80}")

    # 1. Null (mean only)
    null_pred = np.full(n_good, np.mean(y_vec[good]))
    null_r2 = r2_score(y_vec[good], null_pred)
    null_aic = n_good * np.log(np.mean((y_vec[good] - null_pred)**2)) + 2 * 1
    null_bic = n_good * np.log(np.mean((y_vec[good] - null_pred)**2)) + np.log(n_good) * 1
    print(f"  {'Null (mean only)':>40s}  {null_r2:>8.4f}  {'—':>8s}  {null_aic:>10.1f}  {null_bic:>10.1f}")

    # 2. Friction only
    m = fit_ols(X_z[good, 1:2], y_vec[good])
    if m is not None:
        delta = m.rsquared - null_r2
        print(f"  {'Friction only':>40s}  {m.rsquared:>8.4f}  {delta:>+8.4f}  {m.aic:>10.1f}  {m.bic:>10.1f}")

    # 3. C only
    m = fit_ols(X_z[good, 0:1], y_vec[good])
    if m is not None:
        delta = m.rsquared - null_r2
        print(f"  {'C only':>40s}  {m.rsquared:>8.4f}  {delta:>+8.4f}  {m.aic:>10.1f}  {m.bic:>10.1f}")

    # 4. C + friction (additive)
    m = fit_ols(X_z[good][:, [0, 1]], y_vec[good])
    if m is not None:
        delta = m.rsquared - null_r2
        print(f"  {'C + Friction (additive)':>40s}  {m.rsquared:>8.4f}  {delta:>+8.4f}  {m.aic:>10.1f}  {m.bic:>10.1f}")

    # 5. C + Friction + Interaction (full core)
    X_int = np.column_stack([X_z[good, 0], X_z[good, 1], X_z[good, 0] * X_z[good, 1]])
    m_full = fit_ols(X_int, y_vec[good])
    if m_full is not None:
        delta = m_full.rsquared - (fit_ols(X_z[good][:, [0, 1]], y_vec[good]).rsquared if fit_ols(X_z[good][:, [0, 1]], y_vec[good]) is not None else 0)
        print(f"  {'C + Friction + C×Friction (full core)':>40s}  {m_full.rsquared:>8.4f}  {delta:>+8.4f}  {m_full.aic:>10.1f}  {m_full.bic:>10.1f}")

    # 6. All mobility predictors only (MSD, RMS, turnover, packing)
    mob_idx = [2, 3, 4, 5]
    mob_valid = ~np.any(np.isnan(X_z[good][:, mob_idx]), axis=1)
    if mob_valid.sum() > 10:
        m_mob = fit_ols(X_z[good][mob_valid][:, mob_idx], y_vec[good][mob_valid])
        if m_mob is not None:
            delta = m_mob.rsquared - null_r2
            print(f"  {'Mobility proxies only (MSD+Vel+Turn+Packing)':>40s}  {m_mob.rsquared:>8.4f}  {delta:>+8.4f}  {m_mob.aic:>10.1f}  {m_mob.bic:>10.1f}")

    # 7. Full core + mobility
    all_pred = np.column_stack([X_z[good, 0], X_z[good, 1], X_z[good, 0] * X_z[good, 1],
                                X_z[good, 2], X_z[good, 3], X_z[good, 4], X_z[good, 5]])
    all_valid = ~np.any(np.isnan(all_pred), axis=1)
    if all_valid.sum() > 15:
        m_all = fit_ols(all_pred[all_valid], y_vec[good][all_valid])
        if m_all is not None:
            delta = m_all.rsquared - m_full.rsquared
            print(f"  {'Full core + all mobility':>40s}  {m_all.rsquared:>8.4f}  {delta:>+8.4f}  {m_all.aic:>10.1f}  {m_all.bic:>10.1f}")

    # ─── Condition-specific ΔR²: What does C add given friction? ───
    print(f"\n  ── CONDITIONAL ΔR² (What does C add?) ──")

    # ΔR²: friction model → add C
    m_fric = fit_ols(X_z[good, 1:2], y_vec[good])
    m_fric_c = fit_ols(X_z[good][:, [1, 0]], y_vec[good])  # friction + C
    if m_fric is not None and m_fric_c is not None:
        delta_c_given_fric = m_fric_c.rsquared - m_fric.rsquared
        print(f"  C given friction:  ΔR² = {delta_c_given_fric:>+.4f}  (R²: {m_fric.rsquared:.4f} → {m_fric_c.rsquared:.4f})")

    # ΔR²: friction model → add C + interaction
    m_fric_int = fit_ols(np.column_stack([X_z[good, 1], X_z[good, 0], X_z[good, 0] * X_z[good, 1]]), y_vec[good])
    if m_fric is not None and m_fric_int is not None:
        delta_full_given_fric = m_fric_int.rsquared - m_fric.rsquared
        print(f"  C+C×Fric given friction: ΔR² = {delta_full_given_fric:>+.4f}  (R²: {m_fric.rsquared:.4f} → {m_fric_int.rsquared:.4f})")

    # ΔR²: C model → add friction
    m_c = fit_ols(X_z[good, 0:1], y_vec[good])
    if m_c is not None and m_fric_c is not None:
        delta_fric_given_c = m_fric_c.rsquared - m_c.rsquared
        print(f"  Friction given C: ΔR² = {delta_fric_given_c:>+.4f}  (R²: {m_c.rsquared:.4f} → {m_fric_c.rsquared:.4f})")

    # ΔR²: C model → add friction + interaction
    if m_c is not None and m_fric_int is not None:
        delta_full_given_c = m_fric_int.rsquared - m_c.rsquared
        print(f"  Fric+C×Fric given C: ΔR² = {delta_full_given_c:>+.4f}  (R²: {m_c.rsquared:.4f} → {m_fric_int.rsquared:.4f})")

    # ─── Permutation importance ───

    print(f"\n  ── PERMUTATION IMPORTANCE (shuffle predictor, measure R² drop) ──")
    n_perm = 1000

    # Fit full core model
    X_full_core = np.column_stack([X_z[good, 0], X_z[good, 1], X_z[good, 0] * X_z[good, 1]])
    m_ref = fit_ols(X_full_core, y_vec[good])
    if m_ref is not None:
        baseline_r2 = m_ref.rsquared
        print(f"  Baseline (full core model): R² = {baseline_r2:.4f}")

        for pi, pname in enumerate(["pre_C", "friction", "interaction"]):
            perm_r2s = []
            for _ in range(n_perm):
                X_perm = X_full_core.copy()
                X_perm[:, pi] = RNG.permutation(X_perm[:, pi])
                m_perm = fit_ols(X_perm, y_vec[good])
                if m_perm is not None:
                    perm_r2s.append(m_perm.rsquared)
            if perm_r2s:
                mean_perm_r2 = np.mean(perm_r2s)
                drop = baseline_r2 - mean_perm_r2
                ci_lo = np.percentile(perm_r2s, 2.5)
                ci_hi = np.percentile(perm_r2s, 97.5)
                frac_loss = drop / max(baseline_r2, 1e-10)
                print(f"  Permute {pname:>12s}: mean R²={mean_perm_r2:.4f}  drop={drop:+.4f}  "
                      f"frac_loss={frac_loss:.3f}  [95% CI: ({ci_lo:.4f}, {ci_hi:.4f})]")

    # ─── Leave-One-Covariate-Out (LOCO) ───

    print(f"\n  ── LEAVE-ONE-COVARIATE-OUT (LOCO) ──")
    if m_ref is not None:
        all_covs = [
            ([1, 2], "leave out C (keep friction + interaction)"),
            ([0, 2], "leave out friction (keep C + interaction)"),
            ([0, 1], "leave out interaction (keep C + friction, i.e. additive)"),
        ]
        for keep_cols, desc in all_covs:
            X_sub = X_full_core[:, keep_cols]
            m_sub = fit_ols(X_sub, y_vec[good])
            if m_sub is not None:
                r2_drop = m_ref.rsquared - m_sub.rsquared
                print(f"  {desc:>50s}: R² = {m_sub.rsquared:.4f}  drop = {r2_drop:+.4f}")

    # ─── Mobility LOCO: full core vs full core minus each mobility proxy ───

    print(f"\n  ── MOBILITY LOCO (does mobility add beyond full core?) ──")
    all_mob_valid = ~np.any(np.isnan(X_z[good][:, mob_idx]), axis=1)
    if all_mob_valid.sum() > 10:
        X_full_all = np.column_stack([X_z[good][all_mob_valid, 0], X_z[good][all_mob_valid, 1],
                                       X_z[good][all_mob_valid, 0] * X_z[good][all_mob_valid, 1],
                                       X_z[good][all_mob_valid, 2], X_z[good][all_mob_valid, 3],
                                       X_z[good][all_mob_valid, 4], X_z[good][all_mob_valid, 5]])
        m_full_all = fit_ols(X_full_all, y_vec[good][all_mob_valid])
        if m_full_all is not None:
            print(f"  Full core + 4 mobility: R² = {m_full_all.rsquared:.4f}")

            mob_names = ["msd", "rms_velocity", "neighbor_turnover", "packing_var"]
            for mi, mname in enumerate(mob_names):
                leave_out = [0, 1, 2] + [2 + x for x in range(4) if x != mi]
                X_loo = X_full_all[:, leave_out]
                m_loo = fit_ols(X_loo, y_vec[good][all_mob_valid])
                if m_loo is not None:
                    drop = m_full_all.rsquared - m_loo.rsquared
                    print(f"  Drop {mname:>18s}: R² = {m_loo.rsquared:.4f}  drop = {drop:+.4f}")


# ═══════════════════════════════════════════════════════════════════
# PRIORITY 3: INTERACTION STABILITY REPORT — Numerical Evidence
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  PRIORITY 3: INTERACTION STABILITY — NUMERICAL EVIDENCE")
print("=" * 78)

for yi, yname in enumerate(y_names):
    y_vec = y_z[:, yi]
    good = valid_core & ~np.isnan(y_vec)
    if good.sum() < 10:
        continue
    n_good = good.sum()
    print(f"\n  Target: {yname}  (n={n_good})")

    X_full = np.column_stack([X_z[good, 0], X_z[good, 1], X_z[good, 0] * X_z[good, 1]])

    # ─── 1. Full-sample reference ───
    m_ref = fit_ols(X_full, y_vec[good])
    if m_ref is None:
        print("  Could not fit reference model")
        continue

    print(f"\n  ── 1. Full-Sample Reference ──")
    print(f"  R² = {m_ref.rsquared:.4f}, AIC = {m_ref.aic:.1f}")
    param_names = ["const", "pre_C", "friction", "C×Fric"]
    for i, pn in enumerate(param_names):
        print(f"  {pn:>10s}: coef = {m_ref.params[i]:+.4f}, p = {m_ref.pvalues[i]:.4e}, "
              f"t = {m_ref.tvalues[i]:+.2f}")

    interaction_sig = m_ref.pvalues[3] < 0.05
    interaction_pos = m_ref.params[3] > 0
    print(f"  Interaction positive? {interaction_pos}")
    print(f"  Interaction significant (p<0.05)? {interaction_sig}")

    # ─── 2. Bootstrap ───
    print(f"\n  ── 2. Bootstrap Resampling (n_bootstrap=5000) ──")
    n_boot = 5000
    boot_params = np.zeros((n_boot, 4))
    boot_r2 = np.zeros(n_boot)
    boot_converged = 0

    for b in range(n_boot):
        idx = RNG.choice(n_good, size=n_good, replace=True)
        X_b = X_full[idx]
        y_b = y_vec[good][idx]
        m_b = fit_ols(X_b, y_b)
        if m_b is not None:
            boot_params[b] = m_b.params
            boot_r2[b] = m_b.rsquared
            boot_converged += 1
        else:
            boot_params[b] = np.nan
            boot_r2[b] = np.nan

    valid_boot = ~np.isnan(boot_r2)
    n_valid = valid_boot.sum()
    print(f"  Successful fits: {n_valid}/{n_boot}")

    interaction_coefs = boot_params[valid_boot, 3]
    print(f"  Interaction coefficient:")
    print(f"    Mean = {np.mean(interaction_coefs):+.4f}")
    print(f"    Median = {np.median(interaction_coefs):+.4f}")
    print(f"    SD = {np.std(interaction_coefs):.4f}")
    print(f"    95% CI = [{np.percentile(interaction_coefs, 2.5):+.4f}, {np.percentile(interaction_coefs, 97.5):+.4f}]")
    print(f"    90% CI = [{np.percentile(interaction_coefs, 5):+.4f}, {np.percentile(interaction_coefs, 95):+.4f}]")

    # Sign stability
    pct_positive = np.mean(interaction_coefs > 0) * 100
    pct_negative = np.mean(interaction_coefs < 0) * 100
    print(f"    % positive = {pct_positive:.1f}%")
    print(f"    % negative = {pct_negative:.1f}%")

    # Proportion where interaction p < 0.05
    valid_boot2 = valid_boot.copy()
    boot_pvals = np.zeros(n_boot)
    for b in range(n_boot):
        if valid_boot[b]:
            idx = RNG.choice(n_good, size=n_good, replace=True)
            X_b = X_full[idx]
            y_b = y_vec[good][idx]
            m_b = fit_ols(X_b, y_b)
            if m_b is not None:
                boot_pvals[b] = m_b.pvalues[3]
            else:
                boot_pvals[b] = np.nan
    valid_p = ~np.isnan(boot_pvals) & valid_boot
    pct_sig = np.mean(boot_pvals[valid_p] < 0.05) * 100
    pct_sig_01 = np.mean(boot_pvals[valid_p] < 0.01) * 100
    print(f"    % with p<0.05 = {pct_sig:.1f}%")
    print(f"    % with p<0.01 = {pct_sig_01:.1f}%")

    # Bootstrap distribution of R²
    r2_ci_lo, r2_ci_hi = np.percentile(boot_r2[valid_boot], [2.5, 97.5])
    print(f"  R² bootstrap 95% CI = [{r2_ci_lo:.4f}, {r2_ci_hi:.4f}]")

    # Other coefficients
    for pi, pn in enumerate(param_names):
        vals = boot_params[valid_boot, pi]
        print(f"  {pn:>10s}: mean={np.mean(vals):+.4f}  median={np.median(vals):+.4f}  "
              f"95% CI=[{np.percentile(vals,2.5):+.4f}, {np.percentile(vals,97.5):+.4f}]")

    # ─── 3. k-Fold Cross-Validation ───
    print(f"\n  ── 3. k-Fold Cross-Validation (k=5, repeated 100x) ──")

    n_repeat = 100
    k = 5
    cv_r2_full = []
    cv_r2_additive = []
    cv_r2_fric_only = []
    cv_r2_c_only = []
    cv_interaction_sign = []
    cv_interaction_pvals = []

    for rep in range(n_repeat):
        kf = KFold(n_splits=k, shuffle=True, random_state=rep)
        for train_idx, test_idx in kf.split(X_full):
            X_tr, X_te = X_full[train_idx], X_full[test_idx]
            y_tr, y_te = y_vec[good][train_idx], y_vec[good][test_idx]

            # Full model
            m_tr = fit_ols(X_tr, y_tr)
            if m_tr is not None:
                X_te_c = sm.add_constant(X_te)
                y_pred = m_tr.predict(X_te_c)
                cv_r2_full.append(r2_score(y_te, y_pred))
                cv_interaction_sign.append(m_tr.params[3] > 0)
            else:
                cv_r2_full.append(np.nan)
                cv_interaction_sign.append(None)

            # Additive model (C + friction, no interaction)
            X_tr_add = X_tr[:, :2]
            X_te_add = X_te[:, :2]
            m_add = fit_ols(X_tr_add, y_tr)
            if m_add is not None:
                X_te_ac = sm.add_constant(X_te_add)
                y_pred_add = m_add.predict(X_te_ac)
                cv_r2_additive.append(r2_score(y_te, y_pred_add))
            else:
                cv_r2_additive.append(np.nan)

            # Friction only
            X_tr_f = X_tr[:, 1:2]
            X_te_f = X_te[:, 1:2]
            m_f = fit_ols(X_tr_f, y_tr)
            if m_f is not None:
                X_te_fc = sm.add_constant(X_te_f)
                y_pred_f = m_f.predict(X_te_fc)
                cv_r2_fric_only.append(r2_score(y_te, y_pred_f))
            else:
                cv_r2_fric_only.append(np.nan)

            # C only
            X_tr_c = X_tr[:, 0:1]
            X_te_c_ = X_te[:, 0:1]
            m_c_ = fit_ols(X_tr_c, y_tr)
            if m_c_ is not None:
                X_te_cc = sm.add_constant(X_te_c_)
                y_pred_c = m_c_.predict(X_te_cc)
                cv_r2_c_only.append(r2_score(y_te, y_pred_c))
            else:
                cv_r2_c_only.append(np.nan)

    # Summarize
    cv_full = np.array(cv_r2_full)[~np.isnan(cv_r2_full)]
    cv_add = np.array(cv_r2_additive)[~np.isnan(cv_r2_additive)]
    cv_fric = np.array(cv_r2_fric_only)[~np.isnan(cv_r2_fric_only)]
    cv_c = np.array(cv_r2_c_only)[~np.isnan(cv_r2_c_only)]

    print(f"  Full model (C+Fr+C×Fr): mean R² = {np.mean(cv_full):.4f}  sd = {np.std(cv_full):.4f}")
    print(f"  Additive (C+Fr):        mean R² = {np.mean(cv_add):.4f}  sd = {np.std(cv_add):.4f}")
    print(f"  Friction only:          mean R² = {np.mean(cv_fric):.4f}  sd = {np.std(cv_fric):.4f}")
    print(f"  C only:                 mean R² = {np.mean(cv_c):.4f}    sd = {np.std(cv_c):.4f}")

    # Predictive gain from interaction
    gain = np.mean(cv_full) - np.mean(cv_add)
    print(f"  Predictive gain (interaction) = {gain:+.4f}")

    # Fraction of folds where interaction beats additive
    beats = 0
    total = 0
    for i in range(len(cv_r2_full)):
        if not np.isnan(cv_r2_full[i]) and not np.isnan(cv_r2_additive[i]):
            if cv_r2_full[i] > cv_r2_additive[i]:
                beats += 1
            total += 1
    print(f"  Interaction beats additive in {beats}/{total} folds ({100*beats/max(total,1):.1f}%)")

    # Sign direction in CV
    sigs = [s for s in cv_interaction_sign if s is not None]
    if sigs:
        print(f"  Interaction positive in {sum(sigs)}/{len(sigs)} CV fits ({100*sum(sigs)/len(sigs):.1f}%)")

    # ─── 4. Train/Test Split ───
    print(f"\n  ── 4. Train/Test Split (70/30, repeated 200x) ──")

    n_splits = 200
    test_size = 0.3
    test_n = max(1, int(n_good * test_size))

    split_full_r2 = []
    split_add_r2 = []
    split_int_sign = []
    split_int_pvals = []
    split_int_se = []

    for rep in range(n_splits):
        perm = RNG.permutation(n_good)
        split_point = int(n_good * test_size)
        tr_idx = perm[split_point:]
        te_idx = perm[:split_point]

        X_tr, X_te = X_full[tr_idx], X_full[te_idx]
        y_tr, y_te = y_vec[good][tr_idx], y_vec[good][te_idx]

        # Full
        m_tr = fit_ols(X_tr, y_tr)
        if m_tr is not None:
            X_te_c = sm.add_constant(X_te)
            y_pred = m_tr.predict(X_te_c)
            split_full_r2.append(r2_score(y_te, y_pred))
            split_int_sign.append(m_tr.params[3] > 0)
        else:
            split_full_r2.append(np.nan)

        # Additive
        m_tr_add = fit_ols(X_tr[:, :2], y_tr)
        if m_tr_add is not None:
            X_te_ac = sm.add_constant(X_te[:, :2])
            y_pred_add = m_tr_add.predict(X_te_ac)
            split_add_r2.append(r2_score(y_te, y_pred_add))
        else:
            split_add_r2.append(np.nan)

    sf = np.array(split_full_r2)[~np.isnan(split_full_r2)]
    sa = np.array(split_add_r2)[~np.isnan(split_add_r2)]

    print(f"  Full model (C+Fr+C×Fr): mean R² = {np.mean(sf):.4f}  sd = {np.std(sf):.4f}")
    print(f"  Additive (C+Fr):        mean R² = {np.mean(sa):.4f}  sd = {np.std(sa):.4f}")
    print(f"  Predictive gain from interaction = {np.mean(sf) - np.mean(sa):+.4f}")

    # Fraction where full beats additive
    min_len = min(len(sf), len(sa))
    beats_tt = sum(sf[i] > sa[i] for i in range(min_len))
    print(f"  Interaction beats additive in {beats_tt}/{min_len} splits ({100*beats_tt/max(min_len,1):.1f}%)")

    sigs_tt = [s for s in split_int_sign if s is not None]
    if sigs_tt:
        print(f"  Interaction positive in {sum(sigs_tt)}/{len(sigs_tt)} train fits ({100*sum(sigs_tt)/len(sigs_tt):.1f}%)")


# ═══════════════════════════════════════════════════════════════════
# SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  NUMERICAL SUMMARY")
print("=" * 78)

print(f"""
FULL-SAMPLE REFERENCE:
  Interaction survives in {'all 3' if sum(not np.isnan(y[:,i]).all() for i in range(3)) else ''} targets.

CONDITIONAL INFORMATION:
  ΔR² (C given friction): quantifies unique C contribution.
  ΔR² (friction given C): quantifies unique friction contribution.
  Permutation importance: fraction of R² lost when each predictor is shuffled.
  LOCO: R² drop when each predictor is removed.

INTERACTION STABILITY:
  Bootstrap: 95% CI of interaction coefficient, sign stability.
  k-fold CV: mean R² across folds, comparison to additive.
  Train/Test split: repeated held-out R².

See RD-014 documents for interpretation.
""")
