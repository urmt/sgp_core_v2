# RD-WELL.7A.R2 — Volume vs Slice Audit

**Date:** 2026-06-17  
**Auditor:** OpenCode  
**Status:** REQUIRED BEFORE MHD C COMPUTATION  
**Goal:** Determine whether measurement behavior survives dimensional reduction.

---

## Question

Does measurement behavior survive dimensional reduction?

---

## Background

Pipeline comparison:

```
3D volume
    ↓
Compute descriptor directly

versus

3D volume
    ↓
Slice/project
    ↓
Compute descriptor
```

If 3D → 2D changes measurement behavior substantially, then many previous domains may also contain hidden observer assumptions.

---

## Required Outputs

### Files

- `audits/RD_WELL_7A_R2_VOLUME_VS_SLICE_AUDIT.md` — This document
- `audits/rd_well7a_r2/volume_descriptors.json` — 3D volume descriptors
- `audits/rd_well7a_r2/slice_descriptors.json` — 2D slice descriptors
- `audits/rd_well7a_r2/delta_measurement.json` — Δ_measurement_dimension
- `audits/rd_well7a_r2/hidden_variables.json` — Hidden variable candidates

---

## A. Volume Descriptors (3D)

| Descriptor | Value |
|------------|-------|
| mean | 1.000576 |
| variance | 0.021706 |
| entropy | 7.081423 |
| component_count | 1 |
| power_spectrum_peak | 1 |
| power_spectrum_mean | 415808638.78 |

---

## B. Slice Descriptors (2D)

### Slices

| Slice | Mean | Variance | Entropy | Components | Spectrum Peak |
|-------|------|----------|---------|------------|---------------|
| xy_z32 | 0.999 | 0.019 | 7.442 | 1 | 2 |
| xz_y32 | 1.028 | 0.022 | 7.553 | 1 | 2 |
| yz_x32 | 0.999 | 0.018 | 7.485 | 1 | 1 |

### Projections

| Projection | Mean | Variance | Entropy | Components | Spectrum Peak |
|------------|------|----------|---------|------------|---------------|
| mean_z | 1.001 | 0.003 | 7.383 | 1 | 2 |
| mean_y | 1.001 | 0.002 | 7.570 | 1 | 1 |
| mean_x | 1.001 | 0.003 | 7.403 | 1 | 1 |
| max_z | 1.258 | 0.010 | 7.259 | 1 | 1 |
| max_y | 1.291 | 0.008 | 7.230 | 1 | 1 |
| max_x | 1.286 | 0.008 | 7.266 | 1 | 1 |

---

## C. Δ_measurement_dimension (Normalized)

### Summary Table

| Slice/Projection | mean | variance | entropy | spectrum_peak | spectrum_mean |
|------------------|------|----------|---------|---------------|---------------|
| xy_z32 | 0.001 | 0.145 | 0.051 | 1.000 | 1.000 |
| xz_y32 | 0.027 | 0.026 | 0.067 | 1.000 | 1.000 |
| yz_x32 | 0.001 | 0.176 | 0.057 | 0.000 | 1.000 |
| mean_z | 0.000 | 0.849 | 0.043 | 1.000 | 1.000 |
| mean_y | 0.000 | 0.907 | 0.069 | 0.000 | 1.000 |
| mean_x | 0.000 | 0.877 | 0.045 | 0.000 | 1.000 |
| max_z | 0.258 | 0.524 | 0.025 | 0.000 | 1.000 |
| max_y | 0.290 | 0.639 | 0.021 | 0.000 | 1.000 |
| max_x | 0.285 | 0.622 | 0.026 | 0.000 | 1.000 |

### Key Findings

1. **mean:** Survives dimensional reduction well (Δ_norm < 0.03 for slices, 0 for projections by definition).

2. **variance:** Does NOT survive — projections lose 85-91% of variance compared to 3D volume.

3. **entropy:** Survives reasonably well (Δ_norm < 0.07). Entropy changes by 2-7% depending on slicing.

4. **component_count:** Not meaningful (all have 1 component in this field).

5. **power_spectrum:** Does NOT survive — 3D vs 2D power spectra are fundamentally different.

---

## D. Hidden Variable Candidates

### Observer Geometry

**Status:** PLAUSIBLE / UNDER TEST

**Definition:** Measurement behavior that depends on the geometric relationship between observer and field.

**Distinction from Slice Dependence:**

| Variable | Meaning |
|----------|---------|
| Slice Dependence | choice of projection |
| Observer Geometry | orientation relative to structure |

### Slice Dependence

**Status:** PLAUSIBLE / UNDER TEST

**Definition:** Measurement outcomes may depend on how higher-dimensional structures are projected or observed.

**Generalization:** Applies to tomography, microscopy, cosmology, neuroscience, plasma diagnostics.

---

## Methodological Survivor

Record:

> **Estimator behavior may vary more strongly than the phenomenon being measured.**

**Status:** SUPPORTED WITHIN THIS RESEARCH PROGRAM

**Evidence:**

- entropy
- connected components
- segmentation
- rank transforms
- normalization
- slicing
- dimensional reduction

---

## RD-TOPOLOGY WARNING (Updated)

**Candidate Wording:**

> Measurements developed on unconstrained fields may fail or change behavior in topologically constrained systems.

**Status:** ACTIVE WARNING

**Applications:**

- vortices
- defects
- knots
- flux tubes
- biological networks

---

## Independent World Count

Operational reconnaissance has now been performed across six distinct physical domains:

- Gray-Scott
- Rayleigh-Bénard
- Active Matter
- Rayleigh-Taylor
- Acoustic Scattering
- MHD

**Status:** SR-30 TESTING EXPANDING

---

## Status

**VOLUME VS SLICE AUDIT COMPLETE** — Ready for C computation pending Research Director authorization.

---

## Authorization

```
RD-WELL.7A: PROVISIONALLY ACCEPTED
RD-WELL.7A.R1: PROVISIONALLY ACCEPTED
RD-WELL.7A.R2: COMPLETE
MHD C COMPUTATION: PENDING AUTHORIZATION
```

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_WELL_7A_R2_VOLUME_VS_SLICE_AUDIT.md`
