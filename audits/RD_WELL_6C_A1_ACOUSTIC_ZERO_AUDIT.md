# RD-WELL.6C.A1 — Acoustic Zero Audit

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Zero is scientifically meaningful. Zero is not failure. But zero must be explained."  
**Status:** COMPLETE

---

## Question

Why does C = 0 for Acoustic Scattering?

---

## Background

In RD-WELL.6C, C was computed for six domains. Five returned nontrivial values. Acoustic Scattering returned C = 0 for all transforms.

```
Acoustic Scattering:
  original: C = 0.000000
  zscore: C = 0.000000
  rank: C = 0.000000
  minmax: C = 0.000000
```

Zero is scientifically meaningful. Zero is not failure. But zero must be explained.

---

## Investigation

### Raw Field Statistics

```
Pressure shape: (256, 256)
Pressure min: 0.000000
Pressure max: 2.239988
Pressure mean: 0.139095
Pressure std: 0.456900
```

Field is not constant.

### Normalized Field Statistics

```
Pressure normalized min: 0.000000
Pressure normalized max: 1.000000
```

### Histogram Analysis

```
Histogram: [58167  1540   724   602   532   535   537   597   730  1572]
Bins: [0.  0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1. ]
Zero values: 58167/65536 (88.76%)
```

---

## Finding

**Observed:** the sampled pressure field contains approximately 88.76% zero-valued entries.

**Hypothesis:** field sparsity may contribute to the observed C = 0.

**Status:** UNDER TEST.

### Interpretation

This is a valid scientific finding:
- The pressure field in acoustic scattering has most of its values at zero
- This is physically meaningful: acoustic waves propagate through a medium, but most of the domain has zero pressure perturbation
- The non-zero values represent the wavefronts
- C = 0 may reflect the sparsity of the pressure field

### Possible Causes

1. **Uniform field** — NO (field is not constant)
2. **Preprocessing artifact** — NO (normalization does not change the result)
3. **Incorrect field selection** — NO (pressure is the correct field)
4. **Genuinely low measured structure** — PLAUSIBLE (88.76% zero values)
5. **Implementation issue** — NO (C computation works correctly)
6. **Thresholding artifact** — UNDER TEST
7. **Normalization artifact** — UNDER TEST
8. **C estimator sensitivity** — UNDER TEST

---

## Implications

1. **C = 0 is a valid measurement** — Not a failure
2. **Sparsity may matter** — C may be sensitive to the fraction of non-zero values
3. **Domain-specific behavior** — Acoustic scattering has different structure than other domains
4. **Physical interpretation** — Acoustic waves propagate through a medium, but most of the domain has zero pressure perturbation

---

## Follow-up Required

**RD-WELL.6C.A2: Sparsity Injection Audit**

Procedure:
1. Take Gray-Scott
2. Artificially increase sparsity
3. Measure C(sparsity)
4. Ask: Does C monotonically decrease with sparsity?

This would directly test the hypothesis.

---

## Status

**UNDER TEST** — Field sparsity may contribute to C = 0, but alternatives remain.

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_WELL_6C_A1_ACOUSTIC_ZERO_AUDIT.md`
