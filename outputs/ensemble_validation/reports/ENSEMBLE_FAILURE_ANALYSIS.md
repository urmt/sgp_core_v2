# ENSEMBLE FAILURE ANALYSIS — SECTION 10

**Date:** 2025-05-13

---

## What Worked

1. **Deceptive curvature detected** - Score dropped to 0.28 (vs 10.55 legitimate)
2. **Spoof penalty increased** - 0.41 for deceptive vs 0.30 for legitimate
3. **Anti-spoof framework** - Multiple detectors implemented

---

## What Failed

1. **Score calibration** - random_gaussian scored higher than hierarchical (62.95 vs 10.55)
2. **Rejection threshold** - Not reached (need > 0.5, got 0.41 max)
3. **Ordering issues** - Legitimate systems don't rank correctly

---

## Why Failed

The z-score normalization in consensus computation is not properly calibrated for the scale differences between metrics. The current implementation treats all metrics equally but they have very different magnitudes.

---

## Whether Spoofing Remains Possible

YES - The system is not reliable yet. Need:
1. Better score normalization
2. Higher rejection threshold
3. Multi-metric voting system

---

## Whether Geometry-Only Methods May Be Insufficient

POSSIBLY - The ensemble still depends on geometric metrics which can be gamed. Temporal information might help but is not yet integrated.

---

## Status

**PARTIAL FAILURE** - Need more work.