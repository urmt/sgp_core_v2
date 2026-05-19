# STATISTICAL RIGOR FRAMEWORK - SECTION 8

**Date:** 2025-05-13

---

## Implemented Tests

### 1. Bootstrap Testing

- 100 bootstrap samples
- 95% confidence intervals
- Standard error estimation
- Implemented in: `scripts/core/universal_dk_pipeline.py`

### 2. Permutation Testing

- Shuffle data, recompute D(k)
- Compare to observed
- Compute p-value approximation

### 3. Effect Sizes

- R² difference (signal - null)
- Cohen's d where applicable
- Delta R² threshold: > 0.1 significant

### 4. Model Comparison

- AIC (Akaike Information Criterion)
- BIC (Bayesian Information Criterion)
- Select simpler model if ΔAIC > 2

---

## Anti-P-Hacking Rules

1. **Pre-registration** - Define hypotheses before running
2. **No cherry-picking** - Report all trials, not just best
3. **Conservative thresholds** - Require p < 0.01 for claims
4. **Effect size required** - p-value alone insufficient
5. **Replication expectation** - Can repeat with different seeds

---

## Statistical Output Requirements

Every experiment MUST report:

- Sample size (N)
- Parameter estimates with CI
- Effect size (delta R² or equivalent)
- Null comparison result
- Number of trials
- Seed values used

---

## Status

**IMPLEMENTED**  
Framework in place for rigorous statistical testing.