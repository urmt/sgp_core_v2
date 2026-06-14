#!/usr/bin/env python3
"""
T085: Mapping–Generation Divergence Audit
===========================================
Resolve T080 ↔ T081/T082 contradiction by identifying exactly where
conceptual mapping and operational generation disagree.

Method:
  1. Reconstruct T080 as explicit assumption-by-MC prediction matrix
  2. Reconstruct T081/T082 as empirical emergence matrix
  3. Compute divergence (agreement, FP, FN, per-assumption error)
  4. Test H1: Conceptual over-mapping
  5. Test H2: Missing interaction terms
  6. Test H3: Threshold artifacts
  7. Forced verdict

Author: T085 audit
"""

import csv, json, sys
from pathlib import Path
from collections import defaultdict

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# DATA STRUCTURES
# ============================================================

ASSUMPTIONS = ['OC2','OC1','CD1','IC1','IS1','IS2','CD2','EC1','SR1']
ASS_NAMES = {
    'OC2':'Distinguishability', 'OC1':'Stable structure', 'CD1':'Causal relations',
    'IC1':'Extractable info', 'IS1':'Phase structure', 'IS2':'Determinate outputs',
    'CD2':'Self-affecting procedures', 'EC1':'Self-knowledge',
    'SR1':'Self-examination of outputs'
}
MCS = ['MC1','MC2','MC3','MC4','MC5']
MC_NAMES = {
    'MC2':'Productive Transformation', 'MC3':'Constraint Balance',
    'MC4':'Recursive Accessibility', 'MC5':'Recoverable Perturbation',
    'MC1':'Information Preservation'
}

# Threshold for "emerged"
EMERGENCE_THRESHOLD = 0.5

# ============================================================
# PHASE 1: T080 CONCEPTUAL PREDICTION MATRIX
# ============================================================
# From T080: ASSUMPTION_CONSTRAINT_SCORES
# +1 = constraint predicts/entails this assumption
#  0 = neutral
# -1 = constraint contradicts/eliminates this assumption

# Mapping: MC → which assumptions it predicts (+1)
T080_PREDICTIONS = {
    'MC2': {'IC1':+1, 'IS1':+1, 'IS2':+1, 'CD2':+1, 'SR1':+1},
    'MC3': {'OC2':+1, 'OC1':+1, 'IS1':+1, 'CD2':+1, 'SR1':+1},
    'MC4': {'CD2':+1, 'EC1':+1, 'SR1':+1},
    'MC5': {'SR1':+1},
    'MC1': {'OC1':+1, 'CD1':+1, 'IC1':+1, 'IS2':+1},
}

# Also record contradictions (-1)
T080_CONTRADICTIONS = {
    'MC2': {}, 'MC3': {}, 'MC4': {}, 'MC5': {}, 'MC1': {}
}

# Derivation set (from T080 DERIVATION_FROM)
# Assumption → set of MCs it can be "derived from"
T080_DERIVATION = {
    'OC2': {'MC3'},          'OC1': {'MC1','MC3'}, 'CD1': {'MC3'},
    'IC1': {'MC1','MC2'},    'IS1': {'MC3'},        'IS2': {'MC1','MC2'},
    'CD2': {'MC2','MC4'},    'EC1': {'MC4'},        'SR1': {'MC2','MC4','MC5'},
}

# Which MC combinations does T080 claim generate which assumptions?
def t080_predicted(mc_set, ass):
    """Does T080 predict this assumption from this MC set?"""
    # An assumption is "predicted" if any MC in the set has a +1 for it
    for mc in mc_set:
        if ass in T080_PREDICTIONS.get(mc, {}):
            return True
    return False

def t080_predicted_strength(mc_set, ass):
    """Sum of prediction strengths for this assumption from this MC set."""
    total = 0
    for mc in mc_set:
        total += T080_PREDICTIONS.get(mc, {}).get(ass, 0)
    return total

# ============================================================
# PHASE 2: T081/T082 EMPIRICAL EMERGENCE MATRIX
# ============================================================

