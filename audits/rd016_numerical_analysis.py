"""RD-016 Numerical Analysis: Nested Models, Residual-C Correlates, Level Leverage.

P1: Nested model hierarchy (interaction vs Fr²)
P2: Residual(C) correlates with mobility/structural descriptors
P3: Leave-one-friction-level-out + Cook's distance
"""

import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings("ignore")

RNG = np.random.default_rng(42)

with open("coherence-benchmark/results/t901_ensemble.json") as f:
    raw = json.load(f)

rows = []
for r in raw:
    row = {}
    for k, v in r.items():
        row[k] = np.nan if v is None else v
    rows.append(row)

n = len(rows)
X_names = ["pre_C", "friction", "msd", "rms_velocity", "neighbor_turnover", "packing_var"]
y_names = ["dip", "restoration", "tau_rec"]

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

def cv_score_sk(X_in, y_in, k=5, n_repeat=100):
    """Simple k-fold CV using sklearn LinearRegression."""
    scores = []
    for rep in range(n_repeat):
        kf = KFold(n_splits=k, shuffle=True, random_state=rep)
        for tr_idx, te_idx in kf.split(X_in):
            X_tr, X_te = X_in[tr_idx], X_in[te_idx]
            y_tr, y_te = y_in[tr_idx], y_in[te_idx]
            model = LinearRegression().fit(X_tr, y_tr)
            y_pred = model.predict(X_te)
            scores.append(r2_score(y_te, y_pred))
    return np.mean(scores), np.std(scores)


# ═══════════════════════════════════════════════════════════════════
# P1: NESTED MODEL HIERARCHY
# ═══════════════════════════════════════════════════════════════════

print("=" * 78)
print("  P1: NESTED MODEL HIERARCHY")
print("=" * 78)

nested_models = [
    ("1. C", lambda c, f, cf, f2, c2: c),
    ("2. Friction", lambda c, f, cf, f2, c2: f),
    ("3. C + Friction", lambda c, f, cf, f2, c2: np.column_stack([c, f])),
    ("4. C + Friction + Fr²", lambda c, f, cf, f2, c2: np.column_stack([c, f, f2])),
    ("5. C + Friction + C×Fr", lambda c, f, cf, f2, c2: np.column_stack([c, f, cf])),
    ("6. C + Friction + Fr² + C×Fr", lambda c, f, cf, f2, c2: np.column_stack([c, f, f2, cf])),
]

for yi, yname in enumerate(y_names):
    y_vec = y_z[:, yi]
    good = ~(np.isnan(X_z[:, 0]) | np.isnan(X_z[:, 1]) | np.isnan(y_vec))
    if good.sum() < 10:
        continue

    n_g = good.sum()
    c = X_z[good, 0:1]
    f = X_z[good, 1:2]
    cf = c * f
    f2 = f ** 2
    c2 = c ** 2

    print(f"\n  Target: {yname}  (n={n_g})")
    print(f"  {'Model':>35s}  {'R²':>8s}  {'Adj R²':>8s}  {'AIC':>10s}  {'BIC':>10s}  {'CV R²':>8s}")
    print(f"  {'-' * 85}")

    results = []
    for mname, builder in nested_models:
        X_m = builder(c, f, cf, f2, c2)
        m, _ = fit_ols(X_m, y_vec[good])
        if m is not None:
            r2 = m.rsquared
            adj_r2 = m.rsquared_adj
            aic = m.aic
            bic = m.bic
            cv_mean, cv_sd = cv_score_sk(X_m, y_vec[good])
            results.append((mname, r2, adj_r2, aic, bic, cv_mean, cv_sd))
        else:
            results.append((mname, 0, 0, 0, 0, 0, 0))

    for mname, r2, ar2, aic, bic, cv, cv_sd in results:
        print(f"  {mname:>35s}  {r2:>8.4f}  {ar2:>8.4f}  {aic:>10.1f}  {bic:>10.1f}  {cv:>8.4f}")

    # Key question: model 4 vs 5
    m4_r2 = results[3][1]  # C+Fr+Fr²
    m5_r2 = results[4][1]  # C+Fr+C×Fr
    m6_r2 = results[5][1]  # C+Fr+Fr²+C×Fr

    print(f"\n  ── Key Comparisons ──")
    print(f"  C+Fr+Fr² vs C+Fr+C×Fr: ΔR² = {m5_r2 - m4_r2:+.4f}")
    print(f"  C+Fr+Fr² vs C+Fr+Fr²+C×Fr: ΔR² = {m6_r2 - m4_r2:+.4f}")
    print(f"  C+Fr+C×Fr vs C+Fr+Fr²+C×Fr: ΔR² = {m6_r2 - m5_r2:+.4f}")

    # Partial F-test: does interaction add something beyond Fr²?
    m4, _ = fit_ols(np.column_stack([c, f, f2]), y_vec[good])
    m6, _ = fit_ols(np.column_stack([c, f, f2, cf]), y_vec[good])
    if m4 is not None and m6 is not None:
        # F = ((RSS_reduced - RSS_full) / df_diff) / (RSS_full / df_full)
        rss4 = np.sum(m4.resid ** 2)
        rss6 = np.sum(m6.resid ** 2)
        df_diff = m6.df_resid - m4.df_resid
        if rss6 > 0 and df_diff > 0:
            f_stat = ((rss4 - rss6) / df_diff) / (rss6 / m6.df_resid)
            p_val = 1 - sm.distributions.ferf2(f_stat, df_diff, m6.df_resid)
            print(f"  Partial F-test (C×Fr beyond Fr²): F = {f_stat:.3f}, p = {p_val:.4e}")


