# RD-WELL.5B — Alternative Stabilization Metrics Audit

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Construct independent stabilization observables"  
**Status:** COMPLETE

---

## Objective

Construct operational stabilization observables independent of C.

Forbidden: causal language, theory words, survivor promotion.

---

## Method

Three stabilization observables tested on Gray-Scott bubbles:

### S₁: Spectral Entropy Plateau

Compute 1D spectral entropy of mean field over rolling window.

* Metric series: (150,) values [0.0000, 0.0016]
* Stabilization at entropy change < threshold

| Threshold | Stab. Time |
|-----------|-----------|
| 0.01      | t = 86    |
| 0.03      | t = 75    |
| 0.05      | t = 69    |
| 0.1       | t = 61    |

**Threshold sensitivity:** Stable. All thresholds produce detection. Time range: 61-86.

---

### S₂: Temporal Derivative Norm

Compute ||X_t - X_{t-1}|| over time.

* Metric series: (199,) values [0.0000, 0.0261]
* Stabilization at derivative < threshold

| Threshold | Stab. Time |
|-----------|-----------|
| 0.01      | t = 86    |
| 0.03      | t = 35    |
| 0.05      | t = 6     |
| 0.1       | t = 5     |

**Threshold sensitivity:** High sensitivity. Time range: 5-86. Metric spans 3 orders of magnitude.

---

### S₃: Morphology Persistence

Binarize field, count pixels above threshold, measure changes.

* Metric series: (199,) values [0, 1146]
* Stabilization at change < threshold

| Threshold | Stab. Time |
|-----------|-----------|
| 0.01      | t = 63    |
| 0.03      | t = 5     |
| 0.05      | t = 2     |
| 0.1       | t = 2     |

**Threshold sensitivity:** Very high. Time range: 2-63. Metric has extreme outliers.

---

## Comparison Table

| Observable   | Threshold Range | Stab. Time Range | Threshold Robustness |
|-------------|-----------------|------------------|---------------------|
| S₁ Spectral Entropy | 0.01-0.1    | 61-86            | Good (Δ=25)        |
| S₂ Temporal Derivative | 0.01-0.1  | 5-86             | Poor (Δ=81)        |
| S₃ Morphology Persistence | 0.01-0.1 | 2-63            | Very Poor (Δ=61)   |

---

## Finding

**S₁ (Spectral Entropy) is the most threshold-stable stabilization observable tested.**

S₂ and S₃ show high threshold sensitivity, similar to RD-WELL.5A frame variance.

---

## Status

All three metrics are operational definitions.

None have been validated as independent of C.

This audit supports the possibility that spectral entropy is a more robust stabilization observable than frame variance or derivative norm.

---

## Next Steps (per Research Director)

P1: Compute correlation with C (Independence Audit)
P2: Test on maze, spirals, Rayleigh-Bénard
P3: Joint geometry analysis (if correlations permit)

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5b/stabilization_metrics.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5b/run_stabilization_metrics.py`
