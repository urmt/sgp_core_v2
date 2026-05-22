"""
Phase 408: Predictive Breakdown
Maps where emergence prediction fails under adversarial conditions.

Predictor: Phase 407 model (trained on Phase 391-399)
True system: Same base model with adversarial modifications
"""
import json, csv, os, math

SEED = 430
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SECTORS = ["P-A-N", "P-A", "Projection", "P-N", "Antisymmetry", "Neutral", "A-N"]

# Phase 407 predictor parameters
PREDICTOR_K = 1.5e-8
PREDICTOR_WEIGHTS = {"P": 0.52, "A": 0.32, "N": 0.16}
TRUE_K = 7.8125e-9
TRUE_WEIGHTS = {"P": 0.507, "A": 0.451, "N": 0.332}

SECTOR_BASE = {
    "P-A-N": 0.9285, "P-A": 0.9283, "Projection": 0.9279,
    "P-N": 0.9244, "Antisymmetry": 0.9225, "Neutral": 0.9031, "A-N": 0.8864
}

def compute_emergence(sector, depth, weights, w_total, k, sector_override=None):
    df = 1.0 / (1.0 + k * (depth - 1))
    if sector_override:
        raw = sector_override[sector] * df
    else:
        sector_scale = {
            "P-A-N": weights["P"] + weights["A"] + weights["N"],
            "P-A": weights["P"] + weights["A"],
            "Projection": weights["P"],
            "P-N": weights["P"] + weights["N"],
            "Antisymmetry": weights["A"],
            "Neutral": weights["N"],
            "A-N": weights["A"] + weights["N"]
        }
        base = SECTOR_BASE.get(sector, 0.8864)
        scale = sector_scale[sector] / w_total if w_total > 0 else 0
        raw = base * df * max(0.05, scale)
    return min(MAX_EMERGENCE, max(0.05, raw))

def predictor_emergence(sector, depth, p_scale=1.0, a_scale=1.0, n_scale=1.0, k=PREDICTOR_K):
    pw = PREDICTOR_WEIGHTS["P"] * p_scale
    aw = PREDICTOR_WEIGHTS["A"] * a_scale
    nw = PREDICTOR_WEIGHTS["N"] * n_scale
    w_total = sum(PREDICTOR_WEIGHTS.values())
    return compute_emergence(sector, depth, {"P": pw, "A": aw, "N": nw}, w_total, k)

def true_emergence(sector, depth, p_scale=1.0, a_scale=1.0, n_scale=1.0, k=TRUE_K):
    pw = TRUE_WEIGHTS["P"] * p_scale
    aw = TRUE_WEIGHTS["A"] * a_scale
    nw = TRUE_WEIGHTS["N"] * n_scale
    w_total = sum(TRUE_WEIGHTS.values())
    return compute_emergence(sector, depth, {"P": pw, "A": aw, "N": nw}, w_total, k)

def compute_error(pred, true_val):
    return abs(pred - true_val) / max(true_val, 0.01)

# Depth for testing — must be large enough that depth factor matters
TEST_DEPTH = 67108864
MAX_EMERGENCE = 0.9999

print("=" * 60)
print("PHASE 408: PREDICTIVE BREAKDOWN ANALYSIS")
print("=" * 60)

all_conditions_data = {}

# ==========================================================
# CONDITION 1: EXTREME OPERATOR AMPLIFICATION
# ==========================================================
print("\n--- C1: Extreme Operator Amplification ---")
amp_values = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
c1_results = []
c1_predictor = predictor_emergence("P-A-N", TEST_DEPTH, p_scale=1.0, a_scale=1.0, n_scale=1.0)

for amp in amp_values:
    p_true = true_emergence("P-A-N", TEST_DEPTH, p_scale=amp, a_scale=1.0, n_scale=1.0)
    p_pred = predictor_emergence("P-A-N", TEST_DEPTH, p_scale=1.0, a_scale=1.0, n_scale=1.0)
    err = compute_error(p_pred, p_true)
    c1_results.append({"amp": amp, "pred": round(p_pred, 4), "true": round(p_true, 4), "error": round(err, 4)})

# Find breakdown threshold (error > 0.50)
c1_breakdown = None
for r in c1_results:
    if r["error"] > 0.50 and c1_breakdown is None:
        c1_breakdown = r["amp"]
print(f"  Breakdown threshold (error>50%): amp={c1_breakdown}")
for r in c1_results:
    print(f"  amp={r['amp']:.1f}: pred={r['pred']:.4f} true={r['true']:.4f} err={r['error']:.2%}")
all_conditions_data["extreme_operator_amplification"] = c1_results

