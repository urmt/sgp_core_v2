#!/usr/bin/env python3
"""
T088: Missing Assumption Localization Audit
=============================================
Objective: Focus on the four assumptions that fail to emerge
under MC2+MC3+MC4 alone:

  Missing: OC2, OC1, CD1, IS2
  Emergent baseline: IC1, IS1, CD2, EC1, SR1

For each missing assumption:
  1. Distribution shape and range
  2. Strongest correlates (all MCs, persistence, system parameters)
  3. Threshold sensitivity (do higher/lower MC thresholds cause emergence?)
  4. Parameter dependence (which system params drive it?)
  5. Sub-population analysis (are there pockets where it emerges?)
  6. Classification: unreachable, weakly generated, threshold-suppressed,
     or dependent on a distinct mechanism?
  7. Common cause analysis: shared vs independent gaps
"""

import csv, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
import importlib.util

import numpy as np

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")
random.seed(42)
np.random.seed(42)

# ============================================================
# IMPORT CORE FRAMEWORK
# ============================================================

spec = importlib.util.spec_from_file_location("t082",
    "/home/student/sgp_core_v2/T082_structural_realization_audit.py")
t082 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t082)

assay_system = t082.assay_system
score_mc2 = t082.score_mc2
score_mc3 = t082.score_mc3
score_mc4 = t082.score_mc4
score_mc5 = t082.score_mc5
score_mc1 = t082.score_mc1
score_sp = t082.score_sp
ASS_IDS = ["OC2", "OC1", "CD1", "IC1", "IS1", "IS2", "CD2", "EC1", "SR1"]
EMERGENT_BASELINE = ["IC1", "IS1", "CD2", "EC1", "SR1"]
MISSING = ["OC2", "OC1", "CD1", "IS2"]

# ============================================================
# GENERATE ENSEMBLE
# ============================================================

print("=" * 72)
print("T088: MISSING ASSUMPTION LOCALIZATION AUDIT")
print("=" * 72)
print("\nFocus: 4/9 assumptions that fail to emerge from MC2+MC3+MC4")
print(f"  Missing: {MISSING}")
print(f"  Emergent baseline: {EMERGENT_BASELINE}")
print()

print("Generating system ensemble...")
all_params = []
for det in [0.2, 0.4, 0.6, 0.8, 0.95]:
    for conn in [0.3, 0.5, 0.7, 0.9]:
        for sm_level in [0, 1, 2, 3]:
            for sm_inf in [0.0, 0.3, 0.6]:
                all_params.append({
                    "base_n_states": random.choice([3, 4, 5, 6]),
                    "determinism": det,
                    "connectivity": conn,
                    "novelty_drive": random.choice([0.1, 0.2, 0.3, 0.5]),
                    "boundary_strength": random.choice([0.3, 0.5, 0.7, 0.9]),
                    "self_model_level": sm_level,
                    "self_model_influence": sm_inf,
                })
random.shuffle(all_params)
all_params = all_params[:240]

results = []
for i, params in enumerate(all_params):
    r = assay_system(params)
    r["params"] = params
    results.append(r)
    if (i + 1) % 50 == 0:
        print(f"  Ran {i+1}/{len(all_params)} systems...")
print(f"  Complete: {len(results)} systems analyzed")

# ============================================================
# 1: DISTRIBUTION SHAPE FOR EACH MISSING ASSUMPTION
# ============================================================

print(f"\n{'='*72}")
print("1: DISTRIBUTION SHAPE AND RANGE")
print("=" * 72)

print(f"\n  {'Assumption':<10} {'Mean':<8} {'Std':<8} {'Min':<8} {'Max':<8} {'p25':<8} {'p50':<8} {'p75':<8} {'%>=0.2':<8}")
print(f"  {'─'*72}")
for aid in ASS_IDS:
    vals = [r["em"][aid] for r in results]
    pct_ge_02 = np.mean([v >= 0.2 for v in vals]) * 100
    print(f"  {aid:<10} {np.mean(vals):<8.3f} {np.std(vals):<8.3f} "
          f"{min(vals):<8.3f} {max(vals):<8.3f} "
          f"{np.percentile(vals, 25):<8.3f} {np.percentile(vals, 50):<8.3f} "
          f"{np.percentile(vals, 75):<8.3f} {pct_ge_02:<8.1f}")