# ═══════════════════════════════════════════════════════════════════
# P2: RESIDUAL-C MECHANISM AUDIT
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  P2: RESIDUAL(C) MECHANISM — correlations with mobility/structural vars")
print("=" * 78)

# Recompute residuals
c_vals = X_z[:, 0]
f_vals = X_z[:, 1]
good_cf = ~(np.isnan(c_vals) | np.isnan(f_vals))
X_cf = sm.add_constant(f_vals[good_cf])
m_c_f = sm.OLS(c_vals[good_cf], X_cf).fit()
residual_c = np.full(n, np.nan)
residual_c[good_cf] = m_c_f.resid

mobility_names = ["msd", "rms_velocity", "neighbor_turnover", "packing_var"]
mob_idx = [2, 3, 4, 5]

print(f"\n  Correlation of residual(C) with mobility/structural variables:\n")
print(f"  {'Variable':>20s}  {'Pearson r':>10s}  {'p-value':>10s}  {'Spearman ρ':>10s}  {'Interpretation'}")
print(f"  {'-' * 70}")

for name, idx in zip(mobility_names, mob_idx):
    var = X_z[:, idx]
    valid = ~(np.isnan(residual_c) | np.isnan(var))
    if valid.sum() < 5:
        continue
    r_p, p_p = pearsonr(residual_c[valid], var[valid])
    r_s, p_s = spearmanr(residual_c[valid], var[valid])

    interp = ""
    if abs(r_p) < 0.1 and p_p > 0.05:
        interp = "no linear relationship"
    elif abs(r_p) < 0.3:
        interp = "weak"
    elif abs(r_p) < 0.5:
        interp = "moderate"
    else:
        interp = "strong"

    # find largest |r| among mobility vars
    all_rs = []
    for n2, i2 in zip(mobility_names, mob_idx):
        v = X_z[:, i2]
        mask_v = ~(np.isnan(residual_c) | np.isnan(v))
        if mask_v.sum() > 5:
            all_rs.append((abs(pearsonr(residual_c[mask_v], v[mask_v])[0]), n2))
    largest_r = max(all_rs, key=lambda x: x[0]) if all_rs else (0, "")
    flag = " ← largest" if name == largest_r[1] and abs(r_p) > 0.1 else ""
    print(f"  {name:>20s}  {r_p:>+10.4f}  {p_p:>10.4e}  {r_s:>+10.4f}  {interp}{flag}")

# Also correlate residual(C) with raw C
valid = ~np.isnan(residual_c) & ~np.isnan(c_vals)
r_raw, p_raw = pearsonr(residual_c[valid], c_vals[valid])
print(f"  {'Raw C (pre_C)':>20s}  {r_raw:>+10.4f}  {p_raw:>10.4e}  {'—':>10s}  {'by construction, ~sqrt(1 - R²(C~Fr))'}")

