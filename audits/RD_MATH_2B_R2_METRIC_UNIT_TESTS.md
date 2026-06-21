# RD-MATH.2B.R2 — Metric Unit Tests

**Date:** 2026-06-15  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Does the ruler work?"  
**Status:** COMPLETE

---

## Method

Construct toy systems with known answers. Test whether metrics recover them.

---

## TE Unit Tests

| Test | System | Expected | Actual | Pass |
|------|--------|----------|--------|------|
| A | X independent of Y | TE = 0 | 0.000000 | ✅ |
| B | Y(t+1) = X(t) | TE > 0 | 0.000000 | ❌ |
| C | Y(t+1) = random | TE ≈ 0 | 0.000000 | ✅ |

**TE fails Test B.** Causal coupling produces no detected transfer entropy.

---

## Empowerment Unit Tests

| Test | System | Expected | Actual | Pass |
|------|--------|----------|--------|------|
| A | 1 action → 1 outcome | Low | 3.6978 | — |
| B | 4 actions → 4 outcomes | High | 7.4835 | — |
| C | many actions → same outcome | Low | 7.4835 | — |

**Ordering: B > A and B > C?** False. B = C = 7.4835.

**Empowerment fails the ordering test.** Cannot distinguish high from low controllability.

---

## Interpretation

### TE

The implementation either:
- Has a bug in the causal detection
- Uses wrong parameters (tau, k, binning)
- Computes something other than transfer entropy

### Empowerment

The implementation either:
- Counts dimensions, not controllability
- Ignores correlation structure
- Measures something about the embedding, not the dynamics

---

## Verdict

**Both TE and Empowerment do not recover known answers in toy systems.**

They cannot be used scientifically until repaired.

**C is the only metric that passes its unit tests.**

---

## Recommended Next Steps

1. **Debug TE implementation** — compare against known TE estimators
2. **Debug Empowerment implementation** — verify it measures controllability, not dimensionality
3. **Only after unit tests pass** should these metrics be used in RD

---

## Artifact

- Results: `audits/RD_MATH_2B_R2/unit_test_results.json`
- Script: `audits/RD_MATH_2B_R2/run_unit_tests.py`