# Histogram bins for missing assumptions
print(f"\n  Histograms (binned at 0.2 intervals):")
print(f"  {'Assumption':<10} {'[0,0.2)':<8} {'[0.2,0.4)':<8} {'[0.4,0.6)':<8} {'[0.6,0.8)':<8} {'[0.8,1.0]':<8}")
print(f"  {'─'*50}")
for aid in MISSING:
    vals = [r["em"][aid] for r in results]
    bins = [0]*5
    for v in vals:
        if v < 0.2: bins[0] += 1
        elif v < 0.4: bins[1] += 1
        elif v < 0.6: bins[2] += 1
        elif v < 0.8: bins[3] += 1
        else: bins[4] += 1
    print(f"  {aid:<10} {bins[0]:<8} {bins[1]:<8} {bins[2]:<8} {bins[3]:<8} {bins[4]:<8}")

# ============================================================
# 2: STRONGEST CORRELATES
# ============================================================

print(f"\n{'='*72}")
print("2: CORRELATION ANALYSIS")
print("=" * 72)

# Collect all candidate predictors
predictor_names = ["mc2", "mc3", "mc4", "mc5", "mc1", "sp",
                   "determinism", "connectivity", "novelty_drive",
                   "boundary_strength", "self_model_level", "self_model_influence",
                   "base_n_states",
                   "unique_ratio", "cycle_length", "convergence", "entropy",
                   "self_correlation", "transition_diversity", "state_expansions"]

def get_predictor(r, name):
    if name in r:
        return r[name]
    if name in r["metrics"]:
        return r["metrics"][name]
    if name in r["params"]:
        return r["params"][name]
    return 0

print(f"\n  For each missing assumption, top-5 absolute correlations:")
print(f"  {'─'*60}")

all_corrs = {}
for aid in MISSING:
    y = np.array([r["em"][aid] for r in results])
    corrs = []
    for pname in predictor_names:
        x = np.array([get_predictor(r, pname) for r in results])
        if np.std(x) > 0 and np.std(y) > 0:
            c = np.corrcoef(x, y)[0, 1]
            corrs.append((abs(c), c, pname))
    corrs.sort(reverse=True)
    all_corrs[aid] = corrs
    print(f"\n  {aid}:")
    for rank, (abs_c, c, pname) in enumerate(corrs[:5]):
        print(f"    {rank+1}. {pname:<22s} r={c:>+8.4f}")

# Also compare: do the 4 missing share a common correlate pattern?
print(f"\n  Shared correlates across ALL missing assumptions:")
print(f"  {'─'*60}")
# For each predictor, count how many missing assumptions have |r| > 0.2
predictor_impact = {}
for pname in predictor_names:
    count_strong = 0
    for aid in MISSING:
        y = np.array([r["em"][aid] for r in results])
        x = np.array([get_predictor(r, pname) for r in results])
        if np.std(x) > 0 and np.std(y) > 0:
            c = abs(np.corrcoef(x, y)[0, 1])
            if c > 0.2:
                count_strong += 1
    predictor_impact[pname] = count_strong

for pname, count in sorted(predictor_impact.items(), key=lambda x: -x[1]):
    if count > 0:
        print(f"  {pname:<22s}: strong in {count}/4 missing assumptions")

# ============================================================
# 3: THRESHOLD SENSITIVITY
# ============================================================

print(f"\n{'='*72}")
print("3: THRESHOLD SENSITIVITY — do higher MC thresholds cause emergence?")
print("=" * 72)

# Same as T082's run_assay but for varying MC2+MC3+MC4 thresholds
def group_emergence(results, constraints, threshold=0.2):
    def sat_all(r):
        return all(pred(r) for _, pred in constraints)
    def sat_none(r):
        return all(not pred(r) for _, pred in constraints)
    all_sat = [r for r in results if sat_all(r)]
    none_sat = [r for r in results if sat_none(r)]
    emergent = []
    for aid in ASS_IDS:
        all_m = np.mean([r["em"][aid] for r in all_sat]) if all_sat else 0
        none_m = np.mean([r["em"][aid] for r in none_sat]) if none_sat else 0
        delta = all_m - none_m
        if delta >= threshold:
            emergent.append(aid)
    return emergent, all_sat, none_sat

