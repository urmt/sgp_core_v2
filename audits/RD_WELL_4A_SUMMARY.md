# RD-WELL.4A Summary — C Over Time Across Patterns

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Does C increase before stabilization?"  
**Status:** COMPLETE (with corrected interpretation)

---

## Corrected Finding

**Safe finding:** Observed C increased across sampled windows in three Gray-Scott datasets. Temporal relation to stabilization remains under investigation.

**NOT yet established:**
- That C increase precedes stabilization
- That C increase causes stabilization
- That C increase is necessary for stabilization
- That C increase is sufficient for stabilization

---

## Results Across Patterns

| Pattern | window=50 | window=100 | window=200 | Trend |
|---------|-----------|------------|------------|-------|
| bubbles (F=0.098) | 0.4378 | 0.5004 | 0.5265 | Increasing |
| maze (F=0.029) | 0.4139 | 0.5043 | 0.5445 | Increasing |
| spirals (F=0.018) | 0.0000 | 0.0258 | 0.0516 | Increasing |

---

## Key Observations

1. **All three patterns show C increasing with window size**
   - Bubbles: +20% from window=50 to window=200
   - Maze: +32% from window=50 to window=200
   - Spirals: +5163% from window=50 to window=200 (but absolute values are very low)

2. **C values differ dramatically across patterns**
   - Bubbles and maze: C ~0.4-0.5
   - Spirals: C ~0.00-0.05

3. **All patterns show monotonic increase**
   - Each larger window shows higher C

---

## What We Cannot Yet Claim

1. **Temporal ordering:** We have not shown that C increase occurs BEFORE stabilization
2. **Causation:** We have not shown that C increase causes stabilization
3. **Necessity:** We have not shown that C increase is necessary for stabilization
4. **Sufficiency:** We have not shown that C increase is sufficient for stabilization

---

## What Would Be Needed

1. **Operational definition of stabilization**
   - Example: "System stabilizes when variance of mean field changes by less than X% over Y time steps"

2. **Measured stabilization time**
   - Compute stabilization time for each pattern

3. **Temporal ordering analysis**
   - Show that C increase occurs BEFORE stabilization time
   - Not just correlation, but temporal precedence

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well4a/`
- Scripts: `/home/student/sgp_core_v2/audits/rd_well4a/run_C_over_time_*.py`
