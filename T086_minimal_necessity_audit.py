#!/usr/bin/env python3
"""
T086: Minimal Necessity Audit
==============================
Question: Is persistence genuinely fundamental (principle),
one member of an equivalence class (implementation),
or a measurement artifact?

Design:
  Import core framework from T082 (GeneratedSystem, assay_system, run_assay,
  scoring functions, measurement functions).
  Add 5 alternative persistence mechanisms:
    SI — State Inertia: momentum in state transitions (autocorrelation)
    SB — Structural Bonds: transition matrix concentration
    TA — Temporal Averaging: rolling-window entropy reduction
    CQ — Conservation Quantity: stability of abstract state "potential"
    FM — Fixed-Point Memory: convergence to attractor states

  For each alternative, test marginal effect:
    all:  MC2>=0.5, MC3>=0.5, MC4>=0.5, P>=0.5
    none: MC2>=0.5, MC3>=0.5, MC4>=0.5, P<0.5
  This isolates the marginal effect of adding P to the base
  MC2+MC3+MC4 constellation.

  Verdict criteria:
    PRINCIPLE:  Consistent positive marginal deltas (>=0.2) across all 5
                alternatives for >=5/9 assumptions.
    IMPLEMENTATION: 2-4 alternatives produce positive marginal deltas.
    ARTIFACT:  <=1 alternative produces positive marginal deltas.
              AND/OR baseline none-group already scores high.
"""

import csv, json, math, itertools, random
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")
random.seed(42)
np.random.seed(42)

# ============================================================
# IMPORT CORE FRAMEWORK FROM T082
# ============================================================

import importlib.util
spec = importlib.util.spec_from_file_location("t082",
    "/home/student/sgp_core_v2/T082_structural_realization_audit.py")
t082 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t082)

# Re-export what we need
GeneratedSystem = t082.GeneratedSystem
score_mc2 = t082.score_mc2
score_mc3 = t082.score_mc3
score_mc4 = t082.score_mc4
score_mc5 = t082.score_mc5
score_mc1 = t082.score_mc1
score_sp = t082.score_sp
measure_oc2 = t082.measure_oc2
measure_oc1 = t082.measure_oc1
measure_cd1 = t082.measure_cd1
measure_ic1 = t082.measure_ic1
measure_is1 = t082.measure_is1
measure_is2 = t082.measure_is2
measure_cd2 = t082.measure_cd2
measure_ec1 = t082.measure_ec1
measure_sr1 = t082.measure_sr1
detect_mechanisms = t082.detect_mechanisms
compute_coherence = t082.compute_coherence
compute_persistence = t082.compute_persistence
compute_generativity = t082.compute_generativity
compute_recoverability = t082.compute_recoverability
compute_self_modeling = t082.compute_self_modeling
compute_structural_richness = t082.compute_structural_richness
compute_novelty_production = t082.compute_novelty_production
compute_recombination = t082.compute_recombination
compute_recursive_depth = t082.compute_recursive_depth
compute_open_endedness = t082.compute_open_endedness

ASS_IDS = ["OC2", "OC1", "CD1", "IC1", "IS1", "IS2", "CD2", "EC1", "SR1"]
MECH_IDS = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08"]


# ============================================================
# ALTERNATIVE PERSISTENCE SCORERS
# ============================================================

def score_si(metrics, system):
    """State Inertia — momentum in state transitions.
    Measures how often the system stays in or returns to
    recently-visited states. Higher = more inertial."""
    h = system.history
    if len(h) < 10:
        return 0.0
    stays = sum(1 for i in range(1, len(h)) if h[i] == h[i-1])
    stay_ratio = stays / max(1, len(h) - 1)
    returns = 0
    for i in range(5, len(h)):
        if h[i] in h[i-5:i]:
            returns += 1
    return_ratio = returns / max(1, len(h) - 5)
    sc = metrics.get("self_correlation", 0)
    score = stay_ratio * 0.4 + return_ratio * 0.3 + sc * 0.3
    return min(1.0, max(0.0, score))


def score_sb(metrics, system):
    """Structural Bonds — transition matrix concentration.
    Measures how concentrated/crystallized the transition
    probabilities are. Lower row entropy = stronger bonds."""
    n = system.n_actual
    T = system.T
    if n < 2:
        return 0.0
    row_entropies = []
    for i in range(n):
        p = T[i]
        p = p[p > 0]
        if len(p) > 0:
            ent = -sum(p * np.log2(p)) / max(1, math.log2(n))
            row_entropies.append(ent)
    if not row_entropies:
        return 0.0
    mean_entropy = np.mean(row_entropies)
    score = 1.0 - mean_entropy
    return min(1.0, max(0.0, score))