# --- T081: MC2+MC3+MC4 only (baseline generation) ---
T081_EMERGENCE = {}
with open(OUT / "t081_phase1_assumption_emergence.csv") as f:
    for row in csv.DictReader(f):
        T081_EMERGENCE[row['assumption']] = {
            'delta': float(row['delta']),
            'all_mean': float(row['all_mcs_mean']),
            'none_mean': float(row['none_mcs_mean']),
            'emerged': row['emergent'] == 'True',
            'above_threshold': float(row['delta']) >= EMERGENCE_THRESHOLD,
        }

# --- T081-T082: also check if positive delta even if below threshold ---
# Positive delta means the constraint set increases (not decreases) assumption scores

# --- T082 Baseline (MC2+MC3+MC4, 0.5 threshold) ---
T082_BASELINE = {}
with open(OUT / "t082_assumptions_Baseline_MC2+MC3+MC4,_threshol.csv") as f:
    for row in csv.DictReader(f):
        T082_BASELINE[row['assumption']] = {
            'delta': float(row['delta']),
            'all_mean': float(row['all_mean']),
            'none_mean': float(row['none_mean']),
            'emerged': row['emerged'] == 'True',
        }

# --- T082 SP (Structural Persistence) added ---
T082_SP = {}
with open(OUT / "t082_assumptions_SP_Structural_Persistence_adde.csv") as f:
    for row in csv.DictReader(f):
        T082_SP[row['assumption']] = {
            'delta': float(row['delta']),
            'all_mean': float(row['all_mean']),
            'none_mean': float(row['none_mean']),
            'emerged': row['emerged'] == 'True',
        }

# --- T082 MC5 added ---
T082_MC5 = {}
with open(OUT / "t082_assumptions_MC5_Recoverable_Perturbation_a.csv") as f:
    for row in csv.DictReader(f):
        T082_MC5[row['assumption']] = {
            'delta': float(row['delta']),
            'all_mean': float(row['all_mean']),
            'none_mean': float(row['none_mean']),
            'emerged': row['emerged'] == 'True',
        }

# --- T082 MC1 added ---
T082_MC1 = {}
with open(OUT / "t082_assumptions_MC1_Information_Preservation_a.csv") as f:
    for row in csv.DictReader(f):
        T082_MC1[row['assumption']] = {
            'delta': float(row['delta']),
            'all_mean': float(row['all_mean']),
            'none_mean': float(row['none_mean']),
            'emerged': row['emerged'] == 'True',
        }

# ============================================================
# PHASE 3: DIVERGENCE COMPUTATION
# ============================================================

print("=" * 72)
print("T085: Mapping–Generation Divergence Audit")
print("=" * 72)

# ---- 3a. Build unified comparison table: T080 vs T081 vs T082 ----
# MC sets to compare
COMPARISONS = [
    ("MC2+MC3+MC4 (T080 prediction vs T081)", {'MC2','MC3','MC4'}, 'T081'),
    ("MC2+MC3+MC4 (T080 prediction vs T082 baseline)", {'MC2','MC3','MC4'}, 'T082_baseline'),
    ("MC2+MC3+MC4+SP (T080+SP vs T082 SP)", {'MC2','MC3','MC4','MC1'}, 'T082_SP'),  # SP not in T080, approximate with MC1
    ("MC2+MC3+MC4+MC5 (T080+MC5 vs T082 MC5)", {'MC2','MC3','MC4','MC5'}, 'T082_MC5'),
    ("MC2+MC3+MC4+MC1 (T080+MC1 vs T082 MC1)", {'MC2','MC3','MC4','MC1'}, 'T082_MC1'),
]

