# Functional Form Competition

**Question**: Is the interaction model winning because it is correct, or because it is the first nonlinear model tested?

---

## Models Compared

| # | Model | Predictors | k | Description |
|---|-------|-----------|:-:|-------------|
| 1 | Null | — | 1 | Mean only |
| 2 | Friction (linear) | friction | 2 | Baseline |
| 3 | C (linear) | pre_C | 2 | Baseline |
| 4 | Additive (C+Fr) | C, friction | 3 | Two-factor, no interaction |
| 5 | **Interaction (C+Fr+C×Fr)** | C, friction, C×friction | 4 | Current best |
| 6 | Quadratic friction (Fr+Fr²) | friction, friction² | 3 | Nonlinear friction only |
| 7 | Quadratic C (C+C²) | C, C² | 3 | Nonlinear C only |
| 8 | Both quadratic (C+C²+Fr+Fr²) | C, C², friction, friction² | 5 | Full quadratic |
| 9 | C + Fr + Fr² | C, friction, friction² | 4 | Interaction alternative |
| 10 | C + Fr + C² | C, friction, C² | 4 | Alternative curvature |
| 11 | Threshold (best) | C, dummy, C×dummy | 4 | Piecewise |
| 12 | Decision tree (depth 2) | C, friction | — | Nonparametric |
| 13 | Decision tree (depth 3) | C, friction | — | Deeper tree |

---

## 1. Full-Sample Comparison

### ΔC (dip depth)

| Rank | Model | R² | AIC | BIC | ΔR² vs Additive |
|:----:|-------|:---:|:---:|:---:|:---------------:|
| 1 | Decision tree (d=3) | 0.593 | — | — | +0.165* |
| 2 | Both quadratic | 0.537 | 134.1 | 144.6 | +0.109 |
| 3 | C + Fr + Fr² | 0.531 | 132.8 | 141.2 | +0.103 |
| 4 | **Interaction** | **0.523** | **133.9** | **142.3** | **+0.094** |
| 5 | C + Fr + C² | 0.493 | 137.5 | 145.9 | +0.064 |
| 6 | Decision tree (d=2) | 0.452 | — | — | +0.024* |
| 7 | Additive | 0.428 | 142.7 | 149.0 | — |
| 8 | Threshold=0.40 | 0.413 | 146.3 | 154.7 | −0.015 |
| 9 | Quad friction | 0.334 | 151.9 | 158.2 | −0.094 |
| 10 | Friction (linear) | 0.299 | 153.0 | 157.1 | −0.129 |
| 11 | Quad C | 0.195 | 163.2 | 169.5 | −0.233 |
| 12 | C (linear) | 0.105 | 167.6 | 171.8 | −0.323 |
| 13 | Null | 0.000 | — | — | −0.428 |

*Decision trees are not regularized; high R² reflects training-set memorization.

### Restoration

| Rank | Model | R² | AIC | BIC | ΔR² vs Additive |
|:----:|-------|:---:|:---:|:---:|:---------------:|
| 1 | Both quadratic | 0.578 | 128.5 | 139.0 | +0.078 |
| 2 | C + Fr + Fr² | 0.572 | 127.4 | 135.8 | +0.071 |
| 3 | Decision tree (d=3) | 0.547 | — | — | +0.046* |
| 4 | **Interaction** | **0.565** | **128.4** | **136.7** | **+0.064** |
| 5 | C + Fr + C² | 0.551 | 130.2 | 138.6 | +0.051 |
| 6 | Additive | 0.500 | 134.6 | 140.9 | — |
| 7 | Decision tree (d=2) | 0.391 | — | — | −0.109* |
| 8 | Threshold=0.20 | 0.346 | 152.8 | 161.2 | −0.154 |
| 9 | Quad friction | 0.236 | 160.1 | 166.4 | −0.264 |
| 10 | Friction (linear) | 0.229 | 158.7 | 162.9 | −0.271 |
| 11 | Quad C | 0.115 | 169.0 | 175.2 | −0.385 |
| 12 | C (linear) | 0.036 | 172.1 | 176.3 | −0.464 |
| 13 | Null | 0.000 | — | — | −0.500 |

### τ_rec (recovery time)

