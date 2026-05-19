# FAILED METRIC POSTMORTEM — SECTION 2

**Date:** 2025-05-13

---

## DOCUMENT EXACTLY WHY V2_003 METRICS FAILED

---

## 1. WHY SIGMOID FITTING FAILED

**Observation:**
- Sigmoid fit produces R² > 0.99 on ALL data types
- Random Gaussian: R² = 0.993
- Hierarchical: R² = 0.993
- Sparse: R² = 0.993

**Root Cause:**
The sigmoid model D(k) = A / (1 + exp(-β(k - k0))) is flexible enough to fit ANY monotonic curve, including linear D(k) = k.

For D(k) ≈ k (near-linear), sigmoid with small β ≈ 0.2 produces excellent fit because:
- At k >> k0: D(k) ≈ A (saturates)
- At k << k0: D(k) ≈ A*exp(β(k-k0)) (exponential growth)
- In middle: approximately linear

**Result:** High R² is NOT evidence of structure—it's evidence of model flexibility.

---

## 2. WHY R² BECAME MEANINGLESS

**Observation:**
- Random data: R² = 0.994
- Organized data: R² = 0.994

**Root Cause:**
For D(k) ≈ k relationship:
- Sigmoid approximates linear growth
- Both random and structured data have D(k) growing approximately linearly with k
- R² cannot distinguish between different growth rates when growth is monotonic

**Result:** R² is invariant across data types—useless for discrimination.

---

## 3. WHY LINEAR D(k) PROFILES FOOLED THE MODEL

**Observation:**
- D(k) for random Gaussian: [1.0, 2.0, 3.0, ..., k]
- D(k) for hierarchical: [1.0, 2.0, 3.0, ..., k]

**Root Cause:**
Participation ratio definition:
D(k) = 1 / Σ(p_ij²)

For uniform random data, all k neighbors have equal probability → D(k) ≈ k

For hierarchical data (even with clear clusters), averaging over all points still produces approximately linear D(k) because:
- Clusters are embedded in continuous space
- Boundary effects average out
- Global dimensionality dominates local structure

**Result:** D(k) measures GLOBAL embedding dimension, not LOCAL cluster structure.

---

## 4. WHY TOPOLOGY DESTRUCTION BARELY CHANGED OUTPUTS

**Observation:**
- Original k0: 8.47
- After random shuffle: 8.53 (Δ = -0.06)
- After topology shuffle: 8.52 (Δ = -0.04)
- After noise injection: 8.53 (Δ = -0.05)

**Root Cause:**
k0 and R² are GLOBAL properties of the embedding:
- They depend on average behavior over all points
- Local topology changes don't affect global averages much
- For high-dimensional embeddings, global dimension dominates

**Result:** Metrics are insensitive to local structure changes.

---

## 5. WHY HIGH FIT QUALITY ≠ ORGANIZATIONAL STRUCTURE

**Evidence:**
| System | k0 | R² | A | β |
|--------|-----|-----|-----|-----|
| Random Gaussian | 5.82 | 0.995 | 11.6 | 0.21 |
| Hierarchical | 5.80 | 0.995 | 11.5 | 0.21 |
| Sparse | 5.82 | 0.995 | 11.6 | 0.21 |

**Conclusion:**
Perfect fit parameters are IDENTICAL across fundamentally different data structures.

**Root Cause:** The sigmoid model is too flexible and the D(k) metric is too global.

---

## EMPIRICAL EVIDENCE SUMMARY

| Failure | Evidence |
|---------|----------|
| Sigmoid overfitting | R² > 0.99 on random data |
| R² meaninglessness | No difference between systems |
| Linear D(k) dominance | D(k) ≈ k for all systems |
| Topology insensitivity | Δk0 < 0.1 after destruction |
| Multi-seed collapse | All seeds → same parameters |

---

## NO SPECULATION — ONLY OBSERVATIONS

These are empirical facts from V2_003. The metrics failed to provide discrimination power because:

1. The model (sigmoid) fits any monotonic curve
2. The metric (D(k)) measures global, not local, properties
3. The parameters (k0, R²) are invariant across data types

---

## Status

**DOCUMENTED**  
Next: Section 3 — Design new candidate metrics