for label, mc_set, source in COMPARISONS:
    print(f"\n{'=' * 72}")
    print(f"COMPARISON: {label}")
    print(f"{'=' * 72}")
    
    header = f"{'Assumption':<12} {'Name':<28} {'Predicted':<12} {'Delta':<8} {'Emerged':<10} {'Agreement':<12}"
    if source == 'T081':
        header += f"{'Pos. Delta?':<12}"
    print(f"\n  {header}")
    print(f"  {'-' * (len(header)+10)}")
    
    agree = 0
    fp = 0  # predicted but not emerged
    fn = 0  # emerged but not predicted
    total = 0
    
    for ass in ASSUMPTIONS:
        pred = t080_predicted(mc_set, ass)
        
        if source == 'T081':
            d = T081_EMERGENCE[ass]
            delta = d['delta']
            emerged = d['above_threshold']
            pos_delta = d['delta'] > 0
        elif source == 'T082_baseline':
            d = T082_BASELINE[ass]
            delta = d['delta']
            emerged = d['emerged']
            pos_delta = d['delta'] > 0
        elif source == 'T082_SP':
            d = T082_SP[ass]
            delta = d['delta']
            emerged = d['emerged']
            pos_delta = d['delta'] > 0
        elif source == 'T082_MC5':
            d = T082_MC5[ass]
            delta = d['delta']
            emerged = d['emerged']
            pos_delta = d['delta'] > 0
        elif source == 'T082_MC1':
            d = T082_MC1[ass]
            delta = d['delta']
            emerged = d['emerged']
            pos_delta = d['delta'] > 0
        
        if pred and emerged:
            agreement = "MATCH ✓"
            agree += 1
        elif pred and not emerged:
            agreement = "FP ✗"
            fp += 1
        elif not pred and emerged:
            agreement = "FN ✗"
            fn += 1
        else:
            agreement = "MATCH ✓"
            agree += 1
        
        total += 1
        
        row = f"  {ass:<12} {ASS_NAMES[ass]:<28} {'YES' if pred else 'NO':<12} {delta:<+8.3f} {'YES' if emerged else 'NO':<10} {agreement:<12}"
        if source == 'T081':
            row += f"{'YES' if pos_delta else 'NO':<12}"
        print(row)
    
    # Summary
    accuracy = agree / total * 100
    print(f"\n  {'─' * (len(header)+10)}")
    print(f"  Accuracy: {agree}/{total} ({accuracy:.0f}%)")
    print(f"  False positives (predicted but not emerged): {fp}")
    print(f"  False negatives (emerged but not predicted): {fn}")

# ---- 3b. Per-assumption divergence across all sources ----
print(f"\n{'=' * 72}")
print("PER-ASSUMPTION DIVERGENCE PROFILE")
print("=" * 72)

header = f"{'Assumption':<8} {'T080_pred':<12} {'T081_δ':<9} {'T081_em':<9} {'T082_δ':<9} {'T082_em':<9} {'SP_δ':<8} {'SP_em':<9} {'MC5_δ':<9} {'MC5_em':<9} {'MC1_δ':<9} {'MC1_em':<9}"
print(f"\n  {header}")
print(f"  {'-' * len(header)}")

for ass in ASSUMPTIONS:
    pred_234 = t080_predicted({'MC2','MC3','MC4'}, ass)
    pred_2345 = t080_predicted({'MC2','MC3','MC4','MC5'}, ass)
    pred_2341 = t080_predicted({'MC2','MC3','MC4','MC1'}, ass)
    
    t081 = T081_EMERGENCE[ass]
    t082 = T082_BASELINE[ass]
    sp = T082_SP[ass]
    mc5 = T082_MC5[ass]
    mc1 = T082_MC1[ass]
    
    # Find which MC set is needed for T082 to match prediction
    # "Minimally sufficient constraint"
    if not pred_234:
        if pred_2341 and mc1['emerged']:
            needed = "+MC1"
        elif pred_2345 and mc5['emerged']:
            needed = "+MC5"
        else:
            needed = "?none?"
    else:
        if t082['emerged']:
            needed = "MC234"
        elif t081['above_threshold']:
            needed = "MC234(T081)"
        elif t081['delta'] > 0:
            needed = "MC234(weak)"
        else:
            needed = "never"
    
    row = f"  {ass:<8} {'YES' if pred_234 else 'NO':<12} {t081['delta']:<+9.3f} {'YES' if t081['above_threshold'] else 'NO':<9} {t082['delta']:<+9.3f} {'YES' if t082['emerged'] else 'NO':<9} {sp['delta']:<+9.3f} {'YES' if sp['emerged'] else 'NO':<9} {mc5['delta']:<+9.3f} {'YES' if mc5['emerged'] else 'NO':<9} {mc1['delta']:<+9.3f} {'YES' if mc1['emerged'] else 'NO':<9}"
    print(row)

# ============================================================
# PHASE 4: HYPOTHESIS TESTING
# ============================================================
print(f"\n{'=' * 72}")
print("PHASE 4: HYPOTHESIS TESTING")
print("=" * 72)

