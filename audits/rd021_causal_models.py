"""RD-021: Causal Models + Decision Rules.

Fit per Director's spec:
  Model A: Recovery ~ VelocityCondition
  Model B: Recovery ~ VelocityCondition + ResC
  Model C: Recovery ~ VelocityDiagnostics
  Model D: Recovery ~ VelocityDiagnostics + ResC

For each target: dip, restoration, tau_rec.

Plus Spearman correlations, structural stability checks, decision rules V-A/B/C/D.
"""

import numpy as np
import json
import csv
from scipy import stats
import statsmodels.api as sm

SEP = "=" * 78
VELOCITY_CONDITIONS = ["V0", "V1", "V2", "V3", "V4", "V5"]


def load():
    with open("coherence-benchmark/results/rd021_velocity_ensemble.json") as f:
        return json.load(f)


def manipulation_validation(rows):
    """Confirm velocity diagnostics changed; structural descriptors did not."""
    print(f"\n{SEP}")
    print("  MANIPULATION VALIDATION")
    print(f"{SEP}\n")
    print(f"  Condition means (n=10 per condition):\n")
    print(f"  {'Cond':<5s}  {'align_init':>10s}  {'align_pre':>10s}  {'nbrsim_init':>11s}  {'nbrsim_pre':>10s}  {'entropy_pre':>12s}")
    print(f"  {'-'*75}")
    for vc in VELOCITY_CONDITIONS:
        sub = [r for r in rows if r["velocity_condition"] == vc]
        def safe(arr): 
            arr = [v for v in arr if v is not None and not (isinstance(v, float) and np.isnan(v))]
            return np.mean(arr) if arr else np.nan
        a_i = safe([r["vel_align_initial"] for r in sub])
        a_p = safe([r["vel_align_pre"] for r in sub])
        n_i = safe([r["vel_nbrsim_initial"] for r in sub])
        n_p = safe([r["vel_nbrsim_pre"] for r in sub])
        e_p = safe([r["vel_entropy_pre"] for r in sub])
        print(f"  {vc:<5s}  {a_i:>10.3f}  {a_p:>10.3f}  {n_i:>+11.3f}  {n_p:>+10.3f}  {e_p:>12.3f}")

    # ANOVA on velocity diagnostics (initial + pre)
    print(f"\n  ANOVA: velocity diagnostics across conditions")
    for window in ["initial", "pre"]:
        print(f"\n    Window: {window}")
        for key, name in [("vel_align", "alignment"), ("vel_nbrsim", "nbrsim"),
                          ("vel_entropy", "entropy"), ("vel_ke", "KE")]:
            groups = []
            for vc in VELOCITY_CONDITIONS:
                v = [r[f"{key}_{window}"] for r in rows if r["velocity_condition"] == vc
                     and r[f"{key}_{window}"] is not None
                     and not (isinstance(r[f"{key}_{window}"], float) and np.isnan(r[f"{key}_{window}"]))]
                groups.append(v)
            F, p = stats.f_oneway(*groups)
            sig = "***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else "n.s."
            print(f"      {name:<10s}  F={F:>7.3f}, p={p:.4f}  {sig}")

    # ANOVA on structural descriptors
    print(f"\n  ANOVA: structural descriptors across conditions (should be n.s.)")
    for key, name in [("mean_nn_dist", "NNdist"), ("contact_count", "contacts"),
                      ("coordination_number", "coord"), ("component_count", "comps"),
                      ("clustering_coefficient", "cluster")]:
        groups = []
        for vc in VELOCITY_CONDITIONS:
            v = [r[key] for r in rows if r["velocity_condition"] == vc and r[key] is not None]
            v = [x for x in v if not (isinstance(x, float) and np.isnan(x))]
            groups.append(v)
        F, p = stats.f_oneway(*groups)
        sig = "***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else "n.s."
        print(f"    {name:<10s}  F={F:>7.3f}, p={p:.4f}  {sig}")

    # ANOVA on C and recovery
    print(f"\n  ANOVA: pre_C and recovery metrics across conditions")
    for key, name in [("pre_C", "C_pre"), ("dip", "dip"),
                      ("restoration", "restoration"), ("tau_rec", "tau_rec")]:
        groups = []
        for vc in VELOCITY_CONDITIONS:
            v = [r[key] for r in rows if r["velocity_condition"] == vc and r[key] is not None]
            groups.append(v)
        F, p = stats.f_oneway(*groups)
        sig = "***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else "n.s."
        print(f"    {name:<12s}  F={F:>7.3f}, p={p:.4f}  {sig}")


