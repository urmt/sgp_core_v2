# ROBUSTNESS ANALYSIS — SECTION 4

**Date:** 2025-05-13

---

## N Variation Results

| N | Curvature |
|---|-----------|
| 50 | 0.000163 |
| 100 | 0.000085 |
| 200 | 0.000060 |
| 500 | 0.000000 |

**Observation:** Curvature decreases with N (expected - more points = smoother)

---

## Adversarial Test Results

### Curvature Metric

| System | Curvature | Status |
|--------|-----------|--------|
| Random Gaussian | 0.000000 | baseline |
| Hierarchical | 0.000085 | legitimate |
| Fake Hierarchy | 0.000004 | **RESISTED** (4% of real) |
| Deceptive Curvature | 0.071321 | HIGH (deceptive!) |
| False Persistence | 0.000003 | **RESISTED** |

### Instability Metric

| System | Instability | Status |
|--------|-------------|--------|
| Random | 0.0013 | baseline |
| Hierarchical | 0.0065 | organized |
| Adversarial avg | varies | TBD |

---

## Status

**PARTIAL SUCCESS**

- Curvature RESISTS fake hierarchy (4% of real)
- But DEceptive curvature SYSTEM FOOLED the metric (too high!)
- Need to add more robust detection