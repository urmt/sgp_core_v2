# RD-WELL.7B.R1 — MHD Replication Audit

**Date:** 2026-06-17  
**Auditor:** OpenCode  
**Status:** PROVISIONALLY ACCEPTED  
**Goal:** Verify MHD results are robust under replication.

---

## Question

Does MHD remain representation-stable under replication?

---

## Results

### C Values (N=4)

| Metric | Mean | Std | 95% CI |
|--------|------|-----|--------|
| C_original | 0.9964 | 0.0027 | ±0.0026 |
| C_rank | 0.9957 | 0.0034 | — |
| C_zscore | 0.9966 | 0.0024 | — |

### Transform Sensitivity

| Metric | Mean | Std |
|--------|------|-----|
| ΔC_rank | 0.0014 | 0.0007 |
| ΔC_zscore | 0.0002 | 0.0003 |
| ΔC_dimension | 0.0034 | 0.0025 |

---

## Key Findings

### 1. Representation Stability Class (Updated)

**Status:** STRONG EVIDENCE ACCUMULATING

**Within the currently tested domains, representation sensitivity spans approximately two orders of magnitude.**

| Domain | Mean(ΔC_rank) | Status |
|--------|---------------|--------|
| MHD | 0.001 | PROVISIONALLY ACCEPTED |
| RB | 0.057 | PROVISIONALLY ACCEPTED |
| AM | 0.065 | PROVISIONALLY ACCEPTED |
| RT | 0.120 | PROVISIONALLY ACCEPTED |
| GS | 0.227 | PROVISIONALLY ACCEPTED |

**Span:** ~200× range (0.001 to 0.227)

**Evidence:**

The pattern has now survived:

- Replication (multiple trajectories/timepoints)
- Transform audits
- Dimensional audits
- Multiple independent physical worlds

### 2. MHD C Values Are Very High and Stable

**C_original = 0.9964 ± 0.0027**

This is the highest C value observed across all tested domains.

**The important point is not that MHD is "special." The important point is: A highly different physical world did not strongly perturb C. That is exactly what SR-30 was designed to test.**

**Status:** DESCRIPTIVE, NOT EXPLANATORY

### 3. Constraint Structure as Hidden Variable Candidate

**Status:** PLAUSIBLE / UNDER TEST

**Definition:** Structural restrictions imposed by conservation laws, topology, or field constraints that alter measurement behavior.

**Evidence:**

- MHD: Most constrained system (magnetic fields, divergence-free, conservation laws). ΔC_rank = 0.001 (lowest)
- RB: Moderate constraints (incompressibility, buoyancy). ΔC_rank = 0.057 (moderate)
- AM: Moderate constraints (active forces, orientation). ΔC_rank = 0.065 (moderate)
- RT: Moderate constraints (density stratification, gravity). ΔC_rank = 0.120 (intermediate)
- GS: Minimal constraints (reaction-diffusion only). ΔC_rank = 0.227 (highest)

**Possible hypothesis:** Highly constrained systems may exhibit greater representation stability.

**Possible confounders:**

- Dimensionality (2D vs 3D)
- Boundary conditions
- Field smoothness
- Conservation laws
- Discretization choices
- Parameter regimes
- Estimator properties

**Status:** PLAUSIBLE / UNDER TEST — No promotion.

---

## Representation Stability Class

**Status:** STRONG EVIDENCE ACCUMULATING

**Within the currently tested domains, representation sensitivity spans approximately two orders of magnitude.**

---

## Constraint Structure

**Status:** PLAUSIBLE / UNDER TEST

**Possible confounders:**

- Dimensionality (2D vs 3D)
- Boundary conditions
- Field smoothness
- Conservation laws
- Discretization choices
- Parameter regimes
- Estimator properties

---

## RD-CONSTRAINT WARNING

> Apparently stable measurements may derive their robustness from strong physical constraints rather than from universal measurement behavior.

**Status:** ACTIVE WARNING

---

## New Methodological Survivor

> **Within the currently tested physical domains, representation sensitivity exhibited reproducible differences under the present measurement procedures.**

**Status:** SUPPORTED WITHIN THIS RESEARCH PROGRAM

---

## Status

**PROVISIONALLY ACCEPTED** — MHD replication results are robust.

---

## Authorization

```
RD-WELL.7A: PROVISIONALLY ACCEPTED
RD-WELL.7A.R1: PROVISIONALLY ACCEPTED
RD-WELL.7A.R2: PROVISIONALLY ACCEPTED
RD-WELL.7B: PROVISIONALLY ACCEPTED
RD-WELL.7B.R1: PROVISIONALLY ACCEPTED
```

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_WELL_7B_R1_MHD_REPLICATION_AUDIT.md`
