# RD-WELL.6B.R1 — Coupling Stability Under Transformation

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "For every domain, compute C under all transforms, compute S₁, S₂, S₃ under all transforms, compute coupling matrix, report Δr_transform"  
**Status:** PROVISIONAL

**Note:** N=4 transforms is extremely small. The four transforms are not independent samples — they are the same field, same trajectory, same world, same measurement, different coordinate transforms. Effective N << 4. Correlations are exploratory, not inferential.

---

## Question

Does the relationship survive change, or only the measurement?

---

## Method

For every domain:
1. Compute C under all transforms.
2. Compute S₁, S₂, S₃ under all transforms.
3. Compute coupling matrix.
4. Report: Δr_transform

---

## Results

### Rayleigh-Bénard Buoyancy

| Transformation | C | S₁ | S₂ | S₃ |
|----------------|-----|-----|-----|-----|
| original | 0.745474 | 2.613826 | 0.006814 | 1.000000 |
| zscore | 0.745474 | 3.119682 | 0.034159 | 1.000000 |
| rank | 0.765508 | 1.129723 | 0.001640 | 1.000000 |
| minmax | 0.745474 | 2.613878 | 0.006822 | 1.000000 |

### Active Matter Concentration

| Transformation | C | S₁ | S₂ | S₃ |
|----------------|-----|-----|-----|-----|
| original | 0.771579 | 0.000604 | 0.000874 | 0.844951 |
| zscore | 0.771579 | 1.883995 | 0.127886 | 0.844951 |
| rank | 0.732803 | 1.095887 | 0.028442 | 0.813508 |
| minmax | 0.771579 | 0.208779 | 0.011312 | 0.844951 |

---

## Cross-Transform Coupling

### Rayleigh-Bénard Buoyancy

| Coupling | Pearson r | p-value | N | Note |
|----------|-----------|---------|---|------|
| C-S₁ | -0.960800 | 0.039200 | 4 | Significant (p < 0.05) |
| C-S₂ | -0.484905 | 0.515095 | 4 | Not significant |
| C-S₃ | nan | nan | 4 | S₃ constant (1.000000) |

### Active Matter Concentration

| Coupling | Pearson r | p-value | N | Note |
|----------|-----------|---------|---|------|
| C-S₁ | -0.229782 | 0.770218 | 4 | Not significant |
| C-S₂ | 0.156533 | 0.843467 | 4 | Not significant |
| C-S₃ | 1.000000 | 0.000000 | 4 | Perfect correlation (warning light) |

---

## Key Findings

1. **Sample size is small (N=4)** — correlations computed over 4 transformations, not independent observations
2. **C-S₁ coupling in Rayleigh-Bénard:** Strong negative correlation (r = -0.961, p = 0.039), but N=4 is too small for reliable inference
3. **C-S₃ coupling in Active Matter:** Perfect positive correlation (r = 1.000, p = 0.000) — this is a warning light, not a victory
4. **S₃ constant in Rayleigh-Bénard:** S₃ = 1.000000 for all transforms — this explains the NaN in coupling computation

---

## NaN Analysis

**Why was S₃ undefined in Rayleigh-Bénard?**

S₃ (morphology persistence) was constant (1.000000) for all transformations in Rayleigh-Bénard. This means:
- S₃ had zero variance
- Correlation coefficient is undefined for constant input
- This is not missing data — it is a scientific finding

**Possible reasons:**
- Constant metric
- Zero variance
- Failed segmentation
- Domain mismatch
- Representation mismatch

**This may reveal another hidden variable:** Segmentation Dependence

---

## Implications

**Some relationships may survive transformation, but sample size is too small for reliable inference.**

- C-S₁ coupling in Rayleigh-Bénard is strong but N=4 is insufficient
- C-S₃ coupling in Active Matter is perfect but likely an artifact of small sample size
- S₃ constant in Rayleigh-Bénard suggests domain-specific behavior

**Safe wording:**
> Some measurements and relationships remain computable across independent physical worlds, but their stability under representation change remains under test.

---

## Status

Coupling stability under transformation audit complete. Sample size is too small for reliable correlation claims.

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well6b_r1/coupling_stability_audit.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well6b_r1/run_coupling_stability_audit.py`
