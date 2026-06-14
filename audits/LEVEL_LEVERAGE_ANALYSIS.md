# Level Leverage Analysis: Are interaction results driven by individual friction levels?

**Audit ID**: RD-016-P3
**Date**: 2026-06-05
**Question**: Leave-one-friction-level-out and remove-extremes sensitivity analysis. Does the C×friction interaction survive when individual friction levels are held out, especially the extreme levels (0.05, 0.80)?

## Method

For each of the 6 friction levels (0.05, 0.10, 0.20, 0.40, 0.60, 0.80; 10 replicates each):
1. Hold out all 10 runs at that level
2. Fit C+Fr+C×Fr model on remaining 50 runs
3. Compare R², interaction coefficient, p-value with full-model (n=60) estimates

Also: remove both extremes (friction 0.05 and 0.80) and re-fit.

## Results

### Target: ΔC (dip depth)

| Left Out | N | Full R² | LO R² | ΔR² | Int Coef | p(Int) | Significant? |
|----------|---|---------|-------|------|----------|--------|-------------|
| (all) | 60 | 0.523 | 0.523 | — | +0.390 | 0.002 | **Yes** |
| 0.05 | 50 | 0.523 | 0.483 | −0.039 | +0.438 | 0.008 | **Yes** |
| 0.10 | 50 | 0.523 | 0.510 | −0.013 | +0.394 | 0.003 | **Yes** |
| 0.20 | 50 | 0.523 | 0.556 | +0.033 | +0.417 | 0.002 | **Yes** |
| 0.40 | 50 | 0.523 | 0.555 | +0.032 | +0.395 | 0.004 | **Yes** |
| 0.60 | 50 | 0.523 | 0.533 | +0.011 | +0.343 | 0.003 | **Yes** |
| **0.80** | 50 | 0.523 | 0.518 | −0.005 | **+0.274** | **0.143** | **No** |
| **0.05+0.80** | 40 | 0.523 | **0.484** | −0.039 | **+0.306** | **0.253** | **No** |

### Target: Restoration

| Left Out | N | Full R² | LO R² | ΔR² | Int Coef | p(Int) | Significant? |
|----------|---|---------|-------|------|----------|--------|-------------|
| (all) | 60 | 0.565 | 0.565 | — | −0.322 | 0.006 | **Yes** |
| **0.05** | 50 | 0.565 | 0.549 | −0.016 | **−0.289** | **0.060** | **No** |
| 0.10 | 50 | 0.565 | 0.559 | −0.006 | −0.367 | 0.002 | **Yes** |
| 0.20 | 50 | 0.565 | 0.580 | +0.015 | −0.313 | 0.016 | **Yes** |
| 0.40 | 50 | 0.565 | 0.580 | +0.015 | −0.279 | 0.034 | **Yes** |
| 0.60 | 50 | 0.565 | 0.636 | +0.071 | −0.358 | 0.002 | **Yes** |
| **0.80** | 50 | 0.565 | **0.445** | **−0.120** | **−0.225** | **0.203** | **No** |
| **0.05+0.80** | 40 | 0.565 | **0.437** | **−0.128** | **−0.112** | **0.652** | **No** |

### Target: τ_rec (recovery time)

| Left Out | N | Full R² | LO R² | ΔR² | Int Coef | p(Int) | Significant? |
|----------|---|---------|-------|------|----------|--------|-------------|
| (all) | 60 | 0.345 | 0.345 | — | +0.253 | 0.071 | No |
| 0.05 | 50 | 0.345 | 0.332 | −0.013 | +0.316 | 0.098 | No |
| 0.10 | 50 | 0.345 | 0.335 | −0.010 | +0.229 | 0.145 | No |
| 0.20 | 50 | 0.345 | 0.340 | −0.005 | +0.274 | 0.091 | No |
| **0.40** | 50 | 0.345 | 0.385 | +0.040 | **+0.346** | **0.034** | **Yes** |
| 0.60 | 50 | 0.345 | 0.434 | +0.089 | +0.213 | 0.061 | No |
| 0.80 | 50 | 0.345 | 0.255 | −0.090 | +0.101 | 0.621 | No |
| 0.05+0.80 | 40 | 0.345 | 0.244 | −0.101 | +0.152 | 0.611 | No |