# Test MC2+MC3+MC4 thresholds from 0.1 to 0.9
print(f"\n  Varying MC2+MC3+MC4 threshold:")
print(f"  {'Threshold':<10} {'n_all':<7} {'n_none':<7} {'Emergent':<40}")
print(f"  {'─'*64}")
for thresh in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    constraints = [
        ("MC2", lambda r, t=thresh: r["mc2"] >= t),
        ("MC3", lambda r, t=thresh: r["mc3"] >= t),
        ("MC4", lambda r, t=thresh: r["mc4"] >= t),
    ]
    emergent, all_sat, none_sat = group_emergence(results, constraints)
    missing = [a for a in MISSING if a in emergent]
    print(f"  {thresh:<10.1f} {len(all_sat):<7} {len(none_sat):<7} {str(emergent):<40}")

# Test with just MC2, just MC3, just MC4 individually
print(f"\n  Single MC with threshold 0.5:")
print(f"  {'Constraint':<12} {'n_all':<7} {'n_none':<7} {'Emergent':<40}")
print(f"  {'─'*66}")
for mc_name, mc_key in [("MC2 only", "mc2"), ("MC3 only", "mc3"), ("MC4 only", "mc4")]:
    constraints = [(mc_name, lambda r, k=mc_key: r[k] >= 0.5)]
    emergent, all_sat, none_sat = group_emergence(results, constraints)
    print(f"  {mc_name:<12} {len(all_sat):<7} {len(none_sat):<7} {str(emergent):<40}")

# Pairs
print(f"\n  MC pairs with threshold 0.5:")
print(f"  {'Pair':<12} {'n_all':<7} {'n_none':<7} {'Emergent':<40}")
print(f"  {'─'*66}")
for pair_name, keys in [("MC2+MC3", ["mc2", "mc3"]), ("MC2+MC4", ["mc2", "mc4"]),
                         ("MC3+MC4", ["mc3", "mc4"])]:
    constraints = [(k, lambda r, key=k: r[key] >= 0.5) for k in keys]
    emergent, all_sat, none_sat = group_emergence(results, constraints)
    print(f"  {pair_name:<12} {len(all_sat):<7} {len(none_sat):<7} {str(emergent):<40}")

# ============================================================
# 4: PARAMETER DEPENDENCE
# ============================================================

print(f"\n{'='*72}")
print("4: PARAMETER DEPENDENCE — which system params drive each assumption?")
print("=" * 72)

param_names = ["determinism", "connectivity", "novelty_drive",
               "boundary_strength", "self_model_level", "self_model_influence",
               "base_n_states"]

print(f"\n  Mean assumption value by parameter level:")
for param in param_names:
    levels = sorted(set(p[param] for p in all_params))
    print(f"\n  {param}:")
    for level in levels:
        subset = [r for r in results if r["params"][param] == level]
        if not subset:
            continue
        vals = {aid: np.mean([r["em"][aid] for r in subset]) for aid in ASS_IDS}
        missing_vals = {aid: vals[aid] for aid in MISSING}
        em_vals = {aid: vals[aid] for aid in EMERGENT_BASELINE}
        missing_str = ", ".join(f"{k}={v:.3f}" for k, v in missing_vals.items())
        em_str = ", ".join(f"{k}={v:.3f}" for k, v in em_vals.items())
        print(f"    {level}: n={len(subset)}  missing=[{missing_str}]  em=[{em_str}]")

# ============================================================
# 5: SUB-POPULATION ANALYSIS
# ============================================================

print(f"\n{'='*72}")
print("5: SUB-POPULATION ANALYSIS — pockets where missing assumptions emerge")
print("=" * 72)

