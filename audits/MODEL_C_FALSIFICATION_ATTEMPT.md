# Adversarial Attack: Model C (C + Friction + Interaction)

Assume Model C is **wrong**. Find every reason the interaction might be a mirage.

---

## Attack 1: Collinearity Artifact

**Claim**: The C×friction interaction is an artifact of C and friction being highly correlated (r = −0.84, VIF(C) = 3.07 in additive model).

**Evidence**:
- When predictors are strongly correlated, interaction terms can appear significant even when no genuine synergy exists (McClelland & Judd, 1993; residual confounding).
- 95% of C variance is explained by friction. Only 5% is independent.
- The interaction is driven almost entirely by the **endpoints**: high-C/low-friction runs (friction 0.05) vs low-C/high-friction runs (friction 0.80). There is almost no data in the middle of the C×friction space.

**Counter-evidence**:
- VIF(C) = 3.07 is below standard collinearity thresholds (VIF < 5 or 10).
- The interaction survives permutation testing: shuffling the interaction term (product of C × friction) reduces R² by 0.085 (ΔC), 0.056 (restoration).
- Bootstrap resampling: interaction coefficient 95% CI excludes zero for all three targets.
- Leave-one-covariate-out: dropping interaction reduces R² by 0.095 (ΔC), 0.064 (restoration), 0.040 (τ_rec) — all > 0.

**Verdict**: Collinearity inflates the interaction but does not **create** it. The interaction is a real statistical feature of these 60 data points. Whether it generalizes is a separate question.

---

## Attack 2: Small Sample / Overfitting

**Claim**: n = 60 with 4 parameters in the full model (const + C + friction + interaction) = 15:1 ratio. But:
- Small samples inflate R² (adjusted R² = 0.497 for ΔC, still ~0.50).
- Interaction p-values (ΔC p = 0.0015, restoration p = 0.0057) are not corrected for multiple testing.
- We tested the interaction on three targets (ΔC, restoration, τ_rec). A Bonferroni correction would require p < 0.017. Restoration passes (p = 0.0057). τ_rec does not (p = 0.071 in full sample).

**Evidence**:
- k-fold CV: interaction beats additive in 80.0% (ΔC), 70.0% (restoration), 71.6% (τ_rec) of folds. But k-fold R² values have high variance (sd ≈ 0.36 for ΔC).
- Train/test split: interaction beats additive in 83.5% (ΔC), 75.5% (restoration), 70.5% (τ_rec) of 200 random 70/30 splits.
- BUT: mean predictive gain is small: +0.094 for ΔC, +0.050 for restoration, −0.003 for τ_rec.
- τ_rec is extremely unstable: k-fold CV produces astronomically negative R² values due to τ_rec outliers. τ_rec has a few runs where recovery takes very long (τ_rec ≈ 200+ steps) that dominate held-out error.

**Verdict**: The interaction survives cross-validation for ΔC and restoration, but the predictive gain is modest. For τ_rec, the interaction is not reliably detectable (p = 0.071 in full sample, R² gain ~0.04, k-fold CV unstable). The small n means these R² estimates have wide uncertainty.

---

## Attack 3: The Interaction Is an Artifact of the Friction–C Correlation

**Claim**: Since friction determines both C (r = −0.84) and recovery (r_friction,ΔC = 0.55), the "interaction" might just be friction amplified — i.e., because C is a noisy version of friction, C×friction inherits friction's predictive power.

**Evidence**:
- C alone: R² = 0.105 (ΔC). Friction alone: R² = 0.299 (ΔC).
- C+friction additive: R² = 0.428. C+friction+interaction: R² = 0.523.
- The interaction LOCO drop of 0.095 is comparable to the C LOCO drop of 0.118 (ΔC).
- Permutation: shuffling friction destroys 65.6% of model R²; shuffling C destroys 20.5%; shuffling interaction destroys 16.2%.

**Alternative explanation**: The interaction is friction² in disguise. C ≈ −0.16 × friction + 0.98. So C×friction ≈ (−0.16 × friction + 0.98) × friction = −0.16 × friction² + 0.98 × friction. If friction has a quadratic effect on recovery, the interaction would capture it.

