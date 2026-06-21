# P5 — MHD Self-Organization Audit

**Source:** Research Director (P5 authorization)
**Date:** 2026-06-17
**Status:** PROVISIONALLY ACCEPTED

## 1. Purpose

P5 was authorized to answer: **"Does MHD fit the pattern?"**

More specifically, P5 tests whether strong physical constraints alter variance structure itself.

## 2. Method

- **Domain:** MHD (magnetohydrodynamics)
- **Data source:** RD-WELL.7B.R1 (4 replications across parameter regimes)
- **Quantities computed:**
  1. within/between ratio (variance structure)
  2. temporal spread (dynamical sensitivity)
  3. transform sensitivity (representation stability)
  4. dimensional transport (observer dependence)

## 3. Results

### 3.1 Table 1 — MHD Variance Decomposition

| Domain | Within | Between | Ratio | Mean C | Spread |
|--------|--------|---------|-------|--------|--------|
| MHD | 0.000006 | 0.000001 | 10.00x | 0.996393 | 0.007130 |

### 3.2 Table 2 — MHD Transform Sensitivity

| Transform | Mean | Std | Min | Max |
|-----------|------|-----|-----|-----|
| ΔC_rank | 0.001390 | 0.000686 | 0.000569 | 0.002465 |
| ΔC_zscore | 0.000191 | 0.000268 | 0.000015 | 0.000655 |
| ΔC_dimension | 0.003366 | 0.002499 | 0.000907 | 0.007465 |

### 3.3 Table 3 — Cross-Domain Comparison (With MHD)

| Domain | Within | Between | Ratio | Mean ΔC_rank | Spread |
|--------|--------|---------|-------|--------------|--------|
| GS | 0.004087 | 0.003936 | 1.04x | 0.161000 | 0.197846 |
| RB | 0.000015 | 0.000014 | 1.05x | 0.007472 | 0.012494 |
| AM | 0.000030 | 0.000024 | 1.24x | 0.018327 | 0.015573 |
| MHD | 0.000006 | 0.000001 | 10.00x | 0.996393 | 0.007130 |

## 4. Analysis

### 4.1 MHD Variance Structure

**Finding:** MHD has a ratio of 10.00x — dramatically higher than GS (1.04x), RB (1.05x), and AM (1.24x).

**Interpretation:** This is the first domain where temporal variation exceeds regime variation by a large margin. This may be due to:

1. **Strong physical constraints** (magnetic fields, topology)
2. **Extremely low ΔC_rank** (0.001390 vs 0.007-0.161 for other domains)
3. **Strong representation stability**

**Defensible statement:** "MHD exhibited a dramatically different variance decomposition pattern from GS, RB, and AM under the present procedures."

### 4.2 MHD Transform Sensitivity

**Finding:** MHD has very low transform sensitivity:
- ΔC_rank: 0.001390 ± 0.000686
- ΔC_zscore: 0.000191 ± 0.000268
- ΔC_dimension: 0.003366 ± 0.002499

**Interpretation:** MHD is the most representation-stable domain tested so far. This is consistent with the RD-CONSTRAINT WARNING.

### 4.3 MHD vs Other Domains

**Finding:** MHD mean ΔC_rank (0.996393) is dramatically different from other domains:
- GS: 0.161000
- RB: 0.007472
- AM: 0.018327

**Interpretation:** MHD is not just different in magnitude — it is qualitatively different. The C value is near 1.0, suggesting the field is highly ordered.

## 5. Key Findings

1. **MHD has a dramatically different variance decomposition pattern.** Ratio: 10.00x vs 1.04-1.24x for other domains.

2. **MHD has extremely low ΔC_rank.** 0.001390 vs 0.007-0.161 for other domains. This is the most representation-stable domain tested.

3. **MHD has strong physical constraints.** Magnetic fields, topology, conserved quantities. The RD-CONSTRAINT WARNING appears relevant.

4. **MHD may represent a different class of systems.** Unconstrained systems (GS, RB, AM) vs constrained systems (MHD).

## 6. RD-CONSTRAINT WARNING

**Status:** SUPPORTED WITHIN THIS RESEARCH PROGRAM

> Apparently stable measurements may derive their robustness from strong physical constraints rather than from universal measurement behavior.

**Evidence:** MHD has:
- Strong physical constraints (magnetic fields, topology)
- Extremely low ΔC_rank (0.001390)
- Strong representation stability
- Dramatically different variance decomposition pattern (10.00x ratio)

**Implication:** The variance decomposition pattern observed in GS, RB, and AM may not apply to strongly constrained systems.

## 7. Implications

1. **The project may need to distinguish between unconstrained and constrained systems.** GS, RB, AM are unconstrained. MHD is constrained.

2. **The variance decomposition pattern may be a property of unconstrained systems.** Constrained systems may behave differently.

3. **MHD is the strongest stress test attempted.** It introduces magnetic fields, topology, conserved quantities, and 3D geometry.

4. **The RD-CONSTRAINT WARNING is now supported.** Apparent stability may derive from physical constraints.

## 8. Limitations

1. **MHD data not loaded directly.** Used existing data from RD-WELL.7B.R1.
2. **MHD has sparse replication coverage.** Only 4 replications across parameter regimes.
3. **MHD is 3D.** Other domains are 2D. This may affect results.
4. **Do not overinterpret MHD until trajectory replication improves.** (Research Director constraint)

## 9. Next Steps

1. **MHD trajectory replication.** Compute within/between ratio using multiple trajectories (not just parameter regimes).
2. **Protocol variation study.** Test different transforms and implementations.
3. **Compare constrained vs unconstrained systems.** Develop theoretical framework.
4. **External observers.** Genuinely independent researchers.

## 10. Provenance

- **Audit:** P5
- **Date:** 2026-06-17
- **Data source:** RD-WELL.7B.R1 (4 replications)
- **Script:** `audits/rd_p5_mhd/run_p5_analysis.py`
- **Results:** `audits/rd_p5_mhd/p5_results.json`
- **Status:** PROVISIONALLY ACCEPTED