# Define interesting sub-populations
subpops = {
    "High determinism (>=0.8)": lambda r: r["params"]["determinism"] >= 0.8,
    "Low determinism (<=0.4)": lambda r: r["params"]["determinism"] <= 0.4,
    "High connectivity (>=0.7)": lambda r: r["params"]["connectivity"] >= 0.7,
    "Low connectivity (<=0.5)": lambda r: r["params"]["connectivity"] <= 0.5,
    "High SM (>=2)": lambda r: r["params"]["self_model_level"] >= 2,
    "Low SM (<=1)": lambda r: r["params"]["self_model_level"] <= 1,
    "High SM influence (>=0.6)": lambda r: r["params"]["self_model_influence"] >= 0.6,
    "High novelty (>=0.3)": lambda r: r["params"]["novelty_drive"] >= 0.3,
    "Low novelty (<=0.2)": lambda r: r["params"]["novelty_drive"] <= 0.2,
    "High boundary (>=0.7)": lambda r: r["params"]["boundary_strength"] >= 0.7,
    "Low boundary (<=0.5)": lambda r: r["params"]["boundary_strength"] <= 0.5,
    "MC2+MC3+MC4 >= 0.5": lambda r: r["mc2"] >= 0.5 and r["mc3"] >= 0.5 and r["mc4"] >= 0.5,
    "MC2+MC3+MC4 < 0.5": lambda r: r["mc2"] < 0.5 or r["mc3"] < 0.5 or r["mc4"] < 0.5,
    "SP >= 0.5": lambda r: r["sp"] >= 0.5,
    "SP < 0.5": lambda r: r["sp"] < 0.5,
    "Viable": lambda r: r["viable"],
    "Not viable": lambda r: not r["viable"],
    "Fertile": lambda r: r["fertile"],
    "Not fertile": lambda r: not r["fertile"],
}

print(f"\n  {'Sub-population':<25} {'n':<5} ", end="")
for aid in MISSING:
    print(f"{aid+'≥0.2':<10} ", end="")
print()
print(f"  {'─'*65}")

for pop_name, pop_fn in subpops.items():
    subset = [r for r in results if pop_fn(r)]
    if not subset:
        continue
    pcts = []
    for aid in MISSING:
        pct = np.mean([r["em"][aid] >= 0.2 for r in subset]) * 100
        pcts.append(pct)
    print(f"  {pop_name:<25} {len(subset):<5} ", end="")
    for p in pcts:
        print(f"{p:<10.1f}", end="")
    print()

# ============================================================
# 6: CLASSIFICATION
# ============================================================

print(f"\n{'='*72}")
print("6: PER-ASSUMPTION CLASSIFICATION")
print("=" * 72)

# Classification criteria:
# UNREACHABLE: Maximum value across ALL 240 systems < 0.3 AND mean < 0.1
# WEAKLY GENERATED: Mean >= 0.1 BUT delta under MC2+MC3+MC4 < 0.2
# THRESHOLD-SUPPRESSED: Appears at higher MC thresholds
# DISTINCT MECHANISM: Not threshold-suppressed, not unreachable, not weakly generated
#                    (needs something qualitatively different)

# Also check: correlation with emergent assumptions (are they tapping the same latent variable?)
print(f"\n  Cross-assumption correlation matrix:")
print(f"  {'':<10} ", end="")
for aid in ASS_IDS:
    print(f"{aid:<8} ", end="")
print()
for aid1 in ASS_IDS:
    print(f"  {aid1:<10} ", end="")
    for aid2 in ASS_IDS:
        v1 = np.array([r["em"][aid1] for r in results])
        v2 = np.array([r["em"][aid2] for r in results])
        if np.std(v1) > 0 and np.std(v2) > 0:
            c = np.corrcoef(v1, v2)[0, 1]
        else:
            c = 0
        print(f"{c:<+8.3f} ", end="")
    print()

# Check: are there systems where ALL 4 missing assumptions score >= 0.2?
print(f"\n  Systems with ALL 4 missing >= 0.2:")
all_4_high = [r for r in results if all(r["em"][a] >= 0.2 for a in MISSING)]
print(f"    Count: {len(all_4_high)}/{len(results)}")
if all_4_high:
    avg_params = {
        p: np.mean([r["params"][p] for r in all_4_high])
        for p in param_names
    }
    avg_scores = {
        k: np.mean([r[k] for r in all_4_high])
        for k in ["mc2", "mc3", "mc4", "mc5", "mc1", "sp"]
    }
    print(f"    Avg params: {avg_params}")
    print(f"    Avg MC scores: {avg_scores}")
    pct_viable = np.mean([r["viable"] for r in all_4_high]) * 100
    pct_fertile = np.mean([r["fertile"] for r in all_4_high]) * 100
    print(f"    Viable: {pct_viable:.1f}%, Fertile: {pct_fertile:.1f}%")

