# RD-WELL.3 — Operational Ledger Construction

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** RD-WELL.2 complete — blind observations collected  
**Status:** IN PROGRESS

---

## Purpose

Construct a structured operational ledger from blind observations.
This ledger records WHAT was observed, not WHAT it means.

---

## Prohibited Words (from RD-WELL.2)

- coherence, fertility, interaction, persistence, emergence
- observer, sentience, hierarchy, organization, structure
- pattern, function, purpose, adaptive, self, collective
- global, local, information, complexity, dynamics, stability
- attractor, state, variable, parameter, system

---

## Allowed Vocabulary

- **Spatial:** position, value, gradient, boundary, region, domain
- **Temporal:** step, frame, before, after, during, sequence, interval
- **Quantitative:** number, count, ratio, fraction, mean, variance, range
- **Qualitative:** present, absent, increasing, decreasing, constant, oscillating, random
- **Relational:** adjacent, distant, nearby, separate, connected, isolated

---

## Gray-Scott Reaction Diffusion — Operational Ledger

### System Properties
- **Fields:** A, B (concentrations)
- **Resolution:** 128 × 128
- **Boundary:** Periodic
- **Time steps:** 1001 (t=0 to t=1000)
- **Parameters:** F (feed rate), k (kill rate)

### Pattern: Bubbles (F=0.098, k=0.057)

| Time | A mean | A std | A variance | B mean | B std | B variance | A local max | B local max |
|------|--------|-------|------------|--------|-------|------------|-------------|-------------|
| 0 | 0.8967 | 0.1459 | 0.021282 | 0.0579 | 0.1280 | 0.016389 | 94 | 30 |
| 100 | 0.9653 | 0.1183 | 0.013986 | 0.0219 | 0.0853 | 0.007277 | 3073 | 3758 |
| 500 | 0.9695 | 0.1105 | 0.012216 | 0.0193 | 0.0806 | 0.006488 | 3081 | 3820 |
| 1000 | 0.9696 | 0.1104 | 0.012184 | 0.0192 | 0.0805 | 0.006473 | 3132 | 3784 |

**Operational changes:**
- A mean: +0.072862
- B mean: -0.038668
- A variance: -0.009098
- B variance: -0.009916
- A local max: +3038
- B local max: +3754

---

### Pattern: Maze (F=0.029, k=0.057)

| Time | A mean | A std | A variance | B mean | B std | B variance | A local max | B local max |
|------|--------|-------|------------|--------|-------|------------|-------------|-------------|
| 0 | 0.8929 | 0.1327 | 0.017601 | 0.0314 | 0.1012 | 0.010247 | 107 | 100 |
| 100 | 0.5952 | 0.2206 | 0.048657 | 0.1384 | 0.1110 | 0.012316 | 199 | 557 |
| 500 | 0.5153 | 0.1460 | 0.021312 | 0.1635 | 0.0973 | 0.009468 | 485 | 623 |
| 1000 | 0.5139 | 0.1446 | 0.020897 | 0.1639 | 0.0972 | 0.009438 | 500 | 618 |

**Operational changes:**
- A mean: -0.379045
- B mean: +0.132477
- A variance: +0.003296
- B variance: -0.000809
- A local max: +393
- B local max: +518

---

### Pattern: Spirals (F=0.018, k=0.051)

| Time | A mean | A std | A variance | B mean | B std | B variance | A local max | B local max |
|------|--------|-------|------------|--------|-------|------------|-------------|-------------|
| 0 | 0.8967 | 0.1459 | 0.021282 | 0.0579 | 0.1280 | 0.016389 | 94 | 30 |
| 100 | 0.6134 | 0.2423 | 0.058720 | 0.1033 | 0.1053 | 0.011092 | 98 | 520 |
| 500 | 0.6458 | 0.2265 | 0.051309 | 0.0862 | 0.0969 | 0.009382 | 82 | 537 |
| 1000 | 0.5918 | 0.2394 | 0.057296 | 0.1078 | 0.1031 | 0.010634 | 119 | 532 |

**Operational changes:**
- A mean: -0.304885
- B mean: +0.049884
- A variance: +0.036014
- B variance: -0.005755
- A local max: +25
- B local max: +502

---

### Pattern: Gliders (F=0.014, k=0.054)

| Time | A mean | A std | A variance | B mean | B std | B variance | A local max | B local max |
|------|--------|-------|------------|--------|-------|------------|-------------|-------------|
| 0 | 0.8967 | 0.1459 | 0.021282 | 0.0579 | 0.1280 | 0.016389 | 94 | 30 |
| 1000 | 0.7647 | 0.1943 | 0.037771 | 0.0478 | 0.0794 | 0.006309 | 106 | 502 |

**Operational changes:**
- A mean: -0.131955
- B mean: -0.010118
- A variance: +0.016489
- B variance: -0.010080
- A local max: +12
- B local max: +472

---

### Pattern: Spots (F=0.03, k=0.062)

| Time | A mean | A std | A variance | B mean | B std | B variance | A local max | B local max |
|------|--------|-------|------------|--------|-------|------------|-------------|-------------|
| 0 | 0.8929 | 0.1327 | 0.017601 | 0.0314 | 0.1012 | 0.010247 | 107 | 100 |
| 1000 | 0.6639 | 0.1707 | 0.029140 | 0.1096 | 0.1123 | 0.012620 | 478 | 221 |

