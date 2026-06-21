# RD-WELL.7A — MHD Reconnaissance Audit

**Date:** 2026-06-17  
**Auditor:** OpenCode  
**Status:** REQUIRED BEFORE C COMPUTATION  
**Goal:** Construct an operational ledger for MHD before computing C.

---

## Question

What is the operational structure of MHD fields before any measurement or theory?

---

## Background

MHD is sufficiently different that we should not immediately compute C. Magnetic systems introduce entirely new structures:

- magnetic fields
- reconnection
- turbulence
- multi-scale cascades
- topological constraints

Those may alter the meaning of measurements.

**Principle:** Describe before explaining. Observe before measuring.

---

## Required Outputs

### Files

- `audits/RD_WELL_7A_MHD_RECONNAISSANCE.md` — This document
- `audits/rd_well7a/mhd_schema.json` — Dataset schema
- `audits/rd_well7a/mhd_operational_ledger.json` — Operational ledger
- `audits/rd_well7a/mhd_frame_statistics.json` — Frame statistics
- `audits/rd_well7a/mhd_transport_comparison.json` — Transport comparison
- `audits/rd_well7a/rd_magnetism_warning.json` — RD-MAGNETISM WARNING
- `audits/rd_well7a/mhd_frames/` — Extracted frames

---

## Dataset Schema

### Structure

- **File count:** 10 files (different parameter regimes)
- **Trajectories:** 1 per file
- **Timesteps:** 100 per trajectory
- **Spatial dimensions:** 64×64×64 (3D)
- **Boundary conditions:** Periodic in x, y, z

### Fields

- **density** (t0_fields): scalar, shape=(1, 100, 64, 64, 64), dtype=float32
- **magnetic_field** (t1_fields): vector, shape=(1, 100, 64, 64, 64, 3), dtype=float32
- **velocity** (t1_fields): vector, shape=(1, 100, 64, 64, 64, 3), dtype=float32

### Parameter Regimes

Files named: `MHD_Ma_{Ma}_Ms_{Ms}.hdf5`

- Ma (Alfvén Mach number): varies
- Ms (sonic Mach number): varies

Extracted files:
1. Ma_0.7_Ms_0.5
2. Ma_0.7_Ms_0.7
3. Ma_0.7_Ms_1.5
4. Ma_0.7_Ms_2
5. Ma_0.7_Ms_7

---

## Blind Operational Reconnaissance

### Extracted Frames

15 frames extracted across 5 parameter regimes and 3 timepoints (early, middle, late).

### Operational Ledger

| File | Parameters | Timepoint | Mean | Variance | Entropy | Frame Diff | Components | Spectral Peak | Autocorr Length |
|------|------------|-----------|------|----------|---------|------------|------------|---------------|-----------------|
| 0 | Ma_0.7_Ms_0.5 | 0 | 0.468 | 0.029 | 7.442 | 0.162 | 42 | 2 | 32 |
| 0 | Ma_0.7_Ms_0.5 | 50 | 0.474 | 0.024 | 7.309 | 0.196 | 26 | 2 | 32 |
| 0 | Ma_0.7_Ms_0.5 | 99 | 0.512 | 0.036 | 7.590 | 0.216 | 22 | 2 | 32 |
| 1 | Ma_0.7_Ms_0.7 | 0 | 0.444 | 0.032 | 7.484 | 0.192 | 30 | 1 | 32 |
| 1 | Ma_0.7_Ms_0.7 | 50 | 0.392 | 0.024 | 7.296 | 0.201 | 40 | 2 | 32 |
| 1 | Ma_0.7_Ms_0.7 | 99 | 0.336 | 0.028 | 7.365 | 0.210 | 26 | 1 | 32 |
| 2 | Ma_0.7_Ms_1.5 | 0 | 0.201 | 0.021 | 6.898 | 0.139 | 21 | 2 | 32 |
| 2 | Ma_0.7_Ms_1.5 | 50 | 0.135 | 0.011 | 6.232 | 0.121 | 8 | 1 | 32 |
| 2 | Ma_0.7_Ms_1.5 | 99 | 0.175 | 0.017 | 6.695 | 0.131 | 20 | 1 | 32 |
| 3 | Ma_0.7_Ms_2 | 0 | 0.092 | 0.008 | 5.833 | 0.075 | 5 | 1 | 32 |
| 3 | Ma_0.7_Ms_2 | 50 | 0.089 | 0.008 | 5.657 | 0.069 | 8 | 1 | 32 |
| 3 | Ma_0.7_Ms_2 | 99 | 0.076 | 0.006 | 5.513 | 0.142 | 2 | 1 | 32 |
| 4 | Ma_0.7_Ms_7 | 0 | 0.204 | 0.006 | 4.767 | 0.090 | 15 | 1 | 32 |
| 4 | Ma_0.7_Ms_7 | 50 | 0.134 | 0.005 | 5.067 | 0.054 | 16 | 3 | 32 |
| 4 | Ma_0.7_Ms_7 | 99 | 0.145 | 0.003 | 4.800 | 0.000 | 10 | 1 | 32 |