# ---- H1: Conceptual Over-Mapping ----
print(f"\n\nH1: CONCEPTUAL OVER-MAPPING")
print(f"{'─' * 40}")
print("""
Prediction: T080's derivation method is too generous. It counts any positive
association as "derivation", including weak or indirect ones. A stricter
scoring would reduce predicted emergence.

Tests:
  a) Compare T080 prediction strength vs empirical emergence
  b) Check if false positives have weaker predicted strength
  c) Check if T080's "derivation" includes assumptions with negative empirical deltas
""")

# Test H1a: Prediction strength vs emergence
print(f"\n  H1a: Prediction strength vs empirical emergence")
pred_strengths = []
for ass in ASSUMPTIONS:
    strength = t080_predicted_strength({'MC2','MC3','MC4'}, ass)
    delta = T081_EMERGENCE[ass]['delta']
    pred_strengths.append((ass, strength, delta))
    print(f"    {ass}: prediction_strength={strength}, T081_delta={delta:+.3f}")

# Check: do false positives have lower prediction strength?
fp_assumptions = [ass for ass in ASSUMPTIONS if 
    t080_predicted({'MC2','MC3','MC4'}, ass) and not T082_BASELINE[ass]['emerged']]
    
fp_assumptions_t081 = [ass for ass in ASSUMPTIONS if 
    t080_predicted({'MC2','MC3','MC4'}, ass) and not T081_EMERGENCE[ass]['above_threshold']]

print(f"\n  H1b: False positives under T081:")
for ass in fp_assumptions_t081:
    strength = t080_predicted_strength({'MC2','MC3','MC4'}, ass)
    delta = T081_EMERGENCE[ass]['delta']
    print(f"    {ass} ({ASS_NAMES[ass]}): prediction_strength={strength}, delta={delta:+.3f}")
    if delta < 0:
        print(f"      → NEGATIVE delta: T080 predicted emergence, but MC2+MC3+MC4 "
              f"actively REDUCE this assumption in the generative simulation")

print(f"\n  H1c: Assumptions with NEGATIVE empirical delta despite positive prediction:")
for ass in ASSUMPTIONS:
    if t080_predicted({'MC2','MC3','MC4'}, ass) and T081_EMERGENCE[ass]['delta'] < 0:
        print(f"    {ass}: predicted YES, delta={T081_EMERGENCE[ass]['delta']:.3f}")

# H1 score
neg_fp = sum(1 for ass in ASSUMPTIONS if 
    t080_predicted({'MC2','MC3','MC4'}, ass) and T081_EMERGENCE[ass]['delta'] < 0)
h1_score = neg_fp
print(f"\n  H1 score: {neg_fp} assumption(s) with positive prediction but negative empirical delta")
print(f"  → {'STRONG evidence for over-mapping' if h1_score >= 3 else 'MODERATE evidence' if h1_score >= 1 else 'WEAK evidence'}")

# ---- H2: Missing Interaction Terms ----
print(f"\n\nH2: MISSING INTERACTION TERMS")
print(f"{'─' * 40}")
print("""
Prediction: T080's mapping treats each MC-assumption relationship independently.
In the generative simulation, assumptions may depend on interactions between MCs
that T080's additive model misses.

Tests:
  a) Does SP fix specific assumptions that no single MC predicts?
  b) Do systematic FP patterns suggest a missing constraint?
  c) Ablation analysis: which MC removal causes collapse for which assumptions?
""")

# Test H2a: Which assumptions does SP/MC5/MC1 fix specifically?
print(f"\n  H2a: What SP adds to MC2+MC3+MC4")
print(f"  {'Assumption':<12} {'MC234_pred':<12} {'MC234_δ':<10} {'MC234_em':<10} {'+SP_δ':<10} {'+SP_em':<10} {'Fixed?':<10}")
print(f"  {'-'*64}")
fp_234 = []
for ass in ASSUMPTIONS:
    pred = t080_predicted({'MC2','MC3','MC4'}, ass)
    t082_d = T082_BASELINE[ass]
    sp_d = T082_SP[ass]
    fixed = not t082_d['emerged'] and sp_d['emerged']
    if not t082_d['emerged']:
        fp_234.append(ass)
    print(f"  {ass:<12} {'YES' if pred else 'NO':<12} {t082_d['delta']:<+10.3f} {'YES' if t082_d['emerged'] else 'NO':<10} {sp_d['delta']:<+10.3f} {'YES' if sp_d['emerged'] else 'NO':<10} {'YES' if fixed else '':<10}")

