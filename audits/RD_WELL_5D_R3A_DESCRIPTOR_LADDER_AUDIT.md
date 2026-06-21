# RD-WELL.5D.R3A — Descriptor Ladder Audit

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Before computing any new metric, create a descriptor ladder"  
**Status:** COMPLETE

---

## Descriptor Ladder (Revised)

### Layer 0 — Raw
- mean(field)
- variance(field)
- entropy(field)
- power spectrum
- component count
- frame difference
- spatial autocorrelation
- mean intensity
- variance over time
- frame-to-frame difference

### Layer 1a — Algorithmic (Computed directly)
- connected component count
- power spectral peak
- spatial autocorrelation length
- temporal derivative norm

### Layer 1b — Human-Labeled (Require interpretation)
- stabilization
- boundary formation
- periodicity
- drift
- repetition
- movement
- disappearance
- appearance

### Layer 2 — Interpretive (FORBIDDEN for metrics)
- organization
- coherence
- adaptation
- information

**Rule:** Metrics may only consume Layer 0, Layer 1a, or Layer 1b. Layer 2 is forbidden.

**Note:** Layer 1b descriptors are not observed directly — they are inferred from rules. This doesn't make them invalid, but they are one level more abstract than Layer 1a.

---

## Descriptor Audit

### Field Descriptors

All fields use only Layer 1 descriptors:
- appearance
- disappearance
- repetition
- movement
- stabilization
- boundary_formation

**Status:** ✓ PASS

---

### Comparison Descriptors

| Comparison | Descriptor | Layer | Status |
|------------|------------|-------|--------|
| RB_buoyancy vs AM_concentration | appearance_trend | Layer 2 | ✗ FAIL |
| RB_buoyancy vs AM_concentration | stabilization_pattern | Layer 2 | ✗ FAIL |
| RB_buoyancy vs AM_concentration | boundary_symmetry | Layer 2 | ✗ FAIL |
| RB_velocity vs AM_velocity | appearance_trend | Layer 2 | ✗ FAIL |
| RB_velocity vs AM_velocity | boundary_symmetry | Layer 2 | ✗ FAIL |
| RB_velocity vs AM_velocity | stabilization_pattern | Layer 2 | ✗ FAIL |

**Status:** ✗ FAIL — Layer 2 descriptors used in comparisons

---

## Reclassification Recommendations

| Original | Reclassified | Layer |
|----------|--------------|-------|
| appearance_trend | mean_intensity_over_time | Layer 0 |
| stabilization_pattern | frame_difference_trend | Layer 0 |
| boundary_symmetry | boundary_formation | Layer 1 |

---

## RD-WELL.5D.R3 Status

**FINALIZED** (with descriptor decontamination complete)

---

## Most Important Surviving Statement

> Some operational descriptors may survive transport across independent physical worlds.

Status: **UNDER TEST**

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5d_r3a/descriptor_ladder_audit.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5d_r3a/run_descriptor_ladder_audit.py`
