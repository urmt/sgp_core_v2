# RD-WELL.5 — Define Stabilization Operationally

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Define stabilization operationally"  
**Status:** COMPLETE

---

## Operational Definition of Stabilization

**Frame-to-frame variance stabilization time:** The time at which the moving average of frame-to-frame variance drops below a threshold (0.01).

**For Gray-Scott bubbles:** Stabilization time = t=10

---

## Temporal Ordering Test

**Question:** Does C increase before stabilization?

**Method:**
1. Compute C for window before stabilization (t=0-10)
2. Compute C for window after stabilization (t=10-20)
3. Compare

**Results:**
- C before stabilization (t=0-10): 0.314699
- C after stabilization (t=10-20): 0.647895

**Finding:** C INCREASES after stabilization, not before.

---

## Corrected Interpretation

**Safe finding:** C increased after stabilization in one Gray-Scott regime (bubbles).

**NOT yet established:**
- That C increase precedes stabilization
- That C increase causes stabilization
- That C increase is necessary for stabilization
- That C increase is sufficient for stabilization

---

## What This Means

1. **C does NOT increase before stabilization** (in this one test)
2. **C increases AFTER stabilization**
3. **Temporal ordering is reversed** from initial hypothesis

---

## What Would Be Needed

1. **Test more patterns** (maze, spirals)
2. **Test different stabilization metrics** (spectral entropy, derivative norm)
3. **Test different thresholds** for stabilization detection
4. **Test if C increase after stabilization is general**

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5/temporal_ordering_test_simplified.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5/run_temporal_ordering_test_simplified.py`