print(f"\n  Assumptions that MC234 does NOT generate: {', '.join(fp_234)}")
print(f"  Of these, SP fixes: {sum(1 for a in fp_234 if T082_SP[a]['emerged'])}/{len(fp_234)}")
print(f"  MC5 fixes: {sum(1 for a in fp_234 if T082_MC5[a]['emerged'])}/{len(fp_234)}")
print(f"  MC1 fixes: {sum(1 for a in fp_234 if T082_MC1[a]['emerged'])}/{len(fp_234)}")

# Test H2b: Is there a pattern in the false positives?
print(f"\n  H2b: FP pattern analysis")
# Which MC predicts them?
for ass in fp_234:
    predicted_by = [mc for mc in ['MC2','MC3','MC4'] if ass in T080_PREDICTIONS.get(mc, {})]
    needed_for_fix = []
    if T082_SP[ass]['emerged']:
        needed_for_fix.append('SP')
    if T082_MC5[ass]['emerged']:
        needed_for_fix.append('MC5') 
    if T082_MC1[ass]['emerged']:
        needed_for_fix.append('MC1')
    print(f"    {ass}: predicted by {', '.join(predicted_by)}, fixed by {', '.join(needed_for_fix)}")

# Test H2c: Ablation pattern
print(f"\n  H2c: Ablation analysis (from T082)")
print(f"  {'Removed':<12} {'Assumptions emerged':<22} {'Mechanisms':<15} {'Viability':<12}")
print(f"  {'-'*60}")

with open(OUT / "t082_ablation.csv") as f:
    for row in csv.DictReader(f):
        print(f"  {row['removed']:<12} {row['assumptions_emerged']:<22} {row['mechanisms_emerged']:<15} {'YES' if row['viability_basin'] else 'NO':<12}")

# Test H2d: Does T081 ablation show same pattern?
print(f"\n  H2d: T081 ablation (MC2+MC3+MC4 only)")
print(f"  {'Removed':<12} {'n':<6} {'Viable':<8} {'Fertile':<10}")
with open(OUT / "t081_phase6_ablation.csv") as f:
    for row in csv.DictReader(f):
        print(f"  {row['ablation']:<12} {row['n']:<6} {row['viable']:<8} {row['fertile']:<10}")

# H2 score: how many FPs are fixed by adding a persistence constraint?
h2_score = sum(1 for a in fp_234 if T082_SP[a]['emerged'] or T082_MC5[a]['emerged'] or T082_MC1[a]['emerged'])
print(f"\n  H2 score: {h2_score}/{len(fp_234)} FPs fixed by adding persistence-class constraints")
print(f"  → {'STRONG evidence for missing interaction' if h2_score == len(fp_234) else 'MODERATE evidence' if h2_score >= len(fp_234)/2 else 'WEAK evidence'}")

# ---- H3: Threshold Artifacts ----
print(f"\n\nH3: THRESHOLD ARTIFACTS")
print(f"{'─' * 40}")
print("""
Prediction: The 0.5 delta threshold for "emergence" is arbitrary. Assumptions
with positive but sub-threshold deltas may be genuinely generated but not detected.

Tests:
  a) How many FPs have positive delta (just below threshold)?
  b) How does threshold choice affect emergence count?
  c) Compare T081 (MC2+MC3+MC4) vs T082 baseline emergence lists
""")

# Test H3a: FPs with positive delta but below threshold
print(f"\n  H3a: Threshold-sensitive cases")
for ass in fp_234_t081 if 'fp_234_t081' in dir() else fp_234:
    delta = T081_EMERGENCE[ass]['delta']
    t082_d = T082_BASELINE[ass]['delta']
    status = ""
    if delta > 0 and delta < EMERGENCE_THRESHOLD:
        status = "BELOW THRESHOLD"
    elif delta >= EMERGENCE_THRESHOLD:
        status = "ABOVE THRESHOLD (emergent)"
    else:
        status = "NEGATIVE (anti-emergent)"
    print(f"    {ass}: T081 δ={delta:+.3f}, T082 δ={t082_d:+.3f} — {status}")

