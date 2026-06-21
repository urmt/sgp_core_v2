# RD-WELL.5D.R3 — Operational Cross-Domain Comparison

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Do not compute coupling yet"  
**Status:** COMPLETE

---

## Method

Compare only operational phenomena across independent worlds:
- appearance
- disappearance
- repetition
- movement
- stabilization
- boundary formation

No C, no coupling, no theory.

---

## Operational Phenomena Description

### Rayleigh-Bénard

#### Buoyancy
- Appearance: 10 frames
- Disappearance: 10 frames
- Repetition: 9 similarities
- Movement: 9 magnitudes
- Stabilization: decreasing=True
- Boundary formation: 3 frames

#### Pressure
- Appearance: 10 frames
- Disappearance: 10 frames
- Repetition: 9 similarities
- Movement: 9 magnitudes
- Stabilization: decreasing=True
- Boundary formation: 3 frames

#### Velocity Magnitude
- Appearance: 10 frames
- Disappearance: 10 frames
- Repetition: 9 similarities
- Movement: 9 magnitudes
- Stabilization: decreasing=False
- Boundary formation: 3 frames

---

### Active Matter

#### Concentration
- Appearance: 10 frames
- Disappearance: 10 frames
- Repetition: 9 similarities
- Movement: 9 magnitudes
- Stabilization: decreasing=True
- Boundary formation: 3 frames

#### Velocity Magnitude
- Appearance: 10 frames
- Disappearance: 10 frames
- Repetition: 9 similarities
- Movement: 9 magnitudes
- Stabilization: decreasing=True
- Boundary formation: 3 frames

---

## Cross-Domain Comparison

### Comparison 1: Rayleigh-Bénard_buoyancy vs Active Matter_concentration

**Similarities:** 3  
**Differences:** 0

| Phenomenon | Similarity |
|------------|------------|
| appearance_trend | 0.772 |
| stabilization_pattern | 1.000 |
| boundary_symmetry | 1.000 |

---

### Comparison 2: Rayleigh-Bénard_velocity_mag vs Active Matter_velocity_mag

**Similarities:** 2  
**Differences:** 1

| Phenomenon | Similarity |
|------------|------------|
| appearance_trend | 0.602 |
| boundary_symmetry | 1.000 |
| stabilization_pattern | Different |

---

## Key Findings

1. **Buoyancy vs Concentration:** Strong operational similarity (3/3 phenomena similar)
2. **Velocity Magnitude:** Partial similarity (2/3 phenomena similar)
3. **Stabilization Pattern:** Rayleigh-Bénard velocity does NOT decrease, Active Matter velocity DOES decrease
4. **Boundary Symmetry:** All fields show symmetric boundaries

---

## Status

Operational comparison complete. No metrics computed.

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5d_r3/cross_domain_comparison.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5d_r3/run_cross_domain_comparison.py`