def score_ta(metrics, system):
    """Temporal Averaging — smoothing effect on state sequence.
    If rolling-window entropy is lower than global entropy,
    temporal averaging creates structure."""
    h = system.history
    if len(h) < 20:
        return 0.0
    global_ent = metrics.get("entropy", 0)
    if global_ent <= 0:
        return 0.0
    window_size = 5
    window_entropies = []
    for i in range(window_size, len(h)):
        window = h[i-window_size:i]
        counts = Counter(window)
        ent = 0
        for c in counts.values():
            p = c / window_size
            if p > 0:
                ent -= p * math.log2(p)
        max_ent = math.log2(min(window_size, len(set(h))))
        norm_ent = ent / max_ent if max_ent > 0 else 0
        window_entropies.append(norm_ent)
    mean_window_ent = np.mean(window_entropies)
    ratio = mean_window_ent / global_ent
    score = 1.0 - min(1.0, max(0.0, (ratio - 0.3) / 0.7))
    return min(1.0, max(0.0, score))


def score_cq(metrics, system):
    """Conservation Quantity — stability of abstract potential.
    Assigns each state a 'potential' based on transition entropy.
    Lower variance across visited states = better conservation."""
    h = system.history
    if len(h) < 10:
        return 0.0
    n = system.n_actual
    T = system.T
    potentials = []
    for i in range(n):
        p = T[i]
        p = p[p > 0]
        if len(p) > 0:
            ent = -sum(p * np.log2(p)) / max(1, math.log2(n))
            potentials.append(ent)
        else:
            potentials.append(0)
    state_potentials = {s: potentials[min(s, len(potentials)-1)] for s in set(h)}
    visited_pots = [state_potentials[s] for s in h]
    pot_std = np.std(visited_pots)
    score = 1.0 - min(1.0, pot_std * 3)
    return max(0.0, score)


def score_fm(metrics, system):
    """Fixed-Point Memory — convergence to attractor states.
    Measures proportion of time spent in top-K most visited
    states and cycle tightness."""
    h = system.history
    if len(h) < 20:
        return 0.0
    counts = Counter(h)
    total = len(h)
    top_k = max(1, min(3, len(counts)))
    top_states = counts.most_common(top_k)
    top_proportion = sum(c for _, c in top_states) / total
    cycle = metrics.get("cycle_length", 0)
    cycle_score = 0.0
    if cycle == 1:
        cycle_score = 1.0
    elif cycle <= 3:
        cycle_score = 0.7
    elif cycle <= 6:
        cycle_score = 0.4
    elif cycle <= 10:
        cycle_score = 0.2
    score = top_proportion * 0.6 + cycle_score * 0.4
    return min(1.0, max(0.0, score))


# ============================================================
# ASSAY (extends T082's assay_system with alternative scores)
# ============================================================

def assay_system_extended(params):
    r = t082.assay_system(params)
    r["si"] = score_si(r["metrics"], r.get("_system"))
    r["sb"] = score_sb(r["metrics"], r.get("_system"))
    r["ta"] = score_ta(r["metrics"], r.get("_system"))
    r["cq"] = score_cq(r["metrics"], r.get("_system"))
    r["fm"] = score_fm(r["metrics"], r.get("_system"))
    r["p_avg"] = np.mean([r["si"], r["sb"], r["ta"], r["cq"], r["fm"]])
    return r


# Need to patch assay_system to return the system object
_original_assay = t082.assay_system.__code__
# We can't easily do this, so let's recompute by creating systems ourselves

