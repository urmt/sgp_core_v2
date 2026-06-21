# RD-WELL.5D.R3C — Field Normalization Audit

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Are measurements invariant under admissible field transformations?"  
**Status:** COMPLETE

---

## Question

Are measurements invariant under admissible field transformations?

---

## Admissible Transformations

1. **Original:** x
2. **Logarithmic:** log(x + ε)
3. **Z-score:** (x - μ) / σ
4. **Rank:** rank(x) / N
5. **Min-max:** (x - min) / (max - min)

---

## Invariance Scores

### Rayleigh-Bénard Buoyancy

| Measurement | Invariance Score |
|-------------|------------------|
| mean | 0.000 |
| variance | 0.000 |
| frame_diff_mean | 0.128 |

### Active Matter Concentration

| Measurement | Invariance Score |
|-------------|------------------|
| mean | 0.056 |
| variance | 0.000 |
| frame_diff_mean | 0.000 |

---

## Key Findings

1. **Mean and Variance:** Low invariance scores — measurements change under field transformations
2. **Frame Difference:** Moderate invariance score for Rayleigh-Bénard (0.128), low for Active Matter (0.000)
3. **Transformation Sensitivity:** Some measurements exhibit sensitivity to admissible field transformations

---

## Implications

**Transformation sensitivity was observed**

The same measurement (e.g., mean) produces different values under different field transformations (log, z-score, rank, min-max). This means:
- Transformation sensitivity is a candidate hidden variable
- Representation dependence affects comparability
- Unit dependence affects interpretation

**Safe wording:**
> Some operational measurements may remain computable and behaviorally similar across independent physical worlds, but transformation sensitivity was observed in some measurements under the tested transformations.

---

## Status

Field normalization audit complete. Transformation sensitivity was observed in some measurements under the tested transformations. Status: **UNDER TEST**

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5d_r3c/field_normalization_audit.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5d_r3c/run_field_normalization_audit.py`
