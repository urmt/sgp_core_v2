"""RD-019: Causal Model Analysis.

Fit 4 models per the director's specification:
  Model A: Recovery ~ Density
  Model B: Recovery ~ Density + Residual(C)
  Model C: Recovery ~ Residual(C)
  Model D: Recovery ~ Density + Residual(C) + Density×Residual(C)

Report coefficients, p-values, R², ΔR².

Also report structural validation and decision-rule assessment.
"""

import numpy as np
import json
import csv

SEP = "=" * 78


def load_data(path="coherence-benchmark/results/rd019_density_ensemble.json"):
    with open(path) as f:
        rows = json.load(f)
    return rows


def validate_density_manipulation(rows):
    """Confirm that box_width manipulation produced expected structural changes.

    Tests:
      - mean_nn_dist ~ 1/density should be positive
      - coordination_number ~ density should be positive
      - component_count ~ 1/density should be positive (more components when sparse)
    """
    print(f"\n{SEP}")
    print("  TASK 3: STRUCTURAL VALIDATION — Did density manipulation work?")
    print(f"{SEP}\n")

    bw_levels = sorted(set(r["box_width"] for r in rows))
    metrics = ["mean_nn_dist", "contact_count", "coordination_number",
               "component_count", "largest_component_size", "clustering_coefficient"]

    # Compute per-condition means
    cond_means = {}
    for bw in bw_levels:
        sub = [r for r in rows if r["box_width"] == bw]
        cond_means[bw] = {}
        for m in metrics:
            vals = [r[m] for r in sub if r[m] is not None and not (isinstance(r[m], float) and np.isnan(r[m]))]
            cond_means[bw][m] = float(np.mean(vals)) if vals else np.nan

    # Compute correlations with density
    densities = np.array([50.0 / (bw * 30.0) for bw in bw_levels])
    print(f"  {'Metric':<28s}  {'R²(ρ)':>8s}  {'sign expected'}")
    print(f"  {'-'*60}")
    expected = {
        "mean_nn_dist": "-",
        "contact_count": "+",
        "coordination_number": "+",
        "component_count": "-",
        "largest_component_size": "+",
        "clustering_coefficient": "+",
    }
    for m in metrics:
        vals = np.array([cond_means[bw][m] for bw in bw_levels])
        if np.any(np.isnan(vals)):
            print(f"  {m:<28s}  {'N/A':>8s}  (NaN present)")
            continue
        r, p = np.corrcoef(densities, vals)[0, 1], None
        sign_obs = "+" if r > 0 else "-"
        sign_exp = expected[m]
        match = "✓" if sign_obs == sign_exp else "✗ MISMATCH"
        print(f"  {m:<28s}  {r:>+8.3f}  {sign_exp}  {match}")

    return cond_means


def fit_models(rows, residual_type="within"):
    """Fit Models A, B, C, D for a given target and residual type.

    Models:
      A: Recovery ~ Density
      B: Recovery ~ Density + Residual(C)
      C: Recovery ~ Residual(C)
      D: Recovery ~ Density + Residual(C) + Density×Residual(C)

    Returns dict of {target: {model_name: (R², AIC, coefficients_dict)}}
    """
    try:
        import statsmodels.api as sm
    except ImportError:
        print("statsmodels not available — fallback to numpy least-squares")
        sm = None

    res_key = "res_C_within" if residual_type == "within" else "res_C_global"
    targets = [("dip", "ΔC (dip depth)"), ("restoration", "restoration"), ("tau_rec", "τ_rec")]

    results = {}

    # Use effective_density as the density predictor
    density = np.array([r["effective_density"] for r in rows])
    res_C = np.array([r[res_key] for r in rows])

    for tkey, tname in targets:
        y = np.array([r[tkey] for r in rows if r[tkey] is not None and not (isinstance(r[tkey], float) and np.isnan(r[tkey]))])
        if len(y) < 5:
            continue

        target_results = {}

        # Recompute predictors, only valid rows
        valid_idx = [i for i, r in enumerate(rows)
                     if r[tkey] is not None and not (isinstance(r[tkey], float) and np.isnan(r[tkey]))]
        d = density[valid_idx]
        rc = res_C[valid_idx]
        y_arr = np.array([r[tkey] for r in [rows[i] for i in valid_idx]])

        # Standardize predictors for numerical stability
        d_mean, d_std = d.mean(), d.std() or 1
        rc_mean, rc_std = rc.mean(), rc.std() or 1
        d_z = (d - d_mean) / d_std
        rc_z = (rc - rc_mean) / rc_std

        # Model A: Recovery ~ Density
        X_a = sm.add_constant(d_z) if sm else np.column_stack([np.ones(len(d_z)), d_z])
        # Model B: Recovery ~ Density + Residual(C)
        X_b = sm.add_constant(np.column_stack([d_z, rc_z])) if sm else np.column_stack([np.ones(len(d_z)), d_z, rc_z])
        # Model C: Recovery ~ Residual(C)
        X_c = sm.add_constant(rc_z) if sm else np.column_stack([np.ones(len(d_z)), rc_z])
        # Model D: Recovery ~ Density + Residual(C) + Density×Residual(C)
        X_d = sm.add_constant(np.column_stack([d_z, rc_z, d_z * rc_z])) if sm else np.column_stack([np.ones(len(d_z)), d_z, rc_z, d_z * rc_z])

        model_specs = [
            ("A: Density", X_a, ["const", "density"]),
            ("B: Density+ResC", X_b, ["const", "density", "res_C"]),
            ("C: ResC", X_c, ["const", "res_C"]),
            ("D: Density+ResC+Density×ResC", X_d, ["const", "density", "res_C", "density:res_C"]),
        ]

        for name, X, coef_names in model_specs:
            try:
                if sm:
                    fit = sm.OLS(y_arr, X).fit()
                    r2 = fit.rsquared
                    aic = fit.aic
                    coefs = {n: (float(fit.params[i]), float(fit.pvalues[i])) for i, n in enumerate(coef_names)}
                else:
                    # Numpy least-squares fallback
                    beta, *_ = np.linalg.lstsq(X, y_arr, rcond=None)
                    y_pred = X @ beta
                    ss_res = np.sum((y_arr - y_pred)**2)
                    ss_tot = np.sum((y_arr - y_arr.mean())**2)
                    r2 = 1 - ss_res/ss_tot
                    aic = np.nan
                    coefs = {n: (float(beta[i]), np.nan) for i, n in enumerate(coef_names)}
                target_results[name] = (r2, aic, coefs)
            except Exception as e:
                target_results[name] = (np.nan, np.nan, {})

        results[tkey] = (tname, target_results)

    return results