def assay_system(params):
    system = GeneratedSystem(params)
    metrics = system.run(200)

    mc2 = score_mc2(metrics)
    mc3 = score_mc3(metrics)
    mc4 = score_mc4(metrics)
    mc5 = score_mc5(metrics)
    mc1 = score_mc1(metrics)
    sp = score_sp(metrics)

    si = score_si(metrics, system)
    sb = score_sb(metrics, system)
    ta = score_ta(metrics, system)
    cq = score_cq(metrics, system)
    fm = score_fm(metrics, system)
    p_avg = np.mean([si, sb, ta, cq, fm])

    em = {
        "OC2": measure_oc2(metrics, system),
        "OC1": measure_oc1(metrics, system),
        "CD1": measure_cd1(metrics, system),
        "IC1": measure_ic1(metrics, system),
        "IS1": measure_is1(metrics, system),
        "IS2": measure_is2(metrics, system),
        "CD2": measure_cd2(metrics, system),
        "EC1": measure_ec1(metrics, system),
        "SR1": measure_sr1(metrics, system),
    }
    mechs = detect_mechanisms(metrics, system)
    viability = {
        "C": compute_coherence(metrics, system, em),
        "P": compute_persistence(metrics, system, em),
        "G": compute_generativity(metrics, system, em),
        "R": compute_recoverability(metrics, system, em),
        "S": compute_self_modeling(metrics, system, em),
    }
    fertility = {
        "SR": compute_structural_richness(metrics, system, em),
        "NP": compute_novelty_production(metrics, system, em),
        "RC": compute_recombination(metrics, system, em),
        "RD": compute_recursive_depth(metrics, system, em),
        "OE": compute_open_endedness(metrics, system, em),
    }
    viability_threshold = (
        viability["C"] >= 0.75 and
        viability["P"] >= 0.65 and
        viability["G"] >= 0.40
    )
    fertile_signature = (
        viability_threshold and
        fertility["SR"] >= 0.5 and
        fertility["NP"] >= 0.5 and
        fertility["RC"] >= 0.5
    )
    stability = (viability["C"] + viability["P"] + viability["R"]) / 3
    fert_index = (fertility["SR"] + fertility["NP"] + fertility["RC"] +
                  fertility["RD"] + fertility["OE"]) / 5

    return {
        "params": params,
        "metrics": metrics,
        "mc2": mc2, "mc3": mc3, "mc4": mc4,
        "mc5": mc5, "mc1": mc1, "sp": sp,
        "si": si, "sb": sb, "ta": ta, "cq": cq, "fm": fm,
        "p_avg": p_avg,
        "em": em, "mechs": mechs,
        "viability": viability, "fertility": fertility,
        "viable": viability_threshold,
        "fertile": fertile_signature,
        "stability": stability,
        "fertility_index": fert_index,
    }


# ============================================================
# MARGINAL ASSAY (isolates persistence effect)
# ============================================================

def marginal_assay(results, persistence_key, p_label):
    """Compare MC2+MC3+MC4+P vs MC2+MC3+MC4+not-P.
    This isolates the marginal effect of adding P to the base."""
    def base_cond(r):
        return r["mc2"] >= 0.5 and r["mc3"] >= 0.5 and r["mc4"] >= 0.5

    base_systems = [r for r in results if base_cond(r)]
    all_sat = [r for r in base_systems if r[persistence_key] >= 0.5]
    none_sat = [r for r in base_systems if r[persistence_key] < 0.5]

    ass_rows = []
    emergent = []
    for aid in ASS_IDS:
        all_m = np.mean([r["em"][aid] for r in all_sat]) if all_sat else 0
        none_m = np.mean([r["em"][aid] for r in none_sat]) if none_sat else 0
        delta = all_m - none_m
        emerged = delta >= 0.2
        if emerged:
            emergent.append(aid)
        # Bootstrap CI
        if len(all_sat) >= 5 and len(none_sat) >= 5:
            np.random.seed(42 + hash(persistence_key + aid) % 10000)
            boot_deltas = []
            for _ in range(500):
                a_boot = np.random.choice([r["em"][aid] for r in all_sat],
                                          size=len(all_sat), replace=True)
                n_boot = np.random.choice([r["em"][aid] for r in none_sat],
                                          size=len(none_sat), replace=True)
                boot_deltas.append(np.mean(a_boot) - np.mean(n_boot))
            ci_low, ci_high = np.percentile(boot_deltas, [2.5, 97.5])
            reliable = ci_low > 0
        else:
            ci_low, ci_high, reliable = None, None, None

        ass_rows.append({
            "assumption": aid,
            "all_mean": round(all_m, 3),
            "none_mean": round(none_m, 3),
            "delta": round(delta, 3),
            "emerged": emerged,
            "ci_low": round(ci_low, 3) if ci_low is not None else None,
            "ci_high": round(ci_high, 3) if ci_high is not None else None,
            "reliable": reliable,
        })

    return {
        "label": p_label,
        "key": persistence_key,
        "n_all": len(all_sat),
        "n_none": len(none_sat),
        "n_emergent": len(emergent),
        "emergent_list": emergent,
        "rows": ass_rows,
    }


# ============================================================
# EXECUTION
# ============================================================