# Count T081 positive deltas among predicted
print(f"\n  H3b: T081 positive deltas (any threshold)")
t081_positive = sum(1 for ass in ASSUMPTIONS if 
    t080_predicted({'MC2','MC3','MC4'}, ass) and T081_EMERGENCE[ass]['delta'] > 0)
t081_emerged_05 = sum(1 for ass in ASSUMPTIONS if 
    t080_predicted({'MC2','MC3','MC4'}, ass) and T081_EMERGENCE[ass]['delta'] >= 0.5)
t081_emerged_custom = sum(1 for ass in ASSUMPTIONS if 
    t080_predicted({'MC2','MC3','MC4'}, ass) and T081_EMERGENCE[ass]['delta'] >= 0.3)
print(f"  MC2+MC3+MC4 predictions with:")
print(f"    Any positive delta:  {t081_positive}/{len(ASSUMPTIONS)}")
print(f"    Delta >= 0.3:        {t081_emerged_custom}/{len(ASSUMPTIONS)}")
print(f"    Delta >= 0.5:        {t081_emerged_05}/{len(ASSUMPTIONS)}")

# Test H3c: T082 higher-threshold condition
print(f"\n  H3c: T082 with higher thresholds (MC2/MC3/MC4 >= 0.7)")
t082_high = {}
with open(OUT / "t082_assumptions_Higher_thresholds_MC2_MC3_MC4_.csv") as f:
    for row in csv.DictReader(f):
        t082_high[row['assumption']] = {
            'delta': float(row['delta']),
            'emerged': row['emerged'] == 'True',
        }

# T082 interaction condition
t082_interact = {}
with open(OUT / "t082_assumptions_Interaction_MC2_x_MC3_x_MC4_>=.csv") as f:
    for row in csv.DictReader(f):
        t082_interact[row['assumption']] = {
            'delta': float(row['delta']),
            'emerged': row['emerged'] == 'True',
        }

print(f"\n  Threshold comparison for MC2+MC3+MC4:")
print(f"  {'Assumption':<12} {'Standard(0.5)':<16} {'High(0.7)':<14} {'Interaction':<14}")
print(f"  {'-'*56}")
for ass in ASSUMPTIONS:
    std_em = 'YES' if T082_BASELINE[ass]['emerged'] else 'NO'
    high_em = 'YES' if t082_high[ass]['emerged'] else 'NO'
    int_em = 'YES' if t082_interact[ass]['emerged'] else 'NO'
    print(f"  {ass:<12} {std_em:<16} {high_em:<14} {int_em:<14}")

# H3 score: how many mismatches are threshold artifacts?
h3_fps_threshold = sum(1 for ass in ASSUMPTIONS if 
    t080_predicted({'MC2','MC3','MC4'}, ass) and 
    not T081_EMERGENCE[ass]['above_threshold'] and 
    T081_EMERGENCE[ass]['delta'] > 0)
    
h3_fp_high_resolved = sum(1 for ass in ASSUMPTIONS if 
    t080_predicted({'MC2','MC3','MC4'}, ass) and 
    not T082_BASELINE[ass]['emerged'] and 
    t082_high[ass]['emerged'])

print(f"\n  H3 score: {h3_fps_threshold} T081 FPs have positive but sub-threshold delta")
print(f"            {h3_fp_high_resolved} T082 FPs resolved by higher threshold")
print(f"  → {'STRONG evidence for threshold artifact' if h3_fps_threshold >= 3 else 'MODERATE' if h3_fps_threshold >= 1 else 'WEAK'}")

# ============================================================
# PHASE 5: FINAL TABLE AND FORCED VERDICT
# ============================================================
print(f"\n{'=' * 72}")
print("PHASE 5: FINAL TABLE AND FORCED VERDICT")
print("=" * 72)

print(f"\n{'─' * 72}")
print("FINAL DIVERGENCE TABLE")
print(f"{'─' * 72}")
header_final = (
    f"{'Assump':<8} {'Name':<25} {'T080_pred':<11} {'T081_δ':<9} "
    f"{'T081_em':<9} {'T082_em':<9} {'DivMag':<10} {'BestExpl':<25}"
)
print(f"\n{header_final}")
print(f"{'─' * len(header_final)}")

divergences = []

