# Validation Status

## Perturbation Detection

| Test | Result | Status |
|------|--------|--------|
| Granular DEM (T920) | SNR = 2.14 | ✅ |
| Granular DEM (I_pred) | SNR = 0.18 | ✅ C outperforms |
| Granular DEM (C_sigma) | SNR = 0.0 | ✅ C outperforms |
| Granular DEM (MSE) | SNR = −0.80 | ✅ C outperforms |
| Forest succession (T920) | Dip at drought onset | ✅ |
| Null model (shuffled) | No dip | ✅ |

**Conclusion**: C detects perturbations that standard metrics miss or misidentify.

## Structure Discrimination

| Test | Result | Status |
|------|--------|--------|
| 8 testbed systems | C discriminates structured vs unstructured | ✅ |
| Null universes | C ≈ 0 for independent components | ✅ |

**Conclusion**: C cleanly separates structured from unstructured systems.

## Reconstruction (IF-3)

| Test | Result | Status |
|------|--------|--------|
| 90% missing interactions | Structure recovered | ✅ |
| 10× noise injection | Structure recovered | ✅ |
| No interaction structure | Fails gracefully | ✅ |

## Resilience Prediction

| Test | Result | Status |
|------|--------|--------|
| C alone predicts ΔC | R² = 0.10 | ⚠️ Weak |
| C + friction predicts ΔC | R² = 0.52 | ✅ |
| C alone predicts τ_rec | R² = 0.05 | ❌ |
| C + friction predicts τ_rec | R² = 0.35 | ✅ |
| C alone predicts restoration | R² = 0.04 | ❌ |
| C + friction predicts restoration | R² = 0.56 | ✅ |
| High C + poor recovery exists | No | ❌ Fails to falsify |
| Low C + strong recovery exists | Yes (5/60 runs) | ✅ |
| Same C + opposite ΔC sign | Yes | ✅ |

**Conclusion**: C alone is insufficient to predict recovery. Two-factor model (C × mobility) is supported.

## Reproducibility

- Results stable across 10 replicates per condition
- Results robust to ±25% window size variation
- Results robust to ±50% bin count variation
- Results robust to Gaussian vs. Epanechnikov kernel

## Key Limitation

C and friction (mobility) are partially collinear (r ≈ −0.74 in the granular ensemble). The independent contributions of each cannot be fully separated without a dedicated decoupling experiment.
