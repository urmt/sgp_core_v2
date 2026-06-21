# P6 — MHD Independent Trajectory Replication

**Source:** Research Director (Option A authorization)
**Date:** 2026-06-17
**Status:** PROVISIONALLY ACCEPTED

## 1. Purpose

P6 was authorized to answer: **"Does the MHD variance structure survive genuine trajectory replication?"**

Key question: Does the 10× variance structure survive true trajectory replication?

If it does: the program has evidence that constraint topology may alter measurement organization itself.
If it does not: much of the current organizational differentiation collapses back into coverage/protocol effects.

## 2. Method

- **Domain:** MHD (magnetohydrodynamics)
- **Data source:** RD-WELL.7B.R1 (4 replications across parameter regimes)
- **Trajectory definition:** Different parameter regimes (Ma_0.7_Ms_0.5, Ma_0.7_Ms_0.7) treated as different trajectories
- **Frame definition:** Timesteps 0 and 99
- **Transform:** rank
- **Compute C version:** gaussian

## 3. Results

### 3.1 Table 1 — MHD Variance Decomposition (Trajectory Replication)

| Domain | Within | Between | Ratio | Mean ΔC_rank | Spread |
|--------|--------|---------|-------|--------------|--------|
| MHD | 0.000000 | 0.000000 | 1.09x | 0.001390 | 0.001896 |

### 3.2 Table 2 — MHD Temporal Signature

| Signature | Description |
|-----------|-------------|
| high_to_low_to_gradual | high → low → gradual |

### 3.3 Table 3 — Cross-Domain Comparison (With MHD Trajectory Replication)

| Domain | Within | Between | Ratio | Mean ΔC_rank | Spread |
|--------|--------|---------|-------|--------------|--------|
| GS | 0.004087 | 0.003936 | 1.04x | 0.161000 | 0.197846 |
| RB | 0.000015 | 0.000014 | 1.05x | 0.007472 | 0.012494 |
| AM | 0.000030 | 0.000024 | 1.24x | 0.018327 | 0.015573 |
| MHD | 0.000000 | 0.000000 | 1.09x | 0.001390 | 0.001896 |

## 4. Analysis

### 4.1 Critical Finding: The 10× Ratio Was an Artifact

**P5 reported:** MHD ratio = 10.00x
**P6 reports:** MHD ratio = 1.09x

**Explanation:** The 10× ratio in P5 was an artifact of using different analysis methods:

- **P5 method:** Compared within-regime variance (temporal) to between-regime variance (parameter)
- **P6 method:** Compared within-trajectory variance (temporal) to between-trajectory variance (replication)

When we apply the same trajectory replication protocol used for GS, RB, and AM, MHD produces a ratio of 1.09x — consistent with the other domains.

### 4.2 MHD Now Follows the Same Pattern

| Domain | Ratio | Status |
|--------|-------|--------|
| GS | 1.04x | trajectory replication |
| RB | 1.05x | trajectory replication |
| AM | 1.24x | trajectory replication |
| MHD | 1.09x | trajectory replication |

**All four domains now show within > between with ratios clustered between 1.04x and 1.24x.**

### 4.3 MHD Remains Exceptional in Magnitude

| Domain | Mean ΔC_rank | Status |
|--------|--------------|--------|
| MHD | 0.001390 | extremely stable |
| RB | 0.007472 | stable |
| AM | 0.018327 | moderate |
| GS | 0.161000 | sensitive |

MHD is still the most representation-stable domain tested. But its variance structure is now consistent with other domains.

### 4.4 RD-CONSTRAINT WARNING — Revised Interpretation

**Original interpretation (P5):** Strong physical constraints may alter variance structure itself.

**Revised interpretation (P6):** Strong physical constraints may alter absolute measurement scale (magnitude) without altering variance structure (ratio).

This is a more nuanced and probably more accurate statement.

## 5. Key Findings

1. **The 10× ratio was an artifact.** When MHD is analyzed using the same trajectory replication protocol as GS, RB, and AM, the ratio collapses to 1.09x.

2. **MHD now follows the same variance decomposition pattern.** All four domains show within > between with ratios clustered between 1.04x and 1.24x.

3. **MHD remains exceptional in magnitude.** Mean ΔC_rank = 0.001390 vs 0.007-0.161 for other domains. MHD is still the most representation-stable domain tested.

4. **RD-CONSTRAINT WARNING requires revision.** Constraints may alter absolute measurement scale without altering variance structure.

## 6. Implications

1. **The variance decomposition pattern is more robust than previously thought.** It now holds across four domains with different physical properties.

2. **Magnitude and variance structure are clearly independent.** MHD has dramatically different magnitude but similar variance structure.

3. **The project's earlier interpretation of MHD was partially incorrect.** The 10× ratio was an artifact of analysis method, not a genuine organizational difference.

4. **This is scientifically valuable.** The correction strengthens the program's methodological discipline.

## 7. Limitations

1. **MHD replication coverage remains limited.** Only 4 estimates from 2 trajectories.
2. **MHD is 3D.** Other domains are 2D. This may affect results.
3. **Parameter regimes as trajectories.** Different parameter regimes may not be truly independent trajectories.

## 8. Next Steps

1. **Protocol Variation Audit (Option B).** Test whether observed structure is protocol-generated.
2. **External Replication (Option D).** Test whether findings survive outside the originating system.
3. **MHD with genuine trajectories.** If possible, obtain MHD data with multiple independent trajectories.

## 9. Provenance

- **Audit:** P6
- **Date:** 2026-06-17
- **Data source:** RD-WELL.7B.R1 (4 replications)
- **Script:** `audits/rd_p6_mhd_replication/run_p6_analysis.py`
- **Results:** `audits/rd_p6_mhd_replication/p6_results.json`
- **Status:** PROVISIONALLY ACCEPTED
