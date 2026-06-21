# RD-MATH.2A — C/F Dissociation Audit

**Date:** 2026-06-15  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Can F be measured independently of C?"  
**Status:** COMPLETE

---

## Method

- 6 friction levels × 5 replicates = 30 granular simulations
- Each system: 50 grains, 1000 timesteps, 20% removal at step 500
- C computed via `compute_C(X, "gaussian")` on binned time series
- F computed as composite of 4 proxies: TE, Empowerment, Novelty Rate, Recovery

---

## Results

### Quadrant Analysis

| Quadrant | Count | C Range | F Range |
|----------|-------|---------|---------|
| High C, High F | 12 | [0.48, 0.62] | [2.28, 2.34] |
| High C, Low F | 3 | [0.51, 0.55] | [2.27, 2.28] |
| Low C, High F | 3 | [0.41, 0.45] | [2.29, 2.30] |
| Low C, Low F | 12 | [0.32, 0.47] | [2.18, 2.27] |

### Statistical Summary

- C median: 0.4794
- F median: 2.2790
- C-F correlation: 0.8246
- All four quadrants exist

---

## Interpretation

**All four quadrants exist.** C and F are not perfectly correlated.

**But correlation is strong (0.82).** This is not full independence.

**The compass equation Ψ ≈ f(C, F, I) may still hold, but F may be partially redundant with C.**

---

## Research Director's Concern

The question was: "Can systems exhibit high C, low F?"

**Answer: Yes, but only marginally.**

The three systems in the "High C, Low F" quadrant:
- C range: [0.51, 0.55] (above median)
- F range: [2.27, 2.28] (below median, but very close to median)

The separation is small. These are not dramatically different systems.

---

## Caveat

The F composite includes a "Recovery" proxy that directly uses C:
```python
pre_C = compute_C(X[:, :500], estimator="gaussian")
post_C = compute_C(X[:, 500:], estimator="gaussian")
F_REC = post_C / max(pre_C, 1e-10)
```

This creates implicit correlation between C and F.

**The test is incomplete.** F should be measured without reference to C.

---

## Recommended Next Steps

1. **Redo the test with F proxies that do not reference C** (remove Recovery proxy, use only TE, Empowerment, Novelty Rate)
2. **Test whether the separation is statistically significant** (bootstrap confidence intervals on quadrant boundaries)
3. **Test whether the correlation is an artifact of the shared binning scheme**

---

## Artifact

- Results: `audits/RD_MATH_2A/cf_dissociation_results.json`
- Script: `audits/RD_MATH_2A/run_cf_dissociation.py`