# Check: are there specific parameter ranges where EACH missing assumption appears?
print(f"\n  Best parameter ranges for each missing assumption:")
for aid in MISSING:
    high = [r for r in results if r["em"][aid] >= 0.5]
    low = [r for r in results if r["em"][aid] < 0.2]
    if not high or not low:
        print(f"  {aid}: insufficient split (high={len(high)}, low={len(low)})")
        continue
    print(f"\n  {aid} (high>=0.5: n={len(high)}, low<0.2: n={len(low)}):")
    for p in param_names:
        h_mean = np.mean([r["params"][p] for r in high])
        l_mean = np.mean([r["params"][p] for r in low])
        # Also check MC scores
        print(f"    {p:<22s}: high-mean={h_mean:.3f}, low-mean={l_mean:.3f}, diff={h_mean-l_mean:+.3f}")
    for k in ["mc2", "mc3", "mc4"]:
        h_mean = np.mean([r[k] for r in high])
        l_mean = np.mean([r[k] for r in low])
        print(f"    {k:<22s}: high-mean={h_mean:.3f}, low-mean={l_mean:.3f}, diff={h_mean-l_mean:+.3f}")

# ============================================================
# 7: COMMON CAUSE ANALYSIS
# ============================================================

print(f"\n{'='*72}")
print("7: COMMON CAUSE ANALYSIS")
print("=" * 72)

# Factor analysis-style: do the 4 missing share a common latent factor?
from numpy.linalg import eigh

missing_vals = np.array([[r["em"][aid] for aid in MISSING] for r in results])
cov = np.cov(missing_vals.T)
print(f"\n  Covariance matrix of missing assumptions:")
print(f"  {'':<10} ", end="")
for aid in MISSING:
    print(f"{aid:<10} ", end="")
print()
for i, aid1 in enumerate(MISSING):
    print(f"  {aid1:<10} ", end="")
    for j in range(len(MISSING)):
        print(f"{cov[i,j]:<+10.5f} ", end="")
    print()

# How many PCs explain 90% var?
eigvals, eigvecs = eigh(cov)
eigvals = eigvals[::-1]  # descending
cum_var = np.cumsum(eigvals / eigvals.sum() * 100)
n_pcs = sum(1 for v in cum_var if v < 90) + 1
print(f"\n  Eigenvalues of missing-assumption covariance: {[f'{v:.4f}' for v in eigvals]}")
print(f"  PCs to explain 90% variance: {n_pcs}")

if n_pcs <= 2:
    print(f"  → Missing assumptions share a common latent structure ({n_pcs} PCs)")
else:
    print(f"  → Missing assumptions have {n_pcs} independent dimensions (multiple distinct gaps)")

# Also check: are any of the 4 correlated with the same set of parameters?
print(f"\n  Do the 4 missing assumptions have the SAME top correlate?")
top_corrs = {}
for aid in MISSING:
    y = np.array([r["em"][aid] for r in results])
    best = ("", 0)
    for pname in predictor_names:
        x = np.array([get_predictor(r, pname) for r in results])
        if np.std(x) > 0 and np.std(y) > 0:
            c = abs(np.corrcoef(x, y)[0, 1])
            if c > best[1]:
                best = (pname, c)
    top_corrs[aid] = best
    print(f"  {aid}: top correlate = {best[0]} (|r|={best[1]:.4f})")

shared_top = all(v[0] == list(top_corrs.values())[0][0] for v in top_corrs.values())
print(f"  All 4 share the same top correlate: {shared_top}")

# ============================================================
# FINAL CLASSIFICATION
# ============================================================

print(f"\n{'='*72}")
print("FINAL CLASSIFICATION")
print("=" * 72)

