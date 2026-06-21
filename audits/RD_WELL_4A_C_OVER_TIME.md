# RD-WELL.4A — Compute C Over Time

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Does C increase before stabilization?"  
**Status:** COMPLETE

---

## Question

Does C increase before stabilization?  
Or: Does stabilization occur without increased C?

This is an actual scientific question. No ontology required.

---

## Method

Compute C over increasing time windows:
- window=50: C computed on first 50 time steps
- window=100: C computed on first 100 time steps
- window=200: C computed on first 200 time steps

---

## Results: Gray-Scott Bubbles (F=0.098, k=0.057)

| Window | C Value |
|--------|---------|
| 50 | 0.437794 |
| 100 | 0.500418 |
| 200 | 0.526485 |

**C increases over time:** 0.4378 → 0.5004 → 0.5265

---

## Analysis

1. **C increases with window size**
   - From window=50 to window=200: C increases by ~20%

2. **C increase is monotonic**
   - Each larger window shows higher C

3. **What we cannot yet claim:**
   - We have NOT established that C increase precedes stabilization
   - We have NOT defined stabilization operationally
   - We have NOT measured stabilization time
   - We have NOT established temporal ordering

4. **Safe finding:**
   - Observed C increased across sampled windows in one dataset (bubbles)
   - Temporal relation to stabilization remains under investigation

---

## What Would Be Needed to Support "C Increases Before Stabilization"

1. **Operational definition of stabilization**
   - Example: "System stabilizes when variance of mean field changes by less than X% over Y time steps"

2. **Measured stabilization time**
   - Compute stabilization time for each pattern

3. **Temporal ordering**
   - Show that C increase occurs BEFORE stabilization time
   - Not just correlation, but temporal precedence

---

## Next Steps

1. Test more Gray-Scott patterns (maze, spirals)
2. Test Rayleigh-Bénard configurations
3. Test if C increase is necessary for stabilization
4. Test if C increase is sufficient for stabilization

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well4a/C_over_time_simplified.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well4a/run_C_over_time_simplified.py`