print("=" * 72)
print("T086: MINIMAL NECESSITY AUDIT")
print("=" * 72)
print("Question: Is persistence a principle, implementation, or artifact?")
print()

# Generate ensemble (same as T082/T086 v1)
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
print(f"  {len(all_params)} parameter configurations")

results = []
for i, params in enumerate(all_params):
    r = assay_system(params)
    results.append(r)
    if (i + 1) % 50 == 0:
        print(f"  Ran {i+1}/{len(all_params)} systems...")
print(f"  Complete: {len(results)} systems analyzed")


# ============================================================
# SCORE DISTRIBUTIONS
# ============================================================

print(f"\n{'='*72}")
print("SCORE DISTRIBUTIONS")
print("=" * 72)
score_names = ["mc2", "mc3", "mc4", "sp", "si", "sb", "ta", "cq", "fm"]
scores = np.array([[r[n] for n in score_names] for r in results])
print(f"  {'Name':>8} {'Mean':>8} {'Std':>8} {'p50':>8} {'%>=0.5':>8}")
print(f"  {'-'*40}")
for i, n in enumerate(score_names):
    print(f"  {n:>8} {np.mean(scores[:,i]):>8.3f} {np.std(scores[:,i]):>8.3f} "
          f"{np.median(scores[:,i]):>8.3f} {np.mean(scores[:,i]>=0.5)*100:>7.1f}%")


# ============================================================
# BASELINE: MC2+MC3+MC4 alone
# ============================================================

print(f"\n{'='*72}")
print("BASELINE: MC2+MC3+MC4 alone (using T082 run_assay)")
print("=" * 72)

baseline_constraints = [
    ("MC2", lambda r: r["mc2"] >= 0.5),
    ("MC3", lambda r: r["mc3"] >= 0.5),
    ("MC4", lambda r: r["mc4"] >= 0.5),
]
baseline = t082.run_assay(results, baseline_constraints, "Baseline (MC2+MC3+MC4)")
print(f"  All-sat: {baseline['n_all']}, None-sat: {baseline['n_none']}")
print(f"  Assumptions emerged: {baseline['assumption_emergence']['n_emergent']}/9")
print(f"  Emergent: {baseline['assumption_emergence']['emergent_list']}")
print(f"  Mechanisms emerged: {baseline['mechanism_emergence']['n_emergent']}/8")
print(f"  Viability basin: {baseline['viability_basin']['basin_present']}")
print(f"  Fertile corridor: {baseline['fertile_corridor']['corridor_detected']}")
print(f"  PC1%: {baseline['meta_space']['pc1_pct']}")


# ============================================================
# MARGINAL PERSISTENCE EFFECT
# ============================================================

print(f"\n{'='*72}")
print("MARGINAL PERSISTENCE EFFECT (holding MC2+MC3+MC4 constant)")
print("all: MC2+MC3+MC4+P >= 0.5,  none: MC2+MC3+MC4 >= 0.5, P < 0.5")
print("=" * 72)

PERSISTENCE_TYPES = [
    ("sp", "SP (Structural Persistence)"),
    ("si", "SI (State Inertia)"),
    ("sb", "SB (Structural Bonds)"),
    ("ta", "TA (Temporal Averaging)"),
    ("cq", "CQ (Conservation Quantity)"),
    ("fm", "FM (Fixed-Point Memory)"),
]

marginal_results = []
for pkey, plabel in PERSISTENCE_TYPES:
    print(f"\n  --- {plabel} ---")
    ma = marginal_assay(results, pkey, plabel)
    marginal_results.append(ma)
    print(f"  All-sat: {ma['n_all']}, None-sat: {ma['n_none']}")
    print(f"  Assumptions emerged: {ma['n_emergent']}/9 — {ma['emergent_list']}")
    print(f"  {'Assumption':<10} {'Delta':<8} {'CI':<16} {'Reliable?':<10}")
    for row in ma["rows"]:
        ci_str = f"[{row['ci_low']:<+6.3f}, {row['ci_high']:<+6.3f}]" if row['ci_low'] is not None else "N/A (small n)"
        rel_str = str(row['reliable']) if row['reliable'] is not None else "N/A"
        marker = " ***" if row['delta'] >= 0.3 else " **" if row['delta'] >= 0.2 else " *" if row['delta'] >= 0.1 else ""
        print(f"  {row['assumption']:<10} {row['delta']:<+8.3f} {ci_str:<16} {rel_str:<10}{marker}")


# ============================================================
# EMERGENCE HEATMAP
# ============================================================