for ass in ASSUMPTIONS:
    pred = t080_predicted({'MC2','MC3','MC4'}, ass)
    t081_delta = T081_EMERGENCE[ass]['delta']
    t081_em = T081_EMERGENCE[ass]['above_threshold']
    t082_em = T082_BASELINE[ass]['emerged']
    
    # Compute divergence magnitude
    if pred and not t081_em and not t082_em:
        div_mag = "HIGH"
    elif pred and (t081_delta > 0) and not t081_em:
        div_mag = "MODERATE"
    elif pred and t081_em:
        div_mag = "LOW"
    elif not pred and t081_em:
        div_mag = "LOW"
    else:
        div_mag = "NONE"
    
    # Determine best explanation
    if not pred:
        best_expl = "Not predicted"
    elif t081_delta < 0:
        best_expl = "H1: Over-mapping"
    elif t081_delta > 0 and not t081_em and t082_em:
        best_expl = "H2: Missing interaction"
    elif t081_delta > 0 and not t081_em and not t082_em:
        best_expl = "H1: Over-mapping"
    elif t081_delta > 0 and t081_delta < 0.3:
        best_expl = "H3: Threshold"
    elif t081_em:
        best_expl = "Match"
    else:
        best_expl = "Mixed"
    
    divergences.append((ass, pred, t081_delta, t081_em, t082_em, div_mag, best_expl))
    
    emoji = "✓" if div_mag == 'NONE' or div_mag == 'LOW' else "✗"
    row = (
        f"{ass:<8} {ASS_NAMES[ass]:<25} {'YES' if pred else 'NO':<11} "
        f"{t081_delta:<+9.3f} {'YES' if t081_em else 'NO':<9} "
        f"{'YES' if t082_em else 'NO':<9} {div_mag:<10} {best_expl:<25}"
    )
    print(f"  {row}")

# Aggregate counts
h1_count = sum(1 for _, _, _, _, _, _, e in divergences if e == 'H1: Over-mapping')
h2_count = sum(1 for _, _, _, _, _, _, e in divergences if e == 'H2: Missing interaction')
h3_count = sum(1 for _, _, _, _, _, _, e in divergences if e == 'H3: Threshold')
match_count = sum(1 for _, _, _, _, _, _, e in divergences if e in ['Match', 'Not predicted', ''])
high_div = sum(1 for _, _, _, _, _, d, _ in divergences if d == 'HIGH')

print(f"\n  {'─' * len(header_final)}")
print(f"  H1 (Over-mapping):     {h1_count} assumptions")
print(f"  H2 (Missing interact): {h2_count} assumptions")
print(f"  H3 (Threshold):        {h3_count} assumptions")
print(f"  Match / N/A:           {match_count} assumptions")
print(f"  High divergence:       {high_div} assumptions")

# ---- FORCED VERDICT ----
print(f"\n{'═' * 72}")
print("FORCED VERDICT")
print(f"{'═' * 72}")

# Compute evidence weights
# H1: number of assumptions with positive prediction but NEGATIVE delta
h1_weight = sum(1 for ass in ASSUMPTIONS if 
    t080_predicted({'MC2','MC3','MC4'}, ass) and T081_EMERGENCE[ass]['delta'] < 0)

# H2: number of FPs fixed by adding persistence constraint
h2_weight = sum(1 for ass in ASSUMPTIONS if 
    t080_predicted({'MC2','MC3','MC4'}, ass) and 
    not T082_BASELINE[ass]['emerged'] and 
    T082_SP[ass]['emerged'])

# H3: FPs with positive but sub-0.5 delta
h3_weight = sum(1 for ass in ASSUMPTIONS if 
    t080_predicted({'MC2','MC3','MC4'}, ass) and 
    not T081_EMERGENCE[ass]['above_threshold'] and 
    T081_EMERGENCE[ass]['delta'] > 0)

print(f"""
Evidence summary:
  H1 (Over-mapping):     {h1_weight} assumptions — predicted but empirically NEGATIVE
  H2 (Missing interact): {h2_weight} assumptions — MC234 FPs fixed by SP/MC5/MC1
  H3 (Threshold):        {h3_weight} assumptions — predicted, positive delta, below 0.5

Which hypothesis best explains the T080 ↔ T081/T082 discrepancy?
""")