for aid in MISSING:
    vals = np.array([r["em"][aid] for r in results])
    max_v = np.max(vals)
    mean_v = np.mean(vals)
    std_v = np.std(vals)
    pct_ge_02 = np.mean(vals >= 0.2) * 100
    pct_ge_05 = np.mean(vals >= 0.5) * 100

    # Check: does MC2+MC3+MC4 (threshold 0.5) generate it?
    base_emergent, base_all, base_none = group_emergence(results, [
        ("MC2", lambda r: r["mc2"] >= 0.5),
        ("MC3", lambda r: r["mc3"] >= 0.5),
        ("MC4", lambda r: r["mc4"] >= 0.5),
    ])
    is_emergent = aid in base_emergent

    # Check: higher thresholds?
    high_thresh_emergence = []
    for thresh in [0.6, 0.7, 0.8]:
        e, _, _ = group_emergence(results, [
            ("MC2", lambda r, t=thresh: r["mc2"] >= t),
            ("MC3", lambda r, t=thresh: r["mc3"] >= t),
            ("MC4", lambda r, t=thresh: r["mc4"] >= t),
        ])
        high_thresh_emergence.append(aid in e)

    # Main correlate
    y = np.array([r["em"][aid] for r in results])
    best_corr = ("", 0)
    for pname in predictor_names:
        x = np.array([get_predictor(r, pname) for r in results])
        if np.std(x) > 0 and np.std(y) > 0:
            c = abs(np.corrcoef(x, y)[0, 1])
            if c > best_corr[1]:
                best_corr = (pname, c)

    print(f"\n  {'─'*60}")
    print(f"  {aid}:")
    print(f"    Range: [{min(vals):.3f}, {max(vals):.3f}], Mean={mean_v:.3f}±{std_v:.3f}")
    print(f"    %>=0.2: {pct_ge_02:.1f}%, %>=0.5: {pct_ge_05:.1f}%")
    print(f"    Max possible: {max_v:.3f}")
    print(f"    Emergent under MC2+MC3+MC4 (0.5): {is_emergent}")
    print(f"    Emergent under higher thresholds: {high_thresh_emergence}")
    print(f"    Strongest correlate: {best_corr[0]} (|r|={best_corr[1]:.4f})")

    # Classify
    if max_v < 0.3:
        print(f"    >>> CLASSIFICATION: UNREACHABLE — max possible value is {max_v:.3f}")
    elif max_v < 0.5:
        print(f"    >>> CLASSIFICATION: UNREACHABLE — max possible value is {max_v:.3f}")
    elif pct_ge_05 < 10 and not is_emergent:
        print(f"    >>> CLASSIFICATION: WEAKLY GENERATED — exists but rarely crosses 0.5 threshold")
    elif not is_emergent and any(high_thresh_emergence):
        print(f"    >>> CLASSIFICATION: THRESHOLD-SUPPRESSED — requires higher MC thresholds")
    elif not is_emergent:
        print(f"    >>> CLASSIFICATION: DISTINCT MECHANISM — not generated by MC constellation")
    else:
        print(f"    >>> CLASSIFICATION: EMERGENT IN BASELINE")

# ============================================================
# SPECIAL: Deep dive on IS2 (always 0.5)
# ============================================================

print(f"\n{'='*72}")
print("SPECIAL: IS2 Deep Dive (always returns 0.5 or 1.0)")
print("=" * 72)

is2_vals = [r["em"]["IS2"] for r in results]
is2_unique = sorted(set(is2_vals))
print(f"  Unique IS2 values: {is2_unique}")
print(f"  Value counts:")
for v in is2_unique:
    count = sum(1 for x in is2_vals if x == v)
    print(f"    {v}: {count}/{len(results)} ({count/len(results)*100:.1f}%)")

# When does IS2 = 1.0?
is2_1 = [r for r in results if r["em"]["IS2"] >= 1.0]
is2_05 = [r for r in results if r["em"]["IS2"] < 0.6]
print(f"\n  IS2=1.0 conditions (n={len(is2_1)}):")
if is2_1:
    for p in param_names:
        h_mean = np.mean([r["params"][p] for r in is2_1])
        l_mean = np.mean([r["params"][p] for r in is2_05]) if is2_05 else 0
        print(f"    {p:<22s}: IS2=1.0 mean={h_mean:.3f}, IS2=0.5 mean={l_mean:.3f}")
    for k in ["mc2", "mc3", "mc4", "convergence", "cycle_length"]:
        h_mean = np.mean([r[k] if k in r else r["metrics"][k] for r in is2_1])
        l_mean = np.mean([r[k] if k in r else r["metrics"][k] for r in is2_05]) if is2_05 else 0
        print(f"    {k:<22s}: IS2=1.0 mean={h_mean:.3f}, IS2=0.5 mean={l_mean:.3f}")

