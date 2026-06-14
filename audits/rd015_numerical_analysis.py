"""RD-015 Numerical Analysis: Residual Information, Threshold, Functional Forms.

Three priorities, one script:
  P1: Residual(C | friction) → predict recovery
  P2: Threshold model comparison
  P3: Alternative functional forms (quadratic, GAM, tree)
"""

import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.tree import DecisionTreeRegressor
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
        row[k] = np.nan if v is None else v
    rows.append(row)

X_names = ["pre_C", "friction", "msd", "rms_velocity", "neighbor_turnover", "packing_var"]
y_names = ["dip", "restoration", "tau_rec"]
n = len(rows)

X = np.full((n, len(X_names)), np.nan)
y = np.full((n, len(y_names)), np.nan)
for i, r in enumerate(rows):
    for j, name in enumerate(X_names):
        X[i, j] = r.get(name, np.nan)
    for j, name in enumerate(y_names):
        y[i, j] = r.get(name, np.nan)

# Standardize
means = np.nanmean(X, axis=0); stds = np.nanstd(X, axis=0); stds[stds == 0] = 1.0
X_z = (X - means) / stds
ymeans = np.nanmean(y, axis=0); ystds = np.nanstd(y, axis=0); ystds[ystds == 0] = 1.0
y_z = (y - ymeans) / ystds

def fit_ols(X_in, y_in, add_const=True):
    good = ~(np.isnan(y_in) | np.any(np.isnan(X_in), axis=1))
    if good.sum() < X_in.shape[1] + 2:
        return None, good
    X_use = sm.add_constant(X_in[good]) if add_const else X_in[good]
    y_use = y_in[good]
    try:
        m = sm.OLS(y_use, X_use).fit()
        return m, good
    except Exception:
        return None, good

def cv_score(X_in, y_in, k=5, n_repeat=100):
    """Repeated k-fold CV, return mean R² and sd."""
    scores = []
    for rep in range(n_repeat):
        kf = KFold(n_splits=k, shuffle=True, random_state=rep)
        for tr_idx, te_idx in kf.split(X_in):
            X_tr, X_te = X_in[tr_idx], X_in[te_idx]
            y_tr, y_te = y_in[tr_idx], y_in[te_idx]
            m, _ = fit_ols(X_tr, y_tr)
            if m is not None:
                X_te_c = sm.add_constant(X_te)
                y_pred = m.predict(X_te_c)
                scores.append(r2_score(y_te, y_pred))
    scores = np.array(scores)
    scores = scores[~np.isnan(scores)]
    return np.mean(scores), np.std(scores) if len(scores) > 0 else (np.nan, np.nan)


# ═══════════════════════════════════════════════════════════════════
# P1: RESIDUAL INFORMATION AUDIT
# ═══════════════════════════════════════════════════════════════════

print("=" * 78)
print("  P1: RESIDUAL INFORMATION AUDIT — C | friction")
print("=" * 78)

# Regress C on friction
X_c_on_fric = sm.add_constant(X_z[:, 1])  # friction
y_c = X_z[:, 0]  # pre_C
good_c = ~(np.isnan(y_c) | np.any(np.isnan(X_c_on_fric), axis=1))
m_c_fric = sm.OLS(y_c[good_c], X_c_on_fric[good_c]).fit()
print(f"\n  C ~ Friction: R² = {m_c_fric.rsquared:.4f}")
print(f"  Intercept: {m_c_fric.params[0]:+.4f}, Friction coef: {m_c_fric.params[1]:+.4f}")

# Residuals
residual_c = np.full(n, np.nan)
residual_c[good_c] = m_c_fric.resid