if h1_weight >= 3 and h2_weight == 0 and h3_weight == 0:
    print("VERDICT: MAPPING ERROR")
    print("  T080's conceptual mapping is too generous. All false positives are")
    print("  assumptions that T080 claims emerge from MC2+MC3+MC4 but that the")
    print("  generative simulation shows are unaffected or anti-emergent.")
    print("  No missing constraint or threshold adjustment would fix this.")
elif h2_weight >= 3 and h1_weight == 0 and h3_weight <= 1:
    print("VERDICT: SIMULATION ERROR")
    print("  The generative simulation is missing a persistence-class constraint.")
    print("  T080's conceptual mapping is largely correct, but the simulation")
    print("  needs SP, MC5, or MC1 to reproduce the predicted emergence pattern.")
    print("  Adding persistence fixes all false positives without over-mapping.")
elif h3_weight >= 3 and h1_weight == 0 and h2_weight == 0:
    print("VERDICT: THRESHOLD ERROR")
    print("  All false positives have positive but sub-threshold deltas.")
    print("  The conceptual mapping is correct; only the detection threshold")
    print("  needs adjustment. The divergence is quantitative, not qualitative.")
elif h1_weight >= 1 and h2_weight >= 1:
    print("VERDICT: GENUINE THEORETICAL GAP")
    print("  Multiple factors contribute to the divergence:")
    if h1_weight > 0:
        print(f"    - {h1_weight} assumption(s) show over-mapping (predicted but anti-emergent)")
    if h2_weight > 0:
        print(f"    - {h2_weight} assumption(s) require persistence constraints (missing interaction)")
    if h3_weight > 0:
        print(f"    - {h3_weight} assumption(s) are threshold-sensitive")
    print()
    print("  The T080 conceptual model and the T081/T082 operational model disagree")
    print("  on both the scope and the mechanism of substrate emergence. This is not")
    print("  a simple calibration error — it reflects a genuine theoretical gap that")
    print("  cannot be resolved by adjusting a single parameter or adding one constraint.")
else:
    print("VERDICT: THRESHOLD ERROR")
    print("  The primary source of divergence is the 0.5 emergence threshold.")
    print("  Conceptual mapping and operational generation largely agree on direction.")
    print("  A lower threshold or continuous measure would align the results.")

# Specific breakdown
print(f"\n{'─' * 72}")
print("DETAILED DIVERGENCE BREAKDOWN")
print(f"{'─' * 72}")
print(f"""
Assumptions where T080 predictions are CONFIRMED by all empirical tests:
""")
for ass in ASSUMPTIONS:
    if T081_EMERGENCE[ass]['above_threshold'] or T082_BASELINE[ass]['emerged']:
        print(f"  ✓ {ass} ({ASS_NAMES[ass]}): T081 δ={T081_EMERGENCE[ass]['delta']:+.3f}")

print(f"""
Assumptions where T080 predictions are CONSISTENTLY REFUTED:
""")
for ass in ASSUMPTIONS:
    if T081_EMERGENCE[ass]['delta'] < 0 and not T082_BASELINE[ass]['emerged']:
        print(f"  ✗ {ass} ({ASS_NAMES[ass]}): T081 δ={T081_EMERGENCE[ass]['delta']:+.3f}")

print(f"""
Assumptions where T080 predictions are PARTIALLY supported (positive delta, below threshold):
""")
for ass in ASSUMPTIONS:
    if T081_EMERGENCE[ass]['delta'] > 0 and not T081_EMERGENCE[ass]['above_threshold']:
        print(f"  ~ {ass} ({ASS_NAMES[ass]}): T081 δ={T081_EMERGENCE[ass]['delta']:+.3f}")

# Save results
results = {
    'per_assumption': [],
    'hypothesis_scores': {
        'h1_over_mapping': h1_weight,
        'h2_missing_interaction': h2_weight,
        'h3_threshold_artifact': h3_weight,
    },
    'final_table': [
        {'assumption': a, 'predicted': p, 't081_delta': float(f'{d:.3f}'),
         't081_emerged': e, 't082_emerged': t, 'divergence_magnitude': m, 'best_explanation': x}
        for a, p, d, e, t, m, x in divergences
    ],
}

with open(OUT / "T085_divergence_results.json", 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\nResults saved to {OUT / 'T085_divergence_results.json'}")
print("\nT085 complete.")