# Partial correlations: residual(C) vs recovery, controlling for mobility
print(f"\n  ── Partial: residual(C) vs recovery, controlling for mobility variables ──")
residual_std = (residual_c - np.nanmean(residual_c)) / np.nanstd(residual_c)

for yi, yname in enumerate(y_names):
    y_vec = y_z[:, yi]
    valid = ~(np.isnan(residual_std) | np.isnan(y_vec) | np.any(np.isnan(X_z[:, mob_idx]), axis=1))
    if valid.sum() < 10:
        continue

    # residual(C) alone
    m_rc, _ = fit_ols(residual_std[valid].reshape(-1, 1), y_vec[valid])
    r2_rc = m_rc.rsquared if m_rc is not None else 0

    # mobility + residual(C)
    X_mob_rc = np.column_stack([X_z[valid, i] for i in mob_idx] + [residual_std[valid]])
    m_mob_rc, _ = fit_ols(X_mob_rc, y_vec[valid])
    r2_mob_rc = m_mob_rc.rsquared if m_mob_rc is not None else 0

    # mobility only
    X_mob = np.column_stack([X_z[valid, i] for i in mob_idx])
    m_mob, _ = fit_ols(X_mob, y_vec[valid])
    r2_mob = m_mob.rsquared if m_mob is not None else 0

    print(f"  {yname:>15s}:  residual(C) alone R²={r2_rc:.4f},  mobility R²={r2_mob:.4f},  "
          f"mobility+res(C) R²={r2_mob_rc:.4f},  ΔR²(res|mob)={r2_mob_rc - r2_mob:+.4f}")


# ═══════════════════════════════════════════════════════════════════
# P3: LEVEL LEVERAGE ANALYSIS
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  P3: LEVEL LEVERAGE ANALYSIS — leave-one-friction-level-out")
print("=" * 78)

friction_levels = sorted(set(X[:, 1][~np.isnan(X[:, 1])]))
print(f"  Friction levels: {friction_levels}")
print(f"  N per level: {[(fl, sum(abs(X[:,1] - fl) < 0.01)) for fl in friction_levels]}")

