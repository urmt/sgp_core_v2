#!/usr/bin/env python3
"""Collinearity diagnostics — fixed."""
import numpy as np
import json
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

with open("/home/student/sgp_core_v2/coherence-benchmark/results/t901_ensemble.json") as f:
    raw = json.load(f)

rows = []
for r in raw:
    rr = {}
    for k, v in r.items():
        if v is None:
            rr[k] = np.nan
        elif k in ("friction", "rep", "tau_rec"):
            rr[k] = v
        else:
            rr[k] = float(v)
    rows.append(rr)

vars_of_interest = ["pre_C", "friction", "msd", "rms_velocity", "neighbor_turnover"]
N = len(rows)
X = np.column_stack([[r[v] for r in rows] for v in vars_of_interest])
valid = ~np.any(np.isnan(X), axis=1)
Xclean = X[valid]
print(f"  {N} rows, {valid.sum()} clean")

# ─── 1. Correlations ───
print(f"\n{'='*60}")
print("  1. PEARSON CORRELATIONS")
print(f"{'='*60}")
corr = np.corrcoef(Xclean.T)
header = "".join(f"{v:>16s}" for v in vars_of_interest)
print(f"\n{'':>20s}{header}")
for i, vi in enumerate(vars_of_interest):
    line = f"{vi:>20s}" + "".join(f"{corr[i,j]:>16.4f}" for j in range(i+1))
    print(line)

# ─── 2. VIF ───
print(f"\n{'='*60}")
print("  2. VARIANCE INFLATION FACTOR")
print(f"{'='*60}")
for i, v in enumerate(vars_of_interest):
    vif = variance_inflation_factor(Xclean, i)
    print(f"  {v:>20s}: VIF = {vif:.2f}")

# ─── 3. Partial correlations ───
print(f"\n{'='*60}")
print("  3. PARTIAL CORRELATIONS")
print(f"{'='*60}")
for i in range(len(vars_of_interest)):
    for j in range(i+1, len(vars_of_interest)):
        others = [k for k in range(len(vars_of_interest)) if k not in (i, j)]
        Xo = sm.add_constant(Xclean[:, others])
        ri = sm.OLS(Xclean[:, i], Xo).fit().resid
        rj = sm.OLS(Xclean[:, j], Xo).fit().resid
        rp = np.corrcoef(ri, rj)[0,1]
        print(f"  {vars_of_interest[i]:>20s} × {vars_of_interest[j]:<20s}:  r_partial = {rp:+.4f}")

# ─── 4. Leave-one-variable-out sensitivity ───
print(f"\n{'='*60}")
print("  4. LEAVE-ONE-VARIABLE-OUT SENSITIVITY")
print(f"{'='*60}")

recovery_targets = {"dip": "ΔC", "tau_rec": "τ_rec", "restoration": "Restoration"}
mobility_vars = ["msd", "rms_velocity", "neighbor_turnover"]

def z(arr):
    arr = np.asarray(arr, dtype=float)
    m, s = np.nanmean(arr), np.nanstd(arr)
    return (arr - m) / max(s, 1e-10)

for target, tname in recovery_targets.items():
    y_all = np.array([r[target] for r in rows], dtype=float)
    yv = ~np.isnan(y_all)
    if yv.sum() < 10:
        continue
    y = y_all[yv]
    c = Xclean[:, 0][yv]
    f = Xclean[:, 1][yv]
    cf = c * f
    
    yz, cz, fz, cfz = z(y), z(c), z(f), z(cf)
    
    print(f"\n  Target: {tname} (n={yv.sum()})")
    print(f"  {'Model':>40s}  {'R²':>8s}  {'AIC':>10s}  {'Int-p':>10s}")
    print(f"  {'-'*70}")
    
    models = {}
    
    # C only
    m = sm.OLS(yz, sm.add_constant(cz)).fit()
    models["C only"] = (m.rsquared, m.aic, None)
    
    # Friction only
    m = sm.OLS(yz, sm.add_constant(fz)).fit()
    models["Friction only"] = (m.rsquared, m.aic, None)
    
    # C + F
    m = sm.OLS(yz, sm.add_constant(np.column_stack([cz, fz]))).fit()
    models["C + F"] = (m.rsquared, m.aic, None)
    
    # C × F (interaction)
    m = sm.OLS(yz, sm.add_constant(np.column_stack([cz, fz, cfz]))).fit()
    models["C × F (interaction)"] = (m.rsquared, m.aic, m.pvalues[-1])
    base_p_inter = m.pvalues[-1]
    
    # Add each mobility proxy
    for mob_var in mobility_vars:
        idx = vars_of_interest.index(mob_var)
        mv = Xclean[:, idx][yv]
        mvz = z(mv)
        
        # C × F + mobility
        X4 = sm.add_constant(np.column_stack([cz, fz, cfz, mvz]))
        m4 = sm.OLS(yz, X4).fit()
        models[f"C×F + {mob_var}"] = (m4.rsquared, m4.aic, m4.pvalues[-2])
        
        # C + F + mobility (no interaction)
        X5 = sm.add_constant(np.column_stack([cz, fz, mvz]))
        m5 = sm.OLS(yz, X5).fit()
        models[f"C+F + {mob_var} (no inter)"] = (m5.rsquared, m5.aic, None)
    
    for mname, (r2, aic, pip) in models.items():
        pp = f"{pip:>10.6f}" if pip is not None else "  —"
        print(f"  {mname:>40s}  {r2:>8.4f}  {aic:>10.1f}  {pp}")

    # Interaction survival check
    print(f"\n  >>> Interaction survival with mobility covariates:")
    for mob_var in mobility_vars:
        idx = vars_of_interest.index(mob_var)
        mv = Xclean[:, idx][yv]
        mvz = z(mv)
        X4 = sm.add_constant(np.column_stack([cz, fz, cfz, mvz]))
        m4 = sm.OLS(yz, X4).fit()
        pi = m4.pvalues[-2]
        pm = m4.pvalues[-1]
        survives = "SURVIVES" if pi < 0.05 else "DROPS OUT"
        print(f"    {mob_var:>20s}:  interaction p = {pi:.6f}  ({survives})  |  mobility p = {pm:.6f}")
    print(f"    {'Baseline (no mobility)':>20s}:  interaction p = {base_p_inter:.6f}")

print(f"\n{'='*60}")
print("  5. KEY FINDINGS")
print(f"{'='*60}")

c_f_r = corr[0,1]
print(f"""
  Correlations:
    C × friction:          r = {c_f_r:.4f}
    C × MSD:               r = {corr[0,2]:.4f}
    C × RMS velocity:      r = {corr[0,3]:.4f}
    C × turnover:          r = {corr[0,4]:.4f}
    Friction × MSD:        r = {corr[1,2]:.4f}
    Friction × RMS vel:    r = {corr[1,3]:.4f}
    MSD × RMS velocity:    r = {corr[2,3]:.4f}

  VIF:
    pre_C:         {variance_inflation_factor(Xclean, 0):.1f}
    friction:      {variance_inflation_factor(Xclean, 1):.1f}
    msd:           {variance_inflation_factor(Xclean, 2):.1f}
    rms_velocity:  {variance_inflation_factor(Xclean, 3):.1f}
    turnover:      {variance_inflation_factor(Xclean, 4):.1f}

  Note: The extremely high VIF for rms_velocity (>>10) is due to
  multicollinearity with MSD (r = 0.91). These two variables contain
  nearly the same information. They should NOT be used together.
""")