# Test residual(C) on each target
for yi, yname in enumerate(y_names):
    y_vec = y_z[good_c, yi] if yi < y_z.shape[1] else None
    if y_vec is None or np.isnan(y_vec).all():
        continue

    # Residual(C) alone
    resid_valid = good_c & ~np.isnan(y_z[:, yi])
    if resid_valid.sum() < 5:
        continue

    m_res, _ = fit_ols(residual_c[resid_valid].reshape(-1, 1), y_z[resid_valid, yi])
    if m_res is not None:
        r2_res = m_res.rsquared
        p_res = m_res.pvalues[1] if len(m_res.pvalues) > 1 else 1.0
        t_res = m_res.tvalues[1] if len(m_res.tvalues) > 1 else 0.0
        coef_res = m_res.params[1] if len(m_res.params) > 1 else 0.0
        print(f"\n  Target: {yname}")
        print(f"  Residual(C) | friction:  R² = {r2_res:.4f},  coef = {coef_res:+.4f},  t = {t_res:+.2f},  p = {p_res:.4e}")
    else:
        print(f"\n  Target: {yname} — could not fit")

    # Compare: raw C vs residual(C) on this target
    m_raw_c, _ = fit_ols(X_z[resid_valid, 0:1], y_z[resid_valid, yi])
    if m_res is not None and m_raw_c is not None:
        print(f"  Raw C alone:          R² = {m_raw_c.rsquared:.4f}")
        print(f"  Residual(C) alone:    R² = {r2_res:.4f}")
        print(f"  Fraction retained:    {r2_res / max(m_raw_c.rsquared, 1e-10):.3f}")

    # Residual(C) + friction vs friction alone
    X_fric = X_z[resid_valid, 1:2]
    X_fric_res = np.column_stack([X_z[resid_valid, 1], residual_c[resid_valid]])
    m_fric, _ = fit_ols(X_fric, y_z[resid_valid, yi])
    m_fric_res, _ = fit_ols(X_fric_res, y_z[resid_valid, yi])
    if m_fric is not None and m_fric_res is not None:
        r2_gain = m_fric_res.rsquared - m_fric.rsquared
        print(f"  Residual(C) given friction: ΔR² = {r2_gain:+>.4f}")
        print(f"    Friction alone:   R² = {m_fric.rsquared:.4f}")
        print(f"    Friction + Res(C): R² = {m_fric_res.rsquared:.4f}")

    # Residual(C) + friction + interaction vs friction + interaction
    X_fric_int = np.column_stack([X_z[resid_valid, 1], X_z[resid_valid, 0] * X_z[resid_valid, 1]])
    X_fric_int_res = np.column_stack([X_z[resid_valid, 1], X_z[resid_valid, 0] * X_z[resid_valid, 1], residual_c[resid_valid]])
    m_fric_int, _ = fit_ols(X_fric_int, y_z[resid_valid, yi])
    m_fric_int_res, _ = fit_ols(X_fric_int_res, y_z[resid_valid, yi])
    if m_fric_int is not None and m_fric_int_res is not None:
        r2_gain2 = m_fric_int_res.rsquared - m_fric_int.rsquared
        print(f"  Residual(C) given friction + interaction: ΔR² = {r2_gain2:+>.4f}")
        print(f"    Friction + Int:   R² = {m_fric_int.rsquared:.4f}")
        print(f"    Fric + Int + Res: R² = {m_fric_int_res.rsquared:.4f}")

# Breakdown: what fraction of C's predictive power is independent of friction?
print(f"\n  ── C Predictive Power Decomposition ──")
for yi, yname in enumerate(y_names):
    y_vec = y_z[:, yi]
    good = ~(np.isnan(X_z[:, 0]) | np.isnan(X_z[:, 1]) | np.isnan(y_vec))
    if good.sum() < 5:
        continue

    # C alone
    m_c, _ = fit_ols(X_z[good, 0:1], y_vec[good])
    # friction alone
    m_f, _ = fit_ols(X_z[good, 1:2], y_vec[good])
    # residual(C) alone
    res_c_good = residual_c[good]
    m_rc, _ = fit_ols(res_c_good.reshape(-1, 1), y_vec[good])

    if m_c is not None and m_f is not None and m_rc is not None:
        total_c = m_c.rsquared
        unique_c = m_rc.rsquared
        shared_cf = m_f.rsquared  # friction captures some of what C captures
        # actually, shared = friction R² (since C and friction overlap)
        # unique = residual R²
        # shared = total C R² - unique C R²
        shared = total_c - unique_c
        print(f"  {yname:>15s}: C total R²={total_c:.4f}  |  unique to C (residual)={unique_c:.4f}  |  shared with friction={shared:.4f}")
        print(f"                     fraction unique = {unique_c/max(total_c,1e-10):.3f},  fraction shared = {shared/max(total_c,1e-10):.3f}")