print(f"\n{'='*72}")
print("EMERGENCE DELTA HEATMAP: Assumptions × Persistence Type")
print("=" * 72)

print(f"\n  {'Assumption':<10}", end="")
for pkey, _ in PERSISTENCE_TYPES:
    print(f"{pkey:>8}", end="")
print(f"  {'Count':<6}")

emergence_counts = {aid: 0 for aid in ASS_IDS}
for aid in ASS_IDS:
    print(f"  {aid:<10}", end="")
    for ma in marginal_results:
        row = [r for r in ma["rows"] if r["assumption"] == aid][0]
        delta = row["delta"]
        marker = ""
        if row.get("reliable") == True:
            marker = "R"
        elif row.get("reliable") == False:
            marker = "r"
        else:
            marker = "?"
        print(f"{delta:>+8.3f}", end="")
        if row["emerged"]:
            emergence_counts[aid] += 1
    print(f"  {emergence_counts[aid]:>2}/6")

# Classification
print(f"\n  {'Assumption':<10} {'Count':<6} {'Pattern':<20}")
print(f"  {'-'*36}")
for aid in ASS_IDS:
    c = emergence_counts[aid]
    if c >= 5:
        pat = "UNIVERSAL"
    elif c >= 3:
        pat = "CONTINGENT"
    else:
        pat = "RARE"
    print(f"  {aid:<10} {c:>2}/6   {pat:<20}")


# ============================================================
# PERSISTENCE SCORE CORRELATIONS
# ============================================================

print(f"\n{'='*72}")
print("PERSISTENCE SCORE CORRELATIONS (all persistence types)")
print("=" * 72)

pkeys = [p[0] for p in PERSISTENCE_TYPES]
pvals = np.array([[r[pk] for pk in pkeys] for r in results])
corr = np.corrcoef(pvals.T)

print(f"  {'':>12}", end="")
for pk in pkeys:
    print(f"{pk:>8}", end="")
print()
for i, pk1 in enumerate(pkeys):
    print(f"  {pk1:>12}", end="")
    for j in range(len(pkeys)):
        print(f"{corr[i,j]:>+8.3f}", end="")
    print()


# ============================================================
# DIVERGENT CASE ANALYSIS
# ============================================================

print(f"\n{'='*72}")
print("DIVERGENT CASES: Systems where persistence types disagree")
print("=" * 72)

print(f"\n  Persistence type pairs with agreement (both >= 0.5 or both < 0.5):")
for i in range(len(pkeys)):
    for j in range(i+1, len(pkeys)):
        pk1, pk2 = pkeys[i], pkeys[j]
        both_high = sum(1 for r in results if r[pk1] >= 0.5 and r[pk2] >= 0.5)
        both_low = sum(1 for r in results if r[pk1] < 0.5 and r[pk2] < 0.5)
        agreement = (both_high + both_low) / len(results) * 100
        print(f"  {pk1}-{pk2}: both_high={both_high}, both_low={both_low}, agreement={agreement:.1f}%")


# ============================================================
# VERDICT
# ============================================================

print(f"\n{'='*72}")
print("VERDICT")
print("=" * 72)

# Count how many alternatives produce >= 5/9 emergence
alt_with_high_emergence = sum(1 for ma in marginal_results if ma["n_emergent"] >= 5)
n_universal = sum(1 for c in emergence_counts.values() if c >= 5)
n_contingent = sum(1 for c in emergence_counts.values() if 3 <= c < 5)
n_rare = sum(1 for c in emergence_counts.values() if c < 3)

print(f"\n  Alternatives with >=5/9 emergence: {alt_with_high_emergence}/6")
print(f"  Universally emergent (>=5/6):        {n_universal}/9")
print(f"  Contingently emergent (3-4/6):       {n_contingent}/9")
print(f"  Rarely emergent (<3/6):              {n_rare}/9")

# Also check: how many alternatives have any POSITIVE and RELIABLE emergence?
reliable_positives = 0
for ma in marginal_results:
    has_reliable_positive = any(
        row["emerged"] and row.get("reliable") == True
        for row in ma["rows"]
    )
    if has_reliable_positive:
        reliable_positives += 1

print(f"\n  Alternatives with any reliable positive emergence: {reliable_positives}/6")

# Count reliably positive assumptions across all alternatives
reliable_assumptions = {aid: 0 for aid in ASS_IDS}
for ma in marginal_results:
    if ma["n_all"] < 5:
        continue  # skip small-n types
    for row in ma["rows"]:
        if row.get("reliable") == True and row["emerged"]:
            reliable_assumptions[row["assumption"]] += 1