def print_causal_models(results_per_residual, residual_type):
    print(f"\n{SEP}")
    print(f"  TASK 4: CAUSAL MODELS — Residual(C) type: {residual_type}")
    print(f"{SEP}\n")

    for tkey, (tname, model_results) in results_per_residual.items():
        print(f"\n  Target: {tname}")
        print(f"  {'Model':<30s}  {'R²':>7s}  {'AIC':>9s}  {'Coefs (β / p)'}")
        print(f"  {'-'*100}")

        for mname, (r2, aic, coefs) in model_results.items():
            coef_str = "  ".join(f"{n}={b:+.4f}(p={p:.3f})" if not np.isnan(p) else f"{n}={b:+.4f}" for n, (b, p) in coefs.items())
            print(f"  {mname:<30s}  {r2:>7.4f}  {aic:>9.1f}  {coef_str}")

        # Compute ΔR²
        if "A: Density" in model_results and "B: Density+ResC" in model_results:
            r2_a = model_results["A: Density"][0]
            r2_b = model_results["B: Density+ResC"][0]
            print(f"  → ΔR²(B-A) = {r2_b - r2_a:+.4f}  (unique contribution of Residual(C) over Density)")
        if "C: ResC" in model_results and "B: Density+ResC" in model_results:
            r2_c = model_results["C: ResC"][0]
            r2_b = model_results["B: Density+ResC"][0]
            print(f"  → ΔR²(B-C) = {r2_b - r2_c:+.4f}  (unique contribution of Density over Residual(C))")
        if "B: Density+ResC" in model_results and "D: Density+ResC+Density×ResC" in model_results:
            r2_b = model_results["B: Density+ResC"][0]
            r2_d = model_results["D: Density+ResC+Density×ResC"][0]
            print(f"  → ΔR²(D-B) = {r2_d - r2_b:+.4f}  (interaction contribution)")


