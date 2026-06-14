# Residual(C) Mechanism Audit: What does the friction-independent component of C capture?

**Audit ID**: RD-016-P2
**Date**: 2026-06-05
**Question**: After regressing out friction (C ~ friction), the residual(C) carries C's unique predictive signal. What physical or statistical mechanisms does residual(C) correspond to? Is it reducible to other measured variables?

## Background

From RD-015: C and friction share R² = 0.793 (r ≈ −0.89). Residual(C) = C − E[C | friction] is the component of coherence that varies independently of friction. This component predicts recovery 1.2–7.6× better than raw C, suggesting the friction-correlated part of C is anti-predictive noise.

Here we test whether residual(C) can be explained by four mobility/structural descriptors: MSD, RMS velocity, neighbor turnover, and packing variance.

## Method

1. Pearson and Spearman correlations: residual(C) vs each descriptor
2. Partial R²: does residual(C) predict recovery beyond all four mobility variables?

All variables Z-scored. n = 60.

## Results

### Correlation: residual(C) vs mobility descriptors

| Variable | Pearson r | p-value | Spearman ρ | Interpretation |
|----------|-----------|---------|------------|----------------|
| MSD | −0.153 | 0.245 | −0.197 | Weak, n.s. |
| RMS velocity | −0.141 | 0.283 | −0.100 | Weak, n.s. |
| Neighbor turnover | −0.010 | 0.942 | −0.014 | No relationship |
| **Packing variance** | **+0.264** | **0.041** | **+0.281** | **Weak, nominally significant** |

For reference: residual(C) vs raw C: r = +0.455 (by construction, ~√(1 − R²(C~Fr)) = √0.207 ≈ 0.455).

**Interpretation**: Residual(C) is largely orthogonal to all measured mobility descriptors. The max |r| is 0.26 (packing variance), explaining only ~7% of residual(C) variance. This means:

> Residual(C) captures something not measured by standard mobility/structural statistics.

This strengthens the claim that C contains unique information. The friction-independent component of C is not reducible to MSD, RMS velocity, turnover, or packing.

### Partial: residual(C) predictive power beyond mobility

| Target | residual(C) alone R² | Mobility only R² | Mobility + res(C) R² | **ΔR²(res\|mob)** |
|--------|---------------------|------------------|----------------------|-------------------|
| ΔC | 0.129 | 0.333 | 0.438 | **+0.105** |
| Restoration | 0.271 | 0.170 | 0.414 | **+0.244** |
| τ_rec | 0.126 | 0.186 | 0.335 | **+0.150** |

For all three targets, residual(C) adds substantial predictive power beyond the four mobility variables:
- Restoration: ΔR² = +0.244 — residual(C) more than doubles the explained variance
- τ_rec: ΔR² = +0.150 — residual(C) adds 80% to mobility-only R²
- ΔC: ΔR² = +0.105 — residual(C) adds 31% to mobility-only R²

## Interpretation

1. **Residual(C) is not mobility in disguise**. The maximum shared variance with any mobility descriptor is ~7% (packing variance). The friction-independent component of C is a genuinely different quantity.

2. **Residual(C) carries strong predictive signal**. After controlling for all four mobility variables, residual(C) adds ΔR² = 0.10–0.24 across targets. For restoration, it's the single strongest predictor.

3. **What IS residual(C)?** The fact that it correlates weakly with packing variance (r = +0.26, p = 0.04) suggests a connection to structural heterogeneity — systems with higher residual(C) at a given friction level tend to have more variable packing. This is physically plausible: for the same friction coefficient, grains may arrange differently, and C captures that structural variation.

4. **Amplification of RD-015 finding**: residual(C)'s predictive superiority over raw C (1.2–7.6×) is not because it proxies some other measured quantity. It's genuinely capturing friction-independent structural information that mobility statistics miss.

## Threats to validity

| Threat | Assessment |
|--------|-----------|
| **Omitted variable** | Residual(C) may correlate with an unmeasured variable (e.g., grain shape, size distribution, preparation history) |
| **Level-specific artifact** | Residual(C) variance is mostly within friction levels. If certain levels have unusual recovery properties, the correlation may be spurious (see P3) |
| **Nonlinear relationships** | Only linear correlations tested. Residual(C) may have nonlinear relationships with mobility variables |
| **Measurement noise** | MSD and packing variance are computed from the same trajectories as C, but at different temporal resolutions |

## Conclusion

Residual(C) is a genuine, non-redundant predictor of recovery. It captures structure-related variance that mobility descriptors miss. This supports the proposition that coherence measures something real and useful about system organization beyond what standard dynamical statistics capture.
