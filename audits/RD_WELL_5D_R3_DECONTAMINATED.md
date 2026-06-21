# RD-WELL.5D.R3 — Cross-Domain Comparison (Decontaminated)

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Finalize R3 with descriptor decontamination"  
**Status:** COMPLETE

---

## Method

Compare only operational phenomena across independent worlds using ONLY Layer 0 and Layer 1 descriptors.

**Layer 0 — Raw:** mean, variance, entropy, power spectrum, component count, frame difference  
**Layer 1 — Derived:** stabilization, boundary formation, periodicity, drift, repetition  

**Layer 2 — Interpretive:** organization, coherence, adaptation, information (FORBIDDEN)

---

## Layer 0 Descriptors Computed

### Rayleigh-Bénard Buoyancy
- mean_over_time
- variance_over_time
- frame_to_frame_difference
- spatial_autocorrelation

### Active Matter Concentration
- mean_over_time
- variance_over_time
- frame_to_frame_difference
- spatial_autocorrelation

---

## Layer 1 Descriptors Computed

### Rayleigh-Bénard Buoyancy
- stabilization_decreasing
- stabilization_rate
- boundary_formation
- movement_magnitudes
- repetition_similarities

### Active Matter Concentration
- stabilization_decreasing
- stabilization_rate
- boundary_formation
- movement_magnitudes
- repetition_similarities

---

## Cross-Domain Comparison Results

### Layer 0 Comparison

| Phenomenon | Similarity | Layer |
|------------|------------|-------|
| mean_intensity_trend | 0.772 | Layer_0 |
| frame_difference_trend | 0.970 | Layer_0 |

### Layer 1 Comparison

| Phenomenon | Similarity | Layer |
|------------|------------|-------|
| stabilization_pattern | 1.000 | Layer_1 |
| boundary_symmetry | 1.000 | Layer_1 |

---

## Key Findings

1. **Frame Difference Trend:** Very high similarity (0.970) — both domains show similar rates of change
2. **Stabilization Pattern:** Identical behavior (1.000) — both stabilize
3. **Boundary Symmetry:** Identical behavior (1.000) — both show symmetric boundaries
4. **Mean Intensity Trend:** Moderate similarity (0.772) — similar but not identical trends

---

## Status

Cross-domain comparison complete. Using only Layer 0 and Layer 1 descriptors.

**RD-WELL.5D.R3 is now FINALIZED.**

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5d_r3_decontaminated/cross_domain_comparison_decontaminated.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5d_r3_decontaminated/run_cross_domain_comparison_decontaminated.py`
