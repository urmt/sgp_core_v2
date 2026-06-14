# Limitations

## Known

### 1. Small-sample bias

Entropy estimates from Gaussian KDE are biased downward for small samples (< 500 timepoints per component). Coherence may be overestimated in the small-sample regime.

**Mitigation**: Verified robustness at 250+ timepoints (current datasets: 500–2000 timepoints).

### 2. Dimensionality sensitivity

KDE quality degrades as dimensionality increases. Current implementation bins raw data to 10–20 components before entropy computation, which loses spatial resolution but maintains estimate quality.

**Mitigation**: Binning parameter tested across 5–20 bins; C ranking is preserved.

### 3. Gaussian kernel assumption

Coherence uses a Gaussian kernel for density estimation. If the true data distribution is multimodal or heavy-tailed, entropy estimates may be biased.

**Mitigation**: Tested against Epanechnikov kernel; results are rank-correlated at r > 0.95.

### 4. Normalization edge case

When joint differential entropy is negative (which occurs for peaked distributions where density concentrates in a small volume), C can become > 1. Normalization fix: C = T / (T + sum(H_i)) prevents this.

### 5. Stationarity requirement

Coherence assumes that interaction structure is stationary within each sliding window. Rapidly non-stationary systems may show artifacts.

**Mitigation**: Window size ≤ 75 timepoints; perturbation events are localized in time.

### 6. Not a causal metric

Coherence measures statistical dependence, not causal structure. Two systems with identical C may have entirely different causal architectures (common driver vs. reciprocal coupling).

### 7. Collinearity with friction (granular only)

In the granular DEM, friction controls both C and mobility, creating partial collinearity (r ≈ −0.74). This limits causal attribution in the current ensemble.

## Suspected

### 8. System-size sensitivity

Coherence values may depend on the number of components n. Systems with more components may show different C ranges than systems with fewer, even with equivalent interaction topology.

### 9. Recovery metric coupling

ΔC and τ_rec are not independent — systems with large dips may take longer to recover, creating apparent correlation that is measurement artifact rather than system property.

## Not Applicable

### 10. Coherence as complexity

C is NOT a measure of complexity. It measures coordination, which can be high in both simple (synchronized pendulum) and complex (flocking birds) systems. Do not interpret C as complexity.