| Rank | Model | R² | AIC | BIC | ΔR² vs Additive |
|:----:|-------|:---:|:---:|:---:|:---------------:|
| 1 | Decision tree (d=3) | 0.651 | — | — | +0.345* |
| 2 | Decision tree (d=2) | 0.470 | — | — | +0.165* |
| 3 | **Interaction** | **0.345** | **152.9** | **161.3** | **+0.040** |
| 4 | Threshold=0.40 | 0.340 | 153.3 | 161.7 | +0.035 |
| 5 | Both quadratic | 0.338 | 155.5 | 166.0 | +0.033 |
| 6 | C + Fr + C² | 0.338 | 153.5 | 161.9 | +0.033 |
| 7 | C + Fr + Fr² | 0.318 | 155.3 | 163.7 | +0.013 |
| 8 | Additive | 0.305 | 154.4 | 160.7 | — |
| 9 | Quad friction | 0.179 | 164.4 | 170.7 | −0.126 |
| 10 | Friction (linear) | 0.179 | 162.4 | 166.6 | −0.126 |
| 11 | Quad C | 0.096 | 170.2 | 176.5 | −0.209 |
| 12 | C (linear) | 0.046 | 171.4 | 175.6 | −0.259 |
| 13 | Null | 0.000 | — | — | −0.305 |

---

## 2. Key Comparisons

### Interaction vs C + Fr + Fr²

This is the most important comparison. If the interaction (C×Fr) can be entirely replaced by friction², then the interaction is a nonlinear friction artifact.

| Target | Interaction R² | C+Fr+Fr² R² | ΔR² | Winner |
|--------|:-------------:|:-----------:|:---:|:------:|
| ΔC | 0.523 | 0.531 | **−0.009** | C+Fr+Fr² (negligible) |
| Restoration | 0.565 | 0.572 | **−0.007** | C+Fr+Fr² (negligible) |
| τ_rec | 0.345 | 0.318 | **+0.027** | Interaction |

**Verdict**: C+Fr+Fr² marginally beats interaction for ΔC and restoration, but the differences are tiny (ΔR² < 0.01). The models are essentially tied — they capture the same nonlinear structure in different parameterizations. Crucially, **both include C**. The nonlinearity could be friction² or C×friction — neither model eliminates C.

### Interaction vs Both Quadratic (C+C²+Fr+Fr²)

The fully quadratic model has 5 parameters vs 4 for interaction.

| Target | Interaction R² | Both Quad R² | ΔR² | AIC Winner |
|--------|:-------------:|:-----------:|:---:|:----------:|
| ΔC | 0.523 | 0.537 | −0.014 | Interaction (133.9 vs 134.1) |
| Restoration | 0.565 | 0.578 | −0.013 | Interaction (128.4 vs 128.5) |
| τ_rec | 0.345 | 0.338 | +0.007 | Interaction (152.9 vs 155.5) |

**Verdict**: Both quadratic has marginally higher R² but worse AIC for all targets (penalized for extra parameter). The interaction model is more parsimonious.

### Interaction vs Decision Trees

Decision trees (depth 3) achieve the highest R² for all targets (0.593, 0.547, 0.651). However, these are **overfit** — depth 3 with 60 points means ~8 observations per leaf. No cross-validation was applied. The comparison is informative only to show that nonlinear structure exists beyond what linear models capture.

---

## 3. Summary

**Is Model C winning because it's correct, or because it's the first nonlinear model tested?**

**Answer**: Partially both.

- The interaction model does **not** uniquely dominate all alternatives. C+Fr+Fr² and both-quadratic match or slightly exceed its R² for ΔC and restoration.
- But crucially, every competitive model still includes **C** as a predictor. No friction-only nonlinear model (friction + friction²) exceeds R² = 0.334 (ΔC) or 0.236 (restoration). The best nonlinear model without C is the quadratic friction model, which is substantially worse than any model that includes C.
- This means the nonlinear structure requires **both C and friction** — whether parameterized as C×friction or friction² + C.

**Bottom line**: The interaction is not winning only because it is the first nonlinear model tested. Every nonlinear extension that removes C (quadratic friction alone) performs poorly. Every model that includes C (interaction, C+Fr+Fr², both quadratic) performs similarly well. The nonlinearity matters, but C remains an indispensable predictor regardless of functional form.
