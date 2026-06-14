# RD-7A: Cross-Domain Novelty Audit — Results

## Primary Question

**Is C an independent observable, or merely a nonlinear remix of existing measures?**

---

## Answer

**Within the granular domain, C is ~80% reconstructable from MSE alone.** Cross-domain, we cannot tell — the dataset is too small (n=8) for reliable conclusions.

---

## Results

### 1. Cross-Domain (8 systems: S1–S6 + P1 + P2)

| Metric | Value |
|--------|-------|
| **R²** | **0.437** |
| **Adjusted R²** | −0.313 |
| **LOO-CV R²** | **−17.179** |
| LOO-CV RMSE | 1.183 |

The in-sample R² of 0.44 suggests partial reconstruction, but the LOO-R² of −17.18 reveals **catastrophic overfitting**. With 8 data points and 4 predictors, the model has almost no degrees of freedom.

**Per-system LOO errors:**

| System | Actual C | LOO Predicted | |Error| |
|--------|----------|---------------|---------|
| S1 (independent) | 0.004 | 1.377 | **1.373** |
| S2 (fully coupled) | 0.811 | 0.116 | **0.696** |
| S3 (coupled Markov) | 0.261 | 0.665 | 0.404 |
| S4 (modular) | 0.141 | 0.354 | 0.214 |
| S5 (sandpile) | 0.130 | −0.556 | **0.685** |
| S6 (hierarchical) | 0.204 | 0.294 | 0.090 |
| P1 (forest) | 0.685 | 0.756 | 0.071 |
| P2 (granular) | 0.573 | −2.279 | **2.852** |

S1, S2, S5, and P2 have LOO errors > 0.5. The model **fails catastrophically** when leaving out systems it hasn't seen.

**Best univariate predictor:** C_σ alone achieves R² = 0.361, LOO-R² = 0.055 (barely above zero).

### 2. Within-Domain (60 granular runs, t901)

| Metric | Value |
|--------|-------|
| **R²** | **0.808** |
| **Adjusted R²** | 0.797 |
| **LOO-CV R²** | **0.761** |
| LOO-CV RMSE | 0.027 |
| Shapiro-Wilk (residuals) | W = 0.981, p = 0.456 (normal) |

Within the granular domain, **C is 80% reconstructable** from I_pred + C_σ + MSE. The LOO-R² of 0.76 confirms this is not overfitting.

**The dominant relationship:** C ≈ −MSE (r = −0.892). MSE alone explains 80% of C's variance within this domain.

**Partial R² (unique contributions):**

| Metric | Unique R² | % of explained |
|--------|-----------|----------------|
| MSE | **0.596** | **73.8%** |
| C_σ | 0.058 | 7.1% |
| I_pred | 0.002 | 0.2% |

MSE is doing almost all the work. I_pred and C_σ add negligible unique information.

### 3. Residual Analysis (within-domain)

| Friction | Mean Residual | Std |
|----------|--------------|-----|
| μ = 0.05 | +0.019 | 0.015 |
| μ = 0.10 | +0.005 | 0.013 |
| μ = 0.20 | +0.002 | 0.010 |
| μ = 0.40 | −0.007 | 0.027 |
| μ = 0.60 | −0.005 | 0.034 |
| μ = 0.80 | −0.015 | 0.023 |

Residuals are small (mean < 0.02) and normally distributed. There is a slight friction-dependent bias: the model overpredicts C at low friction and underpredicts at high friction. This suggests a nonlinear interaction between friction and the metrics that the linear model doesn't capture.

---

## Verdict

| Domain | R² | LOO-R² | Reconstruction? |
|--------|-----|--------|----------------|
| Cross-domain (8 systems) | 0.437 | **−17.179** | **UNDETERMINED** (overfitting) |
| Within-domain (60 runs) | 0.808 | **0.761** | **YES** (80% reconstructable) |

### What this means:

1. **Within the granular domain, C is not independent.** It is ~80% reconstructable from MSE (r = −0.89). The "total correlation" measure is largely capturing the same information as multiscale entropy, just inverted.

2. **Cross-domain, we cannot determine independence.** With only 8 systems and 4 predictors, any regression is hopelessly overfit. We would need ~40+ diverse systems to make a reliable cross-domain statement.

3. **C's theoretical status is weakened but not eliminated.** Within granular systems, C is a remix of MSE. Whether it captures something genuinely new across diverse physical systems (ecosystems, neural networks, social systems) remains an open question that this dataset cannot answer.

4. **The pillar status:** The theory pillar that "C is an independent observable" is **undermined within the granular domain** but **untested cross-domain**. The honest position is that C is probably not independent, but we lack the data to prove it definitively.

---

## What Would Settle This

To definitively answer "Is C independent?", we need:

1. **40+ diverse systems** spanning different physical substrates (biological, physical, social, computational)
2. **Nonlinear reconstruction** (kernel regression, neural network) to test if C is a nonlinear remix
3. **Information-theoretic decomposition** (partial information decomposition) to quantify unique, redundant, and synergistic information

---

## Deliverables

- `audits/RD07A_CROSS_DOMAIN_NOVELTY.md` — this report
- `audits/rd07a_novelty_audit.json` — statistical results
- `audits/rd07a_fig1_actual_vs_predicted.png` — actual vs predicted (both domains)
- `audits/rd07a_fig2_residuals.png` — residual analysis
- `audits/rd07a_fig3_loo_comparison.png` — LOO-CV comparison
- `audits/rd07a_fig4_c_vs_mse.png` — C vs MSE scatter (the dominant relationship)