**Test**: Fit model with friction² instead of C×friction. Compare:
- C + friction + friction² vs C + friction + C×friction.

**Counter-evidence**: If the interaction were just friction², then adding C to the model shouldn't help beyond friction + friction². C adds ΔR² = 0.129 (ΔC), 0.271 (restoration) beyond friction alone — more than what a friction² term would capture. The friction² hypothesis does not explain why C varies at fixed friction nor why this variation predicts recovery.

**Verdict**: The interaction cannot be fully reduced to friction², but this alternative has not been explicitly tested. **Weakness**: need to fit friction² model.

---

## Attack 4: The Interaction Is Driven by Two Outliers

**Claim**: The interaction significance is carried by a small number of influential points. With n = 60, leave-one-out or delete-2-outliers could make it vanish.

**Evidence**:
- Bootstrap: 5000 resamples, interaction positive in 99.9% of samples for ΔC. This is robust to point removal.
- The bootstrap explicitly resamples with replacement — it tests sensitivity to individual points. 99.9% sign stability means the interaction survives removing any 37% of points (the expected fraction left out in a bootstrap sample).
- Train/test split: interaction positive in 100% of 200 train fits for ΔC, 0% for restoration (consistently negative), 99.5% for τ_rec.

**Counter-evidence**:
- The sign stability is not a test of significance stability. For τ_rec, 98.8% of bootstrap samples have positive interaction, but only 39.7% have p < 0.05. The sign is robust but the confidence is not.
- The 95% CI for the interaction coefficient is wide: [+0.19, +0.59] for ΔC, [−0.57, −0.10] for restoration, [+0.04, +0.49] for τ_rec. This reflects substantial uncertainty.

**Verdict**: The interaction sign is robust to point removal for ΔC and restoration, but the effect size is uncertain. τ_rec is borderline.

---

## Attack 5: The Interaction Is a Selection Effect

**Claim**: The 6 friction levels (0.05, 0.1, 0.2, 0.4, 0.6, 0.8) were chosen to maximize separation. With only 10 replicates per level, the apparent C×friction interaction could be a between-group effect that disappears within groups.

**Evidence**:
- C varies within friction groups (sd 0.012–0.036). This within-group C variation predicts recovery (three-level joint probability p ≈ 0.002).
- If the interaction were purely a between-group artifact, within-friction C would be noise. It is not.

**Counter-evidence**:
- The within-group C range is very small (e.g., at friction = 0.8, C varies from ~0.994 to ~0.998 — a range of 0.004). These are physically tiny differences. Can C really matter at this resolution?
- At friction = 0.05, within-group C variation is larger (sd ≈ 0.036) but still small relative to the between-group range (0.994–1.000).

**Verdict**: The interaction is not purely a selection effect — within-friction C variation predicts recovery. But the within-group C range is so small that it strains plausibility that this tiny variation is causally meaningful.

---

## Attack 6: The Interaction Does Not Predict τ_rec Reliably

**Claim**: Model C's claim to predictive success depends on all three targets. But τ_rec:
- Interaction p = 0.071 in full sample (not significant at α = 0.05).
- Predictive gain over additive: ΔR² = 0.040 (full sample).
- Bootstrap: only 39.7% of samples have p < 0.05.
- Train/test split: mean predictive gain = −0.003 (interaction worse than additive).
- k-fold CV: numerically unstable (negative R² values due to outliers).

**Evidence**: Model C cannot reliably predict recovery time. The interaction adds essentially nothing for τ_rec.

**Verdict**: Model C's success is **target-dependent**. It works for ΔC (dip depth) and restoration (final state), but not for τ_rec (recovery speed). This is consistent with the physical interpretation that C determines whether recovery happens, not how fast.

---

## Attack 7: The Interaction Is a Misspecification Artifact

**Claim**: The true relationship is nonlinear in friction only. The "interaction" appears because we forced a linear model on a nonlinear relationship.

