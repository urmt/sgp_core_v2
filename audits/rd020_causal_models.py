"""RD-020: Causal Models + Decision Rules.

For each recovery target:
  Recovery ~ Strategy
  Recovery ~ Strategy + ResC
  Recovery ~ Strategy * ResC

And structural-importance correlations:
  Correlate mean degree/force/clustering of removed grains with dip/restoration/tau_rec.

Apply decision rules A/B/C/D.
"""

import numpy as np
import json
import csv
from scipy import stats
import statsmodels.api as sm

SEP = "=" * 78

STRATEGIES = [
    ("S0", "random"),
    ("S1", "largest"),
    ("S2", "smallest"),
    ("S3", "highest_degree"),
    ("S4", "lowest_degree"),
    ("S5", "highest_force"),
]


def load():
    with open("coherence-benchmark/results/rd020_selective_ensemble.json") as f:
        return json.load(f)


def per_strategy_summary(rows):
    """Per-strategy means, std, 95% CI for primary metrics."""
    print(f"\n{SEP}")
    print("  RD-020: PER-STRATEGY SUMMARY (n=10 per strategy)")
    print(f"{SEP}\n")
    print(f"  {'Strat':<18s}  {'C_pre':>16s}  {'dip':>16s}  {'Rest.':>16s}  {'τ':>16s}")
    print(f"  {'-'*100}")
    for slabel, sname in STRATEGIES:
        sub = [r for r in rows if r["strategy"] == sname]
        if not sub:
            continue
        n = len(sub)
        for metric, key in [("C_pre", "pre_C"), ("dip", "dip"), ("Rest.", "restoration"), ("τ", "tau_rec")]:
            vals = np.array([r[key] for r in sub if r[key] is not None])
            mean = np.mean(vals)
            sem = np.std(vals, ddof=1) / np.sqrt(n) if n > 1 else 0
            ci_lo = mean - 1.96 * sem
            ci_hi = mean + 1.96 * sem
            if metric == "C_pre":
                c_str = f"{mean:.4f}±{sem:.4f} [{ci_lo:.4f},{ci_hi:.4f}]"
            elif metric == "dip":
                d_str = f"{mean:+.4f}±{sem:.4f}"
            elif metric == "Rest.":
                r_str = f"{mean:.4f}±{sem:.4f}"
            else:
                tau_str = f"{mean:.0f}±{sem:.0f}"
        c = np.array([r["pre_C"] for r in sub])
        d = np.array([r["dip"] for r in sub])
        r_ = np.array([r["restoration"] for r in sub])
        t = np.array([r["tau_rec"] for r in sub])
        c_str = f"{c.mean():.4f}±{c.std(ddof=1)/np.sqrt(n):.4f}"
        d_str = f"{d.mean():+.4f}±{d.std(ddof=1)/np.sqrt(n):.4f}"
        r_str = f"{r_.mean():.4f}±{r_.std(ddof=1)/np.sqrt(n):.4f}"
        t_str = f"{t.mean():.0f}±{t.std(ddof=1)/np.sqrt(n):.0f}"
        print(f"  {slabel+' '+sname:<18s}  {c_str:>16s}  {d_str:>16s}  {r_str:>16s}  {t_str:>16s}")


def compare_to_control(rows):
    """Test each non-control strategy against S0 (random) baseline."""
    print(f"\n{SEP}")
    print("  STRATEGY VS RANDOM (S0) — Welch's t-test per metric")
    print(f"{SEP}\n")
    s0 = [r for r in rows if r["strategy"] == "random"]
    print(f"  {'Comparison':<28s}  {'C_pre (p)':>12s}  {'dip (p)':>12s}  {'Rest. (p)':>12s}  {'τ (p)':>12s}")
    print(f"  {'-'*86}")
    for slabel, sname in STRATEGIES:
        if sname == "random":
            continue
        sub = [r for r in rows if r["strategy"] == sname]
        if not sub: continue
        ps = []
        for key in ["pre_C", "dip", "restoration", "tau_rec"]:
            v0 = np.array([r[key] for r in s0 if r[key] is not None])
            v1 = np.array([r[key] for r in sub if r[key] is not None])
            if len(v0) < 2 or len(v1) < 2: continue
            _, p = stats.ttest_ind(v0, v1, equal_var=False)
            ps.append((key, p))
        label = f"{slabel} ({sname})"
        parts = [f"{p:.4f}" if not np.isnan(p) else "N/A" for _, p in ps]
        print(f"  {label:<28s}  " + "  ".join(f"{x:>12s}" for x in parts))