def spearman_diagnostics(rows):
    """Spearman correlation: diagnostics vs pre_C and restoration."""
    print(f"\n{SEP}")
    print("  SPEARMAN: velocity diagnostics vs C and restoration")
    print(f"{SEP}\n")
    for window in ["initial", "pre"]:
        print(f"  Window: {window}")
        for diag in ["vel_align", "vel_nbrsim", "vel_entropy", "vel_ke"]:
            dvals, cvals, rvals = [], [], []
            for r in rows:
                v = r[f"{diag}_{window}"]
                if v is None or (isinstance(v, float) and np.isnan(v)):
                    continue
                dvals.append(v)
                cvals.append(r["pre_C"])
                rvals.append(r["restoration"])
            dvals, cvals, rvals = np.array(dvals), np.array(cvals), np.array(rvals)
            if len(dvals) < 5: continue
            r_c, p_c = stats.spearmanr(dvals, cvals)
            r_r, p_r = stats.spearmanr(dvals, rvals)
            sig = lambda p: "***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else "n.s."
            print(f"    {diag:<15s}  vs C: r={r_c:+.3f}({sig(p_c)})  vs Rest: r={r_r:+.3f}({sig(p_r)})")
        print()


def fit_models(rows):
    """Fit Models A, B, C, D for each target."""
    print(f"\n{SEP}")
    print("  CAUSAL MODELS")
    print(f"{SEP}\n")

    targets = [("dip", "ΔC (dip depth)"), ("restoration", "restoration"), ("tau_rec", "τ_rec")]
    strategy_names = [vc for vc in VELOCITY_CONDITIONS if vc != "V0"]
    strategy_dummies = {s: np.array([1.0 if r["velocity_condition"] == s else 0.0 for r in rows]) for s in strategy_names}
    res_c = np.array([r["res_C_within"] for r in rows])

    # Velocity diagnostics: use initial-window for "manipulation effect" interpretation
    diag_keys = ["vel_align_initial", "vel_nbrsim_initial", "vel_entropy_initial", "vel_ke_initial"]
    diag_names = ["align_init", "nbrsim_init", "entropy_init", "ke_init"]
    diag_array = np.column_stack([np.array([r[k] for r in rows]) for k in diag_keys])

    for tkey, tname in targets:
        y = np.array([r[tkey] for r in rows if r[tkey] is not None])
        valid = np.array([r[tkey] is not None for r in rows])
        print(f"\n  Target: {tname}")

        # Model A: Recovery ~ VelocityCondition
        X_strat = np.column_stack([strategy_dummies[s][valid] for s in strategy_names])
        X_a = sm.add_constant(X_strat)
        # Model B: Recovery ~ VelocityCondition + ResC
        X_b = sm.add_constant(np.column_stack([X_strat, res_c[valid]]))
        # Model C: Recovery ~ VelocityDiagnostics
        X_c = sm.add_constant(diag_array[valid])
        # Model D: Recovery ~ VelocityDiagnostics + ResC
        X_d = sm.add_constant(np.column_stack([diag_array[valid], res_c[valid]]))

        for label, X, names in [
            ("A: VelocityCondition", X_a, ["const"] + strategy_names),
            ("B: VelCond + ResC", X_b, ["const"] + strategy_names + ["res_C_within"]),
            ("C: VelocityDiagnostics", X_c, ["const"] + diag_names),
            ("D: VelDiag + ResC", X_d, ["const"] + diag_names + ["res_C_within"]),
        ]:
            good = ~(np.isnan(y) | np.any(np.isnan(X), axis=1))
            if good.sum() < len(names) + 2:
                continue
            fit = sm.OLS(y[good], X[good]).fit()
            print(f"\n  Model {label}  (R²={fit.rsquared:.4f}, AIC={fit.aic:.1f}, n={good.sum()})")
            for i, n in enumerate(names):
                p = fit.pvalues[i]
                if np.isnan(p):
                    print(f"    {n:<22s}  β={fit.params[i]:+.4f}  p=N/A")
                else:
                    print(f"    {n:<22s}  β={fit.params[i]:+.4f}  p={p:.4f}")

        # ΔR² comparisons
        fit_a = sm.OLS(y[valid & ~np.any(np.isnan(X_a), axis=1)], X_a[valid & ~np.any(np.isnan(X_a), axis=1)]).fit()
        fit_b = sm.OLS(y[valid & ~np.any(np.isnan(X_b), axis=1)], X_b[valid & ~np.any(np.isnan(X_b), axis=1)]).fit()
        fit_c = sm.OLS(y[valid & ~np.any(np.isnan(X_c), axis=1)], X_c[valid & ~np.any(np.isnan(X_c), axis=1)]).fit()
        fit_d = sm.OLS(y[valid & ~np.any(np.isnan(X_d), axis=1)], X_d[valid & ~np.any(np.isnan(X_d), axis=1)]).fit()
        print(f"  → ΔR²(B-A) = {fit_b.rsquared - fit_a.rsquared:+.4f}  (ResC adds over condition)")
        print(f"  → ΔR²(D-C) = {fit_d.rsquared - fit_c.rsquared:+.4f}  (ResC adds over diagnostics)")
        print(f"  → ΔR²(C-A) = {fit_c.rsquared - fit_a.rsquared:+.4f}  (diagnostics add over condition)")


