# RD-MATH.2B.R1 — Metric Sensitivity Audit

**Date:** 2026-06-15  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Does the ruler work?"  
**Status:** COMPLETE

---

## Method

Generate 5 obviously distinct dynamical regimes:

1. **Ordered lattice**: particles on grid, minimal motion
2. **Random gas**: particles move randomly, no interactions
3. **Clustered aggregate**: particles cluster in center with noise
4. **Oscillatory forcing**: particles oscillate in place
5. **Frozen solid**: particles completely static

Compute: C, TE, Empowerment, Novelty Rate

---

## Results

### Sensitivity Analysis

| Metric | Mean | Std | CV | Verdict |
|--------|------|-----|----|---------|
| C | 0.2682 | 0.3395 | 1.2658 | **Sensitive** |
| TE | 0.0000 | 0.0000 | 0.0000 | **Dead** |
| Empowerment | 5.9868 | 2.9934 | 0.5000 | **Broken** |
| Novelty_Rate | 0.2682 | 0.3395 | 1.2658 | = C |

### Inter-Regime Comparison

| Regime | C | TE | Empowerment | NR |
|--------|---|----|-------------|----|
| ordered_lattice | 0.8113 | 0.0000 | 7.4835 | 0.8113 |
| random_gas | 0.0014 | 0.0000 | 7.4835 | 0.0014 |
| clustered_aggregate | 0.0014 | 0.0000 | 7.4835 | 0.0014 |
| oscillatory | 0.5269 | 0.0000 | 7.4835 | 0.5269 |
| frozen | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

---

## Findings

### 1. C works correctly

C varies as expected:
- ordered_lattice: 0.8113 (high coherence)
- oscillatory: 0.5269 (medium)
- random_gas: 0.0014 (low)
- clustered_aggregate: 0.0014 (low)
- frozen: 0.0000 (zero)

**C is a functioning metric.**

### 2. TE is dead

TE = 0.000000 for ALL regimes, including ordered lattice and oscillatory.

This is impossible. Ordered lattice should have high transfer entropy (structured interactions). Random gas should have some TE (random correlations).

**TE is broken or misimplemented.**

### 3. Empowerment is broken

Empowerment = 7.4835 for ALL non-frozen regimes:
- ordered_lattice: 7.4835
- random_gas: 7.4835
- clustered_aggregate: 7.4835
- oscillatory: 7.4835

This is impossible. Ordered lattice and random gas have completely different dynamics.

**Empowerment is measuring something about the metric implementation, not the system dynamics.**

### 4. Novelty Rate = C

By construction: NR = max(0, C) = C.

**NR is not a separate metric.**

---

## Interpretation

### The ruler is broken

The Research Director asked: "Does the ruler work?"

**Answer: Partially.**

- C works: varies correctly across regimes
- TE is dead: always 0
- Empowerment is broken: constant for non-frozen regimes
- NR = C by construction

### Why did RD-MATH.2B show F_clean = 1.0 × C?

Because:
- F_NR = C (by construction)
- F_TE = 0 (broken)
- F_Emp = 7.4835 (constant)

F_clean = (0 + 7.4835 + C) / 3 = 2.4945 + C/3

This is a linear function of C. That's why R² = 1.0.

**The "reduction" was an artifact of broken metrics.**

### The correct conclusion

**Under the current operationalization, the F proxies (TE, Empowerment, NR) are not functioning as intended.**

This does NOT mean:
- F is reducible to C
- F doesn't exist
- The compass is wrong

It means:
- The metrics need repair
- The compass equation remains untested

---

## Recommended Next Steps

1. **Fix TE implementation** (should not be 0 for ordered systems)
2. **Fix Empowerment implementation** (should vary with dynamics)
3. **Find actual F proxies** that measure fertility independent of C
4. **Re-run RD-MATH.2A/2B with fixed metrics**

---

## Artifact

- Results: `audits/RD_MATH_2B_R1/metric_sensitivity_results.json`
- Script: `audits/RD_MATH_2B_R1/run_metric_sensitivity.py`