def fit_models(rows):
    """Fit Recovery ~ Strategy / Strategy+ResC / Strategy*ResC for each target.

    Encode strategy as 5 dummy variables (S0 = reference).
    """
    print(f"\n{SEP}")
    print("  TASK: CAUSAL MODELS — Strategy effect on recovery")
    print(f"{SEP}\n")

    try:
        import statsmodels.api as sm
    except ImportError:
        print("  statsmodels not available — aborting")
        return

    targets = [("dip", "ΔC (dip depth)"), ("restoration", "restoration"), ("tau_rec", "τ_rec")]

    # Build predictor matrix
    strategy_names = [s for _, s in STRATEGIES if s != "random"]
    strategy_dummies = {}
    for s in strategy_names:
        strategy_dummies[s] = np.array([1.0 if r["strategy"] == s else 0.0 for r in rows])
    res_c = np.array([r["res_C_within"] for r in rows])
    res_c_g = np.array([r["res_C_global"] for r in rows])

    for tkey, tname in targets:
        y = np.array([r[tkey] for r in rows if r[tkey] is not None])
        valid = np.array([r[tkey] is not None for r in rows])

        # Build the strategy-only model
        X_strat = np.column_stack([strategy_dummies[s][valid] for s in strategy_names])
        X_strat_c = sm.add_constant(X_strat)

        # Model: Recovery ~ Strategy + ResC
        X_strat_resc = np.column_stack([X_strat, res_c[valid]])
        X_strat_resc_c = sm.add_constant(X_strat_resc)

        # Model: Recovery ~ Strategy * ResC (interactions)
        interaction_cols = []
        for s in strategy_names:
            interaction_cols.append(strategy_dummies[s][valid] * res_c[valid])
        X_interact = np.column_stack([X_strat, res_c[valid]] + interaction_cols)
        X_interact_c = sm.add_constant(X_interact)

        print(f"\n  Target: {tname}")
        for label, X, names in [
            ("Strategy only", X_strat_c, ["const"] + strategy_names),
            ("Strategy + ResC", X_strat_resc_c, ["const"] + strategy_names + ["res_C_within"]),
            ("Strategy * ResC", X_interact_c, ["const"] + strategy_names + ["res_C_within"] + [f"{s}:res_C" for s in strategy_names]),
        ]:
            good = ~(np.isnan(y) | np.any(np.isnan(X), axis=1))
            if good.sum() < len(names) + 2:
                continue
            fit = sm.OLS(y[good], X[good]).fit()
            print(f"\n  Model: {label}  (R²={fit.rsquared:.4f}, AIC={fit.aic:.1f})")
            for i, n in enumerate(names):
                print(f"    {n:<22s}  β={fit.params[i]:+.4f}  p={fit.pvalues[i]:.4f}")