# ==========================================================
# CONDITION 2: ASYMMETRIC RECURSIVE WEIGHTING
# ==========================================================
print("\n--- C2: Asymmetric Recursive Weighting ---")
k_ratios = [0.1, 0.25, 0.5, 0.75, 1.0, 2.0, 4.0, 8.0, 10.0]
c2_results = []

for kr in k_ratios:
    k_true = TRUE_K * kr
    t = true_emergence("P-A-N", TEST_DEPTH, k=k_true)
    p = predictor_emergence("P-A-N", TEST_DEPTH, k=PREDICTOR_K)
    err = compute_error(p, t)
    c2_results.append({"k_ratio": kr, "pred": round(p, 4), "true": round(t, 4), "error": round(err, 4)})

c2_breakdown = None
for r in c2_results:
    if r["error"] > 0.50 and c2_breakdown is None:
        c2_breakdown = r["k_ratio"]
print(f"  Breakdown threshold: k_ratio={c2_breakdown}")
for r in c2_results:
    print(f"  k_ratio={r['k_ratio']:.2f}: pred={r['pred']:.4f} true={r['true']:.4f} err={r['error']:.2%}")
all_conditions_data["asymmetric_recursive_weighting"] = c2_results

# ==========================================================
# CONDITION 3: HIDDEN RECURSIVE COUPLING
# ==========================================================
print("\n--- C3: Hidden Recursive Coupling ---")
coupling_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
c3_results = []

p_base_true = true_emergence("P-A-N", TEST_DEPTH)

for cp in coupling_values:
    # True system with coupling: emergence modified by cross-term
    t = p_base_true * (1.0 + cp * 0.3)  # coupling amplifies emergence nonlinearly
    t = min(1.0, t)
    p = predictor_emergence("P-A-N", TEST_DEPTH)
    err = compute_error(p, t)
    c3_results.append({"coupling": cp, "pred": round(p, 4), "true": round(t, 4), "error": round(err, 4)})

c3_breakdown = None
for r in c3_results:
    if r["error"] > 0.50 and c3_breakdown is None:
        c3_breakdown = r["coupling"]
print(f"  Breakdown threshold: coupling={c3_breakdown}")
for r in c3_results:
    print(f"  coupling={r['coupling']:.1f}: pred={r['pred']:.4f} true={r['true']:.4f} err={r['error']:.2%}")
all_conditions_data["hidden_recursive_coupling"] = c3_results

# ==========================================================
# CONDITION 4: DISCONTINUOUS OPERATOR SWITCHING
# ==========================================================
print("\n--- C4: Discontinuous Operator Switching ---")
# Simulate: at depth > switch_depth, P is removed
switch_depths = [10, 100, 500, 1000, 2000, 5000, 10000, 50000]
test_depths = [1, 10, 100, 500, 1000, 2000, 5000, 10000, 50000, 100000]
c4_results = []

for sd in switch_depths:
    errors_at_switch = []
    for td in test_depths:
        # Predictor assumes P always present
        p = predictor_emergence("P-A-N", td)
        # True: P removed for depths > sd
        if td <= sd:
            t = true_emergence("P-A-N", td)
        else:
            t = true_emergence("P-A-N", td, p_scale=0.0)
        err = compute_error(p, t)
        errors_at_switch.append({"depth": td, "pred": round(p, 4), "true": round(t, 4), "error": round(err, 4)})

    max_err = max(e["error"] for e in errors_at_switch)
    c4_results.append({
        "switch_depth": sd,
        "errors": errors_at_switch,
        "max_error": round(max_err, 4)
    })
    print(f"  switch@d={sd}: max_error={max_err:.2%}")

c4_breakdown = None
for r in c4_results:
    if r["max_error"] > 0.50 and c4_breakdown is None:
        c4_breakdown = r["switch_depth"]
print(f"  Breakdown threshold: switch_depth={c4_breakdown}")
all_conditions_data["discontinuous_operator_switching"] = c4_results

# ==========================================================
# CONDITION 5: DEPTH-CHAOTIC RECURSION
# ==========================================================
print("\n--- C5: Depth-Chaotic Recursion ---")
chaos_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
c5_results = []

for cl in chaos_levels:
    # Predictor: uses sequential depth ordering
    p = predictor_emergence("P-A-N", TEST_DEPTH)
    # True: depth order is scrambled proportional to chaos level
    # Effective depth at chaos cl: d_eff = d * (1 + cl * (random - 0.5))
    import random
    random.seed(SEED + int(cl * 100))
    d_eff = TEST_DEPTH * (1.0 + cl * (random.random() - 0.5))
    d_eff = max(1, int(d_eff))
    t = true_emergence("P-A-N", d_eff)
    err = compute_error(p, t)
    c5_results.append({"chaos_level": cl, "pred": round(p, 4), "true": round(t, 4), "error": round(err, 4)})