def apply_decision_rules(rows):
    """Apply Director's V-A, V-B, V-C, V-D decision rules."""
    print(f"\n{SEP}")
    print("  DECISION RULES — V-A / V-B / V-C / V-D")
    print(f"{SEP}\n")

    # Velocity organization changed?
    # Take the average F across initial-window diagnostics
    f_align_init, _ = stats.f_oneway(*[
        [r["vel_align_initial"] for r in rows if r["velocity_condition"] == vc and r["vel_align_initial"] is not None]
        for vc in VELOCITY_CONDITIONS
    ])
    f_nbrsim_init, _ = stats.f_oneway(*[
        [r["vel_nbrsim_initial"] for r in rows if r["velocity_condition"] == vc and r["vel_nbrsim_initial"] is not None]
        for vc in VELOCITY_CONDITIONS
    ])
    f_entropy_init, _ = stats.f_oneway(*[
        [r["vel_entropy_initial"] for r in rows if r["velocity_condition"] == vc and r["vel_entropy_initial"] is not None]
        for vc in VELOCITY_CONDITIONS
    ])
    # Pre-perturbation persistence
    f_align_pre, _ = stats.f_oneway(*[
        [r["vel_align_pre"] for r in rows if r["velocity_condition"] == vc and r["vel_align_pre"] is not None]
        for vc in VELOCITY_CONDITIONS
    ])
    f_nbrsim_pre, _ = stats.f_oneway(*[
        [r["vel_nbrsim_pre"] for r in rows if r["velocity_condition"] == vc and r["vel_nbrsim_pre"] is not None]
        for vc in VELOCITY_CONDITIONS
    ])

    vel_changed_init = np.mean([f_align_init, f_nbrsim_init, f_entropy_init]) > 4  # F > 4 indicates substantial effect
    vel_changed_pre = np.mean([f_align_pre, f_nbrsim_pre]) > 4

    # C changed?
    f_c, p_c = stats.f_oneway(*[
        [r["pre_C"] for r in rows if r["velocity_condition"] == vc] for vc in VELOCITY_CONDITIONS
    ])
    c_changed = p_c < 0.05

    # Recovery changed?
    f_dip, p_dip = stats.f_oneway(*[
        [r["dip"] for r in rows if r["velocity_condition"] == vc] for vc in VELOCITY_CONDITIONS
    ])
    f_rest, p_rest = stats.f_oneway(*[
        [r["restoration"] for r in rows if r["velocity_condition"] == vc] for vc in VELOCITY_CONDITIONS
    ])
    f_tau, p_tau = stats.f_oneway(*[
        [r["tau_rec"] for r in rows if r["velocity_condition"] == vc] for vc in VELOCITY_CONDITIONS
    ])
    recovery_changed = (p_dip < 0.05) or (p_rest < 0.05) or (p_tau < 0.05)

    print(f"  Velocity diagnostics:")
    print(f"    Initial window: align F={f_align_init:.1f}, nbrsim F={f_nbrsim_init:.1f}, entropy F={f_entropy_init:.1f}")
    print(f"    Pre-perturbation: align F={f_align_pre:.1f}, nbrsim F={f_nbrsim_pre:.1f}")
    print(f"    -> Velocity organization changed substantially: {vel_changed_init and vel_changed_pre}")
    print(f"  C_pre:  F={f_c:.3f}, p={p_c:.4f}  -> C changed: {c_changed}")
    print(f"  Recovery: dip p={p_dip:.4f}, restoration p={p_rest:.4f}, tau p={p_tau:.4f}")
    print(f"  -> Recovery changed: {recovery_changed}")

    # Decision logic
    if vel_changed_init and c_changed and recovery_changed:
        outcome = "V-A"
    elif vel_changed_init and recovery_changed and not c_changed:
        outcome = "V-B"
    elif vel_changed_init and c_changed and not recovery_changed:
        outcome = "V-C"
    elif vel_changed_init and not c_changed and not recovery_changed:
        outcome = "V-D"
    else:
        outcome = "INSUFFICIENT"

    interp = {
        "V-A": "Strongest support yet that C reflects velocity-field organization",
        "V-B": "C is still a thermometer (velocity changes recovery but not C)",
        "V-C": "C reflects velocity organization but not a recovery-relevant state",
        "V-D": "Velocity-field hypothesis FALSIFIED (velocity changes, neither C nor recovery does)",
        "INSUFFICIENT": "Manipulation did not produce expected effect",
    }
    print(f"\n  DECISION: {outcome}")
    print(f"  Interpretation: {interp[outcome]}")
    return outcome


