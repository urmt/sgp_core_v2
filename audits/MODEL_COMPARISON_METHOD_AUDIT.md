# Model Comparison Method Audit

**Objective**: Audit the scoring methodology used in `audits/MODEL_D_COMPETITIVE_ANALYSIS.md`. Test whether the criteria systematically favored Model D over Model A.

---

## 1. Who Chose the Scoring Criteria?

The original MODEL_D_COMPETITIVE_ANALYSIS.md was written by the same agent that wrote EVIDENCE_LEDGER.md, COLLINEARITY_REPORT.md, and all other audit documents. The scoring criteria were not externally peer-reviewed.

**Risk**: The agent had prior exposure to the finding that Model A is partially falsified. This may have created a confirmation bias toward models that survive falsification (D) over models that predict positive outcomes (A).

---

## 2. Systematic Bias: Do the Criteria Favor Parsimonious Explanations?

**Original criteria**: Each observation scored as "Better explained by A," "Better explained by D," or "Ambiguous."

**Problem**: The rubric does not distinguish between:
- "D explains this better than A" (D has genuine explanatory advantage)
- "D is not falsified by this observation" (D survives, but A also survives)

In practice, "Better explained by D" was assigned when A was falsified and D survived. This conflates **D's survival** with **D's superiority**.

**Example**: Observation 5 (same C, opposite ΔC sign). Under A, this is a fatal contradiction. Under D, it's expected (C doesn't determine direction). The original scores this as "Better explained by D." But D doesn't actively explain the sign reversal — D simply doesn't predict a direction in the first place. "Better explained by D" is misleading. "Not falsified by D" is accurate.

**Result**: The 4–0 score is inflated because 4 of D's "wins" are actually A's "losses."

---

## 3. Were Predictions Weighted Equally?

**No — and this favors D.**

Model A makes positive predictions: "C determines recovery direction," "C determines recovery speed," "C ensures good recovery." These predictions are directly testable. When they fail, A is penalized.

Model D makes negative predictions: "C does NOT determine recovery direction alone," "C does NOT determine recovery speed alone." D is never penalized for these negative predictions — they are confirmed by the same evidence that falsifies A.

**The weighting is asymmetric**: A's positive predictions are tested and potentially falsified. D's negative predictions are tested and confirmed by the same test. D never risks falsification through its positive predictions because it makes almost no positive predictions beyond "C is informative."

**Fair weighting**: If we weight each observation by the risk each model takes, D's risk is near-zero (it predicts nothing positive about recovery). A's risk is high (it predicts C determines recovery). A model that takes no risks cannot "win" on a level playing field.

---

## 4. Were Failed Predictions Penalized Equally?

**No — D has no failed predictions.**

Across all 9 observations:
- **A's failed predictions**: Observations 3–6 (4 failures). A predicts high C → good recovery (true but trivially), low C → poor recovery (false), C determines direction (false), C determines speed (false).
- **D's failed predictions**: None. D never predicts a specific recovery outcome. It predicts that C is informative but non-causal — which is consistent with every observation.

This is not because D is superior. It is because D's claims are **negatively defined** (what C does NOT do) rather than **positively defined** (what C does).

**A model that cannot fail is not scientifically useful.**

---

## 5. Sensitivity Analysis: Changing the Rubric

### Rubric 1 (Original): "Better explained by" — Ambiguous counts as neither

Result: A = 0, D = 4, Ambiguous = 5. D wins.

### Rubric 2: "Actively predicted by" — Ambiguous counts as "both survive"

Score each observation:
- Observation actively predicted by model? +1 point
- Observation contradicted by model? −1 point
- Observation neither predicted nor contradicted? 0 points

| Observation | A score | D score |
|-------------|:---:|:---:|
| 1. C detects perturbations | 0 (both survive) | 0 (both survive) |
| 2. C discriminates structure | 0 (both survive) | 0 (both survive) |
| 3. High C → good recovery | +1 (predicted) | 0 (not predicted, not contradicted) |
| 4. Low C → good recovery | −1 (contradicted) | 0 (not predicted, not contradicted) |
| 5. Same C, opposite ΔC sign | −1 (contradicted) | 0 (not predicted, not contradicted) |
| 6. Same C, 3–4× τ_rec | −1 (contradicted) | 0 (not predicted, not contradicted) |
| 7. Interaction model predicts | 0 (both survive) | 0 (both survive) |
| 8. C outperforms competitors | 0 (both survive) | 0 (both survive) |
| 9. IF-3 reconstruction | 0 (both survive) | 0 (both survive) |