def print_decision_outcome(rows, results_within):
    """Apply director's three decision rules."""
    print(f"\n{SEP}")
    print("  DECISION RULES — Apply to RD-019 data")
    print(f"{SEP}\n")

    dip_models = results_within.get("dip", (None, {}))[1]
    rest_models = results_within.get("restoration", (None, {}))[1]
    tau_models = results_within.get("tau_rec", (None, {}))[1]

    # Outcome 1: Density changes recovery, Res(C) becomes weak after density included
    r2_a = dip_models.get("A: Density", (np.nan,))[0]
    r2_b = dip_models.get("B: Density+ResC", (np.nan,))[0]
    r2_c = dip_models.get("C: ResC", (np.nan,))[0]
    r2_d = dip_models.get("D: Density+ResC+Density×ResC", (np.nan,))[0]
    delta_r2_b_minus_a = r2_b - r2_a
    delta_r2_b_minus_c = r2_b - r2_c

    # Test: is the density-only model strong (R² > 0.10)?
    # Test: does adding ResC improve it (ΔR² > 0.05)?
    # Test: is the ResC-only model weak (R² < 0.10)?
    outcome_1 = (r2_a > 0.10 and delta_r2_b_minus_a < 0.05 and r2_c < 0.10)
    # Outcome 2: Density changes ResC, ResC still predicts recovery after density control
    # Test: density effect on res_C_within? Actually, residual(C) within density is mean-zero by construction
    # Better test: Density in Model A is significant AND ResC is significant in Model B
    if "A: Density" in dip_models and "B: Density+ResC" in dip_models:
        d_a_coef, d_a_p = dip_models["A: Density"][2].get("density", (np.nan, np.nan))
        rc_b_coef, rc_b_p = dip_models["B: Density+ResC"][2].get("res_C", (np.nan, np.nan))
        d_b_coef, d_b_p = dip_models["B: Density+ResC"][2].get("density", (np.nan, np.nan))
    else:
        d_a_coef, d_a_p = np.nan, np.nan
        rc_b_coef, rc_b_p = np.nan, np.nan
        d_b_coef, d_b_p = np.nan, np.nan
    outcome_2 = (d_a_p < 0.05 if not np.isnan(d_a_p) else False) and \
                (rc_b_p < 0.05 if not np.isnan(rc_b_p) else False)

    # Outcome 3: Density barely affects ResC. Within-density ResC is mean-zero, so this would
    # mean that global ResC and within ResC are uncorrelated with recovery.
    # Practical test: Model C R² < 0.10 and Model D R² not much better than A or B
    outcome_3 = (r2_c < 0.10 and r2_d - max(r2_a, r2_b) < 0.05)

    # Print
    print(f"  R² values (target=ΔC):")
    print(f"    Model A (Density only):              R² = {r2_a:.4f}")
    print(f"    Model B (Density + ResC within):     R² = {r2_b:.4f}  ΔR² over A = {delta_r2_b_minus_a:+.4f}")
    print(f"    Model C (ResC within only):          R² = {r2_c:.4f}")
    print(f"    Model D (B + Density×ResC):          R² = {r2_d:.4f}  ΔR² over B = {r2_d - r2_b:+.4f}")
    print(f"")
    print(f"  Coefficient tests (Model A density β={d_a_coef:+.4f} p={d_a_p:.3f}; Model B ResC β={rc_b_coef:+.4f} p={rc_b_p:.3f})")
    print(f"")
    print(f"  OUTCOME 1 (Density explains it all):      {outcome_1}    R²_A={r2_a:.3f}>0.10, ΔR²(B-A)={delta_r2_b_minus_a:+.3f}<0.05, R²_C={r2_c:.3f}<0.10")
    print(f"  OUTCOME 2 (Both density and ResC matter): {outcome_2}    density p={d_a_p:.3f}<0.05 AND resC p={rc_b_p:.3f}<0.05")
    print(f"  OUTCOME 3 (Density barely affects ResC):  {outcome_3}    R²_C={r2_c:.3f}<0.10 AND ΔR²(D-B)={r2_d - r2_b:+.3f}<0.05")

    # Decision
    print(f"\n  PRIMARY OUTCOME: ", end="")
    if outcome_1:
        print("Outcome 1 — Density explains recovery; ResC was largely density proxy")
    elif outcome_2:
        print("Outcome 2 — Both density and Residual(C) matter; ResC is not simple density")
    elif outcome_3:
        print("Outcome 3 — Density barely affects Residual(C); sparseness hypothesis weakened")
    else:
        print("AMBIGUOUS — Mixed evidence across outcomes; see full report")


def write_results_csv(rows, path="audits/RD019_RESULTS_TABLE.csv"):
    """Write the 60-row results table."""
    fieldnames = [
        "box_width", "rep", "seed", "friction", "effective_density",
        "pre_C", "dip", "restoration", "tau_rec",
        "pre_I_pred", "pre_C_sigma", "pre_MSE_s1",
        "rms_velocity", "msd", "neighbor_turnover", "packing_var",
        "res_C_global", "res_C_within",
        "mean_nn_dist", "contact_count", "coordination_number",
        "component_count", "largest_component_size", "clustering_coefficient",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            out = {k: r.get(k, "") for k in fieldnames}
            for k, v in out.items():
                if v is None or (isinstance(v, float) and np.isnan(v)):
                    out[k] = ""
            writer.writerow(out)
    print(f"\n  Wrote {path}")


def main():
    print(f"{SEP}")
    print("  RD-019: CAUSAL MODEL ANALYSIS")
    print(f"{SEP}\n")

    rows = load_data()

    # Task 3: structural validation
    cond_means = validate_density_manipulation(rows)

    # Task 4: causal models — within-residual
    print(f"\n  Residual(C) type: WITHIN density level")
    results_within = fit_models(rows, "within")
    print_causal_models(results_within, "within")

    # Also run with global residual
    print(f"\n  Residual(C) type: GLOBAL (mean-centered across all 60 runs)")
    results_global = fit_models(rows, "global")
    print_causal_models(results_global, "global")

    # Decision rules
    print_decision_outcome(rows, results_within)

    # Write CSV
    write_results_csv(rows)

    return rows, results_within, results_global


if __name__ == "__main__":
    rows, res_within, res_global = main()
