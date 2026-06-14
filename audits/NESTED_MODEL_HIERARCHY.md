# Nested Model Hierarchy: Does C×friction interaction survive Fr² curvature?

**Audit ID**: RD-016-P1
**Date**: 2026-06-05
**Question**: After accounting for friction curvature (Fr²), does the C×friction interaction term still provide unique explanatory power for recovery?

## Approach

Six nested models were compared for all three targets (ΔC, restoration, τ_rec), ordered by increasing complexity:

| # | Model | Predictors | Rationally |
|---|-------|-----------|------------|
| 1 | C-only | C | Baseline coherence |
| 2 | Friction-only | Fr | Baseline mobility |
| 3 | Additive | C + Fr | Baseline two-factor |
| 4 | Fr² curvature | C + Fr + Fr² | Does friction curvature matter? |
| 5 | Interaction | C + Fr + C×Fr | Does interaction matter? |
| 6 | Combined | C + Fr + Fr² + C×Fr | Is interaction needed beyond curvature? |

Metrics: R², adjusted R², AIC, BIC, 5-fold CV R² (100 repeats). n = 60. All variables standardized.

## Results

### Target: ΔC (dip depth)

| Model | R² | Adj R² | AIC | BIC | CV R² |
|-------|-----|--------|-----|-----|-------|
| C-only | 0.105 | 0.089 | 167.6 | 171.8 | −0.085 |
| Friction-only | 0.299 | 0.287 | 153.0 | 157.1 | 0.109 |
| C + Fr | 0.428 | 0.408 | 142.7 | 149.0 | 0.216 |
| **C + Fr + Fr²** | **0.531** | **0.506** | **132.8** | **141.2** | **0.327** |
| C + Fr + C×Fr | 0.523 | 0.497 | 133.9 | 142.3 | 0.322 |
| C + Fr + Fr² + C×Fr | 0.538 | 0.504 | 133.9 | 144.4 | 0.312 |

Key comparisons:
- Fr² vs interaction: ΔR² = **+0.009** (Fr² wins)
- Full vs Fr²: ΔR² = **+0.007** (interaction adds almost nothing beyond Fr²)
- Full vs interaction: ΔR² = **+0.015** (Fr² adds more than interaction)

### Target: Restoration

| Model | R² | Adj R² | AIC | BIC | CV R² |
|-------|-----|--------|-----|-----|-------|
| C-only | 0.036 | 0.019 | 172.1 | 176.3 | −0.167 |
| Friction-only | 0.229 | 0.216 | 158.7 | 162.9 | −0.002 |
| C + Fr | 0.500 | 0.483 | 134.6 | 140.9 | 0.308 |
| **C + Fr + Fr²** | **0.572** | **0.549** | **127.4** | **135.8** | **0.373** |
| C + Fr + C×Fr | 0.565 | 0.541 | 128.4 | 136.7 | 0.364 |
| C + Fr + Fr² + C×Fr | 0.576 | 0.545 | 128.8 | 139.3 | 0.356 |

Key comparisons:
- Fr² vs interaction: ΔR² = **+0.007** (Fr² wins)
- Full vs Fr²: ΔR² = **+0.004** (interaction adds essentially nothing beyond Fr²)
- Full vs interaction: ΔR² = **+0.011** (Fr² adds more than interaction)

### Target: τ_rec (recovery time)

| Model | R² | Adj R² | AIC | BIC |
|-------|-----|--------|-----|-----|
| C-only | 0.046 | 0.030 | 171.4 | 175.6 |
| Friction-only | 0.179 | 0.165 | 162.4 | 166.6 |
| C + Fr | 0.305 | 0.281 | 154.4 | 160.7 |
| C + Fr + Fr² | 0.318 | 0.281 | 155.3 | 163.7 |
| **C + Fr + C×Fr** | **0.345** | **0.310** | **152.9** | **161.3** |
| C + Fr + Fr² + C×Fr | 0.352 | 0.304 | 154.3 | 164.8 |

Key comparisons:
- Fr² vs interaction: ΔR² = **−0.027** (interaction wins — reversal!)
- Full vs Fr²: ΔR² = **+0.034** (interaction adds beyond Fr² for τ_rec)
- Full vs interaction: ΔR² = **+0.007** (Fr² adds little beyond interaction)

## Interpretation

### For ΔC and restoration: Fr² wins decisively

The Fr² curvature model is the best single model for both primary targets:
- Lowest AIC/BIC of any model
- Highest CV R²
- Adding the interaction term on top of Fr² yields ΔR² ≤ 0.007 — negligible

This resolves the ambiguity from RD-015: the interaction model does not contain information beyond what Fr² curvature captures. The apparent interaction effect in Model D was actually capturing the nonlinear (quadratic) dependence of recovery on friction.

### For τ_rec: interaction may matter, but weakly

τ_rec is the only target where interaction beats Fr². However:
- τ_rec models are universally poor (max R² = 0.352)
- CV R² is erratic and unreliable (numerical overflow in sklearn CV scoring)
- The reversal is fragile and driven by endpoints (see P3)

### The functional form is curved, not crossed

The director's Model C (interaction) and Model D (thermometer with C threshold) implied fundamentally different mechanisms:
- Interaction: C has opposite effects at different friction levels (cross-over)
- Threshold: C matters only above/below a mobility threshold

The Fr² result suggests neither is correct in its original form. Instead:
- **Friction has a decelerating relationship with recovery**: the effect of increasing friction on recovery diminishes at high friction levels (diminishing returns)
- C still contributes additively within each friction level
- There is no evidence for a genuine C×friction cross-over once Fr² curvature is modeled

### Implications for model ranking

| Model | After RD-016 | Verdict |
|-------|-------------|---------|
| **A (C-only)** | R² = 0.04–0.10 | Falsified — insufficient alone |
| **B (Mobility-only)** | R² = 0.18–0.30 | Adequate but incomplete |
| **C (Interaction)** | **ΔR² ≈ 0 beyond Fr²** | **Weakened — not needed after quadratic** |
| **D (Thermometer / nonlinear)** | **Best overall (C+Fr+Fr²)** | **Strengthened — curvature captures the effect** |

The best model is **C + Fr + Fr²**: a combined model with additive C, linear friction, and quadratic friction curvature. The interaction term is unnecessary.

## Limitations

1. **n = 60**: with 6 predictors in the full model (C+Fr+Fr²+C×Fr), we have 10 observations per predictor — marginal for reliable inference
2. **CV R² for τ_rec**: numerically unstable, should not be trusted
3. **Partial F-test**: not computed due to low n/df ratio; ΔR² comparison is more appropriate here
4. **Only one nonlinear form tested**: Fr² is a specific curvature. Other nonlinear forms (log, inverse, spline) may perform differently
