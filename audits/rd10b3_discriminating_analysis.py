"""
RD-10B.3 Discrimiting Analysis

The post-hoc detectors are universal time-series properties.
Every world exhibits every motif.

The question becomes:
1. Do motif STRENGTHS differ between worlds?
2. Do motif strengths change at transition points?
3. Do world parameters predict motif strengths?
4. What actually distinguishes worlds with many transitions from few?

Standing rule: patterns may belong to world, representation, detector, or question.
These patterns belong to the DETECTOR — they are time-series properties.
"""

import json
import numpy as np
from collections import defaultdict

# Load results
with open('/home/student/sgp_core_v2/audits/rd10b3_results.json') as f:
    data = json.load(f)

results = data['results']

print("="*70)
print("RD-10B.3 DISCRIMINATING ANALYSIS")
print("="*70)

# ============================================================
# 1. MOTIF STRENGTH DISTRIBUTIONS
# ============================================================
print("\n--- 1. Motif Strength Distributions ---")

for motif in ['binding', 'hierarchy', 'recursion', 'template', 'cycle']:
    values = [r['motifs'].get(motif, 0) for r in results]
    print(f"\n{motif}:")
    print(f"  Mean: {np.mean(values):.4f}")
    print(f"  Std:  {np.std(values):.4f}")
    print(f"  Min:  {np.min(values):.4f}")
    print(f"  Max:  {np.max(values):.4f}")
    print(f"  CV:   {np.std(values)/np.mean(values):.4f}" if np.mean(values) > 0 else "  CV:   N/A")

# ============================================================
# 2. WORLD PARAMETERS vs MOTIF STRENGTHS
# ============================================================
print("\n--- 2. World Parameters vs Motif Strengths ---")

param_keys = ['coupling', 'decay', 'nonlinearity']

for param in param_keys:
    print(f"\n{param}:")
    values = [r[param] for r in results]
    
    for motif in ['binding', 'hierarchy', 'recursion', 'template', 'cycle']:
        motif_vals = [r['motifs'].get(motif, 0) for r in results]
        
        # Correlation
        if np.std(values) > 0 and np.std(motif_vals) > 0:
            corr = np.corrcoef(values, motif_vals)[0, 1]
            print(f"  {motif}: r={corr:.3f}")
        else:
            print(f"  {motif}: r=N/A (zero variance)")

# ============================================================
# 3. TRANSITIONS vs WORLD PARAMETERS
# ============================================================
print("\n--- 3. Transitions vs World Parameters ---")

n_transitions = [len(r['transitions']) for r in results]
print(f"Transitions: mean={np.mean(n_transitions):.0f}, std={np.std(n_transitions):.0f}")

for param in param_keys:
    values = [r[param] for r in results]
    if np.std(values) > 0 and np.std(n_transitions) > 0:
        corr = np.corrcoef(values, n_transitions)[0, 1]
        print(f"  {param}: r={corr:.3f}")

# ============================================================
# 4. MOTIF STRENGTH vs TRANSITIONS
# ============================================================
print("\n--- 4. Motif Strength vs Number of Transitions ---")

for motif in ['binding', 'hierarchy', 'recursion', 'template', 'cycle']:
    motif_vals = [r['motifs'].get(motif, 0) for r in results]
    if np.std(motif_vals) > 0 and np.std(n_transitions) > 0:
        corr = np.corrcoef(motif_vals, n_transitions)[0, 1]
        print(f"  {motif}: r={corr:.3f}")

# ============================================================
# 5. CRITICAL INSIGHT: WHAT'S THE QUESTION DOING?
# ============================================================
print("\n--- 5. The Question's Effect ---")
print("The detectors measure TIME-SERIES PROPERTIES, not architectural motifs.")
print("")
print("Binding = pairwise correlation (any coupled system has this)")
print("Hierarchy = variance in variance (any heterogeneous system has this)")
print("Recursion = autocorrelation (any system with memory has this)")
print("Template = self-similarity (any stable system has this)")
print("Cycle = dominant frequency (any oscillating system has this)")
print("")
print("These are PROPERTIES OF THE REPRESENTATION (time series)")
print("not PROPERTIES OF THE WORLD (architecture).")
print("")
print("The question 'what motifs appear?' selects for time-series properties.")
print("A different question would select for different patterns.")

# ============================================================
# 6. WHAT WOULD A GENUINE DETECTOR LOOK LIKE?
# ============================================================
print("\n--- 6. What Would Genuine Detection Require? ---")
print("A genuine detector must distinguish:")
print("  - World property (exists regardless of measurement)")
print("  - Representation property (depends on how you describe it)")
print("  - Detector property (depends on what you measure)")
print("  - Question property (depends on what you ask)")
print("")
print("Current detectors fail this test.")
print("They detect representation properties, not world properties.")