for yi, yname in enumerate(y_names):
    y_vec = y_z[:, yi]
    print(f"\n  Target: {yname}")

    # Full model fits
    c = X_z[:, 0:1]
    f = X_z[:, 1:2]
    cf = c * f

    print(f"\n  {'Model':>35s}  {'R²':>8s}  {'Adj R²':>8s}  {'AIC':>10s}  {'BIC':>10s}")
    print(f"  {'-' * 75}")

    for mname, preds in [
        ("C+Fr", np.column_stack([c, f])),
        ("C+Fr+Fr²", np.column_stack([c, f, f**2])),
        ("C+Fr+C×Fr", np.column_stack([c, f, c*f])),
        ("C+Fr+Fr²+C×Fr", np.column_stack([c, f, f**2, c*f])),
    ]:
        full_valid = ~(np.isnan(y_vec) | np.any(np.isnan(preds), axis=1))
        m, _ = fit_ols(preds[full_valid], y_vec[full_valid])
        if m is not None:
            print(f"  {mname:>35s}  {m.rsquared:>8.4f}  {m.rsquared_adj:>8.4f}  {m.aic:>10.1f}  {m.bic:>10.1f}")

    # Leave-one-friction-level-out
    print(f"\n  ── Leave-One-Friction-Level-Out (Model: C+Fr+C×Fr) ──")
    print(f"  {'Left Out':>15s}  {'N train':>8s}  {'R² (full)':>10s}  {'R² (train)':>10s}  {'ΔR²':>8s}  {'Coef(Int)':>10s}  {'p(Int)':>10s}  {'Sign?':>6s}")
    print(f"  {'-' * 85}")

    full_valid = ~(np.isnan(y_vec) | np.isnan(c[:,0]) | np.isnan(f[:,0]))
    X_full = np.column_stack([c[full_valid], f[full_valid], cf[full_valid]])
    y_full = y_vec[full_valid]
    n_full = full_valid.sum()

    m_full, _ = fit_ols(X_full, y_full)
    full_r2 = m_full.rsquared if m_full is not None else 0
    full_int_coef = m_full.params[3] if m_full is not None and len(m_full.params) > 3 else 0
    full_int_p = m_full.pvalues[3] if m_full is not None and len(m_full.pvalues) > 3 else 1

    print(f"  {'(all data)':>15s}  {n_full:>8d}  {full_r2:>10.4f}  {full_r2:>10.4f}  {'—':>8s}  {full_int_coef:>+10.4f}  {full_int_p:>10.4e}  {'Yes' if full_int_p < 0.05 else 'No':>6s}")

    for fl in friction_levels:
        mask = np.abs(X[full_valid, 1] - fl) > 0.01  # exclude this level
        if mask.sum() < 10:
            continue

        X_loo = X_full[mask]
        y_loo = y_full[mask]
        m_loo, _ = fit_ols(X_loo, y_loo)

        if m_loo is not None:
            loo_r2 = m_loo.rsquared
            loo_int = m_loo.params[3] if len(m_loo.params) > 3 else 0
            loo_p = m_loo.pvalues[3] if len(m_loo.pvalues) > 3 else 1
            r2_change = loo_r2 - full_r2
            sig = "Yes" if loo_p < 0.05 else "No"
            print(f"  {fl:>15.2f}  {mask.sum():>8d}  {full_r2:>10.4f}  {loo_r2:>10.4f}  {r2_change:>+8.4f}  {loo_int:>+10.4f}  {loo_p:>10.4e}  {sig:>6s}")

    # Cook's distance for each friction level
    print(f"\n  ── Influence of each friction level (leave-one-out Δ coefficient) ──")
    print(f"  {'Level':>15s}  {'N':>6s}  {'Δ Int Coef':>12s}  {'Δ C Coef':>12s}  {'Δ Fr Coef':>12s}  {'Δ R²':>10s}")
    print(f"  {'-' * 70}")

    for fl in friction_levels:
        mask = np.abs(X[full_valid, 1] - fl) > 0.01
        if mask.sum() < 10:
            continue
        X_loo = X_full[mask]
        y_loo = y_full[mask]
        m_loo, _ = fit_ols(X_loo, y_loo)
        if m_loo is not None and m_full is not None:
            d_int = m_loo.params[3] - m_full.params[3] if len(m_loo.params) > 3 and len(m_full.params) > 3 else 0
            d_c = m_loo.params[1] - m_full.params[1] if len(m_loo.params) > 1 and len(m_full.params) > 1 else 0
            d_f = m_loo.params[2] - m_full.params[2] if len(m_loo.params) > 2 and len(m_full.params) > 2 else 0
            d_r2 = m_loo.rsquared - m_full.rsquared
            print(f"  {fl:>15.2f}  {mask.sum():>6d}  {d_int:>+12.4f}  {d_c:>+12.4f}  {d_f:>+12.4f}  {d_r2:>+10.4f}")

    # Also: remove endpoints only
    print(f"\n  ── Subset: remove both extremes (friction 0.05 and 0.80) ──")
    no_extremes = (np.abs(X[full_valid, 1] - 0.05) > 0.01) & (np.abs(X[full_valid, 1] - 0.80) > 0.01)
    if no_extremes.sum() > 10:
        X_ne = X_full[no_extremes]
        y_ne = y_full[no_extremes]
        m_ne, _ = fit_ols(X_ne, y_ne)
        if m_ne is not None:
            print(f"  N = {no_extremes.sum()} (vs {n_full} full)")
            print(f"  R² = {m_ne.rsquared:.4f} (full: {full_r2:.4f})")
            print(f"  Interaction coef = {m_ne.params[3]:+.4f}, p = {m_ne.pvalues[3]:.4e}")
            print(f"  Interaction significant? {'Yes' if m_ne.pvalues[3] < 0.05 else 'No'}")


print("\n" + "=" * 78)
print("  SUMMARY")
print("=" * 78)
print("""
P1: Does interaction matter after Fr² curvature?
  - Compare C+Fr+Fr² vs C+Fr+C×Fr vs C+Fr+Fr²+C×Fr
  - Partial F-test for interaction beyond Fr²

P2: What is residual(C)?
  - Correlate with mobility/structural variables
  - Partial: does residual(C) predict recovery beyond mobility?

P3: Is result driven by a single friction level?
  - Leave-one-level-out for each model
  - Cook's distance / coefficient sensitivity
  - Remove extremes
""")