print(f"  Reliably emergent assumptions (in types with n>=5):")
for aid in ASS_IDS:
    if reliable_assumptions[aid] > 0:
        print(f"    {aid}: {reliable_assumptions[aid]}/4 types (SB, TA, CQ, FM)")

# Also check for reliably NEGATIVE effects
print(f"\n  Reliably NEGATIVE persistence effects:")
for ma in marginal_results:
    if ma["n_all"] < 5:
        continue
    for row in ma["rows"]:
        if row.get("reliable") == False and row["delta"] < -0.1:
            print(f"    {ma['key']} → {row['assumption']}: delta={row['delta']:.3f} (CI=[{row['ci_low']:.3f}, {row['ci_high']:.3f}])")

# Full verdict
# PRINCIPLE: >=5 alternatives with >=5 emergence, AND >=5 universal assumptions
# IMPLEMENTATION: 2-4 alternatives with >=5 emergence
# ARTIFACT: <=1 alternative with >=5 emergence, <=2 universal assumptions

if alt_with_high_emergence >= 5 and n_universal >= 5:
    verdict = "PRINCIPLE — persistence is functionally overdetermined"
elif alt_with_high_emergence <= 1 and n_universal <= 2:
    # Check the mechanism — is it the empty none-group artifact?
    if all(ma["n_none"] == 0 for ma in marginal_results):
        verdict = "ARTIFACT (measurement design) — empty none-group inflates deltas"
    elif all(ma["n_emergent"] == 0 for ma in marginal_results):
        verdict = "ARTIFACT (zero marginal effect) — persistence adds nothing to MC2+MC3+MC4"
    else:
        verdict = "ARTIFACT — persistence adds minimal marginal value"
else:
    verdict = "IMPLEMENTATION — specific persistence mechanism matters"

print(f"\n  >>> VERDICT: {verdict}")


# ============================================================
# WRITE OUTPUTS
# ============================================================

# Marginal effect table
with open(OUT / "t086_marginal_effects.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["persistence_type", "assumption", "all_mean", "none_mean",
                 "delta", "emerged", "ci_low", "ci_high", "reliable"])
    for ma in marginal_results:
        for row in ma["rows"]:
            w.writerow([ma["key"], row["assumption"], row["all_mean"],
                        row["none_mean"], row["delta"], row["emerged"],
                        row["ci_low"] if row["ci_low"] is not None else "",
                        row["ci_high"] if row["ci_high"] is not None else "",
                        row["reliable"]])

# Summary table
with open(OUT / "t086_summary.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["persistence_type", "n_all", "n_none", "n_emergent", "emergent_list"])
    for ma in marginal_results:
        w.writerow([ma["key"], ma["n_all"], ma["n_none"],
                    ma["n_emergent"], ",".join(ma["emergent_list"])])

# Persistence correlation
with open(OUT / "t086_persistence_correlations.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow([""] + pkeys)
    for i, pk1 in enumerate(pkeys):
        row = [pk1]
        for j in range(len(pkeys)):
            row.append(round(corr[i, j], 4))
        w.writerow(row)

# Summary JSON
summary = {
    "audit": "T086 — Minimal Necessity Audit",
    "question": "Is persistence a principle, implementation, or artifact?",
    "verdict": verdict,
    "n_systems": int(len(results)),
    "baseline_emergence": baseline["assumption_emergence"]["n_emergent"],
    "baseline_emergent_list": baseline["assumption_emergence"]["emergent_list"],
    "universally_emergent": [aid for aid in ASS_IDS if emergence_counts[aid] >= 5],
    "contingently_emergent": [aid for aid in ASS_IDS if 3 <= emergence_counts[aid] < 5],
    "rarely_emergent": [aid for aid in ASS_IDS if emergence_counts[aid] < 3],
    "alt_with_high_emergence": alt_with_high_emergence,
    "reliable_positives": reliable_positives,
    "marginal_results": [],
}
for ma in marginal_results:
    summary["marginal_results"].append({
        "key": ma["key"],
        "label": ma["label"],
        "n_all": ma["n_all"],
        "n_none": ma["n_none"],
        "n_emergent": ma["n_emergent"],
        "emergent_list": ma["emergent_list"],
    })

with open(OUT / "t086_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nWrote t086_marginal_effects.csv")
print(f"Wrote t086_summary.csv")
print(f"Wrote t086_persistence_correlations.csv")
print(f"Wrote t086_summary.json")
print(f"\nT086 complete.")
