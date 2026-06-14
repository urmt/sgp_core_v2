# RD-6: Ensemble Resilience Test — Results

## Experiment

200 independent granular realizations.
Fixed perturbation: 50% grain removal at step 500.
Measure: C_pre, C_min, ΔC, τ_rec, C_final/C_pre, collapse (C_final < 0.05).

---

## Summary Table

| Metric | Survived (n=170) | Collapsed (n=30) | Test | p |
|--------|-----------------|-------------------|------|---|
| C_pre | 0.4854 ± 0.0238 | 0.4882 ± 0.0219 | Welch's t = −0.631 | **0.532** |
| Collapse rate | — | 15.0% | — | — |

---

## Primary Question: Does pre-perturbation coherence predict resilience?

### **No.**

| Analysis | Result | Interpretation |
|----------|--------|----------------|
| AUC (ROC) | **0.473** [95% CI: 0.365–0.577] | Chance level (0.500) |
| Cohen's d | **−0.123** [95% CI: −0.502–0.253] | Negligible effect |
| Rank-biserial r | **−0.027** | Negligible association |
| Logistic regression β | 3.009 ± 7.479, p = **0.688** | Not significant |
| Welch's t (C_pre) | −0.631, p = **0.532** | Not significant |

C_pre distributions for survivors and collapsed are **indistinguishable** (mean 0.485 vs 0.488).

---

## Detailed Results

### 1. C_pre does NOT predict collapse

The ROC-AUC is 0.473, which is at chance level. C_pre has zero discriminative ability for predicting which systems collapse under 50% removal.

The logistic regression confirms this: the slope (β = 3.009) is not significantly different from zero (p = 0.688). The predicted collapse probability is essentially flat across the C_pre range:

| C_pre | P(Collapse) |
|-------|-------------|
| 0.30 | 0.123 |
| 0.50 | 0.204 |
| 0.70 | 0.319 |

While there is a slight positive trend (higher C_pre → slightly higher collapse probability), the confidence interval includes zero and the effect is negligible (Cohen's d = −0.123).

### 2. C_pre DOES predict C_final/C_pre (ceiling effect)

Among survivors, C_pre is negatively correlated with C_final/C_pre:

- **Pearson r = −0.555, p < 0.0001**
- **Spearman ρ = −0.558, p < 0.0001**

This is a ceiling effect: systems starting with higher C have less room to overshoot, so their C_final/C_pre ratio is lower. This does not indicate better or worse recovery — it is a mathematical artifact of the ratio.

### 3. τ_rec is constant

All survivors recover within 5 steps (τ_rec = 5.0 for all). There is no variation to correlate with C_pre. Recovery is instantaneous regardless of initial coherence.

### 4. Collapse rate: 15%

30 of 200 runs collapse (C_final < 0.05) at 50% removal. This is consistent with RD-5 (20% at 50% removal, smaller sample).

---

## Effect Sizes and Confidence Intervals

| Effect | Point Estimate | 95% CI | Significant? |
|--------|---------------|--------|-------------|
| Cohen's d (C_pre) | −0.123 | [−0.502, 0.253] | No |
| AUC (ROC) | 0.473 | [0.365, 0.577] | No (chance=0.5) |
| Logistic β (C_pre) | 3.009 | [−11.65, 17.67] | No |

All confidence intervals include the null value. No evidence of any relationship between C_pre and resilience.

---

## Implications

1. **C_pre contains no information about system resilience.** The hypothesis that "higher coherence → better recovery" is not supported.

2. **Collapse is determined by local geometry at the moment of removal**, not by the global coherence state. Whether grains happen to be positioned such that removing 50% causes structural failure is a matter of random initial conditions, not pre-perturbation C.

3. **The "perturbation → recovery" framework is further weakened.** Not only is there no dip (RD-5), but the pre-perturbation state does not predict post-perturbation behavior. C is a state descriptor, not a resilience indicator.

4. **The project's highest-value unresolved hypothesis is now answered: No, pre-perturbation coherence does not predict resilience.**

---

## Deliverables

- `audits/RD06_ENSEMBLE_RESILIENCE.md` — this report
- `audits/rd06_ensemble_raw.json` — 200 runs with all measurements
- `audits/rd06_analysis.json` — statistical analysis results
- `audits/rd06_fig1_distributions.png` — C_pre distributions + scatter
- `audits/rd06_fig2_roc.png` — ROC curve (AUC = 0.473)
- `audits/rd06_fig3_logistic.png` — logistic regression fit
- `audits/rd06_fig4_effect_sizes.png` — effect sizes with 95% CIs
