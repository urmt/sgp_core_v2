# P10 — Signature Robustness Audit

**Source:** Research Director (continuation of P9)
**Date:** 2026-06-17
**Status:** PROVISIONALLY ACCEPTED

## 1. Purpose

P10 answers: **"Do stable signatures remain stable under aggressive protocol perturbation?"**

### Why P10 Matters

P9 established that temporal signatures can be formalized as provisional organizational descriptors. However, P9 only tested stability across trajectories and basic transforms. P10 stress-tests signatures under more aggressive protocol perturbation.

## 2. Protocol Perturbations

| Perturbation | Description | Purpose |
|--------------|-------------|---------|
| Transform variation | rank, raw, zscore, minmax | Test transform sensitivity |
| Temporal subsampling | every 1, 2, 5, 10 timesteps | Test temporal resolution sensitivity |
| Window size variation | 3, 5, 10 timesteps | Test temporal window sensitivity |
| Noise injection | Gaussian noise (σ = 0.01, 0.05, 0.1) | Test noise sensitivity |

## 3. Results

### 3.1 Table 1 — Descriptor Stability Under Perturbation

| Domain | Baseline | Stability | Status |
|--------|----------|-----------|--------|
| GS | peaked | 0.90 | FRAGILE |
| RB | high_to_low_to_gradual | 0.40 | FRAGILE |
| AM | high_to_low_to_gradual | 0.60 | FRAGILE |
| MHD | insufficient_data | 1.00 | ROBUST |

### 3.2 Table 2 — Metric Stability Across Perturbations

| Domain | Spread CV | Persistence CV | Volatility CV | Mean CV |
|--------|-----------|----------------|---------------|---------|
| GS | 1.5173 | 0.0000 | 3.0000 | 1.5058 |
| RB | 1.6280 | 0.0000 | 3.0000 | 1.5427 |
| AM | 1.6295 | 0.0000 | 3.0000 | 1.5432 |
| MHD | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

### 3.3 Table 3 — Signature Robustness Classification

| Domain | Descriptor Stability | Metric Stability | Overall Status |
|--------|---------------------|------------------|----------------|
| GS | HIGH | LOW | FRAGILE |
| RB | LOW | LOW | FRAGILE |
| AM | MEDIUM | LOW | FRAGILE |
| MHD | HIGH | HIGH | ROBUST |

## 4. Analysis

### 4.1 Critical Finding: Most Signatures Are Fragile

P10 reveals that:
- **GS**: FRAGILE (descriptor stability 0.90, but metric CV 1.51)
- **RB**: FRAGILE (descriptor stability 0.40, metric CV 1.63)
- **AM**: FRAGILE (descriptor stability 0.60, metric CV 1.63)
- **MHD**: ROBUST (but this is an artifact of data limitations)

### 4.2 MHD "Robustness" Is an Artifact

MHD shows ROBUST status because:
1. MHD has only 2 estimates (insufficient data)
2. Descriptor is always "insufficient_data"
3. Metrics are always 0

This is not genuine robustness—it's a data limitation artifact.

### 4.3 Metric Stability Is the Weak Point

All domains show high metric CV (>1.0) for:
- temporal_spread
- volatility

This means quantitative metrics are not stable under aggressive perturbation.

### 4.4 Descriptor Stability Varies

- GS: 0.90 (HIGH) — descriptor remains stable under most perturbations
- RB: 0.40 (LOW) — descriptor changes frequently
- AM: 0.60 (MEDIUM) — descriptor is moderately stable

## 5. Key Findings

1. **Most temporal signatures are fragile under aggressive protocol perturbation.** This is a scientifically valuable finding.

2. **MHD "robustness" is an artifact of data limitations.** It does not represent genuine signature stability.

3. **Metric stability is the weak point.** Quantitative metrics are not stable under aggressive perturbation.

4. **Descriptor stability varies across domains.** GS is more stable than RB or AM.

## 6. Implications

1. **P9 signatures should be treated as provisional, not stable.** The program must be more conservative about signature claims.

2. **Signature stability itself is a measurable property.** Some signatures are more robust than others.

3. **The program should not proceed with signature-based comparison until signatures are more robust.** This is the appropriate conservative response.

4. **The warning system is working.** P10 identified a fragility that was not apparent in P9.

## 7. Limitations

1. **Perturbation choice:** Different perturbations may give different results.

2. **Threshold choice:** Admissibility thresholds (80%, 0.2, 90%) are arbitrary.

3. **Small sample:** Few trajectories per domain may limit stability estimates.

4. **Observer bias:** Same researcher conducts all analyses.

## 8. Next Steps

1. **Revise signature definitions** to improve robustness.

2. **Test signature stability with more trajectories** to improve estimates.

3. **Consider alternative signature metrics** that may be more robust.

4. **Do not proceed with signature-based comparison** until signatures are more robust.

## 9. Provenance

- **Audit:** P10
- **Date:** 2026-06-17
- **Script:** `audits/rd_p10_signature_robustness/run_p10_analysis.py`
- **Results:** `audits/rd_p10_signature_robustness/p10_results.json`
- **Status:** PROVISIONALLY ACCEPTED
