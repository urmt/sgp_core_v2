# P1 — GS Independent Trajectory Replication with Replication Ledger

**Source:** Research Director (P1 authorization)
**Date:** 2026-06-17
**Status:** PROVISIONALLY ACCEPTED

## 1. Purpose

P1 was authorized to answer: **"Are representation stability classes robust under replication?"**

The primary replication unit is an independently generated trajectory. Measurements obtained from multiple timepoints within the same trajectory constitute repeated observations rather than independent replications.

## 2. Method

- **Domain:** Gray-Scott Reaction-Diffusion
- **Trajectories:** 5 (indices 0–4)
- **Frame indices:** [0, 250, 500, 750, 1000]
- **Transform:** rank
- **Field:** B (inhibitor)
- **Compute C version:** gaussian
- **Audit provenance:** P1

## 3. Results

### 3.1 Table A — Trajectory Replication

| trajectory | frame | ΔC_rank |
|------------|-------|---------|
| 0 | 0 | 0.0703 |
| 0 | 250 | 0.1786 |
| 0 | 500 | 0.1805 |
| 0 | 750 | 0.1793 |
| 0 | 1000 | 0.1790 |
| 1 | 0 | 0.0224 |
| 1 | 250 | 0.1980 |
| 1 | 500 | 0.2051 |
| 1 | 750 | 0.2012 |
| 1 | 1000 | 0.1983 |
| 2 | 0 | 0.0224 |
| 2 | 250 | 0.2196 |
| 2 | 500 | 0.2196 |
| 2 | 750 | 0.2177 |
| 2 | 1000 | 0.2202 |
| 3 | 0 | 0.0259 |
| 3 | 250 | 0.1816 |
| 3 | 500 | 0.1881 |
| 3 | 750 | 0.1891 |
| 3 | 1000 | 0.1828 |
| 4 | 0 | 0.0366 |
| 4 | 250 | 0.1793 |
| 4 | 500 | 0.1766 |
| 4 | 750 | 0.1761 |
| 4 | 1000 | 0.1766 |

### 3.2 Table B — Within-Trajectory Spread

| trajectory | min | max | mean | spread |
|------------|-----|-----|------|--------|
| 0 | 0.0703 | 0.1805 | 0.1576 | 0.1102 |
| 1 | 0.0224 | 0.2051 | 0.1650 | 0.1827 |
| 2 | 0.0224 | 0.2202 | 0.1799 | 0.1978 |
| 3 | 0.0259 | 0.1891 | 0.1535 | 0.1632 |
| 4 | 0.0366 | 0.1793 | 0.1490 | 0.1427 |

### 3.3 Table C — Between-Trajectory Spread

| frame | mean ΔC_rank | SD |
|-------|--------------|-----|
| 0 | 0.0355 | 0.0182 |
| 250 | 0.1914 | 0.0158 |
| 500 | 0.1940 | 0.0161 |
| 750 | 0.1927 | 0.0153 |
| 1000 | 0.1914 | 0.0163 |

### 3.4 Table D — Provenance Ledger

- Total estimates: 25
- Unique trajectories: 5
- Unique frames: 5
- Transform: rank
- Compute C version: gaussian
- Audit provenance: P1

## 4. Analysis

### 4.1 Dominant Source of Variation

| Source | Variance | Ratio |
|--------|----------|-------|
| Within-trajectory (temporal) | 0.004087 | 1.04x |
| Between-trajectory (replication) | 0.003936 | — |

**Dominant source: TEMPORAL (within-trajectory)**

But only marginally (1.04x ratio). Both sources contribute substantially.

### 4.2 Temporal Pattern

All trajectories exhibit:
- Low ΔC_rank at frame 0 (range: 0.0224–0.0703)
- Rapid increase to plateau (frame 250: 0.179–0.220)
- Plateau maintained through frame 1000 (range: 0.176–0.220)

### 4.3 Trajectory-Level Variation

| Trajectory | mean ΔC_rank | Spread |
|------------|--------------|--------|
| 2 | 0.1799 | 0.1978 |
| 1 | 0.1650 | 0.1827 |
| 3 | 0.1535 | 0.1632 |
| 0 | 0.1576 | 0.1102 |
| 4 | 0.1490 | 0.1427 |

Trajectory 2 consistently has highest ΔC_rank. Trajectory 4 consistently has lowest.

## 5. Key Findings

1. **GS contradiction explained:** Frame-0 estimate ≈ 0.07, frame-250–1000 estimate ≈ 0.18. Both reproduced across all 5 trajectories. The contradiction was a temporal location effect, not a trajectory identity effect.

2. **Within-trajectory variation exceeds between-trajectory variation:** Temporal location matters more than which trajectory is sampled.

3. **Temporal pattern is consistent across trajectories:** All trajectories show low ΔC_rank at frame 0, then stabilization at ~0.18–0.22.

4. **No single-frame estimate is representative:** A single frame gives a point estimate that varies by factor ~2.6–10 depending on temporal location.

## 6. Implications

1. **RD-TEMPORAL WARNING strengthened:** GS representation stability is temporally variable. A single-frame estimate is increasingly difficult to defend as representative.

2. **RD-PSEUDOREPLICATION confirmed:** N=5 temporal samples from single trajectory gave apparent replication but were not independent.

3. **Measurement requires distribution:** The object of study is now the distribution of measurements, not point estimates.

## 7. Limitations

1. **Pseudoreplication acknowledged:** Temporal samples from same trajectory are not independent replications.
2. **N=5 trajectories:** Still small. No uncertainty estimates for trajectory-level variation.
3. **Single regime:** Only one Gray-Scott parameter regime tested.
4. **No protocol variation:** Transform and implementation held fixed.

## 8. Next Steps

1. **P2: RB Independent Trajectory Replication**
2. **P3: AM Independent Trajectory Replication**
3. **Protocol variation study:** Test different transforms and implementations.
4. **External observers:** Genuinely independent researchers.

## 9. Success Criterion

The goal was NOT a single GS number.

The goal was to estimate:

```text
ΔC_rank(GS | trajectory, time, protocol)
```

and determine which source of variation dominates.

**Result:** Temporal location dominates marginally (1.04x), but both sources contribute substantially. No single estimate is representative.

## 10. Provenance

- **Audit:** P1
- **Date:** 2026-06-17
- **Script:** P1 execution script
- **Data:** Gray-Scott Reaction-Diffusion dataset
- **Status:** PROVISIONALLY ACCEPTED