def write_results_csv(rows, path="audits/RD021_RESULTS.csv"):
    fieldnames = [
        "velocity_condition", "rep", "seed", "friction",
        "pre_C", "dip", "restoration", "tau_rec",
        "pre_I_pred", "pre_C_sigma", "pre_MSE_s1",
        # structural
        "mean_nn_dist", "contact_count", "coordination_number",
        "component_count", "clustering_coefficient",
        # velocity diagnostics
        "vel_align_initial", "vel_corrlen_initial", "vel_nbrsim_initial", "vel_entropy_initial", "vel_ke_initial",
        "vel_align_pre", "vel_corrlen_pre", "vel_nbrsim_pre", "vel_entropy_pre", "vel_ke_pre",
        "velocity_alignment", "velocity_correlation_length", "mean_neighbor_velocity_similarity",
        "velocity_entropy", "kinetic_energy",
        # residuals
        "res_C_global", "res_C_within",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            out = {k: r.get(k, "") for k in fieldnames}
            for k, v in list(out.items()):
                if v is None or (isinstance(v, float) and np.isnan(v)):
                    out[k] = ""
            writer.writerow(out)
    print(f"\n  Wrote {path}")


def main():
    print(f"{SEP}")
    print("  RD-021: CAUSAL MODEL ANALYSIS")
    print(f"{SEP}")
    rows = load()
    manipulation_validation(rows)
    spearman_diagnostics(rows)
    fit_models(rows)
    outcome = apply_decision_rules(rows)
    write_results_csv(rows)
    return outcome


if __name__ == "__main__":
    main()