**Evidence**:
- Friction alone: restorations = 0.2–0.5 at friction 0.05–0.10, then jumps to 0.8–1.0 at friction 0.20–0.80. This is a threshold, not a linear relationship.
- C is ≈ linearly related to friction (r = −0.84), so C×friction partially captures the friction threshold as a quadratic.
- A friction-threshold model (dummy for friction ≤ 0.1) might explain as much as the interaction.

**Counter-evidence**:
- The C×friction interaction adds ΔR² = 0.095 (ΔC), 0.064 (restoration) over the additive C+friction model. A friction-dummy model would need to match this gain.
- C+friction additive already has R² = 0.428 (ΔC), 0.500 (restoration) — the interaction adds further gain, beyond what a threshold alone would contribute.

**Verdict**: Nonlinear friction effects are confounded with the interaction term. Not tested: friction + friction² + C model. **Weakness**: no explicit nonlinear friction model comparison.

---

## Attack 8: No Causal Test Exists — C Is Correlational

**Claim**: All evidence for Model C is correlational. No experiment has manipulated C independently of friction.

**Evidence**:
- Every piece of evidence favoring C over D is observational: C survives mobility covariates, C varies at fixed friction, C predicts across systems.
- Model D can explain every piece of evidence as correlation: C co-varies with recovery because both are caused by friction/mobility.
- Without an intervention experiment (vary C, hold friction constant), C and D are observationally indistinguishable for the strong correlation regime.

**Counter-evidence**:
- The T300.2 cross-system data provides some leverage: C predicts recovery in 8 systems without friction. This is hard for D to explain if C is a friction proxy — because there is no friction variation.
- D's response: "In those systems, C is a proxy for something else that also varies." This is unfalsifiable.

**Verdict**: This is the strongest attack on Model C. **C is not established causally.** Every claim is correlational. The interaction survives all statistical tests, but statistical survival is not causal confirmation.

---

## Attack 9: Model C Is Overfit to This Experimental Design

**Claim**: The 60-run design (6 friction × 10 replicates) overrepresents extreme friction values (0.05, 0.80) and underrepresents the middle. The interaction is an artifact of this design, not a general property of granular systems.

**Evidence**:
- 33% of runs are at the two extremes (friction 0.05 and 0.80).
- Only 17% are in the critical transition region (friction 0.1–0.4).
- The interaction is driven by the contrast between extremes — removing either extreme reduces the interaction.
- If the design were uniform across friction (more samples at 0.1–0.4), the interaction might disappear.

**Counter-evidence**:
- This is a testable claim: resample from the existing data with balanced friction distribution.
- A bootstrap that downsamples extremes would test this directly. Not done yet.

**Verdict**: The interaction may be design-dependent. **Weakness**: no balanced-resample test.

---

## Summary: Adversarial Score

| Attack | Severity | Confidence | Unanswered? |
|--------|----------|------------|-------------|
| 1. Collinearity artifact | Medium | Low | Partially answered — VIF acceptable but endpoint-driven |
| 2. Small sample / overfitting | Medium | Medium | Partially answered — CV survives but gain is small |
| 3. Interaction = friction² | Medium | Low | **Unanswered** — not explicitly tested |
| 4. Outlier-driven | Low | High | Bootstrap shows robust sign stability |
| 5. Selection effect (between-group) | Low | Low | Within-friction C variation predicts recovery |
| 6. τ_rec failure | High | High | τ_rec is not well predicted by any model |
| 7. Misspecification / threshold artifact | Medium | Low | **Unanswered** — friction-threshold model not compared |
| 8. No causal test | **Critical** | **High** | All evidence is correlational; intervention required |
| 9. Design-dependent overfitting | Medium | Low | **Unanswered** — balanced-resample test not done |

**Three unanswered attacks remain**: friction² alternative, threshold model comparison, and balanced-resample design test. These should be addressed before confidence in Model C can increase.

**The critical finding**: Attack 8 (no causal test) is the strongest. Model C, like every other model, has no causal evidence. The interaction is a robust statistical feature of these 60 runs, but robustness is not causation.
