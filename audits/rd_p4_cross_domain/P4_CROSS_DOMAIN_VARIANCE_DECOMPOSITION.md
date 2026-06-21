# P4 — Cross-Domain Variance Decomposition Comparison

**Source:** Research Director (P4 authorization)
**Date:** 2026-06-17
**Status:** PROVISIONALLY ACCEPTED

## 1. Purpose

P4 was authorized to answer: **"How do variance structures differ across domains?"**

This reframes the question from "Which domain is most stable?" to a measurement-behavior comparison.

## 2. Method

- **Domains:** GS, RB, AM
- **Data sources:** P1 (GS), P2 (RB), P3 (AM) trajectory replication results
- **Quantities computed:**
  1. within/between ratio (variance structure)
  2. temporal spread (dynamical sensitivity)
  3. temporal signature (qualitative evolution)
  4. magnitude scale (absolute sensitivity)
  5. replication coverage (robustness)

## 3. Results

### 3.1 Table 1 — Variance Decomposition (Complete)

| Domain | Within | Between | Ratio | Mean ΔC_rank | Spread |
|--------|--------|---------|-------|--------------|--------|
| GS | 0.004087 | 0.003936 | 1.04x | 0.1610 | 0.1978 |
| RB | 0.000015 | 0.000014 | 1.05x | 0.0075 | 0.0125 |
| AM | 0.000030 | 0.000024 | 1.24x | 0.0183 | 0.0156 |

### 3.2 Table 2 — Temporal Spread (Dynamical Sensitivity)

| Domain | Temporal Spread | Between Spread | Total Spread |
|--------|-----------------|----------------|--------------|
| GS | 0.1593 | 0.0434 | 0.1978 |
| RB | 0.0106 | 0.0021 | 0.0125 |
| AM | 0.0148 | 0.0044 | 0.0156 |

### 3.3 Table 3 — Temporal Signatures

| Domain | Signature | Description |
|--------|-----------|-------------|
| GS | peaked | peaked in middle |
| RB | high_to_low_to_gradual | high → low → gradual |
| AM | high_to_low_to_gradual | high → low → gradual |

### 3.4 Table 4 — Magnitude Scale (Absolute Sensitivity)

| Domain | Mean ΔC_rank | Std | Min | Max | Range |
|--------|--------------|-----|-----|-----|-------|
| GS | 0.1610 | 0.0648 | 0.0224 | 0.2202 | 0.1978 |
| RB | 0.0075 | 0.0039 | 0.0011 | 0.0136 | 0.0125 |
| AM | 0.0183 | 0.0056 | 0.0108 | 0.0264 | 0.0156 |

### 3.5 Table 5 — Replication Coverage

| Domain | N_trajectories | N_frames | Status |
|--------|----------------|----------|--------|
| GS | 5 | 5 | adequate |
| RB | 5 | 5 | adequate |
| AM | 2 | 5 | LOW REPLICATION |

## 4. Analysis

### 4.1 Variance Structure

**Finding:** All three domains show within > between. Ratios cluster (1.04x, 1.05x, 1.24x).

**Interpretation:** The variance decomposition ordering is partially stable across domains. But AM ratio is higher, suggesting domain-specific modulation.

**Defensible statement:** "Within the currently tested domains and measurement procedures, temporal variation exceeded between-trajectory variation."

### 4.2 Temporal Signatures

**Finding:** RB and AM share high→low→gradual pattern. GS shows peaked pattern.

**Interpretation:** Temporal signatures may cluster by domain type. RB and AM are both fluid-like systems. GS is a reaction-diffusion system.

**Defensible statement:** "Temporal signatures may cluster by domain type."

### 4.3 Magnitude Scales

**Finding:** Magnitudes vary dramatically (0.0075 to 0.1610). Ratio: 21.5x.

**Interpretation:** RD-RATIO WARNING applies. Similar variance ratios conceal large differences in absolute measurement scale.

**Defensible statement:** "Ratio stability and magnitude instability coexist across domains."

### 4.4 Temporal Spread

**Finding:** GS has largest temporal spread (0.1593). RB has smallest (0.0106). AM is intermediate (0.0148).

**Interpretation:** Dynamical sensitivity varies across domains. GS is most sensitive to temporal location.

### 4.5 Replication Coverage

**Finding:** GS and RB have adequate coverage (5 trajectories). AM has LOW REPLICATION (2 trajectories).

**Interpretation:** AM results are provisional pending improved coverage.

## 5. Key Findings

1. **Variance structure is partially stable.** All three domains show within > between. Ratios cluster (1.04x, 1.05x, 1.24x). But AM ratio is higher, suggesting domain-specific modulation.

2. **Temporal signatures cluster.** RB and AM share high→low→gradual pattern. GS shows peaked pattern. This may reflect physical similarities (both fluid-like).

3. **Magnitude scales differ dramatically.** GS: 0.1610 (highest), AM: 0.0183 (intermediate), RB: 0.0075 (lowest). Ratio: 21.5x. RD-RATIO WARNING applies.

4. **Temporal spread varies.** GS: 0.1593 (largest), AM: 0.0148, RB: 0.0106 (smallest).

5. **Replication coverage is uneven.** GS and RB have adequate coverage. AM has LOW REPLICATION.

## 6. Defensible Statements

### Supported

1. "Within the currently tested domains and measurement procedures, temporal variation exceeded between-trajectory variation."

2. "The GS/RB variance decomposition pattern was also observed in AM under the present procedures."

3. "Ratio stability and magnitude instability coexist across domains."

4. "Temporal signatures may cluster by domain type."

### Not Yet Supported

1. "Temporal variation generally exceeds trajectory variation." (Sample remains too small)

## 7. Implications

1. **The project is becoming a measurement-behavior project.** The quantities being compared (ratio, spread, signature, magnitude) are properties of the measurement system, not just the physical systems.

2. **Magnitude, variance structure, and temporal signature may be partially independent properties.** This is WATCH ONLY territory.

3. **The archive should resist collapsing these into a single scalar notion of "stability."** Multiple quantities are needed to characterize measurement behavior.

4. **P5 (MHD) is now more meaningful.** MHD will test whether the pattern holds in a physically different domain (magnetic fields, topology, 3D).

## 8. Limitations

1. **N=2 trajectories for AM.** Results are provisional.
2. **Single regime per domain.** Only one parameter regime tested per domain.
3. **No protocol variation.** Transform and implementation held fixed.
4. **MHD and RT not yet included.** P5 will add MHD.

## 9. Next Steps

1. **P5: Plasma/MHD Self-Organization Audit** — Test whether pattern holds in magnetically constrained system.
2. **Protocol variation study.** Test different transforms and implementations.
3. **Temporal signature classification.** Develop systematic method for characterizing temporal patterns.
4. **External observers.** Genuinely independent researchers.

## 10. Provenance

- **Audit:** P4
- **Date:** 2026-06-17
- **Data sources:** P1 (GS), P2 (RB), P3 (AM)
- **Script:** `audits/rd_p4_cross_domain/run_p4_analysis.py`
- **Results:** `audits/rd_p4_cross_domain/p4_results.json`
- **Status:** PROVISIONALLY ACCEPTED
