# ENSEMBLE QUICK VALIDATION — SECTION 6

**Date:** 2025-05-13

---

## Results

| System | Ensemble Score | Spoof Penalty | Rejected |
|--------|---------------|---------------|----------|
| random_gaussian | 62.95 | 0.30 | No |
| hierarchical | 10.55 | 0.30 | No |
| fake_hierarchy | 18.62 | 0.30 | No |
| deceptive_curvature | **0.28** | **0.41** | No |

---

## Key Findings

### 1. Deceptive Curvature Detected

- Score: 0.28 (much lower than legitimate hierarchical: 10.55)
- Spoof penalty: 0.41 (higher than legitimate: 0.30)

### 2. Ensemble Ordering Issues

- random_gaussian has higher score than hierarchical (needs fixing)
- The z-score normalization is not properly calibrated

### 3. Spoof Detection Partially Working

- Deceptive curvature shows 37% higher spoof penalty
- But rejection threshold (0.5) not reached

---

## Status

**PARTIAL SUCCESS** - Ensemble shows differentiation but needs calibration.