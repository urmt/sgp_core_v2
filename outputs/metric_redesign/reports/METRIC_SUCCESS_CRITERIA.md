# METRIC SUCCESS CRITERIA — SECTION 5

**Date:** 2025-05-13

---

## Success Criteria for New Metrics

A metric ONLY survives if ALL of the following are TRUE:

---

### 1. RANDOM vs ORGANIZED SEPARATION

**Criterion:** 
- Mean(random) must be separable from Mean(organized)
- Effect size > 0.2

**Test:**
```python
effect_size = |organized_mean - null_mean| / null_std
```

**PASS if:** effect_size > 0.2  
**FAIL if:** effect_size ≤ 0.2

---

### 2. TOPOLOGY DESTRUCTION RESPONSE

**Criterion:**
- Metric must change significantly after topology destruction
- Δ > 20% from original value

**Test:**
```python
delta = (metric_original - metric_null) / metric_original
```

**PASS if:** |delta| > 0.2  
**FAIL if:** |delta| ≤ 0.2

---

### 3. MULTI-SEED STABILITY

**Criterion:**
- Coefficient of variation < 0.3 across 10+ seeds

**Test:**
```python
cv = std(metric_values) / mean(metric_values)
```

**PASS if:** cv < 0.3  
**FAIL if:** cv ≥ 0.3

---

### 4. BOOTSTRAP CONFIDENCE

**Criterion:**
- Bootstrap 95% CI width < 30% of mean

**Test:**
```python
ci_width = (ci_upper - ci_lower) / mean
```

**PASS if:** ci_width < 0.3  
**FAIL if:** ci_width ≥ 0.3

---

### 5. NULL REPLACEMENT SURVIVAL

**Criterion:**
- Metric remains discriminative after applying multiple null models
- Effect size > 0.1 against at least 3 null types

**Test:**
- Run against type_i, ii, iii, iv
- Count how many have effect > 0.1

**PASS if:** ≥ 3 null types show effect > 0.1  
**FAIL if:** < 3 null types show effect

---

### 6. CLASSIFICATION ACCURACY

**Criterion:**
- Simple classifier can distinguish organized from random
- Accuracy > 60% (random baseline = 50%)

**Test:**
- Use metric values as features
- Logistic regression or simple clustering

**PASS if:** accuracy > 0.6  
**FAIL if:** accuracy ≤ 0.6

---

### 7. SCALE ROBUSTNESS

**Criterion:**
- Metric survives:
  - N variation (50, 100, 200)
  - D variation (5, 20, 50)
  - Noise variation (0, 0.1, 0.5)

**Test:**
- Run metric across parameter ranges
- Check for monotonic degradation

**PASS if:** Effect size > 0.1 across ALL variations  
**FAIL if:** Effect drops below 0.1 for any variation

---

## DECISION MATRIX

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Random vs Organized | effect > 0.2 | MINIMUM |
| Topology Destruction | Δ > 20% | MINIMUM |
| Multi-seed Stability | CV < 0.3 | MINIMUM |
| Bootstrap CI | width < 30% | MINIMUM |
| Null Replacement | ≥ 3 types | MINIMUM |
| Classification | acc > 60% | MINIMUM |
| Scale Robustness | effect > 0.1 all | DESIRABLE |

**Survival Rule:** Must pass ALL MINIMUM criteria (6/7)

---

## FAILURE CONDITIONS

If ALL metrics fail:

1. Document in WHY_METRICS_FAILED.md
2. Explain what information appears absent
3. Consider whether D(k)-style geometry fundamentally lacks discrimination power
4. Do NOT proceed to real domains

---

## Status

**CRITERIA DEFINED**  
Next: Section 6 — Quick validation runs