c5_breakdown = None
for r in c5_results:
    if r["error"] > 0.50 and c5_breakdown is None:
        c5_breakdown = r["chaos_level"]
print(f"  Breakdown threshold: chaos_level={c5_breakdown}")
for r in c5_results:
    print(f"  chaos={r['chaos_level']:.1f}: pred={r['pred']:.4f} true={r['true']:.4f} err={r['error']:.2%}")
all_conditions_data["depth_chaotic_recursion"] = c5_results

# ==========================================================
# CONDITION 6: RECURSIVE PHASE INVERSION
# ==========================================================
print("\n--- C6: Recursive Phase Inversion ---")
inv_depths = [10, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
test_depths_inv = [1, 10, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
c6_results = []

for inv_d in inv_depths:
    errors_at_inv = []
    for td in test_depths_inv:
        p = predictor_emergence("P-A-N", td)
        if td <= inv_d:
            t = true_emergence("P-A-N", td)
        else:
            # Phase inversion: operators become subtractive
            normal = true_emergence("P-A-N", td)
            inverted = 0.05 + (1.0 - normal) * 0.5  # inverted regime
            t = inverted
        err = compute_error(p, t)
        errors_at_inv.append({"depth": td, "pred": round(p, 4), "true": round(t, 4), "error": round(err, 4)})

    max_err = max(e["error"] for e in errors_at_inv)
    c6_results.append({
        "inversion_depth": inv_d,
        "errors": errors_at_inv,
        "max_error": round(max_err, 4)
    })
    print(f"  invert@d={inv_d}: max_error={max_err:.2%}")

c6_breakdown = None
for r in c6_results:
    if r["max_error"] > 0.50 and c6_breakdown is None:
        c6_breakdown = r["inversion_depth"]
print(f"  Breakdown threshold: inversion_depth={c6_breakdown}")
all_conditions_data["recursive_phase_inversion"] = c6_results

# ==========================================================
# CONDITION 7: STOCHASTIC BIFURCATION INJECTION
# ==========================================================
print("\n--- C7: Stochastic Bifurcation Injection ---")
bif_probabilities = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
c7_results = []

for bp in bif_probabilities:
    # Average over multiple stochastic runs
    n_runs = 20
    true_vals = []
    random.seed(SEED + int(bp * 100))
    for run in range(n_runs):
        # At each depth, probability bp of random operator selection
        # This modifies the effective operator weights
        p_branch = random.random()
        if p_branch < bp:
            # Random operator selection
            ops = random.choice(["P", "A", "N", "P-A", "P-N", "A-N", "P-A-N"])
            ps = 1.0 if "P" in ops else 0.0
            a_s = 1.0 if "A" in ops else 0.0
            n_s = 1.0 if "N" in ops else 0.0
            t = true_emergence("P-A-N", TEST_DEPTH, p_scale=ps, a_scale=a_s, n_scale=n_s)
        else:
            t = true_emergence("P-A-N", TEST_DEPTH)
        true_vals.append(t)
    avg_true = sum(true_vals) / len(true_vals)
    p = predictor_emergence("P-A-N", TEST_DEPTH)
    err = compute_error(p, avg_true)
    c7_results.append({"bif_prob": bp, "pred": round(p, 4), "true": round(avg_true, 4), "error": round(err, 4)})

c7_breakdown = None
for r in c7_results:
    if r["error"] > 0.50 and c7_breakdown is None:
        c7_breakdown = r["bif_prob"]
print(f"  Breakdown threshold: bif_prob={c7_breakdown}")
for r in c7_results:
    print(f"  bif_prob={r['bif_prob']:.1f}: pred={r['pred']:.4f} true={r['true']:.4f} err={r['error']:.2%}")
all_conditions_data["stochastic_bifurcation_injection"] = c7_results

# ==========================================================
# COMPUTE METRICS
# ==========================================================
print("\n" + "=" * 60)
print("COMPUTING BREAKDOWN METRICS")
print("=" * 60)

# Metric 1: predictive_breakdown_threshold per condition
breakdown_thresholds = {
    "extreme_operator_amplification": c1_breakdown,
    "asymmetric_recursive_weighting": c2_breakdown,
    "hidden_recursive_coupling": c3_breakdown,
    "discontinuous_operator_switching": c4_breakdown,
    "depth_chaotic_recursion": c5_breakdown,
    "recursive_phase_inversion": c6_breakdown,
    "stochastic_bifurcation_injection": c7_breakdown
}

# Metric 2: bifurcation_error_growth
# Rate of error increase per unit parameter change
def compute_error_growth(data, param_key, error_key="error"):
    if len(data) < 2:
        return 0
    sorted_data = sorted(data, key=lambda x: x[param_key])
    total_growth = 0
    for i in range(1, len(sorted_data)):
        de = sorted_data[i][error_key] - sorted_data[i-1][error_key]
        dp = sorted_data[i][param_key] - sorted_data[i-1][param_key]
        if dp > 0:
            total_growth += de / dp
    return total_growth / (len(sorted_data) - 1)

bifurcation_error_growth = {
    "extreme_operator_amplification": compute_error_growth(c1_results, "amp"),
    "asymmetric_recursive_weighting": compute_error_growth(c2_results, "k_ratio"),
    "hidden_recursive_coupling": compute_error_growth(c3_results, "coupling"),
    "depth_chaotic_recursion": compute_error_growth(c5_results, "chaos_level"),
    "stochastic_bifurcation_injection": compute_error_growth(c7_results, "bif_prob")
}

# Metric 3: uncertainty_inflation_rate
def compute_inflation(data, param_key):
    sorted_data = sorted(data, key=lambda x: x[param_key])
    if len(sorted_data) < 2:
        return 0
    min_err = sorted_data[0]["error"]
    max_err = sorted_data[-1]["error"]
    param_range = sorted_data[-1][param_key] - sorted_data[0][param_key]
    if param_range == 0:
        return 0
    return (max_err - min_err) / param_range

uncertainty_inflation_rate = {
    "extreme_operator_amplification": compute_inflation(c1_results, "amp"),
    "asymmetric_recursive_weighting": compute_inflation(c2_results, "k_ratio"),
    "hidden_recursive_coupling": compute_inflation(c3_results, "coupling"),
    "depth_chaotic_recursion": compute_inflation(c5_results, "chaos_level"),
    "stochastic_bifurcation_injection": compute_inflation(c7_results, "bif_prob")
}

# Metric 4: coupling_nonlinearity_index
# Deviation from linear error growth (higher = more nonlinear)
def compute_nonlinearity(data, param_key):
    sorted_data = sorted(data, key=lambda x: x[param_key])
    if len(sorted_data) < 3:
        return 0
    errors = [d["error"] for d in sorted_data]
    # Perfect linear: mean of first and last
    linear_endpoints = errors[0] + (errors[-1] - errors[0])
    deviations = [abs(errors[i] - (errors[0] + (errors[-1] - errors[0]) * i / (len(errors) - 1)))
                  for i in range(len(errors))]
    return sum(deviations) / len(deviations)

coupling_nonlinearity_index = {
    "extreme_operator_amplification": compute_nonlinearity(c1_results, "amp"),
    "asymmetric_recursive_weighting": compute_nonlinearity(c2_results, "k_ratio"),
    "hidden_recursive_coupling": compute_nonlinearity(c3_results, "coupling"),
    "depth_chaotic_recursion": compute_nonlinearity(c5_results, "chaos_level"),
    "stochastic_bifurcation_injection": compute_nonlinearity(c7_results, "bif_prob")
}

# Metric 5: irreducibility_score
# Error that persists even at extreme parameters / min error
def compute_irreducibility(data, param_key):
    sorted_data = sorted(data, key=lambda x: x[param_key])
    min_err = min(d["error"] for d in sorted_data)
    max_err = max(d["error"] for d in sorted_data)
    return min_err / max_err if max_err > 0 else 0

irreducibility_score = {
    "extreme_operator_amplification": compute_irreducibility(c1_results, "amp"),
    "asymmetric_recursive_weighting": compute_irreducibility(c2_results, "k_ratio"),
    "hidden_recursive_coupling": compute_irreducibility(c3_results, "coupling"),
    "depth_chaotic_recursion": compute_irreducibility(c5_results, "chaos_level"),
    "stochastic_bifurcation_injection": compute_irreducibility(c7_results, "bif_prob")
}

# Metric 6: chaos_transition_depth
# For condition 4 and 6, find the depth after which error stays > 0.50
def find_chaos_transition(c4_data):
    for r in c4_data:
        for e in r["errors"]:
            if e["error"] > 0.50:
                return e["depth"]
    return None

# ==========================================================
# HYPOTHESES EVALUATION
# ==========================================================
print("\n" + "=" * 60)
print("HYPOTHESIS EVALUATION")
print("=" * 60)

h1_pass = c1_breakdown is not None and c1_breakdown > 1.0
h2_pass = c5_breakdown is not None or c4_breakdown is not None
h3_pass = any(v > 0.10 for v in irreducibility_score.values())  # some irreducible uncertainty
h4_pass = c6_breakdown is not None  # phase inversion produces breakdown
h5_pass = sum(1 for v in breakdown_thresholds.values() if v is not None) >= 5

hypotheses = {
    "H1_PredictiveErrorGrowsNearBoundaries": {
        "target": "breakdown thresholds identifiable for operator amplification",
        "value": c1_breakdown,
        "pass": h1_pass
    },
    "H2_EmergenceBifurcationZones": {
        "target": "depth chaos or operator switching creates forecast instability",
        "value": c5_breakdown if c5_breakdown else (c4_breakdown if c4_breakdown else None),
        "pass": h2_pass
    },
    "H3_IrreducibleUncertainty": {
        "target": "some conditions produce irreducible uncertainty",
        "value": max(irreducibility_score.values()),
        "pass": h3_pass
    },
    "H4_PredictiveCoherenceCollapse": {
        "target": "phase inversion causes coherence collapse",
        "value": c6_breakdown,
        "pass": h4_pass
    },
    "H5_FailureRegionsStructurallyInvariant": {
        "target": ">= 5 of 7 conditions have identifiable breakdown thresholds",
        "value": sum(1 for v in breakdown_thresholds.values() if v is not None),
        "pass": h5_pass
    }
}

passes = sum(1 for h in hypotheses.values() if h["pass"])
verdict_map = {5: "BREAKDOWN-STABLE", 4: "BREAKDOWN-BOUNDED",
               3: "BREAKDOWN-DEGRADING", 2: "BREAKDOWN-FAILED",
               1: "BREAKDOWN-FAILED", 0: "BREAKDOWN-FAILED"}
verdict = verdict_map[passes]

# ==========================================================
# SAVE RESULTS
# ==========================================================
results = {
    "phase": 408,
    "seed": SEED,
    "predictor_params": {"k": PREDICTOR_K, "weights": PREDICTOR_WEIGHTS},
    "true_params": {"k": TRUE_K, "weights": TRUE_WEIGHTS},
    "conditions_data": all_conditions_data,
    "breakdown_thresholds": {k: v for k, v in breakdown_thresholds.items() if v is not None},
    "metrics": {
        "bifurcation_error_growth": {k: round(v, 4) for k, v in bifurcation_error_growth.items()},
        "uncertainty_inflation_rate": {k: round(v, 4) for k, v in uncertainty_inflation_rate.items()},
        "coupling_nonlinearity_index": {k: round(v, 4) for k, v in coupling_nonlinearity_index.items()},
        "irreducibility_score": {k: round(v, 4) for k, v in irreducibility_score.items()}
    },
    "hypotheses": hypotheses,
    "hypothesis_summary": f"{passes}/5 hypotheses PASS",
    "pass_count": passes,
    "total_count": 5,
    "verdict": verdict
}

results_path = os.path.join(SCRIPT_DIR, "phase408_breakdown_results.json")
with open(results_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved: {results_path}")

# Save domain-level CSV
csv_path = os.path.join(SCRIPT_DIR, "phase408_breakdown_metrics.csv")
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["condition", "breakdown_threshold", "error_growth", "inflation_rate", "nonlinearity", "irreducibility"])
    for cond, thresh in breakdown_thresholds.items():
        eg = bifurcation_error_growth.get(cond, "N/A")
        inf = uncertainty_inflation_rate.get(cond, "N/A")
        nl = coupling_nonlinearity_index.get(cond, "N/A")
        ir = irreducibility_score.get(cond, "N/A")
        w.writerow([cond, thresh if thresh else "N/A",
                    round(eg, 4) if isinstance(eg, float) else eg,
                    round(inf, 4) if isinstance(inf, float) else inf,
                    round(nl, 4) if isinstance(nl, float) else nl,
                    round(ir, 4) if isinstance(ir, float) else ir])
print(f"Metrics CSV: {csv_path}")

print(f"\n{'='*60}")
print(f"PHASE 408 VERDICT: {verdict}")
print(f"Hypotheses: {passes}/5 PASS")
print(f"Breakdown thresholds found: {sum(1 for v in breakdown_thresholds.values() if v is not None)}/7")
for h_name, h_data in hypotheses.items():
    s = "PASS" if h_data["pass"] else "FAIL"
    print(f"  {h_name}: {h_data['value']} vs {h_data['target']} -> {s}")
print(f"{'='*60}")
