# Coherence Metric

## Purpose

Quantify the degree to which a multivariate time series is dominated by joint (inter-system) structure versus component-level (independent) variation.

## Definition

Coherence C is the fraction of total system entropy attributable to interaction structure:

\[
C = \frac{T}{T + \sum_i H_i}
\]

- \(T\) = total correlation (multivariate mutual information)
- \(H_i\) = marginal entropy of component \(i\)

## Interpretation

| C range | Interpretation |
|---------|---------------|
| C ≈ 1   | Nearly all variance is joint structure; system is highly coordinated |
| C ≈ 0.5 | Joint structure and independent variation contribute equally |
| C ≈ 0   | Components are nearly independent; no detectable interaction structure |

## Computation

1. **Binning** (if raw data has high dimensionality): Group components by spatial or functional proximity, average within bins. Reduces dimensionality while preserving interaction structure.
2. **Entropy estimation**: Gaussian kernel density estimation with Scott's rule for bandwidth selection.
3. **Total correlation**: Sum of marginal entropies minus joint entropy.
4. **Normalization**: C = T / (T + sum(H_i)). Division by zero prevented by minimum entropy floor (1e-10).

## Dependencies

- `scipy.stats.gaussian_kde` for density estimation
- `numpy` for linear algebra
- No machine learning dependencies

## Scope

Tested on:
- Granular DEM (50 grains, 1000 timesteps, 10 bins)
- Forest succession (20–50 plots, 500 timesteps, 10–20 bins)
- Neural recordings (synthetic and real, 10–100 channels)
- Opinion dynamics (50 agents, 500 timesteps)
- Known failure modes: see `limitations.md`
