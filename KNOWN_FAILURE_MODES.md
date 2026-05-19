# KNOWN FAILURE MODES - SECTION 9

**Date:** 2025-05-13

---

## CRITICAL: Document all failures here

---

## Estimator Instabilities

### 1. Participation Ratio Edge Cases

**Problem:** D(k) = k for uniform distributions
**Symptom:** Linear D(k) curve, perfect R² on random data
**Detection:** Check if D(k) ≈ k for random baseline
**Mitigation:** Use null comparison to detect

### 2. Levina-Bickel Collapse

**Problem:** Returns near-zero for some data
**Symptom:** D < 1, infinite log ratios
**Detection:** Flag D < 0.5 as unstable
**Mitigation:** Use fallback to participation ratio

### 3. Sigmoid Overfitting

**Problem:** Sigmoid fits any monotonic curve
**Symptom:** R² > 0.95 on random data
**Detection:** Null should also have high R²
**Mitigation:** Require signal > null by delta

---

## Overfitting Conditions

### 4. Small N Bias

**Problem:** k > N/2 leads to sampling bias
**Symptom:** D(k) plateaus artificially
**Mitigation:** Limit k < N/3

### 5. Low Dimension Artifacts

**Problem:** D < 10 leads to numerical issues
**Symptom:** Eigenvalue decomposition fails
**Mitigation:** Add noise regularization

### 6. High Variance D(k)

**Problem:** Sample variance dominates signal
**Symptom:** Unstable k0 across seeds
**Mitigation:** Bootstrap CI, report stability

---

## False Positives

### 7. Sigmoid on Random Data

**Problem:** Random data produces high-R² sigmoid
**Cause:** D(k) ≈ k is inherently sigmoid-like
**Detection:** Compare to null - should have similar R²

### 8. Artificially Low k0

**Problem:** Sigmoid fit returns k0 outside data range
**Cause:** Poor initialization
**Mitigation:** Constrain bounds to data range

### 9. Bootstrap Non-convergence

**Problem:** Bootstrap sampling creates singular matrices
**Detection:** Check for nan in CI
**Mitigation:** Increase regularization

---

## Runtime Problems

### 10. O(N²) Scaling

**Problem:** KDTree scales poorly beyond N=10000
**Symptom:** Runtime > 10 minutes
**Mitigation:** Use approximation or subsample

### 11. Memory Overflow

**Problem:** Large distance matrices
**Symptom:** MemoryError on large N
**Mitigation:** Use sparse representations

---

## Topology Artifacts

### 12. Boundary Effects

**Problem:** Points near boundary have different neighbor distributions
**Detection:** Compare bulk vs boundary D(k)

### 13. Density Variations

**Problem:** Non-uniform density affects k-NN distances
**Detection:** Check density profile

---

## When in Doubt

If result looks "too perfect":
1. Assume artifact first
2. Test with null models
3. Run with multiple seeds
4. Check bootstrap stability

---

## Reporting Failures

When experiment fails:
1. Document in this file
2. Note conditions (N, D, k range)
3. Describe symptoms
4. Propose mitigation
5. Update validation checks

---

**THIS DOCUMENT IS CRITICAL**  
Update with every failure encountered.