# ═══════════════════════════════════════════════════════════════════
# P2: THRESHOLD VS INTERACTION
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  P2: THRESHOLD VS INTERACTION MODEL COMPARISON")
print("=" * 78)

# Find optimal friction threshold via grid search
fric_vals = X_z[:, 1]
fric_vals_orig = X[:, 1]
thresholds = sorted(set(fric_vals_orig[~np.isnan(fric_vals_orig)]))
thresholds = [t for t in thresholds if 0.05 < t < 0.8]

for yi, yname in enumerate(y_names):
    y_vec = y_z[:, yi]
    good = ~(np.isnan(X_z[:, 0]) | np.isnan(X_z[:, 1]) | np.isnan(y_vec))
    if good.sum() < 10:
        continue

    print(f"\n  Target: {yname}")

    # Models to compare:
    models = {}

    # 1. Null
    null_pred = np.full(good.sum(), np.mean(y_vec[good]))
    models["Null (mean)"] = {"R²": 0.0, "AIC": np.nan, "BIC": np.nan, "k": 1}

    # 2. Friction only
    m, _ = fit_ols(X_z[good, 1:2], y_vec[good])
    if m is not None:
        models["Friction (linear)"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic, "k": 2}

    # 3. C only
    m, _ = fit_ols(X_z[good, 0:1], y_vec[good])
    if m is not None:
        models["C (linear)"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic, "k": 2}

    # 4. Additive (C + friction)
    m, _ = fit_ols(X_z[good][:, [0, 1]], y_vec[good])
    if m is not None:
        models["Additive (C+Fr)"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic, "k": 3}

    # 5. Full interaction (C + Fr + C×Fr)
    X_int = np.column_stack([X_z[good, 0], X_z[good, 1], X_z[good, 0] * X_z[good, 1]])
    m, _ = fit_ols(X_int, y_vec[good])
    if m is not None:
        models["Interaction (C+Fr+C×Fr)"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic, "k": 4}

    # 6. Threshold model: find optimal friction threshold
    best_threshold = None
    best_threshold_r2 = -1e10
    threshold_results = []

    f_good = X[good, 1]
    c_good = X[good, 0]
    yg = y_vec[good]

    for thresh in thresholds:
        # Dummy: low friction (≤ threshold) vs high friction (> threshold)
        low = (f_good <= thresh).astype(float)
        # Model: C + low_dummy + C×low_dummy (piecewise linear)
        X_th = np.column_stack([c_good, low, c_good * low])
        X_th_z = (X_th - np.nanmean(X_th, axis=0)) / np.maximum(np.nanstd(X_th, axis=0), 1e-10)
        m_th, g2 = fit_ols(X_th_z, yg)
        if m_th is not None:
            threshold_results.append((thresh, m_th.rsquared, m_th.aic, m_th.bic))

    if threshold_results:
        best_threshold, best_r2, best_aic, best_bic = max(threshold_results, key=lambda x: x[1])
        models[f"Threshold={best_threshold:.2f} (piecewise C)"] = {"R²": best_r2, "AIC": best_aic, "BIC": best_bic, "k": 4}

        print(f"\n  Threshold grid search:")
        for th, r2, aic, bic in sorted(threshold_results, key=lambda x: x[0]):
            marker = " ← best" if th == best_threshold else ""
            print(f"    threshold={th:.2f}:  R²={r2:.4f}  AIC={aic:.1f}  BIC={bic:.1f}{marker}")

    # 7. Simple threshold: low vs high (binary, no C)
    best_thresh_simple = None
    best_simple_r2 = -1e10
    for thresh in thresholds:
        low = (f_good <= thresh).astype(float)
        X_s = low.reshape(-1, 1)
        X_s_z = (X_s - np.mean(X_s)) / np.maximum(np.std(X_s), 1e-10)
        m_s, _ = fit_ols(X_s_z, yg)
        if m_s is not None and m_s.rsquared > best_simple_r2:
            best_simple_r2 = m_s.rsquared
            best_thresh_simple = thresh

    if best_thresh_simple is not None:
        models[f"Simple threshold={best_thresh_simple:.2f} (binary only)"] = {"R²": best_simple_r2, "AIC": np.nan, "BIC": np.nan, "k": 2}

    # 8. Piecewise C + friction (separate slopes per regime)
    if best_threshold is not None:
        low = (f_good <= best_threshold).astype(float)
        # C in low regime, C in high regime, friction
        C_low = c_good * low
        C_high = c_good * (1 - low)
        X_pw = np.column_stack([C_low, C_high, f_good])
        X_pw_z = (X_pw - np.nanmean(X_pw, axis=0)) / np.maximum(np.nanstd(X_pw, axis=0), 1e-10)
        m_pw, _ = fit_ols(X_pw_z, yg)
        if m_pw is not None:
            models[f"Piecewise C×regime (th={best_threshold:.2f})"] = {"R²": m_pw.rsquared, "AIC": m_pw.aic, "BIC": m_pw.bic, "k": 4}

    # Print comparison table
    print(f"\n  Model Comparison:")
    print(f"  {'Model':>40s}  {'R²':>8s}  {'AIC':>10s}  {'BIC':>10s}  {'k':>3s}")
    print(f"  {'-' * 75}")
    best_by_aic = min(models.items(), key=lambda x: x[1]["AIC"] if not np.isnan(x[1]["AIC"]) else 1e10)
    best_by_r2 = max(models.items(), key=lambda x: x[1]["R²"])
    def fmt_val(v, fmt=".1f"):
        return f"{v:{fmt}}" if not (isinstance(v, float) and np.isnan(v)) else "N/A"

    for name, vals in sorted(models.items(), key=lambda x: x[1]["R²"], reverse=True):
        marker = ""
        if name == best_by_aic[0]:
            marker = " ← best AIC"
        elif name == best_by_r2[0]:
            marker = " ← best R²"
        print(f"  {name:>40s}  {vals['R²']:>8.4f}  {fmt_val(vals['AIC']):>10s}  {fmt_val(vals['BIC']):>10s}  {vals['k']:>3d}{marker}")

    # CV comparison for best models
    print(f"\n  CV comparison (k=5, 100x repeated):")
    X_int_full = np.column_stack([X_z[good, 0], X_z[good, 1], X_z[good, 0] * X_z[good, 1]])
    cv_int_mean, cv_int_sd = cv_score(X_int_full, yg)
    print(f"  Interaction model:  mean R² = {cv_int_mean:.4f} (sd={cv_int_sd:.4f})")

    X_add = X_z[good][:, [0, 1]]
    cv_add_mean, cv_add_sd = cv_score(X_add, yg)
    print(f"  Additive model:     mean R² = {cv_add_mean:.4f} (sd={cv_add_sd:.4f})")

    if best_threshold is not None:
        f_g = f_good
        th_dummy = (f_g <= best_threshold).astype(float)
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_th_cv_scaled = scaler.fit_transform(np.column_stack([c_good, th_dummy]))
        # Use direct sklearn CV to avoid add_constant dimension mismatch
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import cross_val_score
        scores = cross_val_score(LinearRegression(), X_th_cv_scaled, yg, cv=5)
        cv_th_mean = np.mean(scores)
        cv_th_sd = np.std(scores)
        print(f"  Threshold model:    mean R² = {cv_th_mean:.4f} (sd={cv_th_sd:.4f})")
        # Also do interaction model with sklearn for comparison
        X_int_scaled = scaler.fit_transform(np.column_stack([c_good, f_good, c_good * f_good]))
        scores_int = cross_val_score(LinearRegression(), X_int_scaled, yg, cv=5)
        print(f"  Interaction (sklearn): mean R² = {np.mean(scores_int):.4f} (sd={np.std(scores_int):.4f})")