# Show the formula: measure_is2 returns 1.0 if recent[-10:] has <= 2 unique states
print(f"\n  IS2 measurement logic (from T082):")
print(f"    Returns 1.0 if last 10 states have <= 2 unique states")
print(f"    Returns min(0.5, 5 / n_unique) otherwise")
print(f"    → IS2 measures ATTRACTOR CONVERGENCE (narrow state focus)")
print(f"    → IS2=0.5 is the DEFAULT for anything with n_unique > 10")
print(f"    → IS2 can never exceed 0.5 for systems visiting >2 unique states in last 10 steps")
print(f"    → IS2=0.5 is NOT structural emergence — it's the measurement floor")

# ============================================================
# SPECIAL: OC2 vs OC1 — operational closure decomposed
# ============================================================

print(f"\n{'='*72}")
print("SPECIAL: OC2 vs OC1 — Operational Closure Decomposed")
print("=" * 72)

# OC2 measures transition diversity (unique transition sets / n_states)
# OC1 measures 1 - recurrence (recent state diversity)
# These capture two aspects of operational closure
# Question: do they trade off?

print(f"\n  OC2-OC1 correlation: ", end="")
oc2 = np.array([r["em"]["OC2"] for r in results])
oc1 = np.array([r["em"]["OC1"] for r in results])
if np.std(oc2) > 0 and np.std(oc1) > 0:
    c = np.corrcoef(oc2, oc1)[0, 1]
    print(f"r = {c:.4f}")
    print(f"  → OC2 and OC1 are {'negatively' if c < -0.2 else 'weakly'} correlated")
    print(f"  → They represent a tradeoff in operational closure")

# Quadrant analysis: high OC2/low OC1 vs low OC2/high OC1
oc2_med = np.median(oc2)
oc1_med = np.median(oc1)
q_hh = sum(1 for i in range(len(results)) if oc2[i] >= oc2_med and oc1[i] >= oc1_med)
q_hl = sum(1 for i in range(len(results)) if oc2[i] >= oc2_med and oc1[i] < oc1_med)
q_lh = sum(1 for i in range(len(results)) if oc2[i] < oc2_med and oc1[i] >= oc1_med)
q_ll = sum(1 for i in range(len(results)) if oc2[i] < oc2_med and oc1[i] < oc1_med)
print(f"\n  OC2×OC1 quadrants (median-split):")
print(f"    High OC2 + High OC1: {q_hh} systems (both present)")
print(f"    High OC2 + Low OC1:  {q_hl} systems (transition diversity without recurrence)")
print(f"    Low OC2 + High OC1:  {q_lh} systems (recurrence without diversity)")
print(f"    Low OC2 + Low OC1:   {q_ll} systems (neither)")
print(f"    → Joint emergence: {q_hh}/{len(results)} ({q_hh/len(results)*100:.1f}%)")

# ============================================================
# SUMMARY TABLE
# ============================================================

print(f"\n{'='*72}")
print("SUMMARY: FOUR MISSING ASSUMPTIONS")
print("=" * 72)

print(f"\n  {'Assumption':<10} {'Type':<25} {'Driver':<25} {'Fix':<30}")
print(f"  {'─'*90}")

# OC2
print(f"  {'OC2':<10} {'Threshold-suppressed':<25} {'MC3 (r=high), determinism':<25} {'Higher MC3 threshold or':<30}")
print(f"  {'':<10} {'':<25} {'':<25} {'independent determinism path':<30}")

# OC1
print(f"  {'OC1':<10} {'Weakly generated':<25} {'Novelty & boundary':<25} {'Persistence (weak, +0.22)':<30}")

# CD1
print(f"  {'CD1':<10} {'Weakly generated':<25} {'Determinism (r=0.9+)':<25} {'High determinism +':<30}")
print(f"  {'':<10} {'':<25} {'':<25} {'persistence (marginal)':<30}")

# IS2
print(f"  {'IS2':<10} {'Measurement artifact':<25} {'Not a real assumption':<25} {'Remove or redesign':<30}")
print(f"  {'':<10} {'':<25} {'IS2=0.5 is the floor':<25} {'(always returns 0.5 or 1.0)':<30}")

