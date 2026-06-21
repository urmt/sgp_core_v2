# P2 — RB Independent Trajectory Replication with Replication Ledger

**Source:** Research Director (P2 authorization)
**Date:** 2026-06-17
**Status:** PROVISIONALLY ACCEPTED

## 1. Purpose

P2 was authorized to answer: **"How much of RB variation is temporal versus trajectory-driven?"**

This mirrors the GS protocol exactly, allowing direct comparison with P1.

## 2. Method

- **Domain:** Rayleigh-Bénard Convection
- **Trajectories:** 5 (indices 0–4)
- **Frame indices:** [0, 40, 80, 120, 160] (across 200 steps)
- **Transform:** rank
- **Field:** buoyancy (t0_fields)
- **Compute C version:** gaussian
- **Audit provenance:** P2

## 3. Results

### 3.1 Table A — Trajectory Replication

| trajectory | frame | ΔC_rank |
|------------|-------|---------|
| 0 | 0 | 0.0091 |
| 0 | 40 | 0.0027 |
| 0 | 80 | 0.0052 |
| 0 | 120 | 0.0093 |
| 0 | 160 | 0.0102 |
| 1 | 0 | 0.0114 |
| 1 | 40 | 0.0016 |
| 1 | 80 | 0.0042 |
| 1 | 120 | 0.0095 |
| 1 | 160 | 0.0088 |
| 2 | 0 | 0.0126 |
| 2 | 40 | 0.0011 |
| 2 | 80 | 0.0036 |
| 2 | 120 | 0.0096 |
| 2 | 160 | 0.0096 |
| 3 | 0 | 0.0132 |
| 3 | 40 | 0.0011 |
| 3 | 80 | 0.0047 |
| 3 | 120 | 0.0098 |
| 3 | 160 | 0.0101 |
| 4 | 0 | 0.0136 |
| 4 | 40 | 0.0014 |
| 4 | 80 | 0.0057 |
| 4 | 120 | 0.0091 |
| 4 | 160 | 0.0096 |

### 3.2 Table B — Within-Trajectory Spread

| trajectory | min | max | mean | spread |
|------------|-----|-----|------|--------|
| 0 | 0.0027 | 0.0102 | 0.0073 | 0.0075 |
| 1 | 0.0016 | 0.0114 | 0.0071 | 0.0098 |
| 2 | 0.0011 | 0.0126 | 0.0073 | 0.0114 |
| 3 | 0.0011 | 0.0132 | 0.0078 | 0.0121 |
| 4 | 0.0014 | 0.0136 | 0.0079 | 0.0121 |

### 3.3 Table C — Between-Trajectory Spread

| frame | mean ΔC_rank | SD |
|-------|--------------|-----|
| 0 | 0.0120 | 0.0016 |
| 40 | 0.0016 | 0.0006 |
| 80 | 0.0047 | 0.0007 |
| 120 | 0.0095 | 0.0003 |
| 160 | 0.0097 | 0.0005 |

### 3.4 Table D — Provenance Ledger

- Total estimates: 25
- Unique trajectories: 5
- Unique frames: 5
- Transform: rank
- Compute C version: gaussian
- Audit provenance: P2

## 4. Analysis

### 4.1 Dominant Source of Variation

| Source | Variance | Ratio |
|--------|----------|-------|
| Within-trajectory (temporal) | 0.000015 | 1.05x |
| Between-trajectory (replication) | 0.000014 | — |

**Dominant source: TEMPORAL (within-trajectory)**

But only marginally (1.05x ratio). Both sources contribute substantially.

### 4.2 Temporal Pattern

All trajectories exhibit:
- High ΔC_rank at frame 0 (range: 0.0091–0.0136)
- Drop to minimum at frame 40 (range: 0.0011–0.0016)
- Gradual increase through frames 80–160 (range: 0.0036–0.0102)

### 4.3 Trajectory-Level Variation

| Trajectory | mean ΔC_rank | Spread |
|------------|--------------|--------|
| 4 | 0.0079 | 0.0121 |
| 3 | 0.0078 | 0.0121 |
| 2 | 0.0073 | 0.0114 |
| 0 | 0.0073 | 0.0075 |
| 1 | 0.0071 | 0.0098 |

Trajectory 4 has highest mean ΔC_rank. Trajectory 1 has lowest.

## 5. Key Findings

1. **RB temporal pattern is distinct from GS:** GS shows low→high→stable. RB shows high→low→gradual increase.

2. **Temporal variation dominates (marginally):** Same ratio as GS (1.05x vs 1.04x).

3. **Between-trajectory variation is very small:** SD = 0.0003–0.0016 across frames.

4. **Overall ΔC_rank is much smaller than GS:** mean = 0.0075 vs GS mean = 0.1610.

## 6. GS vs RB Comparison

| Metric | GS | RB |
|--------|----|----|
| mean(ΔC_rank) | 0.1610 | 0.0075 |
| within-trajectory variance | 0.004087 | 0.000015 |
| between-trajectory variance | 0.003936 | 0.000014 |
| within/between ratio | 1.04x | 1.05x |
| range | 0.1978 | 0.0125 |
| temporal pattern | low→high→stable | high→low→gradual |

**Key observation:** The ratio of within/between variance is nearly identical across domains (1.04x vs 1.05x), but the absolute magnitudes differ by ~2 orders of magnitude.

## 7. Implications

1. **Temporal variation exceeds trajectory variation in both domains.** This suggests the temporal pattern may be a general feature of representation sensitivity.

2. **The temporal pattern itself differs between domains.** GS and RB show distinct temporal signatures. This suggests temporal variation is domain-specific, not a universal artifact.

3. **Absolute magnitude differs dramatically.** RB ΔC_rank is ~20× smaller than GS. This confirms representation-stability classes exist, but they are modulated by temporal location.

4. **No cross-domain ranking is valid without temporal sampling.** A single-frame estimate from either domain would be misleading.

## 8. Limitations

1. **Pseudoreplication acknowledged:** Temporal samples from same trajectory are not independent replications.
2. **N=5 trajectories:** Still small. No uncertainty estimates for trajectory-level variation.
3. **Single regime:** Only one RB parameter regime tested.
4. **No protocol variation:** Transform and implementation held fixed.

## 9. Next Steps

1. **P3: AM Independent Trajectory Replication**
2. **Protocol variation study:** Test different transforms and implementations.
3. **Temporal pattern classification:** Characterize temporal signatures across domains.
4. **External observers:** Genuinely independent researchers.

## 10. Provenance

- **Audit:** P2
- **Date:** 2026-06-17
- **Script:** P2 execution script
- **Data:** Rayleigh-Bénard Convection dataset
- **Status:** PROVISIONALLY ACCEPTED