def structural_importance_correlations(rows):
    """For each strategy, compute mean degree/force/clustering of removed grains.
    Correlate with ΔC, restoration, τ_rec.
    """
    print(f"\n{SEP}")
    print("  STRUCTURAL IMPORTANCE CORRELATIONS")
    print(f"{SEP}\n")
    print("  For each strategy, mean structural importance of removed grains")
    print("  is correlated with recovery outcomes.\n")

    # Compute clustering of removed grains for each run
    # (degree and force are already in pre_metrics for S3/S4/S5)
    # We need to compute clustering for all strategies.

    # For simplicity, use what's in pre_metrics
    # S3/S4: removed_degree_mean available
    # S5: removed_force_mean available
    # For all: removed_radii_mean and removed_speed_mean

    print(f"  {'Strat':<18s}  {'N':>3s}  {'<r>':>8s}  {'<deg>':>8s}  {'<force>':>10s}  {'<speed>':>10s}")
    print(f"  {'-'*70}")
    for slabel, sname in STRATEGIES:
        sub = [r for r in rows if r["strategy"] == sname]
        if not sub: continue
        rs = [r.get("removed_radii_mean", np.nan) for r in sub]
        ds = [r.get("removed_degree_mean", np.nan) for r in sub]
        fs = [r.get("removed_force_mean", np.nan) for r in sub]
        ss = [r.get("removed_speed_mean", np.nan) for r in sub]
        def safe(arr):
            arr = np.array([v for v in arr if v is not None and not (isinstance(v, float) and np.isnan(v))])
            if len(arr) == 0: return np.nan
            return np.mean(arr)
        print(f"  {slabel+' '+sname:<18s}  {len(sub):>3d}  {safe(rs):>8.3f}  {safe(ds):>8.2f}  {safe(fs):>10.2f}  {safe(ss):>10.3f}")

    # Now correlate within strategy-level means
    print(f"\n  Cross-strategy correlations (mean of each strategy, n=6):")
    print(f"  {'Predictor':<28s}  {'vs dip':>14s}  {'vs Rest.':>14s}  {'vs τ':>14s}")
    print(f"  {'-'*78}")
    strat_means = {}
    for slabel, sname in STRATEGIES:
        sub = [r for r in rows if r["strategy"] == sname]
        if not sub: continue
        strat_means[sname] = {
            "dip": np.nanmean([r["dip"] for r in sub]),
            "restoration": np.nanmean([r["restoration"] for r in sub]),
            "tau_rec": np.nanmean([r["tau_rec"] for r in sub]),
            "r": np.nanmean([r.get("removed_radii_mean") for r in sub if r.get("removed_radii_mean") is not None]),
            "d": np.nanmean([r.get("removed_degree_mean") for r in sub if r.get("removed_degree_mean") is not None]),
            "f": np.nanmean([r.get("removed_force_mean") for r in sub if r.get("removed_force_mean") is not None]),
            "s": np.nanmean([r.get("removed_speed_mean") for r in sub if r.get("removed_speed_mean") is not None]),
        }

    for pred_key, pred_name in [("r", "removed_radii_mean"), ("d", "removed_degree_mean"),
                                  ("f", "removed_force_mean"), ("s", "removed_speed_mean")]:
        ps = [strat_means[s][pred_key] for s in strat_means]
        ds = [strat_means[s]["dip"] for s in strat_means]
        rs = [strat_means[s]["restoration"] for s in strat_means]
        ts = [strat_means[s]["tau_rec"] for s in strat_means]
        def safe_corr(x, y):
            x, y = np.array(x), np.array(y)
            valid = ~(np.isnan(x) | np.isnan(y))
            if valid.sum() < 3:
                return np.nan, np.nan
            return np.corrcoef(x[valid], y[valid])[0, 1], stats.linregress(x[valid], y[valid]).pvalue
        r_d, p_d = safe_corr(ps, ds)
        r_r, p_r = safe_corr(ps, rs)
        r_t, p_t = safe_corr(ps, ts)
        print(f"  {pred_name:<28s}  {r_d:+.3f}(p={p_d:.3f})  {r_r:+.3f}(p={p_r:.3f})  {r_t:+.3f}(p={p_t:.3f})")


