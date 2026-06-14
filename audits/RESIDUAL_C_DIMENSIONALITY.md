# Residual(C) Dimensionality: Single factor or multiple weak signals?

**Audit ID**: RD-017-D2
**Date**: 2026-06-05
**Question**: Is Residual(C) a single latent factor or a mixture of multiple weak signals?

## Method

Principal Component Analysis (PCA) on all 22 structural descriptors (n=60, p=22, standardized). Plus Partial Least Squares (PLS) regression to predict Residual(C) from structural descriptors.

## Results

### PCA: Structural descriptor space

| Component | Eigenvalue | Variance % | Cumulative % |
|-----------|-----------|------------|-------------|
| PC1 | 11.31 | **53.0%** | 53.0% |
| PC2 | 3.84 | 18.0% | 70.9% |
| PC3 | 1.66 | 7.8% | 78.7% |
| PC4 | 1.33 | 6.2% | 85.0% |
| PC5 | 0.91 | 4.3% | 89.2% |
| PC6 | 0.68 | 3.2% | 92.4% |
| PC7 | 0.56 | 2.6% | 95.0% |
| PC8 | 0.28 | 1.3% | 96.3% |
| PC9 | 0.25 | 1.2% | 97.5% |
| PC10 | 0.16 | 0.8% | 98.3% |

### Key metrics

| Metric | Value |
|--------|-------|
| **PC1 variance explained** | **53.0%** |
| PC2 variance explained | 18.0% |
| PC1 / PC2 ratio | **2.95** |
| PCs needed for 80% variance | **4** |
| PC1 vs Residual(C) correlation | r = **−0.298** (p = 0.021) |

### PC1 loadings (top 10)

| Variable | Loading | Category |
|----------|---------|----------|
| g_r_second_peak | +0.285 | Structural |
| mean_overlap | +0.267 | Force |
| g_r_peak_height | +0.264 | Structural |
| mean_coordination | +0.263 | Contact |
| mean_contact_count | +0.263 | Contact |
| contact_density | +0.263 | Contact |
| mean_nn_dist | **−0.260** | Spatial |
| contact_jaccard_mean | +0.259 | Temporal |
| overlap_cv | **−0.255** | Force |
| overlap_std | +0.253 | Force |

### PLS: Predicting Residual(C) from structure

| Component | Train R² | CV R² (5-fold) |
|-----------|---------|----------------|
| 3-component PLS | 0.405 | **−0.363 ± 0.338** |

PLS predicts Residual(C) from structural descriptors at R² = 0.405 in-sample, but **cross-validated R² is negative** (−0.363), indicating severe overfitting. The structural descriptors cannot reliably predict Residual(C) in held-out data.

## Interpretation

### Verdict: Single latent factor? **Borderline.**

On one hand:
- PC1 explains 53% of variance, PC1/PC2 ratio is 2.95 — this is consistent with a dominant underlying factor (the "packing density/connectivity" axis identified in D1).
- The tight range of top correlations (R² = 0.068–0.176) suggests a diffuse signal rather than distinct clusters.

On the other hand:
- 4 PCs are needed to reach 80% variance — a true single-factor structure would reach this with 1 or 2 components.
- PC1 explains only 53% — not the 60-80% typical of a truly dominant factor.
- PC1 itself correlates only weakly with Residual(C) (r = −0.30).

### But the structural descriptors do NOT capture Residual(C)

The critical finding is from PLS: even with 3 components (capturing ~79% of descriptor variance), the model cannot predict Residual(C) in cross-validation (CV R² < 0). This means:

> **The information in Residual(C) is not contained in the measured structural descriptors.**

This is surprising. Residual(C) correlates weakly with multiple structural variables (D1), but their shared variance cannot linearly combine to reconstruct Residual(C). This implies:

1. **Residual(C) captures a structural property we are not measuring with these 22 descriptors**, or
2. **The relationship between structure and Residual(C) is nonlinear**, or
3. **Residual(C)'s predictive signal is not structural in the granular-physics sense** — it might reflect a dynamical property (e.g., the shape of the C trajectory itself) rather than a static structural one.

### H1 vs H2 evaluation

| Hypothesis | Evidence | Verdict |
|-----------|----------|---------|
| **H1: Single latent factor** | PC1=53%, PC1/PC2=2.95. Consistent with a dominant "packing density" dimension. | **Partially supported** — one dimension dominates structure space |
| **H2: Multiple weak signals** | 4 PCs needed for 80% variance. No single variable explains >18% of Residual(C). PLS fails in CV. | **Partially supported** — Residual(C) is not captured by linear combinations of descriptors |

**The structural descriptors themselves are single-factor-ish (53% shared by PC1), but Residual(C) is not aligned with this factor.** Residual(C) appears to be a distinct latent dimension that the current structural descriptors can only weakly approximate.

## Conclusion

**Verdict: Indeterminate (leaning multi-factor).**

The 22 structural descriptors share a dominant dimension ("packing density × connectivity"), but this dimension explains only ~9% of Residual(C) variance (r² = 0.089). The remaining 91% of Residual(C) is orthogonal to the entire measured structural space.

Residual(C) is not:
- A single well-known granular descriptor
- A simple linear combination of known descriptors
- A mobility proxy

It appears to be a **genuinely distinct latent state variable** that the current measurement suite does not capture. The most productive path forward is likely a new type of measurement — not a new combination of existing ones.
