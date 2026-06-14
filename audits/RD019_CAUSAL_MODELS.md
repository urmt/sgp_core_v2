# RD-019: Causal Models — Full Regression Tables

**Date**: 2026-06-06
**Target variables**: dip (ΔC), restoration, τ_rec
**Predictors**: density (effective density = 50/(box_width × 30)), Residual(C) within density level, interaction
**Software**: statsmodels OLS

## Model Specifications (per Director's instructions)

- **Model A**: Recovery ~ Density
- **Model B**: Recovery ~ Density + Residual(C)
- **Model C**: Recovery ~ Residual(C)
- **Model D**: Recovery ~ Density + Residual(C) + Density × Residual(C)

Standardized predictors. 60 runs total. NaN rows dropped (full n=60 used).

---

## Target: ΔC (dip depth)

### Residual(C) within density level

| Model | R²    | AIC     | Coef: const     | Coef: density   | Coef: res_C      | Coef: density:res_C |
|-------|-------|---------|-----------------|-----------------|------------------|---------------------|
| A     | 0.011 | -189.6  | +0.015 (p=.021) | +0.005 (p=.431) | —                | —                   |
| B     | 0.087 | -192.4  | +0.015 (p=.017) | +0.005 (p=.416) | +0.013 (p=.033)  | —                   |
| C     | 0.077 | -193.7  | +0.015 (p=.017) | —               | +0.013 (p=.032)  | —                   |
| D     | 0.120 | -192.7  | +0.015 (p=.016) | +0.005 (p=.412) | +0.014 (p=.024)  | -0.009 (p=.152)     |

ΔR²(B-A) = +0.077 — **Residual(C) uniquely contributes** over density
ΔR²(B-C) = +0.011 — density contributes almost nothing over Residual(C) alone
ΔR²(D-B) = +0.033 — interaction is marginal (n.s.)

**Interpretation**: For ΔC, **density is irrelevant** (β=0.005, p=0.43). Residual(C) carries essentially all the explanatory power. Adding density to ResC-only model adds only 0.011 R².

### Residual(C) global

| Model | R²    | AIC     | Coef: const     | Coef: density   | Coef: res_C      | Coef: density:res_C |
|-------|-------|---------|-----------------|-----------------|------------------|---------------------|
| A     | 0.011 | -189.6  | +0.015 (p=.021) | +0.005 (p=.431) | —                | —                   |
| B     | 0.093 | -192.8  | +0.015 (p=.017) | +0.008 (p=.188) | +0.014 (p=.027)  | —                   |
| C     | 0.064 | -192.9  | +0.015 (p=.017) | —               | +0.012 (p=.050)  | —                   |
| D     | 0.119 | -192.5  | +0.013 (p=.039) | +0.009 (p=.175) | +0.015 (p=.024)  | -0.008 (p=.204)     |

Same pattern: density is n.s., Residual(C) is significant.

---

## Target: restoration

### Residual(C) within density level

| Model | R²    | AIC     | Coef: const      | Coef: density   | Coef: res_C      | Coef: density:res_C |
|-------|-------|---------|------------------|-----------------|------------------|---------------------|
| A     | 0.123 | -105.7  | +1.103 (p=.000)  | -0.036 (p=.006) | —                | —                   |
| B     | 0.390 | -125.4  | +1.103 (p=.000)  | -0.036 (p=.001) | -0.054 (p=.000)  | —                   |
| C     | 0.267 | -116.4  | +1.103 (p=.000)  | —               | -0.054 (p=.000)  | —                   |
| D     | 0.412 | -125.6  | +1.103 (p=.000)  | -0.036 (p=.001) | -0.052 (p=.000)  | -0.015 (p=.152)     |

ΔR²(B-A) = +0.267 — **Residual(C) uniquely contributes 0.267 R² over density alone**
ΔR²(B-C) = +0.123 — density uniquely contributes 0.123 R² over Residual(C) alone
ΔR²(D-B) = +0.022 — interaction is n.s.

**Interpretation**: For restoration, **both density and Residual(C) matter** (both p < 0.01 in Model B). Neither subsumes the other. They contribute additively.

### Residual(C) global

| Model | R²    | AIC     | Coef: const      | Coef: density   | Coef: res_C      | Coef: density:res_C |
|-------|-------|---------|------------------|-----------------|------------------|---------------------|
| A     | 0.123 | -105.7  | +1.103 (p=.000)  | -0.036 (p=.006) | —                | —                   |
| B     | 0.430 | -129.6  | +1.103 (p=.000)  | -0.050 (p=.000) | -0.059 (p=.000)  | —                   |
| C     | 0.209 | -111.8  | +1.103 (p=.000)  | —               | -0.047 (p=.000)  | —                   |
| D     | 0.442 | -128.8  | +1.100 (p=.000)  | -0.050 (p=.000) | -0.059 (p=.000)  | -0.011 (p=.291)     |

Global residual gives slightly higher R² (0.43 vs 0.39) because it absorbs some density-driven C variation.

---

## Target: τ_rec

### Residual(C) within density level

