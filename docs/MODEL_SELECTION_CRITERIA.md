# Model Selection Criteria: Decision Thresholds

Defined in advance. No retrospective reasoning.

---

## 1. When would we move from D → C?

Current state: D (thermometer) is epistemically safest but challenged by C's predictive success.

**Threshold**: Model C must meet **three** of the following:

| # | Criterion | Threshold | Status |
|---|-----------|-----------|--------|
| T1 | Independent replication | Interaction term significant (p < 0.05) and sign-consistent in ≥ 2 independent datasets (different simulators, different systems, or different friction ranges). | Not met. Only one 60-run granular ensemble. |
| T2 | Out-of-sample cross-validation | Mean predictive gain (interaction over additive) > 0.05 R² with 95% CI > 0, on held-out data not used in training. | Partially met. ΔC: gain = 0.094 (CV), 0.094 (TT). Restoration: gain = 0.056 (CV), 0.050 (TT). τ_rec: NOT met. |
| T3 | Mobility proxy failure resolved | Show that the 4 mobility proxies are *adequate* measures of what D claims causes recovery. If they are inadequate, D's escape is valid. If they are adequate, the interaction survival falsifies D. | Not met. Mobility proxy adequacy is untested. |
| T4 | Design-dependence ruled out | Interaction survives balanced resampling (downsample extremes), friction² alternative, and threshold model comparison. | Not met. Three specific tests remain unanswered. |
| T5 | Causal mechanism demonstrated | Show a plausible mechanism by which C (contact topology) could causally affect recovery that does not reduce to friction or mobility. | Partially met. Granular physics provides mechanism. Not experimentally demonstrated. |

**Decision rule**: Move from D → C as working model when ≥ 3 thresholds are met.
**Current**: 0 thresholds fully met (T2 partially, T5 partially).

---

## 2. When would we move from C → D?

Current state: C (interaction) is predictive frontrunner.

**Threshold**: Model D must meet **two** of the following:

| # | Criterion | Threshold | Status |
|---|-----------|-----------|--------|
| T6 | Interaction disappears in replication | The C×friction interaction (p < 0.05 and positive ΔR² > 0.05) fails to replicate in an independent dataset with comparable power. | Not tested. |
| T7 | Mobility proxies predict recovery | At least one mobility proxy shows p < 0.01 and meaningful effect (β > 0.2) when added to the C+friction model, supporting D's causal claim. | **Not met.** All mobility proxies p > 0.10. |
| T8 | C shown to be pure friction proxy | Within-friction C variation is shown to be uncorrelated with recovery (p > 0.05 across all friction levels). | **Not met.** Within-friction C predicts recovery (p ≈ 0.002, three-level joint). |
| T9 | Intervention experiment | Manipulate C while holding friction constant → no change in recovery (effect size d < 0.2). | Not tested. |

**Decision rule**: Move from C → D as working model when ≥ 2 thresholds are met.
**Current**: 0 thresholds met. C is the predictive frontrunner until evidence favors D.

---

## 3. When would we reject Model A entirely?

Current state: Strong A falsified. Weak A (multi-factor) survives.

| # | Criterion | Threshold |
|---|-----------|-----------|
| T10 | C-alone fails cross-system | On the T300.2 cross-system data, C does not predict recovery (p > 0.05). |
| T11 | C-direction fails universally | Across all datasets, no correlation between C ranking and recovery ranking (or relationship is negative). |

**Decision rule**: Reject A when either threshold is met.
**Current**: T11 met (T900 series). Strong A is rejected. Weak A (C is part of multi-factor interaction) remains viable.

---

## 4. When would we reject Model D entirely?

Current state: D is not falsified but challenged.

| # | Criterion | Threshold |
|---|-----------|-----------|
| T12 | Interaction replication | Interaction term replicates in independent data with p < 0.01, consistent sign, and ΔR² > 0.05. (If C is non-causal proxy, its interaction with friction should not replicate across different systems.) |
| T13 | Intervention experiment | Manipulating C while holding friction constant changes recovery (effect size d > 0.5, p < 0.01). |
| T14 | Mobility measure validated | An adequate mobility measure is identified and validated; it does *not* render C conditionally independent of recovery. |

**Decision rule**: Reject D when ≥ 2 thresholds are met.
**Current**: 0 thresholds met. D remains viable.

---

## 5. When would we declare Model C "established"?

A higher bar than "move from D → C":

| # | Criterion | Threshold |
|---|-----------|-----------|
| T15 | Cross-validation confirmed | Interaction gain > 0.05 R² in ≥ 3 independent datasets. |
| T16 | Causal pathway specified | A plausible, testable causal mechanism is specified — not just "C correlates." |
| T17 | Intervention confirmed | Manipulating C changes recovery (any effect size, p < 0.05). |
| T18 | Rival explanations eliminated | Friction², threshold, and collinearity alternatives all fail to explain the interaction pattern. |

**Decision rule**: Model C is established when ≥ 3 of T15–T18 are met.
**Current**: 0 thresholds met.

---

## Summary Table

| Decision | Rule | Criteria Needed | Currently Met |
|----------|------|----------------|:------------:|
| Move D → C as working model | C clears ≥ 3 of T1–T5 | 3 | 0 |
| Move C → D as working model | D clears ≥ 2 of T6–T9 | 2 | 0 |
| Reject A entirely | Either T10 or T11 | 1 | 1 (T11) |
| Reject D entirely | ≥ 2 of T12–T14 | 2 | 0 |
| Establish C | ≥ 3 of T15–T18 | 3 | 0 |

**Current working posture**: Neither C nor D is established. Both are viable. C leads on prediction. D leads on epistemic safety. The next step to move either is independent replication (T1/T6/T12) or intervention (T9/T13/T17).