**Result**: A = −2, D = 0. D "wins" but only because D made no testable predictions. D's score of 0 does not reflect explanatory power — it reflects risk avoidance.

### Rubric 3: "Uniquely explains" — Only observations that ONE model can account for

| Observation | Score |
|-------------|:----:|
| 1. Perturbation detection | Neither uniquely (both survive) |
| 2. Structure discrimination | Neither uniquely (both survive) |
| 3. High C → good recovery | Neither uniquely (both survive) |
| 4. Low C → strong recovery | D uniquely (A contradicted) |
| 5. Same C, opposite ΔC | D uniquely (A contradicted) |
| 6. Same C, different τ_rec | D uniquely (A contradicted) |
| 7. Interaction predicts | Neither uniquely (both survive) |
| 8. C outperforms competitors | Neither uniquely (both survive) |
| 9. IF-3 reconstruction | Neither uniquely (both survive) |

**Result**: A = 0 uniquely explained, D = 3 uniquely explained (observations where A is contradicted). D wins, but only because the "uniquely explained" rubric rewards models that are NOT falsified. D never had to explain these observations — it merely had to survive them.

### Rubric 4: "Positive predictive success" — Only observations actively predicted

| Model | Active predictions | Confirmed | Failed | Score |
|-------|:---:|:---:|:---:|:---:|
| A (C-causal) | C→ΔC sign, C→τ_rec, C→restoration, High C→good, Low C→poor | 1 (high C→good) | 3 (direction, speed, low C) | 1/4 = 0.25 |
| B (Mobility-only) | Friction→ΔC, Friction→rest, No C needed | 1 (friction→ΔC) | 1 (C adds info) | 1/2 = 0.50 |
| C (Interaction) | C×friction→ΔC, C×friction→rest, C×friction→τ_rec | 2 (ΔC, rest) | 0 (τ_rec marginal) | 2/3 = 0.67 |
| D (Thermometer) | C informative, C conditional indep. given mobility | 1 (C informative) | 1 (C not cond. indep. given mob.) | 1/2 = 0.50 |

**Result**: Model C has the highest positive predictive success rate (0.67). D's positive prediction that C is conditionally independent of recovery given mobility is CHALLENGED by the interaction surviving.

---

## 6. Sensitivity Summary

| Rubric | Winner | Bias |
|--------|:-----:|------|
| 1. "Better explained by" (original) | D (4–0) | Favors models with NO positive predictions (D) |
| 2. "Actively predicted by" | D (0 vs −2) | Same bias — D never risks failed predictions |
| 3. "Uniquely explains" | D (3–0) | Rewards survival, not explanation |
| 4. "Positive predictive success" | C (0.67) | Favors models that make and satisfy positive predictions |

**Result flips when rubric changes.** Under rubric 4 (positive predictive success), Model C wins. Under rubrics 1–3, Model D wins.

**The original 4–0 score is an artifact of a rubric that rewards survival over prediction.**

---

## 7. Conclusion: What Went Wrong

The original MODEL_D_COMPETITIVE_ANALYSIS.md committed a systematic error: **it conflated "D survives this observation" with "D explains this observation."**

D's "wins" on observations 3–6 are not wins — they are non-falsifications. A thermometer that reads "warm" doesn't explain why we're warm. It merely doesn't contradict the observation.

**The correct interpretation**:
- Model D is not falsified by any observation
- Model A is partially falsified by observations 4–6
- Model C has the highest positive predictive success (ΔC and restoration significantly predicted; τ_rec marginal)
- Model D has the lowest positive predictive risk (no positive predictions about recovery)
- The question of whether D or C is "best" cannot be answered by a scorecard — it depends on whether explanatory parsimony or predictive success is valued more

**Recommendation**: Report the result as:
- "Model C has the best predictive fit (R² = 0.52–0.56). Model D is the most parsimonious. Model A is partially falsified. Model B is falsified."
- Rather than: "D wins 4–0."