def apply_decision_rules(rows):
    """Apply Director's A/B/C/D decision rules.

    A: targeted removals change recovery but not C
    B: targeted removals change both C and recovery
    C: targeted removals change C more than recovery
    D: targeted removals change neither
    """
    print(f"\n{SEP}")
    print("  DECISION RULES — Apply to RD-020 data")
    print(f"{SEP}\n")

    # One-way ANOVA per metric across strategies
    s0 = np.array([r["pre_C"] for r in rows if r["strategy"] == "random"])
    s1 = np.array([r["pre_C"] for r in rows if r["strategy"] == "largest"])
    s2 = np.array([r["pre_C"] for r in rows if r["strategy"] == "smallest"])
    s3 = np.array([r["pre_C"] for r in rows if r["strategy"] == "highest_degree"])
    s4 = np.array([r["pre_C"] for r in rows if r["strategy"] == "lowest_degree"])
    s5 = np.array([r["pre_C"] for r in rows if r["strategy"] == "highest_force"])
    F_C, p_C = stats.f_oneway(s0, s1, s2, s3, s4, s5)

    s0d = np.array([r["dip"] for r in rows if r["strategy"] == "random"])
    s1d = np.array([r["dip"] for r in rows if r["strategy"] == "largest"])
    s2d = np.array([r["dip"] for r in rows if r["strategy"] == "smallest"])
    s3d = np.array([r["dip"] for r in rows if r["strategy"] == "highest_degree"])
    s4d = np.array([r["dip"] for r in rows if r["strategy"] == "lowest_degree"])
    s5d = np.array([r["dip"] for r in rows if r["strategy"] == "highest_force"])
    F_d, p_d = stats.f_oneway(s0d, s1d, s2d, s3d, s4d, s5d)

    s0r = np.array([r["restoration"] for r in rows if r["strategy"] == "random"])
    s1r = np.array([r["restoration"] for r in rows if r["strategy"] == "largest"])
    s2r = np.array([r["restoration"] for r in rows if r["strategy"] == "smallest"])
    s3r = np.array([r["restoration"] for r in rows if r["strategy"] == "highest_degree"])
    s4r = np.array([r["restoration"] for r in rows if r["strategy"] == "lowest_degree"])
    s5r = np.array([r["restoration"] for r in rows if r["strategy"] == "highest_force"])
    F_r, p_r = stats.f_oneway(s0r, s1r, s2r, s3r, s4r, s5r)

    s0t = np.array([r["tau_rec"] for r in rows if r["strategy"] == "random"])
    s1t = np.array([r["tau_rec"] for r in rows if r["strategy"] == "largest"])
    s2t = np.array([r["tau_rec"] for r in rows if r["strategy"] == "smallest"])
    s3t = np.array([r["tau_rec"] for r in rows if r["strategy"] == "highest_degree"])
    s4t = np.array([r["tau_rec"] for r in rows if r["strategy"] == "lowest_degree"])
    s5t = np.array([r["tau_rec"] for r in rows if r["strategy"] == "highest_force"])
    F_t, p_t = stats.f_oneway(s0t, s1t, s2t, s3t, s4t, s5t)

    print(f"  One-way ANOVA: does strategy affect each metric?")
    print(f"    pre_C:       F={F_C:.3f}, p={p_C:.4f}  {'***' if p_C<0.001 else '**' if p_C<0.01 else '*' if p_C<0.05 else 'n.s.'}")
    print(f"    dip:         F={F_d:.3f}, p={p_d:.4f}  {'***' if p_d<0.001 else '**' if p_d<0.01 else '*' if p_d<0.05 else 'n.s.'}")
    print(f"    restoration: F={F_r:.3f}, p={p_r:.4f}  {'***' if p_r<0.001 else '**' if p_r<0.01 else '*' if p_r<0.05 else 'n.s.'}")
    print(f"    tau_rec:     F={F_t:.3f}, p={p_t:.4f}  {'***' if p_t<0.001 else '**' if p_t<0.01 else '*' if p_t<0.05 else 'n.s.'}")

    # Effect size: how much does each strategy deviate from random (S0)?
    print(f"\n  Effect sizes (Cohen's d: each strategy vs S0 random):")
    print(f"  {'Comparison':<28s}  {'C_pre':>10s}  {'dip':>10s}  {'Rest.':>10s}  {'τ':>10s}")
    print(f"  {'-'*75}")
    for slabel, sname, sub_C, sub_d, sub_r, sub_t in [
        ("S1 largest", "largest", s1, s1d, s1r, s1t),
        ("S2 smallest", "smallest", s2, s2d, s2r, s2t),
        ("S3 high-deg", "highest_degree", s3, s3d, s3r, s3t),
        ("S4 low-deg", "lowest_degree", s4, s4d, s4r, s4t),
        ("S5 high-force", "highest_force", s5, s5d, s5r, s5t),
    ]:
        def coh(v1, v0):
            s_pooled = np.sqrt((v1.var(ddof=1) + v0.var(ddof=1)) / 2)
            if s_pooled == 0: return 0
            return (v1.mean() - v0.mean()) / s_pooled
        d_C = coh(sub_C, s0)
        d_d = coh(sub_d, s0d)
        d_r = coh(sub_r, s0r)
        d_t = coh(sub_t, s0t)
        print(f"  {slabel:<28s}  {d_C:>+10.3f}  {d_d:>+10.3f}  {d_r:>+10.3f}  {d_t:>+10.3f}")

    # Decision rules
    print(f"\n  DECISION RULE APPLICATION:")
    # Outcome A: strategy changes recovery, not C
    # Outcome B: strategy changes both C and recovery
    # Outcome C: strategy changes C more than recovery
    # Outcome D: strategy changes neither

    # Practical thresholds: strategy has effect on X if at least one pairwise
    # t-test vs S0 has p<0.05 AND |Cohen's d| > 0.5 (medium effect)
    c_effected = p_C < 0.05
    d_effected = p_d < 0.05
    r_effected = p_r < 0.05
    t_effected = p_t < 0.05

    # Effect size comparison: how much do strategies move C vs recovery?
    # Use the SD of the means across strategies
    c_range = max(s0.mean(), s1.mean(), s2.mean(), s3.mean(), s4.mean(), s5.mean()) - \
              min(s0.mean(), s1.mean(), s2.mean(), s3.mean(), s4.mean(), s5.mean())
    d_range = max(s0d.mean(), s1d.mean(), s2d.mean(), s3d.mean(), s4d.mean(), s5d.mean()) - \
              min(s0d.mean(), s1d.mean(), s2d.mean(), s3d.mean(), s4d.mean(), s5d.mean())
    r_range = max(s0r.mean(), s1r.mean(), s2r.mean(), s3r.mean(), s4r.mean(), s5r.mean()) - \
              min(s0r.mean(), s1r.mean(), s2r.mean(), s3r.mean(), s4r.mean(), s5r.mean())

    print(f"\n  Range of strategy means (max - min across 6 strategies):")
    print(f"    C_pre:       {c_range:.4f}")
    print(f"    dip:         {d_range:.4f}")
    print(f"    restoration: {r_range:.4f}")
    print(f"")

    # Decision logic
    any_recovery_changed = d_effected or r_effected or t_effected
    c_changed = c_effected
    if c_changed and any_recovery_changed:
        # Both changed. Is C change larger than recovery change?
        c_signal = abs(c_range) / (np.std(s0) + 1e-10)  # standardized
        d_signal = abs(d_range) / (np.std(s0d) + 1e-10)
        r_signal = abs(r_range) / (np.std(s0r) + 1e-10)
        max_recovery_signal = max(d_signal, r_signal)
        if c_signal > max_recovery_signal * 1.5:
            outcome = "C"
        else:
            outcome = "B"
    elif any_recovery_changed and not c_changed:
        outcome = "A"
    elif c_changed and not any_recovery_changed:
        outcome = "C"
    else:
        outcome = "D"

    print(f"  OUTCOME: {outcome}")
    interp = {
        "A": "C remains a thermometer (strategy changes recovery but not C)",
        "B": "C tracks structurally important organization (both C and recovery change)",
        "C": "C is sensitive to hidden structure but not causally central",
        "D": "Need to abandon removal-based hypotheses; investigate C calculation itself",
    }
    print(f"  Interpretation: {interp[outcome]}")
    return outcome


def write_results_csv(rows, path="audits/RD020_RESULTS.csv"):
    fieldnames = [
        "strategy_label", "strategy", "rep", "seed", "friction",
        "pre_C", "dip", "restoration", "tau_rec",
        "pre_I_pred", "pre_C_sigma", "pre_MSE_s1",
        "rms_velocity", "msd", "neighbor_turnover", "packing_var",
        "res_C_global", "res_C_within",
        "removed_radii_mean", "removed_degree_mean", "removed_force_mean", "removed_speed_mean",
        "kept_degree_mean", "kept_force_mean",
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
    print("  RD-020: CAUSAL MODEL ANALYSIS")
    print(f"{SEP}\n")
    rows = load()
    per_strategy_summary(rows)
    compare_to_control(rows)
    fit_models(rows)
    structural_importance_correlations(rows)
    outcome = apply_decision_rules(rows)
    write_results_csv(rows)
    return outcome


if __name__ == "__main__":
    main()