# ═══════════════════════════════════════════════════════════════════
# P3: FUNCTIONAL FORM COMPETITION
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  P3: FUNCTIONAL FORM COMPETITION")
print("=" * 78)

for yi, yname in enumerate(y_names):
    y_vec = y_z[:, yi]
    good = ~(np.isnan(X_z[:, 0]) | np.isnan(X_z[:, 1]) | np.isnan(y_vec))
    if good.sum() < 10:
        continue

    n_g = good.sum()
    print(f"\n  Target: {yname}  (n={n_g})")
    print(f"  {'Model':>40s}  {'R²':>8s}  {'AIC':>10s}  {'BIC':>10s}")
    print(f"  {'-' * 72}")

    forms = {}

    # 1. Null
    forms["Null (mean)"] = {"R²": 0.0, "AIC": np.nan, "BIC": np.nan}

    # 2. Friction linear
    m, _ = fit_ols(X_z[good, 1:2], y_vec[good])
    if m: forms["Friction (linear)"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic}

    # 3. C linear
    m, _ = fit_ols(X_z[good, 0:1], y_vec[good])
    if m: forms["C (linear)"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic}

    # 4. Additive
    m, _ = fit_ols(X_z[good][:, [0, 1]], y_vec[good])
    if m: forms["Additive (C+Fr)"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic}

    # 5. Interaction
    X_int = np.column_stack([X_z[good, 0], X_z[good, 1], X_z[good, 0] * X_z[good, 1]])
    m, _ = fit_ols(X_int, y_vec[good])
    if m: forms["Interaction (C+Fr+C×Fr)"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic}

    # 6. Quadratic friction: friction + friction²
    f_sq = X_z[good, 1] ** 2
    X_qf = np.column_stack([X_z[good, 1], (X_z[good, 1]**2)])
    m, _ = fit_ols(X_qf, y_vec[good])
    if m: forms["Quadratic friction (Fr+Fr²)"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic}

    # 7. Quadratic C: C + C²
    X_qc = np.column_stack([X_z[good, 0], X_z[good, 0]**2])
    m, _ = fit_ols(X_qc, y_vec[good])
    if m: forms["Quadratic C (C+C²)"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic}

    # 8. Quadratic both: C + C² + Fr + Fr²
    X_qb = np.column_stack([X_z[good, 0], X_z[good, 0]**2, X_z[good, 1], X_z[good, 1]**2])
    m, _ = fit_ols(X_qb, y_vec[good])
    if m: forms["Both quadratic (C+C²+Fr+Fr²)"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic}

    # 9. C + friction + friction² (interaction alternative)
    X_cf2 = np.column_stack([X_z[good, 0], X_z[good, 1], X_z[good, 1]**2])
    m, _ = fit_ols(X_cf2, y_vec[good])
    if m: forms["C + Fr + Fr²"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic}

    # 10. C + friction + C² (alternative interaction)
    X_c2f = np.column_stack([X_z[good, 0], X_z[good, 1], X_z[good, 0]**2])
    m, _ = fit_ols(X_c2f, y_vec[good])
    if m: forms["C + Fr + C²"] = {"R²": m.rsquared, "AIC": m.aic, "BIC": m.bic}

    # 11. Best threshold (from P2)
    f_good = X[good, 1]
    c_good = X[good, 0]
    yg = y_vec[good]
    thresholds_pts = sorted(set(f_good[~np.isnan(f_good)]))
    thresholds_pts = [t for t in thresholds_pts if 0.05 < t < 0.8]
    best_r2_t = -1
    best_th_t = None
    for th in thresholds_pts:
        low = (f_good <= th).astype(float)
        X_t = np.column_stack([c_good, low, c_good * low])
        X_tz = (X_t - np.nanmean(X_t, axis=0)) / np.maximum(np.nanstd(X_t, axis=0), 1e-10)
        mt, _ = fit_ols(X_tz, yg)
        if mt is not None and mt.rsquared > best_r2_t:
            best_r2_t = mt.rsquared
            best_th_t = th
    if best_th_t is not None:
        forms[f"Threshold (best={best_th_t:.2f})"] = {"R²": best_r2_t, "AIC": np.nan, "BIC": np.nan}

    # 12. Decision tree (max_depth=2)
    X_tree = X_z[good][:, [0, 1]]
    y_tree = yg
    tree = DecisionTreeRegressor(max_depth=2, random_state=42)
    tree.fit(X_tree, y_tree)
    y_pred_tree = tree.predict(X_tree)
    tree_r2 = r2_score(y_tree, y_pred_tree)
    forms["Decision tree (depth=2)"] = {"R²": tree_r2, "AIC": np.nan, "BIC": np.nan}

    # Tree with depth 3
    tree3 = DecisionTreeRegressor(max_depth=3, random_state=42)
    tree3.fit(X_tree, y_tree)
    y_pred_tree3 = tree3.predict(X_tree)
    tree3_r2 = r2_score(y_tree, y_pred_tree3)
    forms["Decision tree (depth=3)"] = {"R²": tree3_r2, "AIC": np.nan, "BIC": np.nan}

    # Print sorted by R²
    def fmt_val(v, fmt=".1f"):
        return f"{v:{fmt}}" if not (isinstance(v, float) and np.isnan(v)) else "N/A"
    for name, vals in sorted(forms.items(), key=lambda x: x[1]["R²"], reverse=True):
        print(f"  {name:>40s}  {vals['R²']:>8.4f}  {fmt_val(vals['AIC']):>10s}  {fmt_val(vals['BIC']):>10s}")

    # Key comparison: interaction vs C+Fr+Fr²
    print(f"\n  ── Key comparisons ──")
    if "Interaction (C+Fr+C×Fr)" in forms and "C + Fr + Fr²" in forms:
        int_r2 = forms["Interaction (C+Fr+C×Fr)"]["R²"]
        fr2_r2 = forms["C + Fr + Fr²"]["R²"]
        diff = int_r2 - fr2_r2
        print(f"  Interaction vs C+Fr+Fr²: ΔR² = {diff:+.4f}  (interaction win)" if diff > 0 else
              f"  Interaction vs C+Fr+Fr²: ΔR² = {diff:+.4f}  (Fr² win)" if diff < 0 else
              f"  Interaction vs C+Fr+Fr²: ΔR² = {diff:.4f}  (tie)")

    if "Interaction (C+Fr+C×Fr)" in forms and "Both quadratic (C+C²+Fr+Fr²)" in forms:
        int_r2 = forms["Interaction (C+Fr+C×Fr)"]["R²"]
        both_q = forms["Both quadratic (C+C²+Fr+Fr²)"]["R²"]
        print(f"  Interaction vs both quadratic: ΔR² = {int_r2 - both_q:+.4f}")

    if "Interaction (C+Fr+C×Fr)" in forms and "Threshold (best=..." in [k for k in forms.keys() if "Threshold" in k]:
        # find threshold model
        th_name = [k for k in forms.keys() if "Threshold" in k]
        if th_name:
            int_r2 = forms["Interaction (C+Fr+C×Fr)"]["R²"]
            th_r2 = forms[th_name[0]]["R²"]
            print(f"  Interaction vs {th_name[0]}: ΔR² = {int_r2 - th_r2:+.4f}")

# ─── Summary ───

print("\n" + "=" * 78)
print("  SUMMARY")
print("=" * 78)
print("""
P1: If residual(C | friction) predicts recovery → C contains genuine state info
P2: If threshold model matches or beats interaction → interaction may be threshold artifact
P3: If quadratic/alternative forms match interaction → C not uniquely special
""")
