# RD-021: Causal Models

**Date:** 2026-06-06
**Companion to:** RD021_INTERVENTION_REPORT.md
**Outcome:** V-D (velocity-field hypothesis FALSIFIED)

---

## 1. Model specifications

Per Director's protocol, four models for each recovery target:

- **Model A:** `Recovery ~ VelocityCondition` (5 dummies vs V0)
- **Model B:** `Recovery ~ VelocityCondition + ResC_within`
- **Model C:** `Recovery ~ VelocityDiagnostics` (4 initial-window metrics)
- **Model D:** `Recovery ~ VelocityDiagnostics + ResC_within`

Targets: `dip` (ΔC), `restoration`, `tau_rec`.

Sample size: n=60 (10 reps × 6 conditions).

---

## 2. Model A — Recovery ~ VelocityCondition

This is the test of whether *condition identity* (any of the 5 manipulation
schemes) predicts recovery, ignoring C.

### dip (ΔC)
```
const      β=-0.0086  p=0.549
V1         β=+0.0237  p=0.246
V2         β=+0.0188  p=0.355
V3         β=-0.0021  p=0.917
V4         β=+0.0324  p=0.115
V5         β=-0.0047  p=0.817
R² = 0.0995
```
**All 5 condition dummies n.s.** Condition has no effect on dip depth.

### restoration
```
const      β=+1.155   p<0.0001
V1         β=-0.073   p=0.143
V2         β=-0.074   p=0.137
V3         β=-0.022   p=0.658
V4         β=-0.009   p=0.853
V5         β=+0.031   p=0.538
R² = 0.118
```
**All 5 dummies n.s.** Condition has no effect on restoration.

### tau_rec
```
const      β=+37.0    p=0.010
V1         β=+20.0    p=0.313
V2         β=+42.5    p=0.035
V3         β=+12.5    p=0.527
V4         β=+42.5    p=0.035
V5         β=+0.0     p=1.000
R² = 0.152
```
V2 and V4 show p<0.05 individually, but this is a multiple-comparisons
artefact. The overall ANOVA F=1.94, p=0.10 is non-significant.

---

## 3. Model B — Recovery ~ VelocityCondition + ResC

This is the test of whether C still predicts recovery *after* controlling for
velocity manipulation. C is a residual of the within-condition fit to
`pre_I_pred` (i.e., a within-condition anomaly score).

### dip
```
const      β=-0.0086  p=0.513
V1         β=+0.0237  p=0.206
V2         β=+0.0188  p=0.313
V3         β=-0.0021  p=0.910
V4         β=+0.0324  p=0.086
V5         β=-0.0047  p=0.801
res_C      β=+0.720   p=0.0014  ***
R² = 0.259
```
ResC β=+0.72, p=0.0014. **Condition dummies still all n.s.**
**ΔR²(B-A) = +0.16** — ResC explains 16% additional variance.

### restoration
```
const      β=+1.155   p<0.0001
V1         β=-0.073   p=0.045
V2         β=-0.074   p=0.041
V3         β=-0.022   p=0.540
V4         β=-0.009   p=0.798
V5         β=+0.031   p=0.394
res_C      β=-2.914   p<0.0001  ***
R² = 0.549
```
ResC β=-2.91, p<0.0001. V1/V2 become marginal in this model.
**ΔR²(B-A) = +0.43** — ResC explains 43% additional variance.

### tau_rec
```
const      β=+37.0    p=0.010
V1         β=+20.0    p=0.310
V2         β=+42.5    p=0.034
V3         β=+12.5    p=0.525
V4         β=+42.5    p=0.034
V5         β=+0.0     p=1.000
res_C      β=+278.4   p=0.222
R² = 0.176
```
ResC β=+278, p=0.22 (n.s. in this model). τ_rec has heavy ceiling effects
(several conditions lock at 37), which destroys linear-model power.
**ΔR²(B-A) = +0.02** — ResC adds little over condition for τ_rec.

---

## 4. Model C — Recovery ~ VelocityDiagnostics

This is the test of whether the *measured velocity diagnostics* (initial
window: align, nbrsim, entropy, KE) predict recovery.