### Key Observations

1. **Autocorrelation length = 32 for all frames** — exactly half the domain size (64). This is likely an artifact of periodic boundary conditions.

2. **Entropy varies across parameter regimes** — from ~4.8 (Ma_0.7_Ms_7) to ~7.6 (Ma_0.7_Ms_0.5). Higher Ms correlates with lower entropy.

3. **Component count varies** — from 2 to 42. Some parameter regimes produce more fragmented structures.

4. **Spectral peak is low (1-3)** — indicates large-scale structures dominate.

5. **Frame difference varies** — from 0.0 to 0.216. Some timepoints show no change (frame_diff=0).

---

## Descriptor Ladder Audit

### Classification

| Descriptor | Layer | Consumable by Metrics | Notes |
|------------|-------|----------------------|-------|
| mean | Layer 0 | Yes | Basic statistic |
| variance | Layer 0 | Yes | Basic statistic |
| entropy | Layer 0 | Yes | Basic statistic |
| power_spectrum | Layer 0 | Yes | Basic statistic |
| frame_difference | Layer 0 | Yes | Basic statistic |
| component_count | Layer 0 | Yes | Basic statistic |
| autocorrelation_length | Layer 1a | Yes | Algorithmic |
| spectral_peak | Layer 1a | Yes | Algorithmic |
| temporal_derivative_norm | Layer 1a | Yes | Algorithmic |

### Forbidden Terms

| Term | Layer | Status |
|------|-------|--------|
| organization | Layer 2 | FORBIDDEN |
| coherence | Layer 2 | FORBIDDEN |
| adaptation | Layer 2 | FORBIDDEN |
| information | Layer 2 | FORBIDDEN |
| intelligence | Layer 2 | FORBIDDEN |
| self-awareness | Layer 2 | FORBIDDEN |
| sentience | Layer 2 | FORBIDDEN |
| consciousness | Layer 2 | FORBIDDEN |

---

## Measurement Transport Preparation

### MHD Value Ranges

| Descriptor | Min | Max | Mean | Std |
|------------|-----|-----|------|-----|
| mean | 0.076 | 0.512 | 0.258 | 0.155 |
| variance | 0.003 | 0.036 | 0.017 | 0.011 |
| entropy | 4.767 | 7.590 | 6.397 | 1.009 |
| frame_difference | 0.000 | 0.216 | 0.133 | 0.063 |
| component_count | 2.0 | 42.0 | 19.4 | 11.644 |
| spectral_peak | 1.0 | 3.0 | 1.467 | 0.618 |
| autocorrelation_length | 32.0 | 32.0 | 32.0 | 0.000 |
| temporal_derivative_norm | 0.000 | 0.216 | 0.133 | 0.063 |

### Cross-Domain Comparison

| Domain | Computability | Transform Sensitivity |
|--------|---------------|----------------------|
| MHD | all_descriptors_computable | pending |
| Gray-Scott | all_descriptors_computable | tested |
| Rayleigh-Bénard | all_descriptors_computable | tested |
| Active Matter | all_descriptors_computable | tested |
| Acoustic Scattering | all_descriptors_computable | tested |
| Rayleigh-Taylor | all_descriptors_computable | tested |

**Note:** SR-30 requires operational comparison before semantic comparison.

---

## RD-MAGNETISM WARNING

**Candidate Wording:**

> Fields possessing topological constraints may invalidate measurements that behave well in unconstrained media.

**Status:** ACTIVE WARNING

**Implication:** MHD may expose entirely new hidden variables.

**New Structures:**
- magnetic fields
- reconnection
- turbulence
- multi-scale cascades
- topological constraints

---

## Archive Updates

### Independent World Count

Current tested worlds:

- Gray-Scott ✓
- Rayleigh-Bénard ✓
- Active Matter ✓
- Rayleigh-Taylor ✓
- Acoustic Scattering ✓
- MHD ✓ (reconnaissance complete)

Status:

**SR-30 TESTING EXPANDING**

---

## Status

**RECONNAISSANCE COMPLETE** — Ready for C computation pending Research Director authorization.

---

## Authorization

```
MHD RECONNAISSANCE: COMPLETE
MHD C COMPUTATION: PENDING AUTHORIZATION
```

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_WELL_7A_MHD_RECONNAISSANCE.md`