**Operational changes:**
- A mean: -0.229036
- B mean: +0.078153
- A variance: +0.011539
- B variance: +0.002373
- A local max: +371
- B local max: +121

---

### Pattern: Worms (F=0.058, k=0.065)

| Time | A mean | A std | A variance | B mean | B std | B variance | A local max | B local max |
|------|--------|-------|------------|--------|-------|------------|-------------|-------------|
| 0 | 0.8967 | 0.1459 | 0.021282 | 0.0579 | 0.1280 | 0.016389 | 94 | 30 |
| 1000 | 0.7447 | 0.2183 | 0.047660 | 0.1204 | 0.1398 | 0.019533 | 249 | 633 |

**Operational changes:**
- A mean: -0.151976
- B mean: +0.062504
- A variance: +0.026378
- B variance: +0.003144
- A local max: +155
- B local max: +603

---

## Rayleigh-Bénard Convection — Operational Ledger

### System Properties
- **Fields:** buoyancy, pressure
- **Resolution:** 512 × 128
- **Boundary:** Periodic horizontally, rigid vertically
- **Time steps:** 200
- **Parameters:** Rayleigh (Ra), Prandtl (Pr)

### Configuration: Ra=1e6, Pr=1

| Time | Buoyancy mean | Buoyancy std | Buoyancy variance | Buoyancy local max |
|------|---------------|--------------|-------------------|---------------------|
| 0 | 0.1000 | 0.0707 | 0.005000 | 141 |
| 50 | 0.2693 | 0.3259 | 0.106213 | 11 |
| 100 | 0.3572 | 0.2452 | 0.060112 | 64 |
| 150 | 0.3972 | 0.2394 | 0.057332 | 54 |
| 199 | 0.4239 | 0.2393 | 0.057252 | 41 |

**Operational changes:**
- Buoyancy mean: +0.323933
- Buoyancy variance: +0.052252
- Buoyancy local max: -100

---

### Configuration: Ra=1e8, Pr=1

| Time | Buoyancy mean | Buoyancy std | Buoyancy variance | Buoyancy local max |
|------|---------------|--------------|-------------------|---------------------|
| 0 | 0.1000 | 0.0707 | 0.005000 | 141 |
| 50 | 0.1875 | 0.2265 | 0.051320 | 601 |
| 100 | 0.2338 | 0.2020 | 0.040804 | 1144 |
| 150 | 0.2696 | 0.1976 | 0.039064 | 788 |
| 199 | 0.2969 | 0.1960 | 0.038401 | 942 |

**Operational changes:**
- Buoyancy mean: +0.196914
- Buoyancy variance: +0.033401
- Buoyancy local max: +801

---

### Configuration: Ra=1e10, Pr=1

| Time | Buoyancy mean | Buoyancy std | Buoyancy variance | Buoyancy local max |
|------|---------------|--------------|-------------------|---------------------|
| 0 | 0.1000 | 0.0707 | 0.005000 | 141 |
| 50 | 0.1494 | 0.1757 | 0.030859 | 9294 |
| 100 | 0.1742 | 0.1534 | 0.023543 | 8123 |
| 150 | 0.1933 | 0.1495 | 0.022365 | 8716 |
| 199 | 0.2109 | 0.1476 | 0.021775 | 8246 |

**Operational changes:**
- Buoyancy mean: +0.110870
- Buoyancy variance: +0.016775
- Buoyancy local max: +8105

---

## Cross-Domain Operational Comparison

### Quantities That Change

| Domain | Quantity | Direction | Magnitude |
|--------|----------|-----------|-----------|
| Gray-Scott | A mean | varies | -0.38 to +0.07 |
| Gray-Scott | B mean | varies | -0.04 to +0.13 |
| Gray-Scott | A variance | varies | -0.009 to +0.036 |
| Gray-Scott | B variance | varies | -0.010 to +0.003 |
| Gray-Scott | A local max | varies | +12 to +3038 |
| Gray-Scott | B local max | varies | +121 to +3754 |
| Rayleigh-Bénard | Buoyancy mean | increases | +0.11 to +0.32 |
| Rayleigh-Bénard | Buoyancy variance | increases | +0.017 to +0.052 |
| Rayleigh-Bénard | Buoyancy local max | varies | -100 to +8105 |

### Initial Conditions

All systems start from similar initial conditions:
- Gray-Scott: A mean ~0.89, B mean ~0.03-0.06
- Rayleigh-Bénard: Buoyancy mean ~0.10

### Parameter Dependence

Both systems show different outcomes depending on parameter values:
- Gray-Scott: F and k determine pattern type
- Rayleigh-Bénard: Ra determines flow regime

---

## Artifact

- Framework: `/home/student/sgp_core_v2/audits/RD_WELL_3_OPERATIONAL_LEDGER.md`
- Data: 
  - `/home/student/sgp_core_v2/audits/rd_well2/gray_scott_time_series_observations.json`
  - `/home/student/sgp_core_v2/audits/rd_well2/gray_scott_remaining_patterns_observations.json`
  - `/home/student/sgp_core_v2/audits/rd_well2/rayleigh_benard_blind_observations.json`