### dip
```
const       β=+0.121   p=0.483
align_init  β=-0.015   p=0.833
nbrsim_init β=+0.002   p=0.963
entropy_init β=-0.041  p=0.561
ke_init     β=-0.003   p=0.149
R² = 0.059
```
**All 4 diagnostics n.s.** Velocity metrics have no linear effect on dip.
R² (0.059) is *worse* than Model A's 0.0995 (ΔR²(C-A) = -0.04).

### restoration
```
const       β=+1.345   p=0.002
align_init  β=-0.112   p=0.500
nbrsim_init β=-0.186   p=0.070
entropy_init β=-0.105  p=0.528
ke_init     β=+0.004   p=0.374
R² = 0.124
```
nbrsim_init β=-0.19, p=0.07 (borderline). This is the
*anti-alignment* finding from the Spearman table: higher initial
neighbor-similarity → slightly worse restoration. R² (0.124) is essentially
equal to Model A (0.118, ΔR²(C-A) = +0.006).

### tau_rec
```
const       β=-334.9   p=0.051
align_init  β=+117.7   p=0.088
nbrsim_init β=+85.5    p=0.043
entropy_init β=+158.4  p=0.024
ke_init     β=+2.3     p=0.241
R² = 0.101
```
nbrsim and entropy show p<0.05 but the model overall underperforms the
condition-only Model A (ΔR²(C-A) = -0.05).

---

## 5. Model D — Recovery ~ VelocityDiagnostics + ResC

### dip
```
const       β=+0.124   p=0.443
align_init  β=-0.017   p=0.799
nbrsim_init β=-0.006   p=0.873
entropy_init β=-0.046  p=0.487
ke_init     β=-0.002   p=0.298
res_C       β=+0.682   p=0.0036  **
R² = 0.196
```
ResC β=+0.68, p=0.0036. **All velocity diagnostics n.s.**
**ΔR²(D-C) = +0.14** — ResC adds 14% over diagnostics-only.

### restoration
```
const       β=+1.334   p<0.0001
align_init  β=-0.104   p=0.405
nbrsim_init β=-0.152   p=0.050
entropy_init β=-0.086  p=0.495
ke_init     β=+0.0004  p=0.923
res_C       β=-2.825   p<0.0001  ***
R² = 0.514
```
ResC β=-2.83, p<0.0001. nbrsim_init p=0.05 (borderline).
**ΔR²(D-C) = +0.39** — ResC adds 39% over diagnostics-only.

### tau_rec
```
const       β=-333.8   p=0.051
align_init  β=+116.9   p=0.089
nbrsim_init β=+82.0    p=0.052
entropy_init β=+156.4  p=0.025
ke_init     β=+2.7     p=0.175
res_C       β=+284.6   p=0.229
R² = 0.125
```
ResC p=0.23 (n.s.). τ_rec ceiling effects again destroy power.
**ΔR²(D-C) = +0.02** — ResC adds little for τ_rec.

---

## 6. ΔR² summary table

| Target | A→B (ResC over cond) | C→D (ResC over diag) | A→C (diag over cond) |
|--------|-----------------------|-----------------------|-----------------------|
| dip | **+0.159** | **+0.138** | -0.041 |
| restoration | **+0.431** | **+0.390** | +0.006 |
| tau_rec | +0.024 | +0.024 | -0.051 |

**Pattern:**
- ResC consistently adds substantial R² over both condition and diagnostics
- Velocity diagnostics add essentially nothing over condition (ΔR² A→C ≤ 0.006)
- For τ_rec, even ResC adds little (ceiling effect, not a falsification)

---

## 7. Conclusion

Causal models confirm the manipulation worked (diagnostics changed, condition
identity has some weak effects in nominal p-values) but those changes do not
propagate to C or to recovery in any systematic way.

C is not a measurement of velocity-field organization. C remains a strong
predictor of recovery even after controlling for all 4 velocity diagnostics
(β=-2.83, p<0.0001 for restoration).

**The velocity-field hypothesis is rejected as an explanation for C.**

This is the **third** negative result in the intervention series. The
hypotheses tested so far:
- RD-019: C is a density-driven state — FALSIFIED
- RD-020: C reflects structural importance / contact topology — WEAK-FORM FALSIFIED
- RD-021: C reflects velocity-field organization — FALSIFIED

All three interventions confirm that the structural and dynamical states
typically proposed as candidates for C do not affect it. C persists as a
predictor of recovery regardless of which state is manipulated.
