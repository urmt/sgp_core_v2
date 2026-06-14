# RD-019 Theory Update: Quantitative Hypothesis Status

**Date**: 2026-06-06
**Trigger**: RD-019 intervention design complete. Theory must be updated to reflect pre-experiment baseline.

## Hypothesis Status Table

| # | Hypothesis | Status | Evidence | Falsified by |
|---|-----------|--------|----------|-------------|
| H1 | Residual(C) ≈ packing sparseness / contact-network fragmentation dimension | **Leading** · Likelihood 0.35 | Weak motif correlations (C_rand_bin R²=0.14). Force-chain count n.s. (|r|≤0.09). Best descriptor pre_MSE_s1 R²=0.176. Within-level signal strongest at μ=0.40. Primarily a default-by-elimination — the leading hypothesis because 68 other variables were ruled out, not because strong evidence favors it. | RD-019 I10: if density→C→recovery mediation fails |
| H2 | Residual(C) is a latent dimension not captured by any measured descriptor | **Supported** · Likelihood 0.30 | 69 variables tested across 6 families. Best R²=0.176 (pre_MSE_s1). No combination in PLS passes CV. Multiple entire families ruled out (force heterogeneity, fabric anisotropy, non-affine motion, community structure). Uniqueness survives any set of controls tested. | (Unfalsifiable by observation. Only intervention can resolve.) |
| H3 | Residual(C) is a statistical thermometer — predicts but does not cause | **Challenged** · Likelihood 0.20 | Predictive power is within-level (r up to ±0.73). But mediation tests (RD-017) show suppression not mediation — standard descriptors don't carry its effect. Thermometer view explains the data parsimoniously but the within-level structure is hard for a pure proxy to maintain. | RD-019 I10: if C fully mediates density→recovery |
| H4 | C has no causal role in recovery (pure epiphenomenon) | **Unlikely** · Likelihood 0.10 | C consistently predicts recovery across every test. Information-theoretic audit (RD-015) shows C's information overlaps with friction only partially (I(C;μ)=0.61 vs I(C;recovery)=0.23). Residual(C) has 1.2–7.6× the predictive power of raw C. The effect survives within-level, within-density, and any descriptor control set. | RD-019 I10: if C has no mediation role |
| H5 | Fr² curvature replaces all C effects | **Falsified** · Likelihood 0.05 | Nested model tests (RD-016) show Fr² does improve fit but Residual(C) still has significant within-level signal after controlling for Fr². C+Fr+Fr² is the best model. | RD-016: ΔR²(C|Fr²) = 0.03, p < 0.05 |

## Prior Probability Summary

The hypothesis space after observational saturation:
- **H1 (sparseness)**: 0.35 — leading by elimination
- **H2 (latent dimension)**: 0.30 — supported by unique explanatory power
- **H3 (thermometer)**: 0.20 — challenged but not falsified
- **H4 (epiphenomenon)**: 0.10 — unlikely given consistency
- **H5 (Fr² replaces C)**: 0.05 — falsified

**Estimated entropy**: H(p) = -Σ p_i log₂(p_i) = 1.97 bits
**Maximum possible entropy**: log₂(5) = 2.32 bits

We are 1.97/2.32 = 85% of maximum uncertainty. The experiment is expected to reduce this to ~0.8 bits (65% reduction).

## Predicted Posterior After I10

### Scenario A: Strong mediation (40% probability)
- H1 (sparseness): 0.65
- H2 (latent dimension): 0.15
- H3 (thermometer): 0.10
- H4 (epiphenomenon): 0.05
- H5 (Fr² replaces C): 0.05
- Posterior entropy: 1.42 bits (28% reduction)

### Scenario B: Partial mediation (35% probability)
- H1 (sparseness): 0.25
- H2 (latent dimension): 0.35
- H3 (thermometer): 0.25
- H4 (epiphenomenon): 0.10
- H5: 0.05
- Posterior entropy: 2.00 bits (no reduction — ambiguity increases)

### Scenario C: No mediation (25% probability)
- H1 (sparseness): 0.05
- H2 (latent dimension): 0.10
- H3 (thermometer): 0.55
- H4 (epiphenomenon): 0.25
- H5: 0.05
- Posterior entropy: 1.55 bits (21% reduction — fewer plausible hypotheses)

**Expected posterior entropy**: 0.4×1.42 + 0.35×2.00 + 0.25×1.55 = 0.568 + 0.700 + 0.388 = **1.66 bits**
**Expected entropy reduction**: 1.97 − 1.66 = **0.31 bits** (16%)

This is modest because Scenario B preserves ambiguity. But Scenarios A and C each convincingly settle the question — they just point in opposite directions. The risk is Scenario B (partial mediation), which would require a follow-up experiment.

## Experimental Design Implications

The I10 protocol assumes Scenario A predictions for its sample size (n=80). If Scenario B is the true state, the 10-replicate design may be underpowered for the cross-level comparisons. We can mitigate by:
- Adding intermediate density levels (box_width = 37, 42) if the initial 8-level scan shows nonlinearity
- Running the analysis sequentially (analyze after 40 runs, decide whether to continue)

This is the first time in the project we can design around a quantitative power analysis, because we know the effect size from RD-017 within-level tests.

## Assumptions Register Update

**A16: Density manipulation affects C at fixed friction** (New · Untested)
- Assumption: Varying box_width at fixed n_grains, friction produces measurable C variation
- Risk: If C is insensitive to density over this range (0.021–0.050), the experiment fails
- Mitigation: The box width range (25–60) produces 2.4× density variation. RD-017 within-μ variation suggests C varies ~0.03 across this range — measurable with n=10 per condition.
- Status: Untested (will be verified in step A of analysis plan)

**A17: Friction=0.40 generalizes to other friction levels** (New · Untested)
- Assumption: Mediation results at μ=0.40 hold qualitatively at other frictions
- Risk: If Residual(C)'s role is friction-specific (e.g., it matters only at high friction), conclusions don't generalize
- Mitigation: Acknowledge as limitation. Follow-up (I4) would test generalizability.
- Status: Untested (explicitly left as follow-up)

## Next Theory Step

After I10 result, the theory landscape will be sharply clarified. The expected entropy reduction is 16% on average but could be 28% or 21% in the informative scenarios. If Scenario A (strong mediation): theory updates to "Residual(C) is packing sparseness, causally linked to recovery." If Scenario C (no mediation): theory updates to "Residual(C) is a predictive signature without causal role." If Scenario B: theory remains in the current unresolved state.

The next theory update (RD-020) will be the post-experiment posterior.