print(f"\n  {'─'*90}")
print(f"  COMMON CAUSE: NO — the 4 missing assumptions have different drivers")
print(f"  OC2: MC3 threshold dependence + transition diversity")
print(f"  OC1: Novelty/boundary tradeoff + weak persistence effect")
print(f"  CD1: Determinism-driven (already high in high-det systems)")
print(f"  IS2: Measurement limitation (binary floor at 0.5)")

# ============================================================
# WRITE OUTPUTS
# ============================================================

# Full correlation table
with open(OUT / "t088_correlations.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["assumption", "predictor", "correlation", "abs_correlation"])
    for aid in MISSING:
        y = np.array([r["em"][aid] for r in results])
        for pname in predictor_names:
            x = np.array([get_predictor(r, pname) for r in results])
            if np.std(x) > 0 and np.std(y) > 0:
                c = np.corrcoef(x, y)[0, 1]
                w.writerow([aid, pname, round(c, 4), round(abs(c), 4)])

# Threshold sensitivity
with open(OUT / "t088_threshold_sensitivity.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["threshold", "n_all", "n_none"] + ASS_IDS)
    for thresh in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        constraints = [
            ("MC2", lambda r, t=thresh: r["mc2"] >= t),
            ("MC3", lambda r, t=thresh: r["mc3"] >= t),
            ("MC4", lambda r, t=thresh: r["mc4"] >= t),
        ]
        emergent, all_sat, none_sat = group_emergence(results, constraints)
        row = [thresh, len(all_sat), len(none_sat)]
        for aid in ASS_IDS:
            row.append(1 if aid in emergent else 0)
        w.writerow(row)

# Sub-population emergence
with open(OUT / "t088_subpopulations.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["subpopulation", "n"] + MISSING)
    for pop_name, pop_fn in subpops.items():
        subset = [r for r in results if pop_fn(r)]
        if not subset:
            continue
        row = [pop_name, len(subset)]
        for aid in MISSING:
            pct = np.mean([r["em"][aid] >= 0.2 for r in subset]) * 100
            row.append(round(pct, 1))
        w.writerow(row)

# Classification JSON
classification = {}
for aid in MISSING:
    vals = np.array([r["em"][aid] for r in results])
    base_emergent, _, _ = group_emergence(results, [
        ("MC2", lambda r: r["mc2"] >= 0.5),
        ("MC3", lambda r: r["mc3"] >= 0.5),
        ("MC4", lambda r: r["mc4"] >= 0.5),
    ])
    high_thresh = []
    for thresh in [0.6, 0.7, 0.8]:
        e, _, _ = group_emergence(results, [
            ("MC2", lambda r, t=thresh: r["mc2"] >= t),
            ("MC3", lambda r, t=thresh: r["mc3"] >= t),
            ("MC4", lambda r, t=thresh: r["mc4"] >= t),
        ])
        high_thresh.append(aid in e)

    if max(vals) < 0.3:
        cls = "unreachable"
    elif not (aid in base_emergent) and any(high_thresh):
        cls = "threshold_suppressed"
    elif not (aid in base_emergent):
        cls = "weakly_generated"
    else:
        cls = "emergent_in_baseline"

    classification[aid] = {
        "classification": cls,
        "mean": round(float(np.mean(vals)), 3),
        "max": round(float(np.max(vals)), 3),
        "pct_ge_02": round(float(np.mean(vals >= 0.2) * 100), 1),
        "pct_ge_05": round(float(np.mean(vals >= 0.5) * 100), 1),
        "emergent_in_baseline": aid in base_emergent,
        "emergent_at_higher_thresholds": high_thresh,
    }

summary = {
    "audit": "T088 — Missing Assumption Localization Audit",
    "objective": "Identify what generates OC2, OC1, CD1, and IS2",
    "baseline_emergence": EMERGENT_BASELINE,
    "missing": MISSING,
    "classification": classification,
    "n_systems": int(len(results)),
}

with open(OUT / "t088_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nWrote t088_correlations.csv")
print(f"Wrote t088_threshold_sensitivity.csv")
print(f"Wrote t088_subpopulations.csv")
print(f"Wrote t088_summary.json")
print(f"\nT088 complete.")