| Model | R²    | AIC   | Coef: const      | Coef: density   | Coef: res_C      | Coef: density:res_C |
|-------|-------|-------|------------------|-----------------|------------------|---------------------|
| A     | 0.084 | 663.9 | +72.8 (p=.000)   | +17.9 (p=.024)  | —                | —                   |
| B     | 0.175 | 659.6 | +72.8 (p=.000)   | +17.9 (p=.019)  | +18.6 (p=.015)   | —                   |
| C     | 0.091 | 663.5 | +72.8 (p=.000)   | —               | +18.6 (p=.019)   | —                   |
| D     | 0.209 | 659.1 | +72.8 (p=.000)   | +17.9 (p=.018)  | +17.7 (p=.019)   | +11.3 (p=.128)     |

ΔR²(B-A) = +0.091
ΔR²(B-C) = +0.084
ΔR²(D-B) = +0.034

Both density and Residual(C) significant in Model B for τ_rec (p<0.05).

### Residual(C) global

| Model | R²    | AIC   | Coef: const      | Coef: density   | Coef: res_C      | Coef: density:res_C |
|-------|-------|-------|------------------|-----------------|------------------|---------------------|
| A     | 0.084 | 663.9 | +72.8 (p=.000)   | +17.9 (p=.024)  | —                | —                   |
| B     | 0.195 | 658.2 | +72.8 (p=.000)   | +22.9 (p=.004)  | +21.1 (p=.007)   | —                   |
| C     | 0.065 | 665.1 | +72.8 (p=.000)   | —               | +15.7 (p=.050)   | —                   |
| D     | 0.209 | 659.1 | +74.6 (p=.000)   | +22.7 (p=.004)  | +20.9 (p=.008)   | +7.6 (p=.309)      |

Same pattern.

---

## Summary

| Target        | Density only (A) | ResC only (C) | Both (B) | ΔR²(B-A) | ΔR²(B-C) | Interaction (D-B) |
|---------------|------------------|---------------|----------|----------|----------|-------------------|
| ΔC (dip)      | R²=0.011 n.s.    | R²=0.077*     | R²=0.087 | +0.077   | +0.011   | +0.033 n.s.       |
| restoration   | R²=0.123**       | R²=0.267***   | R²=0.390 | +0.267   | +0.123   | +0.022 n.s.       |
| τ_rec         | R²=0.084*        | R²=0.091*     | R²=0.175 | +0.091   | +0.084   | +0.034 n.s.       |

(Significance: *p<0.05, **p<0.01, ***p<0.001)

---

## Pre-C: Did C move with density?

At the per-run level (n=60):
- r(pre_C, density) = -0.235, p = 0.070
- Linear regression: pre_C = 0.477 - 0.675 × density, R² = 0.055, density p = 0.070

At the per-condition level (n=6):
- r(pre_C_mean, density) = -0.753, p = 0.084

**C is essentially invariant under density manipulation** at friction=0.40. The slight negative trend is consistent with the sparseness prediction (lower density → slightly higher C) but the effect is small and statistically weak (R²=0.055 at the per-run level).

By contrast, all other structural descriptors (NN distance, contact count, coordination number, component count, MSD) responded with R² > 0.91 to the same density manipulation. The fact that C did NOT respond is a critical dissociation.

## Decision Rule Application

| Outcome | Criterion (target = ΔC) | Met? | Reasoning |
|---------|-------------------------|------|-----------|
| 1: Density explains it all | R²_A > 0.10 AND ΔR²(B-A) < 0.05 AND R²_C < 0.10 | **No** | R²_A = 0.011 (fails) |
| 2: Both density and ResC matter | density p < 0.05 AND res_C p < 0.05 in Model B | **No** | density p = 0.416 (fails) |
| 3: Density barely affects ResC | R²_C < 0.10 AND ΔR²(D-B) < 0.05 | **Yes** | R²_C = 0.077 AND ΔR²(D-B) = 0.033 |

**Algorithm flags Outcome 3** for the ΔC target.

**But the more meaningful pattern (per Director's framing):**

| Target      | Density matters? | ResC matters? | Pattern |
|-------------|------------------|---------------|---------|
| ΔC          | No (p=0.43)      | Yes (p=0.033) | **ResC alone** — density has no effect on dip depth |
| restoration | Yes (p=0.001)    | Yes (p<0.001) | **Both matter additively** — neither subsumes the other |
| τ_rec       | Yes (p=0.019)    | Yes (p=0.015) | **Both matter additively** — neither subsumes the other |

The Decision Rules as specified (with ΔC as primary target) flag Outcome 3. The full pattern across all three recovery targets reveals a more nuanced picture: **ResC is the sole predictor of dip depth, but both density and ResC contribute to restoration and τ_rec, with no interaction.**

## Causal Interpretation

The mediation hypothesis (H1: density → C → recovery) predicts that:
- density → C: significant
- C → recovery: significant
- density → recovery drops to n.s. when C is controlled

**Observation**:
- density → C: **R² = 0.055, p = 0.07** (n.s. at α=0.05)
- C → recovery: YES (within-level tests in RD-017 already established this)
- density → recovery: **YES for restoration and τ_rec (p<0.05), NO for ΔC (p=0.43)**

**The mediation chain is broken at step 1.** C is not causally downstream of density. Density does NOT move C. Therefore density cannot affect recovery through C.

**However**, density DOES affect restoration and τ_rec, but through some mechanism OTHER than C. The mechanism is unknown but operates independently of C.