### Coefficient sensitivity (ΔC model)

| Removed Level | Δ Int Coef | Δ C Coef | Δ Fr Coef | Δ R² |
|---------------|-----------|----------|-----------|------|
| 0.05 | +0.047 | −0.046 | +0.009 | −0.039 |
| 0.10 | +0.004 | −0.020 | −0.026 | −0.013 |
| 0.20 | +0.026 | −0.005 | −0.019 | +0.033 |
| 0.40 | +0.005 | −0.119 | −0.104 | +0.032 |
| 0.60 | −0.048 | +0.055 | −0.045 | +0.011 |
| **0.80** | **−0.117** | **+0.299** | **+0.493** | −0.005 |

The interaction coefficient drops from +0.390 (full) to +0.274 when friction=0.80 is removed — a 30% decrease. The C and friction coefficients shift dramatically (+0.30 and +0.49 respectively), showing that friction=0.80 level exerts outsized influence on the model.

## Interpretation

### CRITICAL: The interaction is endpoint-driven

For both ΔC and restoration, the C×friction interaction becomes **non-significant** when either:
1. **Only friction=0.80 is removed** (ΔC p=0.14, restoration p=0.20)
2. **Both extremes (0.05 + 0.80) are removed** (ΔC p=0.25, restoration p=0.65)

The interaction coef magnitude drops 30–65% when extremes are excluded. For restoration, removing extremes collapses R² from 0.565 to 0.437 (−23%) and the interaction coefficient changes by −65%.

This means the interaction model's significance is entirely dependent on the contrast between:
- **low friction** (0.05–0.10): high C, recovery is primarily friction-limited
- **high friction** (0.80): low C, recovery is primarily C-limited

Without these anchors, the model cannot distinguish interaction from noise.

### Friction=0.80 is the most influential level

- Largest coefficient changes when removed (Δ Int = −0.117, Δ C = +0.299, Δ Fr = +0.493)
- Largest single-level R² drop for restoration (−0.120)
- The interaction p-value crosses significance threshold only when this level is included

### The interaction was never really about interaction

The original finding (Model D beats additive) appeared consistent with a genuine C×mobility cross-over. But:
1. P1 shows Fr² curvature captures the same variance — no interaction needed
2. P3 shows the interaction is not robust to endpoint removal

Together, these suggest the interaction was a statistical artifact of:
- Nonlinear friction→recovery relationship (diminishing returns at high friction) masquerading as an interaction
- The high friction level (0.80) having both low C and distinct recovery behavior

## Robustness summary

| Test | ΔC | Restoration | τ_rec |
|------|-----|------------|-------|
| Full model (n=60) | 0.002** | 0.006** | 0.071 |
| Remove 0.05 | 0.008** | 0.060 | 0.098 |
| Remove 0.10 | 0.003** | 0.002** | 0.145 |
| Remove 0.20 | 0.002** | 0.016* | 0.091 |
| Remove 0.40 | 0.004** | 0.034* | 0.034* |
| Remove 0.60 | 0.003** | 0.002** | 0.061 |
| Remove 0.80 | **0.143** | **0.203** | 0.621 |
| Remove 0.05+0.80 | **0.253** | **0.652** | 0.611 |

**Bold** = loses significance (p > 0.05). 
The interaction is only significant when both extremes (especially 0.80) are included.

## Conclusion

The C×friction interaction is **not robust**. It depends entirely on the extreme friction levels, particularly the highest level (0.80). When these levels are removed, the interaction collapses quantitatively (coefficient magnitude drops 30–65%) and statistically (p > 0.25 for all targets).

This, combined with the P1 finding that Fr² curvature captures the same variance, strongly suggests the interaction was a **statistical artifact** — a nonlinear friction→recovery relationship masquerading as a coherence×mobility cross-over.
